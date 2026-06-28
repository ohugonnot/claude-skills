# config/ — la couche poste de travail

Ce dossier transforme le repo en bootstrap de machine : `bash bootstrap.sh` à la racine
installe cette config dans `~/.claude/`.

## Modèle
- **Symlinkés** (source de vérité = ce repo, zéro dérive) : `CLAUDE.md`, `go-best-practices.md`,
  `settings.json`, `hooks/statusline.sh`. Tu édites ici, ça se propage.
- **Copiés** (restent locaux, jamais publiés) : la mémoire. Les `*.example.md` sont des templates ;
  `bootstrap.sh` en fait des copies dans `~/.claude/memory/` si absentes.

## Public vs local
Ce repo est **public** : il ne contient que du réutilisable. Tes faits perso (profil réel, chemins
machine, allowlist) vivent en local et sont **gitignored**. Les versions `.example` montrent quoi remplir.

| Fichier | Rôle |
|---|---|
| `CLAUDE.md` | méthodo globale (restrictions, conception, orchestration sous-agents) |
| `go-best-practices.md` | dialecte Go, référencé par `CLAUDE.md` |
| `settings.json` | réglages portables (effort high, mode auto, statusline) |
| `hooks/statusline.sh` | statusline |
| `memory/*.example.md` | templates de mémoire à remplir en local |
| `settings.local.example.json` | template d'allowlist de permissions |
