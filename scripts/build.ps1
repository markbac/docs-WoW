#!/usr/bin/env pwsh
<#
Build script for Cornerstone book

Steps:
1. Remove existing split/ and diag/ directories
2. Split monolithic markdown into structured book layout
3. Render diagrams via Kroki
4. Build PDF + EPUB via Pandoc / LaTeX

Assumptions:
- Running from book root
- Python is on PATH
- Scripts live in ..\..\scripts\
#>

$ErrorActionPreference = "Stop"

Write-Host "== Cornerstone build started ==" -ForegroundColor Cyan

# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------

$RootDir      = Get-Location
$ScriptsDir   = Resolve-Path "..\..\scripts"
$InputMd      = Join-Path $RootDir "cornerstone_framework_v2.md"

$SplitDir     = Join-Path $RootDir "split"
$DiagDir      = Join-Path $RootDir "diag"
$DistDir      = Join-Path $RootDir "dist"

$TemplateTex  = Join-Path $ScriptsDir "templates\book.tex"
$PdfOut       = "cornerstone.pdf"
$EpubOut      = "cornerstone.epub"

# ------------------------------------------------------------
# Clean previous outputs
# ------------------------------------------------------------

Write-Host "Cleaning previous build artefacts..." -ForegroundColor Yellow

if (Test-Path $SplitDir) {
    Write-Host "  Removing split/" -ForegroundColor DarkGray
    Remove-Item -Recurse -Force $SplitDir
}

if (Test-Path $DiagDir) {
    Write-Host "  Removing diag/" -ForegroundColor DarkGray
    Remove-Item -Recurse -Force $DiagDir
}

if (Test-Path $DistDir) {
    Write-Host "  Removing dist/" -ForegroundColor DarkGray
    Remove-Item -Recurse -Force $DistDir
}

# ------------------------------------------------------------
# Step 1: Split book
# ------------------------------------------------------------

Write-Host "Splitting book markdown..." -ForegroundColor Cyan

python `
    "$ScriptsDir\split_book.py" `
    --verbose `
    "$InputMd" `
    --out "$SplitDir"

# ------------------------------------------------------------
# Step 2: Render diagrams (Kroki)
# ------------------------------------------------------------

Write-Host "Rendering diagrams via Kroki..." -ForegroundColor Cyan

python `
    "$ScriptsDir\render_diagrams_kroki.py" `
    "$SplitDir" `
    "$DiagDir"

# ------------------------------------------------------------
# Step 3: Build PDF + EPUB
# ------------------------------------------------------------

Write-Host "Building PDF and EPUB..." -ForegroundColor Cyan

powershell -ExecutionPolicy Bypass -File `
    "$ScriptsDir\build_book.ps1" `
    -Root "$DiagDir" `
    -Dist "$DistDir" `
    -Template "$TemplateTex" `
    -Pdf "$PdfOut" `
    -Epub "$EpubOut" `
    -DebugMode

# ------------------------------------------------------------
# Done
# ------------------------------------------------------------

Write-Host "== Build complete ==" -ForegroundColor Green
Write-Host "Outputs:" -ForegroundColor Green
Write-Host "  PDF : $DistDir\$PdfOut"
Write-Host "  EPUB: $DistDir\$EpubOut"
