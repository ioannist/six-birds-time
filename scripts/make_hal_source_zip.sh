#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PAPER_DIR="$ROOT_DIR/docs/paper"
BUILD_DIR="$PAPER_DIR/build"
STAGE_DIR="$BUILD_DIR/hal_source_staging"
ZIP_PATH="$BUILD_DIR/hal_source_upload.zip"

rm -rf "$STAGE_DIR"
mkdir -p "$STAGE_DIR/figures" "$STAGE_DIR/sections" "$STAGE_DIR/tables"

cp "$PAPER_DIR/to_notch_a_stone_with_six_birds.tex" "$STAGE_DIR/to_notch_a_stone_with_six_birds.tex"
cp "$PAPER_DIR/references.bib" "$STAGE_DIR/references.bib"

if [[ -f "$PAPER_DIR/to_notch_a_stone_with_six_birds.bbl" ]]; then
  cp "$PAPER_DIR/to_notch_a_stone_with_six_birds.bbl" "$STAGE_DIR/to_notch_a_stone_with_six_birds.bbl"
else
  echo "[make_hal_source_zip] ERROR: to_notch_a_stone_with_six_birds.bbl not found; run paper build first." >&2
  exit 2
fi

if [[ -d "$PAPER_DIR/sections" ]]; then
  cp "$PAPER_DIR/sections/"*.tex "$STAGE_DIR/sections/" 2>/dev/null || true
fi
if [[ -d "$PAPER_DIR/tables" ]]; then
  cp "$PAPER_DIR/tables/"*.tex "$STAGE_DIR/tables/" 2>/dev/null || true
fi
if [[ -d "$PAPER_DIR/figures" ]]; then
  cp "$PAPER_DIR/figures/"*.png "$STAGE_DIR/figures/" 2>/dev/null || true
  cp "$PAPER_DIR/figures/"*.jpg "$STAGE_DIR/figures/" 2>/dev/null || true
  cp "$PAPER_DIR/figures/"*.pdf "$STAGE_DIR/figures/" 2>/dev/null || true
fi

find "$STAGE_DIR" -name "*.aux" -delete
find "$STAGE_DIR" -name "*.log" -delete
find "$STAGE_DIR" -name "*.out" -delete
find "$STAGE_DIR" -name "*.toc" -delete

rm -f "$ZIP_PATH"
(
  cd "$STAGE_DIR"
  zip -r "$ZIP_PATH" . >/dev/null
)

echo "[make_hal_source_zip] Wrote $ZIP_PATH"
