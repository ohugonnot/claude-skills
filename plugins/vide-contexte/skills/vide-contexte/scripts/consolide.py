#!/usr/bin/env python3
"""Measure a project memory folder and print what a consolidation pass should look at.

Why a script: one manual pass on a real folder (about 400 files) found 5 dead links and 15 filename-only links where
a filename-based check had reported none, because a link resolves on the target's
`name:`, not on its filename. The mechanical part is measured here, the model judges
staleness against the forge and the code, the user validates.

Usage:
    python3 consolide.py [--memory-dir DIR] [--index-cap BYTES] [--file-cap BYTES]
"""

import argparse
import os
import re
import subprocess
import sys

INDEX_CAP = 15_000
FILE_CAP = 8_000
# A slug is a bare word: `[[:space:]]` in a quoted bash regex is not a link.
LINK_RE = re.compile(r"\[\[([\w-]+)\]\]")
INDEX_LINK_RE = re.compile(r"\]\(([^)\s]+\.md)\)")
NAME_RE = re.compile(r"^name:\s*\"?([^\"\n]+?)\"?\s*$", re.MULTILINE)
# Session-log headings: pass numbers, "resume" banners, a date in the title.
JOURNAL_HEADING_RE = re.compile(
    r"^#{1,4} .*(\bPasse \d|\bPass \d|REPRISE|EN COURS|\d{4}-\d{2}-\d{2})", re.MULTILINE)
FORGE_REF_RE = re.compile(r"(?<![\w/])(![0-9]{2,}|#[0-9]{2,})\b")
LEDGER_PREFIX = "arbitrages-"
# Owned by senior-review: branch ledgers and the repo learnings have their own lifecycle and cap.
SKILL_OWNED = ("senior_review_learnings.md",)


def default_memory_dir():
    """Claude Code keys the project memory on the launch directory (git top level)."""
    try:
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True,
                             text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        top = os.getcwd()
    project = re.sub(r"[^A-Za-z0-9]", "-", top)
    return os.path.expanduser(f"~/.claude/projects/{project}/memory")


def load(memory_dir):
    files = {}
    for entry in sorted(os.listdir(memory_dir)):
        path = os.path.join(memory_dir, entry)
        if entry.endswith(".md") and os.path.isfile(path):
            with open(path, encoding="utf-8") as fh:
                files[entry] = fh.read()
    return files


def is_index(filename):
    return filename == "MEMORY.md" or filename.startswith("index_")


def in_scope(filename):
    return not (is_index(filename) or filename.startswith(LEDGER_PREFIX) or filename in SKILL_OWNED)


def names_of(files):
    names = {}
    for filename, text in files.items():
        match = NAME_RE.search(text.split("\n---", 1)[0]) if text.startswith("---") else None
        if match:
            names[match.group(1).strip()] = filename
    return names


def link_report(files, names):
    """Dead links, and links that only resolve on a filename (they look fine but are not)."""
    stems = {os.path.splitext(f)[0]: f for f in files}
    dead, by_filename = [], []
    for filename, text in files.items():
        if filename.startswith(LEDGER_PREFIX):
            continue
        for slug in LINK_RE.findall(text):
            # Ledgers carry no name: a link to one resolves on its filename by design.
            if slug in names or slug.startswith(LEDGER_PREFIX) and slug in stems:
                continue
            target = stems.get(slug) or stems.get(slug.replace("-", "_"))
            (by_filename if target else dead).append((filename, slug))
    return dead, by_filename


def index_report(files):
    """Index lines pointing at missing files, and memories no index lists."""
    listed, missing = set(), []
    for filename, text in files.items():
        if not is_index(filename):
            continue
        for target in INDEX_LINK_RE.findall(text):
            target = os.path.basename(target)
            listed.add(target)
            if target not in files:
                missing.append((filename, target))
    orphans = [f for f in files if in_scope(f) and f not in listed]
    return missing, orphans


def report(memory_dir, index_cap=INDEX_CAP, file_cap=FILE_CAP):
    files = load(memory_dir)
    names = names_of(files)
    total = sum(len(text.encode("utf-8")) for text in files.values())
    index_size = len(files.get("MEMORY.md", "").encode("utf-8"))
    dead, by_filename = link_report(files, names)
    missing, orphans = index_report(files)
    heavy = sorted(((len(t.encode("utf-8")), f) for f, t in files.items()
                    if len(t.encode("utf-8")) > file_cap and in_scope(f)), reverse=True)
    journals = sorted(f for f, t in files.items()
                      if len(JOURNAL_HEADING_RE.findall(t)) >= 2 and in_scope(f))
    forge = sorted(((len(set(FORGE_REF_RE.findall(t))), f) for f, t in files.items()
                    if in_scope(f) and FORGE_REF_RE.search(t)), reverse=True)
    unnamed = sorted(f for f in files if in_scope(f) and f not in names.values())

    out = ["## Corpus", "",
           f"- {len(files)} files, {total} bytes",
           f"- MEMORY.md: {index_size}/{index_cap} bytes",
           f"- ledgers ({LEDGER_PREFIX}*): {sum(f.startswith(LEDGER_PREFIX) for f in files)}"]
    sections = [
        ("Dead links (no file carries this name)", [f"{f}: [[{s}]]" for f, s in dead]),
        ("Links resolving on a filename only (fix to the target's name:)",
         [f"{f}: [[{s}]]" for f, s in by_filename]),
        ("Index lines to missing files", [f"{i} -> {t}" for i, t in missing]),
        ("Memories listed in no index", orphans),
        ("Memories without a name: (never linkable)", unnamed),
        (f"Over {file_cap} bytes (condense: decisions, why, live pitfalls)",
         [f"{f}: {size} bytes" for size, f in heavy]),
        ("Session-log shape (dated or numbered headings)", journals),
        ("Forge references to check (distinct !N/#N per file)",
         [f"{f}: {count}" for count, f in forge]),
    ]
    for title, items in sections:
        out += ["", f"## {title}", ""] + ([f"- {item}" for item in items] or ["none"])

    flags = []
    if index_size > index_cap:
        flags.append(f"MEMORY.md is {index_size} bytes, cap {index_cap}")
    if dead or by_filename:
        flags.append(f"{len(dead)} dead links, {len(by_filename)} filename-only links")
    if missing:
        flags.append(f"{len(missing)} index lines point at missing files")
    if heavy:
        flags.append(f"{len(heavy)} memories over {file_cap} bytes")
    return out, flags


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--memory-dir", default=None)
    parser.add_argument("--index-cap", type=int, default=INDEX_CAP)
    parser.add_argument("--file-cap", type=int, default=FILE_CAP)
    args = parser.parse_args(argv)
    memory_dir = args.memory_dir or default_memory_dir()
    if not os.path.isdir(memory_dir):
        print(f"no memory folder at {memory_dir}")
        return 2
    lines, flags = report(memory_dir, args.index_cap, args.file_cap)
    print("\n".join(lines))
    print("\n## To decide\n")
    print("\n".join(f"- {flag}" for flag in flags) or "Nothing crosses a threshold.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
