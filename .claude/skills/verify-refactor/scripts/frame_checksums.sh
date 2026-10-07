#!/bin/bash
# Render each scene at -ql, four at a time, keeping OUTDIR/<Scene>.mp4 and a
# checksum of every decoded frame in OUTDIR/<Scene>.md5 (a few KB, where the
# frames themselves would be hundreds of MB). Compare two runs with
# compare_checksums.py.
#   frame_checksums.sh OUTDIR [filter-regex] [code-root]
# With code-root (a checkout of other code, e.g. `git worktree add DIR main`),
# that code is rendered instead, through PYTHONPATH ahead of the editable
# install: the old code in this repo's environment.
ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
OUT=$(realpath -m "$1"); mkdir -p "$OUT"
CODE=$(realpath "${3:-$ROOT}")
cd "$ROOT"
one() {
  md=$(mktemp -d)
  if PYTHONPATH="$4/src" timeout 1500 uv run manim -ql --disable_caching --media_dir "$md" "$4/$1" "$2" > "$3/$2.log" 2>&1; then
    f=$(find "$md/videos" -name "$2.mp4" -not -path "*partial*" | head -1)
    cp "$f" "$3/$2.mp4"
    ffmpeg -v error -i "$f" -f framemd5 - | grep -v "^#" | awk -F, '{print $NF}' > "$3/$2.md5"
  else
    echo "FAIL $2 ($3/$2.log)"
  fi
  rm -rf "$md"
}
export -f one
"$(dirname "$0")/scenes.sh" "$2" | xargs -P 4 -n 2 bash -c 'one "$0" "$1" '"$OUT $CODE"
echo "rendered $(ls "$OUT"/*.md5 2>/dev/null | wc -l) scenes into $OUT"
