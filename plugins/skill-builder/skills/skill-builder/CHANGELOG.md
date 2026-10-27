# Changelog — skill-builder

## 1.3.0 — 2026-10-27

- **Anti-pattern « deux-points non quoté dans la description »** : YAML invalide, frontmatter chargé vide sans aucun avertissement, skill qui ne se déclenche plus. Vu sur trois skills d'un même dépôt en une journée. Parade : bloc `>-` ou chaîne quotée, et une ligne de checklist qui parse tous les frontmatters.
- **Anti-pattern « règles dupliquées entre skills »** : une section copiée dans plusieurs skills dérive ; la mettre une fois dans un fichier versionné que toutes les machines voient, et ne jamais pointer vers un fichier non versionné (`~/.claude/CLAUDE.md` global).

## 1.2.0 — 2026-08-10

- **Description à la 3e personne** : « Use when you want the opinionated PRINCIPLES » — le skill qui énonce les règles enfreignait celle de la 3e personne. Reformulée en « Use when the user is designing, reviewing or debugging a Claude Code skill ».
- **Mot directeur unifié sur « judgment »** : la description faisait flotter *principles*, *judgment* et *predictability* côte à côte, alors que le skill impose lui-même un mot-ancre unique repris du nom au corps. « Judgment » mène désormais la description.

## 1.1.0 — 2026-06-28

- Ajoute la section « root virtue: predictability » (figer le process, pas l'output) avec ses deux tests : completion criteria vérifiables + leading word.
- Ajoute la distinction model-invoked vs user-invoked (`disable-model-invocation`) et son heuristique.
- Anti-patterns : ajoute « sediment » (couches stale) et « no-op line ».
- Checklist : leading word répété (name + description + body) et signal « done » vérifiable.

## 1.0.0 — 2026-06-16

- Version initiale : choix de primitive (skill vs CLAUDE.md/hook/MCP/subagent), la description comme levier n°1, progressive disclosure, packaging plugin/marketplace, anti-patterns et checklist.
