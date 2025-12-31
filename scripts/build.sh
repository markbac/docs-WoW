#!/usr/bin/env bash
#
# build.sh
#
# Build script for Cornerstone book
#
# Steps:
# 1. Remove existing split/ and diag/ directories
# 2. Split monolithic markdown into structured book layout
# 3. Render diagrams via Kroki
# 4. Build PDF + EPUB via Pandoc / LaTeX
#
# Assumptions:
# - Running from book root
# - Python is on PATH
# - Scripts live in ../../scripts/
#

set -euo pipefail

# ------------------------------------------------------------
# Logging helpers
# ------------------------------------------------------------
info()  { echo -e "\033[36m[INFO]\033[0m  $*"; }
warn()  { echo -e "\033[33m[WARN]\033[0m  $*"; }
ok()    { echo -e "\033[32m[ OK ]\033[0m  $*"; }
dbg()   { echo -e "\033[90m[DBG ]\033[0m  $*"; }

info "== Cornerstone build started =="

# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------
ROOT_DIR="$(pwd)"
SCRIPTS_DIR="$(cd ../../scripts && pwd)"

INPUT_MD="$ROOT_DIR/cornerstone_framework_v2.md"

SPLIT_DIR="$ROOT_DIR/split"
DIAG_DIR="$ROOT_DIR/diag"
DIST_DIR="$ROOT_DIR/dist"

TEMPLATE_TEX="$SCRIPTS_DIR/templates/book.tex"
PDF_OUT="cornerstone.pdf"
EPUB_OUT="cornerstone.epub"

# ------------------------------------------------------------
# Clean previous outputs
# ------------------------------------------------------------
warn "Cleaning previous build artefacts..."

if [[ -d "$SPLIT_DIR" ]]; then
  dbg "Removing split/"
  rm -rf "$SPLIT_DIR"
fi

if [[ -d "$DIAG_DIR" ]]; then
  dbg "Removing diag/"
  rm -rf "$DIAG_DIR"
fi

if [[ -d "$DIST_DIR" ]]; then
  dbg "Removing dist/"
  rm -rf "$DIST_DIR"
fi

# ------------------------------------------------------------
# Step 1: Split book
# ------------------------------------------------------------
info "Splitting book markdown..."

python "$SCRIPTS_DIR/split_book.py" \
  --verbose \
  "$INPUT_MD" \
  --out "$SPLIT_DIR"

# ------------------------------------------------------------
# Step 2: Render diagrams (Kroki)
# ------------------------------------------------------------
info "Rendering diagrams via Kroki..."

python "$SCRIPTS_DIR/render_diagrams_kroki.py" \
  "$SPLIT_DIR" \
  "$DIAG_DIR"

# ------------------------------------------------------------
# Step 3: Build PDF + EPUB
# ------------------------------------------------------------
info "Building PDF and EPUB..."

bash "$SCRIPTS_DIR/build_book.sh" \
  --root "$DIAG_DIR" \
  --dist "$DIST_DIR" \
  --template "$TEMPLATE_TEX" \
  --pdf "$PDF_OUT" \
  --epub "$EPUB_OUT" \
  --debug

# ------------------------------------------------------------
# Done
# ------------------------------------------------------------
ok "== Build complete =="
ok "Outputs:"
echo "  PDF : $DIST_DIR/$PDF_OUT"
echo "  EPUB: $DIST_DIR/$EPUB_OUT"
