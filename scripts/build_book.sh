#!/usr/bin/env bash
#
# build_book.sh
#
# Bash equivalent of the PowerShell Pandoc build script
#

set -euo pipefail

# =================================================
# Argument parsing
# =================================================
usage() {
  echo "Usage:"
  echo "  $0 --root <dir> --dist <dir> --pdf <file> --epub <file> [--template <file>] [--debug]"
  exit 1
}

ROOT=""
DIST=""
TEMPLATE=""
PDF=""
EPUB=""
DEBUG=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root)     ROOT="$2"; shift 2 ;;
    --dist)     DIST="$2"; shift 2 ;;
    --template) TEMPLATE="$2"; shift 2 ;;
    --pdf)      PDF="$2"; shift 2 ;;
    --epub)     EPUB="$2"; shift 2 ;;
    --debug)    DEBUG=1; shift ;;
    *) usage ;;
  esac
done

[[ -z "$ROOT" || -z "$DIST" || -z "$PDF" || -z "$EPUB" ]] && usage

# =================================================
# Logging helpers (ASCII-safe)
# =================================================
log()  { echo -e "\033[36m[INFO]\033[0m  $*"; }
ok()   { echo -e "\033[32m[ OK ]\033[0m  $*"; }
warn() { echo -e "\033[33m[WARN]\033[0m  $*"; }
dbg()  { [[ "$DEBUG" -eq 1 ]] && echo -e "\033[90m[DBG ]\033[0m  $*"; }

# =================================================
# Resolve and validate paths
# =================================================
[[ ! -d "$ROOT" ]] && { echo "Root directory not found: $ROOT"; exit 1; }
ROOT="$(cd "$ROOT" && pwd)"

mkdir -p "$DIST"
DIST="$(cd "$DIST" && pwd)"

if [[ -n "$TEMPLATE" ]]; then
  [[ ! -f "$TEMPLATE" ]] && { echo "Template not found: $TEMPLATE"; exit 1; }
  TEMPLATE="$(cd "$(dirname "$TEMPLATE")" && pwd)/$(basename "$TEMPLATE")"
fi

# =================================================
# Traceability
# =================================================
GIT_HASH="$(git rev-parse --short HEAD 2>/dev/null || echo "N/A")"
DIRTY_COUNT="$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
GIT_DIRTY="Clean"
[[ "$DIRTY_COUNT" -gt 0 ]] && GIT_DIRTY="Dirty"

BUILD_DATE="$(date -u '+%Y-%m-%d %H:%M:%S UTC')"

log "Building Cornerstone"
dbg "Git commit : $GIT_HASH ($GIT_DIRTY)"
dbg "Build date : $BUILD_DATE"
dbg "Root       : $ROOT"
dbg "Dist       : $DIST"

# =================================================
# Collect Markdown files
# =================================================
INPUT_FILES=()

FRONT_MATTER="$ROOT/_front_matter.md"
[[ ! -f "$FRONT_MATTER" ]] && { echo "Missing _front_matter.md in $ROOT"; exit 1; }
INPUT_FILES+=("$FRONT_MATTER")

FRONT_CONTROL="$ROOT/_front_control.md"
[[ -f "$FRONT_CONTROL" ]] && INPUT_FILES+=("$FRONT_CONTROL")

while IFS= read -r -d '' dir; do
  intro="$dir/00_section.md"
  [[ -f "$intro" ]] && INPUT_FILES+=("$intro")

  while IFS= read -r -d '' md; do
    [[ "$(basename "$md")" != "00_section.md" ]] && INPUT_FILES+=("$md")
  done < <(find "$dir" -maxdepth 1 -name "*.md" -type f -print0 | sort -z)

done < <(find "$ROOT" -maxdepth 1 -type d -name '[0-9][0-9]_*' -print0 | sort -z)

ok "Collected ${#INPUT_FILES[@]} Markdown files"

# =================================================
# Flatten Pandoc media
# =================================================
FLATTENED_MEDIA="$DIST/_pandoc_media"
MEDIA_OUT="$FLATTENED_MEDIA/media"

log "Flattening media for Pandoc"
rm -rf "$FLATTENED_MEDIA"
mkdir -p "$MEDIA_OUT"

declare -A SEEN

while IFS= read -r -d '' media_dir; do
  while IFS= read -r -d '' file; do
    name="$(basename "$file")"
    if [[ -n "${SEEN[$name]:-}" ]]; then
      cat <<EOF
Media filename collision detected:

  $name
  - ${SEEN[$name]}
  - $file
EOF
      exit 1
    fi
    SEEN["$name"]="$file"
    cp -f "$file" "$MEDIA_OUT/$name"
    dbg "  + $name"
  done < <(find "$media_dir" -type f -print0)
done < <(find "$ROOT" -type d -name media -print0)

ok "Flattened ${#SEEN[@]} media files"

# =================================================
# Copy cover images
# =================================================
FRONT_COVER_SRC="$(cd "$ROOT/.." && pwd)/front.png"
BACK_COVER_SRC="$(cd "$ROOT/.." && pwd)/back.png"

if [[ -f "$FRONT_COVER_SRC" ]]; then
  cp -f "$FRONT_COVER_SRC" "$MEDIA_OUT/front.png"
  ok "Copied front cover to media/front.png"
else
  warn "Front cover not found: $FRONT_COVER_SRC"
fi

if [[ -f "$BACK_COVER_SRC" ]]; then
  cp -f "$BACK_COVER_SRC" "$MEDIA_OUT/back.png"
  ok "Copied back cover to media/back.png"
else
  warn "Back cover not found: $BACK_COVER_SRC"
fi

# =================================================
# Common Pandoc arguments
# =================================================
PANDOC_COMMON=(
  --from markdown+yaml_metadata_block
  --top-level-division=chapter
  --lua-filter=../../scripts/chapter_mapping.lua
  --metadata "build_date=$BUILD_DATE"
  --metadata "git_commit=$GIT_HASH"
  --metadata "git_dirty=$GIT_DIRTY"
  --metadata "subtitle="
  --resource-path "$FLATTENED_MEDIA:$MEDIA_OUT"
)

# =================================================
# PDF
# =================================================
log "Generating PDF"

PDF_ARGS=(
  "${INPUT_FILES[@]}"
  "${PANDOC_COMMON[@]}"
  --metadata cover_front=front.png
  --metadata cover_back=back.png
  --pdf-engine=xelatex
  -o "$DIST/$PDF"
)

[[ -n "$TEMPLATE" ]] && PDF_ARGS+=(--template="$TEMPLATE")

pandoc "${PDF_ARGS[@]}"
ok "PDF written to $DIST/$PDF"

# =================================================
# EPUB
# =================================================
log "Generating EPUB"

EPUB_COVER="$FRONT_COVER_SRC"

pandoc \
  "${INPUT_FILES[@]}" \
  "${PANDOC_COMMON[@]}" \
  --epub-cover-image="$EPUB_COVER" \
  -o "$DIST/$EPUB"

ok "EPUB written to $DIST/$EPUB"

log "Build complete"
