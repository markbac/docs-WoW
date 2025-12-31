#!/usr/bin/env python3
"""
split_book.py

Split a monolithic Markdown book into:
- One folder per top-level section (# ...)
- One file per chapter (## ...)
- All ### and deeper content remains inside its chapter
- Front matter preserved separately

Additionally:
- Auto-generates structural control directories:
  - _front_control.md           -> \\frontmatter
  - TOC                         -> \\tableofcontents
  - main matter                 -> \\mainmatter

Rules:
- ANY single-# heading starts a new section
- Headings inside fenced code blocks are ignored
- Fenced code blocks are preserved verbatim
- YAML front matter handled explicitly
- Section and chapter ordering is explicit and stable

PEP 8 compliant.
Coloured logging.
Windows-safe filesystem output.
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
import unicodedata
from pathlib import Path
from typing import List, Optional


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------


class ColourFormatter(logging.Formatter):
    """ANSI-coloured log formatter."""

    COLOURS = {
        logging.DEBUG: "\033[36m",
        logging.INFO: "\033[32m",
        logging.WARNING: "\033[33m",
        logging.ERROR: "\033[31m",
        logging.CRITICAL: "\033[41m",
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        colour = self.COLOURS.get(record.levelno, "")
        message = super().format(record)
        return f"{colour}{message}{self.RESET}"


def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(ColourFormatter("%(levelname)s: %(message)s"))
    logging.basicConfig(level=level, handlers=[handler])


log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Regex helpers
# ---------------------------------------------------------------------------

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
NUMBER_PREFIX_RE = re.compile(r"^\d+(\.\d+)*\s+")
CHAPTER_PREFIX_RE = re.compile(
    r"^chapter\s+\d+\s*[:\-–]\s*",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Normalisation helpers
# ---------------------------------------------------------------------------


def strip_heading_numbers(title: str) -> str:
    """Remove numeric prefixes from headings."""
    return NUMBER_PREFIX_RE.sub("", title).strip()

def strip_chapter_prefix(title: str) -> str:
    """Remove 'Chapter X – ' style prefixes from chapter titles."""
    return CHAPTER_PREFIX_RE.sub("", title).strip()

def normalise_heading(line: str) -> str:
    """Strip numbering from any markdown heading."""
    match = HEADING_RE.match(line)
    if not match:
        return line

    hashes, title = match.groups()
    return f"{hashes} {strip_heading_numbers(title)}\n"


def slugify(text: str) -> str:
    """Convert heading text into a filesystem-safe slug."""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s-]+", "_", text)
    return text.lower().strip("_")


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------


def split_book(input_file: Path, output_dir: Path) -> None:
    in_front_matter = False
    front_matter_started = False
    in_code_block = False

    output_dir.mkdir(parents=True, exist_ok=True)

    front_matter: List[str] = []

    section_index = 0
    chapter_index = 0

    current_section_slug: Optional[str] = None
    current_section_lines: List[str] = []

    current_chapter_slug: Optional[str] = None
    current_chapter_lines: List[str] = []

    toc_written = False
    mainmatter_written = False

    def route_line(line: str) -> None:
        if current_chapter_slug:
            current_chapter_lines.append(line)
        elif current_section_slug:
            current_section_lines.append(line)
        else:
            front_matter.append(line)

    def flush_chapter() -> None:
        if not current_section_slug or not current_chapter_slug:
            return

        path = (
            output_dir
            / current_section_slug
            / f"{chapter_index:02d}_{current_chapter_slug}.md"
        )
        path.parent.mkdir(parents=True, exist_ok=True)

        log.debug("Writing chapter: %s", path)
        path.write_text("".join(current_chapter_lines), encoding="utf-8")

    def flush_section_intro() -> None:
        if not current_section_slug:
            return

        path = output_dir / current_section_slug / "00_section.md"
        path.parent.mkdir(parents=True, exist_ok=True)

        log.debug("Writing section intro: %s", path)
        path.write_text("".join(current_section_lines), encoding="utf-8")

    def write_toc_and_mainmatter() -> None:
        nonlocal section_index, toc_written, mainmatter_written

        if not toc_written:
            section_index += 1
            toc_dir = output_dir / f"{section_index:02d}_toc"
            toc_dir.mkdir(parents=True, exist_ok=True)
            (toc_dir / "00_section.md").write_text(
                "\\cleardoublepage\n"
                "\\pdfbookmark[0]{Contents}{toc}\n"
                "\\tableofcontents\n"
                "\\cleardoublepage\n",
                encoding="utf-8",
            )

            log.info("Writing TOC section: %s", toc_dir)
            toc_written = True

        if not mainmatter_written:
            section_index += 1
            mainmatter_dir = output_dir / f"{section_index:02d}_mainmatter"
            mainmatter_dir.mkdir(parents=True, exist_ok=True)
            (mainmatter_dir / "00_section.md").write_text(
                "\\mainmatter\n",
                encoding="utf-8",
            )
            log.info("Writing main matter section: %s", mainmatter_dir)
            mainmatter_written = True

    log.info("Reading input: %s", input_file)

    with input_file.open("r", encoding="utf-8") as fh:
        for line in fh:
            stripped = line.strip()

            # ------------------------------------------------------------
            # Fenced code blocks
            # ------------------------------------------------------------
            if stripped.startswith("```"):
                in_code_block = not in_code_block
                route_line(line)
                continue

            # ------------------------------------------------------------
            # YAML front matter
            # ------------------------------------------------------------
            if stripped == "---":
                if not front_matter_started:
                    in_front_matter = True
                    front_matter_started = True
                    front_matter.append(line)
                    continue
                if in_front_matter:
                    in_front_matter = False
                    front_matter.append(line)
                    continue

            if in_front_matter:
                front_matter.append(line)
                continue

            # ------------------------------------------------------------
            # Headings (ignored in code blocks)
            # ------------------------------------------------------------
            match = None if in_code_block else HEADING_RE.match(line)

            if match:
                level, raw_title = match.groups()
                clean_title = strip_heading_numbers(raw_title)
                
                if level == "##":
                    clean_title = strip_chapter_prefix(clean_title)

                # New section
                if level == "#":
                    flush_chapter()
                    flush_section_intro()

                    if clean_title.lower() == "introduction":
                        write_toc_and_mainmatter()

                    section_index += 1
                    chapter_index = 0

                    current_section_slug = (
                        f"{section_index:02d}_{slugify(clean_title)}"
                    )
                    current_section_lines = [f"# {clean_title}\n"]

                    current_chapter_slug = None
                    current_chapter_lines = []

                    log.info("New section: %s", clean_title)
                    continue

                # New chapter
                if level == "##" and current_section_slug:
                    flush_chapter()

                    chapter_index += 1
                    current_chapter_slug = slugify(clean_title)
                    current_chapter_lines = [f"## {clean_title}\n"]

                    log.info(
                        "  Chapter %02d: %s",
                        chapter_index,
                        clean_title,
                    )
                    continue

            # ------------------------------------------------------------
            # Content routing
            # ------------------------------------------------------------
            route_line(normalise_heading(line))

    # Final flush
    flush_chapter()
    flush_section_intro()

    # ------------------------------------------------------------------
    # Write preserved YAML front matter
    # ------------------------------------------------------------------
    if front_matter:
        path = output_dir / "_front_matter.md"
        log.info("Writing front matter: %s", path)
        path.write_text("".join(front_matter), encoding="utf-8")

    # ------------------------------------------------------------------
    # Structural control artefacts
    # ------------------------------------------------------------------

    front_control = output_dir / "_front_control.md"
    front_control.write_text("\\frontmatter\n", encoding="utf-8")
    log.info("Writing front matter control: %s", front_control)

    log.info("Split complete")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Split a Markdown book into ordered sections and chapters."
    )
    parser.add_argument("input", type=Path, help="Input markdown file")
    parser.add_argument(
        "--out", type=Path, default=Path("split"), help="Output directory"
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose logging"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    configure_logging(args.verbose)

    if not args.input.exists():
        log.error("Input file does not exist: %s", args.input)
        sys.exit(1)

    split_book(args.input, args.out)


if __name__ == "__main__":
    main()
