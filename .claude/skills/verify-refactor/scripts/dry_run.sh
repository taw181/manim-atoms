#!/bin/bash
# Run every scene's construct without writing any frames: catches whatever
# only fails when the code runs (a name used but not imported, a helper
# called with the wrong arguments). Four at a time, each in its own media
# dir so their TeX caches can't trip over each other.
#   dry_run.sh                 # every scene
#   dry_run.sh 'gradiometer'   # scenes whose path or name matches
# Prints FAIL lines with the log to read; exits 1 if any failed.
ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
LOGS=$(mktemp -d)
cd "$ROOT"
run() {
  md=$(mktemp -d)
  timeout 900 uv run manim --dry_run --media_dir "$md" "$1" "$2" > "$3/$2.log" 2>&1 \
    || echo "FAIL $2 ($3/$2.log)"
  rm -rf "$md"
}
export -f run
OUT=$("$(dirname "$0")/scenes.sh" "$1" | xargs -P 4 -n 2 bash -c 'run "$0" "$1" '"$LOGS")
echo "$OUT" | grep FAIL
echo "dry run: $(ls "$LOGS" | wc -l) scenes, $(echo "$OUT" | grep -c FAIL) failed, logs in $LOGS"
! echo "$OUT" | grep -q FAIL
