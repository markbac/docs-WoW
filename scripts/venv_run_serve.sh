#!/usr/bin/env bash
#
# mkdocs.sh
#
# Idempotent MkDocs runner:
# - Creates a Python venv if required
# - Activates it if not already active
# - Installs required dependencies if missing
# - Runs MkDocs (default: serve)
#
# Usage:
#   ./mkdocs.sh            -> mkdocs serve
#   ./mkdocs.sh build      -> mkdocs build
#   ./mkdocs.sh gh-deploy  -> mkdocs gh-deploy
#

set -euo pipefail

VENV_DIR=".venv"
MKDOCS_CMD="${1:-serve}"

REQUIRED_PACKAGES=(
  mkdocs
  mkdocs-material
  mkdocs-macros-plugin
  mkdocs-git-revision-date-localized-plugin
  mkdocs-glightbox
  mkdocs-awesome-pages-plugin
  pymdown-extensions
)

echo "==> MkDocs command: mkdocs ${MKDOCS_CMD}"

# -------------------------------------------------
# Ensure Python is available
# -------------------------------------------------
if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 not found"
  exit 1
fi

# -------------------------------------------------
# Create venv if it does not exist
# -------------------------------------------------
if [[ ! -d "${VENV_DIR}" ]]; then
  echo "==> Creating virtual environment (${VENV_DIR})"
  python3 -m venv "${VENV_DIR}"
fi

# -------------------------------------------------
# Activate venv if not already active
# -------------------------------------------------
if [[ -z "${VIRTUAL_ENV:-}" ]]; then
  echo "==> Activating virtual environment"
  # shellcheck disable=SC1091
  source "${VENV_DIR}/bin/activate"
else
  echo "==> Virtual environment already active: ${VIRTUAL_ENV}"
fi

# -------------------------------------------------
# Upgrade packaging tools (safe + fast)
# -------------------------------------------------
pip install --upgrade pip setuptools wheel >/dev/null

# -------------------------------------------------
# Install required packages if missing
# -------------------------------------------------
echo "==> Ensuring required Python packages are installed"

for pkg in "${REQUIRED_PACKAGES[@]}"; do
  if ! pip show "${pkg}" >/dev/null 2>&1; then
    echo "    Installing ${pkg}"
    pip install "${pkg}"
  fi
done

# -------------------------------------------------
# Run MkDocs
# -------------------------------------------------
echo "==> Running: mkdocs ${MKDOCS_CMD}"
exec mkdocs "${MKDOCS_CMD}"
