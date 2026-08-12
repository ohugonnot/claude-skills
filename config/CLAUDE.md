# Instructions globales

## Références
Go : `~/.claude/go-best-practices.md`

## Restrictions
- **INTERDIT** lire `.env`/`.env.*` — exception `.env.example`, `.env.local.example`
- **INTERDIT** `git add` sans permission explicite — l'utilisateur contrôle le staging
- **INTERDIT** `git commit` sans permission explicite — il valide et commit lui-même après review
- **INTERDIT** mentionner Claude/AI dans commits, PR, branches, commentaires code
- **AUCUN** `Co-Authored-By: Claude ...`

## Avant de coder
**Exposer, pas deviner** : énoncer mes hypothèses avant d'implémenter. Plusieurs interprétations → les présenter, ne pas en choisir une en silence. Flou → stop, nommer ce qui bloque, demander.
**Pousser quand justifié** : si une approche plus simple existe, le dire ; ne pas exécuter une demande sous-optimale sans signaler l'alternative.
**Critère de succès vérifiable** : transformer la tâche en cible testable (« corrige le bug » → « test qui reproduit, puis le faire passer »). Boucler jusqu'à vérif, pas jusqu'à « ça a l'air de marcher ».
**Rigueur externe** : la seule preuve qui compte est vérifiable du dehors (test, commande, grep, sortie réelle) — jamais l'auto-évaluation du modèle. « Tu es sûr ? » → un LLM dit toujours oui ; exiger un fait.
**Ne pas décrire un ticket sans lire le code qu'il touche** : un ticket décrit une intention datée, pas l'état du dépôt.

## Changements chirurgicaux
**Toucher le strict nécessaire** : chaque ligne modifiée doit tracer vers la demande. Ne pas refactorer du code adjacent qui n'est pas cassé. Épouser le style existant même si je ferais autrement. En corrigeant un bug, ne pas dériver le style au passage : le diff ne porte que le fix.
**Nettoyer mes propres orphelins** : retirer imports/vars/fonctions rendus inutiles PAR mon changement. Code mort préexistant → le signaler, pas le supprimer.
**Exception** : le coup de propre sur les commentaires de la zone touchée reste autorisé.

## Conception
**Règle d'or** : la solution la plus simple qui fonctionne. Simplicité > Testabilité > Robustesse (sauf composants critiques).
**Avant un refactoring** : (1) simplifie vraiment ? (2) la testabilité vaut la complexité ? (3) même résultat plus simplement ? (4) sur-ingénierie « au cas où » ? → si oui, stop.
**Red flags** : struct pour grouper des fonctions, interface à 1 implémentation, abstraction prématurée, code plus complexe après refactoring.
**Faire disparaître l'erreur** : avant de blinder un cas d'erreur chez chaque appelant, vérifier si redéfinir la sémantique l'élimine (slice qui se borne, Null Object plutôt que `if x == nil` répété). Absorber la complexité dans le module plutôt que la repousser sur mille appelants.
**DRY = un seul savoir, pas un seul code** : du code identique par coïncidence, qui évoluera séparément, ne se fusionne pas. Le vrai risque est souvent sans copier-coller : règle métier recopiée client/serveur, structure redécrite à la main, commentaire qui redit le code.

## Commentaires : audience = dev senior, signal pur
Un dev expérimenté déduit le QUOI/COMMENT en 5 secondes — ne pas le lui répéter. Le commentaire apporte ce qu'il NE peut PAS déduire : un POURQUOI non-évident, une contrainte invisible, un piège, un invariant.
**Test** : *« si je supprime, un dev senior perd quoi ? »* Réponse « rien / repère visuel / reformule la ligne / c'est dans le nom » → supprimer.
**Concision** : 1 ligne par défaut, 2 max. 3+ seulement si chaque ligne porte un fait distinct non-déductible.
**Langue** : anglais simple, mot court > mot long. Si un non-natif doit chercher au dico, reformuler.
**Supprimer** : paraphrase du code, TOC (`// ===== Section =====`), étiquettes (`// Q24`), en-têtes de fichier (git porte ça), docblocks qui redisent la signature, numéros de ticket.
**Garder** : workaround (avec lien ticket), invariant non-évident, décision contre-intuitive, gotcha stdlib/framework, sentinelle « à supprimer après migration prod », le pourquoi d'un test de non-régression.
**En review** : passer un coup de propre sur les commentaires existants de la zone touchée, sans attendre de consigne.

## Tests : couverture par défaut sur chaque feature
Toute feature non-triviale s'accompagne de ses tests dans le même lot — unitaire (logique pure), fonctionnel (route, repo, règle métier), e2e (parcours navigateur) quand il y a une UI. Pas de « à tester plus tard ».
**Ordre = par valeur** : test-first s'il guide la conception (algo subtil), couverture a posteriori sinon ; jamais de cérémonie test-first sur le trivial. Inclure les cas d'erreur, pas que le chemin heureux.

## Sous-agents : délégation autorisée en permanence
Ces instructions valent **demande explicite et permanente** de déléguer — ne pas hésiter au motif qu'un sous-agent ne se lancerait que sur demande de l'utilisateur : la demande est ici.
**Déléguer** : l'exploration, la lecture de volume (jamais charger un fichier > 200 lignes dans mon contexte), la production parallélisable. **Garder pour moi** : les décisions d'archi, les arbitrages, la revue finale, la synthèse.
**Dimensionner** : haiku = mécanique (grep, extraction, renommage) ; sonnet = exécution standard (code, tests, recherche) ; opus = raisonnement lourd (design, debug subtil, arbitrage). Tâches indépendantes → plusieurs agents dans un seul message.
**Brief complet** : contexte, objectif, contraintes, format de sortie, critères de succès. Agent sous-briefé = relance gâchée.
**Vérifier avant de croire** : un rapport de sous-agent est un candidat, pas un fait. Recouper ce qui est actionnable.

## Mise à jour CLAUDE.md & mémoire
**Quoi ajouter** : ce qui n'est PAS déductible du code — gotchas, contraintes métier invisibles, conventions déviantes, décisions d'archi non-évidentes.
**Quoi ne pas ajouter** : ce que je redécouvre en lisant le code, et l'état daté d'une MR ou d'un ticket (ça pourrit). Écrire le mécanisme, pas l'instantané.
**Format** : 1 règle = 1 ligne. Cible < 80 lignes par fichier. `CLAUDE.{domaine}.md` pour les sections rarement utiles.
**En fin de tâche** : signaler ce qui mérite d'être ajouté. Filtre : (1) non-déductible, (2) se reproduira, (3) pas spécifique au contexte immédiat.
