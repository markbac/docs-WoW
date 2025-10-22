#!/usr/bin/env bash
#
# build_pdfs.sh
#
# Builds the documentation PDFs using mkdocs-to-pdf via a custom Python script
# (scripts/mkdocs_pdf_build.py). This script manages the Python virtual
# environment and sets up necessary environment variables (like PlantUML).
#
# Usage: bash scripts/build_pdfs.sh

# Exit immediately if a command exits with a non-zero status.
# Treat unset variables as an error.
set -euo pipefail

# --- Configuration Variables ---
# Define the directory for the Python virtual environment. Default is .venv-pdf.
VENV_DIR="${VENV_DIR:-.venv-pdf}"
# Define the path to the Python dependency file. Default is requirements.txt.
REQ_FILE="${REQ_FILE:-requirements.txt}"


# --- 1. Create or Reuse Python Virtual Environment ---
if [ ! -d "$VENV_DIR" ]; then
  echo "🛠  Creating virtual environment at $VENV_DIR"
  # Use python3 to ensure the correct executable is used
  python3 -m venv "$VENV_DIR"
fi

# Activate the virtual environment to ensure subsequent python/pip calls use it.
# shellcheck source=/dev/null (Suppress shell check warning for 'source')
source "$VENV_DIR/bin/activate"


# --- 2. Install Dependencies ---
echo "📦 Installing dependencies from $REQ_FILE ..."
# Upgrade pip first for best compatibility
python -m pip install --upgrade pip >/dev/null
# Install all project dependencies (including mkdocs, mkdocs-to-pdf, etc.)
python -m pip install -r "$REQ_FILE"


# --- 3. PlantUML Environment Setup ---
# Set environment variables for the PlantUML Markdown extension.
# Defaults are used if the variables are not already set (e.g., by the CI/CD job).
export PLANTUML_JAR="${PLANTUML_JAR:-tools/plantuml.jar}"
export PLANTUML_OUTPUT_FORMAT="${PLANTUML_OUTPUT_FORMAT:-svg}"

# --- 4. Run PDF Build Script ---
# Set environment flag to enable the 'to-pdf' plugin within the Python script.
export ENABLE_PDF_EXPORT=1
echo "ENABLE_PDF_EXPORT=$ENABLE_PDF_EXPORT"

# Execute the custom Python build script.
# --outdir dist/pdf: Specifies where to copy the final PDF file(s).
# --keep-site: CRITICAL FIX: Prevents the Python script from deleting the 'site/'
#              directory after the PDF build. The 'site/' directory is required
#              for the GitHub Pages artifact upload step in build.yml.
python scripts/mkdocs_pdf_build.py --outdir dist/pdf --keep-site

echo "✅ PDF build complete. Files are in dist/pdf/"