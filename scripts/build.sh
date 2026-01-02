#!/usr/bin/env bash
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

echo "== Cornerstone build started =="

# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------

ROOT_DIR="$(pwd)"
SCRIPTS_DIR="$(cd ../../scripts && pwd)"
INPUT_MD="${ROOT_DIR}/Firmitas_Framework.md"

SPLIT_DIR="${ROOT_DIR}/split"
DIAG_DIR="${ROOT_DIR}/diag"
DIST_DIR="${ROOT_DIR}/dist"

TEMPLATE_TEX="${SCRIPTS_DIR}/templates/book.tex"
PDF_OUT="cornerstone.pdf"
EPUB_OUT="cornerstone.epub"

# ------------------------------------------------------------
# Clean previous outputs
# ------------------------------------------------------------

echo "Cleaning previous build artefacts..."

# Uncomment when you want to fully regenerate split output
# if [[ -d "${SPLIT_DIR}" ]]; then
#   echo "  Removing split/"
#   rm -rf "${SPLIT_DIR}"
# fi

if [[ -d "${DIAG_DIR}" ]]; then
  echo "  Removing diag/"
  rm -rf "${DIAG_DIR}"
fi

if [[ -d "${DIST_DIR}" ]]; then
  echo "  Removing dist/"
  rm -rf "${DIST_DIR}"
fi

# ------------------------------------------------------------
# Step 1: Split book
# ------------------------------------------------------------

# echo "Splitting book markdown..."
# python \
#   "${SCRIPTS_DIR}/split_book.py" \
#   --verbose \
#   "${INPUT_MD}" \
#   --out "${SPLIT_DIR}"

# ------------------------------------------------------------
# Step 2: Render diagrams (Kroki)
# ------------------------------------------------------------

echo "Rendering diagrams via Kroki..."

python \
  "${SCRIPTS_DIR}/render_diagrams_kroki.py" \
  "${SPLIT_DIR}" \
  "${DIAG_DIR}"

# ------------------------------------------------------------
# Step 3: Build PDF + EPUB
# ------------------------------------------------------------

echo "Building PDF and EPUB..."

bash \
  "${SCRIPTS_DIR}/build_book.sh" \
  --root "${DIAG_DIR}" \
  --dist "${DIST_DIR}" \
  --template "${TEMPLATE_TEX}" \
  --pdf "${PDF_OUT}" \
  --epub "${EPUB_OUT}" \
  --debug

# ------------------------------------------------------------
# Done
# ------------------------------------------------------------

echo "== Build complete =="
echo "Outputs:"
echo "  PDF : ${DIST_DIR}/${PDF_OUT}"
echo "  EPUB: ${DIST_DIR}/${EPUB_OUT}"
