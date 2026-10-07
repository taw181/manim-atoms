"""Compare frame_checksums.sh runs, scene by scene and frame by frame.

    python compare_checksums.py BEFORE AFTER
    python compare_checksums.py BEFORE1,BEFORE2,BEFORE3 AFTER

Prints, per scene in AFTER, how many frames differ and the first few frame
numbers. With several BEFORE runs (renders of the old code, comma-separated),
a frame passes if it is identical to that frame in any of them: renders are
not perfectly deterministic, and a scene whose old renders disagree among
themselves in a few frames can then still be proven unchanged frame by
frame. Exits 1 if any scene differs or has no baseline.
"""

import pathlib
import sys

befores = [pathlib.Path(p) for p in sys.argv[1].split(",")]
after = pathlib.Path(sys.argv[2])
bad = 0
for fa in sorted(after.glob("*.md5")):
    runs = [b / fa.name for b in befores if (b / fa.name).exists()]
    if not runs:
        print(f"{fa.stem}: no baseline")
        bad += 1
        continue
    olds = [r.read_text().split() for r in runs]
    new = fa.read_text().split()
    d = [i for i, h in enumerate(new) if all(i >= len(o) or o[i] != h for o in olds)]
    ok = not d and all(len(o) == len(new) for o in olds)
    bad += not ok
    lengths = "/".join(str(len(o)) for o in olds)
    print(f"{fa.stem}: {lengths} vs {len(new)} frames, {len(d)} differ" + (f" {d[:10]}" if d else ""))
print("ALL IDENTICAL" if not bad else f"{bad} scene(s) differ")
sys.exit(1 if bad else 0)
