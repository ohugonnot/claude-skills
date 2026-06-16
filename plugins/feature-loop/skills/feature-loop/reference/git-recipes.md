# Recettes git — snapshots, restore, conflicts-check

Commandes verbatim sorties du SKILL.md (progressive disclosure). La **logique de décision** (quand appliquer quelle recette, garde `no_auto_commit`/`branch_created`, filets de sécurité) reste dans le SKILL.md aux étapes 4.2, 5.0 et 5.1bis. Ce fichier ne tient que le shell exact — le lire au moment d'exécuter ces étapes.

## 4.2 Mode 2 — snapshot pré-impl en mode `no_auto_commit`

Capture COMPLÈTE (tracked + untracked) dans un tree temporaire, sans toucher l'index réel de l'user, ancrée sur une ref technique hors-branche (gc-protégée) :

```bash
TMP_INDEX=$(mktemp -u)
GIT_INDEX_FILE="$TMP_INDEX" git add -A
TREE=$(GIT_INDEX_FILE="$TMP_INDEX" git write-tree)
rm -f "$TMP_INDEX"
pre_impl_sha=$(git commit-tree "$TREE" -p HEAD -m "feature-loop iter-N pre-impl")
git update-ref "refs/feature-loop/snap-iter-N" "$pre_impl_sha"   # ANCRE l'objet → gc-protégé
```

Avantages vs `git stash create` (rejeté car non-ancré donc gc-able, n'attrape pas l'untracked, et rend une chaîne vide sur arbre propre) : capture l'untracked (nouveaux fichiers de la feature), survit au gc (ancré à une ref), valide même à l'itération 1 sur arbre propre (le tree == HEAD donne un SHA valide). La branche de l'user n'est PAS modifiée (HEAD, index réel, `git log` intacts). Nettoyage en fin de run : `git for-each-ref refs/feature-loop/ | … git update-ref -d`.

## 5.0 — restaurer la meilleure version

Filet de sécurité d'abord (sauver l'état courant complet, toujours), puis restauration selon le contexte. JAMAIS de `checkout -- .`/`reset --hard` aveugle.

```bash
# Filet : sauver l'état courant complet (tracked+untracked) dans une ref technique, toujours.
git update-ref refs/feature-loop/safety-pre-restore \
    "$(TMP=$(mktemp -u); GIT_INDEX_FILE=$TMP git add -A; T=$(GIT_INDEX_FILE=$TMP git write-tree); rm -f $TMP; git commit-tree $T -p HEAD -m 'safety')"

if [ "$no_auto_commit" = "true" ]; then
    # snapshot = ref technique (4.2 Mode 2) : restaurer son tree sans toucher l'historique user
    git read-tree -u --reset "$best_iter_sha"        # met le working tree à l'état best, tracked ET untracked
elif [ "$work_mode" = "worktree" ] || [ "$branch_created" = "true" ]; then
    # branche jetable créée par le skill / worktree isolé → reset sûr (best = vrai commit)
    git reset --hard "$best_iter_sha"
else
    # IN-PLACE sur la branche COURANTE de l'user, mode commit : le best est un commit ancêtre.
    # Restauration = JAMAIS un reset qui jetterait un commit user intercalé. On crée une branche
    # pointant sur le best et on PRÉSENTE (la garantie "meilleure version" est tenue par une option claire).
    git branch -f feature-loop/best "$best_iter_sha"
    # → AskUserQuestion : "Meilleure version = iter K (branche feature-loop/best, radar X) ;
    #   la dernière (radar Y) est moins bonne. (1) merger feature-loop/best  (2) garder la dernière
    #   (3) voir le diff". Pas de restauration destructive d'office.
fi
```

La ref `refs/feature-loop/safety-pre-restore` permet de revenir en arrière si la restauration ne convient pas.

## 5.1bis Mode 2 — conflicts-check sans commit (`no_auto_commit`)

Estimer la mergeabilité POST commit user sans modifier le working tree :

```bash
git stash --keep-index --include-untracked  # snapshot des modifs unstaged
git add -A  # stage tout pour le merge-tree
# ... conflicts check (merge-tree, cf. 5.2) ...
git reset  # un-stage
git stash pop  # restaurer les modifs unstaged
```
