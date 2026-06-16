# Exemple complet d'une trace de run

Illustratif — sorti du SKILL.md (progressive disclosure). La spec des préfixes de log vit dans le SKILL.md, section « Logs utilisateur (principe) ». Ceci montre une trace type de bout en bout.

```
[preflight] git status clean, deps OK, baseline build ✓
[scan] fullstack détecté (Node + React + Vitest + Playwright)
[scan] keywords sensibles détectés (auth, token) → --paranoid auto-activé
[init] 3 conventions extraites, 2 lint plugins dispos (jsx-a11y, security)
[init] insights projet chargés (3 patterns connus), lessons cross-projet chargées (5 leçons)
[init] in-place : branche develop protégée → feature-loop/add-csv-export créée+checkout (base 5bcba8236)
[tier] SENSIBLE (keywords auth/token, risque haut) → review Opus + devil's advocate d'office
[iter 1/3] plan Sonnet (4 fichiers, confidence 8)
[iter 1/3] mini-review Haiku : plan validé
[iter 1/3] impl code (agent A, Sonnet)...
[iter 1/3] tests (agent B ≠ A, depuis la spec) : 12 tests, 3 marqués critiques
[iter 1/3] gate: build ✓ lint ✓ typecheck ✓ tests 12/12 ✓
[iter 1/3] redcheck: 3/3 tests critiques rougissent sur mutation ✓
[iter 1/3] lint-plugins: a11y 0 errors, security 1 warning
[iter 1/3] screenshots captés (375/768/1440)
[iter 1/3] review (agent C, Opus, aveugle)...
[iter 1/3] devil's advocate : 2 angles morts identifiés
[iter 1/3] escalade: robustesse borderline (7, conf 0.4) → panel-3 → médiane 7 confirmée
[iter 1/3] preuves vérifiées (14/14 valides)
[iter 1/3] scores: lisi=8 robust=7 secu=6 ... — 1 critical, 3 majors → next iter
[iter 2/3] notes_acknowledged: oui (3/3 pris en compte)
...
[converge] tous axes ≥ 8, 0 critical
[best] meilleure version = iter 3 (radar 8.4) = dernière → pas de restauration
[smoke] re-run final build+tests : ✓
[smoke-live] serveur dev relancé (ancien binaire détecté), schéma dev aligné, POST /tracking → 200, logs sans erreur : ✓
[conflicts] branche mergeable, 0 conflit avec main
[report] feature-loop-report.md écrit
[runs] run loggé dans feature_loop_runs.jsonl
[lessons] 1 meta-leçon cross-projet ajoutée
[done] SUCCESS en 2 itérations, 14min total
```
