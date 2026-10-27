# senior-review — sous-commande `learn` (propose-only, hors revue)

Déclenchée par `learn` en premier argument. C'est le seul moment où le journal et les candidates sont lus : jamais pendant une revue.

## 1. Mesurer
`python3 <skill>/scripts/learn.py` imprime les tables du journal et l'état des mémoires, puis une liste **À décider**. La table d'acceptation donne, par tier, ce que l'utilisateur a gardé des findings confirmés (corrigés sur corrigés + rejetés, les routés hors périmètre étant exclus ; seules comptent les lignes où corrigés et rejetés sont tous deux renseignés) : la précision mesure ce que passe le gate, l'acceptation ce que l'utilisateur retient. Deux flags s'y ajoutent : une acceptation sous 0,70 sur au moins 20 findings jugés (corrigés + rejetés), et les runs restés sans sort depuis plus de 14 jours. Une table par modèle de relecteur (au moins 10 runs) et un flag de plafond de fan-out (plus de 5 agents depuis la 1.16.0) complètent le tout. Ne recalculer aucun chiffre à la main : si une métrique manque, elle s'ajoute au script, avec son test.

## 2. Consolider les mémoires
Lire en entier `senior-review-lessons.md` et `senior-review-lessons-candidates.md` (environ 10k tokens, payés une fois par session `learn`, jamais par revue). Le script ne détecte pas les jumelles : deux entrées qui décrivent le même mécanisme ne partagent presque aucun mot (Jaccard mesuré ≤ 0,14).
- **Promouvoir** : deux candidates du même mécanisme, ou une candidate qui recroise une leçon, fusionnent en une leçon `vu sur N`.
- **Absorber** : une leçon que le SKILL.md énonce déjà sort de la mémoire. Le « vu sur N » n'a plus d'usage une fois la règle codifiée.
- **Élaguer** ce que le script signale : candidates expirées (90 j) ou non datées, misses vues une fois depuis plus de 60 j, entrées trop longues à condenser (garder l'impératif, couper le récit).
- **Learnings du dépôt courant** (`senior_review_learnings.md`, plafond 15 Ko) : lancer `learn` depuis le dépôt concerné. Au-delà du plafond, retirer les sections « Run <date> » et « Promu de ledgers » en ne gardant que les faits qui tiennent encore, fusionner les doublons de sujet, couper dates, MR et tours. Un fait que le code dit déjà sort.
Présenter le lot en un seul `AskUserQuestion` (avant → après par fichier), n'écrire qu'après validation. Pas de bump de version : c'est de la mémoire, pas du contrat.

## 3. Proposer sur le SKILL.md
Au plus **3 propositions**, chacune motivée par une ligne de la liste **À décider** ou une table, via `AskUserQuestion` avec le diff exact (old → new).
- **Sections LOCKED interdites** (`<!-- LOCKED -->`) : décision humaine directe uniquement.
- **Jamais d'affaiblissement d'un garde-fou** (retirer une gate, un panel, une preuve) : le signaler avec le chiffre, la décision reste humaine.
- Une proposition validée bumpe `skill_version` (patch : formulation ; minor : étape, flag, métrique) et ajoute une entrée en tête de `CHANGELOG.md`.

Logger `[learn] journal: N runs · mémoires: X promues, Y élaguées · SKILL.md: M proposées, K validées`.
