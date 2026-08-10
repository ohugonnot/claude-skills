# Gabarit exemple — structure, boilerplate, fil rouge

Issu de la dissection de dossiers **validés** par l'administration. À réutiliser comme matrice de style et de structure — **jamais en copier-coller intégral** (motif de rejet). Réinstancier le fond chaque année.

## Sommaire

- [Structure stable du dossier](#structure-stable-du-dossier)
- [Le fil rouge pluriannuel (réutilisable)](#le-fil-rouge-pluriannuel-reutilisable)
- [Boilerplate réutilisable (à réinstancier, pas à copier tel quel)](#boilerplate-reutilisable-a-reinstancier-pas-a-copier-tel-quel)
- [Tableau Frascati (structure fixe — voir `templates/table-frascati.md`)](#tableau-frascati-structure-fixe-voir-templatestable-frascatimd)
- [Équipe R&D (gabarit — recouper avec le xlsx de l'année)](#equipe-rd-gabarit-recouper-avec-le-xlsx-de-lannee)
- [Style maison](#style-maison)
- [Figures par année (à reproduire/actualiser — voir `figures/GUIDE-figures.md`)](#figures-par-annee-a-reproduireactualiser-voir-figuresguide-figuresmd)

## Structure stable du dossier

```
Page de garde — société, objet, correspondant DGFIP nommé, contacts R&D, logo
1. INTRODUCTION
   1.1 Identification de l'entreprise (tableau : SIREN, APE, forme, effectif total + R&D, CA, bilan, statut PME, SIE)
   1.2 Coordonnées des interlocuteurs R&D (fiches DAF + CTO)
   1.3 Répartition du capital (cascade actionnariale)
   1.4 Caractère de PME au sens communautaire (Règl. UE 651/2014 ; renvoi annexe table de capi)
   1.5 Domaine d'activité et localisation (codes APE/secteur, mots-clés [SECTEUR], France/EEE)
2. PRÉSENTATION DE LA SOCIÉTÉ ET DE SES ACTIVITÉS DE R&D
   2.1 Historique  → 2.1.1 Histoire (depuis [ANNÉE]) | 2.1.2 Bios dirigeants | 2.1.3 Comité de Surveillance
   2.2 Secteur d'activités & modèle d'affaires
   2.3 Environnement concurrentiel (3-4 concurrents + différenciateurs)
   2.4 Activités de R&D → 2.4.1 Origine | 2.4.2 Comité scientifique | 2.4.3 Équipe R&D (organigramme + bios + sous-traitant agréé éventuel) | 2.4.4 Indicateurs Frascati
3. FICHE DESCRIPTIVE DU PROJET  ← cœur scientifique
   Tableau identification opération « [OPÉRATION] » (identifiant, dates depuis [ANNÉE], volume horaire, domaines/codes)
   Contexte général (récap année N-1 + pivot vers problématique N)
   Verrou scientifique/technique
   État de l'art
   Démarche scientifique détaillée (par prototype)
   Résultats de l'opération
   Indicateurs de recherche (tableau Frascati)
Bibliographie (numérotée [1]…[n], citée inline)
Annexe 1 — Définitions et mots-clefs (termes marqués * dans le corps)
Annexe 2 — Logiciels de veille (⚠️ moyen, plus une dépense éligible depuis LFI 2025)
Annexe externe — Activités R&D du sous-traitant agréé éventuel (document séparé)
```

> **Mapping vers la trame officielle 2025 (4 sections de la fiche-opération)** : section C.1 = Contexte général + État de l'art ; C.2 = Verrou ; C.3 = Démarche par prototypes ; C.4 = Résultats + indicateurs Frascati. La partie 1-2 du gabarit alimente A. Présentation entreprise + D. RH.

## Le fil rouge pluriannuel (réutilisable)

Opération unique « **[OPÉRATION]** », ouverte en **[ANNÉE]**, jamais clôturée. Axe constant : le cœur métier de l'entreprise dans [SECTEUR]. Le tableau ci-dessous illustre **la mécanique** d'un fil rouge (années N-2 → N-1 → N) : chaque brique technique est introduite une année, renforcée la suivante, puis devient le verrou d'une année. À réinstancier avec les briques réelles de l'entreprise.

| Élément (exemple illustratif) | Statut |
|---|---|
| Paradigme technique central de l'opération | Introduit N-2, renforcé N-1, **au cœur du verrou N** |
| Composant technique propriétaire | Conçu N-1 |
| Contrainte structurante (sécurité / intégrité / ségrégation) | Verrou central N-1 |
| Axe technique historique | Axe constant depuis [ANNÉE] |
| Brique fonctionnelle | N-2 (première version) → N-1 (version étendue) |
| Difficulté de l'année N (industrialisation à l'échelle) | **Verrou N** (plusieurs prototypes) |
| Cadre réglementaire applicable | Fil rouge réglementaire constant |

**Problématique centrale (forme canonique à instancier)** :
> *Comment concevoir [LE DISPOSITIF TECHNIQUE] qui soit **industrialisable en production** — soutenant la volumétrie réelle et les performances requises (traitement en quasi temps réel d'une opération critique) — **tout en préservant** les contraintes non négociables du domaine (traçabilité, intégrité, conformité réglementaire) ?*

Chaîne de raisonnement auto-suffisante (à dérouler dans C.1) : besoin métier régulé → contrainte forte (traçabilité/intégrité auditable) → une architecture donnée s'impose naturellement → mais la forte volumétrie en fait exploser le coût → la solution naïve ne passe pas en production → problématique. La contrainte réglementaire joue un **double rôle** : elle justifie le choix d'architecture ET interdit les raccourcis de mise à l'échelle (tronquer les données, dégrader l'intégrité), ce qui rend le verrou réellement dur.

**Sous-questions = un prototype chacune (exemple illustratif d'une trajectoire à 3 prototypes)** : (1) approche canonique selon l'état de l'art → échec de scalabilité ; (2) optimisation inédite pour réduire la charge → non viable (effet de bord sur les ressources) ; (3) rupture avec l'orthodoxie du domaine → prometteur. *L'incertitude centrale du dernier prototype porte sur la tenue en temps réel et la cohérence de la solution de rupture.*

## Boilerplate réutilisable (à réinstancier, pas à copier tel quel)

**Présentation société :**
> « Depuis [ANNÉE], [ENTREPRISE] développe [PRODUIT], une solution technologique innovante dans [SECTEUR]. Cette initiative répond à une demande croissante pour des solutions à la fois sécurisées, conformes et traçables, dans un secteur marqué par une forte évolution réglementaire. »

**Socle R&D (liste d'axes — à remplir avec les axes réels de l'entreprise) :** [AXE 1] · [AXE 2] · [AXE 3] · [AXE 4] · [AXE 5].

**Transition pluriannuelle (gabarit à instancier) :**
> « En [N-1], les travaux ont porté sur [RÉSUMÉ N-1]. Ces travaux ont permis de tester différents choix d'architecture et de modélisation, tout en identifiant certaines limites structurelles liées à [LIMITE]. Ces constats ont fourni une base analytique robuste, sur laquelle se sont appuyés les travaux menés en [N]. »

**Formule de verrou :**
> « C'est précisément ce verrou — [DESCRIPTION] — qui a motivé notre démarche de R&D. À notre connaissance, aucune solution existante ne permet aujourd'hui d'atteindre cet objectif sans compromis significatif sur la performance, la scalabilité ou les contraintes du domaine. »
> « Ce travail ne pouvait s'appuyer sur aucune solution éprouvée ni sur une littérature documentée. Il s'agissait d'un problème inédit, dont la résolution nécessitait de concevoir ex nihilo [SOLUTION], capable de concilier des objectifs a priori contradictoires : [O1], [O2], [O3]. »

**Incertitudes :**
> « Dès les premières phases exploratoires, notre équipe R&D a été confrontée à plusieurs incertitudes critiques liées à la nature inédite du modèle envisagé. Une première incertitude tenait à l'absence de référence technique ou scientifique sur [SUJET]. Aucun retour d'expérience ou benchmark ne permettait d'anticiper le comportement d'un tel système à l'échelle, ni les effets sur la latence, la cohérence transactionnelle ou la consommation de ressources. »

**Clôture R&D :**
> « Ce projet s'inscrit pleinement dans le champ de la R&D tel que défini par le ministère de la Recherche : il repose sur la résolution d'un verrou technique non documenté, dans un cadre réglementaire émergent, par des moyens non standards, sans résultat connu d'avance, et avec une forte incertitude sur la faisabilité initiale de la solution retenue. »

**Originalité / absence d'équivalent :**
> « Aucune littérature scientifique n'ayant été trouvée pour des travaux équivalents, cela souligne l'originalité de notre approche. »
> « Aucun système existant ne dispose de ce type de mécanisme. »

**Transférabilité :**
> « Au-delà de ses applications immédiates, les avancées réalisées présentent un fort potentiel de réutilisation dans d'autres environnements distribués à forte volumétrie et exigences réglementaires strictes (services financiers, assurance, santé). »

**Verrou formulé en question de recherche (forme efficace) :**
> « Est-il possible de maintenir dans le temps [LA PROPRIÉTÉ CRITIQUE] à très grande échelle dans [L'ARCHITECTURE RETENUE] ? »

## Tableau Frascati (structure fixe — voir `templates/table-frascati.md`)
Cinq lignes : Nouveauté / Créativité / Incertitude / Systématicité / Transférabilité-Reproductibilité, colonne « Projet – [OPÉRATION] », chaque cellule instanciée sur le verrou de l'année.

## Équipe R&D (gabarit — recouper avec le xlsx de l'année)

Remplir une ligne par personne. Marquer explicitement les personnes qui **ne participent pas** à la R&D (à exclure de l'assiette) et le **sous-traitant agréé éventuel** (document R&D séparé). Aucun vrai nom dans ce gabarit : les lignes ci-dessous sont des exemples de format.

| Personne | Fonction | Diplôme/Qualif | Rôle R&D | Jours-homme |
|---|---|---|---|---|
| [Nom] | Lead dev | [diplôme + établissement] | Conception du verrou et mise au point des prototypes | … |
| [Nom] | CTO | [diplôme + établissement] | Responsable R&D opérationnel | … |
| [Nom] | [fonction support] | [diplôme] | **Ne participe PAS à la R&D** (à exclure explicitement) | — |
| [Nom] | Sous-traitant agréé éventuel | [agrément CIR] | Travaux R&D externalisés ; document séparé | … |

**Format bios** : diplôme(s) datés + établissement → parcours chronologique → « rejoint [ENTREPRISE] en [année] » → paragraphe rôle R&D spécifique. ~150-300 mots (dirigeants), plus court pour les collaborateurs.

## Style maison
- Registre technico-administratif soutenu, incursions scientifiques pour l'état de l'art. Audience = évaluateur technique compétent mais **pas forcément spécialiste du domaine** : le dossier doit être **auto-suffisant** — introduire les concepts clés une fois (rappel du paradigme central sourcé + figure), puis rester technique. Ni vulgarisation excessive, ni présupposé d'expertise pointue. Termes pointus définis en Annexe 1.
- Personne : 3e personne (« les équipes de recherche de [ENTREPRISE] ») alternant avec « nous » dans les sections de démarche (incarne le chercheur).
- Temps : passé composé (travaux réalisés), présent (constats/état de l'art), conditionnel (perspectives/incertitudes).
- Phrases longues, structurées en listes dans les passages techniques.
- **Honnêteté assumée sur les limites et échecs** — trait stylistique qui renforce la crédibilité (« résultats non totalement satisfaisants », « non scalable »).

## Figures par année (à reproduire/actualiser — voir `figures/GUIDE-figures.md`)
- **Année N-2 (exemple : 12 figures)** : organigramme R&D, schémas illustrant le fonctionnement métier (états successifs), ERD itératifs v1→v2→v3, diagramme de flux, tableau de données réelles, schéma d'architecture, logo.
- **Année N-1 (exemple : 8 figures)** : organigramme R&D, tableau personnel R&D, schémas comparatifs des options d'architecture, schéma d'architecture du processus, diagramme événementiel, flux d'orchestration, logo.
- **Année N (à produire)** : organigramme R&D actualisé · schéma de l'architecture du dispositif retenu (dernier prototype) · diagramme de flux/événementiel · courbe de dégradation des performances (prototype en échec : métrique vs charge) · frise des prototypes avec verdict · éventuellement tableau de benchmarks comparés des prototypes.
