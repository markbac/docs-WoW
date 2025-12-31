#!/usr/bin/env python3
"""
render_diagrams_kroki_tree.py

Render Kroki-supported diagram code blocks in Markdown files
and write transformed Markdown + images to a new output directory.

Features:
- Input: file or directory
- Output: new directory
- Each directory gets its own media/ subdirectory
- Diagram code blocks replaced with image links
- Source tree untouched
- Coloured logging
- Verbose mode for detailed tracing

Usage:
  render_diagrams_kroki_tree.py <input> <output> [--verbose]
"""

from pathlib import Path
import base64
import zlib
import re
import shutil
import urllib.request
import sys
from typing import Optional

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

KROKI_BASE = "https://kroki.io"
KROKI_FORMAT = "png"  # <-- PNG output

KROKI_ALIASES = {
    "mermaid": "mermaid",

    "plantuml": "plantuml",
    "puml": "plantuml",
    "uml": "plantuml",
    "c4plantuml": "c4plantuml",
    "c4": "c4plantuml",

    "graphviz": "graphviz",
    "dot": "graphviz",
    "gv": "graphviz",

    "blockdiag": "blockdiag",
    "seqdiag": "seqdiag",
    "actdiag": "actdiag",
    "nwdiag": "nwdiag",
    "packetdiag": "packetdiag",
    "rackdiag": "rackdiag",

    "erd": "erd",
    "nomnoml": "nomnoml",
    "ditaa": "ditaa",
    "svgbob": "svgbob",
    "vega": "vega",
    "vegalite": "vegalite",
    "bpmn": "bpmn",
    "bytefield": "bytefield",
    "wavedrom": "wavedrom",
    "pikchr": "pikchr",
    "excalidraw": "excalidraw",
}

FENCE_RE = re.compile(
    r"(?P<fence>```)\s*(?P<lang>[a-zA-Z0-9_-]+)\s*\n(?P<body>.*?)\n(?P=fence)",
    re.DOTALL,
)

# ---------------------------------------------------------------------------
# Simple coloured logging
# ---------------------------------------------------------------------------

class Log:
    RESET = "\033[0m"
    GREY = "\033[90m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    CYAN = "\033[36m"

    verbose = False

    @classmethod
    def info(cls, msg: str) -> None:
        print(f"{cls.GREEN}INFO{cls.RESET}  {msg}")

    @classmethod
    def debug(cls, msg: str) -> None:
        if cls.verbose:
            print(f"{cls.CYAN}DEBUG{cls.RESET} {msg}")

    @classmethod
    def warn(cls, msg: str) -> None:
        print(f"{cls.YELLOW}WARN{cls.RESET}  {msg}")

    @classmethod
    def error(cls, msg: str) -> None:
        print(f"{cls.RED}ERROR{cls.RESET} {msg}")

# ---------------------------------------------------------------------------
# Kroki helpers
# ---------------------------------------------------------------------------

def encode_diagram(text: str) -> str:
    compressed = zlib.compress(text.encode("utf-8"))
    return base64.urlsafe_b64encode(compressed).decode("ascii")


def fetch_image(diagram_type: str, code: str, out: Path) -> None:
    encoded = encode_diagram(code)
    url = f"{KROKI_BASE}/{diagram_type}/{KROKI_FORMAT}/{encoded}"
    Log.debug(f"Fetching {KROKI_FORMAT.upper()}: {diagram_type} → {out.name}")
    with urllib.request.urlopen(url, timeout=20) as r:
        out.write_bytes(r.read())

# ---------------------------------------------------------------------------
# Markdown processing
# ---------------------------------------------------------------------------

def process_markdown(
    src_md: Path,
    dst_md: Path,
    src_root: Path,
    dst_root: Path,
) -> None:
    Log.info(f"Processing Markdown: {src_md.relative_to(src_root)}")

    text = src_md.read_text(encoding="utf-8")
    counter = 0
    changed = False

    dst_dir = dst_md.parent
    media_dir = dst_dir / "media"
    media_dir.mkdir(exist_ok=True)

    def replace(match):
        nonlocal counter, changed

        raw_lang = match.group("lang").lower()
        if raw_lang not in KROKI_ALIASES:
            Log.debug(f"Ignoring code block lang='{raw_lang}'")
            return match.group(0)

        kroki_type = KROKI_ALIASES[raw_lang]
        code = match.group("body").strip()
        counter += 1

        rel = src_md.relative_to(src_root).with_suffix("")
        safe = str(rel).replace("/", "_").replace("\\", "_")
        img_name = f"{safe}_{counter:02d}.{KROKI_FORMAT}"
        img_path = media_dir / img_name

        Log.debug(
            f"Found diagram #{counter}: "
            f"lang='{raw_lang}' → kroki='{kroki_type}'"
        )

        if img_path.exists():
            Log.debug(f"Reusing existing image: {img_path}")
        else:
            Log.info(f"Rendering diagram → {img_path}")
            fetch_image(kroki_type, code, img_path)

        changed = True
        return f"![Diagram](media/{img_name})"

    new_text = FENCE_RE.sub(replace, text)

    dst_md.parent.mkdir(parents=True, exist_ok=True)
    dst_md.write_text(new_text if changed else text, encoding="utf-8")

    if counter == 0:
        Log.debug("No diagrams found")
    else:
        Log.info(f"Rendered {counter} diagram(s)")

# ---------------------------------------------------------------------------
# File copying
# ---------------------------------------------------------------------------

def copy_non_md(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    Log.debug(f"Copied asset: {src}")

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(src: Path, dst: Path, verbose: bool) -> None:
    Log.verbose = verbose

    if dst.exists():
        raise SystemExit(f"ERROR: Output directory already exists: {dst}")

    src = src.resolve()
    dst = dst.resolve()
    dst.mkdir(parents=True)

    Log.info(f"Source: {src}")
    Log.info(f"Output: {dst}")
    Log.debug("Verbose mode enabled")

    if src.is_file():
        if src.suffix.lower() != ".md":
            raise SystemExit("ERROR: Input file must be Markdown")
        process_markdown(src, dst / src.name, src.parent, dst)
        return

    for path in src.rglob("*"):
        rel = path.relative_to(src)
        out_path = dst / rel

        if path.is_dir():
            out_path.mkdir(exist_ok=True)
        elif path.suffix.lower() == ".md":
            process_markdown(path, out_path, src, dst)
        else:
            copy_non_md(path, out_path)

# ---------------------------------------------------------------------------

if __name__ == "__main__":
    args = sys.argv[1:]

    if len(args) not in (2, 3):
        print("Usage: render_diagrams_kroki_tree.py <input> <output> [--verbose]")
        sys.exit(1)

    verbose_flag = "--verbose" in args
    paths = [a for a in args if not a.startswith("-")]

    main(Path(paths[0]), Path(paths[1]), verbose_flag)
