import fcntl
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import fanout_cap


def launch(session="s1", kind="blind-reviewer", tool="Agent"):
    return json.dumps({"session_id": session, "tool_name": tool,
                       "tool_input": {"subagent_type": kind, "prompt": "x"}})


class FanoutCapTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        patcher = mock.patch.object(tempfile, "tempdir", self.tmp.name)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(self.tmp.cleanup)

    def hook(self, event, now=1000.0):
        out = io.StringIO()
        code = fanout_cap.main(stdin=io.StringIO(event), stdout=out, now=now)
        self.assertEqual(code, 0)
        return json.loads(out.getvalue()) if out.getvalue() else None

    def test_sixth_reviewer_of_a_round_is_denied(self):
        for _ in range(fanout_cap.CAP):
            self.assertIsNone(self.hook(launch()))
        verdict = self.hook(launch())["hookSpecificOutput"]
        self.assertEqual(verdict["permissionDecision"], "deny")
        self.assertIn("tour de plus", verdict["permissionDecisionReason"])

    def test_plugin_namespaced_reviewer_counts(self):
        for _ in range(fanout_cap.CAP):
            self.hook(launch(kind="senior-review:blind-reviewer"))
        self.assertIsNotNone(self.hook(launch(kind="senior-review:blind-reviewer")))

    def test_other_agents_and_tools_pass_and_do_not_count(self):
        for _ in range(10):
            self.assertIsNone(self.hook(launch(kind="Explore")))
            self.assertIsNone(self.hook(launch(tool="Bash")))
        self.assertIsNone(self.hook(launch()))

    def test_reset_opens_a_new_round(self):
        for _ in range(fanout_cap.CAP):
            self.hook(launch())
        fanout_cap.reset("s1")
        self.assertIsNone(self.hook(launch()))

    def test_stale_launches_do_not_block_the_next_review(self):
        for _ in range(fanout_cap.CAP):
            self.hook(launch(), now=1000.0)
        self.assertIsNone(self.hook(launch(), now=1000.0 + fanout_cap.STALE_SECONDS))

    def test_sessions_are_counted_apart(self):
        for _ in range(fanout_cap.CAP):
            self.hook(launch(session="a"))
        self.assertIsNone(self.hook(launch(session="b")))

    def test_hook_waits_for_the_lock_held_by_a_parallel_launch(self):
        # A fan-out message fires its hooks at once; a race is too rare to
        # catch by timing, so hold the lock and check the hook waits for it.
        env = {**os.environ, "TMPDIR": self.tmp.name}
        with open(fanout_cap.state_path("par") + ".lock", "a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            proc = subprocess.Popen([sys.executable, fanout_cap.__file__],
                                    stdin=subprocess.PIPE, env=env, text=True)
            proc.stdin.write(launch(session="par"))
            proc.stdin.close()
            with self.assertRaises(subprocess.TimeoutExpired):
                proc.wait(timeout=0.5)
        self.assertEqual(proc.wait(timeout=5), 0)

    def test_unreadable_input_fails_open(self):
        self.assertIsNone(self.hook("not json"))

    def test_reset_without_state_is_silent(self):
        fanout_cap.reset("never-seen")


if __name__ == "__main__":
    unittest.main()
