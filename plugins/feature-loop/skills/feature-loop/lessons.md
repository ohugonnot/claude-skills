# Feature-loop — meta-leçons cross-projet

Leçons sur *comment piloter la boucle*, valables sur tous les projets (pas les specs d'un projet — ça va dans `project_feature_loop_insights.md`). Chargé à l'init, complété en fin de run et par `learn`.

Format : `- **<titre>** : <règle actionnable> — *vu sur un run réel*`. Additif uniquement.

> ⚠️ **Anonymisation obligatoire avant commit.** Ce fichier s'accumule en local sur des projets réels, puis est versionné ici — dans un repo PUBLIC. Toute leçon commitée doit être **anonymisée** (« un projet réel », « une intégration fournisseur » — jamais de nom client / vendor / branche / champ métier identifiant). Ce qui ne peut pas être généralisé ne se commite pas.

## Leçons

- **Reprendre un reviewer via `to:`/SendMessage n'est pas fiable pour une re-notation ciblée** : sur un run réel, reprendre le juge d'origine pour re-noter un seul axe a produit une réponse plausible mais qui citait des commits/fichiers d'une feature sans rapport (déjà mergée dans l'historique du repo) — l'agent avait perdu le fil du diff exact et était reparti explorer le dépôt. Toujours vérifier les citations file:line d'une re-notation contre le diff attendu avant de l'accepter ; en cas de doute, relancer un agent frais avec le diff exact en commande plutôt que de faire confiance à la continuité de contexte d'un resume.
- **`git diff <base> -- <fichiers>` est silencieux sur les nouveaux fichiers non trackés** : un reviewer (ou la mère) qui vérifie un scope via cette commande verra "aucun changement" pour un fichier de test tout neuf jamais `git add`-é, alors qu'il existe et contient du contenu réel — à tort interprété comme "aucun test écrit". Toujours croiser avec `git status --porcelain` (entrées `??`) avant de conclure qu'un fichier attendu est absent du diff.
- **Une mini-review Haiku peut rejeter un plan à tort** : sur un run réel, Haiku a renvoyé `blocking: true` sur deux points qui étaient en fait déjà couverts par le plan (mal relus, pas absents). Avant de renvoyer systématiquement à l'agent de plan pour révision, la mère peut vérifier elle-même le point contesté sur le code réel — si le plan avait raison, documenter l'override plutôt que de payer un aller-retour de plan inutile.
