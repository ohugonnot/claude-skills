# vide-contexte, sous-commande `consolide` (propose-only, une fois par mois)

Déclenchée par `consolide` en premier argument, ou par « consolide la mémoire », « ménage de la mémoire ». C'est le seul moment où le skill retire ou fusionne : un passage ordinaire n'élague jamais, d'où ce rendez-vous. Rien ne s'écrit avant la validation de l'utilisateur.

## 1. Mesurer
`python3 <skill>/scripts/consolide.py` imprime le corpus face à ses plafonds, puis une liste **To decide**. Il couvre ce qui est mécanique : liens morts, liens qui ne se résolvent que par nom de fichier (un lien se résout sur le `name:` de la cible, jamais sur son fichier ; un contrôle par fichier a déjà rendu « 0 lien mort » sur un dossier qui comptait 5 liens morts et 15 liens par nom de fichier), lignes d'index orphelines, fiches sans `name:`, fiches de plus de 8 Ko, fiches à titres datés ou numérotés (« Passe 5 », « REPRISE »), et les références `!N`/`#N` à vérifier. Ne recompter aucun chiffre à la main : une métrique qui manque s'ajoute au script, avec son test.

Hors périmètre : les `arbitrages-*` (cycle de vie porté par senior-review, Étape 1.9) et `senior_review_learnings.md` (plafond tenu par `senior-review learn`).

## 2. Juger la péremption
Une fiche est périmée quand elle **fige un état** (MR « en review », « reste à faire », version, compte) que la forge ou le code ont dépassé, ou quand le code la **contredit**.
- État de MR ou de ticket : `glab api projects/:id/merge_requests/<N>` ou `gh pr view <N> --json state`, jamais de mémoire.
- Affirmation sur le code : `git show <ref>:<chemin> | grep`, sur la branche par défaut fraîchement fetchée. `git grep <ref>` peut rendre vide à tort : une absence se prouve par `git show`. Quand la fonctionnalité n'est pas encore sur la branche par défaut, juger sur la branche qui la porte et le dire.
- « Livré » n'est pas « mergé » : une pile de MR ouvertes n'est pas du code de la branche par défaut.
- Au-delà d'une trentaine de fiches, déléguer par lots de ~20 à 2 ou 3 agents de lecture (Explore, tier standard), chacun rendant fiche, verdict, quoi, preuve (commande + extrait), et qui la référence. Leur rapport est un candidat : recouper soi-même chaque verdict autre que « garder » avant de le présenter.

## 3. Doublons et journaux
- **Fusionner** deux fiches qui portent le même savoir, même avec des mots différents (chercher par mécanisme, pas par mot-clé). La cible garde son `name:` si d'autres fiches y renvoient.
- **Condenser** une fiche-journal en décisions, leur pourquoi et les pièges encore vrais. Le récit des passes, les SHA et les états de MR partent : git et la forge les portent.
- Une fiche dont le seul savoir est désormais dit par le code ou par CLAUDE.md sort.

## 4. Présenter, puis appliquer
Un tableau par catégorie : **supprimer** (pourquoi + preuve), **fusionner** (source → cible, ce qui survit), **mettre à jour** (quelle phrase), **garder** (en une ligne). Une seule validation pour le lot. Puis appliquer :
- sauvegarde du dossier avant la première écriture (`tar czf ~/.claude/backups/memory-<date>.tgz memory`) ;
- toute suppression ou fusion retire la ligne d'index (MEMORY.md ou `index_*.md`) et réoriente ou retire chaque `[[lien]]` qui la visait ;
- les mises à jour en place peuvent partir à un agent unique (jamais deux agents sur les mêmes fichiers), avec la liste exacte des corrections déjà validées : il applique, il ne re-décide pas.

**Fait quand** `consolide.py` relancé ne signale plus ni lien mort, ni lien par nom de fichier, ni ligne d'index orpheline, et que MEMORY.md tient sous son plafond.

Logger `[consolide] N fiches : S supprimées, F fusionnées, U mises à jour · liens réparés : L`.
