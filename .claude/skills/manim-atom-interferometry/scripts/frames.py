#!/usr/bin/env python3
"""Pull stills out of a manim render so you can actually look at them.

You cannot watch a video, so the render-and-check loop is: render at -ql,
extract frames at the moments that matter, and Read the PNGs.

    python frames.py VIDEO.mp4 -t 3.2 5.0 8.5 --final
    python frames.py VIDEO.mp4 -t 8.5 --sample 1.0,-1.0 2.0,0.5

--sample takes manim scene coordinates, not pixels, and prints the brightest
pixel near each one. Use it to check that two colours are actually
distinguishable rather than trusting the palette names.
"""

import argparse
import subprocess
import sys
from pathlib import Path

FRAME_HEIGHT = 8.0  # manim's default; frame width follows the video's aspect


def grab(video, out, ss=None, sseof=None):
    cmd = ["ffmpeg", "-v", "error"]
    cmd += ["-sseof", str(sseof)] if sseof is not None else ["-ss", str(ss)]
    cmd += ["-i", str(video), "-frames:v", "1", str(out), "-y"]
    subprocess.run(cmd, check=True)
    return out


def sample(png, points, window=4):
    from PIL import Image

    im = Image.open(png).convert("RGB")
    w, h = im.size
    frame_width = FRAME_HEIGHT * w / h
    for x, y in points:
        cx = round((x + frame_width / 2) / frame_width * w)
        cy = round((FRAME_HEIGHT / 2 - y) / FRAME_HEIGHT * h)
        best = max(
            (
                im.getpixel((cx + dx, cy + dy))
                for dx in range(-window, window + 1)
                for dy in range(-window, window + 1)
                if 0 <= cx + dx < w and 0 <= cy + dy < h
            ),
            key=sum,
        )
        print(f"  ({x:6.2f},{y:6.2f}) -> rgb{best}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("video")
    ap.add_argument("-t", "--at", nargs="*", type=float, default=[],
                    help="timestamps in seconds")
    ap.add_argument("--final", action="store_true",
                    help="also grab the last frame")
    ap.add_argument("-o", "--out", default=".", help="output directory")
    ap.add_argument("--sample", nargs="*", default=[], metavar="X,Y",
                    help="manim coords to sample in each extracted frame")
    args = ap.parse_args()

    video = Path(args.video)
    if not video.exists():
        sys.exit(f"no such video: {video}")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    points = [tuple(float(v) for v in p.split(",")) for p in args.sample]

    jobs = [(f"{video.stem}_{t:g}s.png", dict(ss=t)) for t in args.at]
    if args.final or not args.at:
        jobs.append((f"{video.stem}_final.png", dict(sseof=-0.3)))

    for name, kw in jobs:
        png = grab(video, out / name, **kw)
        print(png)
        if points:
            sample(png, points)


if __name__ == "__main__":
    main()
