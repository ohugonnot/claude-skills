# Changelog — tech-article

## 1.4.0 — 2026-10-28

Nouvelle section « Companion code », qui ajoute à l'article un petit POC public que le lecteur peut lancer :
- Le dépôt d'abord, l'article ensuite. Les extraits sont copiés du dépôt tels quels, et les liens sont figés sur un commit.
- Ce que le dépôt doit avoir : tests, dont un vu au rouge, test de bout en bout, CI, et un README honnête sur ce qui est vérifié.
- Trois blocs dans l'article : l'encart dépôt avec son registre de preuves Vérifié / Non vérifié, le renvoi au fichier complet sous chaque extrait, et « les livres derrière l'article ».

« Lean build circuit » : un POC d'observabilité en Go a coûté environ 1,9 M tokens d'agents sur 4 tours de revue. Le tour 1 trouvait surtout des oublis prévisibles, et chaque série de corrections nourrissait le tour suivant. Le circuit retenu :
- un plan avec une definition of done écrite d'avance ;
- le code sur le modèle standard ;
- un seul tour de revue à 3 relecteurs aveugles, dont un seul lance la pile ;
- une passe finale aveugle sur un autre modèle, jamais le plus cher sans demande ;
- l'arrêt quand il ne reste ni bloquant ni important, avec deux tours au plus ;
- l'article écrit en parallèle de la revue.

## 1.3.0 — 2026-10-27

Règles tirées des corrections d'un relecteur humain sur un texte pédagogique, chacune vérifiable :

- **Fluidité 8-11** : une idée par phrase et la cause en toutes lettres (plus de 25 mots ou deux relatives = couper) ; nommer au lieu de pointer (pas de pronom en tête de paragraphe, un renvoi nomme ce qu'il vise) ; une définition longue sort de la phrase qui raisonne, deux termes nouveaux par paragraphe au plus ; une formule citée se redit en clair juste après.
- **Titres** : une affirmation courte qui frappe et nomme son objet, jamais la redite de la citation ou de la phrase dessous.
- **Workflow** : une règle découverte en relisant se relance sur tout le brouillon ; un ajout de relecture repasse la coupe (une idée ne vit qu'à un endroit).
- Checklist : une ligne de contrôle mécanique des phrases.

## 1.2.1 — 2026-08-10

- **Puce SEO générique retirée** : « Internal links with descriptive anchors, never "click here" » est une évidence qu'un rédacteur compétent applique sans qu'on l'écrive — ligne no-op au sens de la doctrine maison. La puce image gagne en revanche un critère vérifiable : l'alt décrit ce que montre l'image plutôt que de la nommer.
- La section SEO est **conservée** : la description couvre « writing or publishing », la publication est donc dans le périmètre déclaré.

## 1.2.0 — 2026-08-10

- **Description à la 3e personne** : « and you want it to read like a human » adressait l'utilisateur — anti-pattern officiel Anthropic. Reformulée en « a technical blog article that should read like a human engineer wrote it ».
- **Déclencheur élargi** : ajout de « even when the word "article" never appears ».

## 1.1.0 — 2026-06-16

- **Section "Self-contained — non-negotiable"** : l'article doit être lisible par quelqu'un qui n'a rien lu d'autre de l'auteur — définir tout terme/outil/concept avant de l'utiliser, annoncer explicitement une suite et résumer le prérequis en une phrase.
- **Anti-slop FR étendu** : ajout de "Comme nous l'avons vu précédemment", "Il faut noter que", "En résumé, voici les points clés", et des variations en boucle de "permettre de".

## 1.0.0 — 2026-06-14

- Version initiale : méthode "histoire qui contient de la technique" — hook in medias res, structure 4-6 H2, patterns anti-slop EN/FR, rythme de phrase, diagramme seulement s'il gagne sa place.
