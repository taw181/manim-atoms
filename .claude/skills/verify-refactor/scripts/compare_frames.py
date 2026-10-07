"""Compare two directories of PNGs (last frames, or saved figures) pixel by pixel.

    uv run python compare_frames.py BEFORE AFTER            # AFTER must have all of BEFORE
    uv run python compare_frames.py BEFORE AFTER --subset   # AFTER re-rendered only some

Lists every image that differs (with how many pixels) or is missing from
AFTER, and exits 1 if any did. A pure refactor must come out identical.
"""

import sys
from pathlib import Path

import numpy as np
from PIL import Image

before, after = Path(sys.argv[1]), Path(sys.argv[2])
subset = "--subset" in sys.argv[3:]
names = sorted(p.name for p in before.glob("*.png"))
if subset:
    names = [n for n in names if (after / n).exists()]
bad = 0
for name in names:
    other = after / name
    if not other.exists():
        print("MISSING", name)
        bad += 1
        continue
    x, y = np.asarray(Image.open(before / name)), np.asarray(Image.open(other))
    if x.shape != y.shape:
        print("DIFFERS", name, "shape", x.shape, "->", y.shape)
        bad += 1
    elif (x != y).any():
        print("DIFFERS", name, int((x != y).any(axis=-1).sum()), "pixels")
        bad += 1
print(f"{len(names)} compared, {bad} differ or missing")
sys.exit(1 if bad else 0)
