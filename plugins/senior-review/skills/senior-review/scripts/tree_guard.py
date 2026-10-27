#!/usr/bin/env python3
"""Check that a round of reviewers left the working tree as they found it.

Why a script and not a prose rule: a reviewer that says it changed nothing is
judging itself. Read-only tools narrow what it can do, but Bash stays open
(reviewers run tests and reproduce crashes), and Bash can write anywhere.
This compares the tree before and after, from the outside.

What counts: HEAD, the index, `git status` (untracked included, every file
listed) and a content hash of every path that status lists. Files outside the
repo and gitignored files are not seen: throwaway programs belong outside the
repo, and build caches from a test run are ignored on purpose. A tracked file
mutated then restored before the check leaves no trace, which is the
live re-run hygiene the skill asks for.

Usage:
    python3 tree_guard.py snap  [--repo DIR] [--state FILE]
    python3 tree_guard.py check [--repo DIR] [--state FILE]

Exit codes: 0 same tree, 1 drift (printed), 2 not a repo or no snapshot.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile


def git(repo, *args):
    proc = subprocess.run(["git", "-C", repo, *args], capture_output=True)
    if proc.returncode != 0:
        return None
    return proc.stdout


def file_hash(path):
    if os.path.islink(path):
        return "link:" + os.readlink(path)
    try:
        with open(path, "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()
    except FileNotFoundError:
        return "absent"
    except IsADirectoryError:
        return "dir"


def snapshot(repo):
    top = git(repo, "rev-parse", "--show-toplevel")
    if top is None:
        return None
    top = top.decode().strip()
    status = git(top, "status", "--porcelain=v1", "-z", "--untracked-files=all")
    entries = [e for e in status.decode("utf-8", "replace").split("\0") if e]
    files = {}
    paths = iter(entries)
    for entry in paths:
        if "R" in entry[:2] or "C" in entry[:2]:
            next(paths, None)  # with -z, a rename's source path follows, unprefixed
        files[entry[3:]] = file_hash(os.path.join(top, entry[3:]))
    head = git(top, "rev-parse", "--verify", "-q", "HEAD")
    index = git(top, "ls-files", "--stage", "-z") or b""
    return {
        "repo": top,
        "head": head.decode().strip() if head else None,
        "index": hashlib.sha256(index).hexdigest(),
        "status": sorted(entries),
        "files": files,
    }


def drift(before, after):
    out = []
    if before["head"] != after["head"]:
        out.append(f"HEAD moved: {before['head']} -> {after['head']}")
    if before["index"] != after["index"]:
        out.append("index changed (something was staged or unstaged)")
    for path in sorted(set(before["files"]) | set(after["files"])):
        was, now = before["files"].get(path), after["files"].get(path)
        if was == now:
            continue
        if was is None:
            out.append(f"new in status: {path}")
        elif now is None:
            out.append(f"back to clean: {path}")
        else:
            out.append(f"content changed: {path}")
    if not out and before["status"] != after["status"]:
        out.append("git status changed")
    return out


def default_state(repo):
    key = hashlib.sha256(os.path.abspath(repo).encode()).hexdigest()[:12]
    return os.path.join(tempfile.gettempdir(), f"senior-review-tree-{key}.json")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("command", choices=("snap", "check"))
    parser.add_argument("--repo", default=os.getcwd())
    parser.add_argument("--state", default=None)
    args = parser.parse_args(argv)

    now = snapshot(args.repo)
    if now is None:
        print(f"not a git repository: {args.repo}", file=sys.stderr)
        return 2
    state = args.state or default_state(now["repo"])

    if args.command == "snap":
        with open(state, "w") as fh:
            json.dump(now, fh)
        print(f"snapshot: {len(now['files'])} paths in status, state {state}")
        return 0

    try:
        with open(state) as fh:
            before = json.load(fh)
    except FileNotFoundError:
        print(f"no snapshot at {state}: run snap before the reviewers", file=sys.stderr)
        return 2
    changes = drift(before, now)
    if not changes:
        print("tree unchanged")
        return 0
    print("TREE DRIFT, stop the loop and show this to the user:")
    for line in changes:
        print(f"- {line}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
