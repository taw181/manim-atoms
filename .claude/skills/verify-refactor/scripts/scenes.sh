#!/bin/bash
# Every renderable scene as "path Scene", one per line, read from
# docs/reference.md (scripts/index.py writes a render command per scene).
# An optional extended regex keeps only the lines matching it:
#   scenes.sh 'squeezing|dipole'
ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
grep -o 'uv run manim -ql src/manim_atoms/[^ ]* [A-Za-z0-9_]*' "$ROOT/docs/reference.md" \
  | awk '{print $5, $6}' | grep -E "${1:-.}"
