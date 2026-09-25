import contextlib
import io
import json
import os
import tempfile
import unittest

import log_run

RUN = ["--slug", "add-csv-export", "--status", "SUCCESS", "--tier", "standard",
       "--mode", "in_place", "--iterations", "2", "--radar-avg", "8.4",
       "--criticals-left", "0", "--escalations", "0", "--branch", "feat"]


class LogRunTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.journal = os.path.join(self.tmp.name, "memory", "feature_loop_runs.jsonl")

    def tearDown(self):
        self.tmp.cleanup()

    def run_cmd(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = log_run.main(["--journal", self.journal, *argv])
        return code, out.getvalue(), err.getvalue()

    def rows(self):
        with open(self.journal) as fh:
            return [json.loads(line) for line in fh]

    def replace(self, flag, value):
        run = list(RUN)
        run[run.index(flag) + 1] = value
        return run

    def test_valid_run_has_every_anomaly_counter_even_at_zero(self):
        self.assertEqual(self.run_cmd("log", *RUN, "--rollbacks", "1", "--live-smoke-fail")[0], 0)
        row = self.rows()[0]
        self.assertEqual(row["anomalies"]["rollbacks"], 1)
        self.assertEqual(row["anomalies"]["vacuous_tests"], 0)
        self.assertTrue(row["anomalies"]["live_smoke_fail"])
        self.assertIsNone(row["subagent_tokens_total"])
        self.assertEqual(log_run.validate(row), [])

    def test_tier_case_is_normalised_but_spelling_is_not(self):
        self.assertEqual(self.run_cmd("log", *self.replace("--tier", "SENSIBLE"))[0], 0)
        self.assertEqual(self.rows()[0]["tier"], "sensible")
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            self.run_cmd("log", *self.replace("--tier", "complex"))

    def test_radar_is_required_unless_aborted(self):
        run = RUN[:RUN.index("--radar-avg")] + RUN[RUN.index("--radar-avg") + 2:]
        code, _, err = self.run_cmd("log", *run)
        self.assertEqual(code, 2)
        self.assertIn("radar_avg is required", err)
        self.assertFalse(os.path.exists(self.journal))
        aborted = list(run)
        aborted[aborted.index("--status") + 1] = "ABORTED"
        self.assertEqual(self.run_cmd("log", *aborted)[0], 0)

    def test_radar_out_of_scale_is_refused(self):
        self.assertEqual(self.run_cmd("log", *self.replace("--radar-avg", "84"))[0], 2)

    def test_axes_below_becomes_a_list(self):
        self.run_cmd("log", *RUN, "--axes-below", "UX, a11y")
        self.assertEqual(self.rows()[0]["axes_below"], ["UX", "a11y"])

    def test_check_flags_invented_anomalies_and_skips_legacy(self):
        self.run_cmd("log", *RUN)
        row = self.rows()[0]
        row["anomalies"]["target_pivoted"] = 1
        with open(self.journal, "a") as fh:
            fh.write(json.dumps(row) + "\n")
            fh.write(json.dumps({"slug": "old", "legacy": True}) + "\n")
        code, out, _ = self.run_cmd("check")
        self.assertEqual(code, 1)
        self.assertIn("unknown anomalies ['target_pivoted']", out)
        self.assertIn("1 invalid line(s)", out)

    def test_default_journal_matches_claude_project_dir_naming(self):
        self.assertTrue(log_run.default_journal("/home/x/work/acme/shop_v2").endswith(
            "/.claude/projects/-home-x-work-acme-shop-v2/memory/feature_loop_runs.jsonl"))


if __name__ == "__main__":
    unittest.main()
