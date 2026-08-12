---
name: vide-contexte
description: >-
  Persists a conversation's non-obvious insights into memory files before its context is cleared
  or compacted — nothing is cleared by this skill, only saved. Use when the user says "vide le
  contexte", "clear context", "vide le context", "sauvegarde avant /clear", "save context before
  clearing" or similar, even when they only announce the /clear without asking to save. NOT for
  closing out a branch (use branch-wrap-up, which runs its own knowledge-capture pass).
---

# Persister le contexte avant de le vider

Workflow en 4 étapes : scanner → dédupliquer → persister → vérifier.
But : qu'une future session retrouve tout ce que cette conversation a appris de **non-déductible**, et rien d'autre.

Deux règles gouvernent tout le reste. **Non-déductible** décide de ce qu'on écrit. **Le mécanisme, pas l'instantané** décide de comment on l'écrit — c'est ce qui fait qu'une mémoire vaut encore quelque chose dans six mois.

## Ce qu'il faut sauvegarder

**Oui — non-déductible du code ou du git :**
- Décisions durables et leur motivation (`project`)
- Gotchas découverts, comportements surprenants, pièges d'outillage (`project`)
- Préférences ou corrections de méthode données par l'utilisateur (`feedback`)
- Qui est l'utilisateur : rôle, expertise, préférences générales (`user`)
- Pointeurs vers ressources externes : URL, dashboard, ticket (`reference`)

**Non — ne pas sauvegarder :**
- Ce qui est lisible dans le code, le git log ou CLAUDE.md
- L'état daté d'une MR, d'une issue ou d'une tâche (« pushée », « pas encore mergée », « reste à faire ») — voir la règle ci-dessous
- Ce qui est déjà en mémoire (vérifier avant d'écrire)
- Les résumés d'activité (« on a fait X aujourd'hui »)
- Les plans et todos de session

Test pour chaque insight : *« une future session pourrait-elle le déduire du dépôt ? »* Si oui → ne pas sauvegarder.

## La règle anti-pourrissement : le mécanisme, pas l'instantané

Un chantier produit deux choses : un **état** (où on en est) et un **savoir** (ce qu'on a compris). L'état pourrit en quelques semaines, le savoir non. N'écrire que le second.

```
✗ « !357 pas encore mergée, reste la review humaine »   → faux dans dix jours
✓ « tout rollup est pondéré base volume »                → vrai tant que le code l'est
```

Cette règle vaut **aussi et surtout pour la `description:`** — c'est elle qui décide du rappel. Une description qui dit « MR pushée, à retargeter » enverra un signal faux longtemps après le merge.

Quand l'insight porte vraiment sur un chantier en cours, écrire ce qui lui survivra : la décision prise et son pourquoi, l'arbitrage tranché, le piège rencontré. Pas le numéro de MR ni son statut.

## Procédure

### 1. Scanner la conversation

Parcourir tous les échanges, en particulier les corrections de trajectoire données par l'utilisateur (ce sont souvent les meilleurs `feedback`). Convertir les dates relatives (« hier », « la semaine prochaine ») en dates absolues.

### 2. Localiser la mémoire et dédupliquer

- **Chemin** : celui annoncé par le harnais dans le contexte (system-reminder mémoire) s'il y en a un. Sinon : `~/.claude/projects/<chemin-encodé>/memory/`, où le chemin encodé est le répertoire du projet avec chaque `/` remplacé par `-` (ex. `/data/work/cv` → `-data-work-cv`).
- Lire `MEMORY.md` (l'index). Si un fichier couvre déjà le sujet → **mettre à jour ce fichier** plutôt que créer un doublon.
- **Chercher la contradiction, pas seulement le doublon** : deux mémoires peuvent traiter des sujets différents et se contredire sur un fait (un mot de passe « non stocké » ici, « dans tel fichier » là). Avant d'écrire un fait, `grep` le corpus sur son mot-clé.
- Une mémoire devenue fausse se corrige ou se supprime : c'est une mise à jour légitime.

### 3. Écrire les mémoires

Un fichier = un fait.

**Nom de fichier** : `<type>_<slug>.md` — `feedback_`, `project_`, `reference_`, `user_`. Le slug en minuscules, mots séparés par `_`.

```markdown
---
name: slug-en-kebab-identique-au-nom-de-fichier-sans-le-préfixe
description: Une ligne — c'est elle qui décide si la mémoire sera rappelée plus tard
metadata:
  type: user | feedback | project | reference
---

Le fait, factuel et autonome.

**Why:** la raison ou le contexte (pour feedback/project).
**How to apply:** quand et comment l'appliquer.
```

- **`name` = le nom de fichier sans son préfixe, underscores en tirets.** `project_pricing_resolver.md` → `name: pricing-resolver`. C'est cette valeur que visent les liens : un `name` en prose ou divergent rend toutes les références vers cette mémoire mortes, silencieusement.
- **Vérifier ce qu'on cite** : tout chemin, symbole ou commande écrit dans une mémoire se vérifie avant d'être écrit (`test -e`, `grep`). Un renommage invalide des dizaines de mémoires sans que rien ne signale l'erreur.
- Lier les mémoires connexes avec `[[slug]]` — le même slug que le `name` de la cible. Un lien sans cible existante est acceptable : il marque une mémoire à écrire plus tard.
- Mettre à jour `MEMORY.md` : `- [Titre](fichier.md) — accroche`. **L'accroche fait ~80 caractères**, jamais plus de 100 : elle sert à décider s'il faut ouvrir le fichier, pas à dispenser de l'ouvrir. L'index est payé à chaque session ; le corps des mémoires ne l'est que sur rappel — mettre le volume dans le corps.

**En supprimant une mémoire**, retirer aussi sa ligne d'index **et** les `[[liens]]` qui la visaient depuis les autres fichiers (`grep -l` sur son slug). Une suppression sans ce nettoyage laisse des liens morts.

### 4. Vérifier, puis confirmer

Avant de rendre la main, contrôler le travail — ces quatre points sont mécaniques :

- [ ] Chaque fichier écrit ou modifié a `name`, `description` et `metadata.type`. Sans `description`, la mémoire ne sera **jamais** rappelée.
- [ ] Chaque `name` correspond à son nom de fichier (préfixe retiré, `_` → `-`).
- [ ] Aucune `description` ni aucun corps ne porte un état daté de MR ou d'issue.
- [ ] `MEMORY.md` contient une ligne par fichier écrit, et plus aucune ligne vers un fichier supprimé.

```
Sauvegardé :
- [feedback_style] <résumé en 1 ligne>
- [project_xxx] <résumé en 1 ligne>
Mis à jour : [project_yyy]

→ /clear (ou /compact pour garder un résumé)
```

Si rien ne mérite d'être sauvegardé, le dire tel quel (« rien de non-déductible à persister ») : un faux souvenir coûte plus cher qu'une absence.

## Ce que ce skill NE fait PAS

- Ne commit pas, ne push pas
- Ne modifie pas CLAUDE.md (sauf demande explicite)
- Ne lance pas `/clear` lui-même : c'est l'utilisateur qui décide
- Ne sauvegarde pas les plans, todos ou états de session
