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

# ------------------------------------------------------------
# Debug / logging controls
# ------------------------------------------------------------

DEBUG=0

for arg in "$@"; do
  case "$arg" in
    --debug)
      DEBUG=1
      shift
      ;;
  esac
done

timestamp() {
  date +"%Y-%m-%d %H:%M:%S"
}

log_info() {
  echo "[INFO ] $(timestamp) $*"
}

log_warn() {
  echo "[WARN ] $(timestamp) $*" >&2
}

log_error() {
  echo "[ERROR] $(timestamp) $*" >&2
}

log_debug() {
  if [[ "$DEBUG" -eq 1 ]]; then
    echo "[DEBUG] $(timestamp) $*"
  fi
}

die() {
  log_error "$*"
  exit 1
}

# ------------------------------------------------------------
# Error handling
# ------------------------------------------------------------

on_error() {
  local exit_code=$?
  local line_no=$1
  log_error "Script failed at line ${line_no} (exit code ${exit_code})"
  log_error "Last command: ${BASH_COMMAND}"
  exit "$exit_code"
}

trap 'on_error $LINENO' ERR

if [[ "$DEBUG" -eq 1 ]]; then
  set -x
fi

# ------------------------------------------------------------
# Banner
# ------------------------------------------------------------

log_info "== Cornerstone build started =="

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
PDF_OUT="Firmitas.pdf"
EPUB_OUT="Firmitas.epub"

log_debug "ROOT_DIR      = ${ROOT_DIR}"
log_debug "SCRIPTS_DIR   = ${SCRIPTS_DIR}"
log_debug "INPUT_MD      = ${INPUT_MD}"
log_debug "SPLIT_DIR     = ${SPLIT_DIR}"
log_debug "DIAG_DIR      = ${DIAG_DIR}"
log_debug "DIST_DIR      = ${DIST_DIR}"
log_debug "TEMPLATE_TEX  = ${TEMPLATE_TEX}"
log_debug "PDF_OUT       = ${PDF_OUT}"
log_debug "EPUB_OUT      = ${EPUB_OUT}"

# ------------------------------------------------------------
# Pre-flight checks
# ------------------------------------------------------------

log_info "Running pre-flight checks..."

command -v python >/dev/null 2>&1 || die "python not found on PATH"
command -v bash   >/dev/null 2>&1 || die "bash not found on PATH"

[[ -f "$INPUT_MD" ]]      || die "Input markdown not found: ${INPUT_MD}"
[[ -f "$TEMPLATE_TEX" ]]  || die "Pandoc template not found: ${TEMPLATE_TEX}"
[[ -x "${SCRIPTS_DIR}/build_book.sh" ]] || log_warn "build_book.sh is not executable (will invoke via bash)"

log_debug "Python version: $(python --version 2>&1)"
log_debug "Bash version:   ${BASH_VERSION}"

# ------------------------------------------------------------
# Clean previous outputs
# ------------------------------------------------------------

log_info "Cleaning previous build artefacts..."

# Uncomment when you want to fully regenerate split output
# if [[ -d "${SPLIT_DIR}" ]]; then
#   log_info "Removing split/"
#   rm -rf "${SPLIT_DIR}"
# fi

if [[ -d "${DIAG_DIR}" ]]; then
  log_info "Removing diag/"
  rm -rf "${DIAG_DIR}"
else
  log_debug "diag/ does not exist, skipping"
fi

if [[ -d "${DIST_DIR}" ]]; then
  log_info "Removing dist/"
  rm -rf "${DIST_DIR}"
else
  log_debug "dist/ does not exist, skipping"
fi

# ------------------------------------------------------------
# Step 1: Split book
# ------------------------------------------------------------

# log_info "Splitting book markdown..."
# log_debug "Invoking split_book.py"
# python \
#   "${SCRIPTS_DIR}/split_book.py" \
#   --verbose \
#   "${INPUT_MD}" \
#   --out "${SPLIT_DIR}"

# ------------------------------------------------------------
# Step 2: Render diagrams (Kroki)
# ------------------------------------------------------------

log_info "Rendering diagrams via Kroki..."
log_debug "Command: python ${SCRIPTS_DIR}/render_diagrams_kroki.py ${SPLIT_DIR} ${DIAG_DIR}"

python \
  "${SCRIPTS_DIR}/render_diagrams_kroki.py" \
  "${SPLIT_DIR}" \
  "${DIAG_DIR}"

log_debug "Diagram render completed"

# ------------------------------------------------------------
# Step 3: Build PDF + EPUB
# ------------------------------------------------------------

log_info "Building PDF and EPUB..."
log_debug "Invoking build_book.sh"

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

log_info "== Build complete =="

if [[ -f "${DIST_DIR}/${PDF_OUT}" ]]; then
  log_info "PDF  : ${DIST_DIR}/${PDF_OUT}"
else
  log_warn "PDF output not found"
fi

if [[ -f "${DIST_DIR}/${EPUB_OUT}" ]]; then
  log_info "EPUB : ${DIST_DIR}/${EPUB_OUT}"
else
  log_warn "EPUB output not found"
fi
