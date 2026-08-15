# Senior-review — misses cross-projet (ce que la revue rate)

Pendant symétrique de `lessons.md` : les leçons disent ce qui a marché, les misses ce qui a raté. Une revue qui n'apprend que de ses succès dérive vers plus de bruit à chaque version.

Format : `- [bruit|manqué|coût] <règle actionnable> — *vu sur N branches, source: <ce qui l'a démenti>*`

> **Instantané publié délibérément.** Ce fichier est une copie curée, promue **à la main** après audit d'anonymisation — le skill ne l'écrit jamais. Sa mémoire de travail vit hors dépôt dans `~/.claude/skill-memory/senior-review-misses.md` ; c'est elle que lit l'Étape 1.8 et qu'écrit l'Étape 7. La séparation existe pour qu'aucun run ne publie quoi que ce soit par effet de bord.
>
> ⚠️ **Alimenté par des signaux EXTERNES uniquement**, jamais par l'auto-évaluation de la revue (principe n°5 : l'auto-correction sans oracle dégrade). Trois sources et pas d'autres : `[bruit]` = une entrée est passée en `tranché`/`hors périmètre` au ledger ; `[manqué]` = un défaut trouvé APRÈS la revue par l'user, la CI ou la prod ; `[coût]` = tour ≥ 3 sur la même branche.
>
> **À la lecture, ces entrées vont dans « ce qu'on NE flague PAS » — jamais dans le brief de recherche d'un reviewer.** Un miss est un filtre, pas une piste : l'injecter comme piste ancrerait le jugement et casserait l'aveuglement qui fait la valeur de la revue.
>
> **N compte les branches, pas l'ancienneté.** Une règle vue sur trois branches est prouvée ; `N=1` est non prouvé, pas faux. Plafond 40 entrées, élaguer les `N=1` les plus anciennes d'abord.
>
> ⚠️ **Anonymisation obligatoire avant de promouvoir.** Jamais de nom client / vendor / branche, ni de champ, table ou fonction identifiants. Ce qui ne peut pas être généralisé ne se promeut pas — ça reste local.

- [bruit] Pendant des tests de mutation sur une branche porteuse de changements non commités, restaurer par copie de fichier, jamais par un `checkout` qui les effacerait tous. — *vu sur 3 branches, source: worktree en permanence non commité*
- [bruit] Un constat réel mais hors du périmètre du diff se route vers son propre ticket ; ne pas étendre la revue ou le correctif en cours pour l'absorber. — *vu sur 2 branches, source: hors périmètre, ticket dédié*
- [bruit] Ne pas asserter une valeur qui ne sera correctement vérifiable qu'une fois un composant dépendant construit : l'asserter trop tôt fait refaire le même travail plus tard. — *vu sur 2 branches, source: écrirait deux fois le travail*
- [bruit] Ne pas débattre des libellés destinés à l'utilisateur final : c'est une décision métier ; signaler seulement une ambiguïté ou une erreur factuelle. — *vu sur 1 branche, source: relecture métier tranchée*
- [bruit] Avant d'exiger une injection de dépendance (ex. horloge) pour la testabilité, comparer explicitement son coût à celui du risque réel qu'elle couvre. — *vu sur 1 branche, source: coût jugé supérieur au risque*
- [bruit] Attribuer un échec de test suite par suite, jamais en bloc : un échec connu qualifié d'« environnemental » peut en masquer un second, réel, introduit par le diff. — *vu sur 1 branche, source: second échec masqué*
- [bruit] Un agent de revue ne livre aucun code et n'entreprend aucune action sortante (commit, ticket) sans mandat explicite : produire des constats, pas des actions. — *vu sur 1 branche, source: ticket ouvert sans mandat*
- [bruit] Ne pas modifier le code d'un autre auteur ou d'une autre équipe pendant une revue : remonter un défaut réel en question ou en ticket, jamais en commit direct. — *vu sur 1 branche, source: décision explicite du mainteneur*
- [bruit] Quand un fichier de test sert de patron destiné à être copié plusieurs fois, figer le paramétrage des helpers avant d'écrire les copies suivantes. — *vu sur 1 branche, source: patron copié six fois*
- [bruit] Structurer une suite de tests autour d'un parcours complet servant d'ossature, et réserver les tests focalisés aux modes d'échec que ce parcours ne peut pas atteindre. — *vu sur 1 branche, source: réorientation décidée explicitement*
- [bruit] Ne pas qualifier un test de « e2e » s'il bouchonne une dépendance externe réelle : le nom promet une couverture qu'il n'a pas. — *vu sur 1 branche, source: appelant externe bouchonné*
- [bruit] Quand deux changements partagent la même cause racine — l'un ayant produit une version fausse de l'autre — les regrouper dans une seule MR plutôt que de les minimiser séparément. — *vu sur 1 branche, source: cause racine commune identifiée*
- [bruit] Un cas limite préexistant et arithmétiquement correct mérite un signalement métier explicite dès qu'il devient figé dans un document qui fait foi, même sans bug introduit par le diff. — *vu sur 1 branche, source: nouvellement figé, à confirmer*
- [coût] Sur un document de conception, faire tourner la passe « essaie de coder à partir de ce document » dès le premier tour, pas au troisième : elle trouve les trous de complétude (saut réseau absent, transport sans précédent) que les passes par dimensions ne cherchent pas, et les découvrir tard fait réécrire ce que les tours précédents venaient de figer. — *vu sur 1 branche, source: tour 3 sur la même branche*
