## Étape 6.5 — Boucle (mode `--loop` uniquement)

Le mode boucle a **un seul critère d'arrêt, et il porte sur le delta, pas sur le rapport** :

> On boucle tant qu'un tour a **modifié du code**. On s'arrête au premier tour qui ne remonte **aucun bloquant** ET **ne produit aucune modification**.

Ce qui est interdit de conclure : « ce tour n'a plus de bloquant, donc c'est fini ». Un tour qui corrige **crée du code que personne n'a jugé**, et son auteur est l'orchestrateur — le juge le plus mal placé pour l'évaluer (principe reviewer ≠ auteur). Tant qu'une ligne a bougé, il reste un delta non relu : c'est ce delta qui décide s'il faut un tour de plus, pas la sévérité du tour écoulé.

**Pas de tour N+1 tant qu'un 🟡 important du tour N reste ouvert.** Chacun est corrigé (il entre alors dans le delta), tranché par l'utilisateur ou routé (ledger, Étape 7) : le tour suivant ne relit que le delta, un important laissé ouvert n'y serait revu par personne.

Le tour N+1 en pratique :
1. **Cible = le delta**, pas la branche entière : le diff des correctifs du tour N (contre un instantané pris avant eux — pas contre `HEAD` si l'arbre porte du travail non commité).
2. **Reviewers frais et aveugles**, jamais les mêmes agents relancés : une continuation coûte autant qu'une passe neuve et arrive avec l'ancrage du tour précédent. Deux dimensions suffisent en général (correctness+sécurité du delta ; tests du delta) — proportionner au volume du delta, pas à celui de la branche.
3. **Le brief inverse la question** : non pas « ce correctif corrige-t-il ? » (déjà prouvé par mutation) mais « **que casse-t-il, qu'oublie-t-il, que surcorrige-t-il ?** ». Lister explicitement les correctifs et ce dont chacun est soupçonné.
4. **Chaque correctif se prouve par mutation inverse** : annuler le correctif doit faire rougir un test. Un correctif sans test qui meurt à son annulation n'est pas fini — c'est le seul signal externe qui distingue « corrigé » de « corrigé en apparence ».
4b. **Retirer ou affaiblir un test se prouve par mutation avant d'être fait** (`scripts/mutate.py`) : muter le comportement qu'il garde dans une copie ; s'il est le seul à rougir, il reste. Quand deux tours se contredisent sur ce point (« retire-le » puis « il garde un trou »), la mutation tranche, pas un avis.
5. Les décisions **tranchées** par l'utilisateur et les **receipts déjà payés** passent au ledger (Étape 7) et ne se re-litigent pas.

Terminaison et honnêteté du décompte : le rapport final d'une boucle dit **le nombre de tours**, ce que chaque tour a trouvé, et **ce que le dernier tour n'a pas changé**. Une boucle annoncée close avec un delta non relu est un rapport faux, quelle que soit la couleur du gate. Pareil avec un 🟡 important resté ouvert : la boucle ne se clôt pas dessus, il est corrigé, tranché ou routé d'abord. À partir du **tour 3**, ajouter une ligne de coût cumulé (agents, tokens) au rapport — la boucle reste due, l'utilisateur reste informé de ce qu'elle coûte.

Garde-fous : un bloquant qui survit à deux tours sans converger, ou deux tours qui se renvoient le même arbitrage, **remonte à l'utilisateur** au lieu d'un troisième correctif (déjà la règle pour un bloquant incertain). **Plafond : 5 tours.** Le tour 5 fini sans convergence, ne pas lancer le 6e : s'arrêter et remonter à l'utilisateur l'état (corrigé, prouvé, encore ouvert), le nombre total d'agents lancés depuis le tour 1 et ce qui ne converge pas (finding qui revient, correctif qui en appelle un autre). Le plafond se compte en tours et en agents, jamais en tokens ni en euros : la dépense n'est pas lisible en cours de run. Une modification qui n'est **que** du commentaire ou du renommage sans effet sémantique ne relance pas un tour complet : elle se vérifie par gate outils + relecture directe, et le rapport le dit.
