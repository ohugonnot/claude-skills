#!/usr/bin/env bash
# PreToolUse guard — applique les règles dures du CLAUDE.md (enforcement, pas suggestion).
# FAIL-OPEN : toute incertitude ou erreur => autorise (exit 0). Seule une violation
# confirmée bloque (exit 2, raison sur stderr). Un bug du hook ne bloque JAMAIS un outil.
# Lit le JSON Claude Code sur stdin UNE SEULE FOIS.
set +e

INPUT=$(cat 2>/dev/null) || exit 0
command -v jq >/dev/null 2>&1 || exit 0   # pas de jq => on ne peut pas parser => autorise

tool=$(printf '%s' "$INPUT" | jq -r '.tool_name // empty' 2>/dev/null) || exit 0

block() { printf 'BLOQUÉ par hook (règle CLAUDE.md) : %s\n' "$1" >&2; exit 2; }

# Vrai si le chemin est un fichier de secrets à protéger (hors exceptions *.example).
is_secret_path() {
  local base; base=$(basename -- "$1" 2>/dev/null) || return 1
  case "$base" in
    *.example|*.example.*|*.sample|*.sample.*|*.template|*.dist) return 1 ;;
  esac
  case "$base" in
    .env|.env.*|*.pem|*.key|id_rsa|id_ed25519|*.p12|*.pfx|*credentials*|*secret*) return 0 ;;
  esac
  return 1
}

case "$tool" in
  Read)
    path=$(printf '%s' "$INPUT" | jq -r '.tool_input.file_path // empty' 2>/dev/null) || exit 0
    [ -n "$path" ] || exit 0
    is_secret_path "$path" && block "lecture d'un fichier de secrets ($path). Exception autorisée : *.example."
    ;;
  Bash)
    cmd=$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null) || exit 0
    [ -n "$cmd" ] || exit 0
    # contournement des hooks git
    printf '%s' "$cmd" | grep -Eq -- '--no-verify|core\.hooksPath=' \
      && block "contournement des hooks git (--no-verify / core.hooksPath interdit)."
    # lecture d'un .env via shell (hors *.example/.sample/...)
    if printf '%s' "$cmd" | grep -Eq -- '(^|[|&;[:space:]])(cat|less|more|head|tail|bat|xxd|od|strings|nl)[[:space:]]+[^|&;]*\.env([[:space:]]|$|\.)'; then
      printf '%s' "$cmd" | grep -Eq -- '\.env\.(example|sample|template|dist|local\.example)' || \
        block "lecture d'un .env via shell. Exception autorisée : *.example."
    fi
    ;;
esac
exit 0
