# Bibliographie & état de l'art — protocole anti-hallucination

C'est le **point le plus surveillé** d'un CIR : une citation inventée découverte par l'expert MESR décrédibilise tout le dossier. L'état de l'art n'est pas une bibliographie décorative — c'est la démonstration **datée** que les connaissances accessibles au lancement ne résolvaient pas le problème (cf. `02-bonnes-pratiques.md` §2).

## Sommaire

- [Règle cardinale](#regle-cardinale)
- [Outil : `scripts/verify-biblio.py`](#outil-scriptsverify-bibliopy)
- [Leçons empiriques (tirées d'une passe biblio réelle, à réappliquer)](#lecons-empiriques-tirees-dune-passe-biblio-reelle-a-reappliquer)
- [Pipeline de bout en bout](#pipeline-de-bout-en-bout)
- [Red flags d'hallucination à traquer](#red-flags-dhallucination-a-traquer)
- [Outils externes (découverte) — verdict](#outils-externes-decouverte-verdict)
- [Règle d'or (à ne jamais oublier)](#regle-dor-a-ne-jamais-oublier)
- [Deux filtres distincts : EXISTENCE puis CRÉDIBILITÉ](#deux-filtres-distincts-existence-puis-credibilite)
- [Troisième filtre : FIDÉLITÉ (ce que la source dit vraiment)](#troisieme-filtre-fidelite-ce-que-la-source-dit-vraiment)
- [Prompts de contrainte (à se donner à soi-même / à un sous-agent biblio)](#prompts-de-contrainte-a-se-donner-a-soi-meme-a-un-sous-agent-biblio)
- [Citation propre en un appel](#citation-propre-en-un-appel)
- [Étapes spécifiques CIR](#etapes-specifiques-cir)
- [Socle réel réutilisable (réfs propres à VOTRE domaine) — à re-vérifier à chaque réemploi](#socle-reel-reutilisable-refs-propres-a-votre-domaine-a-re-verifier-a-chaque-reemploi)

## Règle cardinale
> **Aucun champ de citation (auteurs, titre, revue, année, DOI) n'est rédigé de mémoire.**
> Chaque champ est **recopié** d'une réponse d'API de métadonnées (Crossref / OpenAlex / arXiv / HAL). Une source qui ne résout sur aucun index est **présumée inventée** → supprimée.

Le LLM a le droit de : formuler des requêtes, juger la pertinence d'un abstract, rédiger l'analyse critique d'une source réelle. Il n'a **pas** le droit de : produire un DOI, un numéro de volume/pages, une année ou une liste d'auteurs sans tool result à l'appui.

## Outil : `scripts/verify-biblio.py`
Interroge les index publics et renvoie des métadonnées autoritatives (aucune dépendance, accès réseau requis).

```
verify-biblio.py search "<mots-clés EN>"     # OpenAlex : découvrir des candidats (+ DOI, citations, PDF OA)
verify-biblio.py doi <DOI>                    # Crossref : VÉRIFIER qu'un DOI existe → bloc citation prêt
verify-biblio.py arxiv "<requête ou id>"      # arXiv : prépublications CS
verify-biblio.py hal "<requête FR>"           # HAL : littérature française
verify-biblio.py check "<auteur>" "<mots du titre>" <année>   # anti-invention : la combinaison existe-t-elle ?
verify-biblio.py oa <DOI>                      # Unpaywall : trouver le PDF en accès libre
verify-biblio.py fetch <DOI> biblio            # rapatrier le PDF dans biblio/ + ligne d'index
```

Plus : `verify-biblio.py archive <DOI>` rapatrie un **article fermé** (payant) sous forme de `.txt` (métadonnées vérifiées + abstract OpenAlex). Si le shell est sandboxé sans réseau : interroger les **mêmes URLs d'API** via WebFetch (elles sont dans le code du script) et lire les champs JSON bruts. Le réseau nécessite souvent `dangerouslyDisableSandbox` sur le Bash.

## Leçons empiriques (tirées d'une passe biblio réelle, à réappliquer)
- **Chercher par TITRE, pas en plein texte.** `search` (OpenAlex plein texte) ou arXiv `all:` ramènent un bruit massif sur les sujets pointus (un terme technique pointu existe souvent à l'identique dans un autre champ, en biologie ou en astronomie). Préférer le filtre **`title.search:`** d'OpenAlex (`https://api.openalex.org/works?filter=title.search:<mots>`) et arXiv **`ti:"…"`** — bien plus précis. Ancrer aussi sur les **auteurs de référence de votre domaine** et le **citation chaining**.
- **La plupart des articles CS sont payants** (ACM, IEEE, Elsevier). `fetch` ne réussit que sur l'OA réel ; sinon utiliser `archive` (abstract + métadonnées) — c'est suffisant pour le dossier (la citation vérifiée est le livrable ; le PDF sert à lire). Certains éditeurs OA (MDPI) bloquent même le téléchargement automatisé (Cloudflare 403) → récupération à la main ou accès institutionnel.
- **Red flag confirmé sur le terrain** : entrées Zenodo récentes, titre en CAPITALES, 0 citation, DOI quasi-dupliqués → auto-publication suspecte, **écarter**.
- **Chaque source = une branche.** Étiqueter dans `biblio/INDEX.md` la branche de la problématique servie + la *limite* de la source (c'est la limite qui construit le gap, pas le résumé).
- **Crossref peut renvoyer un nom d'auteur FAUX.** Le DOI prouve l'existence, pas l'exactitude de chaque champ. Recouper avec OpenAlex et les publications de l'auteur lui-même. Cas réel : Crossref renvoie un prénom erroné pour le 2ᵉ auteur d'un article ; le vrai prénom (confirmé par la thèse de l'auteur + OpenAlex) est différent. Corriger dans `refs.bib` et documenter la divergence dans `INDEX.md`.
- **La thèse de doctorat d'un auteur = souvent le texte intégral, en accès libre, d'un article payant.** Pour un article fermé (IEEE/ACM), chercher la thèse de l'auteur sur le dépôt de son université (OPARU, theses.fr, HAL, DiVA…) : elle incorpore ses papiers en plus complet, **avec les évaluations chiffrées** absentes des versions courtes. Cas réel : un article de conférence payant (abstract seul) entièrement développé dans la thèse de son auteur en accès libre — d'où sont sortis les chiffres mesurés absents de la version courte. Attribuer alors chaque claim au document réellement lu (thèse) et garder l'article peer-reviewed pour la contribution canonique.

## Pipeline de bout en bout

1. **Cartographier les besoins de preuve.** Lister les affirmations à sourcer : chaque verrou, chaque « l'état de l'art ne couvre pas X », chaque claim de performance. Une affirmation forte sans source = un risque.
2. **Formuler les requêtes** en anglais (la littérature CS l'est) + en français pour HAL. Mots-clés précis sur le verrou technique (réfs propres à VOTRE domaine), pas l'objectif business.
3. **Découvrir** les candidats : `search` (OpenAlex) et/ou outils dédiés (cf. §Outils externes). Lire le titre + l'abstract renvoyés.
4. **Filtrer** : pertinence réelle au point à appuyer **et** antériorité au lancement des travaux (pour l'état de l'art). Écarter blogs et pages marketing pour le socle académique.
5. **Vérifier l'existence** : pour chaque candidat retenu, `doi <DOI>` (ou `arxiv`/`hal`). `DOI INTROUVABLE` → **rejet**. Pour une citation suspecte déjà rédigée, `check "<auteur>" "<titre>" <année>` → `NON TROUVÉ` = invention.
6. **Recopier** les métadonnées exactes depuis le bloc « CITATION VÉRIFIÉE » → format `templates/biblio.md`. Ne jamais reformuler auteurs/titre/année.
7. **Rapatrier** : `fetch <DOI> biblio` (PDF OA) ou archiver à la main abstract + page DOI si fermé. Ajouter la ligne dans `biblio/INDEX.md` (réf, fichier local, DOI, URL, statut).
8. **Analyser la limite** de chaque source (dans le dossier) : pourquoi elle ne résout pas le problème → c'est ce qui construit le *gap*.
9. **Garde-fou final (refute-check)** : avant de figer, re-résoudre chaque DOI et vérifier que titre/année/revue cités concordent avec la réponse API. Toute discordance = correction ou suppression.

## Red flags d'hallucination à traquer
- DOI qui ne résout pas sur Crossref.
- « et al. » alors que la liste d'auteurs n'a jamais été vérifiée.
- Numéro de volume/pages très précis sans source résolue.
- Revue plausible mais article inexistant (vérifier le couple titre × revue).
- Année qui ne correspond pas à celle du DOI.
- Référence « parfaite » trop bien adaptée au propos (les LLM fabriquent des citations idéales).

## Outils externes (découverte) — verdict
- **OpenAlex / Crossref / arXiv / HAL** : métadonnées autoritatives, DOI réels → **socle de vérification** (déjà câblés dans le script).
- **Semantic Scholar, Google Scholar, Connected Papers, Research Rabbit** : excellents pour **découvrir** et explorer le voisinage d'un article fiable (citation chaining). Toujours re-vérifier le DOI ensuite.
- **Consensus, Elicit, SciSpace, Scite** : aident à trouver des sources et à extraire des conclusions ; **re-vérifier** chaque DOI avant citation.
- **Perplexity (mode Academic)** : utile pour la découverte ; ses citations doivent être **systématiquement re-vérifiées** (peut citer des blogs ou halluciner un DOI). Jamais coller une citation Perplexity sans passage par Crossref/OpenAlex.
- **ChatGPT / Claude sans outil de recherche** : **INTERDIT** pour générer des citations — hallucination quasi garantie sur les métadonnées exactes.

> Recommandation : rester sur le pipeline du script (OpenAlex → vérif DOI Crossref → fetch) = déterministe, traçable, archivé. Les autres outils en complément de découverte seulement.

## Règle d'or (à ne jamais oublier)
> **Ne jamais demander au LLM qui a généré une citation si elle est réelle.** Le modèle qui a halluciné ne peut pas détecter son hallucination. La vérification est **externe** : Crossref (404 = inexistant), OpenAlex, arXiv, HAL. À elle seule, la résolution DOI Crossref attrape ~60 % des fabrications ; combinée au contrôle titre × revue, quasi toutes.

Chiffres qui justifient cette rigueur : GPT-4 fabrique encore ~18 % de ses citations (GPT-3.5 : 55 %) ; le RAG seul laisse jusqu'à 33 % d'hallucination résiduelle. Le détail (études, taux par modèle, comparatif d'outils, endpoints testés) est dans `06-etat-de-lart-IA-detail.md`.

## Deux filtres distincts : EXISTENCE puis CRÉDIBILITÉ
La vérification DOI prouve qu'une source **existe** — pas qu'elle est **crédible**. Les revues prédatrices ont de vrais DOI et sont indexées (OpenAlex/Crossref). Après le filtre anti-hallucination, passer un **filtre qualité de revue** :
- **Red flags de revue prédatrice** : « Impact Factor » auto-proclamé sur la couverture, mention « double-blind peer reviewed » mise en avant comme argument, frais de publication rapides, éditeurs type IJSR / IJRASET / IRJET / IJARSCT, 0 citation + venue obscure, DOI prefix de l'éditeur lui-même uniquement.
- **Signaux de crédibilité** : indexation **Scopus / Web of Science / DOAJ**, revue/conférence reconnue (IEEE, ACM, Springer, Elsevier, *Journal of Systems and Software*, *Acta Polytechnica Hungarica*…), citations réelles, auteurs rattachés à une institution.
- En cas de doute, **privilégier les références canoniques** de votre domaine — un évaluateur MESR les reconnaît. Une source prédatrice dans l'état de l'art **affaiblit** le dossier au lieu de le renforcer.
- Une revue prédatrice peut servir de **mine de références** (sa biblio), jamais de citation directe.

## Troisième filtre : FIDÉLITÉ (ce que la source dit vraiment)
DOI résolu = la source **existe**. Revue sérieuse = elle est **crédible**. Aucun des deux ne garantit que la phrase qu'on écrit *à son sujet* est **exacte**. C'est le filtre le plus traître : la citation est vraie, l'usage qu'on en fait est faux. Un évaluateur qui ouvre le papier le voit immédiatement. Règles tirées d'une passe biblio réelle :
- **Lire ce que la source MESURE, pas son titre.** Avant d'attribuer un chiffre, identifier l'axe expérimental exact. Cas réel : le paramètre balayé dans l'article était une grandeur interne précise, pas la charge concurrente qu'on lui prêtait ; et la valeur citée correspondait à un autre point de mesure que celui annoncé. Une métrique de perf mal lue décrédibilise le chiffre.
- **Distinguer MESURÉ / ANALYTIQUE / ASSERTÉ.** Un raisonnement de complexité (O(n)→O(m)) est un **argument analytique**, pas une mesure. « Double les perfs » obtenu sur un banc 1 cœur / 2 Go reste **indicatif**. Écrire « X mesure le bénéfice » quand X **raisonne** = faux.
- **Distinguer LU EN ENTIER / ABSTRACT SEUL.** Sur un article fermé (seul l'abstract est archivé), n'écrire **que** ce que l'abstract porte. Ne jamais ajouter des limites ou détails techniques « de bon sens » absents du texte. Cas réel : des limites techniques plausibles avaient été inventées et collées à un papier dont seul l'abstract était archivé.
- **Vérifier le DOMAINE exact.** Cas réel : un article portait sur un objet précis (un type de jeton interne), PAS sur des actifs financiers ; le qualifier de « système de trading » sans qualificatif était inexact et dangereux pour le dossier.
- **Représenter la CONTRIBUTION réelle.** Un papier qui **propose et évalue** une solution ne se résume pas à « montre que c'est difficile ».
- **Bon DOCUMENT du même auteur.** Un auteur a souvent plusieurs textes (livre vs *reference*, éditions). Chaque citation verbatim pointe le document qui contient *réellement* la phrase, et le titre rendu en biblio doit correspondre au document nommé dans la prose. Cas réel : une phrase verbatim figurait dans l'édition courte (*reference*) d'un auteur, pas dans son livre principal ; citer la mauvaise édition affichait un titre qui ne contient pas la phrase. Garder le livre pour la doctrine générale, la *reference* pour ses citations textuelles.
- **Ne pas surévaluer la PORTÉE.** « La seule », « toujours », « aucun », « jamais » seulement si la source l'affirme. Si elle rapporte plusieurs options, écrire « parmi les… ». Cas réel : un auteur liste plusieurs parades au coût de reconstruction (matériel, reconstructions ciblées, élagage) ; « la seule parade consiste à élaguer » était une généralisation réfutable d'un coup d'œil au papier.
- **Vérifier le SENS d'un fait attribué aux auteurs.** Ne pas se contenter de trouver que les auteurs disent *quelque chose de proche* : contrôler la direction exacte. Cas réel : écrire qu'un auteur « reconnaît que son protocole sous-estime les deux modèles » était faux ; l'aveu est **asymétrique** (le banc avantage un modèle et en pénalise un autre). Le sens correct était d'ailleurs plus favorable au dossier.
- **Méthode qui marche** : déléguer la lecture du PDF à un sous-agent avec brief strict — *quote exacte + n° de section + dis explicitement ce qui N'EST PAS dans le papier + quel est l'axe expérimental exact + mesuré ou raisonné ?*. Puis relire le dossier ligne à ligne en se demandant pour chaque affirmation : « cette phrase est-elle réellement dans la source, à ce niveau ? ». Le doute se résout par « non présent », jamais de mémoire.

## Prompts de contrainte (à se donner à soi-même / à un sous-agent biblio)
- **Abstention forcée** : « Si tu n'es pas certain, réponds exactement "NON TROUVÉ". Ne devine jamais une référence. »
- **Grounding strict** : « Rédige la synthèse en te basant UNIQUEMENT sur ces papiers vérifiés [liste + DOI]. N'invente aucune citation, n'en cite aucune hors liste. »
- **Extraction sourcée** : « Extrais chaque affirmation avec sa citation exacte, son n° de page et sa section. Signale toute affirmation sans source. »
- **Fidélité à la source** : « N'écris sur une source que ce qu'elle dit vraiment. Donne son axe expérimental exact, distingue mesuré / analytique / asserté, vérifie le domaine précis, et si tu n'as que l'abstract n'ajoute aucun détail absent du texte. »

## Citation propre en un appel
Une fois un DOI **vérifié**, ne jamais reformater de mémoire — récupérer la citation canonique :
`verify-biblio.py bibtex <DOI>` (négociation de contenu DOI → BibTeX). Idem `hal` pour les sources françaises (clé pour le CIR).

## Étapes spécifiques CIR
- Sources **antérieures** au lancement du projet (l'état de l'art est daté, jamais reconstruit a posteriori — risque d'audit majeur).
- Inclure les **brevets** (Espacenet/INPI) et les normes, pas seulement les articles.
- Pour un projet pluriannuel, **mettre à jour** l'état de l'art chaque année.
- Vérifier l'absence de **rétractation** (Retraction Watch) pour les sources sensibles.
- Posture (consensus des prestataires CIR) : l'IA **synthétise une documentation déjà détenue et vérifiée** ; un expert humain affine. Aucune guidance officielle ANR/MESRI n'autorise/encadre l'IA pour l'état de l'art à ce jour.

## Socle réel réutilisable (réfs propres à VOTRE domaine) — à re-vérifier à chaque réemploi
Voir `templates/biblio.md`. Y consigner les références canoniques vérifiées de votre domaine : article peer-reviewed avec DOI résolu sur Crossref, ou source web fondatrice sans DOI (citer alors l'URL exacte). Re-vérifier titre et venue exacts avant chaque citation, même pour une référence déjà utilisée.
