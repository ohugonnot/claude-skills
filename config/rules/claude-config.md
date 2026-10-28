---
paths:
  - "**/.claude/agents/*.md"
  - "**/agents/*.md"
  - "**/SKILL.md"
  - "**/.claude/settings*.json"
---

# Écrire un agent ou un skill Claude Code

- **Un agent typé se règle dans son frontmatter** : `model` (`haiku`/`sonnet`/`opus`/`fable`/`inherit`), `effort` (`low` à `max`), `maxTurns` pour borner celui qui boucle. Sans `maxTurns`, un agent qui attend ses propres sous-agents renvoie des notifications vides à la chaîne.
- **`omitClaudeMd: true`** pour un agent qui tire tout de son brief (mesure, extraction) : un agent custom charge sinon tout CLAUDE.md.
- **`experimental.cacheTtl: 1h` seulement pour un agent long ou rappelé par `SendMessage`** : l'écriture d'un cache 1 h coûte plus que celle d'un cache 5 min, et un run de deux minutes ne relit jamais son préfixe.
- **La `description` est chargée à chaque session, le corps seulement à l'usage** : une ligne, le cas d'usage clé en premier ; détail dans le corps.
- **SKILL.md sous 500 lignes** : le détail va dans `reference/` ou `scripts/`, chargés à la demande. Après `/compact`, seul le début d'un skill invoqué survit : l'essentiel en haut.
- **Une règle qui doit toujours tenir va dans un hook**, pas dans un SKILL.md ni dans CLAUDE.md : le texte est du contexte, pas une contrainte.
