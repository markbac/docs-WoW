#!/usr/bin/env python3
"""
mkdocs_pdf_build.py

Build a single combined PDF from an MkDocs project using the mkdocs-to-pdf plugin,
without running `mkdocs serve`.

What this script does
---------------------
- Loads mkdocs.yml with `yaml.full_load` so `!!python/name:` tags resolve.
- Replaces live function objects (from `pymdownx.superfences` and `pymdownx.emoji`)
  back to their YAML tag strings, then post-processes the dumped YAML so those
  values are emitted as *real* tagged scalars. This lets MkDocs rebuild the
  callables when it loads the generated config.
- Ensures the `to-pdf` plugin exists and is configured for a single combined PDF.
- Sets the PDF cover subtitle dynamically to traceability info (commit/date/dirty).
- Injects the same traceability into `config.extra.pdf_build.subtitle_traceability`
  for use on pages or custom templates.
- Normalises image links so the PDF renderer can embed them:
  * rewrites absolute “/…” links to relative
  * downloads external http/https images into docs/assets/pdf_ext/ and rewrites links
- Pre-renders Mermaid blocks to SVG (supports ```mermaid / ``` mermaid / ~~~mermaid /
  :::mermaid), replaces them with image links, and logs a summary.
- Copies docs to a temporary workspace and creates missing `index.md` in directories
  that contain Markdown files to improve PDF/TOC structure.
- Normalises `hooks:` paths to absolute paths so they still resolve from a temp dir.
- Exports REPO_ROOT to the environment so hooks can find LICENSE and repo URL.

Exit codes
----------
0 = success
2 = mkdocs.yml not found
3 = docs dir not found
4 = no PDFs produced
"""
from __future__ import annotations

import argparse
import datetime
import importlib
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List

import yaml

# Explicit imports so yaml.full_load can resolve !!python/name tags in mkdocs.yml
import pymdownx.superfences  # noqa: F401
import material.extensions.emoji as material_emoji  # noqa: F401

# YAML tag constants to round-trip function objects safely
FENCE_CODE_FORMAT_TAG = "!!python/name:pymdownx.superfences.fence_code_format"
EMOJI_TWEMOJI_TAG = "!!python/name:material.extensions.emoji.twemoji"
EMOJI_TO_SVG_TAG = "!!python/name:material.extensions.emoji.to_svg"

# -----------------------------------------------------------------------------
# CONFIGURATION CONSTANTS
# -----------------------------------------------------------------------------
# Maximum image height in pixels for all diagrams and embedded images.
# Approx. A4 page height ≈ 1050–1100px @ 96 DPI
MAX_IMAGE_HEIGHT_PX = 900

def _slugify(text: str) -> str:
    import re, unicodedata
    t = unicodedata.normalize("NFKD", text)
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = t.lower()
    t = re.sub(r"[^a-z0-9]+", "-", t)
    t = re.sub(r"-{2,}", "-", t).strip("-")
    return t

def prefix_heading_ids(work_docs: Path) -> None:
    """
    Add explicit anchors that match '#<relpath>:<slug>' targets expected by the PDF.
    - Insert <a id="base"></a> at the top (page root)
    - Insert <a id="base:slug"></a> immediately BEFORE every ATX heading (#..######)
    No Jinja, no attr_list needed.
    """
    import re

    heading_re = re.compile(r"^(?P<Hashes>#{1,6})\s*(?P<Text>.+?)\s*$")

    for md in sorted(work_docs.rglob("*.md")):
        rel = md.relative_to(work_docs).as_posix()  # e.g. guides/git-branching.md
        if rel.endswith("/index.md"):
            base = rel[:-len("/index.md")] + "/"    # e.g. guides/
        elif rel.endswith(".md"):
            base = rel[:-3]                         # e.g. guides/git-branching
        else:
            base = rel

        lines = md.read_text(encoding="utf-8").splitlines()
        out: list[str] = []
        changed = False

        # Inject a page-root anchor at the very top
        out.append(f'<a id="{base}"></a>')
        out.append("")  # spacing

        for line in lines:
            m = heading_re.match(line)
            if m:
                text = m.group("Text").strip()
                slug = _slugify(text)
                full_id = f"{base}--{slug}"
                out.append(f'<a id="{full_id}"></a>')
                changed = True
            out.append(line)

        if changed:
            md.write_text("\n".join(out) + "\n", encoding="utf-8")



def get_git_metadata() -> tuple[str, str, str]:
    """
    Fetch Git commit hash, dirty status, and a UTC timestamp.
    """
    try:
        git_hash = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.STDOUT
        ).decode("utf-8").strip()

        git_status = subprocess.check_output(
            ["git", "status", "--porcelain"], stderr=subprocess.STDOUT
        ).decode("utf-8").strip()

        dirty_status = "YES (Uncommitted Changes)" if git_status else "NO (Clean)"
    except subprocess.CalledProcessError:
        git_hash = "N/A (Git not found or not a repo)"
        dirty_status = "N/A"

    now_utc = datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )
    return git_hash, dirty_status, now_utc


def load_yaml(path: Path) -> Dict[str, Any]:
    """
    Load YAML with yaml.full_load so !!python/name tags resolve to callables.
    """
    with path.open("r", encoding="utf-8") as fh:
        return yaml.full_load(fh) or {}


def dump_yaml(data: Dict[str, Any], path: Path) -> None:
    """
    Dump YAML with yaml.safe_dump, then post-process to ensure specific values
    are emitted as real tagged scalars (not quoted strings) so MkDocs/PyYAML
    reconstruct the callables (pymdownx.superfences, pymdownx.emoji).
    """
    text = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)

    # Convert quoted tag strings into real tagged scalars for known keys.
    # Example:
    #   emoji_index: '!!python/name:material.extensions.emoji.twemoji'
    # becomes:
    #   emoji_index: !!python/name:material.extensions.emoji.twemoji
    import re

    tag_literals = [
        re.escape(FENCE_CODE_FORMAT_TAG),
        re.escape(EMOJI_TWEMOJI_TAG),
        re.escape(EMOJI_TO_SVG_TAG),
    ]
    keys = ["format", "emoji_index", "emoji_generator"]

    for key in keys:
        for tag in tag_literals:
            text = re.sub(
                rf"(^\s*{key}\s*:\s*)['\"]({tag})['\"]\s*$",
                rf"\1\2",
                text,
                flags=re.MULTILINE,
            )

    with path.open("w", encoding="utf-8") as fh:
        fh.write(text)


def restore_pymdownx_tags(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Walk the loaded config and replace live function objects (from yaml.full_load)
    with their original !!python/name tag strings so safe_dump can serialise them.
    """
    new_config = config.copy()
    markdown_extensions = new_config.get("markdown_extensions", [])
    if not isinstance(markdown_extensions, list):
        return new_config

    new_markdown_extensions: List[Any] = []

    for item in markdown_extensions:
        cloned_item = item.copy() if isinstance(item, dict) else item

        # Handle pymdownx.superfences custom_fences.format
        if isinstance(cloned_item, dict) and "pymdownx.superfences" in cloned_item:
            sf_config = cloned_item["pymdownx.superfences"]
            custom_fences = sf_config.get("custom_fences", [])
            new_custom_fences = []
            for fence in custom_fences:
                fence_copy = fence.copy() if isinstance(fence, dict) else fence
                if (
                    isinstance(fence_copy, dict)
                    and "format" in fence_copy
                    and fence_copy["format"] is pymdownx.superfences.fence_code_format
                ):
                    fence_copy["format"] = FENCE_CODE_FORMAT_TAG
                new_custom_fences.append(fence_copy)
            sf_config["custom_fences"] = new_custom_fences

        # Handle pymdownx.emoji functions
        if isinstance(cloned_item, dict) and "pymdownx.emoji" in cloned_item:
            em_config = cloned_item["pymdownx.emoji"] or {}
            if isinstance(em_config, dict):
                if (
                    "emoji_index" in em_config
                    and em_config["emoji_index"] is material_emoji.twemoji
                ):
                    em_config["emoji_index"] = EMOJI_TWEMOJI_TAG
                if (
                    "emoji_generator" in em_config
                    and em_config["emoji_generator"] is material_emoji.to_svg
                ):
                    em_config["emoji_generator"] = EMOJI_TO_SVG_TAG
                cloned_item["pymdownx.emoji"] = em_config

        new_markdown_extensions.append(cloned_item)

    new_config["markdown_extensions"] = new_markdown_extensions
    return new_config


def ensure_with_pdf_plugin(config: Dict[str, Any], subtitle_text: str) -> None:
    """
    Ensure 'with-pdf' plugin exists and is configured for a single combined PDF.
    Adds traceability text to the cover and exposes the same in extra.pdf_build.
    """
    plugins = list(config.get("plugins", []))
    idx = None
    for i, item in enumerate(plugins):
        if isinstance(item, str) and item.strip() == "with-pdf":
            plugins[i] = {"with-pdf": {}}
            idx = i
            break
        if isinstance(item, dict) and "with-pdf" in item:
            idx = i
            break
    if idx is None:
        plugins.append({"with-pdf": {}})
        idx = len(plugins) - 1

    block = plugins[idx]["with-pdf"]
    block.setdefault("output_path", "pdf/document.pdf")
    block.setdefault("cover", True)
    block.setdefault("cover_title", config.get("site_name", "Documentation"))
    block.setdefault("cover_subtitle", subtitle_text)
    block.setdefault("enabled_if_env", "ENABLE_PDF_EXPORT")
    block.setdefault("verbose", True)
    block.setdefault("toc_level", 3)
    block.setdefault("debug", True)
    block.setdefault("debug_html", True)
    block.setdefault("single_html", True)

    config["plugins"] = plugins

    extra = dict(config.get("extra") or {})
    pdf_build = dict(extra.get("pdf_build") or {})
    pdf_build["subtitle_traceability"] = subtitle_text
    extra["pdf_build"] = pdf_build
    config["extra"] = extra



def ensure_markdown_extensions(config: Dict[str, Any]) -> None:
    """
    Ensure 'toc' is present (handy for outlines in PDF).
    """
    me = list(config.get("markdown_extensions", []))
    has_toc = any((m == "toc") or (isinstance(m, dict) and "toc" in m) for m in me)
    if not has_toc:
        me.append({"toc": {"permalink": True}})
    config["markdown_extensions"] = me


def switch_theme_to_material(config: Dict[str, Any]) -> None:
    """
    Force Material theme for print-friendly defaults (only for the PDF run).
    """
    config["theme"] = {"name": "material", "palette": [{"scheme": "default"}]}


def copy_docs_tree(src_docs: Path, dst_docs: Path) -> None:
    """
    Copy docs/ into a temp working directory.
    """
    if dst_docs.exists():
        shutil.rmtree(dst_docs)
    shutil.copytree(src_docs, dst_docs)


def create_ephemeral_section_indexes(work_docs: Path) -> None:
    """
    Create minimal index.md files in folders that have markdown files but no index.
    """
    for directory in sorted(work_docs.rglob("*")):
        if not directory.is_dir():
            continue
        if directory.name.startswith("."):
            continue
        md_files = list(directory.glob("*.md"))
        if not md_files:
            continue
        index_md = directory / "index.md"
        if index_md.exists():
            continue
        title = directory.name.replace("-", " ").replace("_", " ").title()
        index_md.write_text(f"# {title}\n\n", encoding="utf-8")


def limit_image_heights(work_docs: Path, max_height_px: int = MAX_IMAGE_HEIGHT_PX):
    """
    Inject style attributes limiting image height directly into Markdown image tags.
    This prevents oversized images from causing WeasyPrint to stop rendering.
    """
    import re
    pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
    for md in work_docs.rglob("*.md"):
        text = md.read_text(encoding="utf-8")
        # Inject inline style limiting height
        text = pattern.sub(
            r'![\1](\2){style="max-height:%dpx; height:auto;"}' % max_height_px,
            text
        )
        md.write_text(text, encoding="utf-8")


def normalise_image_links(work_docs: Path) -> None:
    """
    Ensure images referenced in Markdown are resolvable by the PDF renderer:
    - Rewrite absolute '/...' paths to relative paths (rooted at work_docs)
    - Download external images (http/https) into assets/pdf_ext/ and rewrite links
    """
    import re
    import urllib.request
    import urllib.error

    http_img = re.compile(r'!\[([^\]]*)\]\((https?://[^\s)]+)\)')
    abs_img = re.compile(r'!\[([^\]]*)\]\((/[^)\s]+)\)')  # starts with a single '/'

    ext_dir = work_docs / "assets" / "pdf_ext"
    ext_dir.mkdir(parents=True, exist_ok=True)

    for md in work_docs.rglob("*.md"):
        text = md.read_text(encoding="utf-8")
        changed = False

        # 1) external images → download
        def repl_http(m):
            nonlocal changed
            alt, url = m.group(1), m.group(2)
            suffix = Path(url).suffix
            suffix = suffix if len(suffix) <= 8 else suffix[:8]
            fname = f"ext_{abs(hash(url)) & 0xFFFFFFFF:08x}{suffix}"
            out = ext_dir / fname
            if not out.exists():
                try:
                    with urllib.request.urlopen(url, timeout=10) as r, open(out, "wb") as f:
                        f.write(r.read())
                except (urllib.error.URLError, TimeoutError, OSError):
                    # leave original link if fetch fails
                    return m.group(0)
            rel = out.relative_to(work_docs).as_posix()
            changed = True
            return f"![{alt}]({rel})"

        text = http_img.sub(repl_http, text)

        # 2) absolute /… paths → relative FROM THIS PAGE'S FOLDER
        def repl_abs(m):
            nonlocal changed
            alt, path = m.group(1), m.group(2)   # e.g. "/assets/img.png"
            target = (work_docs / path.lstrip("/")).resolve()
            try:
                rel = os.path.relpath(target, md.parent).replace(os.sep, "/")
            except Exception:
                # Fallback: keep original if something odd happens
                return m.group(0)
            changed = True
            return f"![{alt}]({rel})"

        text = abs_img.sub(repl_abs, text)

        if changed:
            md.write_text(text, encoding="utf-8")

def resize_large_images(work_docs: Path, max_height_px: int = MAX_IMAGE_HEIGHT_PX):
    """
    Resize any existing PNG/JPEG images over a given height limit.
    Uses Pillow to safely scale down while keeping aspect ratio.
    """
    from PIL import Image
    for img_path in work_docs.rglob("*.[pjP][pnP][gG]*"):
        try:
            with Image.open(img_path) as im:
                w, h = im.size
                if h > max_height_px:
                    scale = max_height_px / h
                    new_size = (int(w * scale), int(h * scale))
                    im = im.resize(new_size, Image.Resampling.LANCZOS)
                    im.save(img_path)
                    print(f"Resized {img_path.name} → {new_size}")
        except Exception as e:
            print(f"WARNING: failed to resize {img_path}: {e}", file=sys.stderr)


def preprocess_mermaid(work_docs: Path, assets_dir: Path, max_height_px: int = MAX_IMAGE_HEIGHT_PX) -> None:
    """
    Render Mermaid blocks to PNG (via mermaid-cli) and replace them with Markdown image links.
    - Filenames are predictable: <relative_path>_<n>.png (incremental within each file)
    - Supports ```mermaid, ~~~mermaid, and :::mermaid blocks
    - Logs detailed counts
    """
    import re
    import tempfile as _tmp

    assets_dir.mkdir(parents=True, exist_ok=True)
    mmdc = shutil.which("mmdc")
    use_npx = mmdc is None

    fence_re = re.compile(
        r"(?P<fence>```|~~~)\s*mermaid[^\n]*\n(?P<code>.*?)(?:\n)(?P=fence)",
        re.DOTALL | re.IGNORECASE,
    )
    colon_re = re.compile(
        r"^:::\s*mermaid[^\n]*\n(?P<code>.*?)(?:\n):::\s*$",
        re.DOTALL | re.IGNORECASE | re.MULTILINE,
    )

    def render_png(code: str, out_path: Path) -> None:
        """Render Mermaid code to PNG using CLI."""
        with _tmp.NamedTemporaryFile("w", delete=False, suffix=".mmd") as temp_file:
            temp_file.write(code)
            mmd_in = temp_file.name

        if use_npx:
            cmd = ["npx", "@mermaid-js/mermaid-cli@10.4.0", "-i", mmd_in, "-o", str(out_path), "-H", str(max_height_px)]
        else:
            cmd = [mmdc, "-i", mmd_in, "-o", str(out_path), "-H", str(max_height_px)]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except Exception as exc:
            # Write a fallback SVG so the PDF build doesn’t crash
            out_path.write_text(
                '<svg xmlns="http://www.w3.org/2000/svg" width="640" height="120">'
                '<rect width="100%" height="100%" fill="#f7f7f7" />'
                f'<text x="12" y="32" font-family="sans-serif" font-size="18" fill="#d00">'
                f"Mermaid render error: {type(exc).__name__}</text></svg>",
                encoding="utf-8",
            )
            print(
                f"WARNING: Mermaid render failed; inserted placeholder. "
                f"Cmd: {' '.join(cmd)} | Error: {exc}",
                file=sys.stderr,
            )

    total_found = 0
    total_replaced = 0

    for markdown_file in sorted(work_docs.rglob("*.md")):
        text = markdown_file.read_text(encoding="utf-8")
        replaced_here = 0
        found_here = 0

        # Create a base name based on relative path (safe for filesystem)
        rel_stem = markdown_file.relative_to(work_docs).with_suffix("").as_posix()
        safe_base = rel_stem.replace("/", "_").replace("\\", "_")

        def sub_mermaid(m, counter=[0]):  # mutable default to increment per file
            nonlocal replaced_here, found_here
            found_here += 1
            counter[0] += 1
            code = m.group("code").strip()
            fname = f"{safe_base}_{counter[0]:02d}.png"
            out_path = assets_dir / fname
            if not out_path.exists():
                render_png(code, out_path)
            rel = os.path.relpath(out_path, markdown_file.parent).replace(os.sep, "/")
            replaced_here += 1
            return f"![diagram]({rel})"

        text = fence_re.sub(sub_mermaid, text)
        text = colon_re.sub(sub_mermaid, text)

        if replaced_here:
            markdown_file.write_text(text, encoding="utf-8")

        total_found += found_here
        total_replaced += replaced_here

    print(f"Mermaid: found {total_found} blocks, replaced {total_replaced} with PNGs.")


def normalise_hooks_paths(config: Dict[str, Any], base_dir: Path) -> None:
    """
    Make 'hooks' entries absolute so they resolve when the config file is in a temp dir.
    If a hook path doesn't exist, drop it. If none remain, remove 'hooks'.
    """
    hooks = config.get("hooks")
    if not hooks:
        return
    if isinstance(hooks, str):
        hooks = [hooks]
    if not isinstance(hooks, list):
        return
    fixed: list[str] = []
    for entry in hooks:
        p = Path(entry)
        abs_path = p if p.is_absolute() else (base_dir / p).resolve()
        if abs_path.exists():
            fixed.append(str(abs_path))
        else:
            print(f"WARNING: Hook not found; skipping: {abs_path}", file=sys.stderr)
    if fixed:
        config["hooks"] = fixed
    else:
        config.pop("hooks", None)


def check_dependencies() -> None:
    """
    Lightweight preflight checks for helpful messages. Does not hard-fail.
    """
    try:
        importlib.import_module("mkdocs")  # noqa: F401
    except Exception:
        print(
            "WARNING: MkDocs not importable in this interpreter. "
            "Ensure you're using the same Python where you installed mkdocs.",
            file=sys.stderr,
        )
    try:
        # Many plugins register via entry points; this import may fail even if installed.
        importlib.import_module("mkdocs_to_pdf")  # noqa: F401
    except Exception:
        print(
            "NOTE: Could not import 'mkdocs_to_pdf' module directly. "
            "If the 'to-pdf' plugin is installed, MkDocs can still load it via entry points.",
            file=sys.stderr,
        )


def main() -> int:
    """
    Build a single PDF via mkdocs-to-pdf with a generated config.
    """
    parser = argparse.ArgumentParser(
        description="Build a single PDF via mkdocs-to-pdf (no serve)."
    )
    parser.add_argument("--src", default="mkdocs.yml", help="Path to source mkdocs.yml")
    parser.add_argument(
        "--outdir", default="dist/pdf", help="Destination directory for the generated PDF"
    )
    parser.add_argument("--keep-site", action="store_true", help="Keep 'site/' after build")
    parser.add_argument(
        "--no-theme-switch", action="store_true", help="Do not override theme to Material for PDF"
    )
    parser.add_argument(
        "--max-image-height", type=int, default=MAX_IMAGE_HEIGHT_PX,
        help="Maximum image height (in pixels) for diagrams and inline images."
    )
    args = parser.parse_args()

    check_dependencies()

    repo_root = Path.cwd()
    src_cfg_path = repo_root / args.src
    if not src_cfg_path.exists():
        print(f"ERROR: {src_cfg_path} not found", file=sys.stderr)
        return 2

    # 1) Traceability
    git_hash, dirty_status, generated_on = get_git_metadata()
    pdf_subtitle = f"Generated: {generated_on}. Commit: {git_hash} (Dirty: {dirty_status})"

    print(f"--- PDF Build Traceability ---")
    print(f"Git Hash: {git_hash}")
    print(f"Dirty Status: {dirty_status}")
    print(f"Generated On: {generated_on}")
    print(f"------------------------------")

    # 2) Load + fix tags + hooks
    cfg = load_yaml(src_cfg_path)
    pdf_cfg = restore_pymdownx_tags(cfg)
    normalise_hooks_paths(pdf_cfg, src_cfg_path.parent)

    # 3) Validate docs/
    docs_dir_name = pdf_cfg.get("docs_dir", "docs")
    src_docs = repo_root / docs_dir_name
    if not src_docs.exists():
        print(f"ERROR: docs directory '{docs_dir_name}' not found", file=sys.stderr)
        return 3

    # 4) Temp workspace
    tmp_root = Path(tempfile.mkdtemp(prefix=".mkdocs-to-pdf-"))
    work_docs = tmp_root / "docs"
    assets_dir = work_docs / "assets" / "mermaid"
    copy_docs_tree(src_docs, work_docs)
    create_ephemeral_section_indexes(work_docs)
    #prefix_heading_ids(work_docs)    
    normalise_image_links(work_docs)
    limit_image_heights(work_docs, max_height_px=args.max_image_height)

    # 5) Pre-render Mermaid
    try:
        preprocess_mermaid(work_docs, assets_dir, args.max_image_height)
    except FileNotFoundError as error:
        print(
            "WARNING: Mermaid CLI not found (mmdc/npx). Mermaid diagrams will NOT render in PDFs. "
            f"({error})",
            file=sys.stderr,
        )

    resize_large_images(work_docs, max_height_px=args.max_image_height)

    # 6) Mutate cfg for PDF run
    ensure_with_pdf_plugin(pdf_cfg, pdf_subtitle)
    ensure_markdown_extensions(pdf_cfg)
    if not args.no_theme_switch:
        switch_theme_to_material(pdf_cfg)

    # Force docs/site paths for the temp build
    pdf_cfg["docs_dir"] = str(work_docs)
    pdf_cfg["site_dir"] = str(repo_root / "site")

    # 7) Write generated config (with post-processed tags)
    tmp_cfg_path = tmp_root / "mkdocs-to-pdf.generated.yml"
    dump_yaml(pdf_cfg, tmp_cfg_path)

    # 8) Build
    env = os.environ.copy()
    env["ENABLE_PDF_EXPORT"] = "1"
    env["REPO_ROOT"] = str(repo_root)  # for hooks to find LICENSE and repo_url correctly
    #env["WEASYPRINT_DEBUG"] = "1"
    #env["WEASYPRINT_LOG_LEVEL"] = "DEBUG"
    #env["WEASYPRINT_VERBOSE"] = "1"
    #env["MKDOCS_TO_PDF_DEBUG_HTML"] = "1"

    print("▶ Building PDF with mkdocs-to-pdf.generated.yml …")
    try:
        subprocess.run(
            ["mkdocs", "build", "--config-file", str(tmp_cfg_path), "--clean"],
            check=True,
            env=env,
        )
    except subprocess.CalledProcessError as cpe:
        print(
            "ERROR: MkDocs build failed. Check the above MkDocs error for details.\n"
            f"Hint: ensure 'mkdocs-to-pdf' is installed and your plugins/extensions load in this venv.\n"
            f"Command: {' '.join(cpe.cmd)} | Return code: {cpe.returncode}",
            file=sys.stderr,
        )
        return cpe.returncode or 1

    # 9) Collect result
    produced = repo_root / "site" / "pdf"
    pdfs = list(produced.rglob("*.pdf"))
    if not pdfs:
        print(
            "ERROR: No PDF produced under site/pdf/. Did the 'to-pdf' plugin run?",
            file=sys.stderr,
        )
        return 4

    outdir = repo_root / args.outdir
    outdir.mkdir(parents=True, exist_ok=True)
    for pdf in pdfs:
        shutil.copy2(pdf, outdir / pdf.name)
    print(f"✓ Copied {len(pdfs)} PDF(s) → {outdir}")

    # 10) Cleanup
    if not args.keep_site and (repo_root / "site").exists():
        shutil.rmtree(repo_root / "site")
    shutil.rmtree(tmp_root, ignore_errors=True)
    print("✅ Done. Traceability data injected into PDF configuration.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
