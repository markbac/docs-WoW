#!/usr/bin/env python3
"""
split_book.py

Idempotently split a monolithic Markdown book into a structured
Pandoc-friendly directory layout.

Features:
- PART (#) -> directories with _part.md
- CHAPTER (##) -> one file per chapter
- Removes chapter / subsection numbering
- Extracts front matter and back matter
- Dry-run mode
- Safe to re-run

Usage:
    python split_book.py input.md book/ [--dry-run]
"""

from pathlib import Path
import argparse
import re
import shutil


SECTION_RE = re.compile(r"^#\s+(SECTION\s+.+)$", re.IGNORECASE)
CHAPTER_RE = re.compile(r"^##\s+(Chapter\s+\d+\s+–\s+)?(.+)$", re.IGNORECASE)
SUBSECTION_RE = re.compile(r"^(###)\s+\d+(\.\d+)*\s+(.*)$", re.IGNORECASE)

FRONT_MATTER_END_RE = re.compile(r"^#\s+SECTION\s+", re.IGNORECASE)
ACK_RE = re.compile(r"^#\s+Acknowledgements", re.IGNORECASE)


def slugify(text: str) -> str:
    return (
        text.lower()
        .replace("–", "")
        .replace("—", "")
        .replace(",", "")
        .replace(":", "")
        .replace("'", "")
        .replace(".", "")
        .replace("(", "")
        .replace(")", "")
        .strip()
        .replace(" ", "-")
    )


def write(path: Path, content: str, dry_run: bool) -> None:
    if dry_run:
        print(f"[DRY-RUN] write {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def clean_dir(path: Path, dry_run: bool) -> None:
    if not path.exists():
        return
    if dry_run:
        print(f"[DRY-RUN] clean {path}")
        return
    shutil.rmtree(path)


def main(input_md: Path, output_root: Path, dry_run: bool) -> None:
    lines = input_md.read_text(encoding="utf-8").splitlines()

    # Idempotence: clean generated output
    clean_dir(output_root, dry_run)
    output_root.mkdir(parents=True, exist_ok=True)

    front_matter = []
    back_matter = []
    in_front_matter = True
    in_back_matter = False

    current_part_dir = None
    current_chapter = []
    part_index = 0
    chapter_index = 0

    def flush_chapter():
        nonlocal chapter_index, current_chapter
        if not current_part_dir or not current_chapter:
            return

        chapter_index += 1
        title = current_chapter[0].replace("## ", "")
        filename = f"{chapter_index:02d}-{slugify(title)}.md"
        write(
            current_part_dir / filename,
            "\n".join(current_chapter),
            dry_run,
        )
        current_chapter = []

    for line in lines:
        # Detect acknowledgements / back matter
        if ACK_RE.match(line):
            flush_chapter()
            in_back_matter = True
            in_front_matter = False
            back_matter.append(line)
            continue

        if in_back_matter:
            back_matter.append(line)
            continue

        # Detect start of first section
        if in_front_matter and FRONT_MATTER_END_RE.match(line):
            in_front_matter = False

        if in_front_matter:
            front_matter.append(line)
            continue

        # PART
        section_match = SECTION_RE.match(line)
        if section_match:
            flush_chapter()
            part_index += 1
            chapter_index = 0

            part_title = section_match.group(1)
            part_slug = slugify(part_title)
            current_part_dir = output_root / f"part-{part_index:02d}-{part_slug}"

            write(
                current_part_dir / "_part.md",
                f"# {part_title}",
                dry_run,
            )
            continue

        # CHAPTER
        chapter_match = CHAPTER_RE.match(line)
        if chapter_match:
            flush_chapter()
            title = chapter_match.group(2)
            current_chapter = [f"## {title}"]
            continue

        # SUBSECTION
        subsection_match = SUBSECTION_RE.match(line)
        if subsection_match and current_chapter:
            hashes, _, title = subsection_match.groups()
            current_chapter.append(f"{hashes} {title}")
            continue

        # Body text
        if current_chapter:
            current_chapter.append(line)

    flush_chapter()

    # Write front matter
    if front_matter:
        write(
            output_root / "00-front-matter.md",
            "\n".join(front_matter),
            dry_run,
        )

    # Write back matter
    if back_matter:
        write(
            output_root / "98-acknowledgements.md",
            "\n".join(back_matter),
            dry_run,
        )
        write(
            output_root / "99-back-matter.md",
            "",
            dry_run,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    main(args.input, args.output, args.dry_run)
