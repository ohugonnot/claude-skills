---
name: senior-review
description: >
  Use when the user wants a thorough senior-level fresh-eyes review of changes (working tree, staged, branch, or PR) before merge: bug hunting, security threat-model, design, tests, spec-alignment vs the linked ticket. Use it whenever the user says things like "review my changes", "relis mon code", "revue de code", "can I merge this", "is this ready to ship", "check this MR/PR", "essaie de le faire tomber", "c'est robuste ?", even if they never say "senior-review". Tiers: --quick / standard / --deep. NOT for building features (use feature-loop) nor pure-style lint (CI does that).
argument-hint: "[learn | path | --pr N | --base ref | --staged] [--quick|--deep] [--model haiku|sonnet|opus|fable] [--loop] [--ticket N] [--security] [--adversarial] [--fix] [--comment] [--no-tools]"
---

# Senior Review

**skill_version : 1.30.1** (historique : `CHANGELOG.md` ; sources : `reference/references.md`).

## Pipeline en bref

0. **Scope** : arguments, cible, taille, tier, sort du tour précédent.
1. **Context pack** : changeset, ticket, conventions, cross-fichiers, git, stack, mémoires, ledger.
2. **Gate objectif** : lint, typecheck, tests, SAST avant tout jugement, puis routage.
3. **Revue en aveugle** : un `blind-reviewer` par dimension, 5 agents par tour au plus.
4. **Receipts** : l'orchestrateur prouve chaque finding ; non prouvé, il tombe.
5. **Synthèse** : dédup, refute-panel sur le bloquant ou l'incertain, calibration.
6. **Verdict et rapport** ; 6.5 boucle si `--loop`.
7. **Journal** par `log_run.py`, learnings, ledger.

## Étape 0 — Arguments, scope et tier

Noter d'abord l'instant de départ : `start=$(date -u +%FT%TZ)` (repris par `log_run.py log --since`, Étape 7).

**`learn`** en premier argument : pas de revue, suivre `reference/learn.md` (propositions sur ce fichier jamais appliquées sans validation).

**Cible** (auto-détectée, override possible) :
- *(défaut)* **working tree** : modifs non commitées = `git status --porcelain` → tracked modifiés **+ untracked** (⚠️ `git diff` seul rate les fichiers neufs ; lire les untracked en entier).
- `--base <ref>` : revoir `git diff <ref>...HEAD` (revue de branche ; base = `origin/main`/`develop` si déduisible).
- `--staged` : `git diff --cached`.
- `--pr <N>` : récupérer la PR via `gh pr` (GitHub) ou `glab mr`/`glab issue` (GitLab) ; diff + description + commentaires.
- `<path>` : restreindre à un fichier/module.

**Tier d'effort** :
- `--quick` : 1 reviewer aveugle (Sonnet, ou le modèle choisi) sur un context-pack léger + gate outils, pas de panel.
- **confirmation** (auto-détecté, jamais demandé) : le diff n'a pas bougé depuis la dernière revue de la branche (un merge de la base sans conflit de contenu garde le même diff) → gate outils rejouée sur le sommet courant + ledger relu + notes de MR, **zéro reviewer**. C'est la réponse à « je peux merger ? ». Dès que le diff porte du code nouveau, retour au tier demandé.
- *(défaut)* **standard** : revue décomposée par dimension (∥), gate de vérification, dédup, panel **seulement** sur critical/incertain.
- `--deep` : tout — toutes dimensions + sécu threat-model + refute-panel sur tous les majors + red-check mutation sur les tests + execution-grounding live. Pré-release / scope sensible.

**Mode boucle** — `--loop`, ou toute formulation de l'utilisateur qui demande une boucle (« en boucle », « jusqu'au vert », « recommence jusqu'à ce qu'il n'y ait plus rien ») : un **contrat de terminaison**, pas une intensité (Étape 6.5).

**Plafond de fan-out : 5 agents par tour, refuteurs et passe finale compris.** Environ un relecteur par 150 LOC non générées, plancher 2, plafond 5 ; au-delà, un tour de plus. Compter les agents AVANT de lancer le message de fan-out : le hook `scripts/fanout_cap.py` (PreToolUse) refuse le 6e `blind-reviewer` du tour, et `log_run.py last`/`log` remet le compteur à zéro. Un refus = finir le tour et en ouvrir un autre. Mesure : `reference/budget.md`.

**Autres** : `--ticket <id>` (force le rattachement spec), `--security` (force la passe sécu profonde même en quick/standard), `--adversarial` (force la dimension crash/robustesse quel que soit le routage), `--fix` (applique les fixes high-confidence après confirmation), `--comment` (poste le rapport/inline sur la PR après confirmation), `--no-tools` (si lint/tests indisponibles).

**Modèles** (paramètre `model` du tool `Agent`) : relecteurs en Sonnet, correctness et sécurité au tier max en `--deep` ou scope sensible ; Haiku pour le mécanique ; refuteurs et passe finale sur un autre modèle. `--model <nom>` ou le mot seul fixe celui des relecteurs : lire alors `reference/models.md`, comme avant tout usage de Fable.

Déterminer la cible et le tier. **Cible vide** (working tree propre sans `--base`/`--pr`/path, ou diff vide) → le dire en une ligne et stop — pas de revue à vide. Lancer `python3 <skill>/scripts/log_run.py last [--base <ref>|--staged]` : `"same_diff": true` → tier **confirmation**, le dire dans le rapport. Compter la taille du diff : **> 400 LOC modifiées → avertir** et **découper** en passes ≤ 300-400 LOC (par fichier/feature), agréger+dédupliquer ensuite. Logger `[scope] <cible>, <N> fichiers, <M> LOC, tier=<...>, relecteurs=<modèle> (choisi|défaut)`.

**Sort du tour précédent** : `last` rend `pending_outcome: K` avec K > 0 → une seule question à l'utilisateur, procédure dans `reference/memory.md`, § Étape 0.

## Étape 1 — Context assembly (NE PAS sauter — c'est le différenciateur)

Construire un **context pack** (placé en tête de chaque prompt reviewer = zone stable, cache-friendly) :

1. **Le changeset** : hunks modifiés ; pour un fichier neuf (untracked), son contenu entier. Jamais le repo entier.
2. **Ticket / spec** : auto-détecter l'id (nom de branche `feature/123-…`, `--ticket`, PR liée) → `gh issue view` / `glab issue view` → titre + corps + **critères d'acceptation**. Si introuvable, le dire et reviewer sans.
3. **Conventions projet** (court, < 50 lignes) : `CLAUDE.md` racine + des dossiers touchés, `.cursor/rules`, `CONTRIBUTING.md`, configs lint. Extraire un digest des règles **réellement applicables** (`wc -l` d'abord : ≤ 200 lignes au total, lecture directe ; au-delà, agent `Explore` avec `model: haiku`). Inclure les `.claude/rules/*.md` dont les `paths` couvrent le diff.
4. **Contexte cross-fichiers** : pour chaque symbole exporté modifié, trouver **call sites / callers / implémentations** (grep, ou LSP/gopls si dispo : `findReferences`, `goToImplementation`). Détecter les *breaking changes hors diff* (un appelant que le changement casse). **Chaque fait cross-file du pack porte son receipt** — la ligne d'import ou de déclaration, pas un grep de méthode : `x.Client.Foo(` ne dit pas quel type est derrière. **Sémantique nouvelle sur un champ générique** : dès que le diff donne un sens nouveau à la valeur d'un champ existant (« si `correlation_id` est un uuid, c'est un lien vers X »), le pack liste **tous les producteurs** de ce champ (`grep "Field:"`), avec leur type de valeur.
5. **Historique git** : `git blame`/`git log -p` ciblé sur les lignes/fichiers touchés → *pourquoi* ce code existe, changements récents liés, anti-régression.
6. **Stack / architecture / versions** : langage, framework, **archi dominante** (CQRS/ES, hexagonal, event-driven, microservices, monolithe modulaire…), deps majeures + versions. En cas d'archi/dep peu familière, une recherche web ciblée est permise (cf. principe « recherche externe »).
7. **Learnings repo** (mémoire de feedback) : lire `~/.claude/projects/<encoded-cwd>/memory/senior_review_learnings.md` s'il existe → FP déjà confirmés à ne pas répéter + conventions d'équipe découvertes (plafond et format d'entrée : `reference/memory.md`). Logger `[context] N learnings repo chargés`.
8. **Lessons cross-projet (mémoire du skill)** : `~/.claude/skill-memory/senior-review-lessons.md`, **hors dépôt** ; absent au premier run, continuer sans. Leçons **confirmées** sur *comment reviewer*. Ne **jamais** charger `senior-review-lessons-candidates.md`, qui porte les leçons vues une seule fois. Chaque leçon porte une étiquette de dimension en tête de ligne : `[spec] [correctness] [security] [design] [tests] [perf] [harness]`. Les injecter dans le context pack en **routant chaque leçon vers la dimension concernée** ; `[harness]` va à l'orchestrateur et à l'Étape 4. **En tier `--quick`, ne charger que `[harness]` et `[correctness]`** (`grep -E '^- \[(harness|correctness)\]' lessons.md`), les autres dimensions n'y sont pas reviewées. Logger `[context] M lessons confirmées chargées`.
   **Misses cross-projet** : `~/.claude/skill-memory/senior-review-misses.md` — **hors dépôt**, même régime d'absence, les **échecs** de la revue (`[bruit]`, `[manqué]`, `[coût]`). Les injecter **uniquement dans « ce qu'on NE flague PAS »** (Étape 3) et jamais dans le brief de recherche d'un reviewer — un miss est un filtre, pas une piste. Logger `[context] K misses chargés`.

**Reconnaissance d'architecture → mode spécialiste.** **Nommer la combinaison** stack + archi (ex. « Shopify + CQRS/ES en Go »). Si elle porte des invariants propres qui changent la revue et que l'utilisateur n'a pas donné l'angle, demander via `AskUserQuestion` « je revois en expert senior <stack> ? » (en non-interactif, assumer le mode détecté **en le signalant**). Chaque relecteur devient alors un **senior 10+ ans de cette stack précise** et reçoit la **liste d'invariants/pièges connus** à vérifier en priorité. Exemples : *CQRS/ES* → idempotence des commandes, immutabilité/rejouabilité des events, cohérence projection↔agrégat, sagas/effets de bord rétroactifs ; *Shopify* → pagination/éviction, normalisation E.164, scopes/permissions, throttling, champs version-dépendants de l'Admin API ; *front* → hydratation, a11y, états de chargement.

9. **Ledger d'arbitrages de CETTE branche** : lire `~/.claude/projects/<encoded-cwd>/memory/arbitrages-<branche|PR>.md` s'il existe ; ses trois catégories (`tranché`, `prouvé`, `hors périmètre`) et son format sont dans `reference/memory.md`. Il ne porte **jamais** les findings, sévérités ou verdicts des tours précédents, qui ancreraient le jugement. **L'orchestrateur** lit les trois catégories ; **les reviewers** ne reçoivent que `tranché` aplati en « ne flague pas ça » et `prouvé` en « ne le refais pas », jamais le récit. Une entrée `tranché` reste **réouvrable au prix d'un receipt exécuté**. Logger `[context] ledger: N tranchés, M prouvés (tour K)`.
   S'il existe d'autres `arbitrages-*.md` que celui de la branche : balayage selon `reference/memory.md`, lancé en `run_in_background` pendant le fan-out de l'Étape 3.

Logger `[context] ticket=<#id|absent>, N conventions, M call-sites tracés, stack=<...>, mode spécialiste=<stack | généraliste> (confirmé|détecté)`.

## Étape 2 — Gate objectif (signal externe avant tout jugement LLM)

Lancer les outils dispos sur le périmètre (paralléliser) :
- **lint** (golangci-lint/eslint/ruff…), **typecheck**, **tests** du périmètre, **SAST** (gosec/semgrep/bandit).
Passer leurs sorties **résumées** (échecs, comptes, lignes clés) au context pack : les reviewers **ne re-flaguent pas** ce qu'un outil attrape et **s'appuient** dessus comme findings ancrés. Si un outil manque → `--no-tools`/skip gracieux, le noter (la robustesse de la revue baisse, le dire).

**Gate détendue** : config de lint, test ou CI touchée (`.golangci.yml`, `.eslintrc*`, seuil, job désactivé) ou `grep -nE '^\+.*(nolint|eslint-disable|t\.Skip)'` non vide sur le diff → 🔴 bloquant tant que la MR ne le justifie pas explicitement.

Cible non-code (oracle mécanique) et échec d'outil (attribution base vs diff avant de l'imputer) : `reference/gate.md`.

**Routage des dimensions** : diff majoritairement texte → dimension `contenu` à la place de `perf` et `design`, `correctness` ne portant que sur le code d'outillage ; n'activer que les lentilles pertinentes au diff (pas de passe « injection SQL » sans accès DB, pas de passe a11y sans front). Diff qui touche `migrations/` ou un `.sql` de migration → dimension `migrations`. Logger `[gate] lint/typecheck/tests/SAST: <résumés>` + `[route] dimensions actives: <liste>`.

**Quand activer `crash / robustesse`** (jamais par réflexe) : si le diff **calcule sur des valeurs venues d'un autre système** (montants, quantités, dates lues en base ou reçues d'une API), s'il tourne **sans surveillance** (job, worker, projecteur, cron, consumer), s'il touche un **chemin d'argent ou de conservation de données**, ou si l'utilisateur le demande en toutes lettres (« essaie de le faire tomber », « c'est robuste ? », `--adversarial`). Sur un diff de présentation, de configuration ou de documentation : ne pas l'activer. Quand elle est active et que le budget est plein, c'est `design` qui cède la place, pas `correctness`.

## Étape 3 — Revue décomposée en aveugle (agents ∥, reviewer ≠ auteur)

Un **agent distinct par dimension**, contexte vierge, recevant le context pack (stable) + sa rubrique (volatile). Dimensions standard (activer selon routage) :

- **spec-alignment** : `reference/dimensions/spec.md`
- **correctness / bugs** : `reference/dimensions/correctness.md`
- **security** : `reference/dimensions/security.md`
- **crash / robustesse** (cond., cf. routage) : `reference/dimensions/crash.md`
- **design / maintainability** : `reference/dimensions/design.md`
- **tests** : `reference/dimensions/tests.md`
- **texte d'interface** (cond., diff qui ajoute ou change un libellé vu par un utilisateur) : `reference/dimensions/ui-text.md`
- **contenu / prose** (cond., diff de texte) : `reference/dimensions/content.md`
- **perf** (cond., avec ux/a11y/i18n si front) : `reference/dimensions/perf.md`
- **migrations** (cond., cf. routage ; budget plein : `correctness` la lit en plus de sa rubrique) : `reference/dimensions/migrations.md`

Le prompt relecteur = context pack + « ce qu'on NE flague PAS » + chemins absolus de `reference/dimensions/_common.md` (brief commun) et de sa rubrique, à lire dans son premier lot d'appels. L'orchestrateur ne recopie jamais une rubrique. Le digest conventions (Étape 1.3) est le seul canal de conventions des relecteurs : l'agent ne charge aucun CLAUDE.md.

Logger `[review:<dim>] N findings (x bloquants, y importants)`.

*Exécution* : un appel `Agent` par dimension, lancés en parallèle dans un même message, avec `subagent_type` = **`blind-reviewer`**, l'agent livré par le plugin (`senior-review:blind-reviewer` plugin installé, `blind-reviewer` s'il est lié dans `~/.claude/agents/`), sans Edit ni Write. Absent des types du tool `Agent` : `reference/models.md`. Même agent pour les refuteurs (Étape 5), la passe finale (Étape 6) et les tours de boucle (Étape 6.5).

**Garde de l'arbre autour de chaque fan-out de relecteurs** : `python3 <skill>/scripts/tree_guard.py snap` juste avant de les lancer, `check` dès qu'ils rendent, avant toute commande de l'orchestrateur (le Bash des relecteurs écrit où il veut ; ce qu'elle voit : docstring du script). Les correctifs de l'orchestrateur (`--fix`, boucle) tombent entre un `check` et le `snap` suivant. **Exit 1 = écart non annoncé : arrêter la revue, boucle comprise, et montrer l'écart à l'utilisateur sans rien restaurer soi-même** (lui seul sait ce qui est son travail). Exit 2 (pas un dépôt git) : le dire au rapport.

**Un relecteur qui plante ou rend un retour vide est relancé UNE fois**, neuf et avec le même context pack. Au second échec, sa dimension est déclarée « non couverte » dans le rapport, avec la raison. Le verdict ne devient jamais `approve` sur une dimension silencieuse : l'absence de finding n'est pas une revue propre.

## Étape 4 — Gate de vérification ("receipts")

**Aucun finding critical/major n'est remonté sans preuve.** Pour chacun, l'**orchestrateur exécute lui-même** le `verification_plan` (grep/exec/Read direct) — pas d'agent de vérification dédié, sauf besoin d'isolation (ex. mutation destructive sur un fichier suivi) :
- **grep/ast-grep** : confirmer que le pattern existe vraiment et sur une ligne modifiée.
- **exécution sandbox** : reproduire (snippet, requête, test qui échoue sur le code actuel — fail-to-pass, TDD-Bench). Pour un bug allégué → écrire le test rouge ; s'il ne rougit pas, le finding est suspect → drop ou rétrograder.
- **sécurité** : confirmer que la source est réellement attaquant-contrôlée ET atteint le sink (traçage flux). Sinon → drop.
- **« ça va tout casser »** (un changement de contrat ferait échouer N flux) → grille appelant par appelant avant tout panel : `reference/receipts.md`.
- **« tests faibles »** → **red-check mutation** : muter la ligne ciblée (inverser une condition / constante, type-préservant), relancer la suite. Si rien ne rougit → le test est vacant → finding réel. Si le test ciblé rougit (et lui seul) → les tests protègent → finding FAUX, drop.
  **Passer par `scripts/mutate.py`, pas par des commandes improvisées** : spec JSON (`name`, `file`, `old`, `new`, `cmd`, `expect`, `must_match` optionnel), format et garanties dans `mutate.py --help`.
  Un écart entre prédiction et résultat **se re-mesure avant d'être cru** : `ANCHOR`, `NO-TESTS` et `NO-MATCH` disent que le harnais a raté, pas que le test est faible.

Muter un fichier suivi : seulement via `scripts/mutate.py`, jamais `git checkout/restore`, aucun `.bak` dans le dépôt ; détail `reference/receipts.md`.

Findings non prouvés → **drop silencieux** (ou rétrogradés en `low confidence — à vérifier`). **Exception au drop** : un désaccord inter-couches (count↔display, granularité de jointure) dont le receipt exige de fabriquer un jeu de données multi-entités, voir `reference/receipts.md`. Logger `[verify] k/n findings confirmés, j droppés (faux positifs)`.

## Étape 5 — Synthèse calibrée (dédup + panel adversarial ciblé)

1. **Dédup** cross-dimensions (même `file:line` / même cause).
2. **Refute-panel — seulement sur le douteux/critique** (proportionné : pas sur les nits) : pour chaque finding **bloquant** ou à **confiance non-haute**, un **skeptique indépendant** (modèle/famille ≠ si possible ; sinon prompt reformulé + ordre inversé pour casser le biais de position) est mandaté pour **RÉFUTER**. On garde le finding si la majorité ne le réfute pas. Escalade graduée : 1 refuteur → si désaccord, panel de 3 (médiane/majorité) → si toujours partagé sur un bloquant, **présenter à l'user** (ne jamais trancher seul un bloquant incertain).
3. **Calibration** : confiance finale par finding ; sous le seuil → `low confidence`. **Tiers de sévérité** : 🔴 bloquant (vrai merge-blocker) / 🟡 important / 🔵 nit·suggestion / 👍 praise (1-2 max). Mapping déterministe quand possible (MUST→bloquant, SHOULD→important, MAY→suggestion). **Cap nits ≤ 5 inline**, le reste en compte résumé.

Logger `[panel] x findings réfutés, y confirmés` · `[calib] 🔴N 🟡N 🔵N`.

## Étape 6 — Verdict + rapport (discipline signal/bruit)

Rapport structuré, concis, **commente le code jamais l'auteur**, chaque finding avec `file:line` + raison + fix concret + confiance (+ preuve de vérif si critique) :

```markdown
# Revue — <cible> (<N fichiers, M LOC>)

## Spec-coverage
<Le diff fait-il ce que le ticket #<id> demande ? — Oui / Partiel (gaps listés) / Hors-sujet>
<Scope creep éventuel : modifs hors ticket>
<Décisions non spécifiées : choix de l'implémentation que le ticket ne précisait pas, ou "aucune">

## 🔴 Bloquants (N)   <vrais merge-blockers — sinon "aucun">
1. <constat> — `file.go:42` (confiance: haute) — preuve: <vérif> — fix: <concret>

## 🟡 Importants (N)
…

## 🔵 Mineurs / suggestions (N inline, +K en plus non listés)
…

## 👍 Bien vu (≤2)
…

## Verdict
<approve | request-changes | needs-discussion> — <1 phrase>
Métriques: lint <…> · typecheck <…> · tests <…/…> · SAST <…> · coût: <N agents, ~M tokens>
```

Si rien de matériel : **le dire** (« Aucun bloquant. N suggestions mineures. Le changement améliore la base. »), le silence est une feature. Le seuil de greenlight : le changement **améliore** la base, pas « est parfait ».

**Coût mesuré, pas espéré** : sommer les `subagent_tokens` retournés par chaque appel `Agent` du run (reviewers + refuteurs) pour la ligne `coût:` — mesure objective, base de comparaison avant/après toute optimisation du skill.

Verdict `approve` ET un skill `branch-wrap-up` disponible ET la cible est du travail local non clôturé (working tree/branche, pas une PR déjà ouverte) → suggérer en une ligne `branch-wrap-up --no-review` pour la clôture (commit/push/MR-PR), la review étant faite.

**Passe finale sur un autre modèle, avant `approve`** : dès que 3 relecteurs ou plus d'un même modèle sont passés. Opus par défaut, jamais Fable sans `AskUserQuestion` (sauf `--model fable`). Aveugle, diff complet, tranché/prouvé fournis, aucune liste de pistes, finir par « ce qui m'a surpris ». En standard/deep hors boucle, si les dimensions actives sont ≤ 4, la lancer dans le même fan-out que les relecteurs (plafond 5 tenu) ; sinon après. Brief détaillé : `reference/final-pass.md`.

Grounding live et vérif visuelle (script Playwright) : `reference/gate.md`.

**`--comment`** : après confirmation, poster via `gh pr comment`/`gh pr review` (GitHub) ou `glab mr note` (GitLab), inline avec liens `file#Lx-Ly` (SHA complet pour GitHub). **`--fix`** : appliquer SEULEMENT les fixes high-confidence, dans le working tree, après confirmation — jamais de commit/push auto.

## Étape 6.5 — Boucle (mode `--loop` uniquement)

Contrat : on boucle tant qu'un tour a modifié du code ; arrêt au premier tour sans bloquant ET sans modification ; pas de tour N+1 avec un 🟡 ouvert ; plafond 5 tours ; relecteurs frais sur le delta seul. Procédure complète : `reference/loop.md`, à lire dès que le mode boucle est actif.

## Étape 7 — Learnings (ledger de branche + mémoire par repo + lessons cross-projet)

- **Ligne de run** : une par revue, TOUJOURS, quel que soit le projet, la branche ou le verdict, **écrite par le script et jamais à la main** : `python3 <skill>/scripts/log_run.py log --tier <quick|standard|deep|confirmation> [--loop] --verdict <approve|approve-after-fixes|request-changes|needs-discussion> --model <modèle des relecteurs> --loc N --raised N --confirmed N --dropped-gate N --refuted-panel N [--settled N] [--out-of-scope N] --agents N [--tokens N] [--fixed N --rejected N --deferred N] [--base <ref>|--staged] [--branch pr-N] [--transcript auto --since <start>]`. Ce sont des comptes, jamais des estimations : `--tokens` s'omet plutôt que s'estimer, `--fixed`/`--rejected`/`--deferred` viennent de l'utilisateur ou de la boucle, jamais du jugement du modèle. **Exit ≠ 0 = les compteurs sont faux** : recompter et relancer, jamais contourner par un `echo >>`. Invariants, champs dérivés et `orch_*` (ajoutés au `coût:` du rapport) : `log_run.py --help`. Un `OVER CAP` imprimé se signale dans le rapport. Le journal n'est **jamais chargé** en revue, il sert à `learn`.
Learnings repo, lessons, misses et ledger : règles, formats et plafonds dans `reference/memory.md`, à lire dès qu'un FP est confirmé, qu'une leçon ou un miss est à écrire, ou à partir du tour 2.

## Logs (préfixes, style factuel, pas d'emojis hors rapport final)
`[scope]` `[context]` `[gate]` `[route]` `[review:<dim>]` `[verify]` `[panel]` `[calib]` `[verdict]` `[report]` `[comment]` `[fix]` `[learn]`. 1 ligne par sous-étape clé, pas de silence > 3 min.

`lessons.md` et `misses.md`, à côté de ce fichier, sont des instantanés publiés et promus à la main : jamais chargés en revue, les mémoires de travail sont hors dépôt (Étape 1.8).

## Principes non négociables

La qualité se juge au rapport signal/bruit, pas au rappel : findings prouvés et actionnables (`file:line`, raison, fix), silence assumé quand rien de matériel ; le second levier est le contexte (Étape 1). Les sources de chaque principe : `reference/references.md`.

<!-- LOCKED: modif humaine directe uniquement (jamais via une boucle d'auto-amélioration). -->

- **Reviewer ≠ auteur (blind review).** Le *self-preference bias* est prouvé et causal : un modèle qui juge sa propre sortie se surnote. Les agents reviewers tournent en **contexte vierge**, ne voient PAS le prompt d'implémentation, et — si l'auteur du code est connu comme étant un modèle donné — sont d'un **modèle/famille différent**. Le nom du développeur n'entre jamais dans le prompt.
- **Pas de finding sans preuve vérifiée.** Tout finding cite `file:line` ET passe une **vérification** (grep/ast-grep, exécution en sandbox, test qui échoue, traçage du flux) avant d'être remonté. Un finding non vérifiable est **droppé silencieusement**.
- **Signal > recall.** Mieux vaut 3 vrais bugs que 3 vrais + 11 faux. Cap des nits (≤ 5 inline, le reste compté en résumé), **silence explicite** quand rien de bloquant, et une section **« ce qu'on NE flague PAS »** aussi importante que « ce qu'on cherche ».
- **CoT avant verdict, confiance par finding.** Raisonner (constat → pourquoi → est-ce causé par les lignes modifiées ?) AVANT de poser sévérité + note. Confiance basse → marquée « à vérifier manuellement », jamais bloquante.
- **Signal externe, pas auto-critique en boucle.** La revue s'ancre sur des signaux EXTERNES (lint, typecheck, tests, SAST, exécution), jamais sur la seule relecture du modèle. Pas de « revue de la revue » en boucle fermée.
- **Scope = le diff.** On ne note jamais du code legacy non modifié (même mauvais), ni ce qu'un linter/formatter/CI attrape déjà, ni les fichiers générés/vendored/lock.
- **Spec-alignment est une dimension de premier rang.** Première question : *le diff implémente-t-il ce que le ticket demande* (couverture complète + pas de scope creep) — pas seulement « est-ce correct ».
- **La sécurité est une lentille DISTINCTE** (mindset attaquant, modèle de menace), pas fondue dans la revue de correction : objectifs opposés (la sécu optimise le rappel/paranoïa, la correction la précision). Toujours son propre agent.
- **Effort proportionné.** Pas de panel multi-agents sur un diff de 10 lignes. Paliers `--quick` / standard / `--deep`.
- **Discipline tokens/latence.** À qualité égale, le run le moins cher gagne : (a) le **context pack** (Étape 1) est écrit UNE fois, stable, réutilisé verbatim par tous les reviewers (cache-friendly Anthropic) — jamais reconstruit ni re-collé par dimension ; (b) les **receipts** de l'Étape 4 sont vérifiés par **l'orchestrateur lui-même** (grep/exec/Read direct), jamais délégués à un agent dédié — un aller-retour agent coûterait un tour complet pour reproduire ce qu'une commande fait en un appel ; (c) le **refute-panel** (Étape 5) ne tourne QUE sur le critique/incertain, jamais en aveugle sur l'ensemble des findings ; (d) les sorties d'outils (Étape 2 : lint/tests/SAST) entrent **résumées** dans le context pack (échecs + comptes, pas le log brut complet) ; (e) une **re-revue du même diff**, dans la session ou après un `/clear` : procédure dans `reference/loop.md`, section « Re-revue du même diff ».
- **Review-only par défaut.** On propose des fixes ; on n'édite/poste rien sans `--fix`/`--comment` explicite, et on confirme avant toute action sortante (commentaire PR, push).
- **Mode spécialiste selon l'architecture détectée.** Un généraliste rate les invariants propres à une stack. La revue **reconnaît l'archi** (Étape 1) — ex. « Shopify + CQRS/ES en Go », « Next/tRPC », « Spring/DDD » — et bascule en **expert senior de cette stack** : on le **propose/confirme à l'utilisateur** quand l'angle n'est pas déjà donné, et chaque reviewer reçoit la persona experte + les invariants/pièges connus de l'archi à vérifier en priorité. Le mode spécialiste n'élargit pas le bruit : il **affine** ce qu'on cherche, pas le nombre de findings.
- **Recherche externe autorisée en cas de doute (avec discipline).** Quand un doute porte sur un comportement *version/API/framework-spécifique* (sémantique d'un flag, API tierce, CVE, idiome récent, plafond/pagination d'une API), un reviewer PEUT consulter le web (`WebSearch`/`WebFetch`) plutôt que deviner ou sur-flaguer. Discipline : source **primaire/officielle** d'abord, **citer la source + sa date**, et **re-vérifier contre le code et la version réelle du repo** — une réponse web *informe* mais n'est jamais le receipt (le receipt reste grep/exec/test). En cas d'indispo réseau, le dire et baisser la confiance.

## Ce qu'on NE flague PAS (aussi important que ce qu'on cherche)
- Ce que lint/format/typecheck/CI attrape déjà (indentation, imports, style mécanique).
- Le code **non modifié** (pre-existing), même mauvais — ce n'est pas ce changement.
- Fichiers générés, lock files, `vendor/`, assets minifiés.
- Defense-in-depth quand la défense primaire est adéquate.
- La duplication de code identique *par hasard* quand les deux sites évolueront pour des raisons différentes — fusionner couplerait à tort (DRY porte sur le savoir, pas le texte).
- Une fonction longue mais linéaire et claire — ne suggérer un découpage que s'il simplifie l'appelant (fonction profonde > fonction courte ; le sur-découpage en helpers à enchaîner est le défaut inverse).
- Code de test qui viole intentionnellement des règles de prod.
- Un crash **reproduit en isolation mais démontré inatteignable** par le code appelant : il se signale en une ligne, il ne se classe jamais bloquant. Idem pour un crash dont la propagation a été tracée jusqu'à un recover qui le borne à une requête.
- Nitpicks qu'un senior ne soulèverait pas ; verbosité ; bikeshedding.
- Findings sans `file:line` ou non vérifiables → jamais remontés.

## Tools requis (charger via ToolSearch au besoin)
- `Agent` (`subagent_type: blind-reviewer`, `model` selon Étape 0) — **socle** : un appel distinct par dimension/refuteur, contexte vierge ; la mère ne joue jamais un rôle de reviewer qu'elle orchestre. Fan-out par `Workflow` si disponible : `reference/models.md`.
- `Bash` (git incl. untracked, outils du gate, receipts, `run_in_background`), `gh`/`glab`, LSP/`gopls` si dispo pour le cross-file, `WebSearch`/`WebFetch` en appui jamais comme receipt. Vérif visuelle par script Playwright : `reference/gate.md`.

## Ce que le skill NE fait PAS
<!-- LOCKED -->
- Ne construit pas de feature (c'est `feature-loop`). Ne fait pas de revue de pur style (CI/linter).
- Ne commit/push/merge jamais ; ne poste/édite rien sans `--comment`/`--fix` + confirmation.
- N'invente pas de finding : pas de `file:line` valide + vérifié → pas de finding.
- Ne note pas le code legacy non modifié ; ne re-flague pas ce qu'un outil attrape.
- Ne tranche pas seul un bloquant incertain → escalade user.
- En mode boucle, ne déclare jamais la boucle finie tant qu'un tour a modifié du code : le delta de ce tour n'a pas été relu, et son auteur ne peut pas s'en porter juge.
- Ne reste pas silencieux > 3 min (logs continus).

## Garanties
<!-- LOCKED -->
- **Blind review (reviewer ≠ auteur)** — biais d'auto-préférence neutralisé.
- **Context-first** (diff + cross-file + ticket + conventions + git + env) — le levier n°1 du catch-rate.
- **Spec-alignment** comme dimension de premier rang — attrape les gaps « correct mais pas ce qui était demandé ».
- **Gate objectif (outils) avant jugement LLM** + **gate de vérification** des findings — anti-hallucination/FP.
- **Décomposition par dimension** + sécurité en lentille distincte (mindset attaquant).
- **Panel adversarial ciblé** (réfutation) sur le critique/incertain — moins de biais qu'un juge unique, coût maîtrisé.
- **Signal/bruit discipliné** : cap nits, silence assumé, what-NOT-to-flag, sévérité calibrée.
- **Paliers d'effort** quick/standard/deep — proportionné à l'enjeu.
- **Mode boucle : terminaison sur le delta, pas sur le rapport** — tant qu'un tour modifie du code, un tour de plus le relit en aveugle ; on s'arrête au premier tour sans bloquant ET sans modification.
- **Review-only par défaut** ; actions sortantes sur flag + confirmation.
- **Mémoire de learnings par repo** — ne répète pas les FP, s'adapte aux conventions.
- **Ledger d'arbitrages par branche** — les tours suivants ne re-litigent pas ce qui est tranché ni ne re-paient les receipts, sans jamais voir les findings précédents : l'aveuglement reste intact.
