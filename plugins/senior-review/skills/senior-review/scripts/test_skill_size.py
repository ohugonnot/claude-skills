"""Guards on SKILL.md weight and shape.

SKILL.md is read on every review and kept only partly after compaction, so its
size is a recurring cost: it reached 70 KB before anyone measured it.
"""

import os
import re
import unittest

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_PATH = os.path.join(SKILL_DIR, "SKILL.md")

MAX_SKILL_BYTES = 29_000
# A line this long is a paragraph that dodges the line-count rule.
MAX_LINE_BYTES = 1_200
MAX_DESCRIPTION_CHARS = 1_024
# Compaction keeps about the first 5,000 tokens of an invoked skill. This file
# runs near 4.2 bytes per token and was seen cut near 20,500 bytes.
COMPACTION_KEPT_BYTES = 19_000
# Claude Code ignores unknown keys without a word, so a typo goes unnoticed.
ALLOWED_FRONTMATTER_KEYS = {
    "name", "description", "when_to_use", "argument-hint", "arguments",
    "disable-model-invocation", "user-invocable", "allowed-tools", "model",
    "effort", "context", "agent", "hooks", "paths", "shell", "version",
    "license", "compatibility", "metadata",
}


def read_skill():
    with open(SKILL_PATH, "rb") as fh:
        return fh.read()


def frontmatter(text):
    match = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not match:
        raise AssertionError("SKILL.md has no frontmatter")
    return match.group(1)


def frontmatter_keys(block):
    return [m.group(1) for m in re.finditer(r"^([A-Za-z_][\w-]*):", block, re.M)]


def description(block):
    lines = block.split("\n")
    for i, line in enumerate(lines):
        if not line.startswith("description:"):
            continue
        inline = line[len("description:"):].strip()
        if inline not in (">", ">-", "|", "|-"):
            return inline.strip("'\"")
        folded = []
        for cont in lines[i + 1:]:
            if cont and not cont.startswith(" "):
                break
            folded.append(cont.strip())
        return " ".join(part for part in folded if part)
    raise AssertionError("frontmatter has no description")


class SkillSizeTest(unittest.TestCase):
    def setUp(self):
        self.raw = read_skill()
        self.text = self.raw.decode("utf-8")

    def test_skill_stays_under_byte_cap(self):
        self.assertLessEqual(len(self.raw), MAX_SKILL_BYTES,
                             f"SKILL.md is {len(self.raw)} bytes; move rationale or "
                             "rare branches to reference/")

    def test_no_line_is_a_hidden_paragraph(self):
        too_long = [(n, len(line)) for n, line in enumerate(self.raw.split(b"\n"), 1)
                    if len(line) > MAX_LINE_BYTES]
        self.assertEqual(too_long, [], "lines (number, bytes) over the cap")

    def test_every_reference_file_is_pointed_from_skill(self):
        missing = []
        for root, _, files in os.walk(os.path.join(SKILL_DIR, "reference")):
            for name in files:
                if not name.endswith(".md"):
                    continue
                rel = os.path.relpath(os.path.join(root, name), SKILL_DIR)
                if rel not in self.text:
                    missing.append(rel)
        self.assertEqual(sorted(missing), [], "reference files nobody can reach")

    def test_frontmatter_uses_documented_keys_only(self):
        keys = frontmatter_keys(frontmatter(self.text))
        self.assertIn("name", keys)
        self.assertIn("description", keys)
        self.assertEqual(sorted(set(keys) - ALLOWED_FRONTMATTER_KEYS), [])

    def test_description_fits_the_standard(self):
        text = description(frontmatter(self.text))
        self.assertLessEqual(len(text), MAX_DESCRIPTION_CHARS,
                             f"description is {len(text)} characters")

    def test_steps_survive_compaction(self):
        # A review cut mid-pipeline skipped its run log: every step must fit,
        # so the first section after the steps starts before the cut.
        after_steps = re.split(r"^## Étape .*$", self.text, flags=re.M)[-1]
        next_section = re.search(r"^## ", after_steps, re.M)
        self.assertIsNotNone(next_section, "no section after the last step")
        steps_end = len(self.text.encode()) - len(after_steps[next_section.start():].encode())
        self.assertLessEqual(steps_end, COMPACTION_KEPT_BYTES,
                             f"the steps end at byte {steps_end}")


class HelpersTest(unittest.TestCase):
    def test_folded_description_is_joined(self):
        block = "name: x\ndescription: >\n  one\n  two\nargument-hint: y"
        self.assertEqual(description(block), "one two")
        self.assertEqual(frontmatter_keys(block), ["name", "description", "argument-hint"])

    def test_inline_description_is_read(self):
        self.assertEqual(description('description: "short"'), "short")


if __name__ == "__main__":
    unittest.main()
