#!/usr/bin/env bash
# Installe la config Claude Code depuis ce repo sur la machine courante.
#   git clone https://github.com/ohugonnot/claude-skills ~/claude-skills
#   bash ~/claude-skills/bootstrap.sh
#
# Modèle dotfiles : la config (CLAUDE.md, go-best-practices, settings, statusline)
# et les skills sont SYMLINKÉS depuis ce repo → source de vérité unique, zéro dérive.
# La mémoire perso est COPIÉE depuis les templates (reste locale, jamais publiée).
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_HOME="${HOME}/.claude"
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

mkdir -p "$CLAUDE_HOME/hooks" "$CLAUDE_HOME/memory" "$CLAUDE_HOME/skills"

# 1. Config symlinkée (source = repo) ------------------------------------------
say "Config (CLAUDE.md, go-best-practices, settings, statusline)"
link "$REPO_DIR/config/CLAUDE.md"            "$CLAUDE_HOME/CLAUDE.md"
link "$REPO_DIR/config/go-best-practices.md" "$CLAUDE_HOME/go-best-practices.md"
link "$REPO_DIR/config/settings.json"        "$CLAUDE_HOME/settings.json"
link "$REPO_DIR/config/hooks/statusline.sh"  "$CLAUDE_HOME/hooks/statusline.sh"
link "$REPO_DIR/config/hooks/guard.sh"       "$CLAUDE_HOME/hooks/guard.sh"
ok "config liée"

# 2. Skills symlinkés (chaque plugin) ------------------------------------------
say "Skills (plugins du marketplace)"
for plugdir in "$REPO_DIR"/plugins/*/; do
  name="$(basename "$plugdir")"
  src="${plugdir}skills/${name}"
  [ -d "$src" ] || { warn "$name : pas de skills/$name, ignoré"; continue; }
  link "$src" "$CLAUDE_HOME/skills/$name"
done
ok "skills liés : $(ls "$REPO_DIR"/plugins | tr '\n' ' ')"

# 3. Mémoire : copie des templates si absente (jamais d'écrasement) ------------
say "Mémoire (templates → copie locale si absente)"
[ -e "$CLAUDE_HOME/memory/MEMORY.md" ] || cp "$REPO_DIR/config/memory/MEMORY.example.md" "$CLAUDE_HOME/memory/MEMORY.md"
[ -e "$CLAUDE_HOME/memory/feedback_simplicity.md" ] || cp "$REPO_DIR/config/memory/feedback_simplicity.md" "$CLAUDE_HOME/memory/feedback_simplicity.md"
for t in user_profile user_env; do
  if [ ! -e "$CLAUDE_HOME/memory/$t.md" ]; then
    cp "$REPO_DIR/config/memory/$t.example.md" "$CLAUDE_HOME/memory/$t.md"
    warn "$t.md créé depuis le template — à remplir"
  fi
done
ok "mémoire en place"

echo
ok "Bootstrap terminé."
printf '\n%s\n' \
"À FAIRE À LA MAIN (secrets / état local, non automatisable) :" \
"  - Remplir ~/.claude/memory/user_profile.md et user_env.md (templates posés)." \
"  - Permissions : cp config/settings.local.example.json ~/.claude/settings.local.json puis adapter." \
"  - Auth : gh auth login ; (re)connecter les serveurs MCP." \
"  - Les CLAUDE.md de projet voyagent avec leurs repos git."
