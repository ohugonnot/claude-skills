<!--
Gabarit d'un prototype dans la section C.3 « Travaux réalisés et démarche ».
Structure éprouvée. Réinstancier sur VOTRE verrou, ne pas copier.
Un prototype = une boucle hypothèse → test → résultat → décision.
-->

### Prototype [N] — [TITRE]

**Hypothèse de recherche.**
[Quelle idée on teste et pourquoi elle est plausible au vu de l'état de l'art. Ancrer dans un principe technique, pas dans un objectif business.
Ex. (exemple illustratif) : « Le composant critique faisant partie des invariants métier, la solution naturelle consiste à le modéliser au niveau du module central, conformément aux principes de conception classiques du domaine. »]

**Mise en œuvre.**
[Ce qui a été construit : architecture, interfaces, outils, langage, jeux de données de test. Assez précis pour être reproductible.
Ex. (exemple illustratif) : « Chaque opération génère un enregistrement horodaté contenant les attributs métier nécessaires au calcul. »]

**Incertitudes, difficultés et aléas.**
[Ce qui n'était pas prévisible (incertitude) / ce qui était dur (difficulté) / ce qui dépendait de facteurs externes (aléa).
Marqueurs : « la faisabilité n'était pas garantie », « aucun benchmark ne permettait d'anticiper le comportement à l'échelle ».]

**Résultats — CHIFFRÉS.**
[Mesures réelles : latences, volumétrie traitée, temps de traitement, gains ×N. C'est l'axe 5 du radar — ne jamais écrire « significatif » sans chiffre.
Ex. (exemple illustratif) : « Un jeu de [X] éléments nécessite [Y] s de traitement ; à [10·X] éléments, le temps dépasse [Z] s — incompatible avec la cible. »
Conclure honnêtement : succès partiel, limite atteinte, échec assumé.]

**Décision — ce qui motive le prototype suivant.**
[La boucle de rétroaction R&D : « Cette limite a conduit à l'abandon de cette approche et à l'exploration de [PROTOTYPE N+1]. »]

---

<!-- Schéma de progression attendu (exemple illustratif, à remplacer par VOS prototypes) :
 1. Première approche directe → fonctionnelle MAIS ne passe pas à l'échelle. ÉCHEC.
 2. Approche alternative → réduit le coût MAIS introduit un nouvel effet de bord. NON VIABLE.
 3. Approche hybride → atteint la cible de performance, gain mesuré. PROMETTEUR, incertitudes ouvertes (cohérence, auditabilité, migration).
 Les échecs 1 et 2 PROUVENT l'incertitude : les valoriser, ne pas les masquer. -->
