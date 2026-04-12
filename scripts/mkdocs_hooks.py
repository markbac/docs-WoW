# File: scripts/mkdocs_hooks.py
"""
MkDocs Configuration Hook for Build Traceability

Purpose
-------
Runs during every MkDocs build (serve or build) to inject runtime metadata into
`config.extra.build_metadata`, so templates/pages can render traceability data.

What it injects
---------------
- generated_on (UTC, human readable)
- git_hash (short)
- is_dirty (bool)
- dirty_status (string)
- mkdocs_version (string)
- license_content (full text of LICENSE from repo root, if present)
- repo_url (from `git remote get-url origin`, if available)

Repo root resolution order
--------------------------
1) Environment variable REPO_ROOT (set by the PDF build script)
2) `git rev-parse --show-toplevel`
3) Parent of `config.docs_dir` (fallback)

Dependencies
------------
- mkdocs
- python-dateutil (only if you add parsing; not required here)
- git in PATH (for hash/status/repo URL; if missing we degrade gracefully)
"""

from __future__ import annotations

import os
import shlex
import subprocess
from datetime import datetime, UTC
from typing import Optional
import sys

from mkdocs.config.base import Config
from mkdocs.utils import log
import importlib.metadata
# mkdocs_hooks.py
from pathlib import Path
from bs4 import BeautifulSoup


# Directory for per-page debug dumps
DEBUG_DUMP_DIR = Path("pdf_debug_pages")
DEBUG_DUMP_DIR.mkdir(exist_ok=True)

PAGE_COUNTER = 0


def on_post_page(output_content, page, config):
    """
    Hook: called after each page is rendered to HTML (before mkdocs-to-pdf/with-pdf combines them).
    Use it to log which page is processed and optionally save its HTML.
    """
    global PAGE_COUNTER
    PAGE_COUNTER += 1

    relpath = page.file.src_path
    html_len = len(output_content)
    print(f"[pdf-debug] Page {PAGE_COUNTER:03d}: {relpath} ({html_len/1024:.1f} KB)", file=sys.stderr)

    # Save each page HTML for inspection (optional but useful)
    dump_path = DEBUG_DUMP_DIR / f"{PAGE_COUNTER:03d}_{Path(relpath).stem}.html"
    dump_path.write_text(output_content, encoding="utf-8")

    # Optionally strip Material UI elements if you want to see what’s left
    soup = BeautifulSoup(output_content, "html.parser")
    for sel in [".md-sidebar", ".md-header", ".md-tabs", "nav.md-nav--secondary"]:
        for el in soup.select(sel):
            el.decompose()

    cleaned_html = str(soup)
    cleaned_path = DEBUG_DUMP_DIR / f"{PAGE_COUNTER:03d}_{Path(relpath).stem}_clean.html"
    cleaned_path.write_text(cleaned_html, encoding="utf-8")

    # Return unmodified HTML so the normal PDF plugin still works
    return output_content


def old_on_post_page(output_content, page, config):
    """
    Hook: Runs after each page is rendered but before mkdocs-to-pdf plugin executes.

    Purpose:
        Clean MkDocs Material dynamic elements (sidebars, JS, ToCs, wrappers)
        from the in-memory HTML before WeasyPrint sees them.
        This ensures the entire article content is visible to the renderer.

    Debug:
        - Logs filename and approximate original vs. cleaned HTML length
        - Lists which selectors actually matched and how many elements removed
        - Prints one summary per page
    """
    try:
        relpath = page.file.src_path
        soup = BeautifulSoup(output_content, "html.parser")
        before_len = len(output_content)

        # Elements to strip completely (sidebars, JS, headers, search, etc.)
        selectors = [
            ".md-sidebar",
            ".md-sidebar--secondary",
            "nav.md-nav--secondary",
            "header.md-header",
            "div.md-search",
            "div.md-tabs",
            "div.md-footer",
            "label.md-overlay",
            "input.md-toggle",
            '[data-md-component="announce"]',
            '[data-md-component="palette"]',
        ]
        removed_counts = {}
        total_removed = 0

        for sel in selectors:
            els = soup.select(sel)
            if els:
                removed_counts[sel] = len(els)
                for el in els:
                    el.decompose()
                    total_removed += 1

        # --- NEW: flatten Material layout wrappers ---
        # These wrappers use flex/contain/sticky styles that break WeasyPrint’s flow.
        wrappers = soup.select("div.md-main, div.md-content, div.md-content__inner, div.md-main__inner")
        for w in wrappers:
            # unwrap keeps inner HTML, discards the wrapper tag
            w.unwrap()

        # Also remove Material-specific flex attributes that confuse layout
        for el in soup.find_all(True):
            for attr in ["data-md-component", "class", "style"]:
                if el.has_attr(attr) and "md-" in str(el.get(attr)):
                    # Clean up Material-only attributes/styles
                    if attr == "class":
                        el["class"] = [c for c in el.get("class", []) if not c.startswith("md-")]
                        if not el["class"]:
                            del el["class"]
                    elif attr == "style":
                        del el["style"]
                    elif attr == "data-md-component":
                        del el["data-md-component"]

        # Strip all <script> tags
        scripts = soup.find_all("script")
        if scripts:
            removed_counts["<script>"] = len(scripts)
            for el in scripts:
                el.decompose()
                total_removed += len(scripts)

        after_len = len(str(soup))
        if total_removed:
            print(
                f"[hook] Cleaned '{relpath}' "
                f"({before_len/1024:.1f} KB→{after_len/1024:.1f} KB) "
                f"removed {total_removed} elements: "
                f"{', '.join(f'{k}:{v}' for k,v in removed_counts.items())}",
                file=sys.stderr,
            )
        else:
            print(f"[hook] No Material UI elements removed from '{relpath}'", file=sys.stderr)

        return str(soup)

    except Exception as e:
        print(f"[hook:ERROR] Failed cleaning {page.file.src_path}: {e}", file=sys.stderr)
        return output_content



def get_tool_versions() -> dict:
    """
    Fetch the MkDocs version using importlib.metadata.

    Returns:
        dict: {'mkdocs_version': '<version or fallback>'}
    """
    versions = {}
    try:
        versions["mkdocs_version"] = importlib.metadata.version("mkdocs")
    except importlib.metadata.PackageNotFoundError:
        versions["mkdocs_version"] = "MkDocs Not Found"
    return versions


def _run_git(cmd: str, cwd: str) -> Optional[str]:
    """
    Run a git command and return stripped stdout, or None on failure.
    """
    try:
        result = subprocess.run(
            shlex.split(cmd),
            capture_output=True,
            text=True,
            check=True,
            cwd=cwd,
        )
        out = (result.stdout or "").strip()
        return out if out else None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def get_git_metadata(cwd: str) -> dict:
    """
    Fetch git hash and dirty status for the repo at `cwd` (or nearest git root).

    Returns:
        dict: {
          'git_hash': '<short hash or Unknown>',
          'is_dirty': <bool>,
          'dirty_status': '<string>'
        }
    """
    metadata = {
        "git_hash": "Unknown",
        "is_dirty": False,
        "dirty_status": "N/A",
    }

    # Get short hash
    short_hash = _run_git("git rev-parse --short HEAD", cwd)
    if short_hash:
        metadata["git_hash"] = short_hash
    else:
        log.warning("Git not found or failed to fetch commit hash.")

    # Dirty status
    status = _run_git("git status --porcelain", cwd)
    if status is None:
        metadata["is_dirty"] = True
        metadata["dirty_status"] = "Git status check failed."
    elif status.strip():
        metadata["is_dirty"] = True
        metadata["dirty_status"] = "Local uncommitted changes exist."
    else:
        metadata["is_dirty"] = False
        metadata["dirty_status"] = "Clean"

    return metadata


def _git_toplevel(cwd: str) -> Optional[str]:
    """
    Return the git toplevel directory or None.
    """
    return _run_git("git rev-parse --show-toplevel", cwd)


def _git_repo_url(cwd: str) -> str:
    """
    Return the repo URL for origin, or 'Unknown'.
    """
    url = _run_git("git remote get-url origin", cwd)
    return url or "Unknown"


def get_license_content(repo_root: str) -> str:
    """
    Read LICENSE from repo_root. Return a helpful message if missing/unreadable.
    """
    path = os.path.join(repo_root, "LICENSE")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except OSError as e:
            log.warning(f"Could not read LICENSE file: {e}")
            return "LICENSE file found but could not be read."
    return "LICENSE file not found in repository root."


def _resolve_repo_root(docs_dir: str) -> str:
    """
    Decide the repository root path, preferring:
    1) REPO_ROOT env var
    2) git toplevel (from CWD)
    3) parent of docs_dir
    """
    env_root = os.environ.get("REPO_ROOT")
    if env_root:
        return os.path.abspath(env_root)

    git_root = _git_toplevel(os.getcwd())
    if git_root:
        return git_root

    # Fallback: parent of docs_dir
    return os.path.abspath(os.path.join(docs_dir, os.pardir))


def on_config(config: Config) -> Config:
    """
    MkDocs hook: enrich config.extra.build_metadata with build-time information.
    """
    # Determine repo root robustly
    docs_dir = config.docs_dir
    repo_root = _resolve_repo_root(docs_dir)

    # 1) Gather metadata
    git_metadata = get_git_metadata(repo_root)
    tool_versions = get_tool_versions()
    license_content = get_license_content(repo_root)
    repo_url = _git_repo_url(repo_root)
    build_date = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S %Z")

    injected = {
        "generated_on": build_date,
        "git_hash": git_metadata["git_hash"],
        "is_dirty": git_metadata["is_dirty"],
        "dirty_status": git_metadata["dirty_status"],
        "mkdocs_version": tool_versions["mkdocs_version"],
        "license_content": license_content,
        "repo_url": repo_url,
        "repo_root": repo_root,
    }

    # 2) Inject into config.extra.build_metadata
    if "extra" not in config or config["extra"] is None:
        config["extra"] = {}
    if "build_metadata" not in config["extra"] or config["extra"]["build_metadata"] is None:
        config["extra"]["build_metadata"] = {}

    config["extra"]["build_metadata"].update(injected)

    log.info(
        "Injected build metadata: "
        f"Git Hash={injected['git_hash']} | Dirty={injected['is_dirty']} | "
        f"Repo={injected['repo_url']} | Root={injected['repo_root']}"
    )
    return config
