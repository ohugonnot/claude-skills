---
name: senior-review
description: >
  Use when the user wants a thorough senior-level fresh-eyes review of changes (working tree, staged, branch, or PR) before merge — bug hunting, security threat-model, design, tests, spec-alignment vs the linked ticket. Research-grounded pipeline: context-first assembly (cross-file call sites, conventions, git history, ticket), objective tool gate, parallel blind reviewers (reviewer ≠ author), verification gate (every critical finding needs a receipt: grep/exec/red test), adversarial refute-panel on critical/uncertain findings only. Optimizes signal/noise over recall: caps nits, explicit what-NOT-to-flag, silence when nothing material. Tiers: --quick / standard / --deep. Flags: --pr N, --base ref, --staged, --ticket N, --security, --fix, --comment, --no-tools. NOT for building features (use feature-loop) nor pure-style lint (CI does that).
argument-hint: "[path | --pr N | --base ref | --staged] [--quick|--deep] [--ticket N] [--security] [--fix] [--comment] [--no-tools]"
---

# Senior Review

**skill_version : 1.2.0** (historique : `CHANGELOG.md`). Revue de code de niveau senior, conçue à partir de l'état de l'art académique (LLM-as-judge, vérification, mutation) et des meilleurs outils de revue IA (CodeRabbit, Greptile, Cursor BugBot, GitHub Copilot agentic, Qodo, Snyk).

**Fichiers du skill (progressive disclosure)** : `lessons.md` (meta-leçons cross-projet, chargées à l'Étape 1.8), `reference/references.md` (sources détaillées, à la demande), `CHANGELOG.md` (historique).

## Posture (ce qui distingue une revue excellente d'une revue bruyante)

La recherche converge sur **un seul vrai critère de qualité : le rapport signal/bruit, pas le recall.** Un reviewer qui crie au loup est désactivé — c'est la première cause d'abandon des outils de revue IA (WirelessCar 2025, Graphite). Donc : peu de faux positifs, findings prouvés, silence assumé quand rien de matériel, et chaque finding actionnable (file:line + raison + fix). Le second levier le plus fort est le **contexte** : le diff seul plafonne le catch-rate (~44 %), le contexte cross-fichiers + intention le double (~82 %, bench Greptile). D'où une revue **context-first** et **liée au ticket** (une revue doit vérifier que le code fait *ce qui était demandé*, pas seulement qu'il est correct — la dimension la plus souvent oubliée et la plus chère en prod).

## Principes non négociables

<!-- LOCKED: modif humaine directe uniquement (jamais via une boucle d'auto-amélioration). -->

- **Reviewer ≠ auteur (blind review).** Le *self-preference bias* est prouvé et causal : un modèle qui juge sa propre sortie se surnote (Panickssery 2024, SPB ≈ 0.52 ; Wataoka 2024). Les agents reviewers tournent en **contexte vierge**, ne voient PAS le prompt d'implémentation, et — si l'auteur du code est connu comme étant un modèle donné — sont d'un **modèle/famille différent**. Le nom du développeur n'entre jamais dans le prompt.
- **Pas de finding sans preuve vérifiée.** Tout finding cite `file:line` ET passe une **vérification** (grep/ast-grep, exécution en sandbox, test qui échoue, traçage du flux) avant d'être remonté. Un finding non vérifiable est **droppé silencieusement**. Les LLMs sur-flaggent (overcorrection systématique, arXiv:2603.00539) ; l'execution-grounding rejette ~60 % des faux positifs (arXiv:2604.10800).
- **Signal > recall.** Mieux vaut 3 vrais bugs que 3 vrais + 11 faux. Cap des nits (≤ 5 inline, le reste compté en résumé), **silence explicite** quand rien de bloquant, et une section **« ce qu'on NE flague PAS »** aussi importante que « ce qu'on cherche » (Cloudflare : « telling an LLM what not to do is where the value is »).
- **CoT avant verdict, confiance par finding.** Raisonner (constat → pourquoi → est-ce causé par les lignes modifiées ?) AVANT de poser sévérité + note (+13 pp, G-Eval / LLMBar). Confiance basse → marquée « à vérifier manuellement », jamais bloquante.
- **Signal externe, pas auto-critique en boucle.** L'auto-correction LLM sans oracle dégrade (Huang ICLR 2024). La revue s'ancre sur des signaux EXTERNES (lint, typecheck, tests, SAST, exécution), jamais sur la seule relecture du modèle. Pas de « revue de la revue » en boucle fermée.
- **Scope = le diff.** On ne note jamais du code legacy non modifié (même mauvais), ni ce qu'un linter/formatter/CI attrape déjà, ni les fichiers générés/vendored/lock.
- **Spec-alignment est une dimension de premier rang.** Première question : *le diff implémente-t-il ce que le ticket demande* (couverture complète + pas de scope creep) — pas seulement « est-ce correct ». Sans la description du problème, la revue LLM perd ~22 % de précision (arXiv:2505.20206).
- **La sécurité est une lentille DISTINCTE** (mindset attaquant, modèle de menace), pas fondue dans la revue de correction : objectifs opposés (la sécu optimise le rappel/paranoïa, la correction la précision). Toujours son propre agent.
- **Effort proportionné.** Pas de panel multi-agents sur un diff de 10 lignes. Paliers `--quick` / standard / `--deep`.
- **Review-only par défaut.** On propose des fixes ; on n'édite/poste rien sans `--fix`/`--comment` explicite, et on confirme avant toute action sortante (commentaire PR, push).
- **Mode spécialiste selon l'architecture détectée.** Un généraliste rate les invariants propres à une stack. La revue **reconnaît l'archi** (Étape 1) — ex. « Shopify + CQRS/ES en Go », « Next/tRPC », « Spring/DDD » — et bascule en **expert senior de cette stack** : on le **propose/confirme à l'utilisateur** quand l'angle n'est pas déjà donné, et chaque reviewer reçoit la persona experte + les invariants/pièges connus de l'archi à vérifier en priorité. Le mode spécialiste n'élargit pas le bruit : il **affine** ce qu'on cherche, pas le nombre de findings.
- **Recherche externe autorisée en cas de doute (avec discipline).** Quand un doute porte sur un comportement *version/API/framework-spécifique* (sémantique d'un flag, API tierce, CVE, idiome récent, plafond/pagination d'une API), un reviewer PEUT consulter le web (`WebSearch`/`WebFetch`) plutôt que deviner ou sur-flaguer. Discipline : source **primaire/officielle** d'abord, **citer la source + sa date**, et **re-vérifier contre le code et la version réelle du repo** — une réponse web *informe* mais n'est jamais le receipt (le receipt reste grep/exec/test). En cas d'indispo réseau, le dire et baisser la confiance.

## Pipeline

```
0. PARSE + DÉTECTION CIBLE (working tree défaut / staged / branche vs base / PR)  + tier (quick|standard|deep)
   ↓
1. CONTEXT ASSEMBLY (le différenciateur n°1)
   diff (incl. untracked!) + TICKET/spec + conventions projet (CLAUDE.md/rules/lint)
   + cross-file (call sites/callers/impls) + git blame/log + stack/versions + learnings repo
   ↓  → "context pack" stable (cache-friendly), réutilisé par tous les reviewers
2. GATE OBJECTIF (signal externe AVANT jugement LLM)
   lint + typecheck + tests + SAST (gosec/semgrep/…) → nourrit les reviewers (ne pas re-flaguer)
   + routage dimensions pertinentes (pas de chasse SQLi sans DB — iCodeReviewer)
   ↓
3. REVUE DÉCOMPOSÉE EN AVEUGLE (agents spécialisés ∥, reviewer ≠ auteur)
   spec-alignment · correctness/bugs · security(threat-model) · design/maintainability · tests · [perf/ux cond.]
   chacun : CoT → findings {file:line, sévérité, confiance, raison, fix, PLAN DE VÉRIFICATION}
   ↓
4. GATE DE VÉRIFICATION ("receipts" — tue les faux positifs)
   chaque finding (surtout critical/major) PROUVÉ : grep/ast-grep, exécution sandbox, test qui rougit,
   traçage flux source→sink. Non prouvé → drop. "tests faibles" → red-check par mutation.
   ↓
5. SYNTHÈSE CALIBRÉE  (dédup cross-dimensions + panel adversarial sur le douteux/critique seulement)
   refute-panel (skeptique indépendant tente de réfuter ; majorité pour garder) — PoLL
   + calibration confiance + tiers sévérité (🔴 bloquant / 🟡 important / 🔵 nit·suggestion / 👍 praise)
   ↓
6. VERDICT + RAPPORT (signal/bruit discipliné)  → spec-coverage verdict + go/no-go ; silence si rien
   [option --comment → poste PR ;  --fix → applique les fixes high-confidence, après confirmation]
   ↓
7. LEARNINGS (mémoire par repo : FP confirmés, conventions découvertes) + lessons cross-projet
```

## Logs (préfixes, style factuel, pas d'emojis hors rapport final)
`[scope]` `[context]` `[gate]` `[route]` `[review:<dim>]` `[verify]` `[panel]` `[calib]` `[verdict]` `[report]` `[comment]` `[fix]` `[learn]`. 1 ligne par sous-étape clé, pas de silence > 3 min.

## Parsing des arguments

**Cible** (auto-détectée, override possible) :
- *(défaut)* **working tree** : modifs non commitées = `git status --porcelain` → tracked modifiés **+ untracked** (⚠️ `git diff` seul rate les fichiers neufs ; lire les untracked en entier).
- `--base <ref>` : revoir `git diff <ref>...HEAD` (revue de branche ; base = `origin/main`/`develop` si déduisible).
- `--staged` : `git diff --cached`.
- `--pr <N>` : récupérer la PR via `gh pr` (GitHub) ou `glab mr`/`glab issue` (GitLab) ; diff + description + commentaires.
- `<path>` : restreindre à un fichier/module.

**Tier d'effort** :
- `--quick` : 1 reviewer aveugle (Sonnet) sur un context-pack léger + gate outils, pas de panel. Passe PR rapide.
- *(défaut)* **standard** : revue décomposée par dimension (∥), gate de vérification, dédup, panel **seulement** sur critical/incertain.
- `--deep` : tout — toutes dimensions + sécu threat-model + refute-panel sur tous les majors + red-check mutation sur les tests + execution-grounding live. Pré-release / scope sensible.

**Autres** : `--ticket <id>` (force le rattachement spec), `--security` (force la passe sécu profonde même en quick/standard), `--fix` (applique les fixes high-confidence après confirmation), `--comment` (poste le rapport/inline sur la PR après confirmation), `--no-tools` (si lint/tests indisponibles).

**Dimensionnement modèles** : orchestrateur = le modèle de la session (le plus capable disponible — Opus, Fable… ; synthèse, arbitrage). Reviewers dimension = tier standard (Sonnet ; correctness/sécu escaladent au tier max si `--deep` ou scope sensible). Refuteurs panel = tier standard (modèle/famille ≠ du reviewer initial via MCP si disponible — l'outillage natif est mono-famille Claude, la diversité réelle vient surtout du prompt reformulé + ordre inversé qui cassent le biais de position). Tâches mécaniques (récup ticket, extraction conventions) = tier rapide (Haiku). **Les noms = mapping courant des tiers rapide/standard/max** — sur une génération plus récente, lire par tier, pas par nom (paramètre `model` du tool Agent).

## Étape 0 — Scope + tier

Déterminer la cible et le tier. **Cible vide** (working tree propre sans `--base`/`--pr`/path, ou diff vide) → le dire en une ligne et stop — pas de revue à vide. Compter la taille du diff : **> 400 LOC modifiées → avertir** (au-delà, le taux de détection chute fortement — SmartBear/Cisco ; 87 % détection ≤100 LOC vs 28 % >1000 LOC, Propel) et **découper** en passes ≤ 300-400 LOC (par fichier/feature), agréger+dédupliquer ensuite. Logger `[scope] <cible>, <N> fichiers, <M> LOC, tier=<...>`.

## Étape 1 — Context assembly (NE PAS sauter — c'est le différenciateur)

Construire un **context pack** (placé en tête de chaque prompt reviewer = zone stable, cache-friendly) :

1. **Le changeset** : hunks modifiés ; pour un fichier neuf (untracked), son contenu entier. Jamais le repo entier.
2. **Ticket / spec** : auto-détecter l'id (nom de branche `feature/123-…`, `--ticket`, PR liée) → `gh issue view` / `glab issue view` → titre + corps + **critères d'acceptation**. C'est l'oracle de la dimension spec-alignment. Si introuvable, le dire et reviewer sans (en le signalant).
3. **Conventions projet** (court, < 50 lignes) : `CLAUDE.md` racine + des dossiers touchés, `.cursor/rules`, `CONTRIBUTING.md`, configs lint. Extraire un digest des règles **réellement applicables** (déléguer la lecture à un agent Haiku — ne pas charger > 200 lignes dans le contexte mère).
4. **Contexte cross-fichiers** (ce qui fait passer 44 %→82 %) : pour chaque symbole exporté modifié, trouver **call sites / callers / implémentations** (grep, ou LSP/gopls si dispo : `findReferences`, `goToImplementation`). Détecter les *breaking changes hors diff* (un appelant que le changement casse).
5. **Historique git** : `git blame`/`git log -p` ciblé sur les lignes/fichiers touchés → *pourquoi* ce code existe, changements récents liés, anti-régression.
6. **Stack / architecture / versions** : langage, framework, **archi dominante** (CQRS/ES, hexagonal, event-driven, microservices, monolithe modulaire…), deps majeures + versions (les patterns sécu/perf **et les idiomes** sont version- ET archi-dépendants). En cas d'archi/dep peu familière, une recherche web ciblée est permise (cf. principe « recherche externe »).
7. **Learnings repo** (mémoire de feedback) : lire `~/.claude/projects/<encoded-cwd>/memory/senior_review_learnings.md` s'il existe → FP déjà confirmés à ne pas répéter + conventions d'équipe découvertes. Logger `[context] N learnings repo chargés`.
8. **Lessons cross-projet (mémoire du skill)** : lire `~/.claude/skills/senior-review/lessons.md` (écrites à l'Étape 7 des runs passés) → leçons sur *comment reviewer* (discriminance des tests, routage par clé, hygiène de mutation…). Les injecter dans le context pack en **routant chaque leçon vers la dimension concernée** (une leçon "tests" nourrit le reviewer tests, une leçon "hygiène mutation" nourrit l'Étape 4). Logger `[context] M lessons cross-projet chargées`.

**Reconnaissance d'architecture → mode spécialiste.** À partir de la stack + archi détectées, **nommer la combinaison** (ex. « Shopify + CQRS/ES en Go »). Quand cette combinaison porte des invariants et pièges propres qui changent matériellement la revue :
- **Proposer/confirmer le mode** : si l'utilisateur n'a pas déjà donné l'angle, lui demander via `AskUserQuestion` (« je revois en expert senior <stack> ? ») — en non-interactif, assumer le mode détecté **en le signalant**.
- **Persona experte par reviewer** : chaque agent de dimension devient un **senior 10+ ans de cette stack précise** (pas un généraliste) et reçoit la **liste d'invariants/pièges connus** de l'archi à vérifier en priorité. Exemples : *CQRS/ES* → idempotence des commandes, immutabilité/rejouabilité des events, cohérence projection↔agrégat, sagas/effets de bord rétroactifs ; *Shopify* → pagination/éviction, normalisation E.164, scopes/permissions, throttling, champs version-dépendants de l'Admin API ; *front* → hydratation, a11y, états de chargement.

Logger `[context] ticket=<#id|absent>, N conventions, M call-sites tracés, stack=<...>, mode spécialiste=<stack | généraliste> (confirmé|détecté)`.

## Étape 2 — Gate objectif (signal externe avant tout jugement LLM)

Lancer les outils dispos sur le périmètre (paralléliser) — ils sont l'oracle externe et **désamorcent les FP** :
- **lint** (golangci-lint/eslint/ruff…), **typecheck**, **tests** du périmètre, **SAST** (gosec/semgrep/bandit).
Passer leurs sorties au context pack : les reviewers **ne re-flaguent pas** ce qu'un outil attrape (anti-bruit) et **s'appuient** dessus comme findings ancrés. Si un outil manque → `--no-tools`/skip gracieux, le noter (la robustesse de la revue baisse, le dire).

**Attribution baseline (échec préexistant ≠ introduit par le diff)** : un outil qui échoue n'incrimine le diff que si l'échec n'existe pas déjà sur la base. En cas d'échec (tests/lint/typecheck), vérifier l'attribution : pour `--base`/`--pr`, rejouer l'outil dans un worktree temporaire jetable sur le ref de base (`git worktree add` puis cleanup) ; pour le working tree, comparer vs HEAD quand c'est faisable à coût raisonnable, sinon marquer « attribution non vérifiée ». Un échec **préexistant** est exclu du verdict (scope = le diff) mais signalé en une ligne ; un échec **introduit** est un finding ancré. L'attribution entre dans le context pack — flaguer le diff sur un échec préexistant est exactement le faux positif qu'on combat.

**Routage des dimensions** (mixture-of-prompts, iCodeReviewer) : n'activer que les lentilles pertinentes au diff (pas de passe « injection SQL » sans accès DB, pas de passe a11y sans front). Logger `[gate] lint/typecheck/tests/SAST: <résumés>` + `[route] dimensions actives: <liste>`.

## Étape 3 — Revue décomposée en aveugle (agents ∥, reviewer ≠ auteur)

Un **agent distinct par dimension**, contexte vierge, recevant le context pack (stable) + sa rubrique (volatile). Décomposer plutôt qu'un « God reviewer » (chaque agent a un focus net, les FP d'une dimension ne contaminent pas les autres — Qodo, Intercom, Cursor). Dimensions standard (activer selon routage) :

- **spec-alignment** : le diff couvre-t-il TOUT le ticket (chemins, critères d'acceptation) ? gaps non implémentés ? scope creep (modifs hors ticket) ?
- **correctness / bugs** : logique, cas limites, concurrence/races, nil/maps, off-by-one, fuites de ressources, `defer` en boucle, error shadowing, aliasing de slices, gestion d'erreurs. (Language-aware.)
- **security** (mindset attaquant) : entrées contrôlées par l'attaquant → sinks (injection, XSS, SSRF, path traversal), authz/authn, secrets/PII en logs, crypto, trust boundaries, fail-open. Modèle de menace, pas check-list mécanique (gosec couvre le mécanique).
- **design / maintainability** : abstraction au bon niveau, sur-ingénierie/YAGNI, lisibilité (« compréhensible en 5 s »), nommage, commentaires (pourquoi non-évident, pas paraphrase), adhérence conventions projet.
- **tests** : couverture du *comportement modifié*, cas d'erreur (pas que le happy path), assertions utiles, et — candidat red-check — *les tests échouent-ils vraiment si le code casse ?*
- **perf** (cond.) : N+1, allocations, requêtes, complexité ; pas de micro-opt prématurée. **ux/a11y/i18n** (cond. front).

Chaque agent **raisonne avant de noter** et rend, par finding : `{ severity: blocking|important|nit|suggestion, file, line, confidence: high|med|low, reasoning, finding, fix_concret, verification_plan }`. On lui donne explicitement la section **« ce qu'on NE flague PAS »** (voir plus bas). Prompt « senior 10+ ans **— en mode spécialiste, expert de la stack détectée (Étape 1) : adopte cette persona et vérifie en priorité les invariants/pièges de l'archi** —, terse, evidence-based ; ne récompense pas la longueur ; en cas d'hésitation, baisse la confiance ; en cas de doute version/API, une recherche web ciblée est permise (cite la source, re-vérifie contre le repo) ».

Logger `[review:<dim>] N findings (x bloquants, y importants)`.

*Exécution* : un appel `Agent` par dimension, lancés en parallèle dans un même message. Si le tool `Workflow` est disponible, le fan-out PEUT passer par un script Workflow (un `agent()` par dimension avec `schema` JSON imposé sur le format finding) — sorties validées structurellement, retries de parsing éliminés. L'interactif (AskUserQuestion) reste en conversation principale, jamais dans un workflow.

## Étape 4 — Gate de vérification ("receipts")

**Aucun finding critical/major n'est remonté sans preuve.** Pour chacun, exécuter le `verification_plan` :
- **grep/ast-grep** : confirmer que le pattern existe vraiment et sur une ligne modifiée.
- **exécution sandbox** : reproduire (snippet, requête, test qui échoue sur le code actuel — fail-to-pass, TDD-Bench). Pour un bug allégué → écrire le test rouge ; s'il ne rougit pas, le finding est suspect → drop ou rétrograder.
- **sécurité** : confirmer que la source est réellement attaquant-contrôlée ET atteint le sink (traçage flux). Sinon → drop.
- **« tests faibles »** → **red-check mutation** : muter la ligne ciblée (inverser une condition / constante, type-préservant), relancer la suite. Si rien ne rougit → le test est vacant → finding réel. Si le test ciblé rougit (et lui seul) → les tests protègent → finding FAUX, drop. Restaurer exactement.

**Hygiène du re-run live (V1.0.1)** : si vérifier un finding exige de muter temporairement un fichier suivi (ex: pointer un `config.js`/`.env` vers un serveur de test), restaurer via `git checkout -- <file>` et **ne laisser AUCUN backup parasite** (`.bak`/`.orig`/`config.js.orig_backup`…). git suit déjà le fichier — pas besoin de copie manuelle ; un backup oublié pollue le working tree de l'user et le diff. Vérifier `git status` propre en fin de revue. **Piège du workflow hybride (V1.1.1)** : si le fichier muté porte AUSSI des éditions non commitées (cas fix-puis-review sur le même fichier), `git checkout -- <file>` les efface TOUTES, pas seulement la mutation — restaurer chirurgicalement (Edit inverse sur les seules lignes mutées, ou `git stash` avant de muter), jamais par checkout global.

**Recherche web en appui (pas en substitut)** : pour un doute version/API/framework, consulter la doc officielle peut *confirmer ou réfuter* l'hypothèse (ex. « cette API plafonne-t-elle sans `first:` ? »). Mais le **receipt reste local** (grep/exec/test contre la version réelle du repo) ; la source web est citée (lien + date) et ne suffit jamais seule à remonter un finding bloquant.

Findings non prouvés → **drop silencieux** (ou rétrogradés en `low confidence — à vérifier`). Logger `[verify] k/n findings confirmés, j droppés (faux positifs)`.

## Étape 5 — Synthèse calibrée (dédup + panel adversarial ciblé)

1. **Dédup** cross-dimensions (même `file:line` / même cause).
2. **Refute-panel — seulement sur le douteux/critique** (proportionné : pas sur les nits) : pour chaque finding **bloquant** ou à **confiance non-haute**, un **skeptique indépendant** (modèle/famille ≠ si possible ; sinon prompt reformulé + ordre inversé pour casser le biais de position) est mandaté pour **RÉFUTER**. On garde le finding si la majorité ne le réfute pas (panel de juges variés > juge unique — PoLL, Verga 2024 ; le vote majoritaire tue les flukes d'une seule passe — Cursor BugBot). Escalade graduée : 1 refuteur → si désaccord, panel de 3 (médiane/majorité) → si toujours partagé sur un bloquant, **présenter à l'user** (ne jamais trancher seul un bloquant incertain).
3. **Calibration** : confiance finale par finding ; sous le seuil → `low confidence`. **Tiers de sévérité** : 🔴 bloquant (vrai merge-blocker) / 🟡 important / 🔵 nit·suggestion / 👍 praise (1-2 max). Mapping déterministe quand possible (MUST→bloquant, SHOULD→important, MAY→suggestion). **Cap nits ≤ 5 inline**, le reste en compte résumé.

Logger `[panel] x findings réfutés, y confirmés` · `[calib] 🔴N 🟡N 🔵N`.

## Étape 6 — Verdict + rapport (discipline signal/bruit)

Rapport structuré, concis, **commente le code jamais l'auteur**, chaque finding avec `file:line` + raison + fix concret + confiance (+ preuve de vérif si critique) :

```markdown
# Revue — <cible> (<N fichiers, M LOC>)

## Spec-coverage
<Le diff fait-il ce que le ticket #<id> demande ? — Oui / Partiel (gaps listés) / Hors-sujet>
<Scope creep éventuel : modifs hors ticket>

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
Métriques: lint <…> · typecheck <…> · tests <…/…> · SAST <…>
```

Si rien de matériel : **le dire** (« Aucun bloquant. N suggestions mineures. Le changement améliore la base. ») — le silence est une feature (GitHub Copilot : 29 % des revues silencieuses, assumé). Le seuil de greenlight (Google) : le changement **améliore** la base, pas « est parfait ».

**Execution-grounding live (option, surtout `--deep` ou findings runtime)** : si l'app est runnable et qu'un bug bloquant est suspecté, exercer réellement le chemin pour confirmer qu'il reproduit (relancer un serveur stale, aligner le schéma DB runtime — cf. discipline smoke-live). Sinon, review-only.

**`--comment`** : après confirmation, poster via `gh pr comment`/`gh pr review` (GitHub) ou `glab mr note` (GitLab), inline avec liens `file#Lx-Ly` (SHA complet pour GitHub). **`--fix`** : appliquer SEULEMENT les fixes high-confidence, dans le working tree, après confirmation — jamais de commit/push auto.

## Étape 7 — Learnings (mémoire par repo + lessons cross-projet)

- **Faux positif confirmé** par l'user (« ça c'est voulu ») ou par la vérif → l'écrire dans `~/.claude/projects/<encoded-cwd>/memory/senior_review_learnings.md` (`codebase_fact` vs `team_preference`) pour ne pas le répéter. Ne pas polluer avec des learnings trop génériques/vieux.
- **Leçon sur *comment reviewer*** réutilisable ailleurs → `~/.claude/skills/senior-review/lessons.md` (additive ; format : `- **<titre>** : <règle actionnable> — *vu sur N runs (<slugs>)*`). Ces leçons sont rechargées à l'Étape 1.8 de chaque run — c'est ce qui ferme la boucle d'apprentissage. Logger `[learn] N learnings repo, M lessons cross-projet`.

## Rubrique des dimensions (ancres — ce qu'un senior regarde, par priorité)

Bloquant-potentiel d'abord :
1. **Spec coverage** — couvre tout le ticket ? (pas seulement correct)
2. **Design** — interactions cohérentes, abstraction au bon endroit, pas d'over-engineering (« résous le problème d'aujourd'hui, pas celui spéculé pour demain » — Google)
3. **Correctness** — logique, cas limites, concurrence/races
4. **Security** — entrées validées, authz, secrets/PII, injection, fail-closed
5. **Tests** — présents, rougissent si le code casse, cas d'erreur
6. **Error handling** — wrap `%w`, pas de panic sur erreur normale
Non-bloquant (nit/suggestion) :
7. **Perf** — N+1, allocations (sans micro-opt prématurée) · 8. **Complexity** · 9. **Naming** · 10. **Comments** (pourquoi non-évident) · 11. **Docs** (si comportement public change)

## Ce qu'on NE flague PAS (aussi important que ce qu'on cherche)
- Ce que lint/format/typecheck/CI attrape déjà (indentation, imports, style mécanique).
- Le code **non modifié** (pre-existing), même mauvais — ce n'est pas ce changement.
- Fichiers générés, lock files, `vendor/`, assets minifiés.
- Defense-in-depth quand la défense primaire est adéquate.
- Code de test qui viole intentionnellement des règles de prod.
- Nitpicks qu'un senior ne soulèverait pas ; verbosité ; bikeshedding.
- Findings sans `file:line` ou non vérifiables → jamais remontés.

## Tools requis (charger via ToolSearch au besoin)
- `Agent` (`model: haiku|sonnet|opus|fable…` selon la génération courante) — **socle** : un appel distinct par dimension/refuteur, contexte vierge ; la mère ne joue jamais un rôle de reviewer qu'elle orchestre.
- `Workflow` (optionnel, si disponible) — fan-out des reviewers de dimension / refute-panel avec sorties schema-validées ; l'interactif reste en conversation principale.
- `Bash` — git (diff/blame/log/status incl. untracked), lint/typecheck/tests/SAST, grep/ast-grep, exécution sandbox de vérif, `run_in_background` pour smoke-live. `gh`/`glab` pour PR/MR/issue.
- LSP/`gopls` si dispo (findReferences/goToImplementation) pour le cross-file.
- `mcp__playwright__browser_*` si front (vérif visuelle / reproduction UI).
- `WebSearch`/`WebFetch` — en cas de doute version/API/framework : doc officielle, CVE, sémantique d'un flag. En appui seulement (cf. Étape 4), jamais comme receipt.

## Ce que le skill NE fait PAS
<!-- LOCKED -->
- Ne construit pas de feature (c'est `feature-loop`). Ne fait pas de revue de pur style (CI/linter).
- Ne commit/push/merge jamais ; ne poste/édite rien sans `--comment`/`--fix` + confirmation.
- N'invente pas de finding : pas de `file:line` valide + vérifié → pas de finding.
- Ne note pas le code legacy non modifié ; ne re-flague pas ce qu'un outil attrape.
- Ne tranche pas seul un bloquant incertain → escalade user.
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
- **Review-only par défaut** ; actions sortantes sur flag + confirmation.
- **Mémoire de learnings par repo** — ne répète pas les FP, s'adapte aux conventions.

## Sources (traçabilité)
Détail complet (académique + outils + pratiques, avec ce que chaque source fonde) : `reference/references.md`.

## CHANGELOG
Historique complet : `CHANGELOG.md` (à côté de ce fichier). Version courante : **1.2.0**.
