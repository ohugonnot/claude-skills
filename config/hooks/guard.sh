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
    # Budget de lecture : un Read intégral est relu à chaque tour suivant, donc il se
    # repaie des centaines de fois. Au-delà du seuil, exiger une plage.
    has_range=$(printf '%s' "$INPUT" | jq -r '(.tool_input.limit // .tool_input.offset // empty)' 2>/dev/null) || exit 0
    [ -n "$has_range" ] && exit 0
    case "$path" in
      *.png|*.jpg|*.jpeg|*.gif|*.webp|*.pdf|*.ipynb) exit 0 ;;
    esac
    [ -f "$path" ] || exit 0
    lines=$(wc -l < "$path" 2>/dev/null) || exit 0
    [ -n "$lines" ] && [ "$lines" -gt 500 ] 2>/dev/null && block \
      "lecture intégrale de $path ($lines lignes). Localiser d'abord (grep -n), puis relire avec offset/limit sur la plage utile. Passer outre : Read avec limit=$lines."
    ;;
  Bash)
    cmd=$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null) || exit 0
    [ -n "$cmd" ] || exit 0
    # contournement des hooks git
    printf '%s' "$cmd" | grep -Eq -- '--no-verify|core\.hooksPath=' \
      && block "contournement des hooks git (--no-verify / core.hooksPath interdit)."
    # attribution IA dans un commit ou une PR (règle absolue). "CLAUDE.md" et "Claude Code" restent permis.
    if printf '%s' "$cmd" | grep -Eq -- '(^|[;&|[:space:]])(git[[:space:]]+commit|gh[[:space:]]+pr[[:space:]]+(create|edit))'; then
      printf '%s' "$cmd" | grep -Eiq -- 'co-authored-by|generated with|noreply@anthropic|🤖|Claude (Fable|Opus|Sonnet|Haiku)' \
        && block "attribution IA dans un commit ou une PR (Co-Authored-By, « Generated with », nom de modèle). Retirer la ligne."
    fi
    # restauration git qui efface des modifications non commitées (checkout -- f, restore f, checkout .).
    # Une mutation de test ou un essai se restaure par copie du fichier, jamais par git.
    if printf '%s' "$cmd" | grep -Eq -- '(^|[;&|[:space:]])git[[:space:]]+(checkout|restore)([[:space:]]|$)' \
       && ! printf '%s' "$cmd" | grep -Eq -- 'ALLOW_DISCARD=1|--staged'; then
      cwd=$(printf '%s' "$INPUT" | jq -r '.cwd // empty' 2>/dev/null)
      [ -n "$cwd" ] && [ -d "$cwd" ] && git -C "$cwd" rev-parse --git-dir >/dev/null 2>&1 && {
        seg=$(printf '%s' "$cmd" | sed -E 's/.*git[[:space:]]+(checkout|restore)/\1/; s/[;&|].*//')
        for tok in $seg; do
          case "$tok" in checkout|restore|-*) continue ;; esac
          if [ "$tok" = "." ]; then
            git -C "$cwd" diff --quiet 2>/dev/null || block "git $seg effacerait des modifications non commitées du dépôt entier. Copier le fichier à part (cp), ou préfixer la commande par ALLOW_DISCARD=1 si c'est voulu."
          elif git -C "$cwd" ls-files --error-unmatch -- "$tok" >/dev/null 2>&1; then
            git -C "$cwd" diff --quiet -- "$tok" 2>/dev/null || block "git $seg effacerait les modifications non commitées de $tok. Restaurer par copie (cp), ou préfixer la commande par ALLOW_DISCARD=1 si c'est voulu."
          fi
        done
      }
    fi
    # lecture d'un .env via shell (hors *.example/.sample/...)
    if printf '%s' "$cmd" | grep -Eq -- '(^|[|&;[:space:]])(cat|less|more|head|tail|bat|xxd|od|strings|nl)[[:space:]]+[^|&;]*\.env([[:space:]]|$|\.)'; then
      printf '%s' "$cmd" | grep -Eq -- '\.env\.(example|sample|template|dist|local\.example)' || \
        block "lecture d'un .env via shell. Exception autorisée : *.example."
    fi
    ;;
esac
exit 0
