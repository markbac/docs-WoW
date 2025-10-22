<#
.SYNOPSIS
  Builds the documentation PDFs using mkdocs-to-pdf via a custom Python script.
  Manages the Python virtual environment and sets up necessary environment variables.

.PARAMETER Combined
  A switch parameter to control a combined PDF build (future expansion).

.PARAMETER OutDir
  The destination directory for the final PDF file(s). Default is "dist/pdf".

.PARAMETER VenvDir
  The location of the Python virtual environment directory. Default is ".venv-pdf".

.PARAMETER ReqFile
  The path to the Python dependency file. Default is "requirements.txt".

.NOTES
  Requires Python 3 and the Python dependencies listed in requirements.txt.
#>
param(
  [switch]$Combined = $true,
  [string]$OutDir = "dist/pdf",
  [string]$VenvDir = ".venv-pdf",
  [string]$ReqFile = "requirements.txt"
)


# --- 1. Create or Reuse Python Virtual Environment ---
if (-not (Test-Path $VenvDir)) {
  Write-Host "🛠  Creating virtual environment at $VenvDir"
  # Create the virtual environment using the system python
  python -m venv $VenvDir
}

# Activate the venv
$activate = Join-Path $VenvDir "Scripts\Activate.ps1"
. $activate # Dot-source the activation script to modify the current shell's environment

# --- 2. Install Dependencies ---
Write-Host "📦 Installing dependencies from $ReqFile ..."
# Upgrade pip first, suppressing normal output to keep logs clean
python -m pip install --upgrade pip | Out-Null
# Install all project dependencies
python -m pip install -r $ReqFile


# --- 3. PlantUML Environment Setup ---
# Set default environment variables for the PlantUML Markdown extension.
# Only set the variable if it doesn't already exist.
if (-not $env:PLANTUML_JAR)          { $env:PLANTUML_JAR = "tools/plantuml.jar" }
if (-not $env:PLANTUML_OUTPUT_FORMAT){ $env:PLANTUML_OUTPUT_FORMAT = "svg" }


# --- 4. Run PDF Build Script ---
# Define flags based on input parameters (currently $flag is unused, but available)
$flag = $Combined.IsPresent ? "--combined" : ""

# Set environment flag to enable PDF export in the Python script.
$env:ENABLE_PDF_EXPORT = "1"
Write-Host "ENABLE_PDF_EXPORT=$($env:ENABLE_PDF_EXPORT)"

# Execute the custom Python build script.
# --outdir $OutDir: Uses the parameter for output directory.
# --keep-site: CRITICAL FIX: Prevents mkdocs_pdf_build.py from deleting the 'site/'
#              folder, ensuring the HTML site is available for artifact upload.
python scripts/mkdocs_pdf_build.py --outdir $OutDir --keep-site


Write-Host "✅ PDF build complete. Files are in $OutDir"