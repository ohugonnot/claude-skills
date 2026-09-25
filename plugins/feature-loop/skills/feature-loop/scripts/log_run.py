#!/usr/bin/env python3
"""Append one line per finished run to the feature-loop runs-log.

Why a script and not a prose rule: on the first 22 lines written by hand,
one matched the schema. `tier` came as complexe/complex/SENSIBLE,
`subagent_tokens_total` (the cost measure `learn` compares versions with)
was missing on 19, and 8 anomaly keys were invented once and never again.
argparse holds an enum; a paragraph does not.

Every terminal status is logged, not only SUCCESS: a log with 22 SUCCESS
out of 22 says more about what gets written than about the skill.

Usage:
    python3 log_run.py log --slug add-csv-export --status SUCCESS --tier standard \\
        --mode in_place --iterations 2 --radar-avg 8.4 --criticals-left 0 \\
        --escalations 0 [--axes-below UX,a11y] [--duration-min 14] [--tokens 110000] \\
        [--paranoid] [--vacuous-tests N ...] [--note "..."]
    python3 log_run.py check [--journal PATH]
"""

import argparse
import datetime
import json
import os
import re
import subprocess
import sys

STATUSES = ("SUCCESS", "MAX_ITERATIONS", "ABORTED")
TIERS = ("trivial", "standard", "complexe", "sensible")
MODES = ("in_place", "worktree")
COUNT_ANOMALIES = ("vacuous_tests", "redcheck_inconclusive", "rollbacks", "plan_revisions",
                   "evidence_invalid_pct", "agent_b_retries")
FLAG_ANOMALIES = ("notes_ignored", "live_smoke_fail")


def default_journal(cwd):
    # Claude Code names a project memory dir after the cwd, every non-alnum char as "-".
    encoded = re.sub(r"[^A-Za-z0-9]", "-", os.path.abspath(cwd))
    return os.path.expanduser(f"~/.claude/projects/{encoded}/memory/feature_loop_runs.jsonl")


def current_branch(repo):
    proc = subprocess.run(["git", "-C", repo, "rev-parse", "--abbrev-ref", "HEAD"],
                          capture_output=True, text=True)
    return proc.stdout.strip() if proc.returncode == 0 else None


def skill_version():
    skill_md = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "SKILL.md")
    try:
        with open(skill_md, encoding="utf-8") as fh:
            match = re.search(r"skill_version : ([\d.]+)", fh.read())
    except OSError:
        return None
    return match.group(1) if match else None


def is_count(value):
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def validate(row):
    problems = []
    for key, allowed in (("status", STATUSES), ("tier", TIERS), ("mode", MODES)):
        if row.get(key) not in allowed:
            problems.append(f"{key} {row.get(key)!r} not in {allowed}")
    if not row.get("slug"):
        problems.append("slug is required")
    for key in ("iterations", "criticals_left", "escalations"):
        if not is_count(row.get(key)):
            problems.append(f"{key} must be an integer >= 0")
    radar = row.get("radar_avg")
    if radar is None and row.get("status") != "ABORTED":
        problems.append("radar_avg is required unless the run was ABORTED")
    if radar is not None and not (isinstance(radar, (int, float)) and 0 <= radar <= 10):
        problems.append("radar_avg must be between 0 and 10")
    if not isinstance(row.get("axes_below"), list):
        problems.append("axes_below must be a list")
    if not isinstance(row.get("paranoid"), bool):
        problems.append("paranoid must be a boolean")
    for key in ("duration_min", "subagent_tokens_total"):
        if row.get(key) is not None and not is_count(row.get(key)):
            problems.append(f"{key} must be an integer >= 0 or null")
    anomalies = row.get("anomalies")
    if not isinstance(anomalies, dict):
        problems.append("anomalies must be an object")
    else:
        for key in COUNT_ANOMALIES:
            if not is_count(anomalies.get(key)):
                problems.append(f"anomalies.{key} must be an integer >= 0")
        for key in FLAG_ANOMALIES:
            if not isinstance(anomalies.get(key), bool):
                problems.append(f"anomalies.{key} must be a boolean")
        unknown = set(anomalies) - set(COUNT_ANOMALIES) - set(FLAG_ANOMALIES)
        if unknown:
            problems.append(f"unknown anomalies {sorted(unknown)}: use --note")
    return problems


def cmd_log(args):
    row = {
        "slug": args.slug,
        "date": datetime.date.today().isoformat(),
        "status": args.status,
        "iterations": args.iterations,
        "radar_avg": args.radar_avg,
        "axes_below": [axis.strip() for axis in args.axes_below.split(",") if axis.strip()],
        "criticals_left": args.criticals_left,
        "duration_min": args.duration_min,
        "subagent_tokens_total": args.tokens,
        "mode": args.mode,
        "branch": args.branch or current_branch(args.repo),
        "paranoid": args.paranoid,
        "tier": args.tier,
        "escalations": args.escalations,
        "skill_version": skill_version(),
        "anomalies": {key: getattr(args, key) for key in COUNT_ANOMALIES + FLAG_ANOMALIES},
    }
    if args.note:
        row["note"] = args.note
    problems = validate(row)
    if problems:
        for problem in problems:
            print(f"[runs] run NOT logged: {problem}", file=sys.stderr)
        return 2
    journal = args.journal or default_journal(args.repo)
    os.makedirs(os.path.dirname(journal), exist_ok=True)
    with open(journal, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"[runs] run logged in {journal}")
    return 0


def cmd_check(args):
    journal = args.journal or default_journal(args.repo)
    bad = 0
    if os.path.exists(journal):
        with open(journal, encoding="utf-8") as fh:
            for number, line in enumerate(fh, 1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    row, problems = None, ["not valid JSON"]
                if row is not None:
                    if row.get("legacy"):
                        continue
                    problems = validate(row)
                if problems:
                    bad += 1
                    print(f"line {number}: {'; '.join(problems)}")
    print(f"{bad} invalid line(s)")
    return 1 if bad else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--journal", help="default: the project memory dir of --repo")
    parser.add_argument("--repo", default=".")
    sub = parser.add_subparsers(dest="command", required=True)

    log = sub.add_parser("log")
    log.add_argument("--slug", required=True)
    log.add_argument("--status", required=True, choices=STATUSES)
    log.add_argument("--tier", required=True, type=str.lower, choices=TIERS)
    log.add_argument("--mode", required=True, choices=MODES)
    log.add_argument("--iterations", required=True, type=int)
    log.add_argument("--radar-avg", type=float)
    log.add_argument("--axes-below", default="")
    log.add_argument("--criticals-left", required=True, type=int)
    log.add_argument("--escalations", required=True, type=int)
    log.add_argument("--duration-min", type=int)
    # Optional on purpose: a required field pushes the model to invent a number.
    log.add_argument("--tokens", type=int, help="subagent_tokens_total")
    log.add_argument("--paranoid", action="store_true")
    log.add_argument("--branch")
    log.add_argument("--note", help="anything the counters below do not cover")
    for key in COUNT_ANOMALIES:
        log.add_argument(f"--{key.replace('_', '-')}", dest=key, type=int, default=0)
    for key in FLAG_ANOMALIES:
        log.add_argument(f"--{key.replace('_', '-')}", dest=key, action="store_true")

    sub.add_parser("check")
    args = parser.parse_args(argv)
    return {"log": cmd_log, "check": cmd_check}[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
