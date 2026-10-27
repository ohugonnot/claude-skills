import contextlib
import io
import json
import os
import tempfile
import unittest

import learn


def run(tier, raised, confirmed, gate, panel=0, agents=2, tokens=100000, **extra):
    row = {"date": "2026-09-01", "project": "shop", "branch": "feat", "tier": tier,
           "loop": False, "loc": 50, "raised": raised, "confirmed": confirmed,
           "dropped_gate": gate, "refuted_panel": panel, "settled": 0, "out_of_scope": 0,
           "agents": agents, "tokens": tokens, "verdict": "approve"}
    row.update(extra)
    return row


class LearnTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name
        self.journal = os.path.join(self.dir, "runs.jsonl")

    def tearDown(self):
        self.tmp.cleanup()

    def write_journal(self, rows):
        with open(self.journal, "w") as fh:
            for row in rows:
                fh.write(json.dumps(row) + "\n")

    def write_memory(self, name, lines):
        with open(os.path.join(self.dir, name), "w") as fh:
            fh.write("# title\n\n" + "\n".join(lines) + "\n")

    def report(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            learn.main(["--journal", self.journal, "--memory-dir", self.dir, "--today", "2026-12-31"])
        return out.getvalue()

    def test_precision_per_tier_ignores_inconsistent_counters(self):
        self.write_journal([run("standard", 10, 5, 5)] * 3
                           + [run("standard", 10, 10, 5, legacy=True)])
        report = self.report()
        self.assertIn("| standard | 3 | 50% | 50% |", report)
        self.assertIn("precision of `standard` is 50%", report)
        self.assertIn("over-flag", report)

    def test_legacy_with_consistent_counters_counts_for_cost(self):
        self.write_journal([run("quick", 2, 2, 0, legacy=True, agents=1, tokens=60000)])
        self.assertIn("| 1 | 1 | 2.0 | 30k |", self.report())

    def test_findings_on_unchanged_diff_are_flagged_as_variance(self):
        self.write_journal([run("standard", 3, 3, 0, round=2, same_diff=True, new_loc=0,
                                diff_sha="abc")])
        self.assertIn("reviewer variance", self.report())

    def test_legacy_round_never_feeds_convergence(self):
        self.write_journal([run("standard", 3, 3, 0, round=9, same_diff=True, legacy=True)])
        self.assertNotIn("reviewer variance", self.report())

    def test_run_without_diff_identity_is_not_measured(self):
        self.write_journal([run("standard", 1, 1, 0, diff_sha=None, same_diff=None),
                            run("standard", 1, 1, 0, diff_sha="abc", same_diff=False)])
        self.assertIn("Convergence: 1 runs carry a diff identity", self.report())

    def test_memory_caps_long_entries_and_bad_tags(self):
        self.write_journal([])
        self.write_memory("senior-review-misses.md",
                          ["- [manque] typo tag — *vu sur 1 branche* · 2026-09-01"]
                          + ["- [bruit] " + "x" * 400 + " — *vu sur 2 branches*"] * 25)
        report = self.report()
        self.assertIn("misses is", report)
        self.assertIn("unknown tag in `- [manque]", report)
        self.assertIn("condense", report)
        self.assertIn("misses: seen once, since 2026-09-01", report)

    def test_repo_learnings_over_cap_is_flagged(self):
        self.write_journal([])
        repo_learnings = os.path.join(self.dir, "senior_review_learnings.md")
        with open(repo_learnings, "w") as fh:
            fh.write("- **codebase_fact** : " + "x" * 16000 + "\n")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            learn.main(["--journal", self.journal, "--memory-dir", self.dir,
                        "--repo-learnings", repo_learnings, "--today", "2026-12-31"])
        self.assertIn("repo learnings is 15.6 Ko, cap 15 Ko", out.getvalue())

    def test_candidates_expire_or_need_a_date(self):
        self.write_journal([])
        self.write_memory("senior-review-lessons-candidates.md",
                          ["- [tests] old one — *vu sur 1 run* · 2026-08-01",
                           "- [tests] fresh one — *vu sur 1 run* · 2026-12-01",
                           "- [tests] no date — *vu sur 1 run*"])
        report = self.report()
        self.assertIn("expired (2026-08-01)", report)
        self.assertIn("undated `- [tests] no date", report)
        self.assertNotIn("fresh one", report)

    def test_acceptance_ignores_rows_without_outcome(self):
        self.write_journal([run("standard", 10, 10, 0, fixed=6, rejected=2, deferred=1),
                            run("standard", 10, 10, 0, fixed=None, rejected=None, deferred=None),
                            run("standard", 10, 10, 0)])
        report = self.report()
        self.assertIn("| standard | 1 | 10 | 6 | 2 | 1 | 75% |", report)
        self.assertNotIn("acceptance of `standard`", report)

    def test_low_acceptance_and_stale_outcomes_are_flagged(self):
        self.write_journal([run("standard", 20, 20, 0, fixed=5, rejected=15, deferred=0, pending=0),
                            run("standard", 2, 2, 0, pending=2),
                            run("standard", 2, 2, 0, pending=2)])
        report = self.report()
        self.assertIn("acceptance of `standard` is 25%", report)
        self.assertIn("2 runs without outcome for over 14 days", report)

    def test_acceptance_flag_needs_20_judged_findings(self):
        self.write_journal([run("standard", 20, 20, 0, fixed=4, rejected=15, deferred=1)])
        self.assertNotIn("acceptance of", self.report())
        self.write_journal([run("standard", 20, 20, 0, fixed=5, rejected=15, deferred=0)])
        self.assertIn("acceptance of `standard` is 25%", self.report())

    def test_findings_all_routed_give_no_acceptance_flag(self):
        self.write_journal([run("standard", 20, 20, 0, fixed=0, rejected=0, deferred=20)])
        report = self.report()
        self.assertNotIn("acceptance of", report)
        self.assertIn("| standard | 1 | 20 | 0 | 0 | 20 | - |", report)

    def test_partial_outcome_is_not_known(self):
        self.write_journal([run("standard", 10, 10, 0, fixed=3, rejected=None, deferred=None),
                            run("standard", 10, 10, 0, fixed=6, rejected=2, deferred=None)])
        self.assertIn("| standard | 1 | 10 | 6 | 2 | 0 | 75% |", self.report())

    def test_legacy_lines_never_feed_acceptance(self):
        self.write_journal([run("standard", 10, 10, 0, fixed=9, rejected=0, legacy=True),
                            run("standard", 10, 10, 0, fixed=6, rejected=2)])
        self.assertIn("| standard | 1 | 10 | 6 | 2 | 0 | 75% |", self.report())

    def test_outcome_flag_waits_more_than_14_days_and_needs_pending(self):
        self.write_journal([run("standard", 2, 2, 0, pending=2, date="2026-12-17")])
        self.assertNotIn("without outcome", self.report())
        self.write_journal([run("standard", 2, 2, 0, pending=0, date="2026-09-01")])
        self.assertNotIn("without outcome", self.report())
        self.write_journal([run("standard", 2, 2, 0, pending=2, date="2026-12-16")])
        self.assertIn("1 runs without outcome for over 14 days", self.report())

    def test_fanout_over_cap_is_flagged(self):
        self.write_journal([run("standard", 3, 3, 0, agents=7, skill_version="1.20.0"),
                            run("standard", 3, 3, 0, agents=7, skill_version="1.15.0"),
                            run("standard", 3, 3, 0, agents=7),
                            run("standard", 3, 3, 0, agents=5, skill_version="1.26.0")])
        self.assertIn("1 runs above 5 agents since 1.16.0", self.report())

    def test_agents_table_has_density_column(self):
        self.write_journal([run("standard", 4, 4, 0, agents=2, loc=100),
                            run("standard", 4, 4, 0, agents=2, loc=300),
                            run("standard", 4, 4, 0, agents=2, loc=None)])
        self.assertIn("| 2-3 | 3 | 4.0 | 25k | 2.0 |", self.report())

    def test_models_under_ten_runs_are_left_out(self):
        self.write_journal([run("standard", 4, 3, 1, model="opus", fixed=2, rejected=0)] * 10
                           + [run("standard", 4, 4, 0, model="haiku")] * 3)
        report = self.report()
        self.assertIn("| opus | 10 | 75% | 100% |", report)
        self.assertNotIn("| haiku |", report)

    def test_nothing_to_decide_is_said(self):
        self.write_journal([run("quick", 2, 2, 0)])
        self.assertIn("Nothing crosses a threshold.", self.report())


if __name__ == "__main__":
    unittest.main()
