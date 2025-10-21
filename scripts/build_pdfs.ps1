param(
  [switch]$Combined = $true,
  [string]$OutDir = "dist/pdf",
  [string]$VenvDir = ".venv-pdf",
  [string]$ReqFile = "requirements.txt"
)

# --- create or reuse venv ---
if (-not (Test-Path $VenvDir)) {
  Write-Host "🛠  Creating virtual environment at $VenvDir"
  python -m venv $VenvDir
}

# Activate the venv
$activate = Join-Path $VenvDir "Scripts\Activate.ps1"
. $activate

# --- install all requirements ---
Write-Host "📦 Installing dependencies from $ReqFile ..."
python -m pip install --upgrade pip | Out-Null
python -m pip install -r $ReqFile

# --- PlantUML environment ---
if (-not $env:PLANTUML_JAR)          { $env:PLANTUML_JAR = "tools/plantuml.jar" }
if (-not $env:PLANTUML_OUTPUT_FORMAT){ $env:PLANTUML_OUTPUT_FORMAT = "svg" }

# --- run PDF build ---
$flag = $Combined.IsPresent ? "--combined" : ""
$env:ENABLE_PDF_EXPORT = "1"
Write-Host "ENABLE_PDF_EXPORT=$($env:ENABLE_PDF_EXPORT)"
python scripts/mkdocs_pdf_build.py --outdir dist/pdf


Write-Host "✅ PDF build complete. Files are in $OutDir"
