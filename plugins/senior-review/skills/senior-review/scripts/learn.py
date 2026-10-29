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
# (file, byte cap, entry cap, max chars per entry). Caps come from reference/memory.md.
MEMORY_RULES = {
    "lessons": ("senior-review-lessons.md", 10240, 40, 600),
    "misses": ("senior-review-misses.md", 8192, 40, 300),
    "candidates": ("senior-review-lessons-candidates.md", 16384, None, 600),
}
# Loaded at step 1.7 of every review of that repo, so it needs a cap too.
REPO_LEARNINGS_CAP = 15360
CANDIDATE_TTL_DAYS = 90
MISS_N1_TTL_DAYS = 60
PRECISION_FLOOR = 0.65
GATE_CEILING = 0.30
ACCEPTANCE_FLOOR = 0.70
ACCEPTANCE_MIN_JUDGED = 20
OUTCOME_TTL_DAYS = 14
MODEL_MIN_RUNS = 10
# Version of the cap "at most 5 agents per round, reviewers included".
FANOUT_CAP = 5
FANOUT_CAP_SINCE = (1, 16, 0)


def version_tuple(text):
    try:
        return tuple(int(part) for part in text.split("."))
    except (AttributeError, ValueError):
        return None


def outcome_known(row):
    """Legacy lines typed `fixed` or `deferred` by hand with their own meaning.
    A half-known outcome would skew the ratio, so fixed and rejected go together."""
    return not row.get("legacy") and all(isinstance(row.get(k), int) for k in ("fixed", "rejected"))


def outcome_sums(rows):
    """Totals over the rows whose outcome is known; the others carry no signal."""
    known = [r for r in rows if outcome_known(r)]
    sums = {key: sum(r.get(key) or 0 for r in known) for key in log_run.OUTCOMES}
    sums.update(runs=len(known), confirmed=sum(r["confirmed"] for r in known))
    return sums


def acceptance(sums):
    """What the user kept out of what they judged; routed findings are not a judgement."""
    return ratio(sums["fixed"], sums["fixed"] + sums["rejected"])


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


def journal_report(rows, today):
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

    out += ["| tier | runs renseignés | confirmed | fixed | rejected | deferred | acceptance |",
            "|---|---|---|---|---|---|---|"]
    for tier in list(log_run.TIERS) + ["?"]:
        sums = outcome_sums(by_tier.get(tier, []))
        if not sums["runs"]:
            continue
        out.append(f"| {tier} | {sums['runs']} | {sums['confirmed']} | {sums['fixed']} "
                   f"| {sums['rejected']} | {sums['deferred']} | {acceptance(sums)} |")
        judged = sums["fixed"] + sums["rejected"]
        if judged >= ACCEPTANCE_MIN_JUDGED and sums["fixed"] / judged < ACCEPTANCE_FLOOR:
            flags.append(f"acceptance of `{tier}` is {acceptance(sums)} on {judged} judged "
                         "findings: the user rejects what the gate lets through, tighten "
                         "\"ce qu'on ne flague pas\"")
    sums = outcome_sums(usable)
    out.append("")
    out.append(f"Outcome known for {sums['runs']} of {len(usable)} runs.")
    stale = [r for r in rows if (r.get("pending") or 0) > 0 and r.get("date")
             and (today - datetime.date.fromisoformat(r["date"])).days > OUTCOME_TTL_DAYS]
    if stale:
        flags.append(f"{len(stale)} runs without outcome for over {OUTCOME_TTL_DAYS} days: "
                     "answer step 0 at the next review or run `log_run.py outcome`")
    over_cap = [r for r in rows if not r.get("legacy") and isinstance(r.get("agents"), int)
                and r["agents"] > FANOUT_CAP
                and (version_tuple(r.get("skill_version")) or ()) >= FANOUT_CAP_SINCE]
    if over_cap:
        flags.append(f"{len(over_cap)} runs above {FANOUT_CAP} agents since "
                     f"{'.'.join(map(str, FANOUT_CAP_SINCE))}: the cap is not held")
    out.append("")

    model_rows = collections.defaultdict(list)
    for row in usable:
        if isinstance(row.get("model"), str):
            model_rows[row["model"]].append(row)
    kept = {model: rs for model, rs in model_rows.items() if len(rs) >= MODEL_MIN_RUNS}
    out += ["| model | runs | precision | acceptance |", "|---|---|---|---|"]
    for model, model_rs in sorted(kept.items()):
        out.append(f"| {model} | {len(model_rs)} "
                   f"| {ratio(sum(r['confirmed'] for r in model_rs), sum(r['raised'] for r in model_rs))} "
                   f"| {acceptance(outcome_sums(model_rs))} |")
    out.append(f"{sum(len(rs) for rs in model_rows.values())} runs carry a model, "
               f"{len(kept)} with at least {MODEL_MIN_RUNS}.")
    out.append("")

    out += ["| agents | runs | confirmed/run | tokens/finding | confirmed/100 LOC |",
            "|---|---|---|---|---|"]
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
        sized = [r for r in bucket_rows if isinstance(r.get("loc"), int) and r["loc"] > 0]
        density = (f"{100 * sum(r['confirmed'] for r in sized) / sum(r['loc'] for r in sized):.1f}"
                   if sized else "-")
        out.append(f"| {bucket} | {len(bucket_rows)} | {confirmed / len(bucket_rows):.1f} "
                   f"| {tokens // max(1, confirmed) // 1000}k | {density} |")
    out.append("")

    raised = sum(r["raised"] for r in usable)
    out_of_scope = sum(r.get("out_of_scope") or 0 for r in usable)
    out.append(f"Out of scope: {out_of_scope} ledger entries for {raised} raised findings "
               f"({ratio(out_of_scope, raised)}).")

    measured = [r for r in rows if not r.get("legacy") and r.get("diff_sha")]
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


def default_repo_learnings():
    """The repo memory Claude Code keys on the launch directory (git top level)."""
    top = log_run.git(os.getcwd(), "rev-parse", "--show-toplevel") or os.getcwd()
    project = re.sub(r"[^A-Za-z0-9]", "-", top)
    return os.path.expanduser(f"~/.claude/projects/{project}/memory/senior_review_learnings.md")


def repo_learnings_report(path):
    if not os.path.exists(path):
        return [], []
    size = os.path.getsize(path)
    with open(path, encoding="utf-8") as fh:
        long_entries = [line for line in fh if line.startswith("- ") and len(line) > 400]
    out = [f"- repo learnings: {size / 1024:.1f}/{REPO_LEARNINGS_CAP // 1024} Ko, "
           f"{len(long_entries)} over 400 chars ({path})"]
    flags = []
    if size > REPO_LEARNINGS_CAP:
        flags.append(f"repo learnings is {size / 1024:.1f} Ko, cap {REPO_LEARNINGS_CAP // 1024} Ko")
    return out, flags


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--journal", default=log_run.JOURNAL)
    parser.add_argument("--memory-dir", default=os.path.dirname(log_run.JOURNAL))
    parser.add_argument("--today", type=datetime.date.fromisoformat, default=datetime.date.today())
    parser.add_argument("--repo-learnings", default=None)
    args = parser.parse_args(argv)

    rows = [row for _, row in log_run.read_journal(args.journal) if row]
    lines, flags = journal_report(rows, args.today)
    memory_lines, memory_flags = memory_report(args.memory_dir, args.today)
    repo_lines, repo_flags = repo_learnings_report(args.repo_learnings or default_repo_learnings())
    memory_lines += repo_lines
    memory_flags += repo_flags
    print("\n".join(lines + [""] + memory_lines))
    print("\n## To decide\n")
    for flag in flags + memory_flags:
        print(f"- {flag}")
    if not flags and not memory_flags:
        print("Nothing crosses a threshold.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
