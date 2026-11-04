# migrations

- **migrations** (cond., diff qui touche `migrations/` ou un `.sql` de migration) : le schéma change sous des données et du code qui tournent déjà. Un comportement du moteur se prouve sur sa version réelle (doc officielle datée, ou essai sur une base jetable), jamais de mémoire.
  - **Index resté INVALID** : après un `CREATE INDEX CONCURRENTLY` échoué, `CREATE INDEX IF NOT EXISTS` voit le nom et saute l'index INVALID. Exiger une vérification de `pg_index.indisvalid`. Sur PostgreSQL 18, un index enfant INVALID s'attache au parent partitionné sans erreur, et le parent devient INVALID.
  - **Verrou sur un parent partitionné** : un `CREATE INDEX` non concurrent prend un ShareLock sur le parent et ses partitions, attend les écrivains en cours et fait la file devant les nouveaux inserts. Exiger `lock_timeout`, ou le motif `ON ONLY` sur le parent, index concurrent par partition puis `ATTACH PARTITION`.
  - **DDL séparé du backfill** : un `NOT NULL` ajouté sans défaut sur une grosse table est un finding.
  - **Code N-1** : la compatibilité avec la version précédente du code se juge selon le modèle de déploiement du dépôt, lu dans ses conventions ou ses learnings, jamais supposé.
  - **Test ancien/nouveau SQL** : il ne protège pas un filtre que la fixture ne rend jamais discriminant. Demander la mutation qui retire chaque filtre.
  - **Une instruction par fichier** quand l'outil envoie le fichier en une seule requête simple : `CONCURRENTLY` refuse de tourner dans un bloc de transaction, et plusieurs instructions dans une requête simple en forment un implicite.
