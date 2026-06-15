---
name: issue-mr
description: >
  Use when the user wants to turn a task description into a well-formed issue with its branch and MR/PR — on GitLab (glab) or GitHub (gh), auto-detected from the remote. Three behaviors: SCAFFOLD (clean tree → issue + branch + MR/PR shell), ISOLER (uncommitted work gets isolated into its own issue/branch/MR — file list and commit message validated first), ANALYSE (--analyse or vague/non-trivial task: explore the code, settle design with the user, produce a structured spec issue — constat/pourquoi/périmètre/plan — ready to feed feature-loop --issue=N). Discovers project conventions live (labels, default branch, commit scopes) instead of hardcoding; validates everything with the user BEFORE creating anything; never mentions AI. Flags: --analyse, --issue-only. NOT for implementing the task (use feature-loop) nor for wrapping up an existing branch (use branch-wrap-up).
argument-hint: "<task description> [--analyse] [--issue-only]"
---

# Issue + Branche + MR/PR

**skill_version : 2.0.3** (historique : `CHANGELOG.md` — fusion de 4 copies projet divergentes). Transforme une description de tâche en issue bien formée + branche + MR/PR, sur GitLab (`glab`) ou GitHub (`gh`). **Comportement global, données projet découvertes** : aucun label, branche cible ou scope n'est codé en dur — tout vient du repo courant (CLI, git, CLAUDE.md) et passe par une validation user.

La tâche : $ARGUMENTS

**Règle d'or : RIEN n'est créé (issue, branche, commit, MR/PR) avant la validation explicite de l'Étape 3.** Jamais de mention Claude/AI dans les issues, branches, commits, MR/PR.

## Étape 0 — Plateforme + contexte git (NE PAS sauter)

1. **Plateforme** : `git remote get-url origin` → `gitlab` → `glab` ; `github` → `gh` ; autre/absent → demander. Vérifier l'auth (`glab auth status` / `gh auth status`) — échec → le dire et s'arrêter proprement (rien à créer sans API).
2. **Branche par défaut/cible** : « Main branch » déclarée dans `<repo>/CLAUDE.md` si présente, sinon `git remote show origin` (ligne `HEAD branch`). C'est la base ET la target de la MR/PR.
3. **État git** → mode :
   - **Changements non commités présents** (tracked modifiés / untracked pertinents) → **Mode ISOLER** : ce travail doit finir dans la nouvelle branche/MR (cas fréquent : on a codé, puis on veut isoler proprement).
   - **Working tree propre** → **Mode SCAFFOLD** : issue + branche + MR/PR vide (le code viendra après).
4. La nouvelle branche se crée **depuis `origin/<défaut>` à jour** (`git fetch origin`) — jamais depuis la branche courante si elle est protégée ou porte des commits sans rapport (sinon la MR/PR les embarquerait).

Logger : `[mode] <plateforme> · <ISOLER (N fichiers)|SCAFFOLD> · base origin/<défaut>`.

## Étape 1 — Mode ANALYSE (sur `--analyse`, tâche floue, ou pont feature-loop)

Déclencheurs : flag `--analyse` ; OU la description rate ≥ 2 points du test de clarté (quoi / pourquoi / périmètre exclu) ; OU invocation depuis le pont feature-loop (Étape 1 de feature-loop, spec vague). Sinon, sauter à l'Étape 2 avec un corps d'issue simple (contexte + attendu).

1. **Explorer le code** concerné par la tâche (zones touchées, état actuel, contraintes). Fichier > 200 lignes ou exploration large → déléguer à un agent (`Agent`, tier rapide/standard) et ne remonter que la synthèse.
2. **Trancher la conception avec l'user** : regrouper les vraies questions ouvertes (choix d'approche, périmètre, trade-offs) en UNE `AskUserQuestion` multi-questions (max 3) — pas un interrogatoire au fil de l'eau. À valeur égale, recommander l'option qui laisse le système le plus facile à changer (boussole ETC).
3. **Produire le corps d'issue structuré** :
   - **Constat** — ce qui existe / ce qui pose problème (avec refs `file:line` si utile)
   - **Pourquoi** — la valeur du changement
   - **Périmètre** — inclus ET exclu, explicitement
   - **Plan** — esquisse d'implémentation par zone (pas du code)
   - **Risques / questions tranchées** — les décisions prises en 2. et leurs raisons

Ce format rend l'issue directement consommable comme SPEC par un skill d'implémentation (`feature-loop --issue=N` chez qui l'a) — et reste la bonne forme d'issue même sans. Logger `[analyse] exploration faite, K questions tranchées, issue structurée prête`.

## Étape 2 — Métadonnées (découverte, zéro hardcode)

1. **Titre d'issue court** — ~8 mots max, lowercase, descriptif (ex. « fix login redirect on expired session »).
2. **Labels** — `glab label list` / `gh label list` (ou la liste déjà connue via le CLAUDE.md projet) → choisir 1+ label de zone pertinent ; si un schéma `Category::*` existe, en choisir **exactement un** (Bug/Feature/Chore/…). **Ne jamais inventer un label absent de la liste** (échec silencieux).
3. **Titre conventionnel MR/PR** — `type(scope): description` ; types : `feat|fix|chore|refactor|docs|style|test|ci|perf` ; **scope déduit des commits récents** (`git log --oneline -30` : réutiliser les scopes en usage) et du CLAUDE.md ; description impérative, lowercase, sans point final.
4. **Nom de branche** — `<issue-number>-<slug-du-titre>` (ex. `123-fix-login-redirect`) — convention reconnue par `feature-loop --issue=N`.
5. **Langue** — celle des issues existantes du projet (`glab issue list` / `gh issue list` sur 2-3 titres) ; à défaut, la langue de la description fournie.

## Étape 3 — Validation user (OBLIGATOIRE avant toute création)

Présenter via `AskUserQuestion` : titre d'issue, labels, titre MR/PR, branche cible, mode (ISOLER/SCAFFOLD), corps d'issue (résumé si long). Options : valider / ajuster / **issue seulement** (équivaut à `--issue-only`).

En **Mode ISOLER**, inclure dans cette même validation : la **liste des fichiers** à embarquer (exclure les artefacts non liés — screenshots, dumps, fichiers générés) et le **message de commit**. Ne committer qu'après cet accord (respecte l'interdit « git add/commit sans permission explicite »).

## Étape 4 — Créer l'issue

Corps : l'analyse structurée (Étape 1) ou un vrai contexte + attendu — **jamais un placeholder vide**.

```bash
glab issue create --title "<titre>" --description "<corps>" --label "<l1>,<l2>" --yes
# ou
gh issue create --title "<titre>" --body "<corps>" --label "<l1>" --label "<l2>"
```

Capturer le numéro d'issue (`#123`). `--issue-only` → sauter aux résumé (Étape 7).

## Étape 5 — Branche (+ commit en ISOLER)

**GitLab SCAFFOLD** : rien ici — la branche sera créée par la MR (`--create-source-branch`, Étape 6).
**GitHub (les deux modes)** : `gh issue develop <N> --base <défaut> --checkout` (branche liée à l'issue, nom `N-slug`) ; si la version de `gh` ne le supporte pas → `git switch -c <N>-<slug> origin/<défaut>`.
**GitLab ISOLER** : `git fetch origin && git switch -c <N>-<slug> origin/<défaut>` (les changements du working tree suivent si la base est compatible ; sinon `git stash` → switch → `git stash pop` → résoudre).

**Mode ISOLER, après le switch** (fichiers et message validés en Étape 3) :
```bash
git add <fichiers validés>
git commit -m "<titre conventionnel>

<corps optionnel>

Closes #<N>"
```
- Avant de pousser : lancer build/lint/tests du périmètre — on ne pousse pas du rouge.
- Vérifier qu'aucun fichier hors-scope ne part dans le commit (`git status` après add).
- `git push -u origin <N>-<slug>`.

## Étape 6 — MR / PR (description structurée, jamais vide)

**GitLab** :
```bash
glab mr create --title "<titre conventionnel>" --description "<description structurée>" \
  --related-issue <N> --source-branch "<N>-<slug>" --target-branch "<défaut>" \
  --squash-before-merge=true --remove-source-branch=true --yes
```
SCAFFOLD → ajouter `--create-source-branch` (la branche n'existe pas encore) ; ISOLER → ne PAS l'ajouter (déjà poussée).

**GitHub ISOLER** : `gh pr create --title "<titre conventionnel>" --body "<description structurée>" --base <défaut> --head <N>-<slug>`.
**GitHub SCAFFOLD — gotcha** : GitHub refuse une PR sans commit d'écart (« No commits between … ») → **pas de PR à ce stade** ; le dire dans le résumé (« PR à ouvrir au premier commit : `gh pr create --base <défaut>` »), l'issue + la branche liée suffisent.

**Description de MR/PR** — objectif : qu'un dev qui n'a pas travaillé dessus comprenne immédiatement la valeur et puisse attaquer la review sans chercher. Dense en information utile, zéro remplissage. Sections dans l'ordre :

- **Contexte** — le modèle de données ou le flux système concerné. Obligatoire si la MR touche un mécanisme non-évident (JSONB, event sourcing, saga, webhook) ; optionnel si le domaine est évident.
- **Problème** — le constat précis + un cas réel si disponible ("10 items cassés sur staging"). Pas de description du fix ici.
- **Choix retenu** (si plusieurs approches possibles) — l'option choisie ET pourquoi les alternatives ont été écartées. Critique pour les bugs non-triviaux et les décisions de design.
- **Fix** — ce qui change, en langage métier. Préférer "Avant : … / Après : …" pour les changements de comportement. Pas de liste de fichiers (le diff fait ça).
- **Effets de bord** (toujours présente) — "Aucun" si le changement est purement additif ; sinon liste explicite : ce qui devient plus tolérant / plus strict, quels appelants sont touchés, ce qui reste inchangé.
- **Vérification** — build/lint/tests passés, e2e ou smoke si réalisé. Permet au reviewer de savoir ce qui a déjà été vérifié.
- **Limites / risques** (si pertinent) — ce qui n'est pas couvert, ce qui nécessite une attention particulière en prod, les cas limites connus.
- **Guide reviewer** (si diff non-trivial) — ordre de lecture conseillé, fichiers clés à lire en premier.
- `Closes #<N>`

En SCAFFOLD (pas de diff) : Contexte + Problème + Plan attendu. Jamais de placeholder vide. Jamais de liste de fichiers modifiés.

## Étape 7 — Checkout + résumé

S'assurer que la branche est checkout localement (SCAFFOLD GitLab : `git fetch origin && git switch <branche>`). Résumé final : URL issue · URL MR/PR (ou « PR différée — GitHub scaffold ») · branche (checkout local) · labels · titre conventionnel · mode · plateforme. Si la suite est une implémentation non-triviale ET qu'un skill `feature-loop` est disponible, suggérer `feature-loop --issue=<N>` (il chargera l'issue comme spec et reprendra la branche `<N>-<slug>` créée ici). Ne pas re-suggérer si issue-mr a été invoqué depuis le pont feature-loop : feature-loop reprend la main automatiquement.

## Ce que le skill NE fait PAS

- N'implémente pas la tâche et ne clôture pas un cycle de dev — c'est le rôle d'autres skills (`feature-loop`, `branch-wrap-up`) quand ils sont disponibles.
- Ne crée RIEN sans la validation de l'Étape 3 ; ne commit/push jamais sans la liste de fichiers + message validés.
- N'invente pas de labels ; ne laisse jamais une description d'issue/MR vide.
- Ne crée pas de branche depuis une branche protégée ou porteuse de commits sans rapport.
- Ne mentionne jamais Claude/AI nulle part.
- Ne merge pas, ne pousse rien sur la branche par défaut.

## Intégration écosystème

- **feature-loop** (si disponible) : `--issue=N` charge l'issue comme SPEC et reconnaît la branche `N-slug`. Le pont (Étape 1 de feature-loop) peut invoquer issue-mr en mode ANALYSE quand la spec est vague — c'est ce mode qui produit l'issue-SPEC structurée.
- **Projets** : les spécificités (labels favoris, scopes, target particulière) se déclarent dans le `CLAUDE.md` du repo — le skill les lit ; sinon il découvre via CLI.
- **Copies projet** : une copie de ce skill peut vivre dans `.claude/skills/issue-mr/` d'un repo pour en faire profiter l'équipe. Chez un user qui a AUSSI la version globale (`~/.claude/skills`), la globale prime (précédence documentée : personal > project) — garder les contenus synchronisés depuis la globale, qui est la source de vérité.
