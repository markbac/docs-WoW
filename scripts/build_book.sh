#!/usr/bin/env bash
#
# buildbook.sh
#
# Shell equivalent of build_book.ps1
#
# Outputs:
# - PDF with covers
# - PDF without covers
# - EPUB
#

set -euo pipefail

# =================================================
# Argument parsing
# =================================================

ROOT=""
DIST=""
TEMPLATE=""
PDF=""
EPUB=""
DEBUG=false

while [ $# -gt 0 ]; do
  case "$1" in
    --root)     ROOT="$2"; shift 2 ;;
    --dist)     DIST="$2"; shift 2 ;;
    --template) TEMPLATE="$2"; shift 2 ;;
    --pdf)      PDF="$2"; shift 2 ;;
    --epub)     EPUB="$2"; shift 2 ;;
    --debug)    DEBUG=true; shift ;;
    *)
      echo "[ERR ] Unknown argument: $1"
      exit 1
      ;;
  esac
done

[ -z "$ROOT" ] && echo "[ERR ] --root is required" && exit 1
[ -z "$DIST" ] && echo "[ERR ] --dist is required" && exit 1
[ -z "$PDF"  ] && echo "[ERR ] --pdf is required"  && exit 1
[ -z "$EPUB" ] && echo "[ERR ] --epub is required" && exit 1

# =================================================
# Logging helpers
# =================================================

log()  { echo "[INFO]  $*"; }
ok()   { echo "[ OK ]  $*"; }
warn() { echo "[WARN]  $*"; }
dbg()  { $DEBUG && echo "[DBG ]  $*"; }

# =================================================
# Resolve paths
# =================================================

[ ! -d "$ROOT" ] && echo "[ERR ] Root directory not found: $ROOT" && exit 1
ROOT="$(cd "$ROOT" && pwd)"

mkdir -p "$DIST"
DIST="$(cd "$DIST" && pwd)"

if [ -n "$TEMPLATE" ]; then
  [ ! -f "$TEMPLATE" ] && echo "[ERR ] Template not found: $TEMPLATE" && exit 1
  TEMPLATE="$(cd "$(dirname "$TEMPLATE")" && pwd)/$(basename "$TEMPLATE")"
fi

# =================================================
# Toolchain checks
# =================================================

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "[ERROR] Required tool not found: $1" >&2
    exit 127
  }
}

log "Checking build toolchain..."

require_cmd pandoc
require_cmd xelatex

ok "Pandoc version: $(pandoc --version | head -n1)"
ok "LaTeX version : $(xelatex --version | head -n1)"

# =================================================
# Traceability
# =================================================

GIT_HASH="$(git rev-parse --short HEAD 2>/dev/null || true)"
[ -z "$GIT_HASH" ] && GIT_HASH="N/A"

DIRTY_COUNT="$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
[ "$DIRTY_COUNT" -gt 0 ] && GIT_DIRTY="Dirty" || GIT_DIRTY="Clean"

BUILD_DATE="$(date -u '+%Y-%m-%d %H:%M:%S UTC')"

log "Building Firmitas"
dbg "Git commit : $GIT_HASH ($GIT_DIRTY)"
dbg "Build date : $BUILD_DATE"
dbg "Root       : $ROOT"
dbg "Dist       : $DIST"

# =================================================
# Collect Markdown files
# =================================================

INPUT_FILES=()

FRONT_MATTER="$ROOT/_front_matter.md"
[ ! -f "$FRONT_MATTER" ] && echo "[ERR ] Missing _front_matter.md" && exit 1
INPUT_FILES+=("$FRONT_MATTER")

FRONT_CONTROL="$ROOT/_front_control.md"
[ -f "$FRONT_CONTROL" ] && INPUT_FILES+=("$FRONT_CONTROL")

for section in "$ROOT"/[0-9][0-9]_*; do
  [ ! -d "$section" ] && continue

  intro="$section/00_section.md"
  [ -f "$intro" ] && INPUT_FILES+=("$intro")

  chapters="$section/chapters"
  if [ -d "$chapters" ]; then
    while IFS= read -r -d '' file; do
      INPUT_FILES+=("$file")
    done < <(find "$chapters" -type f -name '*.md' -print0 | sort -z)
  fi
done

ok "Collected ${#INPUT_FILES[@]} Markdown files"

# =================================================
# Flatten media for Pandoc
# =================================================

FLATTENED_MEDIA="$DIST/_pandoc_media"
MEDIA_OUT="$FLATTENED_MEDIA/media"

log "Flattening media for Pandoc"

rm -rf "$FLATTENED_MEDIA"
mkdir -p "$MEDIA_OUT"

declare -A SEEN=()

while IFS= read -r -d '' media_dir; do
  while IFS= read -r -d '' file; do
    name="$(basename "$file")"
    if [[ -n "${SEEN[$name]:-}" ]]; then
      echo "[ERR ] Media filename collision detected: $name"
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

COVER_FRONT="$MEDIA_OUT/front.png"
COVER_BACK="$MEDIA_OUT/back.png"

[ -f "$ROOT/front.png" ] && cp -f "$ROOT/front.png" "$COVER_FRONT" || COVER_FRONT=""
[ -f "$ROOT/back.png"  ] && cp -f "$ROOT/back.png"  "$COVER_BACK"  || COVER_BACK=""

[ -n "$COVER_FRONT" ] && ok "Copied front cover" || warn "Front cover not found"
[ -n "$COVER_BACK"  ] && ok "Copied back cover"  || warn "Back cover not found"

# =================================================
# Pandoc argument arrays
# =================================================

PANDOC_COMMON=(
  --from markdown+yaml_metadata_block
  --lua-filter=scripts/chapter_mapping.lua
  --metadata fontsize=10.5pt
  --metadata linestretch=1.15
  --metadata "build_date=$BUILD_DATE"
  --metadata "git_commit=$GIT_HASH"
  --metadata "git_dirty=$GIT_DIRTY"
  --metadata "subtitle="
  --resource-path="$FLATTENED_MEDIA"
  --section-divs
  --standalone
)

PANDOC_PDF=(
  --top-level-division=chapter
  --pdf-engine=xelatex
)

TEMPLATE_ARG=()
[ -n "$TEMPLATE" ] && TEMPLATE_ARG+=(--template="$TEMPLATE")

COVER_META=(
  --metadata "cover_front=${COVER_FRONT}"
  --metadata "cover_back=${COVER_BACK}"
)

EPUB_ARGS=()
[ -n "$COVER_FRONT" ] && EPUB_ARGS+=(--epub-cover-image="$COVER_FRONT")

# =================================================
# PDF with covers
# =================================================

log "Generating PDF (with covers)"

pandoc \
  "${INPUT_FILES[@]}" \
  "${PANDOC_COMMON[@]}" \
  "${PANDOC_PDF[@]}" \
  "${COVER_META[@]}" \
  "${TEMPLATE_ARG[@]}" \
  -o "$DIST/$PDF"

ok "PDF with covers written"

# =================================================
# PDF without covers
# =================================================

PDF_NO_COVER="${PDF%.pdf}-nocover.pdf"

log "Generating PDF (no covers)"

pandoc \
  "${INPUT_FILES[@]}" \
  "${PANDOC_COMMON[@]}" \
  "${PANDOC_PDF[@]}" \
  "${TEMPLATE_ARG[@]}" \
  -o "$DIST/$PDF_NO_COVER"

ok "PDF without covers written"

# =================================================
# EPUB
# =================================================

log "Generating EPUB"

pandoc \
  "${INPUT_FILES[@]}" \
  "${PANDOC_COMMON[@]}" \
  --toc \
  --toc-depth=2 \
  "${EPUB_ARGS[@]}" \
  -o "$DIST/$EPUB"

ok "EPUB written"

log "Build complete"
