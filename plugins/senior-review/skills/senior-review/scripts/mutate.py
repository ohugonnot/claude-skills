#!/usr/bin/env python3
"""Run mutation red-checks from a spec, safely, on a working tree that may hold
uncommitted work.

Why a script and not inline commands: three failure modes cost real review
rounds, and all three are mechanical.

1. A crash between "mutate" and "restore" leaves the repo mutated. Here every
   target file is snapshotted to a temp dir BEFORE the first edit, restore runs
   in a finally block, and the restore is verified by hash.
2. A test filter that matches nothing reports SURVIVED, which reads as a
   coverage hole that does not exist. Here the baseline run must actually
   execute tests, or the mutation is skipped and flagged.
3. A summary printed only at the end is lost when the run dies. Here each
   result is flushed as it happens.

git is never used: `git checkout`/`restore` would wipe uncommitted work, and
writing to the index can make a later commit ship the mutated version.

Spec (JSON, list of objects):
    [
      {
        "name": "reset of the discount field",
        "file": "src/cart.py",
        "old": "item.discount = None",       # must appear EXACTLY once
        "new": "",                            # "" deletes the anchor
        "cmd": ["pytest", "-q", "tests/test_cart.py::test_copy_drops_discount"],
        "expect": "KILLED"                    # or "SURVIVED" (a known gap)
      }
    ]

Optional per-mutation keys:
    "cwd"            working dir for cmd (default: --root)
    "timeout"        seconds for cmd (default: --timeout)
    "must_match"     regex the BASELINE output must contain, e.g. "PASS: test_copy"
                     Strongest guard against a filter that runs nothing.

Usage:
    python3 mutate.py --spec mutations.json --root /path/to/repo
    python3 mutate.py --spec mutations.json --root . --dry-run

Exit code: 0 when every mutation matched its expectation, 1 otherwise.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

# A test runner that matches no test usually still exits 0. Treat these as
# "nothing ran" so a bad filter never masquerades as a surviving mutant.
NO_TESTS_MARKERS = [
    "no tests to run",
    "no test files",
    "no tests ran",
    "collected 0 items",
    "0 passing",
    "Ran 0 tests",
]


def sha(path: str) -> str:
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def log(line: str) -> None:
    print(line, flush=True)


def run(cmd: list[str], cwd: str, timeout: int) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout
        )
        return proc.returncode, proc.stdout + proc.stderr
    except subprocess.TimeoutExpired:
        return 124, f"<timeout after {timeout}s>"
    except FileNotFoundError as exc:
        return 127, f"<command not found: {exc}>"


def nothing_ran(output: str) -> bool:
    low = output.lower()
    return any(marker.lower() in low for marker in NO_TESTS_MARKERS)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True, help="JSON file describing the mutations")
    parser.add_argument("--root", default=".", help="repo root the files are relative to")
    parser.add_argument("--timeout", type=int, default=600, help="default per-command timeout")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="check anchors and baselines, mutate nothing",
    )
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    with open(args.spec) as handle:
        spec = json.load(handle)
    if not isinstance(spec, list) or not spec:
        log("spec must be a non-empty JSON list")
        return 1

    # --- snapshot every target BEFORE touching anything -------------------
    targets = sorted({item["file"] for item in spec})
    snapdir = tempfile.mkdtemp(prefix="mutate-pristine-")
    pristine: dict[str, str] = {}
    for rel in targets:
        src = os.path.join(root, rel)
        if not os.path.isfile(src):
            log(f"!! target missing, aborting before any edit: {rel}")
            shutil.rmtree(snapdir, ignore_errors=True)
            return 1
        dst = os.path.join(snapdir, rel.replace(os.sep, "__"))
        shutil.copy2(src, dst)
        pristine[rel] = dst
    log(f"[snapshot] {len(targets)} file(s) copied outside the repo: {snapdir}")

    results: list[tuple[str, str, str]] = []
    mismatches: list[str] = []

    try:
        for item in spec:
            name = item["name"]
            rel = item["file"]
            path = os.path.join(root, rel)
            cwd = os.path.join(root, item.get("cwd", "."))
            timeout = int(item.get("timeout", args.timeout))
            expect = item["expect"].upper()

            source = open(path).read()
            hits = source.count(item["old"])
            if hits != 1:
                log(f"?? {name:44s} anchor found {hits}x, skipped")
                results.append((name, "ANCHOR", expect))
                mismatches.append(name)
                continue

            # --- baseline: the command must really run tests, and pass ----
            code, output = run(item["cmd"], cwd, timeout)
            if nothing_ran(output):
                log(f"?? {name:44s} baseline ran NO test (bad filter?), skipped")
                results.append((name, "NO-TESTS", expect))
                mismatches.append(name)
                continue
            if code != 0:
                log(f"?? {name:44s} baseline already RED, skipped")
                results.append((name, "RED-BASELINE", expect))
                mismatches.append(name)
                continue
            if "must_match" in item and not re.search(item["must_match"], output):
                log(f"?? {name:44s} baseline output lacks {item['must_match']!r}, skipped")
                results.append((name, "NO-MATCH", expect))
                mismatches.append(name)
                continue

            if args.dry_run:
                log(f".. {name:44s} anchor ok, baseline green (dry-run)")
                results.append((name, "DRY", expect))
                continue

            # --- mutate, test, always restore -----------------------------
            try:
                with open(path, "w") as handle:
                    handle.write(source.replace(item["old"], item["new"], 1))
                code, _ = run(item["cmd"], cwd, timeout)
                got = "SURVIVED" if code == 0 else "KILLED"
            finally:
                shutil.copy2(pristine[rel], path)
                if sha(path) != sha(pristine[rel]):
                    log(f"!! RESTORE FAILED for {rel}: copy back from {pristine[rel]}")
                    return 1

            flag = "ok" if got == expect else "!!"
            if got != expect:
                mismatches.append(name)
            log(f"{flag} {name:44s} expected={expect:9s} got={got}")
            results.append((name, got, expect))

        log("")
        log(f">>> {len(results)} mutation(s), {len(mismatches)} mismatch(es)")
        for name in mismatches:
            log(f"    - {name}")
        if mismatches:
            log("")
            log("A mismatch is a claim to re-measure, not a finding to report:")
            log("ANCHOR/NO-TESTS/NO-MATCH mean the harness misfired, not the tests.")
        return 0 if not mismatches else 1
    finally:
        for rel, snap in pristine.items():
            path = os.path.join(root, rel)
            if os.path.isfile(path) and sha(path) != sha(snap):
                shutil.copy2(snap, path)
                log(f"[restore] {rel} put back from snapshot")
        log(f"[snapshot] kept for inspection: {snapdir}")


if __name__ == "__main__":
    sys.exit(main())
