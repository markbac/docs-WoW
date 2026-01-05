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

    $FrontCoverSrc = Join-Path $Root "\front.png"
    $BackCoverSrc  = Join-Path $Root "\back.png"

    if (-not (Test-Path $MediaDir)) {
        throw "Media directory not found: $MediaDir"
    }

    $result = @{
        Front = $null
        Back  = $null
    }

    if (Test-Path $FrontCoverSrc) {
        $dst = Join-Path $MediaDir "front.png"
        Copy-Item -Force $FrontCoverSrc $dst
        Ok "Copied front cover to $dst"
        $result.Front = $dst
    } else {
        Warn "Front cover not found: $FrontCoverSrc"
    }

    if (Test-Path $BackCoverSrc) {
        $dst = Join-Path $MediaDir "back.png"
        Copy-Item -Force $BackCoverSrc $dst
        Ok "Copied back cover to $dst"
        $result.Back = $dst
    } else {
        Warn "Back cover not found: $BackCoverSrc"
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
if (-not (Test-Path $Root)) { throw "Root directory not found: $Root" }
$Root = (Resolve-Path $Root).Path

if (-not (Test-Path $Dist)) {
    New-Item -ItemType Directory -Path $Dist | Out-Null
}
$Dist = (Resolve-Path $Dist).Path

if ($Template) {
    if (-not (Test-Path $Template)) { throw "Template not found: $Template" }
    $Template = (Resolve-Path $Template).Path
}

# =================================================
# Traceability
# =================================================
$GitHash = (git rev-parse --short HEAD 2>$null)
if (-not $GitHash) { $GitHash = "N/A" }

$DirtyCount = (git status --porcelain 2>$null | Measure-Object).Count
$GitDirty = if ($DirtyCount -gt 0) { "Dirty" } else { "Clean" }

$BuildDate = (Get-Date).ToUniversalTime().ToString("yyyy-MM-dd HH:mm:ss 'UTC'")

Log "Building Firmitas"
Dbg "Git commit : $GitHash ($GitDirty)"
Dbg "Build date : $BuildDate"
Dbg "Root       : $Root"
Dbg "Dist       : $Dist"

# =================================================
# Collect Markdown files (new structure)
# =================================================
$InputFiles = @()

# Front matter (must be first)
$FrontMatter = Join-Path $Root "_front_matter.md"
if (-not (Test-Path $FrontMatter)) {
    throw "Missing _front_matter.md in $Root"
}
$InputFiles += $FrontMatter

# Front control (optional)
$FrontControl = Join-Path $Root "_front_control.md"
if (Test-Path $FrontControl) {
    $InputFiles += $FrontControl
}

# Sections
Get-ChildItem $Root -Directory |
    Where-Object { $_.Name -match '^\d{2}_' } |
    Sort-Object Name |
    ForEach-Object {

        # Section intro
        $sectionIntro = Join-Path $_.FullName "00_section.md"
        if (Test-Path $sectionIntro) {
            $InputFiles += $sectionIntro
        }

        # Chapters (new location)
        $chaptersDir = Join-Path $_.FullName "chapters"
        if (Test-Path $chaptersDir) {
            Get-ChildItem $chaptersDir -File -Filter "*.md" |
                Sort-Object Name |
                ForEach-Object {
                    $InputFiles += $_.FullName
                }
        }
    }

Ok "Collected $($InputFiles.Count) Markdown files"


# =================================================
# Media preparation
# =================================================
$FlattenedMedia = Join-Path $Dist "_pandoc_media"
Flatten-PandocMedia -Root $Root -OutDir $FlattenedMedia

$MediaDir = Join-Path $FlattenedMedia "media"
$covers = Copy-CoverImages -Root $Root -MediaDir $MediaDir

# =================================================
# Cover metadata (safe keys)
# =================================================
$CoverMeta = @()

if ($covers.Front) {
    $frontTexPath = ($covers.Front -replace '\\', '/')
    $CoverMeta += "--metadata"
    $CoverMeta += "cover_front=$frontTexPath"
}

if ($covers.Back) {
    $backTexPath = ($covers.Back -replace '\\', '/')
    $CoverMeta += "--metadata"
    $CoverMeta += "cover_back=$backTexPath"
}



# =================================================
# Common Pandoc arguments
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
    "--standalone",
    "--metadata=link-citations=true"
)


$PandocPdfOnly = @(
    "--top-level-division=chapter",
    "--pdf-engine=xelatex"
)

# =================================================
# PDF
# =================================================
Log "Generating PDF"

$pandocPdf = @()
$pandocPdf += $InputFiles
$pandocPdf += $PandocCommon
$pandocPdf += $PandocPdfOnly
$pandocPdf += $CoverMeta

if ($Template) {
    $pandocPdf += "--template=$Template"
}

$pandocPdf += "-o"
$pandocPdf += (Join-Path $Dist $Pdf)

pandoc @pandocPdf
if ($LASTEXITCODE -ne 0) {
    throw "Pandoc PDF build failed"
}

Ok "PDF written to $(Join-Path $Dist $Pdf)"

# =================================================
# EPUB
# =================================================
Log "Generating EPUB"

$pandocEpub = @()
$pandocEpub += $InputFiles
$pandocEpub += $PandocCommon
$pandocEpub += "--toc"
$pandocEpub += "--toc-depth=2"

if ($covers.Front) {
    $pandocEpub += "--epub-cover-image=$($covers.Front)"
}

$pandocEpub += "-o"
$pandocEpub += (Join-Path $Dist $Epub)

pandoc @pandocEpub
if ($LASTEXITCODE -ne 0) {
    throw "Pandoc EPUB build failed"
}

Ok "EPUB written to $(Join-Path $Dist $Epub)"

Log "Build complete"
