#!/usr/bin/env python3
"""
split_book.py

Split a monolithic Markdown book into:
- One folder per top-level section (# ...)
- One file per chapter (## ...)
- Chapters stored under a 'chapters/' subdirectory
- All ### and deeper content remains inside its chapter
- Front matter preserved separately

Additionally:
- Auto-generates structural control directories inserted between
  Acknowledgements and Introduction:
  - 03_toc/00_section.md        -> ToC
  - 04_mainmatter/00_section.md -> \\mainmatter

MkDocs integration:
- Writes a root `.pages` file
- Writes per-section `.pages` files
- Reader-facing section numbering skips structural sections

Rules:
- ANY single-# heading starts a new section
- Headings inside fenced code blocks are ignored
- YAML front matter handled explicitly

PEP 8 compliant.
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
        msg = super().format(record)
        return f"{colour}{msg}{self.RESET}"


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
CHAPTER_PREFIX_RE = re.compile(r"^chapter\s+\d+\s*[:\-–]\s*", re.IGNORECASE)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def strip_heading_numbers(title: str) -> str:
    return NUMBER_PREFIX_RE.sub("", title).strip()


def strip_chapter_prefix(title: str) -> str:
    return CHAPTER_PREFIX_RE.sub("", title).strip()


def normalise_heading(line: str) -> str:
    match = HEADING_RE.match(line)
    if not match:
        return line
    hashes, title = match.groups()
    return f"{hashes} {strip_heading_numbers(title)}\n"


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s-]+", "_", text)
    return text.lower().strip("_")


# ---------------------------------------------------------------------------
# MkDocs helpers
# ---------------------------------------------------------------------------


def write_root_pages(output_dir: Path) -> None:
    (output_dir / ".pages").write_text(
        'title: "Firmitas Framework"\n',
        encoding="utf-8",
    )
    log.info("Created root .pages file")


def write_section_pages(
    section_dir: Path,
    visible_index: Optional[int],
    title: str,
) -> None:
    pages_file = section_dir / ".pages"

    if visible_index is None:
        pages_file.write_text("hide: true\n", encoding="utf-8")
    else:
        pages_file.write_text(
            f'title: "Section {visible_index:02d} – {title}"\n',
            encoding="utf-8",
        )


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------


def split_book(input_file: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    write_root_pages(output_dir)

    in_front_matter = False
    front_matter_started = False
    in_code_block = False

    front_matter: List[str] = []

    section_index = 0
    visible_section_index = 0
    chapter_index = 0

    current_section_dir: Optional[Path] = None
    current_section_title: Optional[str] = None
    current_section_lines: List[str] = []

    current_chapter_slug: Optional[str] = None
    current_chapter_lines: List[str] = []

    inserted_controls = False
    last_section_title_lower: Optional[str] = None

    def flush_chapter() -> None:
        if not current_section_dir or not current_chapter_slug:
            return

        chapter_dir = current_section_dir / "chapters"
        chapter_dir.mkdir(exist_ok=True)

        path = chapter_dir / f"{chapter_index:02d}_{current_chapter_slug}.md"
        path.write_text("".join(current_chapter_lines), encoding="utf-8")

    def flush_section_intro() -> None:
        if not current_section_dir:
            return

        path = current_section_dir / "00_section.md"
        path.write_text("".join(current_section_lines), encoding="utf-8")

    def insert_toc_and_mainmatter() -> None:
        nonlocal section_index, inserted_controls

        if inserted_controls:
            return

        for name, content in (
            ("toc", "\\tableofcontents\n"),
            ("mainmatter", "\\mainmatter\n"),
        ):
            section_index += 1
            d = output_dir / f"{section_index:02d}_{name}"
            d.mkdir()
            (d / "00_section.md").write_text(content, encoding="utf-8")
            write_section_pages(d, None, "")
            log.info("Inserted %s", name)

        inserted_controls = True

    log.info("Reading input: %s", input_file)

    with input_file.open(encoding="utf-8") as fh:
        for line in fh:
            stripped = line.strip()

            if stripped.startswith("```"):
                in_code_block = not in_code_block
                if current_chapter_slug:
                    current_chapter_lines.append(line)
                elif current_section_dir:
                    current_section_lines.append(line)
                else:
                    front_matter.append(line)
                continue

            if stripped == "---":
                if not front_matter_started:
                    in_front_matter = True
                    front_matter_started = True
                elif in_front_matter:
                    in_front_matter = False
                front_matter.append(line)
                continue

            if in_front_matter:
                front_matter.append(line)
                continue

            match = None if in_code_block else HEADING_RE.match(line)

            if match:
                level, raw_title = match.groups()
                clean_title = strip_heading_numbers(raw_title)
                clean_lower = clean_title.lower()

                if level == "#":
                    flush_chapter()
                    flush_section_intro()

                    if (
                        not inserted_controls
                        and last_section_title_lower
                        in ("acknowledgements", "acknowledgments")
                    ):
                        insert_toc_and_mainmatter()

                    section_index += 1
                    chapter_index = 0

                    slug = f"{section_index:02d}_{slugify(clean_title)}"
                    current_section_dir = output_dir / slug
                    current_section_dir.mkdir()

                    current_section_title = clean_title
                    current_section_lines = [f"# {clean_title}\n"]

                    current_chapter_slug = None
                    current_chapter_lines = []

                    if clean_lower not in ("toc", "mainmatter"):
                        visible_section_index += 1
                        write_section_pages(
                            current_section_dir,
                            visible_section_index,
                            clean_title,
                        )
                    else:
                        write_section_pages(current_section_dir, None, "")

                    last_section_title_lower = clean_lower
                    log.info("New section: %s", clean_title)
                    continue

                if level == "##" and current_section_dir:
                    flush_chapter()
                    chapter_index += 1

                    chap_title = strip_chapter_prefix(clean_title)
                    current_chapter_slug = slugify(chap_title)
                    current_chapter_lines = [f"## {chap_title}\n"]

                    log.info("  Chapter %02d: %s", chapter_index, chap_title)
                    continue

            if current_chapter_slug:
                current_chapter_lines.append(normalise_heading(line))
            elif current_section_dir:
                current_section_lines.append(normalise_heading(line))
            else:
                front_matter.append(line)

    flush_chapter()
    flush_section_intro()

    if front_matter:
        (output_dir / "_front_matter.md").write_text(
            "".join(front_matter),
            encoding="utf-8",
        )

    (output_dir / "_front_control.md").write_text(
        "\\frontmatter\n",
        encoding="utf-8",
    )

    log.info("Split complete")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--out", type=Path, default=Path("split"))
    parser.add_argument("--verbose", action="store_true")
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
