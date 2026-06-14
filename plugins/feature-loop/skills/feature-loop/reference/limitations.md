# Feature-loop — Limitations connues

Lu à la demande quand l'un de ces contextes est détecté (le SKILL.md pointe ici).

- **`vendor/` ou `node_modules/` en symlink avec le repo principal (mode `--worktree` UNIQUEMENT)** : non applicable en in-place (défaut), qui utilise le vrai dossier du repo. En mode `--worktree`, git partage par défaut ces dossiers (pour la perf). Conséquence : l'autoloader composer / require résout les classes vers `/main/src/...`, pas `/worktree/src/...`. **Impact** : tests runtime via `ClassMetadata` (Doctrine), `ReflectionClass`, ou tout autre mécanisme d'introspection chargent la **vieille version** des entités/modules. Les modifs entités/sources ne sont PAS testables runtime depuis le worktree. Stratégies (si tu tiens au `--worktree`) :
  - Tests source-string limités (mais attention aux faux confort méta-tests, cf rubric)
  - Skip explicite des tests runtime entités avec message `'Limitation worktree symlink — testé post-merge sur master'`
  - OU pour un fix complet : `composer install` / `npm install` dans le worktree (recopier le dossier) au prix de +30s setup
  - Le pre-flight (étape 0 V6) détecte et log le symlink — l'agent doit en tenir compte
- **Extension Chrome MV3 / projets sans build standard** : `npm run build/lint/typecheck` peuvent être absents. Le skill skip gracefully. Conséquence : axes `robustesse` ancrés sur lint plugins + tests seulement, pas sur typecheck.
- **Axes UI non applicables** sur extensions, librairies, CLI : le skill devrait les filtrer au scope detection (Étape 2). Si l'agent les inclut quand même, le reviewer doit les marquer N/A explicitement plutôt que noter mal.
- **Tests E2E "flaky" avec retry** : 1 retry seulement (V3). Si test passe au retry, accepté avec flag `tests_flaky: true`. Pour features sensibles, peut justifier 2-3 retries — pas dans la version courante, à voir si besoin.
