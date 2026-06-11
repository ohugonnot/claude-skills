---
name: book-distill
description: >-
  Lit un livre (PDF ou EPUB) et produit une fiche de lecture markdown fidèle et pédagogique :
  cartographie du livre, lecture ciblée, citations vérifiées mot à mot contre le texte,
  distillation thématique en idées reliées, note argumentée, contrepoints. Use whenever the
  user provides a book file or asks to summarize or distill a book — « résume ce livre »,
  « fiche de lecture », « extrais la substance », "book summary", "distill this book" —
  even if they never say the word « fiche ».
argument-hint: "[chemin-du-livre] [audience]"
---

# Book-distill — du livre à la fiche de lecture

Tu lis un livre (stratégiquement, pas page à page) et tu en distilles une fiche markdown qui transmet l'essentiel à quelqu'un qui ne le lira pas. Deux promesses non négociables :

1. **Fidélité** : tout ce que la fiche attribue au livre vient du livre, vérifié contre le texte. Une affirmation vraie dans le monde réel mais absente du livre est une erreur quand même (hallucination « extrinsèque » : le mode d'échec typique d'un modèle qui connaît déjà le sujet).
2. **Pédagogie** : la fiche construit la compréhension (exemple concret avant le principe, le pourquoi sous chaque affirmation, des idées reliées entre elles), elle ne liste pas des extraits.

Chaque règle ci-dessous existe pour une raison documentée : `reference/science.md` tient les justifications et leurs sources. Adapter une règle au contexte est permis ; la supprimer sans avoir lu sa justification ne l'est pas.

## Entrées

| Entrée | Défaut |
|---|---|
| Chemin du livre (PDF/EPUB) | obligatoire |
| Audience | lecteur curieux, néophyte du domaine du livre |
| Longueur cible | 1 200-2 000 mots (annoncer tout écart, avec la raison) |
| Langue de la fiche | celle de la conversation |
| Contexte personnel du demandeur avec le livre | optionnel, nourrit l'avis |

**Règle cardinale : sans le texte du livre, pas de fiche.** Une fiche écrite de mémoire d'entraînement est générique, sans exemples réels, et truffée d'attributions invérifiables. Fichier introuvable → STOP, demander le chemin.

## Phase 0 — Préparation

1. Lire `lessons.md` (même dossier) : les pièges connus, classés par thème.
2. Vérifier l'outillage : `pdftotext -v` (poppler-utils). Un EPUB se traite directement (`unzip` + strip des balises : texte plus propre, frontières de chapitres gratuites).
3. Localiser le fichier (`ls`, sinon `find`).

## Phase 1 — Cartographier avant de lire

C'est le *systematic skimming* d'Adler (How to Read a Book) : construire la carte AVANT de lire. Sans carte, on lit linéairement et on sur-pondère le dernier tiers lu (biais mesuré chez les LLM ; les chapitres du milieu sont aussi structurellement sous-couverts si on avale tout d'un bloc : « lost in the middle »).

1. Extraire les premières pages : titre, copyright, préface, table des matières.
   ⚠️ L'édition s'identifie par le **contenu** (features couvertes, dédicace, chapitres ajoutés ; croiser DEUX marqueurs), jamais par les métadonnées du fichier, qui mentent souvent.
2. Lire la **préface ET la conclusion** en entier : c'est là que l'auteur formule lui-même sa thèse, et la phrase-thèse de l'auteur bat toujours la thèse populaire du livre (Beck : « TDD is a way of managing fear », pas red/green/refactor).
3. Construire la carte des chapitres (numéro, titre, pages), puis trier en trois classes :
   - **A (cœur)** : porte la thèse → lecture complète ;
   - **B (support)** : 2-3 premières pages + conclusion du chapitre (les premières phrases de paragraphes suffisent souvent) ;
   - **C (skip)** : études de cas interminables, annexes → 1 page pour confirmer, puis passer.
4. Budget : **80-140 pages lues pour un livre de 300-500 pages** (proportionnellement plus de skip au-delà). Moins de 60 = pas de substance ; plus de 180 = du temps perdu.
5. **Annoncer le plan de lecture à l'utilisateur avant de lire** : « je lis X pages sur Y ; A = …, B = …, C = … ».

Les 4 questions d'Adler structurent la fiche : de quoi parle le livre (→ une-phrase) ; que dit-il en détail (→ les idées) ; est-ce vrai (→ avis + contrepoints) ; et alors (→ pour qui).

## Phase 2 — Lire et prendre des notes

Extraire par tranches : `pdftotext -f N -l M` (~600 tokens/page). Pour chaque chapitre lu, noter dans un fichier de travail `/tmp/distill-<slug>-notes.md` :

```
## Ch. N — Titre (pages X-Y, classe A/B/C)
- Idée centrale : (1-2 phrases)
- Exemples marquants : (noms, métaphores, anecdotes DU LIVRE, avec leurs chiffres)
- Citation courte : "…" (p. N) — ≤ 25 mots, recopiée EXACTEMENT
- A vieilli ? : oui/non + pourquoi
```

**Règles de fidélité (non négociables) :**
- **Verbatim d'abord** : extraire les passages exacts AVANT de synthétiser, et ne synthétiser qu'à partir d'eux (c'est la pratique anti-hallucination documentée n°1 pour les documents longs).
- Toute citation est recopiée du texte, avec sa page (le numéro **imprimé** sur la page, jamais un offset calculé : l'offset varie à l'intérieur d'un même PDF). Pas de folio fiable → citer par `(ch. N)`.
- Ce qui vient de toi (critique, mise en contexte) ira dans l'avis et les contrepoints, jamais présenté comme venant du livre.
- **Quota anti-biais de fin** : au moins une note par chapitre de classe A, y compris les premiers lus. Le fichier de notes couvre tous les chapitres A de façon équilibrée.

**Scanning ciblé (livres techniques)** : la substance n'est pas dans la prose mais dans (1) les exemples de code nommés, (2) les encadrés warning/pitfall, (3) les aveux et nuances de l'auteur (« aucune recherche n'étaye », « we were wrong » : ils font un avis infiniment plus fin), (4) les annexes-résumés. Les chercher activement avec grep sur le texte extrait.

**Fan-out (optionnel, pour les gros livres)** : déléguer des groupes de chapitres à des sous-agents avec le contrat `templates/agent-lecteur.md` (l'adapter, ne pas le réinventer ; calibrer la concurrence sur la machine). Garder pour toi la préface, la conclusion et le chapitre-thèse. Sur un livre normal, lire séquentiellement soi-même est souvent plus simple et meilleur.

## Phase 3 — Distiller

**Construire, ne pas tronquer.** Un bon résumé applique trois macro-règles (Kintsch & van Dijk) : supprimer le trivial, généraliser (remplacer des cas par leur principe), et **construire** des phrases nouvelles qui subsument plusieurs passages. Le marqueur du résumé expert (Brown & Day) : la proportion de phrases qui n'existent dans aucune phrase du livre. Le copy-delete (recopier en raccourcissant) est le marqueur du novice.

- **Organisation thématique, pas chapitre par chapitre** : 5 à 9 idées, chacune avec un titre qui porte l'idée (jamais « Chapitre 4 ») et UN exemple concret du livre.
- **Relier les idées entre elles** (« cette idée découle de la précédente parce que… ») : sélectionner les meilleurs passages sans les relier détruit précisément ce que le lecteur doit retenir, les connexions.
- **Contrôle de couverture** : comparer la table des matières à la liste des idées. Tout chapitre A absent de la fiche est soit couvert, soit écarté explicitement avec sa raison.
- Chiffres : recopier la nuance AVEC le chiffre (« 30 % plus lent… pour une fonction triviale ») ; citer les chiffres datés avec leur date, jamais modernisés en douce.

## Phase 4 — Juger (seulement après avoir compris)

Règle d'Adler : on n'a le droit de dire « d'accord / pas d'accord » qu'après avoir pu dire « je comprends ». La note et la critique se produisent APRÈS les phases 1-3, jamais en parallèle.

1. **Note /10** , convention Sivers : « sur 10 lecteurs de l'audience visée, combien devraient lire ce livre ? ». Pas une note de plaisir.
2. **Sous-critères** (la note opaque ne s'argumente pas) : Idées / Applicable / Lisibilité / Actualité / Exemples, chacun justifiable par un élément précis du livre. Un profil tout à 8-9 est de la complaisance : le contraste fait la crédibilité.
3. **Contrepoints obligatoires** (2-3) : limites, contre-arguments, ce que le livre ignore, ce qui est contesté depuis. C'est le manque n°1 documenté des résumés commerciaux : condenser sans jamais juger. Chercher l'actualité éditoriale avant d'écrire (nouvelle édition ? thèse contestée ? techno citée disparue ?).

## Phase 5 — Écrire la fiche

Gabarit : `templates/fiche.md` (structure par défaut sensée ; adapter si le livre l'exige, en le disant). Écrire le draft dans `/tmp/distill-<slug>-draft.md`. Règles d'écriture, chacune avec sa raison :

1. **Ouvrir par un organisateur** : un chapeau qui ancre le livre dans ce que le lecteur connaît déjà, avant tout vocabulaire du livre.
2. **Concret avant abstrait** : pour chaque idée, l'exemple du livre d'abord, le principe ensuite. Jamais la règle abstraite seule (l'effet « exemples concrets » est un des mieux répliqués du champ).
3. **Le pourquoi mécanistique sous chaque affirmation** : un néophyte ne peut pas générer l'explication lui-même, la fiche la livre (« ça marche parce que… », la chaîne causale, pas le seul résultat).
4. **Vieux → neuf, phrase par phrase** : chaque phrase ouvre sur ce qui est déjà posé et ferme sur l'information neuve (contrat donné-nouveau, Clark & Haviland). Un passage « décousu », c'est presque toujours ça.
5. **Signaler la structure** : titres porteurs de l'idée, phrases-clés en gras, renvois explicites entre idées (levier texte le mieux chiffré : g ≈ 0.5 en rétention). Un titre est une promesse : la section doit l'encaisser (un titre « X fait moins peur » exige la phrase qui le démontre).
6. **Une citation vérifiée par grande idée**, avec sa page : valeur lecteur + preuve d'ancrage.
7. **Tout sigle décodé à sa première apparition ; tout terme technique suivi d'un exemple d'une ligne.**
8. **Embarquer du rappel** : 2-3 questions de récupération en fin de fiche (réponses repliées) + 1 prompt d'auto-explication dans le corps (« avant de lire la suite : pourquoi X échouerait-il si… ? »). La lecture seule crée une illusion de connaissance ; le rappel est la technique d'apprentissage la plus efficace documentée.
9. **Couper l'extraneous sans pitié** : zéro digression, zéro redite chapeau↔idée, zéro flourish. On ne « rajoute » pas de la bonne charge cognitive, on libère de la mémoire de travail. Un écho VOULU entre deux endroits emploie les MÊMES mots ; la paraphrase d'une idée déjà posée est une redite, pas un écho.
10. **Honnêteté de périmètre** : une section finale dit ce que la fiche ne remplace pas (« le chapitre X mérite la lecture intégrale parce que… ») et quelle édition a été lue, combien de pages, comment.
11. **Énumérations au point-virgule interdites** : trois propositions collées par « ; » ne racontent pas, réécrire en vraies phrases (souvent en escalade narrative). Exception : l'antithèse en deux volets, où le « ; » porte le contraste.
12. **Italique d'emphase interdit** : l'italique est réservé aux titres d'œuvre et aux termes étrangers. L'emphase rhétorique (le *et*, le *est*) est redondante avec le texte ; si le contraste manque, l'écrire en toutes lettres.
13. **Charge mémoire minimale** : jamais de référence que le lecteur doit résoudre (« le troisième temps » → le nommer : « le troisième temps : la vérification »), antécédent d'un pronom à une phrase maximum (deux noms du même genre en lice = répéter le nom), pas de « Et »/« Mais » nus en attaque de phrase (connecteur intégré : « Git, lui, … »). Le texte doit couler sans rien demander à retenir.

**Sorties courtes par section** : rédiger idée par idée, jamais la fiche d'un seul jet (la fidélité d'une génération longue se dégrade vers la fin, c'est mesuré).

## Phase 6 — Vérifier (boucle, pas checklist)

### 6a. Vérification des claims (mécanique, découplée)

- Découper la fiche en **affirmations atomiques** « le livre dit que X » (citations, exemples nommés, chiffres, attributions).
- Vérifier chacune contre le texte extrait : `python3 ${CLAUDE_SKILL_DIR}/scripts/check-claim.py /tmp/distill-<slug>-*.txt "fragment"` (**exécuter** le script, ne pas le réécrire : il normalise les artefacts de rip — césures, ligatures, apostrophes typographiques — avant de chercher ; un FAIL est une présomption, re-tester un fragment plus court avant d'accuser).
- Vérifier la claim seule contre sa source, **sans relire le raisonnement qui l'a produite** (la vérification découplée évite le biais de confirmation, c'est le principe Chain-of-Verification).
- Consigne explicite : *même vraie dans le monde réel, une affirmation que le livre ne contient pas est FAUSSE pour la fiche.* Introuvable → corriger ou supprimer, jamais garder « parce que ça sonne juste ».

### 6b. Auto-évaluation

| Critère | /points | Gate |
|---|---|---|
| Fidélité (claims vérifiées, citations avec pages, rien d'inventé) | /30 | une claim invérifiable conservée = STOP |
| Cœur du livre transcrit (la thèse de l'auteur, pas un tuto ni un best-of) | /20 | |
| Pédagogie (concret→abstrait, pourquoi mécanistique, vieux→neuf, sigles décodés) | /20 | |
| Couverture (chapitres A tous couverts ou écartés avec raison) | /10 | un A oublié = -5 |
| Jugement honnête (note contrastée justifiée, contrepoints réels) | /10 | |
| Forme (longueur tenue, structure signalée, questions de rappel) | /10 | |

### 6c. Correction ciblée

Score < 85 ou gate ouvert → identifier les critères faibles, corriger CES passages seulement, retour en 6a. Itérer jusqu'à ≥ 85 et zéro gate. Typique : 2-3 tours sur un premier livre.

**Toujours terminer par** : signaler que la note et l'avis sont des drafts que le demandeur doit relire et signer.

## Auto-amélioration

Après chaque livre : promouvoir tout piège réutilisable dans la bonne section de `lessons.md` (lu en Phase 0) ; garder ce fichier sous ~150 lignes en consolidant ; si une leçon contredit ce SKILL.md, proposer la mise à jour à l'utilisateur.
