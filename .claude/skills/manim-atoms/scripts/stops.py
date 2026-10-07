#!/usr/bin/env python3
"""Print when a scene stops, so frames.py can be pointed at each stop.

    uv run python stops.py manim_atoms.tweezers.scenes.rearrangement TweezerRearrangement

Runs the scene without rendering, with beat(), stage_break() and hold()
recording the scene's clock, and prints the times just before each stop:
paste them after frames.py's -t. A stop comes after its settling wait, so
the frame just before it is the picture the presenter stops on.
"""

import importlib
import sys

from manim import tempconfig

module, name = sys.argv[1:3]
scene = getattr(importlib.import_module(module), name)
times = []


class Probe(scene):
    def _mark(self, *args, **kwargs):
        times.append(self.renderer.time)

    beat = stage_break = hold = _mark


with tempconfig({"dry_run": True, "quality": "low_quality", "disable_caching": True,
                 "verbosity": "ERROR", "progress_bar": "none"}):
    Probe().render()
print(" ".join(f"{max(t - 0.1, 0):.2f}" for t in times))
