param (
    [Parameter(Mandatory = $true)]
    [string]$Root,

    [Parameter(Mandatory = $true)]
    [string]$Dist,

    [string]$Template,

    [Parameter(Mandatory = $true)]
    [string]$Pdf,

    [Parameter(Mandatory = $true)]
    [string]$Epub,

    [switch]$DebugMode
)

$ErrorActionPreference = "Stop"

# =================================================
# Logging helpers
# =================================================
function Log($msg)  { Write-Host "[INFO]  $msg" -ForegroundColor Cyan }
function Ok($msg)   { Write-Host "[ OK ]  $msg" -ForegroundColor Green }
function Warn($msg) { Write-Host "[WARN]  $msg" -ForegroundColor Yellow }
function Dbg($msg)  {
    if ($DebugMode) {
        Write-Host "[DBG ]  $msg" -ForegroundColor DarkGray
    }
}

# =================================================
# Copy cover images into Pandoc media
# =================================================
function Copy-CoverImages {
    param (
        [Parameter(Mandatory)]
        [string] $Root,

        [Parameter(Mandatory)]
        [string] $MediaDir
    )

    $FrontCoverSrc = Join-Path $Root "front.png"
    $BackCoverSrc  = Join-Path $Root "back.png"

    $result = @{ Front = $null; Back = $null }

    if (Test-Path $FrontCoverSrc) {
        $dst = Join-Path $MediaDir "front.png"
        Copy-Item -Force $FrontCoverSrc $dst
        Ok "Copied front cover"
        $result.Front = $dst
    } else {
        Warn "Front cover not found"
    }

    if (Test-Path $BackCoverSrc) {
        $dst = Join-Path $MediaDir "back.png"
        Copy-Item -Force $BackCoverSrc $dst
        Ok "Copied back cover"
        $result.Back = $dst
    } else {
        Warn "Back cover not found"
    }

    return $result
}

# =================================================
# Flatten media for Pandoc
# =================================================
function Flatten-PandocMedia {
    param (
        [Parameter(Mandatory)]
        [string] $Root,

        [Parameter(Mandatory)]
        [string] $OutDir
    )

    Log "Flattening media for Pandoc"

    if (Test-Path $OutDir) {
        Remove-Item -Recurse -Force $OutDir
    }

    $mediaOut = Join-Path $OutDir "media"
    New-Item -ItemType Directory -Path $mediaOut -Force | Out-Null

    $seen = @{}

    Get-ChildItem -Path $Root -Recurse -Directory -Filter media | ForEach-Object {
        Get-ChildItem -Path $_.FullName -File | ForEach-Object {
            if ($seen.ContainsKey($_.Name)) {
                throw "Media filename collision detected: $($_.Name)"
            }
            $seen[$_.Name] = $_.FullName
            Copy-Item -Force $_.FullName (Join-Path $mediaOut $_.Name)
            Dbg "  + $($_.Name)"
        }
    }

    Ok "Flattened $($seen.Count) media files"
}

# =================================================
# Resolve paths
# =================================================
$Root = (Resolve-Path $Root).Path

if (-not (Test-Path $Dist)) {
    New-Item -ItemType Directory -Path $Dist | Out-Null
}
$Dist = (Resolve-Path $Dist).Path

if ($Template) {
    $Template = (Resolve-Path $Template).Path
}

# =================================================
# Traceability
# =================================================
$GitHash = git rev-parse --short HEAD 2>$null
if ([string]::IsNullOrWhiteSpace($GitHash)) {
    $GitHash = "N/A"
}

$DirtyCount = 0
try {
    $DirtyCount = (git status --porcelain 2>$null | Measure-Object).Count
} catch {
    $DirtyCount = 0
}

$GitDirty  = if ($DirtyCount -gt 0) { "Dirty" } else { "Clean" }
$BuildDate = (Get-Date).ToUniversalTime().ToString("yyyy-MM-dd HH:mm:ss 'UTC'")

Log "Building Firmitas"
Dbg "Git commit : $GitHash ($GitDirty)"
Dbg "Build date : $BuildDate"

# =================================================
# Collect Markdown files (single content set)
# =================================================
function Collect-MarkdownFiles {
    $files = @()

    $files += (Join-Path $Root "_front_matter.md")

    $frontControl = Join-Path $Root "_front_control.md"
    if (Test-Path $frontControl) {
        $files += $frontControl
    }

    Get-ChildItem $Root -Directory |
        Where-Object { $_.Name -match '^\d{2}_' } |
        Sort-Object Name |
        ForEach-Object {

            $intro = Join-Path $_.FullName "00_section.md"
            if (Test-Path $intro) {
                $files += $intro
            }

            $chapters = Join-Path $_.FullName "chapters"
            if (Test-Path $chapters) {
                Get-ChildItem $chapters -File -Filter "*.md" |
                    Sort-Object Name |
                    ForEach-Object { $files += $_.FullName }
            }
        }

    return $files
}

$InputMarkdown = Collect-MarkdownFiles
Ok "Collected markdown files: $($InputMarkdown.Count)"

# =================================================
# Media prep
# =================================================
$FlattenedMedia = Join-Path $Dist "_pandoc_media"
Flatten-PandocMedia -Root $Root -OutDir $FlattenedMedia

$MediaDir = Join-Path $FlattenedMedia "media"
$covers   = Copy-CoverImages -Root $Root -MediaDir $MediaDir

# =================================================
# Pandoc arguments
# =================================================
$PandocCommon = @(
    "--from", "markdown+yaml_metadata_block",
    "--lua-filter=scripts\chapter_mapping.lua",
    "--metadata", "fontsize=10pt",
    "--metadata", "linestretch=1.15",
    "--metadata", "build_date=$BuildDate",
    "--metadata", "git_commit=$GitHash",
    "--metadata", "git_dirty=$GitDirty",
    "--metadata", "subtitle=",
    "--resource-path=$FlattenedMedia",
    "--section-divs",
    "--standalone"
)

$PandocPdfOnly = @(
    "--top-level-division=chapter",
    "--pdf-engine=xelatex"
)

$TemplateArg = @()
if ($Template) {
    $TemplateArg += "--template=$Template"
}

$CoverMeta = @()
if ($covers.Front) {
    $CoverMeta += "--metadata"
    $CoverMeta += "cover_front=$($covers.Front -replace '\\','/')"
}
if ($covers.Back) {
    $CoverMeta += "--metadata"
    $CoverMeta += "cover_back=$($covers.Back -replace '\\','/')"
}

$EpubCoverArg = @()
if ($covers.Front) {
    $EpubCoverArg += "--epub-cover-image=$($covers.Front)"
}

# =================================================
# PDF with covers
# =================================================
Log "Generating PDF (with covers)"

pandoc `
    $InputMarkdown `
    $PandocCommon `
    $PandocPdfOnly `
    $CoverMeta `
    $TemplateArg `
    -o (Join-Path $Dist $Pdf)

Ok "PDF with covers written"

# =================================================
# PDF without covers
# =================================================
$PdfNoCovers = [System.IO.Path]::GetFileNameWithoutExtension($Pdf) + "-nocovers.pdf"

Log "Generating PDF (no covers)"

pandoc `
    $InputMarkdown `
    $PandocCommon `
    $PandocPdfOnly `
    $TemplateArg `
    -o (Join-Path $Dist $PdfNoCovers)

Ok "PDF without covers written"

# =================================================
# EPUB
# =================================================
Log "Generating EPUB"

pandoc `
    $InputMarkdown `
    $PandocCommon `
    --toc `
    --toc-depth=2 `
    $EpubCoverArg `
    -o (Join-Path $Dist $Epub)

Ok "EPUB written"

Log "Build complete"
