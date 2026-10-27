import contextlib
import io
import os
import subprocess
import tempfile
import unittest

import tree_guard


def sh(repo, *cmd):
    subprocess.run(cmd, cwd=repo, check=True, capture_output=True)


class TreeGuardTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = os.path.join(self.tmp.name, "repo")
        self.state = os.path.join(self.tmp.name, "state.json")
        os.mkdir(self.repo)
        sh(self.repo, "git", "init", "-q", "-b", "main")
        sh(self.repo, "git", "config", "user.email", "t@t")
        sh(self.repo, "git", "config", "user.name", "t")
        self.write("a.txt", "one\n")
        self.write("b.txt", "two\n")
        sh(self.repo, "git", "add", ".")
        sh(self.repo, "git", "commit", "-q", "-m", "init")
        # Work in progress the reviewers must not touch.
        self.write("a.txt", "one, edited\n")
        self.write("draft.txt", "untracked\n")

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, content, root=None):
        with open(os.path.join(root or self.repo, name), "w") as fh:
            fh.write(content)

    def run_cmd(self, command):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            code = tree_guard.main([command, "--repo", self.repo, "--state", self.state])
        return code, out.getvalue()

    def check_after(self, change):
        self.assertEqual(self.run_cmd("snap")[0], 0)
        change()
        return self.run_cmd("check")

    def test_untouched_tree_passes(self):
        code, out = self.check_after(lambda: None)
        self.assertEqual((code, out.strip()), (0, "tree unchanged"))

    def test_already_modified_file_edited_again_is_drift(self):
        code, out = self.check_after(lambda: self.write("a.txt", "one, edited twice\n"))
        self.assertEqual(code, 1)
        self.assertIn("content changed: a.txt", out)

    def test_clean_tracked_file_modified_is_drift(self):
        code, out = self.check_after(lambda: self.write("b.txt", "two, edited\n"))
        self.assertEqual(code, 1)
        self.assertIn("new in status: b.txt", out)

    def test_new_untracked_file_is_drift(self):
        code, out = self.check_after(lambda: self.write("repro_test.py", "x\n"))
        self.assertEqual(code, 1)
        self.assertIn("new in status: repro_test.py", out)

    def test_deleted_file_is_drift(self):
        code, out = self.check_after(lambda: os.remove(os.path.join(self.repo, "b.txt")))
        self.assertEqual(code, 1)
        self.assertIn("new in status: b.txt", out)

    def test_reverting_work_in_progress_is_drift(self):
        # A `git checkout --` by a reviewer would erase the user's uncommitted work.
        code, out = self.check_after(lambda: sh(self.repo, "git", "checkout", "--", "a.txt"))
        self.assertEqual(code, 1)
        self.assertIn("back to clean: a.txt", out)

    def test_staging_and_committing_are_drift(self):
        code, out = self.check_after(lambda: sh(self.repo, "git", "add", "a.txt"))
        self.assertIn("index changed", out)
        code, out = self.check_after(lambda: sh(self.repo, "git", "commit", "-q", "-m", "x"))
        self.assertEqual(code, 1)
        self.assertIn("HEAD moved", out)

    def test_writes_outside_the_repo_pass(self):
        outside = os.path.join(self.tmp.name, "scratch")
        os.mkdir(outside)
        code, _ = self.check_after(lambda: self.write("crash_repro.go", "package x\n", outside))
        self.assertEqual(code, 0)

    def test_mutation_restored_before_check_passes(self):
        def mutate_then_restore():
            path = os.path.join(self.repo, "a.txt")
            with open(path) as fh:
                saved = fh.read()
            self.write("a.txt", "mutated\n")
            self.write("a.txt", saved)
        self.assertEqual(self.check_after(mutate_then_restore)[0], 0)

    def test_gitignored_build_output_passes(self):
        self.write(".gitignore", "build/\n")
        os.mkdir(os.path.join(self.repo, "build"))
        code, _ = self.check_after(lambda: self.write("cache.bin", "x", os.path.join(self.repo, "build")))
        self.assertEqual(code, 0)

    def test_check_without_snapshot_or_outside_a_repo_fails_loudly(self):
        self.assertEqual(self.run_cmd("check")[0], 2)
        self.repo = self.tmp.name
        self.assertEqual(self.run_cmd("snap")[0], 2)


if __name__ == "__main__":
    unittest.main()
