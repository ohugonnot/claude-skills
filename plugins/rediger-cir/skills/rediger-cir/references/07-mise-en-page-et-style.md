# Mise en page Word & style rédactionnel

Conventions calées sur les **dossiers de référence validés** des années antérieures. À appliquer dès la première rédaction pour éviter les reprises.

## Sommaire

- [1. Production du Word (pipeline pandoc)](#1-production-du-word-pipeline-pandoc)
- [2. Mise en page (calée sur les dossiers de référence)](#2-mise-en-page-calee-sur-les-dossiers-de-reference)
- [3. Figures (bloc centré + légende)](#3-figures-bloc-centre-legende)
- [4. Bibliographie normée + liens](#4-bibliographie-normee-liens)
- [5. Liens vers le glossaire (Annexe 1)](#5-liens-vers-le-glossaire-annexe-1)
- [6. Style rédactionnel — anti-pattern IA (obligatoire)](#6-style-redactionnel-anti-pattern-ia-obligatoire)
- [7. Citations réglementaires — règle de déduplication](#7-citations-reglementaires-regle-de-deduplication)
- [8. Listes à puces — où et où pas](#8-listes-a-puces-o-et-o-pas)
- [9. Densité — chaque phrase doit gagner sa place](#9-densite-chaque-phrase-doit-gagner-sa-place)
- [10. Fluidité — lecture à voix haute](#10-fluidite-lecture-a-voix-haute)
- [11. Titres de sous-sections « porteurs de conclusion »](#11-titres-de-sous-sections-porteurs-de-conclusion)

## 1. Production du Word (pipeline pandoc)

On rédige en **Markdown**, on convertit en `.docx` à la demande. Une seule commande :
```
scripts/build-docx.sh "CIR 2025/<dossier>.md"
```
Le script (autonome) :
- télécharge le binaire **pandoc** dans `~/.cache/cir-pandoc` s'il est absent (rien à installer) ;
- applique le gabarit de style **`assets/reference.docx`** automatiquement (figures/légendes centrées) ;
- active **citeproc** si un `refs.bib` est présent à côté du `.md` (+ `ieee.csl` pour le style) ;
- passe `--from=markdown-implicit_figures` (on contrôle les figures explicitement, voir §3) et `--resource-path` (embarque les images).

Le gabarit `assets/reference.docx` a été produit via `scripts/center-figure-styles.py` (centre les styles Figure, ImageCaption, CaptionedFigure, Caption). Le corps reste **aligné à gauche** par défaut.

## 2. Mise en page (calée sur les dossiers de référence)

- **Corps de texte : aligné à gauche.** Le dernier dossier de référence validé est à gauche (la quasi-totalité des paragraphes en « left », un seul « justifié »). **Ne pas justifier.**
- **Figures : centrées.** Légende **centrée** juste en dessous.
- **Bibliographie : sur une page à part** (saut de page avant).
- **Annexes : sur une page à part** (saut de page avant).
- Saut de page en Markdown (rendu docx) :
  ````
  ```{=openxml}
  <w:p><w:r><w:br w:type="page"/></w:r></w:p>
  ```
  ````

## 3. Figures (bloc centré + légende)

Image et légende dans des divs `custom-style` qui mappent vers les styles centrés du gabarit :
```
::: {custom-style="Figure"}
![](figures/ma-figure.png)
:::

::: {custom-style="Image Caption"}
Figure N. Titre de la figure. Source : [ENTREPRISE] Research…
:::
```
- La **légende ne contient pas de citation `[@clé]`** (citer en clair « d'après Auteur ([ANNÉE]) »). Les liens biblio restent dans le corps.
- Figures en **SVG** (cf. `figures/GUIDE-figures.md`), rendues en PNG via `cairosvg` ; **sans tiret cadratin** dans les libellés non plus.

## 4. Bibliographie normée + liens

- Citations en clés **`[@clé]`** résolues depuis `refs.bib` (entrées vérifiées par DOI, cf. `05-bibliographie...`). Style **IEEE** (`ieee.csl`), numérotation par ordre d'apparition.
- `link-citations: true` dans l'en-tête YAML → chaque `[n]` du texte devient un **lien cliquable** vers son entrée.
- Emplacement de la biblio : un titre `## Bibliographie` puis un div `::: {#refs}\n:::` (citeproc la remplit là, avant les annexes).
- Pour une **norme française**, remplacer `ieee.csl` par un CSL ISO 690 (le script le prend automatiquement).

## 5. Liens vers le glossaire (Annexe 1)

Chaque terme jargon, à sa **première occurrence** dans le corps, pointe vers sa définition :
- dans le corps : `[terme-A](#g-terme-a)`, `[terme-B](#g-terme-b)`…
- dans l'Annexe 1 : ancrer le terme `- [**terme-A**]{#g-terme-a} (*…*) : définition.`
Pandoc transforme ces liens en renvois Word internes cliquables. Anglicismes traduits au passage (scalabilité → montée en charge, framework → cadre logiciel…), le terme d'origine entre parenthèses la première fois. Une fois un terme francisé, **toutes** les occurrences suivantes utilisent le français : le rappel entre parenthèses à la 1ʳᵉ occurrence n'autorise pas à reprendre l'anglais ensuite. Piège récurrent : un anglicisme déjà traduit qui resurgit plus loin alors qu'il a déjà été francisé.

## 6. Style rédactionnel — anti-pattern IA (obligatoire)

Le dossier ne doit pas « sentir » l'IA. Règles dures :
- **Aucun tiret cadratin (—) dans la prose.** Remplacer par virgule, parenthèses, deux-points, ou « c'est-à-dire ». (Exception : un tiret présent dans le **titre réel** d'une référence citée reste tel quel.)
- **Aucune phrase ouverte par une conjonction** : ni *Et*, *Mais*, *Or*, *Donc*, *Car*, *Surtout*, *Ainsi*. Réintégrer en milieu de phrase (*cependant*, *toutefois*, *pourtant*, *en revanche*) ou reformuler.
- **Points-virgules de prose allégés** : préférer des phrases courtes. (Les `;` internes aux clusters de citations `[@a; @b]` ne comptent pas, c'est de la syntaxe.)
- Éviter les tics : clivées « Ce n'est pas X, c'est Y », « C'est précisément … qui », triades systématiques, virgule d'Oxford (« A, B, et C » → « A, B et C »), « non négociable », vocabulaire savant inutile.

### 6 bis. Registre attendu par le relecteur métier
Cible : **« une phrase qu'un humain pourrait écrire »**, académique mais naturelle. Règles dures :
- **Phrases courtes.** Une idée par phrase. Préférer le point au « : » et à la subordonnée qui rallonge. Couper toute phrase de 3+ propositions.
- **Peu de deux-points.** N'en garder qu'un quand il introduit une vraie énumération ou définition ; sinon, scinder en deux phrases.
- **Aucune tournure « romanesque » / imagée** : « La tension naît là », « se paie sur deux fronts », « X expose la difficulté suivante »… → constat direct.
- **Antécédents explicites.** Jamais de « ce problème / ce choix / cette tension / il » flottant : nommer le référent (« le verrou », « le choix technique retenu »…). Le relecteur ne doit jamais se demander « quoi ? qui ? ».
- **Mots justes, pas de métaphore non assumée** : « tension » a été refusé comme imprécis en C.1 → « difficulté / problème ». Éviter aussi « impacter » (préférer « pèse sur », « se répercute sur »).

## 7. Citations réglementaires — règle de déduplication

Chaque texte réglementaire (réfs propres à VOTRE secteur) ne doit apparaître **qu'une seule fois** avec sa citation biblio `[@clé]` et son lien glossaire `[le règlement](#g-reglement)` : là où il appuie un argument technique précis (une contrainte de rétention, une exigence réglementaire précise…).

- **Dans l'intro de contexte** : ne pas nommer ces textes réglementaires avec des liens biblio. Nommer sans lien ou ne pas nommer du tout — la citation réglementaire arrive là où elle sert de preuve.
- **Chaque occurrence** dans le corps doit avoir le lien glossaire `[le règlement](#g-reglement)` dès la première fois, puis simplement son nom (sans lien) les occurrences suivantes dans la même section.
- Double citation du même règlement dans un même dossier = signal d'alerte : vérifier que l'une n'est pas redondante.

## 8. Listes à puces — où et où pas

Les consignes officielles DGFiP/MESR **n'interdisent pas** les listes à puces. La seule contrainte écrite (p.2 du gabarit générique) est : *"précis et décrire scientifiquement les opérations, tout en étant synthétique."*

**Bullets bienvenus (attendus dans le gabarit officiel) :**
- Section I — Présentation société, critères de sélection des opérations, organigramme R&D
- Section II — tableau synthétique des opérations (format imposé)
- Résultats de benchmarks chiffrés, liste de prototypes testés, tableau de couverture état de l'art

**Prose fortement préférée (pratique, pas règle dure) :**
- Section III — contexte, état de l'art, verrous, démarche expérimentale : la chaîne logique *littérature → gap → verrou → hypothèse → résultat* se démontre par des phrases enchaînées, pas par des bullets qui fragmentent le raisonnement.

**Règle de décision** : une liste de **faits** (résultats, membres de l'équipe, prototypes) → bullet OK. Un **raisonnement** (pourquoi ce gap, pourquoi ce verrou) → prose.

## 9. Densité — chaque phrase doit gagner sa place

Supprimer tout mot qui ne porte pas d'information nouvelle. Tester : *"si je l'enlève, perd-on quelque chose ?"* Non → couper.

- Pléonasmes : "réglementation applicable", "résultat final", "période de temps" → supprimer l'adjectif/complément redondant.
- Tournures creuses : "il convient de noter que", "dans le cadre de", "au niveau de", "à titre d'exemple" → reformuler ou supprimer.
- Nominalisation inutile : "procéder à la vérification de" → "vérifier" ; "effectuer une analyse de" → "analyser".
- Sujet vague : "cela permet de", "il est possible de" → nommer le sujet réel.

Objectif : phrase la plus courte possible qui transmet l'information complète. La densité est une preuve de maîtrise technique.

**Garde-fou : densité ≠ style télégraphique.** Couper les mots **vides** (tournures creuses, « d'ailleurs », pléonasmes), jamais les mots **grammaticaux** (articles, liaisons) qui portent le naturel. Une énumération sans articles (« achat ou vente, dépôt ou retrait ») se lit comme des notes, pas comme de la prose académique : écrire « l'achat ou la vente, le dépôt ou le retrait ». Signal de sur-correction repéré en relecture métier : le relecteur remet des articles et re-scinde des phrases trop comprimées → la densité s'attaque au creux, pas à la grammaire.

## 10. Fluidité — lecture à voix haute

- Tester chaque phrase **à voix haute**. La virgule marque une **respiration**, pas un réflexe.
- Pas de qualificatif « collé » en fin de phrase (« …des comptes, à forte volumétrie et en temps réel » → réintégrer : « gérer en temps réel et sur de gros volumes les … »).
- Pas d'apposition longue qui coupe sujet et verbe.
- Une idée par phrase quand c'est possible ; casser les phrases à rallonge.
- Viser le niveau « très bon » du **radar B** (`04-radar-notation.md`) : lisibilité, clarté, langue, auto-suffisance, justesse, enchaînement. Faire relire en aveugle si possible.

## 11. Titres de sous-sections « porteurs de conclusion »
La trame CIR impose les **4 sections** (contexte/état de l'art, verrous, démarche, résultats) et leur contenu, **pas** le libellé des sous-titres internes → liberté de rédaction (vérifié : Guide MESR, dossier générique impots.gouv.fr).
Recommandé pour l'état de l'art : des **titres-thèse** qui portent la conclusion de chaque sous-section, de sorte que les titres **lus à la suite donnent le déroulé du raisonnement** (problème → piste → conclusion). Ex. : « Côté écriture : la sérialisation plafonne le débit d'un compte chaud. », « Bilan : aucune technique ne couvre les deux fronts. »
Pourquoi c'est conforme, et même un atout : la doctrine valorise le **précis/nommé contre le vague** (cf. exigence « verrou nommé », `01-exigences-officielles.md`), et l'expertise MESR cherche une **analyse critique visible**.
Garde-fous : (1) rester **concis** (la trame limite les caractères) ; (2) dans l'état de l'art, les titres énoncent des **constats de littérature et des manques** (« non documenté », « non résolu »), **pas** les verrous [ENTREPRISE] formalisés — ceux-ci se nomment en partie « verrous » (sinon raisonnement à l'envers) ; (3) **ne pas répéter le titre** dans la phrase d'ouverture du corps (le titre annonce, le corps développe).
