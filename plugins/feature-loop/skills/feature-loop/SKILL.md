---
name: feature-loop
description: >
  Use when the user wants a non-trivial feature implemented with autonomous, iterative, quality-gated delivery — best when quality matters more than raw speed. A mother agent sizes the difficulty tier and delegates to SEPARATE subagents (code writer ≠ test-writer ≠ blind reviewer; tests written from the spec). Objective gate (build/lint/typecheck/tests + test-must-go-red mutation check) BEFORE any LLM review; runnable features get a mandatory LIVE smoke test before any "tested" SUCCESS. Loops until all quality axes ≥ 8/10 with zero criticals (max 3 iters), keeps the BEST version, emits a markdown report. Subcommands: status (runs dashboard), learn (propose-only self-improvement). Flags: --fast, --paranoid, --worktree, --max-iter=N, --threshold=N, --judge, --issue=N (GitLab/GitHub issue as spec). NOT for quick edits (do them directly) nor review-only (use senior-review).
argument-hint: "[description | status | learn] [--issue=N] [--fast|--paranoid|--no-paranoid] [--worktree] [--max-iter=N] [--threshold=N] [--judge=sonnet|opus] [--no-redcheck]"
---

# Feature Loop

**skill_version : 8.15.1** (historique : `CHANGELOG.md`). Implémentation itérative auto-notée d'une feature jusqu'à convergence sur un radar de qualité.

**Fichiers du skill (progressive disclosure)** : `scoring-rubric.md` (chargé par le reviewer), `lessons.md` (chargé par la mère à l'init), `reference/subcommands.md` (lu au dispatch `status`/`learn`), `reference/report-template.md` (lu au §5.4), `reference/git-recipes.md` (recettes shell snapshot/restore/conflicts, lues aux §4.2/5.0/5.1bis), `reference/log-example.md` (trace de run illustrative), `reference/limitations.md` (lu si contexte concerné), `reference/references.md` (sources académiques, à la demande), `reference/stack-*.md` (packs spécialistes — symfony, golang, htmx, javascript, cqrs-es — chargés à l'Étape 2bis selon la stack détectée, combinables).

**Architecture** (patterns officiels Anthropic, *Building Effective Agents*) :
- **Orchestrator-workers** : une **mère** (Opus, haute réflexion) estime, décompose, délègue à des sous-agents spécialisés, puis synthétise. Elle reste le cerveau ; les workers sont les bras.
- **Evaluator-optimizer** : boucle générer → évaluer → raffiner, avec un évaluateur **distinct** du générateur. Valide quand les critères sont clairs et mesurables (notre radar).
- **Séparation stricte des rôles** : écrivain-code ≠ écrivain-tests ≠ relecteur. Le *self-preference bias* est prouvé (un modèle qui se juge se surnote). La mère orchestre, ne s'auto-juge jamais.
- **Effort proportionné à la difficulté** : multi-agents ≈ 15× les tokens d'un chat (Anthropic). On dimensionne modèle + profondeur à l'enjeu → rapide sur le facile, lourd sur le critique.

Sources détaillées (patterns Anthropic, LLM-as-judge, raffinement itératif, tests LLM) : `reference/references.md`.

```
PRE-FLIGHT (baseline projet : git clean, deps, build pass)
  ↓
INIT (clarifier + détecter scope/keywords-sensibles + extraire conventions + lint plugins
      + ESTIMER LA DIFFICULTÉ → tier + modèles (Étape 2bis)
      + charger insights projet + lessons cross-projet + branche in-place [ou worktree si --worktree])
  ↓
LOOP × max 3 (default, --max-iter ; --fast = chemin court si tier TRIVIAL) :
  PLAN (Sonnet) → MINI-REVIEW PLAN (Haiku)
        ↓
  IMPLEMENT CODE  (agent A — Sonnet/Opus selon tier)        ⟍ agents
  ÉCRIRE TESTS depuis la SPEC (agent B ≠ A, dès STANDARD)    ⟍ DISTINCTS
        ↓
  GATE OBJECTIF : build/lint/typecheck/tests + RED-CHECK (test critique doit pouvoir rougir)
       (lint plugins spécialisés + retry flaky 1×) — PAS de juge LLM si le gate casse
        ↓
  REVIEW BLIND (agent C ≠ A,B — Sonnet défaut / Opus si complexe-sensible)
       + écrit un test adversarial par finding   [+ DEVIL'S ADVOCATE si paranoid/auto]
        ↓
  ESCALADE SUR DOUTE (score borderline / désaccord juges / confiance basse / scope sensible
       → 2e juge, puis panel de 3, puis arbitre Opus)
        ↓
  VALIDATION DES PREUVES (anti-hallucination, file:line vérifiés)
        ↓
  DÉTECTION RÉGRESSION / PERSISTANCE / STAGNATION  → garder la MEILLEURE version (pas la dernière)
        ↓
  Convergence ?  → SUCCESS    Régression ? → ROLLBACK + contrainte
        ↓
       next iter (force notes_acknowledged)
  ↓
SMOKE TEST FINAL (offline build/tests) → SMOKE TEST LIVE (run réel + exercer le chemin) → CONFLICTS CHECK vs main → RAPPORT MARKDOWN → insights + lessons + runs-log + skill_version → user décide
```

## Principes non négociables

<!-- LOCKED: jamais d'édition auto par `learn` (propose-only, voir Étape 7). Modif humaine uniquement. -->

Fondements académiques de ces règles : `reference/references.md`.

- **Travail à deux, pas tête baissée** : ambiguïté → demander avant de coder. Stopper la boucle pour toute décision produit ou trade-off non technique.
- **Honnêteté > faux confort** : une solution simple aux limites documentées bat une solution complexe qui se prétend parfaite. Sur-ingénierie constatée à l'usage → reculer proprement (rollback simplificateur, 4.8), pas persister.
- **Solution minimale viable avant infrastructure** : JAMAIS de parser custom / framework / abstraction avant d'avoir essayé la solution simple. Si elle ne suffit pas, justifier par les cas concrets qu'elle rate.
- **Logs temps réel** : 1 ligne par sous-étape clé. Pas de silence > 3 min.
- **Review en aveugle** : le reviewer ne voit JAMAIS le prompt d'implémentation.
- **Séparation des rôles writer ≠ tester ≠ reviewer (non négociable)** : l'auteur du code ne l'évalue ni ne le teste JAMAIS (self-preference bias prouvé, refs). Donc (a) review = sous-agent au contexte vierge ; (b) tests = sous-agent dédié ≠ auteur **dès STANDARD**, écrits depuis la SPEC (pas en lisant l'impl) ; (c) sur TRIVIAL/express la mère peut coder ET tester, mais la **review reste déléguée** (auto-review interdite, toujours).
- **Pas de validation sans signal externe** : l'auto-correction LLM sans oracle externe dégrade (refs). Aucune itération SUCCESS sur la seule auto-critique : il faut le gate objectif vert (build/lint/tests) ET un juge séparé.
- **Le run réel est le signal ultime** : pour toute app *runnable*, gate offline + intg sur DB de test = nécessaires mais PAS suffisants (ils ne voient pas un serveur resté sur l'ancien binaire, une migration non rejouée sur la DB runtime, une erreur de câblage, une intégration que les mocks simulaient). Exécuter l'app réelle et exercer le chemin de bout en bout (smoke LIVE, §5.1b) avant tout SUCCESS « testé ». Live bloqué (auth/creds) → maximum faisable + dire explicitement ce qui reste à confirmer ; jamais « testé » sur la seule foi des mocks.
- **Tout test critique doit pouvoir rougir (red-check)** : 76 % des tests LLM ratent le fail-to-pass (refs). Avant de faire confiance à un test critique : muter sa ligne cible, vérifier qu'il ÉCHOUE, restaurer. Resté vert = vacant → réécrire. Périmètre : tests critiques seulement (§4.5b).
- **Effort proportionné à la difficulté** : multi-agents ≈ 15× les tokens d'un chat. Panel, devil's advocate, review Opus, itérations multiples seulement si l'enjeu le justifie. Trivial → mode express (2bis).
- **Doute → escalade (panel avant gros modèle)** : jugement incertain (score borderline près du seuil, désaccord juges ≥ 2 pts, confiance basse, scope sensible, preuves invalides) jamais accepté tel quel → 2ᵉ juge → panel mixte de 3 → arbitre Opus (§4.6c).
- **Garder la meilleure version, pas la dernière** : les gains plafonnent après 2-3 itérations et une itération peut régresser → snapshot du meilleur radar (`best_iter_sha`), restauré si la dernière est moins bonne.
- **Preuves obligatoires et vérifiées** : tout score < 10 cite `file:line` ; le skill VÉRIFIE que ces refs existent.
- **Build/lint/typecheck/tests doivent passer** : sinon score robustesse = 0.
- **Isolation par branche** : in-place sur branche dédiée par défaut (courante si feature branch, sinon `feature-loop/<slug>` créée depuis la courante si protégée — develop/main/master). Worktree UNIQUEMENT sur `--worktree`. `run_base_sha` + snapshots → rollback sûr. L'in-place rend les edits visibles live dans l'éditeur de l'user.
- **Pas de commit/push/merge automatique** sur la branche principale, ni sur la branche user en in-place au-delà des snapshots de mécanisme.
- **Prompt caching** : parties stables (rubrique, conventions, insights) en tête des prompts ; partie variable (diff, findings) en fin.
- **Discipline tokens/latence** — à qualité égale, le run le moins cher gagne : (a) le reviewer TIRE ses inputs (COMMANDES exactes `git diff <pre_impl_sha>..HEAD -- <scope>` + liste fermée de fichiers), la mère ne colle pas le contenu ; jamais les deux ; re-lecture limitée au scope ; (b) itération corrective → continuer le même juge (SendMessage), pas d'agent frais (§4.6) ; (c) Playwright sobre — snapshots ciblés, `curl` pour le non-visuel ; clic réel OBLIGATOIRE pour les contrôles UI nouveaux (§5.1b) ; (d) sorties shell tronquées (`tail`/`--filter` ; suite complète aux seuls gates) ; (e) validation de preuves = grep par la mère, jamais un agent ; (f) paralléliser l'indépendant (A∥B, tools groupés, panel parallèle).
- **Axes standards + extension** : les axes de base (lisibilité, robustesse, modularité, simplicité, YAGNI, tests + scope-specifics) sont obligatoires. +1-3 axes domain-specific possibles, jamais en substitution. Renommer/supprimer un axe standard = interdit.
- **Skip Sonnet refusé si paranoid actif** : mode paranoid actif → délégation de l'impl à Sonnet non négociable. Sécurité > overhead.
- **Mode spécialiste selon l'archi (auto, annoncé)** : l'Étape 2bis nomme la combinaison stack+archi et confère à l'impl, au test-writer ET au reviewer une persona d'expert senior + les invariants/pièges d'archi à respecter/vérifier. Écrire idiomatique = moins de bugs à la source (d'où l'application à l'impl, pas au seul reviewer). Auto-détecté, jamais une question de plus.
- **Recherche externe permise en cas de doute** : un agent qui doute d'une API/version/framework PEUT consulter le web (doc officielle d'abord) plutôt qu'halluciner une signature — mais l'oracle reste le gate objectif + red-check + smoke live, jamais la réponse web. En cas de doute seulement, pas par défaut.
- **Pas de "mergeable proprement" sans commit** : §5.2 refuse de logger `mergeable` si 0 commit applicatif ; le rapport force un commit final (5.1bis) avant le conflicts check.

## Parsing des arguments

**Sous-commandes** (premier token, pas de boucle d'implémentation) :
- `status` — affiche le tableau de bord des runs passés sur ce repo (lit le runs-log persistant). Voir Étape 6.
- `learn` — analyse les runs passés + complète `lessons.md`, et propose (sans appliquer en silence) des évolutions du SKILL.md. Voir Étape 7.

**Mode feature** (défaut) :
- `<description>` — description libre de la feature
- `--worktree` — force l'isolation worktree git au lieu de l'in-place. Cas d'usage : faire tourner deux runs en parallèle sur le même repo sans collision de branche. Sinon, défaut = in-place sur branche dédiée (voir Étape 3).
- `--paranoid` — force le 2e reviewer Opus en devil's advocate (sinon auto-activé sur keywords sensibles)
- `--no-paranoid` — désactive le devil's advocate même si keywords sensibles détectés
- `--max-iter=N` — override la limite par défaut (**3**). Augmenter au-delà de 5 nécessite justification : les iter 4-5 apportent peu en pratique (observé sur runs réels : converge en 2-3, ou MAX_ITERATIONS valide avec limites documentées).
- `--threshold=N` — override le seuil de SUCCESS par axe (8)
- `--fast` — force l'évaluation en **mode express** (Étape 2bis) et supprime les confirmations d'avant-boucle. Le mode express s'active DÉJÀ tout seul sur une tâche TRIVIALE sans keyword sensible (cf. 2bis) ; `--fast` ne fait que sauter la confirmation et l'imposer si l'estimation hésite. Refusé dès qu'un keyword sensible apparaît.
- `--judge=sonnet|opus` — override le modèle du reviewer par défaut (défaut : Sonnet, escalade auto sur doute). `--judge=opus` force Opus à chaque review (plus lent/cher, qualité de jugement max).
- `--no-redcheck` — désactive le red-check (4.5b) sur les tests critiques. Déconseillé : c'est le garde-fou anti tests vacants. Utile seulement sur un projet où la mutation est impraticable (build trop lent, pas d'exécution ciblée possible).
- `--issue=N` — charge l'issue GitLab/GitHub #N comme SPEC (`glab issue view N`, ou `gh issue view N` si le remote est GitHub : titre + description deviennent la description de la feature). Si une branche liée `N-*` existe (créée par `glab mr create --related-issue`, ex. via le skill projet `issue-mr`), elle devient la branche de travail (Étape 3). Voir Étape 1 pour le pont issue-mr quand la spec est vague.

## Logs utilisateur (principe)

Préfixes : `[preflight]`, `[scan]`, `[init]`, `[tier]`, `[iter N/max]`, `[plan]`, `[impl]`, `[tests]`, `[gate]`, `[redcheck]`, `[review]`, `[devil]`, `[escalade]`, `[evidence]`, `[converge]`, `[best]`, `[smoke]`, `[smoke-live]`, `[commit]`, `[conflicts]`, `[report]`, `[insights]`, `[lessons]`, `[runs]`, `[done]`. Sous-commandes : `[status]`, `[learn]`. Pas d'emojis. Style factuel.

Exemple complet d'une trace de run de bout en bout : `reference/log-example.md`.

## Étape 0 — Pre-flight check (baseline projet)

**Avant tout** vérifier que le projet est dans un état exploitable. Si non, le skill ne peut pas mesurer ses propres changements.

Log : `[preflight] vérification baseline...`

Checks dans le repo principal (avant tout choix de branche / worktree) :
1. **Git clean** : `git status --porcelain`. Si modifs non commitées → `AskUserQuestion` : "Le repo a des modifications non commitées. Options : 1) commit avant de continuer / 2) stash temporaire (récupéré à la fin) / 3) annuler".
2. **Deps installées** : présence de `node_modules/` (Node), `vendor/` (PHP), équivalent selon stack. Si pas installé → proposer `npm install` (ou équivalent) puis continuer.
3. **Baseline build pass** : lancer build + lint + typecheck + tests sur HEAD actuel — **la MÊME suite que le gate 4.5 exécutera** (tags d'intégration inclus, ex. `go test -tags intg`, si le gate les lancera). Une baseline partielle fait découvrir les échecs préexistants en pleine boucle → diagnostic stash coûteux (et un `git stash` sans `-u` laisse les fichiers untracked qui cassent la compile — toujours `-u`). Si ÉCHEC → `AskUserQuestion` : "Le projet ne passe pas son propre build/lint/tests sur HEAD. Options : 1) corriger d'abord (skill ne peut pas comparer un avant/après sur base cassée) / 2) continuer quand même — si l'échec est PRÉEXISTANT et hors de la zone touchée, le documenter et l'exclure du verdict de gate / 3) annuler".

**Check piège vendor/node_modules symlink** : UNIQUEMENT en mode `--worktree`. APRÈS création du worktree (étape 3), vérifier :
```bash
for dep in vendor node_modules; do
  if [ -L "$WORKTREE/$dep" ]; then
    REAL=$(realpath "$WORKTREE/$dep")
    MAIN=$(realpath "$REPO_MAIN/$dep")
    [ "$REAL" = "$MAIN" ] && echo "WARN: $WORKTREE/$dep symlinked to main → autoloader/require résoudra vers /main/src, runtime test des modifs entités IMPOSSIBLE"
  fi
done
```
Si symlink détecté → logger `[preflight] WARN: <dep> symlinked to main — limitation runtime test (voir Limitations connues)`. Ne pas BLOQUER (juste avertir l'agent + reviewer pour qu'ils en tiennent compte).

**En mode in-place (défaut)** : ce piège n'existe pas — le repo principal utilise son vrai `vendor/`/`node_modules`, les tests runtime des modifs sont fiables. C'est un avantage concret de l'in-place sur les monorepos `go.work` + vendor.

**Détecter règle CLAUDE.md user "no auto-commit"** : lire `~/.claude/CLAUDE.md` (global user) ET `<repo>/CLAUDE.md` (projet) si présents. Chercher des patterns comme :
- `INTERDIT git add` / `interdit git commit`
- `sans permission explicite`
- `l'utilisateur valide` / `l'user décide`
- `ne commit pas` / `pas d'auto-commit`

Si détecté → flag `no_auto_commit: true` dans le journal. Conséquence : l'étape 5.1bis ne **force pas** le commit, elle **propose** le message à exécuter manuellement. Voir 5.1bis pour le détail. Logger `[preflight] règle user "no auto-commit" détectée → mode proposition manuelle pour le commit final`.

Loguer le résultat de chaque check. Si tout ok : `[preflight] baseline OK`.

## Étape 1 — Clarifier la feature + détection sensibilité

Récupérer la description (args du skill ou demander).

**Spec depuis une issue (`--issue=N`)** : `glab issue view N` (GitLab) ou `gh issue view N` (GitHub, selon le remote) → le titre + la description de l'issue DEVIENNENT la description de la feature (une issue au format analyse — constat/pourquoi/périmètre/plan — passe le test de clarté d'office). Logger `[init] spec chargée depuis issue #N (<titre>)`. Échec glab/gh (issue inexistante, pas de remote) → le dire et retomber sur la description libre.

Test de clarté — la description doit répondre à :
1. **Quoi** : ce qui doit exister à la fin
2. **Qui** : utilisateur cible
3. **Pourquoi / contraintes** : exigences non triviales
4. **Périmètre** : ce qui est EXCLU

Si une réponse manque → `AskUserQuestion`.

**Pont issue-mr (spec vague)** : si le test de clarté échoue sur ≥ 2 points ET qu'un skill `issue-mr` est disponible (global depuis sa v2.0.0 — mode ANALYSE) → proposer via `AskUserQuestion` de l'invoquer MAINTENANT, avant la boucle : l'analyse explore le code, tranche la conception avec l'user et produit une issue structurée qui devient la SPEC ; la branche `<issue>-<slug>` créée devient la branche de travail (Étape 3). Bénéfice : le plan 4.3 converge plus vite et l'agent B (tests-depuis-la-spec) teste un vrai contrat. Contraintes : invocation par la mère en conversation principale UNIQUEMENT (un sous-agent ne peut pas invoquer de skill), et UNIQUEMENT ici — jamais au milieu de la boucle (l'interactivité d'issue-mr casserait l'autonomie). Refus user → clarifier par `AskUserQuestion` classiques.

**Détection de keywords sensibles** : la description et le scope contiennent-ils un de :
`auth`, `password`, `payment`, `payer`, `paiement`, `stripe`, `token`, `permission`, `role`, `crypto`, `hash`, `secret`, `pii`, `gdpr`, `rgpd`, `migration`, `sql`, `admin`, `audit`, `acl`, `oauth`, `jwt`, `session`, `csrf`, `xss` ?

Si oui ET pas de `--no-paranoid` → activer automatiquement le devil's advocate (`paranoid: true` dans le journal). Logger `[scan] keywords sensibles détectés (<liste>) → --paranoid auto-activé`.

**Calibrage `migration`/`sql`** : ces deux keywords sur-déclenchent — une migration purement additive (`ADD COLUMN ... DEFAULT`, index) est à bas risque et ne justifie pas SENSIBLE (review Opus + DA + panel ≈ 3-4× le coût). Si `migration`/`sql` sont les SEULS keywords détectés → ne pas forcer : qualifier le risque réel (additive vs ALTER destructif / UPDATE-DELETE de données / changement de type) et proposer le choix paranoid on/off via l'AskUserQuestion de l'Étape 2, avec cette qualification et une recommandation. Les autres keywords (auth, payment, secret, pii…) continuent de forcer l'auto-activation.

## Étape 2 — Auto-détection scope + axes + conventions + lint plugins

Log : `[scan] détection stack en cours...`

Scanner en parallèle :
- Stack : `package.json`, `Cargo.toml`, `pyproject.toml`, `go.mod`, etc.
- Front / Back / Tests / E2E / Conventions (voir liste détaillée plus bas)

**Framework de tests** : détection sur `vitest.config*`, `jest.config*`, `pytest.ini`, `playwright.config*`, etc.

Si **AUCUN framework de tests détecté avec confiance** → `AskUserQuestion` :
"Aucun framework de tests détecté. Options : 1) initialiser Vitest (ou équivalent cohérent avec la stack) / 2) framework personnalisé (à préciser) / 3) désactiver l'axe tests pour ce run".

Ne JAMAIS installer un framework non confirmé par l'user — éviter le mismatch (Vitest installé sur projet Jest, etc.).

**Lint plugins disponibles** : parser `package.json` (`devDependencies` + `dependencies`) à la recherche de :
- `eslint-plugin-jsx-a11y` → a11y métriques
- `eslint-plugin-security` → security métriques
- `eslint-plugin-react-hooks` → robustesse hooks
- `eslint-plugin-import` → cycles / imports
- `@typescript-eslint/eslint-plugin` → règles TS strictes
- équivalents Python (`bandit`, `pylint-security`) ou Go (`gosec`)

Lister ceux dispos. Ils seront lancés à l'étape 4.5 et nourriront la review. **Pas d'install automatique** — si manquant, l'axe correspondant reste 100% qualitatif.

Log : `[init] N conventions extraites, M lint plugins dispos (<liste>)`.

Déduire :
- **Scope** : backend / frontend / fullstack
- **Axes activés** : voir `scoring-rubric.md` pour les barèmes à ancres concrètes.
  - **Standards (toujours présents)** : lisibilité, robustesse, modularité, simplicité, YAGNI, tests.
  - **Packs conditionnels (activer seulement les pertinents)** :
    - *Front* : UX/UI, contraste, aéré, responsive, doc-utilisateur, a11y (sur screenshots multi-viewport).
    - *Sécurité/OWASP* : si keywords sensibles OU sortie consommée par un tiers (rubrique = checklist OWASP).
    - *Performance*, *observabilité* : selon scope.
    - **Pack user-facing** (repris d'outil-factory, si la feature produit une UI/contenu vu par un utilisateur final, typiquement un produit public) : i18n (si multilingue), copywriting (si texte user), SEO (si page publique), CTA/conversion (si page à objectif de conversion — rare en interne). Une route API n'active AUCUN de ces axes.
- **Axes domain-specific** (optionnel) : l'agent peut proposer 1-3 axes complémentaires si la feature a une dimension propre (ex: "résilience anti-bot/WAF" pour scraping, "Compat couche pure" pour refacto avec API publique stable). **Chaque axe additionnel doit avoir une rubrique 0-10 explicite définie AVANT l'impl** et stockée dans `.feature-loop.json` au champ `axes_custom`. **Substitution interdite** : jamais retirer/renommer un axe standard. L'axe "valeur vs concurrence" (outil-factory) n'est disponible que sur demande explicite (produit public comparable), jamais d'office.
- **Conventions** : extraire 3-5 patterns concrets du codebase (composant, test, error handling, validation, styling)

Présenter via `AskUserQuestion` :
```
Scope détecté : <fullstack>
Stack : <...>
Axes activés (N) : <liste>
Conventions extraites : <paths>
Lint plugins dispos : <liste>
Mode paranoid : <on/off> (auto si keywords sensibles)
→ Confirmer / Ajuster ?
```

**Mode express (2bis)** : sauter cette confirmation — logger le récap (scope/stack/tier) et continuer directement. L'user interrompt s'il veut ajuster.

## Étape 2bis — Estimation de difficulté + dimensionnement des modèles

But : **proportionner l'effort à l'enjeu** (multi-agents ≈ 15× les tokens d'un chat — Anthropic). La mère estime AVANT d'agir, puis fixe le tier, les modèles et la profondeur. Règle : estimer → dimensionner → déléguer → vérifier → réajuster.

### Estimer sur 4 dimensions (basse/moyenne/haute)
1. **Complexité de raisonnement** : logique subtile, algo, archi vs CRUD/copie mécanique.
2. **Volume / contexte** : nombre de fichiers, lignes, surfaces touchées.
3. **Risque si erreur** : sécurité, données, paiement, migration, prod-facing vs cosmétique réversible.
4. **Parallélisable** : sous-tâches indépendantes (→ fan-out workers) vs séquentiel.

### Tier résultant (inscrit au journal : `difficulty_tier`)
| Tier | Signature | Profondeur boucle |
|---|---|---|
| **TRIVIAL** | mécanique, < 50 LOC, ≤ 2 fichiers, risque nul, 0 keyword sensible | **mode express d'office** (cf. ci-dessous) |
| **STANDARD** | feature normale, logique modérée, risque limité | boucle 1–2 itérations, 1 reviewer Sonnet |
| **COMPLEXE** | raisonnement lourd OU large surface OU archi transverse | boucle complète, reviewer Opus, escalade possible |
| **SENSIBLE** | keyword sensible (auth/paiement/crypto/migration/données…) OU risque élevé | boucle complète + devil's advocate + panel d'office ; jamais de chemin court |

`paranoid` (Étape 1) force SENSIBLE. Présenter le tier à l'user en Étape 2.

### Dimensionnement des modèles (rôle × tier)
La **mère** tourne toujours sur le meilleur modèle disponible (= le modèle de la session — Opus, Fable…, haute réflexion) — orchestration, arbitrages, synthèse, décision finale. Elle délègue les bras :

| Rôle (sous-agent) | TRIVIAL | STANDARD | COMPLEXE | SENSIBLE |
|---|---|---|---|---|
| Plan | (mère) | Sonnet | Sonnet | Sonnet |
| Mini-review plan | — | Haiku | Haiku | Haiku |
| **Impl code** (agent A) | mère\* | Sonnet | Sonnet/Opus | Sonnet/Opus |
| **Tests** (agent B ≠ A) | mère\* | Sonnet | Sonnet | Sonnet |
| **Review** (agent C ≠ A,B) | Sonnet\*\* | Sonnet | Opus | Opus |
| Devil's advocate / panel | — | si doute | si doute | **d'office** |

\* TRIVIAL : la mère peut coder ET écrire les tests, MAIS la review est obligatoirement déléguée (agent ≠ mère). Dès STANDARD, l'agent tests (B) est distinct de l'agent code (A).
\*\* même TRIVIAL passe par un reviewer distinct : on n'économise jamais la *séparation des rôles*, on économise sur le MODÈLE et la PROFONDEUR.

**Tiers sémantiques (robustesse aux générations de modèles)** : les noms de la table = mapping par défaut au moment d'écrire — lire Haiku = tier rapide/mécanique, Sonnet = tier standard, Opus = tier raisonnement max. Si la session tourne sur un modèle plus récent/capable (ex. Fable 5), la mère = le modèle de la session, et chaque rôle prend le meilleur modèle disponible de son tier (paramètre `model` du tool Agent).

`--judge=opus` force la review en Opus quel que soit le tier. Inversement le reviewer Sonnet reste le défaut (rapide), l'escalade (§4.6c) monte en puissance seulement sur doute.

### Reconnaissance d'archi → persona spécialiste
Le tier choisit *quel modèle* ; la persona choisit *quelle expertise*. À partir du `[scan]` (Étape 2), **nommer la combinaison stack + archi dominante** (CQRS/ES, hexagonal, event-driven, Shopify/Stripe, Next/tRPC…) et la consigner au journal (`specialist_stack`). Quand elle porte des invariants propres :
- **Auto-activé et annoncé**, sans question supplémentaire (l'Étape 2 a déjà son AskUserQuestion ; on n'en rajoute pas). Logger `[tier] mode spécialiste: <stack> → personas expertes (impl/tests/review)`.
- **Persona experte par rôle** : les briefs de l'implémenteur (4.4), du test-writer (4.4b) et du reviewer (4.6) reçoivent « expert senior 10+ ans de <stack> » + une **courte liste d'invariants/pièges** de l'archi à respecter/vérifier en priorité. Exemples : *CQRS/ES* → idempotence des commandes, immutabilité/rejouabilité des events, cohérence projection↔agrégat, sagas/effets rétroactifs ; *Shopify* → pagination/éviction, normalisation E.164, scopes, throttling, champs version-dépendants de l'Admin API ; *front* → hydratation, a11y, états de chargement. La mère établit cette liste (elle PEUT s'appuyer sur une recherche web ciblée si la stack lui est peu familière, cf. principe « recherche externe »).
- **Généraliste** si aucune archi marquante (CRUD simple) : on ne force pas une persona artificielle.
- **Packs spécialistes fournis** : quand un pack `reference/stack-<nom>.md` existe pour la stack détectée, la mère le LIT à ce moment et en injecte les sections par rôle dans les briefs (impl → invariants impl, tests → invariants tests, review → checklist, gate → commandes). Disponibles : `stack-symfony.md` (Symfony/Doctrine/Twig), `stack-golang.md` (Go 1.21+, erreurs silencieuses qui compilent), `stack-htmx.md` (API basse fréquence = hallucinations max), `stack-javascript.md` (vanilla front, erreurs silencieuses async/Unicode), `stack-cqrs-es.md` (pack d'ARCHITECTURE, se combine avec un pack langage — ex. Go+CQRS sur un même projet : charger les deux). Un pack prime sur la liste d'invariants improvisée par la mère ; il s'y AJOUTE des invariants projet (CLAUDE.md) sans les remplacer.

### Mode express (auto sur TRIVIAL, ou forcé par `--fast`)

But : ne pas sortir l'artillerie sur un ticket simpliste. **Déclenché d'office** quand le tier est TRIVIAL ET 0 keyword sensible — pas besoin de `--fast` (qui ne fait que sauter les confirmations et l'imposer si l'estimation hésite).

Chemin court : pas de confirmation Étape 2 (logger le scope+tier détectés et continuer ; axes = standards seuls) → pas de dimensionnement élaboré → **pas de phase PLAN ni mini-review Haiku** (surdimensionné pour < 50 LOC) → impl + tests **par la mère** si les critères d'auto-impl (4.4a) sont réunis, sinon agent A (code) + agent B (tests) → gate objectif (build/lint/tests + red-check sur LE test du comportement principal) → **UNE review déléguée en aveugle** → si gate+review verts : SUCCESS en 1 itération, pas de devil's advocate ni panel. Smoke offline obligatoire ; live seulement si runnable trivialement. Rapport court (statut + radar + fichiers + commit proposé), pas le template complet.

**Garde-fous JAMAIS sacrifiés en express** : séparation reviewer ≠ writer (auto-review interdite, même quand la mère code), gate objectif avant la review, preuves file:line, respect de `no_auto_commit`. **Bascule hors express** dès qu'un keyword sensible OU un overflow (`loc_real > loc_planned*1.5`) apparaît en cours → reprise en boucle standard. Logger `[tier] mode express (TRIVIAL) → review déléguée maintenue, reste allégé`.

### Escalade de modèle en cours de route (la mère peut changer d'avis)
Si un agent Sonnet rend un travail superficiel/faux, ou si une review est incertaine, relancer avec Opus ou un panel. L'estimation initiale n'est pas un contrat figé (cf. §4.6c et boucle adaptative). Logger `[iter N/max] escalade modèle : <rôle> Sonnet→Opus (raison)`.

## Étape 3 — Charger insights + lessons + espace de travail + journal

**Mémoire cross-runs (par projet)** : chercher `~/.claude/projects/<encoded-cwd>/memory/project_feature_loop_insights.md` (encoded-cwd = path absolu avec `/` → `-`).

Si existe : Read, parser, passer comme contexte aux prompts impl/review. Logger `[init] insights projet chargés (N patterns)`.

**Meta-leçons cross-projet** : lire `~/.claude/skills/feature-loop/lessons.md` (créer avec un header minimal s'il n'existe pas). Ces leçons portent sur *comment piloter la boucle* (indépendant du projet) — les passer en tête des prompts impl/review (zone stable, cache-friendly). Logger `[init] lessons cross-projet chargées (N leçons)`.

### Espace de travail : in-place (défaut) ou worktree (`--worktree`)

Enregistrer `run_base_sha = $(git rev-parse HEAD)` AVANT toute modification (permet un reset propre au "jeter").

**Mode in-place (défaut)** — le repo principal EST l'espace de travail, les edits sont visibles live dans l'éditeur de l'user :
- Déterminer la branche de travail :
  - Si la spec vient d'une issue GitLab (`--issue` ou pont issue-mr, Étape 1) et qu'une branche liée `<issue>-*` existe (locale ou `origin/`) → `git fetch origin` puis checkout de cette branche : la convention projet (`<issue>-<slug>`, MR liée) prime sur `feature-loop/<slug>`. Logger `[init] in-place : branche issue <branch> checkout (base <sha-court>)`.
    - **Garde repo sale** : si le repo principal porte des modifs non commitées ÉTRANGÈRES à cette feature (WIP d'une autre session/branche), un checkout les embarque (ou échoue) et le diff/commit final mélangerait les deux travaux → proposer d'office le mode worktree. Worktree sur une branche EXISTANTE : `git worktree add .claude/worktrees/<slug> <branche-issue>` puis `EnterWorktree` avec `path:` (EnterWorktree seul crée une branche NEUVE depuis la base par défaut — il ne sait pas checkout une branche existante). Si la branche issue est déjà checkoutée dans le repo principal, l'y libérer d'abord en parquant le WIP sur une branche locale au même commit (`git switch -c wip-parking`, zéro modif du working tree) — jamais de stash du travail d'une autre session.
  - Si la branche courante est **protégée** (`develop`, `main`, `master`, ou la "Main branch" déclarée dans `<repo>/CLAUDE.md`) → `git checkout -b feature-loop/<slug>` depuis la courante. Logger `[init] in-place : branche <base> protégée → feature-loop/<slug> créée+checkout (base <sha-court>)`.
  - Sinon (déjà sur une feature branch) → rester dessus. Logger `[init] in-place sur branche courante <branch> (snapshots de mécanisme créés ici, squashables en fin de run)`.
- `$WORK` = racine du repo. Pas de `cd`.
- Rollback (4.8) = reset/revert vers le `pre_impl_sha` de l'iter, dans l'arbre vivant.

**Mode worktree (`--worktree`)** :
- `EnterWorktree(name: "feature-loop-<slug>")`. `$WORK` = path du worktree. Lancer ensuite le check symlink vendor/node_modules (Étape 0).
- Cas d'usage : deux runs en parallèle sur le même repo sans collision.

**Artefacts de run (les deux modes)** : `.feature-loop.json` (journal) et `feature-loop-report.md` (rapport) vivent sous `$WORK/.feature-loop/`. En in-place, s'assurer que `.feature-loop/` est ignoré par git (l'ajouter à `<repo>/.gitignore` s'il n'y est pas) pour ne PAS polluer les commits applicatifs. Le runs-log persistant, lui, vit hors arbre (Étape 6).

Créer `$WORK/.feature-loop/.feature-loop.json` :
```json
{
  "feature": "...",
  "started_at": "<ISO>",
  "scope": "...",
  "stack": { "lang": "...", "framework": "...", "tests": "...", "e2e": "...", "lint_plugins": ["..."] },
  "axes": ["..."],
  "threshold": 8,
  "max_iterations": 3,
  "difficulty_tier": "standard",
  "specialist_stack": "<ex: Shopify + CQRS/ES en Go | null si généraliste>",
  "judge_model": "sonnet",
  "paranoid": true,
  "paranoid_auto_triggered_by": ["auth", "token"],
  "best_iter_sha": null,
  "best_radar": null,
  "escalations": [],
  "work_mode": "in_place",
  "work_path": "<repo root ou worktree path>",
  "branch": "feature-loop/<slug> ou branche courante",
  "branch_created": true,
  "run_base_sha": "<sha HEAD avant toute modif>",
  "conventions": [{ "path": "...", "purpose": "..." }],
  "project_insights": "<contenu ou null>",
  "lessons_loaded": 5,
  "baseline": { "build": "pass", "lint_errors": 0, "tests_passed": 47 },
  "iterations": [],
  "rollback_counts": {},
  "persistent_critics": {},
  "final_status": "in_progress"
}
```

## Étape 4 — Boucle d'itération (max 3 par défaut, configurable via `--max-iter`)

### 4.1 Construire le prompt d'implémentation

**Structure cache-friendly** — placer en tête (stable) :
1. Description courte de la feature
2. Conventions extraites (paths + extraits)
3. Project insights (cross-runs)
4. Rubrique des axes (résumée)
5. Contraintes (CLAUDE.md)
6. Charte du code (bloc ci-dessous, verbatim)

**Charte du code** (les conventions du projet priment en cas de conflit) :
> - Le nom EST l'explication : teste-le sur 3 questions (pourquoi il existe / ce qu'il fait / comment l'utiliser) — si un commentaire décrit le *quoi*, renommer au lieu de commenter. Après une fusion/délégation qui fait gagner un nouvel appelant à une fonction existante, re-tester son nom contre TOUS ses appelants (pas seulement le premier) : un nom fidèle à un seul usage devient trompeur une fois partagé.
> - Fonction profonde : petite surface (un appel), beaucoup de travail caché. Découper sans exposer — le sur-découpage (helpers que l'appelant doit enchaîner, méthodes siamoises) est un défaut au même titre que la fonction-fleuve.
> - Commentaires, 3 genres seulement : le **pourquoi** (décision non évidente), l'**avertissement** (piège, ordre à ne pas casser), le **contrat** (ce que la fonction promet). Jamais de paraphrase ; 1 ligne par défaut ; dans le doute, ne pas commenter. Un commentaire long et pénible à écrire signale une abstraction ratée : reconcevoir plutôt que documenter.
> - Erreurs : quand la sémantique le permet, faire disparaître le cas d'erreur (borner, valeur par défaut, null object) au lieu d'imposer des checks à chaque appelant — tirer la complexité vers le bas, dans le module.
> - DRY = savoir, pas code : deux fragments identiques qui évolueront pour des raisons différentes ne sont PAS une duplication — ne pas les fusionner. Boussole ETC : « est-ce plus facile à changer après ? »
> - Boy-scout borné au périmètre : dans les zones touchées, supprimer les commentaires morts/paraphrases existants ; ne rien nettoyer hors scope.

Puis en queue (volatile) :
7. État spécifique à l'itération (critiques précédentes, notes_for_implementer, scores cibles)

Cette structure permet à Anthropic prompt cache de réutiliser le préambule sur toutes les itérations.

Itération 1 : prompt = préambule + exigences de base (tests, build pass, front → Playwright).

Itération N>1 : prompt = préambule + critiques classifiées du tour précédent + `notes_for_implementer` du tour précédent + contraintes anti-régression (axes ≥ N à préserver) + résumé des tentatives précédentes.

**Forçage notes_acknowledged au tour N>1** : ajouter explicitement au prompt :
> "Tu DOIS retourner un champ `notes_acknowledged` qui liste, pour CHAQUE note du tour précédent, comment tu l'as appliquée dans cette implémentation. Format : `[ { note: '...', applied_at: 'file:line', explanation: '...' } ]`. Si tu ne peux pas appliquer une note, dis-le explicitement avec la raison."

Si retour vide ou évasif (toutes `explanation` génériques) → re-prompt avec emphase. Si toujours évasif → flag dans le journal `notes_ignored: true`, à mentionner au reviewer.

Calculer `prompt_hash`. Si déjà vu → reformuler avec variation.

### 4.2 Snapshot pré-implem

Le snapshot permet le rollback/restore. Sa forme dépend de `no_auto_commit` (détecté au pre-flight) :

**Mode 1 — `no_auto_commit: false`** (défaut) : commit de mécanisme.
```bash
git add -A && git commit --allow-empty -m "feature-loop iter-N pre-impl" --no-verify
```
`--no-verify` est volontaire : un snapshot de mécanisme ne doit pas être bloqué par un pre-commit hook applicatif. Noter le SHA dans `pre_impl_sha`.

**Mode 2 — `no_auto_commit: true`** (règle user « pas d'auto-commit ») : ne pas polluer l'**historique de la branche de l'user**, mais le snapshot doit rester **sûr** (anti perte de données : capturer aussi l'untracked, survivre au `git gc`, marcher même sur arbre propre). On crée donc un commit-objet **sur une ref technique dédiée hors-branche** (jamais sur HEAD, jamais dans `git log` de la branche) — **commandes exactes : `reference/git-recipes.md` §4.2 Mode 2** (capture tracked+untracked via index temporaire → `commit-tree` → `update-ref refs/feature-loop/snap-iter-N`). Préféré à `git stash create` (non-ancré donc gc-able, rate l'untracked, chaîne vide sur arbre propre). La branche de l'user n'est PAS modifiée (HEAD, index réel, `git log` intacts).

Rollback (4.8) et restore best (5.0) sur ce snapshot = restaurer le tree de `pre_impl_sha`/`best_iter_sha` dans le working tree **après sauvegarde de l'état courant** (jamais de `checkout -- .` aveugle, cf. 5.0). Nettoyage en fin de run : `git for-each-ref refs/feature-loop/ | … git update-ref -d` (supprimer les refs techniques). Logger `[iter N/max] snapshot ref-technique (no_auto_commit) <sha-court>`.

### 4.3 Phase PLAN (Sonnet) + MINI-REVIEW (Haiku)

**Mode express (2bis)** : sauter 4.3 entièrement — pas de plan formel ni de mini-review Haiku (la mère implémente directement, 4.4a). Reprendre à 4.4.

Log : `[iter N/max] plan Sonnet...`

Sonnet retourne `{ plan, files, tests, risks, confidence }`.

Sanity check basique : paths cohérents, confidence ≥ 6.

**Puis mini-review Haiku** :
```
Agent(
  subagent_type: "general-purpose",
  model: "haiku",
  description: "feature-loop plan check iter N",
  prompt: <prompt court>
)
```

Le prompt :
- "Voici la feature demandée : <description en 1-2 phrases>"
- "Voici le plan proposé par un autre agent : <plan JSON>"
- "Voici 3 conventions du projet (extraits) : <conventions>"
- "Vérifie 3 points : (a) le plan adresse-t-il la feature complètement ? (b) les fichiers cités sont-ils les bons (pas de fichier random, paths cohérents) ? (c) le scope est-il minimal (pas de refacto opportuniste) ?"
- "Réponse JSON : `{ verdict: 'ok'|'concerns'|'reject', concerns: [...], blocking: boolean }`"

Si `verdict: 'reject'` ou `blocking: true` → renvoyer le plan à Sonnet avec les concerns Haiku, demander un plan révisé. Max 2 révisions de plan, après quoi escalation user.

Log : `[iter N/max] mini-review Haiku : <verdict>`.

Si OK → continuer.

### 4.4 Phase IMPLEMENT — agent A (code)

Log : `[iter N/max] impl code (agent <modèle>)...`

Modèle selon le tier (Étape 2bis) : Sonnet (STANDARD), Sonnet/Opus (COMPLEXE/SENSIBLE), mère (TRIVIAL seulement). Mêmes obligations qu'avant (build pass, conventions, scope minimal, STOP_NEED_CLARIFICATION possible).

**Persona + recherche** : si `specialist_stack` est défini (2bis), briefer l'agent A en « expert senior 10+ ans de <stack> » et lui passer la liste d'invariants/pièges d'archi à respecter (écrire idiomatique = moins de bugs à la source). En cas de doute sur une API/un flag/une version, une **recherche web ciblée** est permise (doc officielle d'abord) plutôt que deviner une signature — mais le gate objectif + les tests de B restent l'oracle.

**Périmètre de l'agent A** : le code applicatif **uniquement**. Dès STANDARD, l'agent A **n'écrit aucun test** — tous les tests viennent de l'agent B (4.4b), pour ne pas épouser ses propres angles morts. (Pas d'exception « test unitaire trivial » : la frontière trivial/comportemental est floue et servirait de fuite à la séparation writer≠tester. Les tests critiques red-checkés sont ceux de B, jamais de A.)

Au tour N>1 : inclure forçage `notes_acknowledged` (voir 4.1).

Si retour `STOP_NEED_CLARIFICATION` → AskUserQuestion → re-prompt.

**Post-impl (TOUT agent d'impl — A, Sonnet/Opus ou mère —, à chaque itération) :**

- **Vérification overflow** : compter les LOC réelles. Si `loc_real > loc_planned * 1.5` → flag `impl_overflowed_plan: true`, re-classer le tier vers le haut, ET forcer le devil's advocate au tour suivant (compensation). Logger `[iter N/max] WARN: impl overflow (planned X, real Y) → tier ré-estimé + DA forcée`.
- **Garde de périmètre** : `git diff --name-only $pre_impl_sha` confronté au scope déclaré (fichiers/globs du plan 4.3, ou une consigne explicite type « test-only / ne pas toucher prod »). Tout fichier hors scope — surtout du **code prod sur une tâche test-only** — est flaggé `out_of_scope_edits: [...]` et **présenté à la mère AVANT le gate** : revert par défaut, OU conservation avec justification écrite au journal (ex: vraie régression que le test révèle, à valider explicitement). Logger `[iter N/max] WARN: edits hors scope : <fichiers>`. Découvert en run réel : un agent d'impl (agent A) a modifié un `.templ` de prod de sa propre initiative pour rendre la prémisse d'un test vraie — rattrapé en review, mais un `git diff --name-only` le détecte instantanément (un round-trip + investigation en moins).

#### 4.4a — Implémentation par la mère (TRIVIAL uniquement)

La mère (Opus) peut s'attribuer l'impl SEULEMENT si TOUS ces critères sont vrais d'après le plan validé en 4.3 :

1. `loc_planned < 50`  2. `files_touched <= 2`  3. `files_new == 0`  4. `paranoid == false`  5. `iter == 1`  6. `difficulty_tier == TRIVIAL`

Si **un seul** échoue → délégation à l'agent A (Sonnet/Opus) OBLIGATOIRE.

**Même si la mère code, la review reste déléguée** (agent C ≠ mère, 4.6) — l'auto-review est interdite en toutes circonstances (self-preference bias). C'est la différence clé vs l'ancien "skip Sonnet" : on économise un agent d'impl sur le trivial, **jamais** le regard neuf du relecteur.

Si auto-impl : logger `[iter N/max] impl par la mère (TRIVIAL, loc=X) — review déléguée maintenue` et flag `impl_by_self: true`. Les checks post-impl de 4.4 (overflow, garde de périmètre) s'appliquent aussi à l'auto-impl.

#### 4.4b — Phase TESTS — agent B (≠ agent A), depuis la SPEC

Dès le tier **STANDARD** (sur TRIVIAL la mère écrit les tests). Log : `[iter N/max] tests (agent B, depuis la spec)...`

**Pourquoi un agent distinct** : un test écrit par l'auteur du code teste ce que le code *fait*, pas ce qu'il *devrait* faire — il fige les bugs (regression oracles). Un agent qui ne voit QUE la spec écrit des tests sur le *contrat observable*. 76 % des tests LLM ratent le critère fail-to-pass. **Positionnement vs TDD** : ce « test-depuis-la-spec » capture le bénéfice central du TDD (tester le contrat, pas l'impl) sans imposer l'ordre test-first — incompatible avec la séparation writer≠tester en agents parallèles ; la discipline « rouge » du TDD est garantie a posteriori par le red-check (4.5b).

**Cas dégénéré — le livrable EST du code de test** : quand la feature elle-même est une suite/un module de tests (e2e, harnais de recette…), il n'y a pas de « test du test » → la séparation A (code) ≠ B (tests) s'effondre. Dans ce cas : agent A écrit les tests, **l'agent B ne s'applique pas**, et le signal externe qui le remplace est le **gate live + le red-check** (4.5b — muter la chose réellement testée, prouver que le test rougit). L'invariant non négociable qui DEMEURE = **reviewer ≠ writer** (agent C en aveugle). Ne pas spawner un agent B « tests des tests » (méta-test sans valeur).

**Inputs de l'agent B** (Sonnet, contexte vierge) :
- La **spec/description** de la feature + le contrat d'interface (signatures publiques, entrées→sorties attendues, cas d'usage, cas d'erreur).
- Les conventions de test du projet (extraites Étape 2) + un exemple de test existant.
- **PAS le code de l'agent A** (ou seulement les signatures publiques, jamais le corps). L'agent B teste l'intention, pas l'implémentation.
- **Persona** : si `specialist_stack` défini, expert senior <stack> — il connaît les idiomes de test ET les invariants d'archi à couvrir (ex. CQRS/ES : rejouabilité, idempotence ; Shopify : formats/pagination). Recherche web permise en cas de doute sur l'outil de test ou une API.

**Sortie** : tests couvrant chemin nominal + cas limites (vide/énorme/négatif/NaN/unicode selon le type) + cas d'erreur. Tests sur le comportement observable, pas sur des privates. Il **identifie quels tests sont "critiques"** (logique métier clé, sécurité) ET, pour chacun, fournit son **`target_file:line`** = la ligne de prod que le test protège (nécessaire au red-check 4.5b ; un test critique sans target ne peut pas être red-checké).

**Forme et stratégie (imposées dans le brief de B)** :
- **Structure AAA** : chaque test sépare visiblement Arrange (préparation) / Act (UNE seule action) / Assert (vérification) — lisibilité et diagnostic d'échec immédiats. Suivre la convention du projet si elle existe (table-driven Go, etc.) : AAA s'applique à l'intérieur du pattern local, pas contre lui.
- **Pyramide des tests** : allouer par couche — unitaires nombreux (logique pure, rapides), intégration ciblée (route/repo/règle métier), e2e rares (parcours utilisateur clé, si front). Ne JAMAIS écrire un e2e lent pour ce qu'un test unitaire attrape.
- **Doublures déterministes** : tout non-déterminisme (horloge, réseau, aléa, DB) passe par une doublure injectée (clock fixe, stub, seed) — pas de sleep/retry pour masquer un flaky. Doubler la frontière uniquement, jamais la logique sous test (mock excessif = anti-pattern, cf. rubrique). Rappel : ces doublures rendent le smoke test LIVE (§5.1b) d'autant plus obligatoire — elles ne remplacent jamais le run réel.

Si l'agent B ne peut pas écrire un test sans connaître un détail d'implémentation → c'est un signal que l'API fuit l'implémentation : le noter pour le reviewer (couplage).

**Garde de défaillance de l'agent B** (symétrique à 4.3) : si la sortie de B est vide, non-compilante, ou un refus → re-prompt B 1× (brief affiné) ; si toujours inexploitable → relancer un agent B' distinct 1× ; si échec persistant → **escalade user** (AskUserQuestion : « l'agent de tests n'a pas produit de suite exploitable — livrer sans tests sur ce périmètre ? préciser le contrat ? »). Tant que `tests_produced == 0`, l'itération ne peut PAS être SUCCESS (cohérent avec « pas de validation sans signal externe » : sans tests, pas de signal). Ne JAMAIS combler en laissant l'agent A écrire les tests (rouvrirait la fuite writer==tester).

**Justification "scope petit" sans plan chiffré = refusée**. Le plan 4.3 doit fournir `loc_estimated` pour autoriser le skip.

### 4.5 Phase GATE OBJECTIF (avant tout juge LLM)

Le gate objectif passe AVANT la review LLM : pas d'avis subjectif sur du code qui ne compile/passe pas (et c'est le signal externe sans lequel l'itération ne vaut rien). Si le gate casse → score robustesse = 0, on saute la review, retour à l'agent A avec l'erreur brute.

Log : `[iter N/max] vérification métriques...`

```bash
npm run build 2>&1 | tail -50
npm run lint 2>&1 | tail -50
npm run typecheck 2>&1 | tail -50
npm test -- --run 2>&1 | tail -100
```

**Retry flaky** : si tests fail :
1. Re-run UNE seule fois (`npm test -- --run` à nouveau)
2. Si pass au retry → noter `tests_flaky: true` dans le journal, considérer comme pass, logger `[iter N/max] tests flaky (passé au retry)`
3. Si toujours fail au retry → vrai échec, score robustesse = 0, decision: `build_failure`

Si build/lint/typecheck échouent (pas de retry pour ceux-là) → idem score robustesse = 0.

**Lint plugins spécialisés** : pour chaque plugin disponible (détecté en Étape 2), lancer la règle dédiée si possible :
```bash
npx eslint --config <config> --no-eslintrc --rulesdir ... --rule '...' <files>
# ou simplement laisser eslint global appliquer ses règles si déjà configuré
```

Stocker counts par catégorie : `a11y_errors`, `security_warnings`, `hooks_errors`, etc. Passer ces résultats au reviewer en 4.6.

Si scope front + tout pass : capturer screenshots Playwright multi-viewport (375/768/1440) pour la review visuelle.

#### 4.5b — RED-CHECK (un test critique doit pouvoir échouer)

Sur les seuls tests marqués **critiques** par l'agent B (logique métier clé, sécurité) — pas tous, question de coût. Garde-fou contre les tests vacants (`assertTrue(true)`, assertions absentes) : 76 % des tests LLM passent même sur du code cassé.

**Prérequis — l'agent B fournit la cible.** Quand l'agent B (4.4b) marque un test « critique », il livre aussi son `target_file:line` (la ligne de prod que ce test est censé protéger) — il la connaît, c'est le contrat qu'il teste. **Sans `target` fourni, pas de red-check sur ce test** : on le note `redcheck_skipped` (le reviewer en tient compte) plutôt que de muter une ligne au hasard (faux résultat sur un test d'intégration multi-fichiers).

Pour chaque test critique avec `target` (cap : ~3-5 les plus importants par itération) :
1. **Muter** `target_file:line` par une mutation **type-préservante** : inverser une condition (`if (x)` → `if (!x)`), changer une valeur de retour dans le **même type** (`return total` → `return 0`), décaler un opérateur (`>=` → `>`). Éviter ce qui change le type de retour.
2. **Lancer toute la suite** (pas seulement le test ciblé) et **classer** — le critère universel (vaut autant en typé qu'en dynamique JS/Python) :
   - le **test ciblé échoue** ET **aucun autre test** ne change de statut → ✅ le test protège bien CE comportement, pour la bonne raison.
   - **compile/build/typecheck error** (langage typé) OU **un AUTRE test casse aussi** (la mutation a un effet de bord large, dynamique inclus) → mutation invalide : restaurer, **essayer une autre mutation**. Après 2 essais → `redcheck_inconclusive`.
   - le test ciblé reste **vert** sur une mutation valide → **vacant**.
3. **Restaurer** `target_file:line` — **méthode selon l'état du fichier** (les deux cas existent en run réel) : (a) fichier **propre/committé** → `git checkout -- <target_file>` (robuste ; ne JAMAIS faire un `cp` depuis un backup, un mauvais cwd laisse le fichier muté/cassé) ; (b) fichier **porteur de modifs NON committées** de ce run → `git checkout` les effacerait → restaurer par **remplacement de la chaîne exacte** du contenu original gardé en mémoire. Puis **vérifier l'intégrité** : `git diff -- <target_file>` doit être **vide** (restauration exacte). Diff non vide → re-restaurer depuis le snapshot 4.2.
4. Test **vert** → vacant : renvoyer à l'agent B pour réécriture, flag `vacuous_test_found`. Pas de SUCCESS tant qu'un test critique reste vacant.

**Discriminance — un test peut passer pour la MAUVAISE raison** : muter UNE ligne ne révèle pas un test couvert par une **défense redondante** (deux handlers « ceinture+bretelles » : retirer un seul ne change rien d'observable) ni par un **comportement natif** de la plateforme (ex: un `<dialog>` HTML se ferme sur Escape sans aucun JS → un test qui ferme via Escape passe même si le handler applicatif est cassé). Avant de croire un test critique « non-vacant », vérifier qu'il cible le **mécanisme spécifique** et qu'aucun chemin redondant/natif ne le ferait passer ; si c'est le cas, re-cibler le test (ou muter le bon point). Le red-check mono-mutation est nécessaire, pas suffisant, quand des défenses se recouvrent.

**`inconclusive` n'est PAS un laissez-passer** : un test critique qu'on n'a pas pu prouver non-vacant reste un risque, pas un neutre. `redcheck_inconclusive > 0` sur un test critique → **plafonne l'axe Tests à 7** et est signalé au reviewer (même traitement que `redcheck_skipped`, jamais plus indulgent). Sinon un vrai vacant non-mutable se cacherait derrière « inconclusive ».

Logger `[redcheck] K rougissent / J vacants / L inconclusive`. Coût maîtrisé : la suite est déjà lancée au gate 4.5 — le red-check réutilise ce harnais, 3-5 mutations max. Sur TRIVIAL/`--fast` : red-check sur LE test du comportement principal. Désactivable par `--no-redcheck` (déconseillé).

### 4.6 Phase REVIEW BLIND — agent C (≠ A, ≠ B)

Modèle : **Sonnet par défaut** (rapide/éco), **Opus** si tier COMPLEXE/SENSIBLE ou `--judge=opus`. L'escalade (§4.6c) monte en puissance seulement sur doute. Le reviewer N'EST JAMAIS l'agent qui a écrit le code ni celui qui a écrit les tests (self-preference bias).

Log : `[iter N/max] review (agent C, <modèle>, aveugle)...`

Lire `scoring-rubric.md`.

**Inputs** :
- Description courte (PAS le prompt impl — review en aveugle)
- Rubrique + axes activés (standards + packs conditionnels)
- **Diff vs `pre_impl_sha`** uniquement (scope limité)
- Contenu des fichiers nouveaux
- Métriques objectives (build/lint/typecheck/tests) + résultat du **red-check** (tests vacants détectés ?)
- **Lint plugins outputs** (a11y count, security count, hooks count, etc.) — "données objectives à intégrer au scoring"
- Screenshots paths si applicable
- Scores précédents (iter > 1)
- Project insights
- Flag `notes_ignored`, flag `vacuous_test_found` (mentions spéciales)

**Prompt review** :
- "Tu es un dev senior 10+ ans. Review en aveugle. Tu n'as PAS écrit ce code ni ces tests." Si `specialist_stack` défini (2bis) : « expert senior de <stack> — vérifie en priorité ses invariants/pièges d'archi (liste fournie) ». En cas de doute version/API, recherche web ciblée permise (doc officielle ; le receipt reste file:line + métriques objectives, pas la réponse web)."
- **Anti-biais explicites** (cf. recherche LLM-as-judge) : "Ne récompense JAMAIS la longueur (anti-verbosity) — un code plus court qui fait le travail est meilleur. Liste D'ABORD tout ce qui cloche, puis note (anti-leniency). En cas d'hésitation entre N et N+1, prends N. Préfère le pire cas crédible au 'ça marche'."
- **CoT avant le verdict** : "Raisonne axe par axe (constat + file:line) AVANT de poser chaque note." Le raisonnement explicite améliore l'accord avec l'humain.
- **Lentille cohérence inter-couches** (si le diff touche une requête agrégée ou un mapping post-requête) : "Vérifie que tout `COUNT`/total de pagination porte sur le MÊME ensemble que les lignes affichées après filtrage applicatif (un total calculé avant un `continue`/filtre aval est gonflé) ; que tout `WHERE`/`NOT EXISTS` par-ligne jointe correspond à l'intention par-entité (cas multi-items même clé) ; que filtre SQL et filtre applicatif partagent la même clé de scope. Rejoue le chemin sur 0/1/PLUSIEURS entités du même groupe."
- **Confiance par axe** : "Retourne une `confidence` 0-1 par axe. Si tu hésites ou si les preuves sont minces, baisse la confiance — ce n'est pas pénalisé, c'est utile."
- "Tu DOIS intégrer les métriques objectives : si `a11y_errors > 0`, l'axe accessibilité plafonne à 7 ; si `security_warnings > 0`, l'axe sécurité plafonne à 7 ; si `vacuous_test_found`, l'axe tests plafonne à 6."
- **Tests adversariaux (repris d'outil-factory)** : "Pour CHAQUE finding (critical/major), ajoute sur son entrée un champ `adversarial_test` = le test qui le démontre (même emplacement que `fix_approach`, cf. format scoring-rubric.md). Sur scope sensible, écris-le réellement (XSS, entrée limite, contournement) — il sera ajouté à la suite."
- **`fix_approach` minimaliste obligatoire** : pour CHAQUE critique, propose la solution MINIMALE qui résout les cas concrets identifiés. Cite EXPLICITEMENT les cas que le fix doit couvrir. Ne propose JAMAIS d'infrastructure (parser custom, framework, abstraction, fichier > 50 lignes, méta-test qui réimplémente un private) sans avoir D'ABORD proposé l'option simple. Anti-pattern à pénaliser : méta-tests qui dupliquent leur cible (faux confort).
- Reste = preuves obligatoires (file:line), classification critical/major/minor, `notes_for_implementer`, JSON strict (voir format dans scoring-rubric.md).

**Review d'itération corrective = CONTINUER le même juge, pas un agent frais** : quand le diff de l'iter N+1 ne fait QUE corriger les findings de l'iter N (pas de code nouveau substantiel), la re-review se fait par **SendMessage au juge C de l'iter N** (contexte conservé) avec : résumé des fixes + diff des corrections. Le juge re-note les **seuls axes sous le seuil** et DOIT vérifier les fixes contre les fichiers réels (pas sur le résumé — anti rubber-stamp). C'est le pattern evaluator-optimizer canonique (évaluateur persistant entre rounds) ; l'aveuglement protège le PREMIER jugement, pas la vérification de correction. Économie mesurée : ~35k tokens + ~1 min par itération corrective. **Review aveugle fraîche obligatoire** dès que l'iter ajoute du code nouveau substantiel ou touche un axe non reviewé.

#### 4.6b — Devil's advocate (si paranoid / tier SENSIBLE)

Un 2ᵉ agent adversarial, contexte vierge, mandaté pour CASSER (pas pour valider) — calibré sur les "DA patterns" de `scoring-rubric.md`. Score final = min des deux. Cap optionnel : -2 max par axe. Sur scope sensible, 0 finding high/critical est obligatoire pour SUCCESS. **Lancer EN PARALLÈLE de la review 4.6** (2 appels Agent dans le même message) : les deux jugent le même état figé sans dépendre l'un de l'autre — wall-clock divisé par ~2 sur tier SENSIBLE, aucun effet sur le verdict (≠ du piège test-writer∥reviewer, où le reviewer notait un état périmé).

#### 4.6c — Escalade sur doute (panel avant gros modèle)

**Escalade graduée — on n'appelle le panel que quand c'est vraiment incertain** (sinon le panel-3 = ~3× le coût review se déclencherait sur presque tout run standard, ce qu'on veut éviter). Du moins cher au plus cher, on s'arrête dès que c'est tranché :

**Niveau 0 — rien** (cas normal) : aucun critère ci-dessous → la review 4.6 fait foi.

**Niveau 1 — 2ᵉ juge** (léger, ~1× review en plus), déclenché si l'UN est vrai :
- axe **borderline** près du seuil (score dans `[seuil−1 ; seuil+0.5]`), quelle que soit la confiance ;
- **confiance modérée-basse** (< 0.7) sur un axe qui décide du verdict — c'est l'incertitude qui justifie un 2ᵉ avis, pas la certitude (cf. scoring-rubric.md : confiance basse → escalade, pas pénalité) ;
- **désaccord** 2-3 pts entre review (4.6) et devil's advocate (4.6b) sur un axe.
→ 2ᵉ juge **au moins au niveau de modèle du reviewer initial** (ne jamais faire juger un avis Opus par un Sonnet) : si le reviewer C était Opus, le 2ᵉ juge est Opus ; sinon Sonnet. Prompt reformulé + **ordre du diff/des findings inversé** (casse le biais de position). Sur les **seuls axes douteux**. Convergence (écart < 2 pts) → médiane, fin.

**Niveau 2 — panel de 3** (réservé à la vraie incertitude), si l'UN est vrai :
- **confiance très basse** (< 0.4) sur un axe bloquant ;
- le 2ᵉ juge (niveau 1) **diverge encore** ≥ 2 pts ;
- **scope SENSIBLE** avec un axe sécurité sous le seuil ;
- **preuves invalides** > 30 % qui persistent après re-review (4.7).
→ 3 juges **indépendants** (prompts séparés, aucun ne voit la sortie des autres ; ordre de présentation varié entre eux). **Composition** : par défaut **panel mixte** = 1 juge au niveau du reviewer initial (Opus si COMPLEXE/SENSIBLE) + 2 juges Sonnet. Le juge fort tient le plancher de compétence (on ne dilue pas un avis Opus dans du Sonnet pur), les 2 Sonnet apportent la pluralité de votes à bas coût. Agrégation : **médiane par axe + union des criticals/majors** + **dispersion** (écart max entre juges par axe).
   *Exécution* : 3 appels `Agent` parallèles dans un même message ; si le tool `Workflow` est disponible, le panel PEUT être lancé via un script Workflow (3 `agent()` avec `schema` JSON imposé) — sorties validées structurellement, retries de parsing éliminés. Les phases interactives (AskUserQuestion) restent toujours dans la conversation principale, jamais dans un workflow.
> **Honnêteté coût/diversité (corrige une promesse trop large)** : le « 7-8× moins cher qu'un gros juge » vaut pour un panel de *petits* juges vs un *gros* juge unique — pas pour 3× Opus. Sur scope sensible, le panel mixte coûte ~ (1 Opus + 2 Sonnet), soit l'ordre d'**une review Opus**, et sa valeur est surtout la **réduction du biais de position/formulation**, PAS l'économie ni la diversité de famille (l'outillage est mono-famille Claude). Si des juges d'une autre famille sont dispo (MCP), les préférer — c'est là que la diversité joue vraiment.

**Niveau 3 — arbitre / user**, déclenché si l'UN est vrai :
- **dispersion du panel** > 2 pts sur un axe **bloquant** (le panel n'a PAS convergé — la médiane seule serait un chiffre arbitraire sur 3 avis incohérents) ;
- point **produit / non technique** sur lequel le panel reste partagé.
→ **arbitre Opus** sur ce point précis (pas toute la review). Si l'arbitre reste incertain sur un axe **bloquant et technique**, OU si le point est non technique → **escalade user** (AskUserQuestion). On ne livre jamais un SUCCESS sur un axe bloquant non tranché.

> Effet « rapide sur le facile » : une feature standard bien faite (axes clairs, confiance ≥ 0.7) ne déclenche **aucune** escalade. Le coût ne monte que sur le réellement douteux ou le sensible.

Garde-fou : un axe **sécurité/auth/données sous le seuil ne se "vote" jamais à la hausse** — il reste bloquant tant qu'il n'est pas corrigé. Logger `[iter N/max] escalade : <critère> → <2e juge|panel-3|arbitre Opus> sur axes <...>`. Journaliser `escalations: [...]`.

### 4.7 Validation des preuves (anti-hallucination)

Vérifier file:line cités. Re-review si > 30% invalides. **Cette validation passe AVANT le snapshot du meilleur état (4.7b)** : on ne fige jamais un `best_radar` sur un radar dont les preuves ne sont pas encore validées (sinon le « meilleur » pourrait pointer un état sur-noté par des preuves hallucinées).

#### 4.7b — Snapshot du meilleur état

**Après** review + escalade (4.6c) **et preuves validées (4.7)** : le radar de l'itération est désormais fiable. Si c'est le **meilleur** radar jusqu'ici, enregistrer le snapshot pour pouvoir y revenir en 5.0.
- **Première itération valide** (`best_radar == null`) → setter d'office, sans comparaison.
- **Sinon** → remplacer seulement si score moyen supérieur **ET** pas plus de criticals que le meilleur précédent.

```
best_iter_sha = <ref technique/commit du snapshot 4.2 de cette iter, ou HEAD si commit applicatif déjà fait>
best_radar    = <radar validé de cette iter>
```
En mode `no_auto_commit`, `best_iter_sha` est la **ref technique** `refs/feature-loop/snap-iter-N` (cf 4.2 Mode 2), pas un commit de branche. Logger `[best] iter N = meilleur radar (X) jusqu'ici`. Sert la restauration 5.0 (les gains plafonnent, une iter tardive peut régresser).

### 4.8 Détection régression / persistance / stagnation

Base :
- Régression sur axe ≥ 8 → rollback + contrainte
- Critique persistante 3 tours → escalation user
- Convergence improbable → escalation user

**Heuristique trade-off caché (régression cumulée)** :

À chaque tour, calculer `cumulative_regression = somme des baisses sur tous les axes` vs `gain sur axe(s) cible(s)`. Si :
- `cumulative_regression > 2` ET
- au moins 1 axe cible (visé par les critiques du tour précédent) a gagné ≥ 1 point

→ le major/critique initial était probablement SUR-ÉVALUÉ. Loguer `[iter N/max] trade-off caché détecté (gain +X sur cible vs -Y cumulé ailleurs)` et **forcer le reviewer du tour suivant à répondre dans son JSON** : "Le major précédent était-il vraiment major, ou un minor déguisé ? Justifie." Champ `major_reclassification` ajouté au journal.

**Régression douce vs violente** :

| Type | Définition | Action |
|---|---|---|
| Douce | ≤ 1 point cumulé sur axes ≥8, ET cause racine commune identifiée, ET solde net positif sur majors/criticals fermés | **Continue avec warning** + flag `soft_regression_allowed: true` + justification écrite obligatoire au journal |
| Violente | > 1 point sur ≥ 1 axe, OU plusieurs causes éparses, OU axe cible non amélioré, OU régression sans majors fermés | **Rollback strict** (revert pur du commit) |

L'agent doit justifier explicitement dans le journal toute dérogation. Sans justification → rollback strict appliqué par défaut.

**Mode rollback simplificateur** (alternative au rollback strict) :

Si une approche s'avère sur-ingénierée à l'usage (révélé par régression cumulée sur lisi/simpl/YAGNI/modul tout en fermant un major), l'agent peut proposer un **rollback simplificateur** au lieu du rollback strict :
1. Revenir à l'approche plus simple (souvent celle d'iter 1 ou d'une iter antérieure)
2. **MAIS** garder les améliorations concrètes (helpers utiles, glob auto, patterns étendus)
3. Documenter EXPLICITEMENT les limites assumées dans un docblock ou commentaire au point concerné
4. Ajouter 2-3 tests edge case ciblés pour les cas spécifiques que la simple version ratait

Ce mode = ce qu'un dev senior ferait spontanément en disant "ok, j'ai sur-ingénieré, je recule mais je garde ce qui est utile et je documente honnêtement les limites" (cf principe "honnêteté > faux confort"). À privilégier sur le rollback strict quand : (a) sur-ingénierie identifiée par cumulative_regression, (b) la simplification ne recrée PAS de critical/major. Logger `[iter N/max] rollback simplificateur appliqué`.

### 4.9 Journaliser

Append au journal. Champs supplémentaires :
- `paranoid_active: boolean`
- `lint_plugins_results: { a11y_errors, security_warnings, ... }`
- `tests_flaky: boolean`
- `notes_acknowledged: [...]` (avec applied_at file:line)
- `notes_ignored: boolean`
- `plan_revisions: int` (combien de fois Haiku a rejeté le plan)
- `devil_advocate_disagreements: [...]`
- `evidence_invalid_count: int`
- `rollback_counts: { "<iter>": int }` — incrémenter la clé de l'itération de 1 à chaque rollback exécuté (strict ou simplificateur, 4.8)
- `redcheck: { critical: int, vacuous: int, inconclusive: int, skipped: int }` (4.5b)
- `escalations: [...]` (niveau atteint + axes concernés, 4.6c)
- `best_iter_sha`, `best_radar` (4.7b)

### 4.10 Critère d'arrêt

**Renforcement MAX_ITERATIONS** :

Si `n == max_iterations` ET pas SUCCESS strict → AVANT de générer le rapport, présenter à l'user avec **justification explicite** :

```
MAX_ITERATIONS (N=<max>) atteint, pas SUCCESS strict.

État actuel :
- Axes sous seuil : <liste avec scores>
- Critical/Major restants : <liste courte>

Diagnostic — pourquoi on n'a pas convergé en N tours :
  <synthèse 2-3 lignes — cause racine probable, pas du blabla>

Je pense qu'avec <X> itération(s) supplémentaire(s) je pourrais :
  - Fix <axe> de N→M : <comment, en 1 ligne>
  - Fix <axe> de N→M : <comment, en 1 ligne>

Options :
  1) Accepter l'état (axes sous seuil = limites assumées documentées) → présenter rapport + merge
  2) Autoriser +X itération(s) avec ces objectifs précis → on continue
  3) Abandonner (jeter le travail — voir sémantique "jeter" en 5.6 selon le mode)
```

**Pas de continuation automatique** au-delà de max_iterations. L'agent doit fournir un **diagnostic concret** + un **plan chirurgical** des iter supplémentaires demandées (pas "je vais essayer encore"). L'user décide en connaissance de cause.

Feedback user (cf mémoire) : "essayer en 3 iter, si vraiment besoin de plus on en parle, c'est lui qui décide". Le skill honore ce principe : default 3, escalation argumentée pour aller au-delà, pas de masturbation silencieuse.

## Étape 5 — Finalisation

### 5.0 Restaurer la MEILLEURE version (pas forcément la dernière)

Avant le smoke test : comparer le radar de l'itération finale à `best_radar` (4.7b). Si la dernière EST la meilleure (cas normal d'une convergence propre) → rien à faire. Sinon, restaurer `best_iter_sha` — **mais la méthode dépend du contexte, jamais de `reset --hard` aveugle** (risque de détruire du travail de l'user sur sa propre branche) :

**Garde appliquée (prédicat exécutable, pas un commentaire).** Deux invariants : (1) **filet de sécurité d'abord** — sauvegarder l'état courant AVANT toute restauration (ref technique `refs/feature-loop/safety-pre-restore`), jamais de `checkout -- .`/`reset --hard` qui détruit du travail non sauvegardé ; (2) **tester `no_auto_commit` EN PREMIER** (un projet peut avoir la règle globale `no_auto_commit` ET une branche créée par le skill → le snapshot est une ref technique, pas un commit de branche).

Trois cas de restauration, **commandes exactes : `reference/git-recipes.md` §5.0** :
- **`no_auto_commit: true`** → `git read-tree -u --reset "$best_iter_sha"` (restaure le tree de la ref technique, tracked+untracked, sans toucher l'historique user).
- **worktree OU branche créée par le skill (`branch_created`)** → `git reset --hard "$best_iter_sha"` (sûr, best = vrai commit sur branche jetable).
- **in-place sur la branche COURANTE de l'user (mode commit)** → JAMAIS de reset (jetterait un commit user intercalé) : `git branch -f feature-loop/best "$best_iter_sha"` puis AskUserQuestion (merger feature-loop/best / garder la dernière / voir le diff). Pas de restauration destructive d'office.

Logger `[converge] meilleure = iter K (radar X) > dernière (Y) → <read-tree|reset|branche+demande>`. La ref `refs/feature-loop/safety-pre-restore` permet de revenir en arrière si la restauration ne convient pas. Justification : gains qui plafonnent + régression tardive possible → on livre le meilleur état, **jamais au prix d'une destruction non sauvegardée** (cohérent avec 5.6 et CLAUDE.md « input ambigu = pas d'action destructive »). En mode user-branch-commit, la garantie « meilleure version » est tenue par une **option présentée**, pas par un abandon silencieux.

### 5.1 Smoke test final offline (si SUCCESS)

Log : `[smoke] re-run final build+tests...`

Re-lancer build + lint + typecheck + tests sur l'état final (après restauration éventuelle). Si échec → déclasser SUCCESS, présenter à l'user.

### 5.1b — Smoke test LIVE (exécution réelle — OBLIGATOIRE si l'app est runnable)

Log : `[smoke-live] exécution réelle...`

**Pourquoi.** Le gate offline (build/lint/tests, MÊME les intg sur une DB de test) n'exerce PAS l'app en train de tourner contre son environnement réel. Les pannes qui se cachent là : un serveur de dev déjà lancé qui tourne encore sur l'ANCIEN binaire (le code édité n'est pas chargé) ; une migration éditée mais **non rejouée** sur la DB que l'app live utilise (le runner ne ré-applique pas une migration déjà passée) ; une erreur de câblage/config runtime ; une intégration que les mocks simulaient. **Tests verts ≠ ça marche.** Cette étape est le signal externe réel — voir le principe « le run réel est le signal » dans les Principes non négociables.

Procédure :

1. **Runnable ?** La feature touche-t-elle un point d'entrée exécutable (serveur, CLI, UI, job/cron) ? Si c'est une lib pure SANS chemin runtime ni consommateur à invoquer → logger `[smoke-live] non runnable (lib pure) — skip justifié` et passer. Sinon le live smoke est REQUIS. **Réutiliser d'abord un skill projet s'il existe** (`run`, `verify`, ou un skill de lancement dédié) plutôt que réinventer.

2. **Process déjà lancé = suspect de staleness.** Si un process long de dev (serveur) écoute déjà, il a très probablement démarré AVANT les edits de ce run → il sert du vieux code. **Le relancer** pour charger le nouveau binaire/code. Tuer **par PID du listener** (`ss -ltnp | grep :<port>` → kill ce PID) — JAMAIS `pkill -f <motif>` quand le motif peut matcher la commande shell courante (auto-kill garanti). Relancer en arrière-plan avec capture des logs ; attendre l'écoute effective.

3. **Aligner le runtime sur les edits.** Si la feature touche le schéma (migrations) ou la config : appliquer/charger ces changements sur l'ENVIRONNEMENT que l'app live utilise réellement (la DB dev pointée par la config runtime — **pas seulement** la DB de test des intg). Gotcha majeur : éditer une migration DÉJÀ appliquée ne la rejoue pas → la DB runtime garde l'ancien schéma → l'app neuve casse dessus. Vérifier le schéma réel (`information_schema` / introspection) ; en cas de dérive, soit ajouter une migration forward (`ALTER`), soit reset/réappliquer selon le contexte (jamais de reset destructif d'une DB de l'user sans confirmation).

4. **Exercer le chemin modifié de bout en bout.** Déclencher RÉELLEMENT la feature (requête HTTP, clic Playwright, invocation CLI) et OBSERVER la réponse + les **logs applicatifs**. Pour une feature UI : **afficher ≠ exercer** — (a) SOUMETTRE chaque form nouveau/modifié (POST réel, pas seulement le GET de la page), (b) cliquer chaque contrôle ajouté (checkbox, bouton, lien), (c) vérifier l'effet en DB ou sur la page résultante, (d) vérifier que chaque route nouvelle a un **lien entrant** dans l'UI (pas d'URL orpheline — la review code-centrique ne le voit pas). Critère de succès : pas de 5xx ni d'erreur dans les logs, sortie conforme. UI → Playwright (au moins un viewport). Route protégée → réutiliser une session existante / le harnais d'auth du projet.

5. **Si la vérif live est partiellement bloquée** (auth/SSO non scriptable, creds externes, service tiers indispo) : faire le MAXIMUM faisable — booter l'app et confirmer démarrage propre + route non-5xx ; rejouer les requêtes/SQL EXACTES du chemin contre l'env dev réel (preuve au niveau DB/HTTP). PUIS dire EXPLICITEMENT à l'user ce qui n'a pas pu être auto-vérifié + les étapes exactes pour qu'il confirme. **Ne JAMAIS présenter un SUCCESS comme « testé » quand seuls des mocks / une DB de test ont tourné** — l'honnêteté prime (cf. principe honnêteté > faux confort).

6. **Échec live → déclasser SUCCESS.** L'erreur live (log/réponse) devient une contrainte : repartir en itération (4.x) pour la corriger, ou présenter à l'user si hors périmètre. Le rapport (5.4) note ce qui a été vérifié live vs laissé manuel.

### 5.1bis — Commit final

Log : `[commit] vérification commit final dans l'espace de travail...`

Avant tout conflicts check : vérifier que la branche de travail a au moins un commit applicatif (les `feature-loop iter-N pre-impl` ne comptent pas — ce sont des snapshots).

```bash
cd $WORK
APPLICATIVE_COMMITS=$(git log $run_base_sha..HEAD --oneline 2>&1 | grep -vc "feature-loop iter-.*-impl")
```

#### Mode 1 — `no_auto_commit: false` (par défaut, pas de règle user détectée)

Si `APPLICATIVE_COMMITS == 0` → **forcer un commit applicatif** maintenant :
```bash
git add -A
git commit -m "feat(<slug>): <résumé feature en 1 ligne>"
```
Le message reprend le slug de la feature. Pas de Co-Authored-By, pas de mention Claude/AI. Si pre-commit hook échoue → l'inscrire dans le rapport et présenter à l'user.

#### Mode 2 — `no_auto_commit: true` (règle CLAUDE.md user détectée au pre-flight)

Si `APPLICATIVE_COMMITS == 0` → **NE PAS commit**. À la place :

1. Préparer le message de commit (format identique : `feat(<slug>): <résumé>`)
2. Logger `[commit] règle user 'no auto-commit' active → commit proposé, non exécuté`
3. Dans le rapport markdown final, section **"Commit à exécuter manuellement"** :
   ```markdown
   ## Commit à exécuter manuellement

   Le skill respecte ta règle CLAUDE.md "pas d'auto-commit". Modifs prêtes mais non commitées.

   À exécuter quand tu valides :
   \```bash
   cd <work-path>
   git add -A   # .feature-loop/ est gitignoré, n'entre pas dans le commit
   git commit -m "feat(<slug>): <résumé feature>"
   \```

   Une fois committé, la branche est mergeable proprement (vérifié pré-validation au conflicts check ci-dessous).
   ```
4. **Conflicts check (5.2) peut être lancé quand même** sur l'état "staged" (stash des unstaged → `git add -A` → merge-tree → `git reset` → `git stash pop`) — **commandes exactes : `reference/git-recipes.md` §5.1bis Mode 2**. Cela donne une estimation honnête de la mergeabilité POST commit user, sans modifier le working tree.

5. Le rapport indique : **"Mergeable proprement (sous réserve du commit à exécuter manuellement)"** ou **"Conflits attendus avec main : <liste>"** selon le résultat.

**Sans ce commit (mode 2), le rapport ne peut PAS prétendre "mergeable proprement" simple** — il doit explicitement mentionner que le commit user est requis avant le merge réel.

### 5.2 Conflicts check vs main

Log : `[conflicts] vérification mergeabilité vs main...`

**Préalable (selon le mode 5.1bis) :**
- **Mode 1** (commit auto) : 5.1bis a forcé ≥1 commit applicatif → exécuter le merge-tree ci-dessous.
- **Mode 2** (`no_auto_commit`) : pas de commit par design → conflicts-check déjà estimé en 5.1bis via la procédure stash décrite dans son Mode 2. NE PAS relancer le merge-tree ci-dessous (il porterait sur HEAD sans les modifs non-committées), pas d'échec dur.

```bash
git fetch origin
git merge-tree $(git merge-base HEAD origin/main) HEAD origin/main 2>&1 | head -50
```

Si conflits détectés → noter dans la présentation : "Branche mergeable avec **X conflits** sur fichiers : <liste>. Tu devras résoudre manuellement au merge."

Log : `[conflicts] N conflits détectés sur <fichiers>` ou `[conflicts] mergeable proprement`.

### 5.3 Construire le radar ASCII

### 5.4 Rapport markdown final

Log : `[report] feature-loop-report.md écrit`

Écrire `$WORK/.feature-loop/feature-loop-report.md` en suivant `reference/report-template.md` (**le lire à ce moment** — toutes les sections sont obligatoires) : en-tête statut/durée/itérations/paranoid, feature demandée, radar final + delta iter 1, timeline des itérations, criticals/majors fixés et restants, **Ajouts non demandés** (scope creep justifié — seuil : > 20 LOC ou > 1 option/flag/cache/abstraction ; l'user peut demander leur retrait avant merge), fichiers modifiés, métriques finales, conflits avec main, recommandations, espace de travail.

Ce fichier vit sous `$WORK/.feature-loop/`, l'user peut le partager ou l'archiver. Plus utile que le JSON brut.

### 5.5 Insights projet (mémoire cross-runs) + findings non-triviaux

Compiler et écrire `project_feature_loop_insights.md` dans la mémoire du projet.

**Findings non-triviaux à propager explicitement** : à la fin de chaque run, l'agent doit identifier 1-3 **findings non-triviaux** découverts pendant le run, et proposer leur écriture en mémoire cross-runs (pas seulement dans CLAUDE.md qui peut être réécrit). Critère "non-trivial" :

- Découverte empirique qui contredit une hypothèse documentée (ex: "api_key cassait CORS, alors qu'on croyait l'inverse")
- Piège qui aurait fait perdre du temps à un autre dev sans cette info
- Convention spécifique au projet qui n'est PAS déductible du code en 5 min
- Comportement subtil d'une API tierce (WAF anti-bot, OAuth, etc.) découvert en live

Pour chaque finding : créer ou enrichir un fichier dédié `project_<finding-slug>.md` dans la mémoire du projet avec frontmatter `type: project` et un **Why:** + **How to apply:** explicites.

Logger `[insights] N findings non-triviaux proposés en mémoire`. L'écriture est faite directement par le skill (pas de question à l'user — un finding empirique validé live est par défaut intéressant).

Ajouter une ligne dans `MEMORY.md` du projet pour chaque nouveau fichier (format index standard).

### 5.6 Présentation à l'user

Output structuré :
- Statut + durée + itérations
- Radar final
- Lien vers le rapport markdown (`$WORK/.feature-loop/feature-loop-report.md`)
- Mention conflits
- Espace de travail : mode (in-place/worktree) + branche + path

Puis `AskUserQuestion` : merger / garder / jeter. Sémantique du "jeter" selon le mode :
- **worktree** : `ExitWorktree` (supprime le worktree) après confirmation.
- **in-place, branche `feature-loop/<slug>` créée par le skill** : `git checkout <base> && git branch -D feature-loop/<slug>` après confirmation explicite.
- **in-place sur la branche courante de l'user** : action destructive sur SON arbre → confirmation explicite obligatoire (cf CLAUDE.md "input ambigu = pas d'action destructive"), puis proposer `git reset --hard $run_base_sha` SANS l'exécuter d'office. Ne jamais reset la branche de l'user sans un "oui" sans ambiguïté.

Si l'user choisit merger/garder ET qu'un skill `branch-wrap-up` est disponible : suggérer `branch-wrap-up --no-review` pour la clôture (commit si mode no_auto_commit, push, MR/PR, capture) — la review en aveugle de ce run tient lieu de passe senior-review, ne pas la payer deux fois.

### 5.7 Runs-log persistant + lessons cross-projet

**Runs-log** : append une ligne JSON au fichier HORS arbre `~/.claude/projects/<encoded-cwd>/memory/feature_loop_runs.jsonl` (créer s'il n'existe pas). Une ligne = un run terminé :
```json
{"slug":"add-csv-export","date":"<ISO>","status":"SUCCESS","iterations":2,"radar_avg":8.4,"axes_below":[],"criticals_left":0,"duration_min":14,"subagent_tokens_total":110000,"mode":"in_place","branch":"feature-loop/add-csv-export","paranoid":false,"tier":"standard","escalations":0,"skill_version":"8.6.0","anomalies":{"vacuous_tests":0,"redcheck_inconclusive":0,"rollbacks":0,"plan_revisions":0,"evidence_invalid_pct":0,"notes_ignored":false,"live_smoke_fail":false,"agent_b_retries":0}}
```
Ce fichier survit aux runs ET aux suppressions de branche/worktree (d'où le hors-arbre) — c'est la source du tableau de bord `status`. Le champ **`anomalies`** trace les endroits où la **boucle elle-même** a buté (vs la feature) : tests vacants, mutations inconclusives, rollbacks, plans rejetés, preuves hallucinées, notes ignorées, échec smoke-live, agent B relancé. C'est l'historique d'échec du *skill*, matière première de `learn` (Étape 7) — remplir les compteurs depuis le journal `.feature-loop.json`, zéros inclus (l'absence d'anomalie est aussi un signal). **`subagent_tokens_total`** : somme des `subagent_tokens` retournés par chaque appel Agent du run (la mère les note au fil de l'eau) — c'est la mesure objective du coût, base de comparaison avant/après toute optimisation du skill ; `status` peut alors montrer la tendance coût/durée par tier. Logger `[runs] run loggé dans feature_loop_runs.jsonl`.

**Lessons cross-projet** : si le run a révélé une leçon sur *comment piloter la boucle* (réutilisable sur un AUTRE projet — ex: "un major a11y sur icon-button est presque toujours réel, ne pas le reclasser en minor", "le skip Sonnet overflow quasi-systématiquement sur les features touchant une migration"), l'append à `~/.claude/skills/feature-loop/lessons.md`. **Test de tri** : spécifique au projet courant → insight projet (5.5) ; vrai sur d'autres projets → lesson cross-projet ici. **Anonymisation obligatoire** : ce fichier peut être publié (repo public) — la leçon ne nomme JAMAIS un client / projet / vendor / branche / champ métier réels ; généraliser (« un projet réel », « une intégration tierce »). Logger `[lessons] N meta-leçon(s) cross-projet ajoutée(s)`.

## Étape 6 — Sous-commande `status` (hors boucle, lecture seule)

Tableau de bord des runs passés depuis le runs-log hors arbre (`feature_loop_runs.jsonl`, cf. 5.7). Lecture seule : aucune question, aucune modif fichier. Procédure complète : **lire `reference/subcommands.md` au dispatch**.

## Étape 7 — Sous-commande `learn` (propose-only, hors boucle)

Analyse les runs-logs (+ champ `anomalies` = échecs de la boucle elle-même), complète `lessons.md` (additif uniquement, **leçons anonymisées** — aucun nom client/projet réel, cf. 5.7), propose une consolidation de `lessons.md` quand doublons/contradictions/inflation (> ~30 leçons) — diff présenté, appliqué seulement sur validation —, et PROPOSE des évolutions du SKILL.md sans JAMAIS les appliquer seul : sections LOCKED interdites, garde-fou anti-dérive (ne propose jamais d'affaiblir un garde-fou), versioning semver uniquement sur modif validée par l'user. Procédure complète : **lire `reference/subcommands.md` au dispatch**.

## Quand interagir avec l'user (récap)

| Situation | Étape |
|---|---|
| Repo non clean / build cassé au baseline | 0 |
| Description vague | 1 |
| Auto-détection ambiguë | 2 |
| Framework de tests non détecté avec confiance | 2 |
| Axes / conventions / paranoid à confirmer | 2 |
| Plan Sonnet rejeté 2× par Haiku | 4.3 |
| Sonnet retourne `STOP_NEED_CLARIFICATION` | 4.3/4.4 |
| Régression ≥ 2 fois sur même axe | 4.8 |
| Critique persistante 3 tours | 4.8 |
| Stagnation prédite | 4.8 |
| Critical d'ordre produit | 4.6 (via review) |
| Smoke test final offline échoue | 5.1 |
| Smoke test LIVE échoue (erreur runtime) | 5.1b |
| Smoke test LIVE bloqué (auth/creds/service tiers) → dire ce qui reste à confirmer | 5.1b |
| `learn` propose une modif SKILL.md ou une consolidation lessons.md | 7 (`reference/subcommands.md`) |
| Statut final de l'espace de travail (merger/garder/jeter) | 5.6 |
| Reset destructif de la branche courante de l'user (in-place, "jeter") | 5.6 |
| Panel partagé sur un point produit/non technique après escalade | 4.6c |

Règle d'or : mieux vaut 1 question bien posée que 3 itérations dans la mauvaise direction.

## Tools requis (à charger via ToolSearch)

- `EnterWorktree`, `ExitWorktree` (UNIQUEMENT en mode `--worktree` ; inutiles en in-place où l'on reste dans le repo via `git checkout -b`)
- `TaskCreate`, `TaskUpdate`
- `mcp__playwright__browser_*` (si front — review visuelle ET smoke test LIVE §5.1b)
- `Bash` avec `run_in_background: true` — pour le smoke test LIVE (§5.1b) : lancer/relancer le serveur dev et capturer ses logs sans bloquer. Relancer un serveur déjà up = tuer **par PID du listener** (`ss -ltnp | grep :<port>`), jamais `pkill -f <motif>` qui matche la commande courante (auto-kill).
- `Agent` (natif, supporte `model: haiku|sonnet|opus|fable…` selon les modèles de la génération courante) — **socle de la séparation des rôles** : un appel `Agent` distinct par rôle (impl A, tests B, review C, devil's advocate, juges du panel), chacun en contexte vierge. La mère ne fait jamais le rôle d'un agent qu'elle a déjà joué sur la même itération. Les agents ne peuvent pas eux-mêmes spawner d'agents (la mère reste seule à déléguer).
- `WebSearch`, `WebFetch` — recherche externe « en cas de doute » version/API/framework (cf. Principes) : doc officielle d'abord, l'oracle reste le gate objectif + red-check + smoke live.
- `Workflow` (optionnel, si disponible) — exécution déterministe du panel-3 (§4.6c) avec sorties schema-validées. Les phases interactives (AskUserQuestion) restent dans la conversation principale, jamais dans un workflow.

## Ce que le skill NE fait PAS

<!-- LOCKED: jamais d'édition auto par `learn` (propose-only, voir Étape 7). Modif humaine uniquement. -->

- Ne push pas, ne merge pas, ne commit pas sur la branche principale
- Ne supprime pas le worktree, ni ne reset/supprime la branche de l'user, sans confirmation explicite
- Ne déclenche pas la boucle sur baseline cassé (questionne)
- Ne déclenche pas la boucle sans description claire (questionne)
- N'installe AUCUN package sans confirmation (lint plugins, frameworks de tests)
- N'accepte pas un score sans `file:line` valide
- Ne valide pas SUCCESS si build/lint/tests cassent (smoke test final offline non plus)
- Ne prétend JAMAIS « testé » sur la seule foi des mocks / d'une DB de test : si l'app est runnable, le smoke test LIVE (§5.1b) est obligatoire ; s'il est bloqué (auth/creds), dire explicitement ce qui reste à confirmer côté user
- Ne mentionne pas Claude/AI dans les commits
- N'ajoute pas de Co-Authored-By
- Ne fait pas de refactoring opportuniste hors scope feature
- Ne note pas sur du code legacy non modifié (scope review = diff uniquement)
- Ne reste pas silencieux > 3 min (logs continus)

## Limitations connues

Détail : `reference/limitations.md` — **à lire si l'un de ces contextes est détecté** : symlink `vendor/`/`node_modules/` en mode `--worktree` (tests runtime des entités non fiables), projet sans build standard (extension Chrome MV3…), axes UI non applicables (lib/CLI), retry flaky limité à 1.

## Garanties

<!-- LOCKED: jamais d'édition auto par `learn` (propose-only, voir Étape 7). Modif humaine uniquement. -->
<!-- Historique des versions qui ont introduit chaque garantie : CHANGELOG.md. -->

Fondements : `reference/references.md`.

- **Pre-flight** : baseline projet vérifiée avant tout (même suite que le gate).
- **Isolation par branche** : in-place sur branche dédiée par défaut, ou worktree (`--worktree`) ; `run_base_sha` + snapshots → reset/rollback sûr, jamais de reset destructif de la branche user sans confirmation.
- **Séparation writer ≠ tester ≠ reviewer** : l'auteur du code ne le teste ni ne le juge jamais ; review en aveugle ; auto-review interdite même quand la mère code.
- **Tests depuis la spec par un agent distinct** (dès STANDARD) : contrat, pas implémentation ; AAA, pyramide unit/intégration/e2e, doublures déterministes ; « rouge » tenu par le red-check.
- **Gate objectif avant juge LLM** : pas de SUCCESS sans signal externe (build/lint/typecheck/tests verts) ; métriques + lint plugins avant la review ; retry flaky 1×.
- **Red-check** : tout test critique doit pouvoir rougir (anti tests vacants).
- **Smoke offline + smoke LIVE + conflicts check** : exécution réelle de l'app et chemin exercé de bout en bout avant tout SUCCESS « testé » ; live bloqué → maximum faisable + dire ce qui reste à confirmer.
- **Anti-biais du juge** : review en aveugle + anti-verbosity + anti-leniency + CoT avant note + confiance par axe + preuves file:line vérifiées ; screenshots multi-viewport (front).
- **Escalade sur doute (graduée)** : borderline / désaccord / confiance basse → 2ᵉ juge → panel mixte de 3 → arbitre Opus ; axe sécurité jamais voté à la hausse ; devil's advocate auto sur keywords sensibles.
- **Effort proportionné** : modèle et profondeur selon le tier ; **mode express d'office sur TRIVIAL** ; impl par la mère conditionnée à 5 critères mesurables (loc<50, files≤2, files_new=0, paranoid=off, iter=1) + flag overflow ; mini-review Haiku du plan (hors express).
- **Garder la meilleure version** : restauration du meilleur radar, pas la dernière ; détection convergence/stagnation/critiques persistantes.
- **notes_acknowledged forcé** : le tour N+1 prouve qu'il a lu le tour N.
- **Scope review = diff** (pas de pollution legacy) ; scope creep flaggué au rapport (« Ajouts non demandés »).
- **Commit applicatif obligatoire avant « mergeable »** : forcé, ou proposé si `no_auto_commit`.
- **Traçabilité 3 niveaux** : journal JSON + rapport markdown + runs-log persistant hors arbre (`status`) ; chaque run porte `anomalies` + `skill_version`.
- **Mémoire cross-runs** : insights projet + findings non-triviaux + meta-leçons cross-projet (`lessons.md`).
- **`learn` propose-only** : additif dans `lessons.md` ; toute évolution du SKILL.md = diff validé par l'user, jamais les sections LOCKED.
- **Axes standards-base + extension** : pas de substitution silencieuse.
- **Prompt caching** : préambule stable en tête des prompts.
- **Interactions ciblées** : contrôle user préservé sur décisions non techniques.

---

## CHANGELOG
Historique complet des versions : `CHANGELOG.md` (à côté de ce fichier). Version courante : **8.15.0**.
