# config/ — la couche poste de travail

Ce dossier transforme le repo en bootstrap de machine : `bash bootstrap.sh` à la racine
installe cette config dans `~/.claude/`.

## Modèle
- **Symlinkés** (source de vérité = ce repo, zéro dérive) : `CLAUDE.md`, `rules/`,
  `settings.json`, `hooks/statusline.sh`. Tu édites ici, ça se propage.
- **Copié** (reste local, jamais publié) : le profil. `profil.example.md` est un template ;
  `bootstrap.sh` le copie en `~/.claude/rules/profil.md` s'il est absent. Une règle sans `paths:`
  se charge à chaque session, là où l'ancien `~/.claude/memory/` n'était lu par rien.

## Public vs local
Ce repo est **public** : il ne contient que du réutilisable. Tes faits perso (profil réel, chemins
machine, allowlist) vivent en local et sont **gitignored**. Les versions `.example` montrent quoi remplir.

| Fichier | Rôle |
|---|---|
| `CLAUDE.md` | méthodo globale (restrictions, conception, orchestration sous-agents) |
| `rules/` | règles chargées seulement sur les fichiers qu'elles visent (`paths:`) : Go, écriture d'agents et de skills |
| `settings.json` | réglages portables (effort high, mode auto, statusline) |
| `hooks/statusline.sh` | statusline |
| `profil.example.md` | template du profil local (shell, OS, chemins), copié par `bootstrap.sh` |
| `settings.local.example.json` | template d'allowlist de permissions |
