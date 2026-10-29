import contextlib
import fcntl
import io
import json
import os
import subprocess
import tempfile
import threading
import unittest
from unittest import mock

import log_run

COUNTS = ["--tier", "standard", "--verdict", "approve", "--loc", "10", "--raised", "3",
          "--confirmed", "2", "--dropped-gate", "1", "--refuted-panel", "0", "--agents", "2",
          "--tokens", "1000"]


def sh(repo, *cmd):
    subprocess.run(cmd, cwd=repo, check=True, capture_output=True)


class LogRunTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = os.path.join(self.tmp.name, "repo")
        os.mkdir(self.repo)
        self.journal = os.path.join(self.tmp.name, "mem", "runs.jsonl")
        sh(self.repo, "git", "init", "-q", "-b", "main")
        sh(self.repo, "git", "config", "user.email", "t@t")
        sh(self.repo, "git", "config", "user.name", "t")
        sh(self.repo, "git", "remote", "add", "origin", "git@gitlab.com:team/shop.git")
        self.commit("a.txt", "one\n")
        sh(self.repo, "git", "checkout", "-q", "-b", "feat")

    def tearDown(self):
        self.tmp.cleanup()

    def commit(self, name, content):
        with open(os.path.join(self.repo, name), "w") as fh:
            fh.write(content)
        sh(self.repo, "git", "add", name)
        sh(self.repo, "git", "commit", "-q", "-m", name)

    def run_cmd(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = log_run.main(["--journal", self.journal, *argv, "--repo", self.repo]
                                if argv[0] != "check" else ["--journal", self.journal, *argv])
        return code, out.getvalue(), err.getvalue()

    def lines(self):
        with open(self.journal) as fh:
            return fh.read().splitlines()

    def rows(self):
        return [json.loads(line) for line in self.lines()]

    def test_valid_line_is_appended_with_derived_fields(self):
        code, _, _ = self.run_cmd("log", *COUNTS)
        self.assertEqual(code, 0)
        row = self.rows()[0]
        self.assertEqual(row["project"], "shop")
        self.assertEqual(row["branch"], "feat")
        self.assertEqual(row["round"], 1)
        self.assertFalse(row["loop"])
        self.assertIsNone(row["same_diff"])

    def test_logged_round_resets_the_fanout_cap(self):
        with mock.patch.dict(os.environ, {"CLAUDE_CODE_SESSION_ID": "sess"}), \
                mock.patch.object(log_run.fanout_cap, "reset") as reset:
            self.run_cmd("log", *COUNTS)
        reset.assert_called_once_with("sess")

    def test_refused_log_keeps_the_fanout_count(self):
        counts = list(COUNTS)
        counts[counts.index("--raised") + 1] = "9"
        with mock.patch.dict(os.environ, {"CLAUDE_CODE_SESSION_ID": "sess"}), \
                mock.patch.object(log_run.fanout_cap, "reset") as reset:
            code, _, _ = self.run_cmd("log", *counts)
        self.assertNotEqual(code, 0)
        reset.assert_not_called()

    def test_broken_invariant_writes_nothing(self):
        counts = list(COUNTS)
        counts[counts.index("--confirmed") + 1] = "3"
        code, _, err = self.run_cmd("log", *counts)
        self.assertEqual(code, 2)
        self.assertIn("recount", err)
        self.assertFalse(os.path.exists(self.journal))

    def test_tier_outside_enum_is_refused(self):
        counts = list(COUNTS)
        counts[counts.index("--tier") + 1] = "standard+loop"
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            self.run_cmd("log", *counts)

    def test_missing_tokens_is_logged_as_null(self):
        counts = COUNTS[:COUNTS.index("--tokens")]
        self.assertEqual(self.run_cmd("log", *counts)[0], 0)
        self.assertIsNone(self.rows()[0]["tokens"])

    def test_round_is_derived_and_new_loc_measured_between_heads(self):
        self.run_cmd("log", *COUNTS, "--base", "main")
        self.commit("b.txt", "x\ny\nz\n")
        self.run_cmd("log", *COUNTS, "--base", "main")
        second = self.rows()[1]
        self.assertEqual(second["round"], 2)
        self.assertEqual(second["new_loc"], 3)
        self.assertFalse(second["same_diff"])

    def test_unchanged_working_tree_is_same_diff(self):
        with open(os.path.join(self.repo, "new.txt"), "w") as fh:
            fh.write("untracked\n")
        self.run_cmd("log", *COUNTS)
        _, out, _ = self.run_cmd("last")
        self.assertTrue(json.loads(out)["same_diff"])
        with open(os.path.join(self.repo, "new.txt"), "w") as fh:
            fh.write("edited\n")
        _, out, _ = self.run_cmd("last")
        self.assertFalse(json.loads(out)["same_diff"])

    def test_committed_work_without_base_is_not_same_diff(self):
        # Reviewing committed work without --base hashes an empty diff: two
        # different commits must not look like an unchanged diff.
        self.run_cmd("log", *COUNTS)
        self.commit("b.txt", "x\n")
        _, out, _ = self.run_cmd("last")
        self.assertIsNone(json.loads(out)["same_diff"])

    def test_rewritten_previous_head_gives_null_new_loc(self):
        self.run_cmd("log", *COUNTS, "--base", "main")
        rows = self.rows()
        rows[0]["head"] = "deadbee"
        with open(self.journal, "w") as fh:
            fh.write(json.dumps(rows[0]) + "\n")
        _, out, _ = self.run_cmd("last", "--base", "main")
        self.assertIsNone(json.loads(out)["new_loc"])

    def test_log_without_outcome_stores_null(self):
        self.assertEqual(self.run_cmd("log", *COUNTS)[0], 0)
        row = self.rows()[0]
        for key in ("fixed", "rejected", "deferred", "model"):
            self.assertIsNone(row[key])
        self.assertEqual(row["pending"], 2)

    def test_outcome_patches_only_the_matching_round(self):
        self.run_cmd("log", *COUNTS)
        self.run_cmd("log", *COUNTS)
        with open(self.journal, "a") as fh:
            fh.write("not json\n")
        before = self.lines()
        code, _, _ = self.run_cmd("outcome", "--fixed", "1", "--rejected", "1", "--round", "1")
        self.assertEqual(code, 0)
        after = self.lines()
        self.assertEqual(after[1:], before[1:])
        first = json.loads(after[0])
        self.assertEqual((first["fixed"], first["rejected"], first["deferred"], first["pending"]),
                         (1, 1, 0, 0))
        self.assertEqual(json.loads(after[0])["raised"], json.loads(before[0])["raised"])
        # Without --round, the last round of the branch is patched.
        self.run_cmd("outcome", "--fixed", "2", "--rejected", "0")
        self.assertEqual(json.loads(self.lines()[1])["fixed"], 2)

    def test_outcome_over_confirmed_is_refused(self):
        self.run_cmd("log", *COUNTS)
        before = self.lines()
        code, _, err = self.run_cmd("outcome", "--fixed", "2", "--rejected", "1")
        self.assertEqual(code, 2)
        self.assertIn("exceeds confirmed", err)
        self.assertEqual(self.lines(), before)
        os.remove(self.journal)
        code, _, _ = self.run_cmd("log", *COUNTS, "--fixed", "3")
        self.assertEqual(code, 2)
        self.assertFalse(os.path.exists(self.journal))

    def test_last_reports_pending_outcome(self):
        self.run_cmd("log", *COUNTS)
        self.assertEqual(json.loads(self.run_cmd("last")[1])["pending_outcome"], 2)
        self.run_cmd("outcome", "--fixed", "2", "--rejected", "0")
        self.assertNotIn("pending_outcome", json.loads(self.run_cmd("last")[1]))

    def write_rows(self, rows):
        with open(self.journal, "w") as fh:
            fh.write("".join(json.dumps(row) + "\n" for row in rows))

    def test_outcome_refuses_a_legacy_line(self):
        self.run_cmd("log", *COUNTS)
        self.write_rows([dict(self.rows()[0], legacy=True)])
        before = self.lines()
        for extra in ([], ["--round", "1"]):
            code, _, err = self.run_cmd("outcome", "--fixed", "1", "--rejected", "1", *extra)
            self.assertEqual(code, 2)
            self.assertIn("legacy", err)
            self.assertEqual(self.lines(), before)

    def test_outcome_without_round_skips_a_legacy_last_line(self):
        self.run_cmd("log", *COUNTS)
        self.run_cmd("log", *COUNTS)
        self.write_rows([self.rows()[0], dict(self.rows()[1], legacy=True)])
        self.assertEqual(self.run_cmd("outcome", "--fixed", "2", "--rejected", "0")[0], 0)
        self.assertEqual(self.rows()[0]["fixed"], 2)
        self.assertIsNone(self.rows()[1]["fixed"])

    def test_outcome_refuses_an_ambiguous_round(self):
        self.run_cmd("log", *COUNTS)
        self.run_cmd("log", *COUNTS)
        self.write_rows([self.rows()[0], dict(self.rows()[1], round=1)])
        before = self.lines()
        code, _, err = self.run_cmd("outcome", "--fixed", "1", "--rejected", "1", "--round", "1")
        self.assertEqual(code, 2)
        self.assertIn("ambiguous", err)
        self.assertEqual(self.lines(), before)

    def test_outcome_does_not_patch_another_branch(self):
        self.run_cmd("log", *COUNTS)
        self.run_cmd("log", *COUNTS, "--branch", "other")
        self.run_cmd("outcome", "--fixed", "2", "--rejected", "0")
        self.assertEqual([row["fixed"] for row in self.rows()], [2, None])
        code, _, _ = self.run_cmd("outcome", "--fixed", "1", "--rejected", "0", "--branch", "ghost")
        self.assertEqual(code, 2)

    def test_negative_counts_are_refused(self):
        self.run_cmd("log", *COUNTS)
        before = self.lines()
        code, _, err = self.run_cmd("outcome", "--fixed", "-1", "--rejected", "2")
        self.assertEqual(code, 2)
        self.assertIn("must be an integer >= 0", err)
        self.assertEqual(self.lines(), before)
        code, _, _ = self.run_cmd("log", *COUNTS, "--fixed", "-1", "--rejected", "2")
        self.assertEqual(code, 2)
        self.assertEqual(self.lines(), before)

    def test_model_must_be_a_string(self):
        self.run_cmd("log", *COUNTS)
        for bad in (5, ["opus"]):
            problems = log_run.validate(dict(self.rows()[0], model=bad))
            self.assertIn("model must be a string or null", problems)

    def test_outcome_keeps_mode_and_symlink(self):
        self.run_cmd("log", *COUNTS)
        os.chmod(self.journal, 0o640)
        link = os.path.join(self.tmp.name, "link.jsonl")
        os.symlink(self.journal, link)
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = log_run.main(["--journal", link, "outcome", "--fixed", "1", "--rejected", "1",
                                 "--repo", self.repo])
        self.assertEqual(code, 0)
        self.assertTrue(os.path.islink(link))
        self.assertEqual(os.stat(self.journal).st_mode & 0o777, 0o640)
        self.assertEqual(self.rows()[0]["fixed"], 1)

    def test_log_appended_during_outcome_is_not_lost(self):
        self.run_cmd("log", *COUNTS)
        real_replace = os.replace
        workers = []

        def racing_replace(source, target):
            worker = threading.Thread(target=log_run.main, args=(
                ["--journal", self.journal, "log", *COUNTS, "--repo", self.repo],))
            worker.start()
            workers.append(worker)
            worker.join(0.5)
            real_replace(source, target)

        with mock.patch.object(log_run.os, "replace", racing_replace):
            code, _, _ = self.run_cmd("outcome", "--fixed", "1", "--rejected", "1")
        workers[0].join(10)
        self.assertEqual(code, 0)
        self.assertEqual(len(self.rows()), 2)
        self.assertEqual(self.rows()[0]["fixed"], 1)

    def test_log_reads_the_journal_under_the_lock(self):
        held = []
        real_compare = log_run.compare_with_previous

        def spy(args, ident):
            with open(self.journal + ".lock", "w") as fh:
                try:
                    fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    held.append(False)
                except BlockingIOError:
                    held.append(True)
            return real_compare(args, ident)

        with mock.patch.object(log_run, "compare_with_previous", spy):
            self.run_cmd("log", *COUNTS)
        self.assertEqual(held, [True])

    def test_model_is_free_text_or_null(self):
        self.run_cmd("log", *COUNTS, "--model", " Opus ")
        self.run_cmd("log", *COUNTS)
        self.assertEqual([row["model"] for row in self.rows()], ["opus", None])

    def write_transcript(self, *entries):
        path = os.path.join(self.tmp.name, "session.jsonl")
        with open(path, "w") as fh:
            for entry in entries:
                fh.write(json.dumps(entry) + "\n")
        return path

    def assistant(self, stamp, output, fresh, created, read, message_id=None):
        message = {"usage": {"input_tokens": fresh, "cache_creation_input_tokens": created,
                             "cache_read_input_tokens": read, "output_tokens": output}}
        if message_id:
            message["id"] = message_id
        return {"type": "assistant", "timestamp": stamp, "message": message}

    def test_transcript_sums_assistant_turns_only(self):
        path = self.write_transcript(
            self.assistant("2026-10-29T10:00:00.000Z", 10, 1, 100, 1000),
            {"type": "user", "timestamp": "2026-10-29T10:00:30.000Z", "message": {}},
            self.assistant("2026-10-29T10:01:00.000Z", 20, 2, 200, 2000))
        self.assertEqual(self.run_cmd("log", *COUNTS, "--transcript", path)[0], 0)
        row = self.rows()[0]
        self.assertEqual((row["orch_turns"], row["orch_output"], row["orch_context"]),
                         (2, 30, 3303))

    def test_since_excludes_earlier_turns(self):
        path = self.write_transcript(
            self.assistant("2026-10-29T10:00:00.000Z", 10, 1, 100, 1000),
            {"type": "user", "timestamp": "2026-10-29T10:00:30.000Z", "message": {}},
            self.assistant("2026-10-29T10:01:00.000Z", 20, 2, 200, 2000))
        self.run_cmd("log", *COUNTS, "--transcript", path, "--since", "2026-10-29T10:00:45Z")
        row = self.rows()[0]
        self.assertEqual((row["orch_turns"], row["orch_output"], row["orch_context"]),
                         (1, 20, 2202))

    def test_message_written_on_several_lines_counts_once(self):
        path = self.write_transcript(
            self.assistant("2026-10-29T10:00:00.000Z", 10, 1, 100, 1000, "msg_a"),
            self.assistant("2026-10-29T10:00:01.000Z", 10, 1, 100, 1000, "msg_a"))
        self.run_cmd("log", *COUNTS, "--transcript", path)
        self.assertEqual(self.rows()[0]["orch_turns"], 1)

    def test_missing_transcript_gives_null_and_exit_zero(self):
        missing = os.path.join(self.tmp.name, "absent.jsonl")
        self.assertEqual(self.run_cmd("log", *COUNTS, "--transcript", missing)[0], 0)
        self.assertEqual(self.run_cmd("log", *COUNTS)[0], 0)
        for row in self.rows():
            self.assertEqual([row[key] for key in log_run.ORCH_FIELDS], [None, None, None])

    def test_auto_transcript_path_follows_cwd_and_session(self):
        with mock.patch.dict(os.environ, {"CLAUDE_CODE_SESSION_ID": "abc"}), \
                mock.patch.object(os, "getcwd", return_value="/home/me/.cfg/proj"):
            path = log_run.transcript_path("auto")
        self.assertTrue(path.endswith("/.claude/projects/-home-me--cfg-proj/abc.jsonl"))

    def test_check_reports_bad_lines_and_skips_legacy(self):
        os.makedirs(os.path.dirname(self.journal))
        self.run_cmd("log", *COUNTS)
        with open(self.journal, "a") as fh:
            fh.write('{"tier": "GO"}\n')
            fh.write('{"tier": "GO", "legacy": true}\n')
            fh.write("not json\n")
        code, out, _ = self.run_cmd("check")
        self.assertEqual(code, 1)
        self.assertIn("2 invalid line(s)", out)


if __name__ == "__main__":
    unittest.main()
