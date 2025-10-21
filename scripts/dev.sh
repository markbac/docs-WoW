#!/usr/bin/env bash
# Ensures a clean local MkDocs dev environment with local PlantUML rendering.
# - Creates or reuses a venv
# - Installs requirements.txt
# - Sets PlantUML env vars
# - Runs mkdocs serve with the correct interpreter

set -euo pipefail

VENV_DIR="${VENV_DIR:-.venv-pdf}"
REQ_FILE="${REQ_FILE:-requirements.txt}"
PLANTUML_JAR_PATH="tools/plantuml.jar"

echo "🚀 Setting up MkDocs development environment..."

# --- create or reuse virtual environment ---
if [ ! -d "$VENV_DIR" ]; then
  echo "🛠  Creating virtual environment at $VENV_DIR"
  python3 -m venv "$VENV_DIR"
fi

# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

# --- install requirements ---
echo "📦 Ensuring dependencies from $REQ_FILE ..."
python -m pip install --upgrade pip >/dev/null
python -m pip install -r "$REQ_FILE"

# --- set PlantUML env vars ---
export PLANTUML_JAR="${PLANTUML_JAR:-$PLANTUML_JAR_PATH}"
export PLANTUML_OUTPUT_FORMAT="${PLANTUML_OUTPUT_FORMAT:-svg}"

echo "PLANTUML_JAR=$PLANTUML_JAR"
echo "PLANTUML_OUTPUT_FORMAT=$PLANTUML_OUTPUT_FORMAT"

# --- warn if PlantUML jar is missing ---
if [ ! -f "$PLANTUML_JAR" ]; then
  echo "⚠️  PlantUML jar not found at $PLANTUML_JAR"
  echo "   Run: bash scripts/get_plantuml.sh  or place plantuml.jar manually."
fi

# --- run the dev server ---
echo "🌐 Launching MkDocs development server..."
exec mkdocs serve
