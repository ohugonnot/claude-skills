# Pourquoi ces règles — la base de preuves

Chaque règle du SKILL.md s'appuie sur un finding documenté. Ce fichier tient les justifications et leurs sources, pour pouvoir adapter une règle en connaissance de cause. Tags : [SOLIDE] = méta-analyse ou résultat répliqué ; [INDICATIF] = étude isolée ou opinion d'expert convergente.

## Distiller, pas tronquer

- **Macro-règles de Kintsch & van Dijk (1978, Psychological Review)** : un bon résumé = suppression du trivial + généralisation + **construction** de propositions nouvelles qui subsument plusieurs passages. Une réécriture à un niveau d'abstraction supérieur, pas une compression proportionnelle. [SOLIDE]
- **Brown & Day (1983, JVLVB)** : les novices font du copy-delete (recopier en raccourcissant), les experts construisent des phrases nouvelles trans-paragraphes. Le marqueur de qualité d'un résumé : la proportion de phrases qui n'existent dans aucune phrase du livre. [SOLIDE]
- **Le piège du surlignage (Dunlosky et al. 2013, PSPI)** : sélectionner les meilleurs passages sans les relier dégrade les questions d'inférence (Peterson 1992) : marquer des items isolés détruit les connexions entre concepts. D'où la règle « idées reliées, pas best-of ». [SOLIDE]
- **Dunlosky et al. 2013, verdict sur la summarization** : « low utility » pour l'apprenant moyen, efficace seulement chez qui sait déjà résumer ; la **qualité** du résumé est le médiateur (Bednall & Kehoe 2011 : corrélation positive entre définitions correctes incluses et performance). Ce skill encode précisément les gestes du résumeur expert. [SOLIDE]

## Écrire pour qu'on apprenne

- **Exemples concrets** : effet répliqué directement (Micallef & Newton 2024, Teaching of Psychology) ; séquence concret → abstrait supérieure à l'un ou l'autre seul (Fyfe et al., concreteness fading). D'où « l'exemple du livre d'abord, le principe ensuite ». [SOLIDE]
- **Worked examples** (Sweller & Cooper ; méta-analyse Barbieri et al. 2023) : les novices apprennent mieux d'une solution déroulée pas à pas ; l'effet s'inverse chez les avancés (expertise reversal, Kalyuga) → dérouler le premier concept difficile, abréger ce qui réutilise le même schéma. [SOLIDE]
- **Elaborative interrogation** (Dunlosky 2013 : utilité modérée) : le « pourquoi » améliore la rétention quand l'apprenant peut générer l'explication ; un néophyte ne le peut pas → la fiche LIVRE le pourquoi mécanistique. [SOLIDE]
- **Given-new contract** (Clark & Haviland 1977 ; validation au niveau paragraphe : Kent 1984) : une phrase qui ouvre sur du nouveau sans ancrage ralentit la compréhension et dégrade la mémoire. D'où « vieux → neuf, phrase par phrase ». [SOLIDE]
- **Signaling** (Schneider et al. 2018, méta-analyse, 103 études, N = 12 201) : baliser la structure (titres porteurs, mise en relief, liens explicites) donne g = 0.53 en rétention, g = 0.33 en transfert. Le levier texte le mieux chiffré du champ. [SOLIDE]
- **Charge cognitive** (Sweller 2010, Educ. Psych. Review) : on n'ajoute pas de « bonne charge », on supprime l'extraneous (digressions, redondances, décor) pour libérer la mémoire de travail. D'où « couper sans pitié ». [SOLIDE]
- **Dual coding / multimédia** (Paivio ; Mayer ; Ginns 2006) : texte + image aide seulement si le mapping est serré et contigu ; l'image décorative est de la charge extraneous pure. (Pertinent si la fiche embarque des schémas.) [SOLIDE]
- **Advance organizers** (Ausubel ; méta-analyse Luiten et al. 1980, 135 études) : effet positif mais petit → le chapeau-organisateur vaut le coup parce qu'il est quasi gratuit, pas parce qu'il est puissant. [SOLIDE pour la direction]

## Embarquer du rappel (et l'honnêteté du format)

- **Retrieval practice** : g ≈ 0.61 (Adesope et al. 2017, méta-analyse, 217 études), une des deux seules techniques « high utility » de Dunlosky 2013 avec la pratique espacée. Une fiche statique ne teste pas → embarquer 2-3 questions de rappel avec feedback. [SOLIDE]
- **Self-explanation** : g = 0.55 (Bisra et al. 2018, méta-analyse, 69 effets) → le prompt « pourquoi X échouerait-il si… ? » dans le corps. [SOLIDE]
- **Illusion de connaissance** : les gens surestiment leur compréhension (illusion of explanatory depth, Rozenblit & Keil) et un texte fluide est pris à tort pour un texte retenu (fluency illusion). Un résumé fluide est le terrain idéal de la fausse confiance → section « ce que cette fiche ne remplace pas » + questions de rappel. [SOLIDE]
- **Critique des résumés commerciaux** : le défaut structurel n°1 documenté (Blinkist vs Shortform) est de condenser sans jamais juger : le lecteur ignore si la thèse est solide, datée ou contestée → contrepoints obligatoires. [INDICATIF, convergent]
- **Adler (How to Read a Book)** : lecture structurelle → interprétative → critique ; on ne juge qu'après avoir compris → la note se produit en Phase 4, jamais pendant la lecture. [Canon méthodologique]

## Fidélité (anti-hallucination LLM)

- **Verbatim d'abord** : pour les documents longs, extraire les citations pertinentes avant d'exécuter la tâche améliore le recall (recommandation officielle Anthropic, long-context tips). [SOLIDE]
- **Lost in the middle** (Liu et al. 2023, confirmé sur fenêtres 128k+) : l'information au milieu du contexte est structurellement sous-exploitée → chunking par chapitre + carte préalable, jamais « tout le PDF d'un bloc ». [SOLIDE]
- **Les hallucinations se concentrent en fin de génération longue** (arXiv 2505.15291) → rédiger idée par idée, sorties courtes et bornées. [INDICATIF]
- **Hallucination extrinsèque** (Maynez et al. 2020, ACL) : ajouter une information absente de la source, parfois VRAIE grâce au pré-entraînement mais infidèle au livre. Le piège sournois d'une fiche → consigne « vraie dans le monde ≠ dans le livre ». [SOLIDE]
- **Claims atomiques** (FActScore, arXiv 2305.14251) : découper la sortie en faits courts indépendants et vérifier chacun contre la source ; <2 % d'erreur vs annotation humaine. C'est le modèle de la Phase 6a et de `check-claim.py`. [SOLIDE]
- **Chain-of-Verification** (CoVe, arXiv 2309.11495) : vérifier chaque claim indépendamment, SANS accès au raisonnement qui l'a produite : la décorrélation évite la propagation d'erreur. [SOLIDE]
- **SummHay** (arXiv 2407.01370) : même les meilleurs modèles long-contexte citent mal à grande échelle (couverture+citation faible sans retrieval) → ne jamais croire « le modèle a tout lu », d'où le contrôle de couverture TOC ↔ idées. [SOLIDE]
- **Citations hallucinées** : 13-21 % mesurés dans des systèmes commerciaux (arXiv 2606.00898) → toute citation entre guillemets se retrouve mécaniquement dans le texte extrait avant publication. [INDICATIF]
- **Map-reduce vs refine** (OpenAI « Summarizing books with human feedback » ; Google Cloud) : la décomposition récursive par sections est validée à l'échelle du livre et rend chaque étage auditable ; la synthèse finale recoud la cohérence que le map-reduce perd. [SOLIDE]

## Ce qui n'est PAS retenu (et pourquoi)

- **Progressive summarization (Forte)** : aucun essai contrôlé ; Forte lui-même la présente comme un outil de découvrabilité de notes, pas d'apprentissage ; ses couches reposent sur le surlignage (utilité faible). Non intégré. [INDICATIF]
- **Cornell / Zettelkasten comme gabarits** : preuves mixtes ou quasi absentes ; leurs ingrédients actifs (reformulation, une-idée-par-note, liaison à l'existant) sont déjà couverts par Kintsch, Brown & Day et le given-new. Les gabarits eux-mêmes n'apportent rien de plus. [INDICATIF]
