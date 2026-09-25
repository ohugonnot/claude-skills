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
        self.write_journal([run("standard", 3, 3, 0, round=2, same_diff=True, new_loc=0)])
        self.assertIn("reviewer variance", self.report())

    def test_legacy_round_never_feeds_convergence(self):
        self.write_journal([run("standard", 3, 3, 0, round=9, same_diff=True, legacy=True)])
        self.assertNotIn("reviewer variance", self.report())

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

    def test_nothing_to_decide_is_said(self):
        self.write_journal([run("quick", 2, 2, 0)])
        self.assertIn("Nothing crosses a threshold.", self.report())


if __name__ == "__main__":
    unittest.main()
