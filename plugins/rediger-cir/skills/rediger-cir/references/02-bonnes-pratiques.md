# Bonnes pratiques de rédaction CIR

Synthèse de la doctrine MESR/BOFiP et des cabinets spécialisés (Ayming, Sogedev, Leyton, F.Initiatives, Myriad). Convergence forte sur les fondamentaux ; les tournures et proportions sont des pratiques de cabinet (à adapter).

## Sommaire

- [1. Démontrer l'incertitude scientifique (le nerf de la guerre)](#1-demontrer-lincertitude-scientifique-le-nerf-de-la-guerre)
- [2. État de l'art : méthode](#2-etat-de-lart-methode)
- [3. Démarche expérimentale et prototypes](#3-demarche-experimentale-et-prototypes)
- [4. R&D logicielle (l'administration est stricte)](#4-rd-logicielle-ladministration-est-stricte)
- [5. Do's & Don'ts](#5-dos-donts)
- [6. Feuilles de temps](#6-feuilles-de-temps)
- [7. Fidélité au système réel décrit (zéro hallucination de mécanisme)](#7-fidelite-au-systeme-reel-decrit-zero-hallucination-de-mecanisme)

## 1. Démontrer l'incertitude scientifique (le nerf de la guerre)

Sans verrou démontré → requalification en ingénierie classique ou en CII → hors CIR.

**Distinction à marteler :** *défi technique* = complexe mais solution connue ; *verrou* = l'état de l'art ne fournit aucune réponse au démarrage.

**Gabarit d'un verrou convaincant :**
> Verrou = [contrainte technique précise et **chiffrée**] + [pourquoi l'état de l'art n'y répond pas] + [conséquence si non levé].
> Ex. : « Maintenir un temps de réponse sous le seuil cible alors que le volume traité augmente d'un ordre de grandeur ; les approches documentées ne tiennent pas cet objectif à cette échelle sans dégrader la fiabilité ; sans cela le système est inexploitable en production. »

### Tournures à EMPLOYER
- « Les connaissances accessibles au démarrage des travaux ne permettaient pas de résoudre… » *(ancre l'incertitude dans l'état de l'art ET la date)*
- « Il n'existe pas de solution transposable à nos contraintes [X, Y, Z]. »
- « Les bibliothèques/outils existants présentent des limites non résolues sur [latence/scalabilité/cohérence]. »
- « Cette incertitude a imposé de formuler des hypothèses, de tester plusieurs approches et d'accepter qu'une partie des essais échoue. »
- « Les résultats intermédiaires de ces itérations ont orienté les travaux suivants. » *(boucle de rétroaction = marqueur R&D fort)*
- « À l'issue du projet, le verrou [Z] demeure partiellement non levé et nécessite de nouvelles investigations. »
- « conçu ex nihilo », « sans résultat connu d'avance », « objectifs a priori contradictoires ».

### Tournures à BANNIR
- « Cela n'existe pas sur le marché » / « pas de concurrent » → confond innovation produit et R&D fiscale.
- « Nous manquions de compétence / de budget / de temps » → aléa de gestion, jamais un verrou.
- Récit qui fait passer l'entreprise pour négligente : « mis en production sans pouvoir tenir les comptes », « le système ne fonctionnait pas » → cadrer le manque comme **limite de la méthode orthodoxe atteinte à l'échelle**, jamais comme défaillance de la société (un acteur régulé ne s'auto-incrimine pas).
- « Notre solution est unique » sans appui bibliographique → affirmation gratuite.
- Analyse concurrentielle à la place de l'état de l'art → rejet quasi systématique.
- Ne présenter que les succès → absence d'incertitude perçue → disqualification.

## 2. État de l'art : méthode

Ce n'est **ni une bibliographie ni une analyse de marché** : c'est la démonstration **datée** d'un *gap* dans les connaissances accessibles.

1. **Cibler** une question technique précise (3-4 mots-clés), pas un objectif business.
2. **Sourcer** large, y compris hors secteur : publications (Google Scholar, HAL, Scopus, IEEE Xplore, theses.fr), **brevets** (Espacenet/INPI, Google Patents — explicitement attendus ; révèlent solutions ET limites), normes (ISO/AFNOR), doc interne (tests échoués).
3. **Analyser** chaque source (~10 lignes) en se centrant sur **ses limites** (non-transposable, ne change pas d'échelle, perf insuffisante, hypothèse inapplicable).
4. **Dater** : sources antérieures au lancement ; privilégier < 5 ans.
5. **Conclure sur le gap** : « [A] est limité par [X], [B] ne couvre pas [Y], [C] présuppose [Z] absent de notre contexte. Aucune solution accessible ne permet donc d'atteindre [objectif] dans les conditions requises. »

**Quantité** : 5-10 références analysées en profondeur > 50 listées. ~3 pages sur 10. Chaque référence reliée explicitement à un verrou.

### Piège : le raisonnement à l'envers (anti-pattern critique)

**Logique correcte** : l'état de l'art révèle un gap → ce gap pose le problème → la R&D est justifiée.

**Logique à bannir** : on a un problème → on convoque la littérature pour le confirmer → ça justifie la R&D.

Patterns à détecter et corriger :
- « L'état de l'art le confirme : … (tel ou tel auteur) » dans la *question de recherche*, avant la section état de l'art → inversion : la littérature est convoquée en témoin à charge, pas analysée.
- « Ces travaux […] sans couvrir notre cas » → les limites de la littérature sont décrites à travers le prisme de l'entreprise, pas en termes généraux.
- « Reste à établir qu'aucune réponse n'existait déjà » → annonce rétroactive : le verdict précède l'analyse.
- « Notre problème est X, et la littérature ne le couvre pas » → le problème précède la littérature.

**Reformulation correcte** : nommer d'abord ce que la source *ne documente pas* (en termes généraux), puis noter que ce gap coïncide avec les conditions du problème. Les lacunes de la littérature définissent le verrou — elles ne le valident pas.

### Où vivent les conclusions : pas dans les verrous

Chaque section a son foyer : les **verrous** (C.2) posent l'incertitude et annoncent le plan d'essais ; la **démarche** (C.3) démontre ; les **résultats** (C.4) concluent. La section verrous ne livre **jamais le verdict** (« P2 écarté », « seul P3 tient », les chiffres O(n) → O(1)). Annoncer le gagnant avant la démonstration aplatit l'incertitude (le pivot Frascati) et frôle le raisonnement à l'envers.

- À garder en clôture de C.2 : la **feuille de route** (quel prototype éprouve quelle voie) et l'**incertitude** (rien de levable depuis la littérature, mécanismes non standards, échecs assumés, issue non acquise au lancement). « Échecs assumés » suffit, sans dire *lequel* échoue.
- À renvoyer en C.4 : « ce qui est acquis / écarté / la décision », **démontré et chiffré**. Une conclusion a sa force là où elle est prouvée par la mesure, pas affirmée en amont.
- Nuance (ne pas sur-corriger) : **prouver analytiquement que les méthodes existantes échouent** reste du ressort des verrous — la doctrine l'exige (« pourquoi les méthodes existantes échouent »). Ex. : « l'instantané ne change pas la classe de complexité, car la synthèse doit porter l'ensemble de déduplication » est une déduction, pas un verdict de prototype. La ligne de partage : verrou = *pourquoi* (analytique, déductif) ; C.4 = *combien* (mesuré) + quel prototype tranche. Transformer la déduction en « question ouverte » sous-vendrait l'analyse et se contredirait avec le verrou.

## 3. Démarche expérimentale et prototypes

Structurer en **5 temps** (jamais un journal chronologique brut) : Verrou → Hypothèses testables → Protocole (outils, paramètres) → Analyse critique des résultats → Connaissances acquises / verrous résiduels. Montrer la progression « H1 → test → résultat contradictoire → ajustement → H2 ».

**Valoriser les échecs** (preuve la plus forte de l'incertitude). Un projet est éligible même non abouti ; un dossier « trop propre » affaiblit la démonstration. Documenter : tentatives infructueuses et leurs causes, pistes abandonnées et pourquoi, blocages ayant reformulé les hypothèses, verrous résiduels.
> Formulation type : « Cette approche a échoué car […], ce qui nous a conduits à reformuler l'hypothèse et à explorer […]. »

**Preuves à conserver** (infabricables a posteriori → valeur max) : commits/logs datés, comptes-rendus de tests échoués, benchmarks horodatés, captures de simulations, comptes-rendus de réunion R&D.

## 4. R&D logicielle (l'administration est stricte)

Éligible seulement si les 5 critères Frascati sont satisfaits, l'incertitude étant discriminante. La complexité, l'effort ou la nouveauté commerciale ne suffisent jamais.

| Éligible | Inéligible |
|---|---|
| Algorithme original sans solution documentée | Adapter un algo existant à un nouveau cas |
| Architecture dont le **comportement global est inconnu a priori** | Microservices « complexes », intégration d'API, stack récente (React, K8s) |
| Modèle/structure dont la perf est un verrou (latence, scalabilité) | Correction de bug, extension fonctionnelle, nouvelle version |
| Prototype validant une hypothèse technique incertaine | Assemblage de briques existantes |

**Verrous logiciels recevables** : faux positifs < seuil + latence < seuil sur flux massif ; modèle fiable sur données dégradées sans solution publiée ; comportement global d'une architecture distribuée non résolu par les patterns existants ; chiffrement de pointe avec incertitudes ouvertes. → **Un cas de scalabilité d'architecture distribuée à forte volumétrie (cohérence transactionnelle à grande échelle non couverte par les patterns existants) est typiquement recevable.**

**Jurisprudence clé :**
- **CAA Toulouse 28/03/2024 (Kaliop)** : développeurs ≠ techniciens de recherche par défaut ; fiches de poste trop générales + rattachement à un responsable *production* → rejet.
- **CAA Paris 06/03/2024 (Scality)** : un « research developer » peut être assimilé à un ingénieur de recherche → **la précision de la fiche de poste est décisive** (jurisprudence contradictoire avec Toulouse).
- **CAA Bordeaux 10/03/2022** : l'extension fonctionnelle ne qualifie pas une recherche ; il faut « des techniques différentes de celles existantes ».
- **TA Nîmes 23/11/2022** : une nouvelle version = mise à jour applicative, pas un produit nouveau.

## 5. Do's & Don'ts

**Vocabulaire à EMPLOYER** : verrou technologique, état de l'art, incertitude technique réelle, dépassement de l'état de l'art, démarche expérimentale, hypothèses testées, développement expérimental, contribution scientifique.

**Vocabulaire à BANNIR** : part de marché, rentabilité, compétitivité, gain client, roadmap produit, stratégie commerciale, « innovation » sans qualificatif technique.

**Do's** : 1 problématique = 1 opération ; objectifs en termes scientifiques chiffrés ; état de l'art = analyse critique des limites ; documenter échecs et itérations ; cohérence stricte heures déclarées ↔ travaux décrits ↔ volet financier ; collecter les preuves au fil de l'eau.

**Don'ts** : dossier « trop propre » sans impasse ; copier-coller d'une année sur l'autre (rejet automatique) ; état de l'art = analyse concurrentielle ; verrous vagues ; objectifs business ; approche purement comptable a posteriori.

**Équilibre narration/preuve** : la narration expose le raisonnement (verrou → hypothèse → test → résultat) ; chaque affirmation technique forte s'adosse à une preuve (référence datée, log, benchmark). « Rien n'est plus risqué qu'une liste d'affirmations non justifiées. »

## 6. Feuilles de temps

Obligation (BOI-BIC-RICI-10-10-20-20) : établir « avec précision le temps réellement et exclusivement passé » aux opérations. **Forfaitisation exclue.** Format libre mais chaque entrée = date + description détaillée + lien au projet éligible. Granularité quotidienne à mensuelle, saisie contemporaine. Outils acceptés : Jira, Lucca, Excel individualisé, agendas extractibles s'ils sont assez précis. → Le xlsx jours-homme par prototype doit être adossé à des feuilles de temps individuelles, pas seulement à un total annuel.

## 7. Fidélité au système réel décrit (zéro hallucination de mécanisme)

La règle « zéro hallucination » de la biblio vaut aussi pour **chaque mécanisme technique décrit**. Ne décrire que ce qui est réellement implémenté ; ne jamais ajouter une étape « qui sonne juste » mais absente du système.

- Exemple : un mécanisme de reprise automatique décrit comme existant alors qu'il n'est pas implémenté → démasqué en relecture métier.
- Double risque : (1) le mécanisme inventé se fait repérer par l'expert MESR ou par l'équipe, **comme une citation fausse** ; (2) pire, une parade inventée **minore le verrou** (si une difficulté paraît déjà contournée, l'incertitude semble levée) → la fidélité protège la démonstration d'incertitude.
- Réflexe : pour chaque mécanisme écrit, se demander « c'est dans le code / l'archi, ou je le déduis parce que c'est plausible ? ». Vérifier comme on vérifie un DOI ; au moindre doute, faire confirmer par l'équipe technique.
