#!/usr/bin/env bash
#
# buildbook.sh
#
# Build Firmitas:
# - PDF with ToC (content-driven via 03_toc/00_section.md)
# - PDF without ToC
# - EPUB (Pandoc-generated ToC)
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

log()  { echo "[INFO]  $*" >&2; }
ok()   { echo "[ OK ]  $*" >&2; }
warn() { echo "[WARN]  $*" >&2; }
dbg()  { $DEBUG && echo "[DBG ]  $*" >&2; }


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
require_cmd pdflatex

ok "Pandoc version: $(pandoc --version | head -n1)"
ok "LaTeX version : $(pdflatex --version | head -n1)"

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

# =================================================
# Collect Markdown files
# =================================================

collect_markdown() {
  local include_toc="$1"
  local files=()

  local FRONT_MATTER="$ROOT/_front_matter.md"
  [ ! -f "$FRONT_MATTER" ] && {
    echo "[ERR ] Missing _front_matter.md in $ROOT"
    exit 1
  }
  files+=("$FRONT_MATTER")

  local FRONT_CONTROL="$ROOT/_front_control.md"
  [ -f "$FRONT_CONTROL" ] && files+=("$FRONT_CONTROL")

  for section in "$ROOT"/[0-9][0-9]_*; do
    [ ! -d "$section" ] && continue

    local name
    name="$(basename "$section")"
    local intro="$section/00_section.md"

    if [[ "$name" == 03_toc* ]]; then
      if $include_toc; then
        [ -f "$intro" ] && files+=("$intro")
        dbg "Including ToC section"
      else
        dbg "Skipping ToC section"
      fi
    else
      [ -f "$intro" ] && files+=("$intro")
    fi

    local chapters="$section/chapters"
    if [ -d "$chapters" ]; then
      while IFS= read -r -d '' file; do
        files+=("$file")
      done < <(find "$chapters" -type f -name '*.md' -print0 | sort -z)
    fi
  done

  printf '%s\n' "${files[@]}"
}

mapfile -t INPUT_WITH_TOC    < <(collect_markdown true)
mapfile -t INPUT_WITHOUT_TOC < <(collect_markdown false)

ok "Collected markdown (with ToC)   : ${#INPUT_WITH_TOC[@]}"
ok "Collected markdown (without ToC): ${#INPUT_WITHOUT_TOC[@]}"

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

COVER_FRONT=""
COVER_BACK=""

[ -f "$ROOT/front.png" ] && {
  cp -f "$ROOT/front.png" "$MEDIA_OUT/front.png"
  COVER_FRONT="$MEDIA_OUT/front.png"
  ok "Copied front cover"
} || warn "Front cover not found"

[ -f "$ROOT/back.png" ] && {
  cp -f "$ROOT/back.png" "$MEDIA_OUT/back.png"
  COVER_BACK="$MEDIA_OUT/back.png"
  ok "Copied back cover"
} || warn "Back cover not found"

# =================================================
# Pandoc arguments
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

PANDOC_PDF_ONLY=(
  --top-level-division=chapter
  --pdf-engine=xelatex
)

COVER_META=()
[ -n "$COVER_FRONT" ] && COVER_META+=(--metadata "cover_front=${COVER_FRONT//\\//}")
[ -n "$COVER_BACK"  ] && COVER_META+=(--metadata "cover_back=${COVER_BACK//\\//}")

# =================================================
# PDF with ToC
# =================================================

log "Generating PDF (with ToC)"

pandoc \
  "${INPUT_WITH_TOC[@]}" \
  "${PANDOC_COMMON[@]}" \
  "${PANDOC_PDF_ONLY[@]}" \
  "${COVER_META[@]}" \
  ${TEMPLATE:+--template="$TEMPLATE"} \
  -o "$DIST/$PDF"

ok "PDF with ToC written to $DIST/$PDF"

# =================================================
# PDF without ToC
# =================================================

PDF_NO_TOC="${PDF%.pdf}-notoc.pdf"

log "Generating PDF (without ToC)"

pandoc \
  "${INPUT_WITHOUT_TOC[@]}" \
  "${PANDOC_COMMON[@]}" \
  "${PANDOC_PDF_ONLY[@]}" \
  "${COVER_META[@]}" \
  ${TEMPLATE:+--template="$TEMPLATE"} \
  -o "$DIST/$PDF_NO_TOC"

ok "PDF without ToC written to $DIST/$PDF_NO_TOC"

# =================================================
# EPUB
# =================================================

log "Generating EPUB"

EPUB_ARGS=()
[ -n "$COVER_FRONT" ] && EPUB_ARGS+=(--epub-cover-image="$COVER_FRONT")

pandoc \
  "${INPUT_WITH_TOC[@]}" \
  "${PANDOC_COMMON[@]}" \
  --toc \
  --toc-depth=2 \
  "${EPUB_ARGS[@]}" \
  -o "$DIST/$EPUB"

ok "EPUB written to $DIST/$EPUB"

log "Build complete"
