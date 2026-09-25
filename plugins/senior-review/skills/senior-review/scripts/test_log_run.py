import contextlib
import io
import json
import os
import subprocess
import tempfile
import unittest

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

    def rows(self):
        with open(self.journal) as fh:
            return [json.loads(line) for line in fh]

    def test_valid_line_is_appended_with_derived_fields(self):
        code, _, _ = self.run_cmd("log", *COUNTS)
        self.assertEqual(code, 0)
        row = self.rows()[0]
        self.assertEqual(row["project"], "shop")
        self.assertEqual(row["branch"], "feat")
        self.assertEqual(row["round"], 1)
        self.assertFalse(row["loop"])
        self.assertIsNone(row["same_diff"])

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

    def test_rewritten_previous_head_gives_null_new_loc(self):
        self.run_cmd("log", *COUNTS, "--base", "main")
        rows = self.rows()
        rows[0]["head"] = "deadbee"
        with open(self.journal, "w") as fh:
            fh.write(json.dumps(rows[0]) + "\n")
        _, out, _ = self.run_cmd("last", "--base", "main")
        self.assertIsNone(json.loads(out)["new_loc"])

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
