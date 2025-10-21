#!/usr/bin/env bash
set -euo pipefail

# Location of virtual environment
VENV_DIR="${VENV_DIR:-.venv-pdf}"
REQ_FILE="${REQ_FILE:-requirements.txt}"

# --- create or reuse venv ---
if [ ! -d "$VENV_DIR" ]; then
  echo "🛠  Creating virtual environment at $VENV_DIR"
  python3 -m venv "$VENV_DIR"
fi
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

# --- install all requirements ---
echo "📦 Installing dependencies from $REQ_FILE ..."
python -m pip install --upgrade pip >/dev/null
python -m pip install -r "$REQ_FILE"

# --- PlantUML environment ---
export PLANTUML_JAR="${PLANTUML_JAR:-tools/plantuml.jar}"
export PLANTUML_OUTPUT_FORMAT="${PLANTUML_OUTPUT_FORMAT:-svg}"

# --- WeasyPrint system deps (Ubuntu/WSL only, if not already installed) ---
# sudo apt-get update && sudo apt-get install -y \
#   libcairo2 libpango-1.0-0 libgdk-pixbuf2.0-0 libffi8 libxml2 libxslt1.1 fonts-dejavu-core


export ENABLE_PDF_EXPORT=1
echo "ENABLE_PDF_EXPORT=$ENABLE_PDF_EXPORT"
python scripts/mkdocs_pdf_build.py --outdir dist/pdf

echo "✅ PDF build complete. Files are in dist/pdf/"
