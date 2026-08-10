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

Workflow en 4 étapes : scanner → dédupliquer → persister → confirmer.
But : qu'une future session retrouve tout ce que cette conversation a appris de non-déductible, et rien d'autre.

## Ce qu'il faut sauvegarder

**Oui — non-déductible du code ou du git :**
- Décisions durables et leur motivation (`project`)
- Gotchas découverts, comportements surprenants, pièges d'outillage (`project`)
- Préférences ou corrections de méthode données par l'utilisateur (`feedback`)
- Qui est l'utilisateur : rôle, expertise, préférences générales (`user`)
- Pointeurs vers ressources externes : URL, dashboard, ticket (`reference`)

**Non — ne pas sauvegarder :**
- Ce qui est lisible dans le code, le git log ou CLAUDE.md
- L'état de la tâche en cours (temporaire par nature)
- Ce qui est déjà en mémoire (vérifier avant d'écrire)
- Les résumés d'activité (« on a fait X aujourd'hui »)
- Les plans et todos de session

Test pour chaque insight : *« une future session pourrait-elle le déduire du dépôt ? »* Si oui → ne pas sauvegarder.

## Procédure

### 1. Scanner la conversation

Parcourir tous les échanges, en particulier les corrections de trajectoire données par l'utilisateur (ce sont souvent les meilleurs `feedback`). Convertir les dates relatives (« hier », « la semaine prochaine ») en dates absolues.

### 2. Localiser la mémoire et dédupliquer

- **Chemin** : celui annoncé par le harnais dans le contexte (system-reminder mémoire) s'il y en a un. Sinon : `~/.claude/projects/<chemin-encodé>/memory/`, où le chemin encodé est le répertoire du projet avec chaque `/` remplacé par `-` (ex. `/data/work/cv` → `-data-work-cv`).
- Lire `MEMORY.md` (l'index). Pour chaque insight : si un fichier couvre déjà le sujet → **mettre à jour ce fichier** plutôt que créer un doublon. Une mémoire devenue fausse se corrige ou se supprime : c'est une mise à jour légitime.

### 3. Écrire les mémoires

Un fichier = un fait. Format aligné sur le harnais :

```markdown
---
name: slug-court-en-kebab
description: Une ligne — c'est elle qui décide si la mémoire sera rappelée plus tard
metadata:
  type: user | feedback | project | reference
---

Le fait, factuel et autonome.

**Why:** la raison ou le contexte (pour feedback/project).
**How to apply:** quand et comment l'appliquer.
```

- Lier les mémoires connexes avec `[[slug-de-l-autre]]`.
- Mettre à jour `MEMORY.md` : une ligne par mémoire, format `- [Titre](fichier.md) — accroche`. L'index est chargé à chaque session : une ligne par entrée, jamais le contenu.

### 4. Confirmer et rendre la main

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
