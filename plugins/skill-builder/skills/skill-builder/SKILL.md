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

A skill only helps if it triggers at the right moment. The `description` in the frontmatter decides that almost entirely. Spend most of your effort here — and know the real failure mode: **Claude UNDER-triggers skills** far more than it over-triggers (it only consults a skill when it can't trivially handle the task itself). So lean inclusive and a little "pushy".

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

- **< 500 lines is the target, not a law.** Anthropic's own docx skill is 590. Go longer when the domain warrants it, but past ~500 add a layer of hierarchy and clear pointers ("for X, read references/x.md").
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

- **Vague description** ("helps with code") — it never triggers. The most common failure, and worse than over-triggering.
- **Over-restrictive description** — too many caveats and the skill under-triggers (the bigger risk). Lean pushy; reserve "NOT for" for genuine sibling competition.
- **Monster SKILL.md** — only a problem if the bulk is detail that belongs in scripts/ or references/; size alone isn't the sin (docx is 590 lines).
- **Hardcoding one project's specifics** in a skill meant to be reused — keep it stack-agnostic, discover specifics live.
- **Renaming the concept mid-body** — one term, used consistently (the model anchors on it).
- **Wrong primitive** — an always-on rule should be CLAUDE.md or a hook, not a skill.
- **Sediment** — stale instructions left from past versions that no longer match the skill; prune them on every edit instead of layering on top.
- **No-op line** — a sentence the agent would follow anyway; delete the whole sentence, don't trim its words.

## Checklist

- [ ] A skill is the right primitive (not CLAUDE.md / subagent / hook / MCP)
- [ ] `description` has Use-when + real trigger phrases, leans pushy (under-triggering is the bigger risk); NOT-for only if a sibling competes
- [ ] Name is lowercase-hyphen, reads like a command
- [ ] Body is skimmable; heavy detail lives in reference/
- [ ] One leading word the model already knows, repeated in name + description + body; imperative, minimal examples
- [ ] The skill gives the agent a checkable "done" signal (completion criteria)
- [ ] Triggers on the intended phrases, silent on adjacent cases
- [ ] If shared: plugin.json + marketplace.json, version pinned, `claude plugin validate` passes
