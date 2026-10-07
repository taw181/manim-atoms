"""Compare two frame_checksums.sh runs, scene by scene and frame by frame.

    python compare_checksums.py BEFORE AFTER

Prints, per scene in AFTER, how many frames differ and the first few frame
numbers. Exits 1 if any scene differs or has no baseline.
"""

import pathlib
import sys

before, after = map(pathlib.Path, sys.argv[1:3])
bad = 0
for fa in sorted(after.glob("*.md5")):
    fb = before / fa.name
    if not fb.exists():
        print(f"{fa.stem}: no baseline")
        bad += 1
        continue
    x, y = fb.read_text().split(), fa.read_text().split()
    d = [i for i, (p, q) in enumerate(zip(x, y)) if p != q]
    ok = not d and len(x) == len(y)
    bad += not ok
    print(f"{fa.stem}: {len(x)} vs {len(y)} frames, {len(d)} differ" + (f" {d[:10]}" if d else ""))
print("ALL IDENTICAL" if not bad else f"{bad} scene(s) differ")
sys.exit(1 if bad else 0)
