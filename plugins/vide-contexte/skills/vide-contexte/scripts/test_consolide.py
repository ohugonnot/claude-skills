import contextlib
import io
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


if __name__ == "__main__":
    unittest.main()
