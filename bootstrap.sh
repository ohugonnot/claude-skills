#!/usr/bin/env bash
# Installe la config Claude Code depuis ce repo sur la machine courante.
#   git clone https://github.com/ohugonnot/claude-skills ~/claude-skills
#   bash ~/claude-skills/bootstrap.sh
#
# Modèle dotfiles : la config (CLAUDE.md, rules, settings, statusline)
# et les skills sont SYMLINKÉS depuis ce repo → source de vérité unique, zéro dérive.
# Le profil perso est COPIÉ depuis un template (reste local, jamais publié).
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Surchargeable : une installation Max range sa config ailleurs (`CLAUDE_HOME=~/.claude-max bash bootstrap.sh`)
CLAUDE_HOME="${CLAUDE_HOME:-${HOME}/.claude}"
STAMP="$(date +%Y%m%d-%H%M%S)"

say()  { printf '\033[1;34m▸ %s\033[0m\n' "$*"; }
warn() { printf '\033[1;33m! %s\033[0m\n' "$*"; }
ok()   { printf '\033[1;32m✓ %s\033[0m\n' "$*"; }

link() {  # link <src> <dest> ; sauvegarde un fichier réel existant avant de remplacer
  local src="$1" dest="$2"
  if [ -e "$dest" ] && [ ! -L "$dest" ]; then
    mv "$dest" "${dest}.bak-${STAMP}"
    warn "sauvegardé $(basename "$dest") → $(basename "$dest").bak-${STAMP}"
  fi
  ln -sfn "$src" "$dest"
}

# rules/ est un vrai dossier : il mêle les règles du repo et le profil local, qui
# atterrirait dans le repo public si le dossier entier était un symlink.
[ -L "$CLAUDE_HOME/rules" ] && rm "$CLAUDE_HOME/rules"
mkdir -p "$CLAUDE_HOME/hooks" "$CLAUDE_HOME/rules" "$CLAUDE_HOME/skills" "$CLAUDE_HOME/agents"

# 1. Config symlinkée (source = repo) ------------------------------------------
say "Config (CLAUDE.md, rules, settings, statusline)"
link "$REPO_DIR/config/CLAUDE.md"            "$CLAUDE_HOME/CLAUDE.md"
for rule in "$REPO_DIR"/config/rules/*.md; do
  link "$rule" "$CLAUDE_HOME/rules/$(basename "$rule")"
done
link "$REPO_DIR/config/settings.json"        "$CLAUDE_HOME/settings.json"
link "$REPO_DIR/config/hooks/statusline.sh"  "$CLAUDE_HOME/hooks/statusline.sh"
link "$REPO_DIR/config/hooks/guard.sh"       "$CLAUDE_HOME/hooks/guard.sh"
ok "config liée"

# 1 bis. Agents symlinkés ------------------------------------------------------
# Un agent typé coûte le modèle qu'il déclare, là où le général part sur celui de la
# conversation. Leur `description` est chargée à chaque démarrage : la garder courte.
say "Agents (chercheur, mesureur)"
for agent in "$REPO_DIR"/config/agents/*.md; do
  link "$agent" "$CLAUDE_HOME/agents/$(basename "$agent")"
done
ok "agents liés"

# 2. Skills symlinkés (chaque plugin) ------------------------------------------
say "Skills (plugins du marketplace)"
for plugdir in "$REPO_DIR"/plugins/*/; do
  name="$(basename "$plugdir")"
  src="${plugdir}skills/${name}"
  [ -d "$src" ] || { warn "$name : pas de skills/$name, ignoré"; continue; }
  link "$src" "$CLAUDE_HOME/skills/$name"
done
ok "skills liés : $(ls "$REPO_DIR"/plugins | tr '\n' ' ')"

# 3. Profil local : règle sans `paths`, donc chargée à chaque session ----------
# ~/.claude/memory/ n'est lu par rien : la mémoire auto vit dans ~/.claude/projects/.
say "Profil (template → ~/.claude/rules/profil.md si absent)"
if [ ! -e "$CLAUDE_HOME/rules/profil.md" ]; then
  cp "$REPO_DIR/config/profil.example.md" "$CLAUDE_HOME/rules/profil.md"
  warn "profil.md créé depuis le template, à remplir"
fi
ok "profil en place"

echo
ok "Bootstrap terminé."
printf '\n%s\n' \
"À FAIRE À LA MAIN (secrets / état local, non automatisable) :" \
"  - Remplir ~/.claude/rules/profil.md (template posé)." \
"  - Permissions : cp config/settings.local.example.json ~/.claude/settings.local.json puis adapter." \
"  - Auth : gh auth login ; (re)connecter les serveurs MCP." \
"  - Les CLAUDE.md de projet voyagent avec leurs repos git."
