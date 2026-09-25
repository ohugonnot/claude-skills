#!/usr/bin/env python3
"""Read the run journal and the skill memories, print what deserves a decision.

Why a script: the two trend analyses done so far were computed by hand in a
session, and the memory caps written in SKILL.md were never enforced because
nothing ever ran at the moment they were crossed. This prints numbers and
flags; the model turns them into at most 3 proposals, the user decides.

Lines flagged `legacy` (written before log_run.py) still count for cost when
their counters add up, never for convergence (their `round` was typed by hand).

Usage:
    python3 learn.py [--journal PATH] [--memory-dir DIR]

Twin lessons are not detected here: word overlap between two entries that
describe the same mechanism measured 0.14 at best, below any usable threshold.
"""

import argparse
import collections
import datetime
import json
import os
import re
import sys

import log_run

LESSON_TAGS = {"spec", "correctness", "security", "design", "tests", "perf", "harness"}
MISS_TAGS = {"bruit", "manqué", "coût"}
# (file, byte cap, entry cap, max chars per entry). Caps come from SKILL.md step 7.
MEMORY_RULES = {
    "lessons": ("senior-review-lessons.md", 10240, 40, 600),
    "misses": ("senior-review-misses.md", 8192, 40, 300),
    "candidates": ("senior-review-lessons-candidates.md", 16384, None, 600),
}
CANDIDATE_TTL_DAYS = 90
MISS_N1_TTL_DAYS = 60
PRECISION_FLOOR = 0.65
GATE_CEILING = 0.30


def counters_ok(row):
    keys = ("raised", "confirmed", "dropped_gate", "refuted_panel")
    if not all(isinstance(row.get(k), int) for k in keys):
        return False
    return row["raised"] == row["confirmed"] + row["dropped_gate"] + row["refuted_panel"]


def agents_bucket(agents):
    if agents <= 1:
        return "1"
    if agents <= 3:
        return "2-3"
    if agents <= 5:
        return "4-5"
    return "6+"


def ratio(part, whole):
    return f"{part / whole:.0%}" if whole else "-"


def journal_report(rows):
    out = ["## Journal", ""]
    usable = [r for r in rows if counters_ok(r)]
    legacy = sum(1 for r in rows if r.get("legacy"))
    no_tokens = sum(1 for r in rows if not r.get("tokens"))
    out.append(f"{len(rows)} runs, {len(usable)} with consistent counters, {legacy} legacy, "
               f"{no_tokens} without tokens.")
    out.append("")

    out += ["| tier | runs | precision | gate drop | panel refuted | tokens/finding |",
            "|---|---|---|---|---|---|"]
    flags = []
    by_tier = collections.defaultdict(list)
    for row in usable:
        by_tier[row.get("tier") or "?"].append(row)
    for tier in list(log_run.TIERS) + ["?"]:
        tier_rows = by_tier.get(tier)
        if not tier_rows:
            continue
        raised = sum(r["raised"] for r in tier_rows)
        confirmed = sum(r["confirmed"] for r in tier_rows)
        gate = sum(r["dropped_gate"] for r in tier_rows)
        panel = sum(r["refuted_panel"] for r in tier_rows)
        paid = [r for r in tier_rows if r.get("tokens")]
        per_finding = (sum(r["tokens"] for r in paid) // max(1, sum(r["confirmed"] for r in paid))
                       if paid else None)
        out.append(f"| {tier} | {len(tier_rows)} | {ratio(confirmed, raised)} | {ratio(gate, raised)} "
                   f"| {ratio(panel, confirmed + panel)} | {f'{per_finding // 1000}k' if per_finding else '-'} |")
        if raised >= 20 and confirmed / raised < PRECISION_FLOOR:
            flags.append(f"precision of `{tier}` is {ratio(confirmed, raised)}: tighten "
                         "\"ce qu'on ne flague pas\" or the routing")
        if raised >= 20 and gate / raised > GATE_CEILING:
            flags.append(f"`{tier}` reviewers over-flag: the gate drops {ratio(gate, raised)}")
        if len(tier_rows) >= 20 and tier in ("standard", "deep") and panel == 0:
            flags.append(f"the panel refuted nothing on {len(tier_rows)} `{tier}` runs: dead weight?")
    out.append("")

    out += ["| agents | runs | confirmed/run | tokens/finding |", "|---|---|---|---|"]
    by_agents = collections.defaultdict(list)
    for row in usable:
        if isinstance(row.get("agents"), int) and row.get("tokens"):
            by_agents[agents_bucket(row["agents"])].append(row)
    for bucket in ("1", "2-3", "4-5", "6+"):
        bucket_rows = by_agents.get(bucket)
        if not bucket_rows:
            continue
        confirmed = sum(r["confirmed"] for r in bucket_rows)
        tokens = sum(r["tokens"] for r in bucket_rows)
        out.append(f"| {bucket} | {len(bucket_rows)} | {confirmed / len(bucket_rows):.1f} "
                   f"| {tokens // max(1, confirmed) // 1000}k |")
    out.append("")

    raised = sum(r["raised"] for r in usable)
    out_of_scope = sum(r.get("out_of_scope") or 0 for r in usable)
    out.append(f"Out of scope: {out_of_scope} ledger entries for {raised} raised findings "
               f"({ratio(out_of_scope, raised)}).")

    measured = [r for r in rows if not r.get("legacy") and "same_diff" in r]
    variance = [r for r in measured if r.get("same_diff") and r["confirmed"] > 0]
    out.append(f"Convergence: {len(measured)} runs carry a diff identity.")
    for row in variance:
        flags.append(f"{row['project']}/{row['branch']} round {row['round']}: {row['confirmed']} "
                     "confirmed on an unchanged diff, reviewer variance (confirmation tier skipped?)")
    by_branch = collections.defaultdict(list)
    for row in measured:
        by_branch[(row["project"], row["branch"])].append(row)
    for (project, branch), branch_rows in by_branch.items():
        if len(branch_rows) >= 3:
            steps = ", ".join(f"r{r['round']} +{r.get('new_loc') if r.get('new_loc') is not None else '?'}"
                              f"loc {r['confirmed']}f" for r in branch_rows)
            out.append(f"- {project}/{branch}: {steps}")
    return out, flags


def entries(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as fh:
        return [line.rstrip("\n") for line in fh if line.startswith("- [")]


def seen(entry):
    match = re.search(r"vu sur (\d+)", entry)
    return int(match.group(1)) if match else None


def dated(entry):
    found = re.findall(r"\d{4}-\d{2}-\d{2}", entry)
    return datetime.date.fromisoformat(found[-1]) if found else None


def memory_report(memory_dir, today):
    out = ["## Memories", ""]
    flags = []
    loaded = {}
    for kind, (name, byte_cap, entry_cap, max_chars) in MEMORY_RULES.items():
        path = os.path.join(memory_dir, name)
        items = entries(path)
        loaded[kind] = items
        size = os.path.getsize(path) if os.path.exists(path) else 0
        tags = MISS_TAGS if kind == "misses" else LESSON_TAGS
        bad_tags = [e for e in items if re.match(r"- \[([^\]]+)\]", e).group(1) not in tags]
        too_long = [e for e in items if len(e) > max_chars]
        n1 = [e for e in items if seen(e) == 1]
        out.append(f"- {kind}: {len(items)} entries, {size / 1024:.1f}/{byte_cap // 1024} Ko, "
                   f"{len(n1)} seen once, {len(too_long)} over {max_chars} chars")
        if size > byte_cap:
            flags.append(f"{kind} is {size / 1024:.1f} Ko, cap {byte_cap // 1024} Ko")
        if entry_cap and len(items) > entry_cap:
            flags.append(f"{kind} has {len(items)} entries, cap {entry_cap}")
        for entry in bad_tags:
            flags.append(f"{kind}: unknown tag in `{entry[:60]}`")
        for entry in too_long:
            flags.append(f"{kind}: condense ({len(entry)} chars) `{entry[:60]}`")

    for entry in loaded["candidates"]:
        when = dated(entry)
        if when is None:
            flags.append(f"candidates: undated `{entry[:60]}`")
        elif (today - when).days > CANDIDATE_TTL_DAYS:
            flags.append(f"candidates: expired ({when}) `{entry[:60]}`")
    for entry in loaded["misses"]:
        when = dated(entry)
        if seen(entry) == 1 and when and (today - when).days > MISS_N1_TTL_DAYS:
            flags.append(f"misses: seen once, since {when} `{entry[:60]}`")
    return out, flags


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--journal", default=log_run.JOURNAL)
    parser.add_argument("--memory-dir", default=os.path.dirname(log_run.JOURNAL))
    parser.add_argument("--today", type=datetime.date.fromisoformat, default=datetime.date.today())
    args = parser.parse_args(argv)

    rows = [row for _, row in log_run.read_journal(args.journal) if row]
    lines, flags = journal_report(rows)
    memory_lines, memory_flags = memory_report(args.memory_dir, args.today)
    print("\n".join(lines + [""] + memory_lines))
    print("\n## To decide\n")
    for flag in flags + memory_flags:
        print(f"- {flag}")
    if not flags and not memory_flags:
        print("Nothing crosses a threshold.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
