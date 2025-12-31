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
# Logging helpers (ASCII-safe)
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
            $name = $_.Name

            if ($seen.ContainsKey($name)) {
                throw @"
Media filename collision detected:

  $name
  - $($seen[$name])
  - $($_.FullName)

Media filenames must be globally unique.
"@
            }

            $seen[$name] = $_.FullName

            Copy-Item `
                -Path $_.FullName `
                -Destination (Join-Path $mediaOut $name)

            Dbg "  + $name"
        }
    }

    Ok "Flattened $($seen.Count) media files"
}

# =================================================
# Resolve and validate paths
# =================================================
if (-not (Test-Path $Root)) {
    throw "Root directory not found: $Root"
}
$Root = (Resolve-Path $Root).Path

if (-not (Test-Path $Dist)) {
    New-Item -ItemType Directory -Path $Dist | Out-Null
}
$Dist = (Resolve-Path $Dist).Path

if ($Template) {
    if (-not (Test-Path $Template)) {
        throw "Template not found: $Template"
    }
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

Log "Building Cornerstone"
Dbg "Git commit : $GitHash ($GitDirty)"
Dbg "Build date : $BuildDate"
Dbg "Root       : $Root"
Dbg "Dist       : $Dist"

# =================================================
# Collect Markdown files (numeric, deterministic)
# =================================================
$InputFiles = @()

$FrontMatter = Join-Path $Root "_front_matter.md"
if (-not (Test-Path $FrontMatter)) {
    throw "Missing _front_matter.md in $Root"
}
$InputFiles += $FrontMatter
Dbg "Front matter: _front_matter.md"

$FrontControl = Join-Path $Root "_front_control.md"
if (Test-Path $FrontControl) {
    $InputFiles += $FrontControl
    Dbg "Front control: _front_control.md"
}

$Sections = Get-ChildItem $Root -Directory |
    Where-Object { $_.Name -match '^\d{2}_' } |
    Sort-Object Name

foreach ($Section in $Sections) {
    Dbg "Dir: $($Section.Name)"

    $SectionIntro = Join-Path $Section.FullName "00_section.md"
    if (Test-Path $SectionIntro) {
        $InputFiles += $SectionIntro
        Dbg "  + 00_section.md"
    }

    Get-ChildItem $Section.FullName -File -Filter "*.md" |
        Where-Object { $_.Name -ne "00_section.md" } |
        Sort-Object Name |
        ForEach-Object {
            $InputFiles += $_.FullName
            Dbg "  + $($_.Name)"
        }
}

Ok "Collected $($InputFiles.Count) Markdown files"

# =================================================
# Optional covers
# =================================================
$CoverMeta = @()

$FrontCover = Join-Path $Root "cover\front.png"
$BackCover  = Join-Path $Root "cover\back.png"

if (Test-Path $FrontCover) {
    $CoverMeta += "--metadata"
    $CoverMeta += "front-cover=$FrontCover"
    Dbg "Front cover: $FrontCover"
} else {
    Warn "Front cover not found, skipping"
}

if (Test-Path $BackCover) {
    $CoverMeta += "--metadata"
    $CoverMeta += "back-cover=$BackCover"
    Dbg "Back cover: $BackCover"
} else {
    Warn "Back cover not found, skipping"
}

# =================================================
# Flatten media
# =================================================
$FlattenedMedia = Join-Path $Dist "_pandoc_media"

Flatten-PandocMedia `
    -Root $Root `
    -OutDir $FlattenedMedia

# =================================================
# Common Pandoc arguments
# =================================================
$PandocCommon = @(
    "--from", "markdown+yaml_metadata_block",
    "--number-sections",
    "--top-level-division=chapter",
    "--metadata", "build_date=$BuildDate",
    "--metadata", "git_commit=$GitHash",
    "--metadata", "git_dirty=$GitDirty",
    "--resource-path=$FlattenedMedia"
)

# =================================================
# PDF
# =================================================
Log "Generating PDF"

$pandocPdf = @()
$pandocPdf += $InputFiles
$pandocPdf += $PandocCommon
$pandocPdf += $CoverMeta

if ($Template) {
    $pandocPdf += "--template=$Template"
}

$pandocPdf += "--pdf-engine=xelatex"
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
$pandocEpub += $CoverMeta
$pandocEpub += "--to=epub"
$pandocEpub += "-o"
$pandocEpub += (Join-Path $Dist $Epub)

pandoc @pandocEpub
if ($LASTEXITCODE -ne 0) {
    throw "Pandoc EPUB build failed"
}

Ok "EPUB written to $(Join-Path $Dist $Epub)"

Log "Build complete"
