#!/bin/bash
# Render each scene's last frame (-ql -s) to OUTDIR/<Scene>.png, four at a
# time, each in its own media dir. Run it once before a refactor and once
# after, then compare_frames.py BEFORE AFTER.
#   last_frames.sh OUTDIR [filter-regex]
ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
OUT=$(realpath -m "$1"); mkdir -p "$OUT"
cd "$ROOT"
render() {
  md=$(mktemp -d)
  if timeout 900 uv run manim -ql -s --disable_caching --media_dir "$md" "$1" "$2" > "$3/$2.log" 2>&1; then
    cp "$(find "$md/images" -name "$2*.png" | head -1)" "$3/$2.png" 2>/dev/null || echo "NOPNG $2"
  else
    echo "FAIL $2 ($3/$2.log)"
  fi
  rm -rf "$md"
}
export -f render
"$(dirname "$0")/scenes.sh" "$2" | xargs -P 4 -n 2 bash -c 'render "$0" "$1" '"$OUT"
echo "rendered $(ls "$OUT"/*.png 2>/dev/null | wc -l) last frames into $OUT"
