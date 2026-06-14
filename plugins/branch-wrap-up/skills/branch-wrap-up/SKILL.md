---
name: branch-wrap-up
description: >
  Use when the user says the work is done and wants to close out a branch —
  orchestrates the wrap-up of already-written work: gathers uncommitted/branch
  changes, delegates the code review to senior-review (standard tier by default),
  proposes a conventional commit message in the project's own style, suggests
  push + MR/PR on GitLab (glab) or GitHub (gh) auto-detected from the remote,
  and runs a CLAUDE.md/memory knowledge-capture check. Propose-only on git:
  never runs add/commit/push itself, the user validates each action; never
  mentions AI. NOT for the deep review itself (use senior-review), nor for
  building a feature (use feature-loop), nor for creating the issue/branch/MR
  up front (use issue-mr). Flags: --no-review (review already done),
  --quick/--deep (tier passed through to senior-review).
argument-hint: "[--no-review] [--quick|--deep]"
---

# Branch Wrap-Up

**skill_version : 1.1.0** (historique : `CHANGELOG.md`). Clôture d'une branche de travail : review déléguée → proposition de commit → suggestion push/MR-PR → capture de connaissances. S'applique à du travail **déjà fait** — à la main ou laissé par `feature-loop` en mode `no_auto_commit`.

<!-- LOCKED: modif humaine directe uniquement -->
## Principes

- **Review → Propose → Capture.** Dans cet ordre, jamais de raccourci.
- **Propose-only sur git** : le skill ne lance JAMAIS `git add`, `git commit`, `git push` ni de création de MR/PR lui-même. Il prépare les commandes exactes, l'utilisateur exécute (ou donne son feu vert explicite).
- **Reviewer ≠ auteur** : la review est déléguée à `senior-review` (ou à défaut à un agent aveugle), jamais faite par la session qui a écrit le code.
- **Zéro hardcode** : plateforme, branche cible, format de commit, langue — tout est découvert live dans le projet (conventions reprises d'`issue-mr`).
- **Effort proportionné** : wrap-up d'un patch de 10 lignes ≠ clôture d'une feature de 3 jours. Tier de review et profondeur de capture dimensionnés à l'enjeu.

## Logs

Préfixes de progression, une ligne par sous-étape clé, style factuel : `[context]` `[gather]` `[review]` `[commit]` `[push]` `[capture]` `[done]`.

## Parsing des arguments

- `--no-review` : saute l'Étape 2 (l'utilisateur a déjà reviewé — ex. sortie de `senior-review` ou de `feature-loop` dans la même session).
- `--quick` / `--deep` : tier passé tel quel à `senior-review` (défaut : standard).

## Étape 0 — Plateforme + contexte git

1. **Plateforme** : `git remote get-url origin` → `gitlab` → `glab`, `github` → `gh`, autre/absent → demander. Vérifier l'auth (`glab auth status` / `gh auth status`) seulement si l'Étape 4 sera atteinte.
2. **Branche cible** : « Main branch » du `CLAUDE.md` projet si documentée, sinon `git remote show origin` (ligne `HEAD branch`). Jamais supposer `main`.
3. **Règle commit** : détecter une règle « no auto-commit » dans les CLAUDE.md (global/projet). Si présente — et c'est le défaut prudent même sans règle — tout reste propose-only. Logger `[context] plateforme=<glab|gh>, cible=<branche>, no_auto_commit=<oui/non>`.
4. **Routage clôture vs isolation** : branche courante protégée (`main`/`develop`/cible) OU travail non commité hors-sujet par rapport à la branche courante → ce n'est pas une clôture mais une isolation : rediriger vers `issue-mr` (mode ISOLER) avant de continuer.

## Étape 1 — Rassembler les changements

```bash
git status -sb          # tracking + untracked
git diff HEAD --stat    # vue d'ensemble
git log --oneline -10   # style de commit du projet
```

- Inclure les fichiers untracked qui semblent intentionnels (sources, pas artefacts de build) avec une note.
- **Gros diff (> ~200 lignes)** : ne pas le charger dans le contexte mère — déléguer la lecture à un agent tier rapide qui rend un résumé par fichier (quoi/pourquoi apparent/risques).
- Si l'arbre est propre ET la branche au niveau du remote : le dire et s'arrêter (`[done] rien à clôturer`).

## Étape 2 — Review (déléguée)

Sauf `--no-review` :

0. **Review déjà faite dans la session ?** Si `feature-loop` a livré ce diff dans la session courante, sa review en aveugle tient lieu de cette étape → proposer de traiter comme `--no-review` (ne pas payer une review en double).
1. **Si le skill `senior-review` est disponible** : l'invoquer avec la cible adaptée à l'Étape 1 — working tree s'il reste des modifs non commitées, sinon `--base <branche cible>` pour relire les commits de la branche (sinon senior-review répond « cible vide »). Tier standard — ou `--quick`/`--deep` si passés. Ne pas dupliquer sa logique ici.
2. **Sinon (fallback)** : déléguer une passe unique à un agent aveugle tier standard (contexte : diff + conventions CLAUDE.md ; sortie : findings 🔴 bloquant / 🟡 important / 🔵 mineur). Jamais de self-review par la mère.

**Gate** : ne passer à l'Étape 3 que sans 🔴 non résolu. S'il en reste, proposer de corriger d'abord (ou acter explicitement avec l'utilisateur que c'est assumé).

## Étape 3 — Proposition de message de commit

Arbre propre mais branche en avance sur le remote (cas `feature-loop` mode auto-commit, ou commits manuels déjà faits) : rien à committer — sauter directement à l'Étape 4 (push/MR-PR).

Format conventionnel, aligné sur `issue-mr` :

- `type(scope): description` — types `feat|fix|chore|refactor|docs|style|test|ci|perf`.
- **Scope déduit de l'usage réel** : `git log --oneline -30` (réutiliser les scopes existants) + CLAUDE.md. Pas de scope inventé.
- Description impérative, lowercase, sans point final ; référencer l'issue (`#N`) si la branche en porte une (`N-slug`).
- Langue : celle des commits existants du projet.
- Plusieurs changements logiques → proposer un **découpage en commits séparés** avec la liste fichiers→commit.
- Jamais de mention Claude/AI, jamais de `Co-Authored-By`.

Présenter :

```
Commit proposé :

  fix(wizard): mark list measures as non-missing when default exists #155

À exécuter quand prêt :
  git add <fichiers>
  git commit -m "..."
```

## Étape 4 — Push / MR-PR

Si la branche est en avance sur le remote ET n'est pas la branche cible :

- Proposer (sans exécuter) : `git push -u origin <branche>` puis `glab mr create` / `gh pr create` selon la plateforme, avec description structurée (Résumé / Changements / Vérification).
- Gotcha GitHub : pas de PR sans commit d'écart (« No commits between… ») — donc la PR n'est proposable qu'après le commit de l'Étape 3.
- Décision via une AskUserQuestion **groupée** (commit + push + MR/PR en un seul écran), pas un interrogatoire au fil de l'eau.

Déjà à jour ou sur la branche cible : sauter silencieusement.

## Étape 5 — Capture de connaissances

La valeur ajoutée propre à ce skill : transformer ce que la session a appris en savoir persistant.

**Filtre CLAUDE.md** (toutes conditions) : non-déductible du code · se reproduira en future session · pas déjà présent. Bons candidats : gotchas découverts, contraintes métier invisibles, décisions d'archi avec leur pourquoi. Mauvais : ce que le code montre, patterns standards, contexte temporaire.

**Filtre mémoire** (toutes conditions) : traverse les sessions · pas déjà dans CLAUDE.md · passe le test *« si je supprime et relis le code, est-ce que ça manquera ? »*. Types : `user`, `feedback` (Règle → Why → How to apply), `project`, `reference`.

Proposer explicitement chaque ajout (texte exact + destination), appliquer seulement sur validation. Rien à capturer → le dire : `[capture] rien de nouveau pour CLAUDE.md ni la mémoire`.

Même filtre que `vide-contexte`, déclencheur différent : `vide-contexte` capture avant un `/clear` (n'importe quand), cette étape capture à la clôture d'une branche. Avant de proposer : lire la mémoire projet existante — y compris les insights écrits par `feature-loop` dans la même session (`project_feature_loop_insights.md`, `project_<slug>.md`) — et ne pas re-proposer ce qui y est déjà. Si `vide-contexte` ou `feature-loop` viennent de tourner, leurs captures comptent comme déjà faites.

<!-- LOCKED: modif humaine directe uniquement -->
## Ce que le skill NE fait PAS

- Ne fait pas la review profonde lui-même — c'est `senior-review` (délégation, Étape 2).
- Ne construit pas de feature — c'est `feature-loop`.
- Ne crée pas l'issue/la branche/le squelette de MR en amont — c'est `issue-mr`.
- N'exécute jamais `git add`, `git commit`, `git push`, ni `--force`, ni de création de MR/PR sans validation explicite.
- Ne mentionne jamais Claude/AI dans commits, MR/PR ou code ; aucun `Co-Authored-By`.
- Ne déclare jamais « ready to commit » si des artefacts de debug traînent ou si un 🔴 est ouvert.
- Ne duplique pas dans CLAUDE.md ce qui y est déjà ou ce qui se déduit du code.
