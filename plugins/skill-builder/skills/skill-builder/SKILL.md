---
name: skill-builder
description: >-
  Use when the user is designing, reviewing or debugging a Claude Code skill and needs the
  judgment behind a good SKILL.md — should this even be a skill (vs CLAUDE.md / subagent / hook
  / MCP), why a description does or doesn't trigger, how to keep the body skimmable, how to
  package it. Carries the opinionated principles plus a review checklist. Trigger on "review my
  SKILL.md", "why doesn't my skill trigger", "principles of a good skill", "should this be a
  skill or a hook", "is my skill description good", even when the word "skill" is only implied.
  NOT for interactive scaffolding from scratch (use Anthropic's Skill Creator), nor for general
  coding.
---

# Skill Builder — the principles behind a skill that triggers and stays focused

> For interactive scaffolding, evaluation and benchmarking of a skill, use Anthropic's official **Skill Creator** (claude.com/plugins/skill-creator). This skill is the complementary **judgment layer**: the opinionated principles that make a skill trigger reliably and stay focused, plus a review checklist and the packaging path. Use it to design, review, or debug a skill, not to generate boilerplate.

## The root virtue: predictability

A skill exists to pull determinism out of a stochastic system. What you make repeatable is the **process**, not the output — the agent should take the same approach every run, even when the result differs. Design the procedure; don't script the answer. Two tests fall out of this:

- **Completion criteria the agent can check.** The skill must give it a way to tell *done* from *not-done* — otherwise it stops early and calls it finished.
- **One leading word.** Anchor the skill on a single concept the model already knows well (e.g. *tracer bullet*, *receipt*, *lesson*, *seam*) and repeat it in the name, the description and the body. A word the model thinks with anchors both *triggering* and *execution* — far more than a phrase it has to decode.

## First: is a skill even the right tool?

Claude Code has five extension primitives. Pick the one that fits before writing anything.

- **Skill** — a reusable workflow or body of knowledge, pulled in **when its description matches the request**. For "how to do X well" that recurs across projects. (This is what you're building here.)
- **CLAUDE.md** — always-on project context (conventions, commands, layout). For facts every session in THIS repo needs. Not triggered; always loaded.
- **Subagent** — a delegated task run in its own context window. For fan-out, isolation, or a specialized role.
- **Hook** — deterministic automation on an event (PostToolUse, Stop…). For "always run X when Y", enforced by the harness, not the model.
- **MCP server** — external tools/data over a protocol. For reaching a system the model otherwise can't.

If the answer is "knowledge or a procedure the model should apply when the situation arises", it's a skill. Otherwise stop and use the right primitive.

## The description is everything (the #1 lever)

A skill only helps if it triggers at the right moment. The `description` in the frontmatter decides that almost entirely. Spend most of your effort here. Whether yours under- or over-triggers is a measurement, not a given: write 3 prompts that must trigger it and 3 that must not, run them (`tool_used: Skill` grader, see the official limits below), and tune the description on the result. Until measured, lean inclusive and a little "pushy".

A strong description:

1. **"Use when…" + real trigger phrases** someone would actually type, and be pushy: "use this whenever the user mentions X, Y or Z, **even if they don't say** '<skill>' explicitly". Anthropic's own docx/xlsx skills phrase it exactly that way.
2. **What it does**, in one breath — enough for the model to know it's the right tool.
3. **"NOT for…" — only if a sibling skill competes.** Anthropic's official skills mostly OMIT this, because their domains are distinct (pdf ≠ xlsx, no confusion possible). Add it when you have adjacent skills that could both match (a "review changes" skill vs a "ship a feature" skill) — there it disambiguates. Don't add it just to look careful: an over-restrictive description makes the skill under-trigger, which is the worse problem.

```
---
name: my-skill
description: Use when <situations>, e.g. "<real phrase>", "<real phrase>" — be a little pushy
  ("whenever the user mentions …, even if they don't say '<skill>'"). <what it does in one line>.
  [NOT for <adjacent case> — add only if a sibling skill competes.]
---
```

Name: lowercase, hyphens, a verb-or-noun that reads as a command (`book-distill`, `senior-review`). Add `argument-hint` if the skill takes arguments.

**Model-invoked vs user-invoked.** By default a skill is model-invoked: its description sits in context and other skills can reach it — right for reusable knowledge that should fire on its own. Set `disable-model-invocation: true` to make it user-invoked (`/skill` only): the description leaves the model's reach, saving context. Reserve it for skills nobody else needs to auto-trigger — heavy, domain-specific, run-on-demand (a tax-dossier writer, a one-off migration).

## Keep the body skimmable (progressive disclosure)

Three loading levels: **metadata** (name + description, always in context) → **SKILL.md body** (loaded when the skill fires) → **bundled resources** (loaded or executed on demand). Keep the body lean so it doesn't crowd the context.

- **Body under 500 lines** (official rule, not a target). Past that, split into files linked directly from SKILL.md ("for X, read references/x.md").
- **Externalize the heavy stuff — when it pays.** Two thirds of Anthropic's official skills are a single SKILL.md; split only when it earns it. When you do, **`scripts/` (executable, deterministic ops) earns its place far more often than `references/` (docs)** — the document skills (pdf, xlsx, docx) are mostly scripts. Use `references/<variant>.md` for multi-framework domains; a reference over ~300 lines gets a table of contents.
- **Imperative and concrete.** "Do X. Never Y." Minimal example over paragraphs of theory.
- A checklist at the end beats a wall of prose.

## Folder shape

```
my-skill/
└── SKILL.md            # required: frontmatter (name, description) + body
    (optional alongside:)
    scripts/*           # executable code for deterministic ops (earns its place most often)
    references/*.md     # detail loaded on demand (multi-framework, heavy domains)
    assets/*            # templates, fonts, icons used in the output
```

Personal skills live in `~/.claude/skills/<name>/` (or a project's `.claude/skills/`). To SHARE one, wrap it in a plugin.

## Package for distribution (plugin + marketplace)

To make a skill installable by others:

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json          # { "name", "description", "version", "author" }
└── skills/
    └── my-skill/
        └── SKILL.md
```

A **marketplace** is a repo with `.claude-plugin/marketplace.json` listing plugins (each `source` a relative path like `./plugins/my-plugin`). Users add and install with:

```bash
/plugin marketplace add owner/repo
/plugin install my-plugin@marketplace-name
```

Validate before publishing: `claude plugin validate <path>`. Pin a `version` (omit it and every commit becomes a new auto-updating version). Keep all files inside the plugin root (no `../shared`).

## The loop to author one

1. **Decide it's a skill** (see the five primitives).
2. **Write the description first** — Use-when + real trigger phrases, leaning pushy; add NOT-for only if a sibling competes. This is the product.
3. **Write the lean body** — core principle, the steps/loop, a minimal example, a checklist.
4. **Externalize the heavy stuff** to `reference/`.
5. **Test triggering**: does it fire on the real phrases? Does it stay silent on the adjacent cases? Tune the description, not the body.
6. **Package + validate** if sharing (plugin.json, marketplace.json, `claude plugin validate`).

## Anti-patterns

- **Vague description** ("helps with code"): it never triggers.
- **Over-restrictive description**: too many caveats and the skill stops triggering. Lean pushy; reserve "NOT for" for genuine sibling competition.
- **Monster SKILL.md**: a body past 500 lines, or one whose bulk is detail that belongs in scripts/ or references/.
- **Hardcoding one project's specifics** in a skill meant to be reused — keep it stack-agnostic, discover specifics live.
- **Renaming the concept mid-body** — one term, used consistently (the model anchors on it).
- **Wrong primitive** — an always-on rule should be CLAUDE.md or a hook, not a skill.
- **Sediment** — stale instructions left from past versions that no longer match the skill; prune them on every edit instead of layering on top.
- **No-op line** — a sentence the agent would follow anyway; delete the whole sentence, don't trim its words.
- **Unquoted colon in the description** — `description: Use when … : …` is invalid YAML (`mapping values are not allowed here`). Nothing warns you: the frontmatter silently loads empty and the skill never triggers. Use a folded block (`description: >-`, text indented on the next lines) or quote the string. Seen on three skills of one repo in a single day, all with French text (« … : … »).
- **Rules duplicated across skills** — the same cost or style section pasted into several skills drifts apart. Put it once in a versioned file every machine sees (the repo's CLAUDE.md, a shared reference), point to it, and keep in each skill only the line specific to it. A pointer to an unversioned file (a global `~/.claude/CLAUDE.md`) breaks on every other machine.

## Official limits (checked 2026-11-04)

Authoring rules, https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices :
1. `description` 1,024 characters at most, in the third person ("Processes X", not "I can help"); `name` 64 at most, lowercase, digits, hyphens.
2. References one level deep from SKILL.md; a reference file over 100 lines opens with a table of contents.
3. No time-sensitive information: history goes to an "old patterns" section or the CHANGELOG.
4. One term per concept across the whole skill.
5. Build evaluations first: three at least, run on Haiku, Sonnet and Opus.

Claude Code, https://code.claude.com/docs/en/skills and https://code.claude.com/docs/en/plugin-evals :
6. `claude plugin eval` has free graders (`regex`, `tool_used`, `tool_order`, `file_exists`); `claude plugin eval init` proposes prompts that should and should not trigger; skill-creator iterates on one skill in a session.
7. `description` plus `when_to_use` are cut at 1,536 characters in the listing; `/skill-doctor` shows what each skill costs, `skillOverrides: "name-only"` collapses one.
8. Other frontmatter fields: `when_to_use`, `paths`, `context: fork` with `agent`, `hooks`, `allowed-tools`.
9. Compaction keeps the first 5,000 tokens of each invoked skill (25,000 shared): essentials first.
10. Body under 500 lines, and under 5k tokens once loaded (https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview).
11. Triggering is measured with a trigger eval (a `tool_used: Skill` grader, `min: 0` and `max: 0` for a prompt that must not fire it), never asserted.

## Checklist

- [ ] A skill is the right primitive (not CLAUDE.md / subagent / hook / MCP)
- [ ] `description` has Use-when + real trigger phrases, leans pushy, checked by a trigger eval (3 prompts that must fire, 3 that must not); NOT-for only if a sibling competes
- [ ] Name is lowercase-hyphen, reads like a command
- [ ] Body is skimmable; heavy detail lives in reference/
- [ ] One leading word the model already knows, repeated in name + description + body; imperative, minimal examples
- [ ] The skill gives the agent a checkable "done" signal (completion criteria)
- [ ] Triggers on the intended phrases, silent on adjacent cases (measured, not assumed)
- [ ] Passes the official limits below (description, references, terminology, evals)
- [ ] Frontmatter parses: `python3 -c "import sys,yaml; [yaml.safe_load(open(f).read().split('---')[1]) for f in sys.argv[1:]]" */SKILL.md` exits 0 (catches the unquoted-colon trap)
- [ ] If shared: plugin.json + marketplace.json, version pinned, `claude plugin validate` passes
