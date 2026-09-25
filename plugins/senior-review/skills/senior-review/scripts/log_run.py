#!/usr/bin/env python3
"""Append one line per review to the run journal, and read it back.

Why a script and not a prose rule: on the first 123 lines written by hand,
only 46 matched the schema. `tier` had 12 spellings, `verdict` 11, `project`
12, and 42 lines broke the counter invariant. A prose rule does not hold an
enum; argparse does.

Everything that git or the journal already knows is derived here, never typed
by the model: date, project, branch, head, diff identity, round, new_loc.
`round` used to be declared and was wrong (one branch went 1,2,1,1,3,3,2,9,2).

Subcommands:
    log    validate and append one line; exit 2 and write nothing if invalid
    last   print what the previous review of this branch looked like, and
           whether the diff under review changed since (confirmation tier)
    check  list journal lines that do not match the schema

Usage:
    python3 log_run.py last [--base origin/main]
    python3 log_run.py log --tier standard --loc 227 --raised 18 --confirmed 14 \\
        --dropped-gate 4 --refuted-panel 0 --agents 4 --tokens 544918 \\
        --verdict request-changes [--base origin/main] [--loop]
    python3 log_run.py check
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys

JOURNAL = os.path.expanduser("~/.claude/skill-memory/senior-review-runs.jsonl")
TIERS = ("quick", "standard", "deep", "confirmation")
VERDICTS = ("approve", "approve-after-fixes", "request-changes", "needs-discussion")
COUNTERS = ("loc", "raised", "confirmed", "dropped_gate", "refuted_panel",
            "settled", "out_of_scope", "agents")
# Byte caps come from SKILL.md step 7; candidates has none, its size is shown anyway.
MEMORIES = (("senior-review-lessons.md", 10240),
            ("senior-review-misses.md", 8192),
            ("senior-review-lessons-candidates.md", None))


def git(repo, *args):
    """Return stdout, or None when git fails (not a repo, unknown ref...)."""
    proc = subprocess.run(["git", "-C", repo, *args], capture_output=True)
    if proc.returncode != 0:
        return None
    return proc.stdout.decode("utf-8", "replace").strip()


def project_name(repo):
    remote = git(repo, "remote", "get-url", "origin")
    if remote:
        return re.sub(r"\.git$", "", remote.rstrip("/")).rsplit("/", 1)[-1].rsplit(":", 1)[-1]
    top = git(repo, "rev-parse", "--show-toplevel") or os.path.abspath(repo)
    return os.path.basename(top)


def diff_sha(repo, base, staged):
    """Identity of the code under review. A merge of the base without content
    conflict keeps `base...HEAD` identical, which is what confirmation wants."""
    if base:
        diff = git(repo, "diff", f"{base}...HEAD")
    elif staged:
        diff = git(repo, "diff", "--cached")
    else:
        # `git diff HEAD` misses new files, so hash untracked contents too.
        diff = git(repo, "diff", "HEAD")
        untracked = git(repo, "ls-files", "--others", "--exclude-standard")
        if diff is not None and untracked:
            parts = [diff]
            for path in sorted(untracked.splitlines()):
                try:
                    with open(os.path.join(repo, path), "rb") as fh:
                        parts.append(path + "\0" + hashlib.sha256(fh.read()).hexdigest())
                except OSError:
                    parts.append(path)
            diff = "\n".join(parts)
    if diff is None:
        return None
    return hashlib.sha256(diff.encode()).hexdigest()[:16]


def read_journal(path):
    """Yield (line_number, row) for each parsable line; bad JSON gives row=None."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as fh:
        for number, line in enumerate(fh, 1):
            if not line.strip():
                continue
            try:
                yield number, json.loads(line)
            except json.JSONDecodeError:
                yield number, None


def identity(args):
    repo = args.repo
    return {
        "project": args.project or project_name(repo),
        "branch": args.branch or git(repo, "rev-parse", "--abbrev-ref", "HEAD"),
        "head": git(repo, "rev-parse", "--short", "HEAD"),
        "diff_sha": diff_sha(repo, args.base, args.staged),
    }


def compare_with_previous(args, ident):
    previous = [row for _, row in read_journal(args.journal)
                if row and row.get("project") == ident["project"]
                and row.get("branch") == ident["branch"]]
    last = previous[-1] if previous else None
    new_loc = None
    same_diff = None
    if last:
        if last.get("diff_sha") and ident["diff_sha"]:
            same_diff = last["diff_sha"] == ident["diff_sha"]
        # Working-tree reviews change files, not commits: same_diff covers them.
        if (args.base or args.staged) and last.get("head") and ident["head"]:
            stat = git(args.repo, "diff", "--shortstat", last["head"], "HEAD")
            if stat is not None:
                new_loc = sum(int(n) for n in re.findall(r"(\d+) (?:insertion|deletion)", stat))
    return {"round": len(previous) + 1, "new_loc": new_loc,
            "same_diff": same_diff, "previous": last}


def skill_version():
    skill_md = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "SKILL.md")
    try:
        with open(skill_md, encoding="utf-8") as fh:
            match = re.search(r"skill_version : ([\d.]+)", fh.read())
    except OSError:
        return None
    return match.group(1) if match else None


def validate(row):
    """Return the list of problems; empty means the line is usable."""
    problems = []
    if row.get("tier") not in TIERS:
        problems.append(f"tier {row.get('tier')!r} not in {TIERS}")
    if row.get("verdict") not in VERDICTS:
        problems.append(f"verdict {row.get('verdict')!r} not in {VERDICTS}")
    if not isinstance(row.get("loop"), bool):
        problems.append("loop must be a boolean")
    for key in COUNTERS:
        value = row.get(key)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            problems.append(f"{key} must be an integer >= 0")
    if row.get("tokens") is not None and not isinstance(row.get("tokens"), int):
        problems.append("tokens must be an integer or null")
    if not row.get("project") or not row.get("branch"):
        problems.append("project and branch are required")
    if not problems and row["raised"] != row["confirmed"] + row["dropped_gate"] + row["refuted_panel"]:
        problems.append(f"raised ({row['raised']}) != confirmed + dropped_gate + refuted_panel "
                        f"({row['confirmed']} + {row['dropped_gate']} + {row['refuted_panel']}): recount")
    return problems


def memory_sizes(journal):
    folder = os.path.dirname(os.path.abspath(journal))
    parts = []
    for name, cap in MEMORIES:
        path = os.path.join(folder, name)
        if not os.path.exists(path):
            continue
        size = os.path.getsize(path)
        label = name.replace("senior-review-", "").replace(".md", "")
        if cap:
            flag = " OVER CAP" if size > cap else ""
            parts.append(f"{label} {size / 1024:.1f}/{cap // 1024} Ko{flag}")
        else:
            parts.append(f"{label} {size / 1024:.1f} Ko")
    return ", ".join(parts)


def cmd_log(args):
    ident = identity(args)
    known = compare_with_previous(args, ident)
    row = {
        "date": datetime.date.today().isoformat(),
        "project": ident["project"], "branch": ident["branch"],
        "head": ident["head"], "diff_sha": ident["diff_sha"],
        "round": known["round"], "new_loc": known["new_loc"], "same_diff": known["same_diff"],
        "tier": args.tier, "loop": args.loop, "loc": args.loc,
        "raised": args.raised, "confirmed": args.confirmed,
        "dropped_gate": args.dropped_gate, "refuted_panel": args.refuted_panel,
        "settled": args.settled, "out_of_scope": args.out_of_scope,
        "agents": args.agents, "tokens": args.tokens, "verdict": args.verdict,
        "skill_version": skill_version(),
    }
    problems = validate(row)
    if problems:
        for problem in problems:
            print(f"[learn] run NOT logged: {problem}", file=sys.stderr)
        return 2
    os.makedirs(os.path.dirname(os.path.abspath(args.journal)), exist_ok=True)
    with open(args.journal, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=True) + "\n")
    print(f"[learn] run logged: {row['project']}/{row['branch']} round {row['round']}, "
          f"{row['confirmed']}/{row['raised']} confirmed")
    sizes = memory_sizes(args.journal)
    if sizes:
        print(f"[learn] memories: {sizes}")
    return 0


def cmd_last(args):
    ident = identity(args)
    known = compare_with_previous(args, ident)
    print(json.dumps({"project": ident["project"], "branch": ident["branch"],
                      "next_round": known["round"], "same_diff": known["same_diff"],
                      "new_loc": known["new_loc"], "previous": known["previous"]},
                     ensure_ascii=False))
    return 0


def cmd_check(args):
    bad = 0
    for number, row in read_journal(args.journal):
        if row is None:
            problems = ["not valid JSON"]
        elif row.get("legacy"):
            continue
        else:
            problems = validate(row)
        if problems:
            bad += 1
            print(f"line {number}: {'; '.join(problems)}")
    print(f"{bad} invalid line(s)")
    return 1 if bad else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--journal", default=JOURNAL)
    sub = parser.add_subparsers(dest="command", required=True)

    def target_args(p):
        p.add_argument("--repo", default=".")
        p.add_argument("--base", help="ref of a branch review (git diff base...HEAD)")
        p.add_argument("--staged", action="store_true")
        p.add_argument("--project", help="override; default is the origin remote name")
        p.add_argument("--branch", help="override, e.g. pr-42; default is the current branch")

    log = sub.add_parser("log")
    target_args(log)
    log.add_argument("--tier", required=True, choices=TIERS)
    log.add_argument("--loop", action="store_true")
    log.add_argument("--verdict", required=True, choices=VERDICTS)
    for counter in ("loc", "raised", "confirmed", "dropped-gate", "refuted-panel", "agents"):
        log.add_argument(f"--{counter}", required=True, type=int)
    log.add_argument("--settled", type=int, default=0)
    log.add_argument("--out-of-scope", type=int, default=0)
    # Optional on purpose: a required field pushes the model to invent a number.
    log.add_argument("--tokens", type=int)

    target_args(sub.add_parser("last"))
    sub.add_parser("check")

    args = parser.parse_args(argv)
    return {"log": cmd_log, "last": cmd_last, "check": cmd_check}[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
