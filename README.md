# claude-skills

Skills personnels pour [Claude Code](https://claude.com/claude-code) — une famille cohérente qui couvre le cycle de vie complet d'une tâche de dev, du cadrage à la clôture. Chaque skill connaît les autres : il sait quand passer la main, ne refait jamais le travail d'un voisin, et les conventions (format de commit, détection GitLab/GitHub, branche cible, propose-only sur git) sont identiques partout.

## Le pipeline

```
 1. issue-mr          2. feature-loop       3. senior-review      4. branch-wrap-up
 ┌─────────────┐      ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
 │   CADRER    │ ───▶ │ IMPLÉMENTER │ ───▶ │   RELIRE    │ ───▶ │  CLÔTURER   │
 │ issue+branche│      │ boucle auto │      │ reviewers   │      │ commit+PR   │
 │ +MR/PR shell │      │ quality-gated│     │ aveugles    │      │ +capture    │
 └─────────────┘      └─────────────┘      └─────────────┘      └─────────────┘

 à tout moment : vide-contexte (persiste les insights en mémoire avant /clear)
```

| # | Skill | Rôle | Entrée → Sortie |
|---|---|---|---|
| 1 | [`issue-mr`](skills/issue-mr) | **Cadrer.** Transforme une description de tâche en issue bien formée + branche + MR/PR shell (GitLab `glab` / GitHub `gh`, auto-détecté). Mode ANALYSE pour les tâches floues : exploration du code, design tranché avec l'utilisateur, issue-spec structurée. | idée floue → issue `#N` + branche `N-slug` |
| 2 | [`feature-loop`](skills/feature-loop) | **Implémenter.** Boucle autonome quality-gated : writer ≠ test-writer ≠ reviewer aveugle, gate objectif (build/lint/tests + mutation check) avant toute revue LLM, smoke test live obligatoire. `--issue=N` consomme directement l'issue produite par issue-mr. | issue/spec → code livré + rapport |
| 3 | [`senior-review`](skills/senior-review) | **Relire.** Revue niveau senior en seconde paire d'yeux : reviewers aveugles par dimension (correctness/sécurité/design/tests), findings vérifiés par receipts, panel adversarial sur les critiques. Tiers `--quick` / standard / `--deep`. | diff/branche/PR → verdict + findings prouvés |
| 4 | [`branch-wrap-up`](skills/branch-wrap-up) | **Clôturer.** Review déléguée à senior-review, proposition de commit conventionnel, suggestion push + MR/PR, capture de connaissances (CLAUDE.md/mémoire). Propose-only : l'utilisateur valide chaque action git. | branche finie → commitée, poussée, documentée |
| — | [`vide-contexte`](skills/vide-contexte) | **Mémoriser.** Orthogonal au pipeline : avant un `/clear`, extrait les insights non-déductibles de la conversation et les persiste en fichiers mémoire (dédup contre l'index). | conversation → mémoire persistante |
| — | [`book-distill`](skills/book-distill) | **Distiller.** Hors pipeline dev : lit un livre (PDF/EPUB) et produit une fiche de lecture markdown fidèle et pédagogique — cartographie Adler A/B/C, notes verbatim-first, distillation thématique, contrepoints, citations vérifiées mot à mot contre le texte (`check-claim.py`), boucle qualité ≥ 85/100. | livre → fiche de lecture vérifiée |

## Comment ils travaillent ensemble

Les jointures sont câblées dans les skills eux-mêmes — pas besoin de les orchestrer à la main :

- **issue-mr → feature-loop** : en fin de SCAFFOLD, issue-mr suggère `feature-loop --issue=N` ; feature-loop charge l'issue comme spec et reprend la branche `N-slug`. Dans l'autre sens, si feature-loop reçoit une spec trop vague, il propose d'invoquer issue-mr (mode ANALYSE) avant de boucler.
- **feature-loop → branch-wrap-up** : en sortie de run, feature-loop suggère `branch-wrap-up --no-review` — sa review interne en aveugle tient lieu de passe senior-review, pas de double review. Si feature-loop a déjà commité (mode auto-commit), branch-wrap-up le détecte et saute directement au push/MR.
- **senior-review → branch-wrap-up** : sur verdict `approve` d'un travail local, senior-review suggère `branch-wrap-up --no-review` pour la clôture.
- **branch-wrap-up → senior-review / issue-mr** : branch-wrap-up ne review jamais lui-même, il délègue à senior-review (cible adaptée : working tree ou `--base`). Et si le travail non commité est hors-sujet ou la branche protégée, il redirige vers issue-mr (mode ISOLER) — isolation ≠ clôture.
- **Capture mémoire sans doublons** : feature-loop écrit ses insights de run, branch-wrap-up et vide-contexte lisent l'existant avant de proposer — chaque insight n'est persisté qu'une fois.

**Usage typique.** Tâche complète : `/issue-mr <description>` → `/feature-loop --issue=N` → `/branch-wrap-up --no-review`. Travail fait à la main : `/branch-wrap-up` (il déclenche senior-review tout seul). Juste une relecture : `/senior-review`. Tâche floue : `/issue-mr --analyse` d'abord.

## Installation

Cloner puis copier dans le dossier skills de Claude Code :

```bash
git clone https://github.com/ohugonnot/claude-skills.git /tmp/claude-skills
cp -r /tmp/claude-skills/skills/* ~/.claude/skills/
```

Ou en symlink pour rester synchronisé avec le repo :

```bash
git clone https://github.com/ohugonnot/claude-skills.git ~/claude-skills
for s in issue-mr feature-loop senior-review branch-wrap-up vide-contexte book-distill; do
  ln -s ~/claude-skills/skills/$s ~/.claude/skills/$s
done
```

Les skills sont alors invocables via `/issue-mr`, `/feature-loop`, `/senior-review`, `/branch-wrap-up`, `/vide-contexte`, `/book-distill` — ou déclenchés automatiquement quand la demande correspond à leur description.

## Garanties communes

- **Propose-only sur git** : aucun skill ne commit, push ou merge sans validation explicite de l'utilisateur.
- **Reviewer ≠ auteur** : le code est toujours relu par un agent qui ne l'a pas écrit.
- **Zéro hardcode projet** : labels, branche cible, scopes de commit, langue — découverts live dans chaque repo.
- **Versionnés** : chaque skill porte un `skill_version` semver et son `CHANGELOG.md`.

## Notes

- Chaque skill garde son `CHANGELOG.md` et, pour feature-loop/senior-review, un `lessons.md` (leçons distillées run après run, anonymisées).
- L'historique `.archive/` (versions antérieures, données nommées) n'est volontairement pas publié.
