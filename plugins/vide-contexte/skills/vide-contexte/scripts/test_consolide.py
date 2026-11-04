import contextlib
import datetime
import io
import json
import os
import tempfile
import unittest

import consolide


def memory(name, body="", mtype="project"):
    return f"---\nname: {name}\ndescription: \"x\"\nmetadata:\n  type: {mtype}\n---\n\n{body}\n"


class ConsolideTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, filename, text):
        with open(os.path.join(self.dir, filename), "w", encoding="utf-8") as fh:
            fh.write(text)

    def test_link_resolves_on_name_not_on_filename(self):
        self.write("project_alpha.md", memory("alpha-decision", "see [[beta-trap]]"))
        self.write("reference_beta.md", memory(
            "beta-trap", "see [[project_alpha]] and [[gone]], grep '[[:space:]]', [[arbitrages-12-x]]"))
        self.write("arbitrages-12-x.md", "# Arbitrages\n- see [[gone-too]]\n")
        files = consolide.load(self.dir)
        dead, by_filename = consolide.link_report(files, consolide.names_of(files))
        self.assertEqual(dead, [("reference_beta.md", "gone")])
        self.assertEqual(by_filename, [("reference_beta.md", "project_alpha")])

    def test_index_missing_target_and_orphans(self):
        self.write("MEMORY.md", "- [A](project_alpha.md)\n- [X](project_deleted.md)\n")
        self.write("index_products.md", "- [B](reference_beta.md)\n")
        self.write("project_alpha.md", memory("alpha"))
        self.write("reference_beta.md", memory("beta"))
        self.write("project_lost.md", memory("lost"))
        self.write("arbitrages-12-branch.md", "# Arbitrages\n")
        missing, orphans = consolide.index_report(consolide.load(self.dir))
        self.assertEqual(missing, [("MEMORY.md", "project_deleted.md")])
        self.assertEqual(orphans, ["project_lost.md"])

    def test_flags_heavy_journal_and_forge_references(self):
        log = "## Passe 5 (2026-07-07)\nx\n## REPRISE EN COURS\ny\nMR !314, issue #143, !314 again\n"
        self.write("MEMORY.md", "- [J](project_journal.md)\n")
        self.write("project_journal.md", memory("journal", log + "z" * 9000))
        self.write("arbitrages-12-branch.md", "# Arbitrages\n" + log + "z" * 9000)
        self.write("senior_review_learnings.md", memory("learnings", "z" * 14000))
        lines, flags = consolide.report(self.dir)
        text = "\n".join(lines)
        self.assertIn("project_journal.md: 2", text)
        self.assertIn("## Session-log shape", text)
        self.assertTrue(any("1 memories over 8000 bytes" in flag for flag in flags))
        self.assertNotIn("arbitrages-12-branch.md", text)

    def test_clean_folder_raises_no_flag(self):
        self.write("MEMORY.md", "- [A](project_alpha.md)\n")
        self.write("project_alpha.md", memory("alpha", "a decision and its why"))
        _, flags = consolide.report(self.dir)
        self.assertEqual(flags, [])

    def test_main_on_missing_folder_exits_2(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(consolide.main(["--memory-dir", os.path.join(self.dir, "nope")]), 2)


class VerdictCacheTest(unittest.TestCase):
    NOW = datetime.date(2026, 11, 4)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = os.path.join(self.tmp.name, "memory")
        self.repo = os.path.join(self.tmp.name, "repo")
        os.makedirs(self.dir)
        os.makedirs(self.repo)
        self.cache = os.path.join(self.tmp.name, "skill-memory", "verdicts.json")

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, filename, text):
        with open(os.path.join(self.dir, filename), "w", encoding="utf-8") as fh:
            fh.write(text)

    def record(self, filename, verdict="garder", reason="decision still true in code", **kwargs):
        kwargs.setdefault("now", self.NOW)
        consolide.record_verdict(self.cache, self.dir, filename, verdict, reason, self.repo, **kwargs)

    def status(self, now=None):
        files = {f: t for f, t in consolide.load(self.dir).items() if consolide.in_scope(f)}
        return consolide.cache_status(files, consolide.load_cache(self.cache), self.repo, now or self.NOW)

    def test_recorded_verdict_is_served_until_the_file_changes(self):
        self.write("project_a.md", memory("a", "a decision"))
        self.assertEqual(self.status(), ([], ["project_a.md"]))
        self.record("project_a.md")
        self.assertEqual(self.status(), (["project_a.md"], []))
        self.write("project_a.md", memory("a", "a decision, edited"))
        self.assertEqual(self.status(), ([], ["project_a.md"]))

    def test_reason_is_mandatory_and_not_a_bare_label(self):
        self.write("project_a.md", memory("a"))
        for bad in ("", "   ", "unchanged", "Superseded.", " UNCHANGED "):
            with self.assertRaises(ValueError, msg=repr(bad)):
                self.record("project_a.md", reason=bad)
        with self.assertRaises(ValueError):
            self.record("project_a.md", verdict=" ")
        self.assertFalse(os.path.exists(self.cache))

    def test_criteria_version_bump_invalidates_everything(self):
        self.write("project_a.md", memory("a"))
        self.record("project_a.md")
        original = consolide.CRITERIA_VERSION
        consolide.CRITERIA_VERSION = original + 1
        try:
            self.assertEqual(self.status(), ([], ["project_a.md"]))
        finally:
            consolide.CRITERIA_VERSION = original

    def test_verdict_expires_after_ninety_days(self):
        self.write("project_a.md", memory("a"))
        self.record("project_a.md")
        self.assertEqual(self.status(self.NOW + datetime.timedelta(days=90))[1], [])
        self.assertEqual(self.status(self.NOW + datetime.timedelta(days=91))[1], ["project_a.md"])

    def test_cited_path_that_disappears_invalidates_the_verdict(self):
        target = os.path.join(self.repo, "svc", "handler.go")
        os.makedirs(os.path.dirname(target))
        open(target, "w").close()
        self.write("project_a.md", memory("a", "see `svc/handler.go` and `svc/never_existed.go`"))
        self.record("project_a.md")
        self.assertEqual(self.status()[1], [])
        os.remove(target)
        self.assertEqual(self.status()[1], ["project_a.md"])

    def test_unreachable_forge_gives_unverifiable_and_is_never_served(self):
        self.write("project_a.md", memory("a", "MR !314 is in review"))
        self.record("project_a.md", verdict="périmé", reason="glab api failed: connection refused",
                    forge_unreachable=True)
        entry = next(iter(json.load(open(self.cache, encoding="utf-8"))["verdicts"].values()))
        self.assertEqual(entry["verdict"], "non vérifiable")
        self.assertEqual(self.status(), ([], ["project_a.md"]))

    def test_corrupt_cache_file_reads_as_empty(self):
        os.makedirs(os.path.dirname(self.cache))
        with open(self.cache, "w") as fh:
            fh.write("{not json")
        self.assertEqual(consolide.load_cache(self.cache), {"verdicts": {}})

    def test_second_run_judges_nothing_and_an_edit_brings_back_one(self):
        self.write("MEMORY.md", "- [A](project_a.md)\n- [B](project_b.md)\n")
        self.write("project_a.md", memory("a", "one"))
        self.write("project_b.md", memory("b", "two"))

        def run():
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                consolide.main(["--memory-dir", self.dir, "--cache", self.cache, "--repo-root", self.repo])
            return buffer.getvalue()

        self.assertIn("0 en cache, 2 à juger", run())
        for filename in ("project_a.md", "project_b.md"):
            self.assertEqual(consolide.main(
                ["--memory-dir", self.dir, "--cache", self.cache, "--repo-root", self.repo,
                 "--record", filename, "--verdict", "garder", "--reason", "still matches the code"]), 0)
        self.assertIn("2 en cache, 0 à juger", run())
        self.write("project_b.md", memory("b", "two, edited"))
        self.assertIn("1 en cache, 1 à juger", run())

    def test_record_cli_refuses_a_bare_reason_with_exit_2(self):
        self.write("project_a.md", memory("a"))
        with contextlib.redirect_stdout(io.StringIO()):
            code = consolide.main(["--memory-dir", self.dir, "--cache", self.cache, "--repo-root", self.repo,
                                   "--record", "project_a.md", "--verdict", "garder", "--reason", "unchanged"])
        self.assertEqual(code, 2)

    def test_index_files_are_not_counted(self):
        self.write("MEMORY.md", "- [A](project_a.md)\n")
        self.write("project_a.md", memory("a"))
        self.assertEqual(self.status(), ([], ["project_a.md"]))


if __name__ == "__main__":
    unittest.main()
