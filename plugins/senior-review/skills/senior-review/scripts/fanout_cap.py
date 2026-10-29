#!/usr/bin/env python3
"""PreToolUse hook: refuse the sixth blind reviewer of a review round.

Why a hook and not a prose rule: the cap of 5 agents per round was written in
SKILL.md and still broken on 12 runs, every time on a large diff where the
skill asks for one more round instead of a wider one. Text is context, not a
constraint.

A round ends when `log_run.py log` writes its line, which calls `reset`.
Launches older than STALE_SECONDS are dropped, so a review that died before
its log line does not block the next one.

Hook input is the PreToolUse JSON on stdin. Only Agent calls whose
subagent_type is the skill's blind-reviewer count; anything else passes.

Usage (hook): python3 fanout_cap.py
"""

import contextlib
import fcntl
import json
import os
import sys
import tempfile
import time

CAP = 5
STALE_SECONDS = 3 * 3600


def main(stdin=sys.stdin, stdout=sys.stdout, now=None):
    try:
        event = json.load(stdin)
    except ValueError:
        return 0  # fail open: a broken hook must not block every agent
    if not is_reviewer_launch(event):
        return 0
    now = time.time() if now is None else now
    with locked_launches(event.get("session_id") or "nosession") as launches:
        launches[:] = [t for t in launches if now - t < STALE_SECONDS]
        if len(launches) >= CAP:
            json.dump(deny(len(launches)), stdout)
            return 0
        launches.append(now)
    return 0


def is_reviewer_launch(event):
    if event.get("tool_name") not in ("Agent", "Task"):
        return False
    kind = (event.get("tool_input") or {}).get("subagent_type") or ""
    return kind.endswith("blind-reviewer")


def deny(launched):
    reason = (
        f"senior-review : {launched} relecteurs déjà lancés dans ce tour, plafond {CAP} "
        "(refuteurs et passe finale compris). Termine ce tour (log_run.py log) et "
        "lance la suite dans un tour de plus. Si c'était la relance d'un relecteur "
        "planté, déclare sa dimension non couverte au rapport."
    )
    return {"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}


def reset(session_id):
    with contextlib.suppress(FileNotFoundError):
        os.remove(state_path(session_id))


def state_path(session_id):
    safe = "".join(c if c.isalnum() or c == "-" else "_" for c in session_id)
    return os.path.join(tempfile.gettempdir(), f"senior-review-fanout-{safe}.json")


@contextlib.contextmanager
def locked_launches(session_id):
    # Parallel Agent calls fire their hooks at the same time: lock, or two
    # hooks read the same count and both let a sixth through.
    path = state_path(session_id)
    with open(path + ".lock", "a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            with open(path) as fh:
                launches = json.load(fh)
        except (FileNotFoundError, ValueError):
            launches = []
        yield launches
        with open(path, "w") as fh:
            json.dump(launches, fh)


if __name__ == "__main__":
    sys.exit(main())
