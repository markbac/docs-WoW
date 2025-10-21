param(
  [string]$VenvDir = ".venv-pdf",
  [string]$ReqFile = "requirements.txt",
  [string]$PlantUMLJarPath = "tools/plantuml.jar"
)

Write-Host "🚀 Setting up MkDocs development environment..."

# --- create or reuse venv ---
if (-not (Test-Path $VenvDir)) {
  Write-Host "🛠  Creating virtual environment at $VenvDir"
  python -m venv $VenvDir
}

# Activate
$activate = Join-Path $VenvDir "Scripts\Activate.ps1"
. $activate

# --- install requirements ---
Write-Host "📦 Ensuring dependencies from $ReqFile ..."
python -m pip install --upgrade pip | Out-Null
python -m pip install -r $ReqFile

# --- set PlantUML env vars ---
if (-not $env:PLANTUML_JAR)          { $env:PLANTUML_JAR = $PlantUMLJarPath }
if (-not $env:PLANTUML_OUTPUT_FORMAT){ $env:PLANTUML_OUTPUT_FORMAT = "svg" }

Write-Host "PLANTUML_JAR=$env:PLANTUML_JAR"
Write-Host "PLANTUML_OUTPUT_FORMAT=$env:PLANTUML_OUTPUT_FORMAT"

# --- warn if PlantUML jar is missing ---
if (-not (Test-Path $env:PLANTUML_JAR)) {
  Write-Host "⚠️  PlantUML jar not found at $env:PLANTUML_JAR"
  Write-Host "   Run: bash scripts/get_plantuml.sh or place plantuml.jar manually."
}

# --- run the dev server ---
Write-Host "🌐 Launching MkDocs development server..."
mkdocs serve
