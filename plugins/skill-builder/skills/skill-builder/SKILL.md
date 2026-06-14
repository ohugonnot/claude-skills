---
name: skill-builder
description: Use when you want to author, fix, or package a Claude Code skill — write a SKILL.md that actually triggers, choose between a skill / CLAUDE.md / subagent / hook / MCP, keep it skimmable, and bundle it into an installable plugin and marketplace. Trigger on "write a skill", "create a SKILL.md", "make a Claude Code skill", "why doesn't my skill trigger", "publish my skill", "package as a plugin". NOT for using an existing skill, nor for general coding.
---

# Skill Builder — write a Claude Code skill that triggers and ships

## First: is a skill even the right tool?

Claude Code has five extension primitives. Pick the one that fits before writing anything.

- **Skill** — a reusable workflow or body of knowledge, pulled in **when its description matches the request**. For "how to do X well" that recurs across projects. (This is what you're building here.)
- **CLAUDE.md** — always-on project context (conventions, commands, layout). For facts every session in THIS repo needs. Not triggered; always loaded.
- **Subagent** — a delegated task run in its own context window. For fan-out, isolation, or a specialized role.
- **Hook** — deterministic automation on an event (PostToolUse, Stop…). For "always run X when Y", enforced by the harness, not the model.
- **MCP server** — external tools/data over a protocol. For reaching a system the model otherwise can't.

If the answer is "knowledge or a procedure the model should apply when the situation arises", it's a skill. Otherwise stop and use the right primitive.

## The description is everything (the #1 lever)

A skill only helps if it **triggers at the right moment and stays quiet otherwise**. That is decided almost entirely by the `description` in the frontmatter. Spend most of your effort here.

A strong description has three parts:

1. **"Use when…"** — the situations, in the user's words. Include concrete trigger phrases someone would actually type ("write a blog article", "why doesn't my skill trigger").
2. **What it does**, in one breath — enough for the model to know it's the right tool.
3. **"NOT for…"** — the adjacent cases where it must stay silent. This single clause prevents most misfires (a skill that fires on everything is worse than no skill).

```
---
name: my-skill
description: Use when <situations + real trigger phrases> — <what it does in one line>.
  Trigger on "<phrase>", "<phrase>". NOT for <adjacent case> (use <other thing>).
---
```

Name: lowercase, hyphens, a verb-or-noun that reads as a command (`book-distill`, `senior-review`). Add `argument-hint` if the skill takes arguments.

## Keep the body skimmable (progressive disclosure)

The SKILL.md body is loaded into context when the skill fires. A 2000-line SKILL.md blows the budget and dilutes attention. Rules:

- **One screen of orientation, then structure.** Lead with the core principle and the loop/steps. A reader (human or model) should grasp it in 30 seconds.
- **Push detail into `reference/` files** the skill points to, loaded on demand ("for the full stack conventions, see reference/stacks.md"). The main file stays lean.
- **Imperative and concrete.** "Do X. Never Y." Show the minimal example, not paragraphs of theory.
- A checklist at the end beats a wall of prose.

## Folder shape

```
my-skill/
└── SKILL.md            # required: frontmatter (name, description) + body
    (optional alongside:)
    reference/*.md       # detail loaded on demand
    scripts/*            # helper scripts the skill calls
    templates/*          # output templates
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
2. **Write the description first** — Use-when + trigger phrases + NOT-for. This is the product.
3. **Write the lean body** — core principle, the steps/loop, a minimal example, a checklist.
4. **Externalize the heavy stuff** to `reference/`.
5. **Test triggering**: does it fire on the real phrases? Does it stay silent on the adjacent cases? Tune the description, not the body.
6. **Package + validate** if sharing (plugin.json, marketplace.json, `claude plugin validate`).

## Anti-patterns

- **Vague description** ("helps with code") — it never triggers, or triggers on everything. The most common failure.
- **No "NOT for"** — the skill misfires and erodes trust.
- **Monster SKILL.md** — hundreds of lines loaded every time; split into reference/.
- **Hardcoding one project's specifics** in a skill meant to be reused — keep it stack-agnostic, discover specifics live.
- **Renaming the concept mid-body** — one term, used consistently (the model anchors on it).
- **Wrong primitive** — an always-on rule should be CLAUDE.md or a hook, not a skill.

## Checklist

- [ ] A skill is the right primitive (not CLAUDE.md / subagent / hook / MCP)
- [ ] `description` has Use-when + real trigger phrases + a NOT-for clause
- [ ] Name is lowercase-hyphen, reads like a command
- [ ] Body is skimmable; heavy detail lives in reference/
- [ ] One concept = one word, imperative, minimal examples
- [ ] Triggers on the intended phrases, silent on adjacent cases
- [ ] If shared: plugin.json + marketplace.json, version pinned, `claude plugin validate` passes
