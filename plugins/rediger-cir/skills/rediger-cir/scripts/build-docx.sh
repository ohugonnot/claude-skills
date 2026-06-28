#!/usr/bin/env bash
# Convertit un dossier Markdown en .docx via pandoc (binaire autonome téléchargé si absent).
# Les figures référencées en chemin relatif (ex. figures/x.png) sont embarquées.
# Usage : build-docx.sh <fichier.md> [reference.docx]
#   reference.docx (optionnel) = gabarit de style Word (titres, polices…) pour le rendu final.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="${1:?usage: build-docx.sh <fichier.md> [reference.docx]}"
REF="${2:-}"
OUT="${SRC%.md}.docx"
SRCDIR="$(dirname "$SRC")"

# Gabarit de style par défaut (figures et légendes centrées, corps à gauche) si aucun n'est fourni
if [ -z "$REF" ] && [ -f "$SCRIPT_DIR/../assets/reference.docx" ]; then
  REF="$SCRIPT_DIR/../assets/reference.docx"
fi

PANDOC="$(command -v pandoc || true)"
if [ -z "$PANDOC" ]; then
  CACHE="${HOME}/.cache/cir-pandoc"
  PANDOC="$CACHE/pandoc"
  if [ ! -x "$PANDOC" ]; then
    echo "pandoc absent → téléchargement du binaire autonome (une seule fois)…"
    mkdir -p "$CACHE"
    ver="3.1.11"
    curl -sL "https://github.com/jgm/pandoc/releases/download/${ver}/pandoc-${ver}-linux-amd64.tar.gz" \
      | tar xz -C "$CACHE" --strip-components=2 "pandoc-${ver}/bin/pandoc"
  fi
fi

args=( "$SRC" --from=markdown-implicit_figures --resource-path="$SRCDIR" -o "$OUT" )
[ -n "$REF" ] && args+=( --reference-doc="$REF" )

# Citations normées + liens cliquables si un refs.bib est présent à côté du .md
if [ -f "$SRCDIR/refs.bib" ]; then
  args+=( --citeproc --bibliography="$SRCDIR/refs.bib" )
  CSL="$(ls "$SRCDIR"/*.csl 2>/dev/null | head -1 || true)"
  [ -n "$CSL" ] && args+=( --csl="$CSL" )
fi

"$PANDOC" "${args[@]}"
echo "✓ $OUT"
