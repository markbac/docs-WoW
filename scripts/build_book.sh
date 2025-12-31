#!/usr/bin/env bash
set -euo pipefail

# --------------------------------------
# Colours
# --------------------------------------
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
DIM="\033[2m"
RESET="\033[0m"

log()  { echo -e "${BLUE}ℹ${RESET}  $*"; }
ok()   { echo -e "${GREEN}✔${RESET}  $*"; }
warn() { echo -e "${YELLOW}⚠${RESET}  $*"; }
dbg()  { [ "$VERBOSE" = "1" ] && echo -e "${DIM}… $*${RESET}"; }

# --------------------------------------
# Defaults
# --------------------------------------
ROOT_DIR=""
DIST_DIR=""
TEMPLATE=""
PDF_OUT=""
EPUB_OUT=""
VERBOSE=0

# --------------------------------------
# Argument parsing
# --------------------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --root)     ROOT_DIR="$2"; shift 2 ;;
    --dist)     DIST_DIR="$2"; shift 2 ;;
    --template) TEMPLATE="$2"; shift 2 ;;
    --pdf)      PDF_OUT="$2"; shift 2 ;;
    --epub)     EPUB_OUT="$2"; shift 2 ;;
    --verbose)  VERBOSE=1; shift ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# --------------------------------------
# Validation
# --------------------------------------
[ -z "$ROOT_DIR" ]   && { echo "Missing --root"; exit 1; }
[ -z "$DIST_DIR" ]   && { echo "Missing --dist"; exit 1; }
[ -z "$PDF_OUT" ]    && { echo "Missing --pdf"; exit 1; }
[ -z "$EPUB_OUT" ]   && { echo "Missing --epub"; exit 1; }

mkdir -p "$DIST_DIR"

# --------------------------------------
# Traceability
# --------------------------------------
GIT_HASH="$(git rev-parse --short HEAD 2>/dev/null || echo N/A)"
DIRTY_COUNT="$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
BUILD_DATE="$(date -u '+%Y-%m-%d %H:%M:%S UTC')"
GIT_DIRTY="Clean"

[ "$DIRTY_COUNT" != "0" ] && GIT_DIRTY="Dirty"

log "Building book"
dbg "Commit: $GIT_HASH ($GIT_DIRTY)"
dbg "Build date: $BUILD_DATE"

# --------------------------------------
# Assemble ordered input list
# --------------------------------------
INPUT_FILES=()

FRONT="$ROOT_DIR/_front_matter.md"
[ ! -f "$FRONT" ] && { echo "Missing _front_matter.md"; exit 1; }

INPUT_FILES+=("$FRONT")
dbg "Front matter: $FRONT"

for SECTION in "$ROOT_DIR"/[0-9][0-9]_section_* "$ROOT_DIR"/[0-9][0-9]_appendix; do
  [ -d "$SECTION" ] || continue
  dbg "Section: $(basename "$SECTION")"

  if [ -f "$SECTION/00_section.md" ]; then
    INPUT_FILES+=("$SECTION/00_section.md")
    dbg "  + 00_section.md"
  fi

  for CHAPTER in "$SECTION"/[0-9][0-9]_*.md; do
    [ "$(basename "$CHAPTER")" = "00_section.md" ] && continue
    INPUT_FILES+=("$CHAPTER")
    dbg "  + $(basename "$CHAPTER")"
  done
done

ok "Collected ${#INPUT_FILES[@]} Markdown files"

# --------------------------------------
# Common Pandoc flags
# --------------------------------------
COMMON_FLAGS=(
  --from markdown+yaml_metadata_block
  --number-sections
  --top-level-division=part
  --part-title
  --metadata build_date="$BUILD_DATE"
  --metadata git_commit="$GIT_HASH"
  --metadata git_dirty="$GIT_DIRTY"
  --lua-filter=..\..\scripts\chapter_mapping.lua
)

# --------------------------------------
# PDF build
# --------------------------------------
log "Generating PDF"

pandoc \
  "${INPUT_FILES[@]}" \
  "${COMMON_FLAGS[@]}" \
  --template="$TEMPLATE" \
  --pdf-engine=xelatex \
  -o "$DIST_DIR/$PDF_OUT"

ok "PDF written to $DIST_DIR/$PDF_OUT"

# --------------------------------------
# EPUB build
# --------------------------------------
log "Generating EPUB"

pandoc \
  "${INPUT_FILES[@]}" \
  "${COMMON_FLAGS[@]}" \
  --to epub \
  -o "$DIST_DIR/$EPUB_OUT"

ok "EPUB written to $DIST_DIR/$EPUB_OUT"
