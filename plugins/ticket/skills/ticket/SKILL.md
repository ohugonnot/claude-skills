---
name: ticket
description: >-
  Use when the user hands over a ticket (issue, bug, feature request, review finding) to take from
  description to a reviewed, tested MR/PR, in phrasings such as "fais le ticket", "take this ticket",
  "plan fable execution sonnet /senior-review opus", "crée le ticket et fais un plan", "en TDD avec
  test e2e et captures playwright au plus près du réel", "/senior-review en boucle et commit push si
  tout est ok", "comme d'hab", or just a ticket number or link plus "vas-y" / "go". Use it whenever a
  ticket has to be delivered end to end, even if the word "ticket" is never used as a skill name.
  A light ticket method: read the ticket and the code it touches, plan by a strong-model agent, TDD
  execution by a standard-model agent, proof closest to real use (replayable Playwright e2e with
  mobile/tablet/desktop captures), a /senior-review loop, then a retrospective that proposes rule
  lines for the user to approve. NOT for the heavy autonomous loop (use feature-loop), nor for only
  creating the issue/branch/MR shell (use issue-mr), nor for closing already-written work (use
  branch-wrap-up), nor for a review alone (use senior-review).
argument-hint: "<numéro ou lien du ticket | description> [--trivial]"
---

# Ticket : de la description à la MR prouvée

**skill_version : 1.1.0** (historique : `CHANGELOG.md`).

Un ticket est fini quand sa preuve se vérifie **du dehors** : un test vu rouge puis vert, une capture lue, un tour de revue qui ne change plus rien. Jamais quand « ça a l'air de marcher ». Ce skill est léger exprès : il enchaîne des outils qui existent (`/issue-mr`, `/senior-review --loop`, `/branch-wrap-up`, chacun si disponible) et ne fait lui-même que l'orchestration et les vérifications.

Le ticket : $ARGUMENTS

## 1. Lire la phrase de lancement

La phrase de lancement fixe les rôles. La lire mot à mot avant d'agir.

| La demande dit | Ce que ça déclenche |
|---|---|
| « plan fable », « plan en opus » | agent `Plan` avec ce `model`, lecture seule. **Sauf si un plan existe déjà** dans le ticket. |
| « exécution sonnet » / « en opus » | `model` de l'agent exécutant. |
| « /senior-review opus en boucle » | `/senior-review --loop`, relecteurs sur ce modèle. |
| « met le plan dans le ticket » | le plan va dans la description du ticket. |
| « crée le ticket », « ticket MR » | `/issue-mr` d'abord (ticket + branche + MR en draft). |
| « commit push si tout est review et testé » | autorisation **conditionnelle**, limitée à ce ticket (voir § 6). |
| « comme d'hab », « fais au mieux », « avance sans moi » | tout enchaîner sans attendre de validation ; la cadence reste un écran, un test à la fois (§ 3.5). |

Rien de précisé : plan sur le modèle le plus capable disponible, exécution sur le modèle standard (Sonnet), revue en boucle au tier standard sur le modèle standard, commit **proposé**, pas exécuté. Une revue plus chère que ce qui est demandé (modèle supérieur, tier deep, plus de 5 relecteurs) : annoncer le coût estimé et demander, même si la phrase dit « en boucle ». Un modèle demandé mais indisponible : le dire en une ligne et prendre le suivant.

## 2. Trivial ou pas

**Trivial** = correctif localisé, sans changement de contrat ni d'écran (libellé, garde d'une ligne, typo de config). Alors :
- pas d'agent `Plan`, pas d'exécutant : la session principale corrige elle-même ;
- test rouge seulement si c'est un bug reproductible ;
- pas d'e2e, sauf si un défaut que seul le navigateur voit est en jeu (champ affiché, unité, devise, rendu) : le nommer, sinon le dire superflu ;
- une revue rapide (`/senior-review --quick`) une fois, puis § 6.

Tout le reste suit le déroulé complet. Dans le doute, annoncer le choix en une ligne et continuer.

## 3. Déroulé complet

### 3.1 Lire le ticket ET le code qu'il touche
- Lire le ticket **avec ses commentaires** (`glab issue view N --comments`, `gh issue view N --comments`) : les décisions prises après coup y sont. Une consigne orale qui contredit le ticket : réécrire le ticket et la description de MR avant de coder.
- Lire le code sur la **base à jour** (`git fetch`, comparer à `origin/<branche par défaut>`, jamais une branche locale périmée).
- Un ticket décrit une intention datée : chercher si une partie est déjà faite ailleurs (`grep` du symbole, `git log -S`). Une mesure qui invalide un point du ticket : ne pas le coder, écrire pourquoi dans la MR.
- Avant de créer une surface (route, table, colonne, type), prouver par une commande qu'elle n'existe pas, côté producteur et côté consommateur. Avant de changer un comportement, lire le nom des tests qui le couvrent : un comportement nommé est un comportement décidé.
- Bug ou perf : **reproduire et mesurer avant** de proposer un correctif.
- Lire la mémoire projet sur la zone touchée (gotchas, métriques d'appareil réel, harnais e2e).

**Fini quand** : le périmètre réel est écrit en 3 lignes, avec ce que le code fait déjà.

### 3.2 Hypothèses et critère de succès
Énoncer les hypothèses et transformer le ticket en **cible testable** : quel test rougit aujourd'hui, quelle capture doit montrer quoi. Plusieurs lectures possibles du ticket : les présenter, ne pas en choisir une en silence. Une décision qui touche le produit se pose en conséquence concrète pour l'utilisateur final, avec un défaut recommandé et le coût d'y revenir.

### 3.3 Plan (agent fort)
- `Agent` type `Plan`, sur le modèle choisi au § 1, brief : ticket, périmètre de 3.1, critère de 3.2, contraintes du dépôt (CLAUDE.md). Demander : étapes, fichiers, tests rouges à écrire d'abord, cas limites, ce qui n'est **pas** dans le périmètre.
- Le plan rendu par l'agent s'écrit dans un fichier ; c'est ce chemin qu'on passe à l'exécutant. Si la demande le prévoit, le recopier dans la description du ticket.
- La session principale ne refait pas le plan : elle le relit contre le code de 3.1 et corrige ce qui contredit un fait mesuré.

### 3.4 Test rouge d'abord, au plus près du réel
- Choisir le niveau le plus haut qui attrape le défaut : unitaire < intégration sur vraie base < e2e contre le serveur réellement démarré.
- **E2E rejouable** : un scénario qui touche un écran devient un test **dans le harnais e2e du projet** (spec ou module existant, lancé par sa commande habituelle), committé sur la branche du ticket. Une sonde jetable aide à explorer ; elle ne sert jamais de preuve et ne se commit pas.
- **Captures** sur les écrans touchés, aux tailles par défaut : mobile **390×844**, tablette **820×1180**, desktop **1280×900**. Si la mémoire du projet porte des métriques relevées sur l'appareil réel, elles remplacent la taille par défaut. Un profil d'appareil Playwright reproduit le moteur, pas l'appareil.
- **Mobile = profil d'appareil** (`devices["iPhone 15"]` : tactile, user-agent, densité), jamais un simple redimensionnement. Écran visé iPhone : **WebKit** en plus de Chromium (un `calc-size()` passe dans l'un, pas dans l'autre). Un débordement se mesure contre `screen.width`, car Chromium émulé élargit `innerWidth` sur une page qui déborde. Ce que WebKit sous Linux ne montre pas (barre d'adresse iOS et `100vh`, `safe-area-inset`, zoom des champs) s'écrit dans la MR comme non vérifié.
- **La preuve se lit en rapport chiffré** : un script Playwright qui pose ses écouteurs (console, `pageerror`, réponses en erreur) **avant** `goto` et rend un JSON, quelques centaines de tokens, plutôt qu'un arbre d'accessibilité MCP à plus de dix mille. Si `feature-loop` est installé avec `scripts/probe-viewports.mjs`, l'utiliser au lieu de le réécrire (lancé depuis le projet, `--storage-state` pour une page connectée). Le script complète le scénario e2e du harnais, il ne le remplace pas.
- **Ce qu'un script improvisé rate** (mesuré : écrit à la volée, il n'a lancé que Chromium et manqué un défaut sur deux) : lire d'abord le CSS de l'écran et ajouter une largeur de part et d'autre de chaque breakpoint (un texte coupé entre 700 et 900 px échappe aux trois tailles fixes) ; cliquer chaque contrôle touché, `pageerror` à l'écoute (une erreur au clic n'existe pas au chargement) ; relever les cibles tactiles sous 44 px. Un clic qui expire seulement en Chromium iPhone signale une page qui déborde, pas un test instable : WebKit et Firefox cliquent.
- **Le rapport n'affirme que ce qu'il a mesuré** : « aucune requête en échec » seulement si le compteur existe et vaut 0, une cause se cite en `fichier:ligne` ou reste une hypothèse. Une passe MCP exploratoire ne prouve aucune absence (de 3 à 8 défauts sur 8 trouvés selon le run).
- Un double (mock, faux serveur) ne fabrique pas une forme d'erreur que le vrai client ne produit jamais : la traduction d'une erreur se teste là où sa vraie forme existe (serveur de test, vraie chaîne).
- Un champ lu avec repli : couvrir les deux branches par des données fabriquées, pas par celles que le dépôt contient par hasard.
- Une capture qui ne peut pas être produite fait échouer le test.
- Le test s'exécute et **rougit pour la bonne raison** avant toute ligne de code (garder la sortie).
- Un test qui doit prouver un **délai** (debounce, timeout) espace ses évènements, sinon une rafale synchrone tient dans une seule tâche et la mutation « délai à 0 » survit.

**Fini quand** : la sortie rouge est conservée et son message nomme le défaut visé.

### 3.5 Exécution déléguée (agent standard)
Un `Agent` `general-purpose`, `model: sonnet` (ou le modèle demandé). Le brief n'hérite de rien, il contient :
- le chemin du plan, les fichiers autorisés, les commandes de test et de gate du dépôt ;
- l'ordre TDD : test rouge montré, puis code, puis vert ;
- les interdits, écrits en clair : ne pas lire `.env*` (sauf `.env.example`), ni `git add`/`commit`/`checkout`/`stash`, rien en prod, aucune écriture hors du dépôt, aucune action refusée à la session principale ;
- commentaires : zéro par défaut, une ligne en anglais simple pour un pourquoi non déductible, aucun numéro de ticket ;
- pas d'interface ni de paramètre ajouté pour les seuls tests ;
- les pistes données sont des amorces, le rendement attendu est dans ce qui n'est pas listé ;
- réponse en 5 lignes : ce qui a changé, les commandes lancées et leur résultat réel.

Écran par écran : un écran, son test et sa capture avant le suivant. Les correctifs suivants repartent au **même** exécutant (`SendMessage`), il garde son contexte. Jamais deux agents qui modifient le même module en parallèle.

### 3.6 Vérifier soi-même, jamais sur parole
- `git diff --stat`, puis lecture ciblée du diff. Supprimer les sondes jetables restées dans l'arbre.
- Relancer **soi-même** la gate du dépôt une fois, en fin de lot : build, lint, tests des paquets touchés, suite large (des tests anciens peuvent encoder le bug : les inverser sur le nouveau contrat, jamais les neutraliser).
- Une gate verte dit ce qu'elle a exercé (nombre de tests) : ne jamais tronquer sa sortie par `head`, filtrer les lignes `ok`/`FAIL` et compter les deux.
- **Mutation inverse** : annuler le correctif doit faire rougir le test **sur une assertion**, pas à la compilation. Copier le fichier hors du dépôt, muter, restaurer par `cp`, vérifier par `diff -q`. Jamais `git checkout -- <fichier>` sur un fichier non commité : il efface le correctif avec la mutation.
- **Live** : relancer l'application sur le code à jour (un serveur qui garde l'ancien binaire valide du vieux code), aligner le schéma de la base de travail, dérouler le chemin, lire réponse et logs.
- **Lire chaque capture une fois**, comme l'utilisateur final : chiffre incohérent, accent cassé, état intermédiaire, bouton qui déborde. Tout écart devient un test rouge avant correctif.
- Un défaut trouvé sur un écran : auditer son écran jumeau (même flux, autre variante) avec ce défaut comme piste.
- Si le plugin `frontend-design` est installé, l'utiliser pour juger le rendu quand le ticket change un écran.

**Fini quand** : gate verte relancée par la session principale, mutation inverse rouge, e2e verts, captures lues.

### 3.7 Boucle de revue
- `/senior-review --loop`, relecteurs sur le modèle fixé au § 1 (le dire dans les arguments). Cible = le working tree non commité.
- Le brief des relecteurs leur interdit de modifier les sources ; après chaque tour, comparer `git diff --stat` à l'état laissé. Sans `senior-review` : un relecteur frais en lecture seule par tour (agent `Explore` ou équivalent), même règle d'arrêt.
- Un bloquant ou un important : correctif par l'exécutant, puis tour suivant sur le delta. Un finding qui change la conception repasse par un plan court.
- **Pas de tour suivant tant qu'un important du tour précédent reste ouvert.**
- **Arrêt** : premier tour sans bloquant, sans important ouvert, **et sans modification du code de production**. Un delta qui ne touche que des tests clôt la boucle seulement si une mutation exécutée prouve que ces tests attrapent le défaut ; sinon le tour est dû. Annoncer la sévérité tour par tour (bloquant, important, mineur, rien) plutôt qu'affirmer « fini ».
- Livrable avec un mode d'emploi (runbook, script, README) : un dernier tour aveugle « je suis un autre dev, sur ma machine, je suis le mode d'emploi », sur un autre modèle que l'auteur.
- Au **tour 5** sans convergence : s'arrêter et remonter à l'utilisateur l'état, le coût cumulé et ce qui ne converge pas.
- Les findings des relecteurs se vérifient dans le code avant d'être appliqués ou relayés.

**Fini quand** : le dernier tour n'a rien changé, et le rapport dit le nombre de tours.

## 4. Les preuves annoncées

Dans le rapport, distinguer en une ligne chacun :
- **le code est juste** : quels tests, rouges puis verts, et la mutation inverse ;
- **l'effet est visible** pour l'utilisateur final, et sous quelle condition ;
- **le décor** : ce que le parcours a réellement déroulé, ce qui était fabriqué (état de départ en base, réponse d'API simulée) et ce qui reste non exercé, avec la raison.

« Testé » sans ces trois lignes est une affirmation non prouvée. Une tâche de fond s'annonce au passé, après l'appel.

## 5. Étape humaine

Cookie de session, SSO, MFA, accès à un environnement : le demander **dès que le besoin apparaît**, avec la marche exacte (commandes dans la syntaxe du shell de l'utilisateur), au lieu de contourner. En autonomie (« fais au mieux »), garder les questions pour ce qui change le livrable ; les arbitrages techniques secondaires s'annoncent, ils ne se soumettent pas.

## 6. Livraison

- **Commit** : seulement si la phrase de lancement l'autorise, et seulement quand § 3.6 et § 3.7 sont tenus. Sinon `/branch-wrap-up --no-review` (si disponible) propose le bloc commit. Message dans le style du dépôt (`git log --oneline -20`), en respectant les règles de l'utilisateur sur l'attribution (CLAUDE.md). L'autorisation couvre ce ticket, pas le suivant. Vérifier la branche courante (`git rev-parse --abbrev-ref HEAD`) juste avant, et lire la MR d'une branche existante avant d'y ajouter un travail sans rapport. Commit à valider par l'utilisateur : présenter le diff hunk par hunk (changement, motif, preuve), pas par thème.
- **Push** : jamais chaîné au commit dans la même commande ; vérifier la branche courante avant, et que sa MR n'est pas déjà mergée (un push après un merge en squash ressuscite la branche). Après : `git ls-remote origin <branche>`.
- **MR/PR** : reste en draft jusqu'à ce que tout soit tenu, puis sortie du draft (pas pour une MR empilée sur une MR non mergée). Jamais de merge.
- **Description de MR** : sections « Livré » et « Tests » ; captures jointes quand un écran change ; constats hors périmètre dans « Suites connues (pas dans cette MR) », impact mesuré, plutôt qu'un ticket par constat. Un ajustement adjacent né de la recette va dans la même MR.

## 7. Rétrospective (proposer, l'utilisateur valide)

Source : **les corrections de l'utilisateur pendant ce ticket** (« tu as testé ? », « tu es sûr ? », « pourquoi tu t'es arrêté ? ») et les pièges rencontrés. Chaque correction révèle une règle qui manquait.
- Au plus 3 lignes, chacune avec sa destination : CLAUDE.md du projet, mémoire `feedback`/`project`, ou ce skill.
- Filtre : non déductible du code, se reproduira, absent de la mémoire (`grep` avant de proposer). Le mécanisme, pas l'état daté de la MR.
- Une ligne destinée à ce skill reste générique : aucun nom de client, de produit, de service ni de chiffre interne, car le skill peut vivre dans un dépôt public. Ce qui ne se généralise pas va en mémoire projet.
- Écrire seulement après son accord. Une écriture refusée sur un fichier de skill ou de config : donner la ligne à coller, ne pas contourner. Rien à retenir : le dire en une ligne.

## 8. Checklist de fin de ticket

- [ ] Périmètre réel mesuré dans le code, pas recopié du ticket
- [ ] Test vu rouge avant le code, vert après, mutation inverse rouge sur une assertion, fichier restauré par `cp`
- [ ] Scénario d'écran dans le harnais e2e du projet, captures aux trois tailles lues une fois
- [ ] Gate du dépôt relancée par la session principale, nombre de tests exercés lu ; application relancée sur le code à jour
- [ ] Boucle de revue : dernier tour sans bloquant, sans important, sans modification de production
- [ ] Rapport : code juste, effet visible, décor et non-exercé, nombre de tours, coût
- [ ] Commit et push seulement sous autorisation ; MR sortie du draft seulement si tout est coché
- [ ] Rétrospective proposée, rien écrit sans son accord

---

## CHANGELOG
Historique complet : `CHANGELOG.md` (à côté de ce fichier). Version courante : **1.1.0**.
