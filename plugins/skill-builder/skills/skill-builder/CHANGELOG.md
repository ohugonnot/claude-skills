# Changelog — skill-builder

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
