#!/usr/bin/env python3
"""
mkdocs_pdf_build.py

Python script to prepare and build a single PDF from an MkDocs project
using the mkdocs-to-pdf plugin.

This script manages necessary configuration changes for a successful PDF build:
- It uses yaml.full_load to correctly parse custom Python tags (like those
  used by Pymdownx SuperFences) from the mkdocs.yml file.
- It restores these Python function objects back to their YAML string tags
  before dumping the temporary config file for the MkDocs build.
- It ensures 'mkdocs-to-pdf' is present and configured for a single combined PDF.
- It switches the theme to 'material' for crisper print CSS.
- It pre-renders Mermaid fences to SVG so they render in the PDF.
- It works on a temporary copy of the documentation to avoid side-effects.

Libraries to install (via requirements.txt): pyyaml, mkdocs, mkdocs-to-pdf, etc.
Unit tests: ToDo in a future iteration.
"""

from __future__ import annotations
import argparse
import os  # Required for os.path.relpath
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any, List
import yaml
# Explicit import needed for yaml.full_load to resolve custom tags from mkdocs.yml
import pymdownx.superfences

# Constant for the Python tag used by pymdownx.superfences.
FENCE_CODE_FORMAT_TAG = '!!python/name:pymdownx.superfences.fence_code_format'


def load_yaml(path: Path) -> Dict[str, Any]:
    """
    Loads a YAML file using yaml.full_load to correctly parse Python objects.

    :param path: Path to the YAML file (e.g., mkdocs.yml).
    :returns: The loaded configuration as a dictionary.
    """
    with path.open("r", encoding="utf-8") as file_handle:
        # Use full_load to properly parse !!python/name tags.
        return yaml.full_load(file_handle) or {}


def dump_yaml(data: Dict[str, Any], path: Path) -> None:
    """
    Dumps a dictionary to a YAML file using yaml.safe_dump.

    :param data: The configuration dictionary to save.
    :param path: Path where the YAML file should be written.
    """
    with path.open("w", encoding="utf-8") as file_handle:
        yaml.safe_dump(data, file_handle, sort_keys=False, allow_unicode=True)


def restore_pymdownx_tags(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Restores the Python function object loaded by yaml.full_load in the
    'pymdownx.superfences' custom fences back to its YAML tag string.

    This is necessary because yaml.safe_dump (used for writing the temporary
    config) cannot serialize Python function objects.

    :param config: The loaded MkDocs configuration dictionary.
    :returns: A new configuration dictionary with the custom fence tags restored
              (Returns a modified copy instead of in-place change).
    """
    # Clone the config to prevent side effects on the original object
    new_config = config.copy()

    markdown_extensions = new_config.get("markdown_extensions", [])
    if not isinstance(markdown_extensions, list):
        return new_config

    # Deep copy the list items containing nested dictionaries
    new_markdown_extensions: List[Any] = []

    for item in markdown_extensions:
        # Clone dictionary list item to ensure no mutation of original nested objects
        cloned_item = item.copy() if isinstance(item, dict) else item

        if isinstance(cloned_item, dict) and 'pymdownx.superfences' in cloned_item:
            sf_config = cloned_item['pymdownx.superfences']
            custom_fences = sf_config.get('custom_fences', [])

            # Create a new list for custom_fences to safely replace the list.
            new_custom_fences = []

            for fence in custom_fences:
                # Use .copy() on nested dict before potential modification.
                fence_copy = fence.copy() if isinstance(fence, dict) else fence

                # Check for object identity.
                if isinstance(fence_copy, dict) and 'format' in fence_copy and \
                   fence_copy['format'] is pymdownx.superfences.fence_code_format:

                    # Replace the function object with the constant string.
                    fence_copy['format'] = FENCE_CODE_FORMAT_TAG

                new_custom_fences.append(fence_copy)

            sf_config['custom_fences'] = new_custom_fences

        new_markdown_extensions.append(cloned_item)

    new_config["markdown_extensions"] = new_markdown_extensions
    return new_config


def ensure_to_pdf_plugin(config: Dict[str, Any]) -> None:
    """
    Ensures the 'to-pdf' plugin is present and configured for a single combined PDF.

    Modifies the configuration dictionary *in place*.
    :param config: The configuration dictionary.
    """
    plugins = list(config.get("plugins", []))
    idx = None
    for i, item in enumerate(plugins):
        if isinstance(item, str) and item.strip() == "to-pdf":
            plugins[i] = {"to-pdf": {}}
            idx = i
            break
        if isinstance(item, dict) and "to-pdf" in item:
            idx = i
            break
    if idx is None:
        plugins.append({"to-pdf": {}})
        idx = len(plugins) - 1

    block = plugins[idx]["to-pdf"]
    # sensible defaults
    block.setdefault("enabled_if_env", "ENABLE_PDF_EXPORT")
    block.setdefault("toc_title", "Table of Contents")
    block.setdefault("toc_level", 3)
    # write one combined PDF here:
    block.setdefault("output_path", "pdf/document.pdf")

    config["plugins"] = plugins


def ensure_markdown_extensions(config: Dict[str, Any]) -> None:
    """
    Ensures the 'toc' markdown extension is present for page outlines.

    Modifies the configuration dictionary *in place*.
    :param config: The configuration dictionary.
    """
    me = list(config.get("markdown_extensions", []))
    has_toc = any((m == "toc") or (isinstance(m, dict) and "toc" in m) for m in me)
    if not has_toc:
        me.append({"toc": {"permalink": True}})
    config["markdown_extensions"] = me


def switch_theme_to_material(config: Dict[str, Any]) -> None:
    """
    Overrides the theme to 'material' just for the PDF build (crisper print CSS).

    Modifies the configuration dictionary *in place*.
    :param config: The configuration dictionary.
    """
    config["theme"] = {"name": "material", "palette": [{"scheme": "default"}]}


def copy_docs_tree(src_docs: Path, dst_docs: Path) -> None:
    """
    Copies the documentation directory tree from source to destination.

    :param src_docs: Path to the source 'docs' directory.
    :param dst_docs: Path to the temporary destination 'docs' directory.
    """
    if dst_docs.exists():
        shutil.rmtree(dst_docs)
    shutil.copytree(src_docs, dst_docs)


def create_ephemeral_section_indexes(work_docs: Path) -> None:
    """
    Creates temporary 'index.md' files in directories lacking them.

    This ensures that section entries in the documentation navigation have
    some content, which is useful for PDF generation and TOC structure.
    These files exist only in the temporary copy used for the PDF build.

    :param work_docs: Path to the temporary working 'docs' directory.
    """
    for directory in sorted(work_docs.rglob("*")):
        if not directory.is_dir():
            continue
        # skip special folders like assets
        if directory.name.startswith("."):
            continue
        md_files = list(directory.glob("*.md"))
        if not md_files:
            continue
        index_md = directory / "index.md"
        if index_md.exists():
            continue
        # Derive a nice title from the folder name
        title = directory.name.replace("-", " ").replace("_", " ").title()
        index_md.write_text(f"# {title}\n\n", encoding="utf-8")


def preprocess_mermaid(work_docs: Path, assets_dir: Path) -> None:
    """
    Renders ```mermaid fences to SVG via mermaid-cli (mmdc or npx fallback)
    and replaces them with image links so WeasyPrint sees them in the PDF.

    :param work_docs: Path to the temporary working 'docs' directory.
    :param assets_dir: Path to the assets directory for saving rendered SVGs.
    """
    # Inline imports to keep the main imports clean
    import re
    import tempfile as _tmp
    import shutil

    assets_dir.mkdir(parents=True, exist_ok=True)
    mmdc = shutil.which("mmdc")
    use_npx = mmdc is None
    fence_re = re.compile(r"```mermaid\s*\n(.*?)\n```", re.DOTALL)

    def render_svg(code: str, svg_path: Path) -> None:
        """Helper to call mmdc (Mermaid CLI) for SVG rendering."""
        with _tmp.NamedTemporaryFile("w", delete=False, suffix=".mmd") as temp_file:
            temp_file.write(code)
            mmd_in = temp_file.name

        # Use a pinned version with npx if mmdc executable is not found
        cmd = (
            ["npx", "@mermaid-js/mermaid-cli@10.4.0", "-i", mmd_in, "-o", str(svg_path)]
            if use_npx else
            [mmdc, "-i", mmd_in, "-o", str(svg_path)]
        )
        # Suppress stdout/stderr if possible
        subprocess.run(cmd, check=True, capture_output=True)

    for markdown_file in work_docs.rglob("*.md"):
        text = markdown_file.read_text(encoding="utf-8")
        changed = False

        def substitute_mermaid(match):
            nonlocal changed
            code = match.group(1).strip()
            # Create a safe, hashed filename for cache
            safe_name = markdown_file.stem + "_" + str(abs(hash(code)))[:8] + ".svg"
            svg_path = assets_dir / safe_name

            if not svg_path.exists():
                try:
                    render_svg(code, svg_path)
                except Exception:
                    # Fallback on render error with a placeholder SVG
                    svg_path.write_text(
                        '<svg xmlns="http://www.w3.org/2000/svg" width="640" height="120">'
                        '<rect width="100%" height="100%" fill="#f7f7f7" />'
                        '<text x="12" y="32" font-family="sans-serif" font-size="18" fill="#d00">'
                        'Mermaid render error</text>'
                        '</svg>',
                        encoding="utf-8",
                    )
            changed = True
            
            # FIX: Calculate path relative to the current Markdown file's directory (md.parent).
            # This ensures WeasyPrint can resolve the path for nested documents.
            relative_path = os.path.relpath(svg_path, markdown_file.parent)
            
            return f'![diagram]({Path(relative_path).as_posix()})'

        new_text = fence_re.sub(substitute_mermaid, text)
        if changed:
            markdown_file.write_text(new_text, encoding="utf-8")


def main() -> int:
    """
    Main entry point for the PDF build script.

    Parses arguments, loads the source configuration, prepares a temporary
    documentation copy, mutates the configuration for the PDF build,
    runs mkdocs, and copies the resulting PDF to the final output directory.

    :returns: Exit code (0 for success, non-zero for error).
    """
    parser = argparse.ArgumentParser(description="Build a single PDF via mkdocs-to-pdf (no serve).")
    parser.add_argument("--src", default="mkdocs.yml", help="Path to source mkdocs.yml")
    parser.add_argument("--outdir", default="dist/pdf", help="Destination directory for the generated PDF")
    parser.add_argument("--keep-site", action="store_true", help="Keep 'site/' after build")
    parser.add_argument("--no-theme-switch", action="store_true", help="Do not override theme to Material for PDF")
    args = parser.parse_args()

    repo_root = Path.cwd()
    src_cfg_path = repo_root / args.src
    if not src_cfg_path.exists():
        print(f"ERROR: {src_cfg_path} not found", file=sys.stderr)
        return 2

    # Step 1: Load and Fix Configuration Tags
    cfg = load_yaml(src_cfg_path)
    # restore_pymdownx_tags reverts function objects to strings and returns a copy,
    # which becomes our mutable config for the PDF build.
    pdf_cfg = restore_pymdownx_tags(cfg)
    
    # Comment: 'restore_pymdownx_tags' must be called here to fix the raw configuration
    # loaded from disk before subsequent processing.

    # Step 2: Validate docs directory
    docs_dir_name = pdf_cfg.get("docs_dir", "docs")
    src_docs = repo_root / docs_dir_name
    if not src_docs.exists():
        print(f"ERROR: docs directory '{docs_dir_name}' not found", file=sys.stderr)
        return 3

    # Step 3: Prepare temporary docs workspace
    tmp_root = Path(tempfile.mkdtemp(prefix=".mkdocs-to-pdf-"))
    work_docs = tmp_root / "docs"
    assets_dir = work_docs / "assets" / "mermaid"
    copy_docs_tree(src_docs, work_docs)

    create_ephemeral_section_indexes(work_docs)

    # Step 4: Pre-render Mermaid diagrams
    try:
        preprocess_mermaid(work_docs, assets_dir)
    except FileNotFoundError as error:
        print(f"WARNING: Mermaid CLI not found (mmdc/npx). Mermaid diagrams will NOT render in PDFs. ({error})")

    # Step 5: Mutate configuration for PDF run (in-place modifications on pdf_cfg copy)
    ensure_to_pdf_plugin(pdf_cfg)
    ensure_markdown_extensions(pdf_cfg)
    if not args.no_theme_switch:
        switch_theme_to_material(pdf_cfg)

    # Set docs and site paths for the temp build
    pdf_cfg["docs_dir"] = str(work_docs)
    # ensure site output lands in the repo root, not under the temp dir
    pdf_cfg["site_dir"] = str(repo_root / "site")

    # Step 6: Write generated config
    tmp_cfg_path = tmp_root / "mkdocs-to-pdf.generated.yml"
    dump_yaml(pdf_cfg, tmp_cfg_path)

    # Step 7: Build (enable plugin via env)
    env = os.environ.copy()
    env["ENABLE_PDF_EXPORT"] = "1"

    print("▶ Building PDF with mkdocs-to-pdf.generated.yml …")
    subprocess.run(["mkdocs", "build", "--config-file", str(tmp_cfg_path), "--clean"], check=True, env=env)

    # Step 8: Collect result
    produced = repo_root / "site" / "pdf"
    pdfs = list(produced.rglob("*.pdf"))
    if not pdfs:
        print("ERROR: No PDF produced under site/pdf/. Did the 'to-pdf' plugin run?", file=sys.stderr)
        return 4

    outdir = repo_root / args.outdir
    outdir.mkdir(parents=True, exist_ok=True)
    for pdf in pdfs:
        shutil.copy2(pdf, outdir / pdf.name)
    print(f"✓ Copied {len(pdfs)} PDF(s) → {outdir}")

    # Step 9: Cleanup
    if not args.keep_site and (repo_root / "site").exists():
        shutil.rmtree(repo_root / "site")
    shutil.rmtree(tmp_root, ignore_errors=True)
    print("✅ Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())