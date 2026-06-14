# Feature-loop — Sous-commandes `status` et `learn`

Lu à la demande quand le premier token des args est `status` ou `learn` (dispatch : SKILL.md « Parsing des arguments »). Aucune des deux ne lance la boucle d'implémentation.

## Étape 6 — Sous-commande `status` (hors boucle, lecture seule)

Déclenchée par `status` en premier token. NE lance PAS de boucle.

1. Lire `~/.claude/projects/<encoded-cwd>/memory/feature_loop_runs.jsonl` (encoded-cwd = cwd absolu avec `/` → `-`). Absent → afficher "Aucun run feature-loop enregistré sur ce repo." et stop.
2. Parser chaque ligne, afficher un tableau trié par date décroissante :

```
FEATURE-LOOP — runs sur <repo> (N runs)
═══════════════════════════════════════════════════════════════
date        slug                statut      iter  radar  axes<8     mode
2026-05-28  add-csv-export      SUCCESS     2     8.4    —          in-place
2026-05-24  user-card-web       MAX_ITER    3     7.6    UX, a11y   worktree
2026-05-20  fix-mariadb-migr    SUCCESS     1     8.9    —          in-place
───────────────────────────────────────────────────────────────
SUCCESS: 2/3 · médiane iter: 2 · radar moyen: 8.3
```

3. Si des runs sont MAX_ITER/ABORTED, signaler en une ligne les `axes_below` les plus fréquents (repère un axe chroniquement faible sur ce projet).

Pas d'`AskUserQuestion`, aucune modif fichier.

## Étape 7 — Sous-commande `learn` (propose-only, hors boucle)

Déclenchée par `learn` en premier token. Améliore le skill à partir des runs passés, SANS jamais le réécrire en silence.

### 7.1 Analyse
1. Lire les runs-logs (ce projet, ou tous via glob `~/.claude/projects/*/memory/feature_loop_runs.jsonl`) + le `lessons.md` actuel.
2. Identifier des **patterns cross-runs** : axes chroniquement faibles, reclassements major→minor récurrents, skip-Sonnet qui overflow souvent, régressions répétées sur un même type de feature, escalations fréquentes.
3. Exploiter le champ **`anomalies`** des run-logs (V8.2) : tests vacants récurrents, preuves invalides, échecs smoke-live, notes ignorées, agents B relancés — c'est la carte des endroits où la BOUCLE elle-même échoue (pas la feature). Un compteur qui revient sur ≥ 2 runs = candidat leçon ou proposition SKILL.md.

### 7.2 Écriture libre dans `lessons.md` (surface d'auto-amélioration autorisée)
Pour chaque pattern réutilisable sur un AUTRE projet, append à `~/.claude/skills/feature-loop/lessons.md`. Format : `- **<titre>** : <règle actionnable> — *vu sur N runs (<slugs>)*`. Additif uniquement, jamais de réécriture destructive. Logger `[learn] N leçon(s) ajoutée(s) à lessons.md`.

### 7.2bis Consolidation de `lessons.md` (propose-only)
`lessons.md` est chargé en tête des prompts impl/review à CHAQUE run : sa croissance non bornée coûte des tokens et dilue le signal. Quand l'UN est vrai — (a) > ~30 leçons, (b) doublon/contradiction détecté entre leçons (ou entre une leçon et une règle du SKILL.md qui l'a raffinée), (c) leçon « vu sur 1 run » jamais re-confirmée depuis > 6 mois — proposer via `AskUserQuestion` une consolidation : fusion des doublons, marquage `**[SUPERSEDED — voir <cible>]**` en tête de la leçon périmée (on n'efface pas l'historique), distillation des leçons anciennes en règles plus courtes. Présenter le diff exact (old → new) ; n'appliquer QUE sur validation explicite. L'additif-only (7.2) reste la règle pour les ajouts automatiques de fin de run — la consolidation est un acte de maintenance validé par l'user, jamais silencieux. Logger `[learn] consolidation proposée (N leçons → M)`.

### 7.3 Propositions sur le SKILL.md (JAMAIS auto-appliquées)
Si un pattern suggère un changement de la LOGIQUE du skill (au-delà d'une simple leçon), `learn` PROPOSE, il n'applique jamais seul :
1. **Sections LOCKED interdites** : ne JAMAIS proposer de modif sur "Principes non négociables", "Ce que le skill NE fait PAS", "Garanties" (balises `<!-- LOCKED -->`). Ces contrats ne changent que par décision humaine directe, hors `learn`.
2. Sections éditables : présenter via `AskUserQuestion` le résumé du changement + le diff exact (old → new) + les runs qui le motivent.
3. N'appliquer l'`Edit` QUE sur validation explicite de l'user. Logger `[learn] M proposition(s) SKILL.md, <K> validée(s)`.

**Garde-fou anti-dérive** : `learn` ne propose JAMAIS d'affaiblir un garde-fou (retirer une review, un check, une confirmation user). S'il observe qu'un garde-fou ralentit, il le SIGNALE à l'user sans proposer de le retirer — la décision reste humaine.

### 7.4 Versioning (`skill_version`) — uniquement sur modif validée du SKILL.md
Quand l'user **valide** une proposition 7.3 qui change la logique du skill, incrémenter `skill_version` (semver) ET ajouter une ligne en tête de `CHANGELOG.md` :
- **patch** (8.0.x) : clarification, garde-fou ajouté, correction de formulation.
- **minor** (8.x.0) : nouvelle étape/commande/axe, nouveau flag, sans casser l'existant.
- **major** (x.0.0) : changement de contrat (sections LOCKED — décision humaine directe, hors `learn`).
Une simple leçon dans `lessons.md` (7.2) **ne bump PAS** la version (c'est de la mémoire, pas du contrat). Le `skill_version` courant est reporté dans chaque run-log et dans le radar de review (traçabilité : quelle version a produit quel run).
