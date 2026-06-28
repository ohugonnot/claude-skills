# Radar de notation CIR — 8 axes

Outil d'auto-évaluation et de quality-gate. Les **dossiers de référence des années antérieures ont été validés par l'administration** : leurs scores fixent la **baseline** (le niveau « ça passe »). Le dossier de l'année courante doit **égaler ou dépasser** la baseline sur chaque axe avant dépôt.

Notation **itérative** : pour chaque axe sous le plancher, appliquer l'action corrective indiquée, réécrire, re-noter. Ne pas s'arrêter à la note — produire l'action.

## Les 8 axes (chacun /10)

| # | Axe | Ce qu'on mesure | Action corrective si faible |
|---|---|---|---|
| 1 | **Éligibilité Frascati** | Les 5 critères démontrés (pas seulement affirmés), avec preuve par critère | Reprendre le tableau Frascati, ancrer chaque ligne sur un fait du dossier (pas une généralité) |
| 2 | **État de l'art & sourcing** | Références réelles et vérifiées, analyse critique des limites, démonstration du *gap*, antériorité au lancement | Ajouter des références vérifiées (cf. `05-bibliographie...`), expliciter pourquoi chaque source ne résout pas le problème |
| 3 | **Verrou & incertitude** | Verrou nommé et chiffré ; pourquoi l'issue n'était pas garantie ; distinction défi/verrou | Reformuler en « contrainte chiffrée + pourquoi l'état de l'art échoue + conséquence » ; passer le test de l'expert |
| 4 | **Démarche expérimentale** | Hypothèses → protocole → tests → analyse ; itérations ; **échecs valorisés** | Documenter les impasses (prototypes successifs) et la boucle de rétroaction entre prototypes |
| 5 | **Preuves & résultats chiffrés** ⚠️ | Benchmarks, métriques, données réelles, comparatifs quantifiés | Injecter les chiffres réels (latences, nb d'événements, gains ×N) ; remplacer tout « significatif/important » par une mesure |
| 6 | **Justification RH & temps** | Qualifications/diplômes, jours-homme cohérents, lien personnel↔travaux, feuilles de temps non forfaitaires | Aligner le xlsx jours-homme avec les fiches de poste et les feuilles de temps datées ; exclure le non-R&D |
| 7 | **Conformité formelle** | Identification entreprise, PME, trame officielle (4 sections), annexes, fil rouge pluriannuel, sous-traitant agréé | Vérifier la présence des 4 sections de la trame officielle, l'agrément du sous-traitant, le renvoi aux dossiers antérieurs |
| 8 | **Figures & lisibilité** | Schémas probants (archi, flux, ERD, organigramme, frise), style technico-administratif maîtrisé | Produire les figures manquantes (cf. `figures/GUIDE-figures.md`), légender et sourcer chacune |

## Baseline (dossiers de référence validés) et plancher de l'année courante

> Ces notes /10 sont des **estimations internes rétro-attribuées** aux dossiers de référence (validés par l'administration) — pas des notes officielles : l'administration ne note pas sur 10. Elles servent de repère de qualité interne, pas de barème administratif.

Renseigner les deux colonnes de référence avec les notes attribuées aux dossiers validés des années antérieures. Le plancher de l'année courante se cale sur ces notes (égaler ou dépasser) ; on peut le relever sur les axes à renforcer.

| Axe | Dossier réf. N-2 | Dossier réf. N-1 | **Plancher** |
|---|:---:|:---:|:---:|
| 1. Frascati | [note dossier réf.] | [note dossier réf.] | **≥ baseline** |
| 2. État de l'art | [note dossier réf.] | [note dossier réf.] | **≥ baseline** |
| 3. Verrou & incertitude | [note dossier réf.] | [note dossier réf.] | **≥ baseline** |
| 4. Démarche expérimentale | [note dossier réf.] | [note dossier réf.] | **≥ baseline** |
| 5. Preuves chiffrées | [note dossier réf.] | [note dossier réf.] | **≥ baseline** ⚠️ souvent point faible historique |
| 6. RH & temps | [note dossier réf.] | [note dossier réf.] | **≥ baseline** |
| 7. Conformité formelle | [note dossier réf.] | [note dossier réf.] | **≥ baseline** + trame officielle à jour |
| 8. Figures & lisibilité | [note dossier réf.] | [note dossier réf.] | **≥ baseline** |
| **Moyenne** | **[note dossier réf.]** | **[note dossier réf.]** | **viser ≥ baseline** |

**Lecture stratégique :** quand les dossiers de référence validés sont faibles sur un axe (le plus souvent l'**axe 5, preuves chiffrées**), c'est la marge de progression la plus nette. Conserver et étoffer les benchmarks réels du brouillon fait monter cet axe de façon décisive. L'axe 6 (RH/temps) gagne en alignant le xlsx jours-homme avec des feuilles de temps réelles.

## Procédure

1. Noter le dossier courant sur les 8 axes, **justifier chaque note en 1 phrase** (preuve à l'appui, pas d'impression).
2. Comparer au plancher. Tout axe sous le plancher → bloquant.
3. Appliquer l'action corrective de la colonne 4, réécrire la section concernée.
4. Re-noter les axes touchés. Itérer jusqu'à ce que tous les axes ≥ plancher et la moyenne ≥ baseline.
5. Restituer un **tableau radar final** (axe / note / plancher / verdict / action restante éventuelle) + 3 forces et 3 faiblesses résiduelles.

> Ces notes sont une aide à la décision interne, pas une garantie d'acceptation par l'administration. Elles calibrent la qualité par rapport à des dossiers réellement validés ; elles ne remplacent pas un rescrit (cf. `01-exigences-officielles.md` §6).

---

# Radar B — qualité rédactionnelle (par paragraphe / par section)

Le radar A note le **fond** (éligibilité, preuves…). Le radar B note la **forme** : un dossier juste mais illisible passe mal. À appliquer paragraphe par paragraphe pendant la rédaction, en bouclant jusqu'à « très bon partout » (cible **≥ 9/10** sur chaque axe).

| Axe | Mesure | Action corrective si faible |
|---|---|---|
| 1. **Lisibilité / fluidité** | Phrases courtes, un rythme, on suit sans relire | Couper les phrases longues (1 idée = 1 phrase), sortir les citations du milieu des phrases |
| 2. **Clarté & accessibilité** | Facile à suivre, pas surchargé, « pas trop de plus-value » | Dégraisser, supprimer le jargon non introduit, expliciter l'implicite |
| 3. **Langue française** | Correction, sobriété, pas d'anglicisme inutile | Relire à voix haute, simplifier le vocabulaire savant |
| 4. **Auto-suffisance** | Chaque notion nécessaire est posée ; se comprend seul | Introduire le concept manquant (avec figure si besoin) avant de l'employer |
| 5. **Justesse / rigueur** | Exact, citations bien placées, pas d'esbroufe | Adosser chaque affirmation forte à une preuve ; retirer le décoratif |
| 6. **Enchaînement & fil conducteur** | Transitions explicites entre sections ; déroulé cumulatif ; le *pourquoi de la R&D* ressort | Ajouter une phrase de jonction en tête/fin de section ; vérifier que chaque partie prépare la suivante |

**Méthode** : noter chaque paragraphe, lister les axes < 9, réécrire, re-noter. Idéalement, faire relire par un **relecteur en aveugle** (≠ l'auteur) pour l'objectivité. Boucler jusqu'à ce que tous les paragraphes soient ≥ 9 sur les 6 axes.
