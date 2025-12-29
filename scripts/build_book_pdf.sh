#!/usr/bin/env bash
set -euo pipefail

BOOK_DIR="book"
DIST_DIR="dist"
TEMPLATE="templates/book.tex"
OUTPUT_PDF="keystone.pdf"

# -----------------------------
# Traceability
# -----------------------------
GIT_HASH="$(git rev-parse --short HEAD 2>/dev/null || echo N/A)"
GIT_DIRTY="$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
BUILD_DATE="$(date -u '+%Y-%m-%d %H:%M:%S UTC')"

DIRTY_STATUS="Clean"
if [ "$GIT_DIRTY" != "0" ]; then
  DIRTY_STATUS="Dirty"
fi

mkdir -p "$DIST_DIR"

echo "📘 Building Keystone PDF"
echo "Commit: $GIT_HASH ($DIRTY_STATUS)"
echo "Built:  $BUILD_DATE"
echo

pandoc \
  $(find "$BOOK_DIR" -name "*.md" | sort) \
  --from markdown+yaml_metadata_block \
  --template="$TEMPLATE" \
  --metadata-file="$BOOK_DIR/book.yaml" \
  --metadata build_date="$BUILD_DATE" \
  --metadata git_commit="$GIT_HASH" \
  --metadata git_dirty="$DIRTY_STATUS" \
  --toc \
  --number-sections \
  --top-level-division=part \
  --pdf-engine=xelatex \
  -o "$DIST_DIR/$OUTPUT_PDF"

echo "✅ PDF written to $DIST_DIR/$OUTPUT_PDF"
