<#
.SYNOPSIS
Idempotent MkDocs runner for Ways of Working documentation.

.DESCRIPTION
- Creates a Python virtual environment if required
- Activates it if not already active
- Installs required Python packages if missing
- Runs MkDocs (default: serve)

.USAGE
.\mkdocs.ps1
.\mkdocs.ps1 build
.\mkdocs.ps1 gh-deploy
#>

param (
    [string]$MkdocsCommand = "serve"
)

$ErrorActionPreference = "Stop"

$VenvDir = ".venv"
$VenvActivate = Join-Path $VenvDir "Scripts\Activate.ps1"

$RequiredPackages = @(
    "mkdocs",
    "mkdocs-material",
    "mkdocs-macros-plugin",
    "mkdocs-git-revision-date-localized-plugin",
    "mkdocs-glightbox",
    "mkdocs-awesome-pages-plugin",
    "pymdown-extensions",
    "beautifulsoup4",
    "lxml"
)

Write-Host "==> MkDocs command: mkdocs $MkdocsCommand"

# -------------------------------------------------
# Ensure Python is available
# -------------------------------------------------
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "python not found in PATH"
}

# -------------------------------------------------
# Create venv if it does not exist
# -------------------------------------------------
if (-not (Test-Path $VenvDir)) {
    Write-Host "==> Creating virtual environment ($VenvDir)"
    python -m venv $VenvDir
}

# -------------------------------------------------
# Activate venv if not already active
# -------------------------------------------------
if (-not $env:VIRTUAL_ENV) {
    Write-Host "==> Activating virtual environment"
    if (-not (Test-Path $VenvActivate)) {
        Write-Error "Virtual environment activation script not found: $VenvActivate"
    }
    . $VenvActivate
}
else {
    Write-Host "==> Virtual environment already active: $env:VIRTUAL_ENV"
}

# -------------------------------------------------
# Upgrade packaging tools (safe to re-run)
# -------------------------------------------------
python -m pip install --upgrade pip setuptools wheel | Out-Null

# -------------------------------------------------
# Install required packages if missing
# -------------------------------------------------
# -------------------------------------------------
# Install required packages if missing
# -------------------------------------------------
Write-Host "==> Ensuring required Python packages are installed"

foreach ($pkg in $RequiredPackages) {

    $oldPreference = $ErrorActionPreference
    $ErrorActionPreference = 'SilentlyContinue'

    python -m pip show $pkg *> $null
    $exitCode = $LASTEXITCODE

    $ErrorActionPreference = $oldPreference

    if ($exitCode -ne 0) {
        Write-Host "    Installing $pkg"
        python -m pip install $pkg
    }
}

# -------------------------------------------------
# Run MkDocs
# -------------------------------------------------
Write-Host "==> Running: mkdocs $MkdocsCommand"
mkdocs $MkdocsCommand
