#!/usr/bin/env python3
"""
Build a single PDF from an MkDocs project (no serve) using mkdocs-to-pdf.

- Forces Material theme only for the PDF run (your live site can stay Cerulean).
- Adds an automatic PDF TOC via the plugin.
- Pre-renders Mermaid fences to SVG so they render in the PDF.
- Works on a temporary copy of your docs; no in-place edits.
"""

from __future__ import annotations
import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any
import yaml
# FIX 1: Explicitly import the module needed by the YAML constructor
import pymdownx.superfences 


def load_yaml(path: Path) -> Dict[str, Any]:
    # FIX 1: Using yaml.full_load instead of safe_load to properly parse !!python/name tags
    with path.open("r", encoding="utf-8") as f:
        return yaml.full_load(f) or {}


def dump_yaml(data: Dict[str, Any], path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)


# FIX 2: New function to revert the python object to a string before dumping
def restore_pymdownx_tags(config: Dict[str, Any]) -> None:
    """Restores the Python object in the markdown_extensions list back to the YAML tag string
    so that yaml.safe_dump can write it without error.
    """
    me = list(config.get("markdown_extensions", []))
    
    for i, item in enumerate(me):
        if isinstance(item, dict) and 'pymdownx.superfences' in item:
            sf_config = item['pymdownx.superfences']
            custom_fences = sf_config.get('custom_fences', [])
            
            for fence in custom_fences:
                # Check if the 'format' value is the function object loaded by full_load
                if 'format' in fence and fence['format'] is pymdownx.superfences.fence_code_format:
                    # Replace the function object with the original YAML tag string
                    fence['format'] = '!!python/name:pymdownx.superfences.fence_code_format'


def ensure_to_pdf_plugin(config: Dict[str, Any]) -> None:
    """Ensure mkdocs-to-pdf is present and configured for a single combined PDF."""
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
    """Make sure 'toc' is present for page outlines (harmless for PDF)."""
    me = list(config.get("markdown_extensions", []))
    has_toc = any((m == "toc") or (isinstance(m, dict) and "toc" in m) for m in me)
    if not has_toc:
        me.append({"toc": {"permalink": True}})
    config["markdown_extensions"] = me


def switch_theme_to_material(config: Dict[str, Any]) -> None:
    """Use Material just for the PDF build (crisper print CSS)."""
    config["theme"] = {"name": "material", "palette": [{"scheme": "default"}]}


def copy_docs_tree(src_docs: Path, dst_docs: Path) -> None:
    if dst_docs.exists():
        shutil.rmtree(dst_docs)
    shutil.copytree(src_docs, dst_docs)

def create_ephemeral_section_indexes(work_docs: Path) -> None:
    """
    For each directory under docs/ that contains Markdown files but no index.md,
    create a temporary index.md with a single heading so the PDF has content
    for section entries. These files exist only in the temp copy used for PDF.
    """
    for d in sorted(work_docs.rglob("*")):
        if not d.is_dir():
            continue
        # skip special folders like assets
        if d.name.startswith("."):
            continue
        md_files = list(d.glob("*.md"))
        if not md_files:
            continue
        index_md = d / "index.md"
        if index_md.exists():
            continue
        # Derive a nice title from the folder name
        title = d.name.replace("-", " ").replace("_", " ").title()
        index_md.write_text(f"# {title}\n\n", encoding="utf-8")


def preprocess_mermaid(work_docs: Path, assets_dir: Path) -> None:
    """
    Render ```mermaid fences to SVG via mermaid-cli (mmdc or npx fallback)
    and replace them with image links so WeasyPrint sees them in the PDF.
    """
    import re, html, tempfile as _tmp, subprocess, shutil

    assets_dir.mkdir(parents=True, exist_ok=True)
    mmdc = shutil.which("mmdc")
    use_npx = mmdc is None
    fence_re = re.compile(r"```mermaid\s*\n(.*?)\n```", re.DOTALL)

    def render_svg(code: str, svg_path: Path) -> None:
        with _tmp.NamedTemporaryFile("w", delete=False, suffix=".mmd") as tf:
            tf.write(code)
            mmd_in = tf.name
        cmd = (
            ["npx", "@mermaid-js/mermaid-cli@10.4.0", "-i", mmd_in, "-o", str(svg_path)]
            if use_npx else
            [mmdc, "-i", mmd_in, "-o", str(svg_path)]
        )
        subprocess.run(cmd, check=True)

    for md in work_docs.rglob("*.md"):
        text = md.read_text(encoding="utf-8")
        changed = False

        def _sub(match):
            nonlocal changed
            code = match.group(1).strip()
            safe_name = md.stem + "_" + str(abs(hash(code)))[:8] + ".svg"
            svg_path = assets_dir / safe_name
            if not svg_path.exists():
                try:
                    render_svg(code, svg_path)
                except Exception as e:
                    # (Optional) write a small placeholder SVG rather than fail hard
                    svg_path.write_text(
                        '<svg xmlns="http://www.w3.org/2000/svg" width="640" height="120">'
                        '<rect width="100%" height="100%" fill="#f7f7f7" />'
                        '<text x="12" y="32" font-family="sans-serif" font-size="18" fill="#d00">'
                        'Mermaid render error</text>'
                        '</svg>',
                        encoding="utf-8",
                    )
            changed = True
            rel = svg_path.relative_to(work_docs)
            return f'![diagram]({rel.as_posix()})'

        new_text = fence_re.sub(_sub, text)
        if changed:
            md.write_text(new_text, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Build a single PDF via mkdocs-to-pdf (no serve).")
    ap.add_argument("--src", default="mkdocs.yml", help="Path to source mkdocs.yml")
    ap.add_argument("--outdir", default="dist/pdf", help="Destination directory for the generated PDF")
    ap.add_argument("--keep-site", action="store_true", help="Keep 'site/' after build")
    ap.add_argument("--no-theme-switch", action="store_true", help="Do not override theme to Material for PDF")
    args = ap.parse_args()

    repo_root = Path.cwd()
    src_cfg_path = repo_root / args.src
    if not src_cfg_path.exists():
        print(f"ERROR: {src_cfg_path} not found", file=sys.stderr)
        return 2

    cfg = load_yaml(src_cfg_path)
    pdf_cfg = dict(cfg)

    # docs dir
    docs_dir_name = pdf_cfg.get("docs_dir", "docs")
    src_docs = repo_root / docs_dir_name
    if not src_docs.exists():
        print(f"ERROR: docs directory '{docs_dir_name}' not found", file=sys.stderr)
        return 3

    # temp working copy of docs
    tmp_root = Path(tempfile.mkdtemp(prefix=".mkdocs-to-pdf-"))
    work_docs = tmp_root / "docs"
    assets_dir = work_docs / "assets" / "mermaid"
    copy_docs_tree(src_docs, work_docs)

    create_ephemeral_section_indexes(work_docs)

    # pre-render Mermaid
    try:
        preprocess_mermaid(work_docs, assets_dir)
    except FileNotFoundError as e:
        print(f"WARNING: Mermaid CLI not found (mmdc/npx). Mermaid diagrams will NOT render in PDFs. ({e})")

    # mutate config for PDF run
    ensure_to_pdf_plugin(pdf_cfg)
    ensure_markdown_extensions(pdf_cfg)
    if not args.no_theme_switch:
        switch_theme_to_material(pdf_cfg)
        
    # FIX 2: Restore the Python function object to its string representation for dumping
    restore_pymdownx_tags(pdf_cfg)

    pdf_cfg["docs_dir"] = str(work_docs)
    # ensure site output lands in the repo root, not under the temp dir
    pdf_cfg["site_dir"] = str(repo_root / "site")

    # write generated config
    tmp_cfg_path = tmp_root / "mkdocs-to-pdf.generated.yml"
    dump_yaml(pdf_cfg, tmp_cfg_path)

    # build (enable plugin via env)
    env = os.environ.copy()
    env["ENABLE_PDF_EXPORT"] = "1"

    print("▶ Building PDF with mkdocs-to-pdf.generated.yml …")
    subprocess.run(["mkdocs", "build", "--config-file", str(tmp_cfg_path), "--clean"], check=True, env=env)

    # collect result
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

    if not args.keep_site and (repo_root / "site").exists():
        shutil.rmtree(repo_root / "site")
    shutil.rmtree(tmp_root, ignore_errors=True)
    print("✅ Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())