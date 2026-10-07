"""Trace a scene's script without rendering it.

After every play and wait it records the animations' types and run time, and
a digest of every mobject on screen (points, colours, opacities, stroke
widths, in draw order; not class names, which change nothing drawn). Two
versions of the code whose traces match draw the same thing at the same
moment, which settles a refactor of a scene too noisy to compare by frames.

    python scene_trace.py MODULE_FILE SCENE OUT.json
    PYTHONPATH=/tmp/old/src python scene_trace.py /tmp/old/src/.../MODULE_FILE SCENE OLD.json

With TRACE_STOP=k it also writes OUT.json.mobs, the digest of each top-level
mobject after step k, to find which one a difference is in.
"""
import hashlib
import importlib.util
import json
import sys

import numpy as np
from manim import *

path, name, out = sys.argv[1:4]
spec = importlib.util.spec_from_file_location("traced", path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
cls = getattr(mod, name)
trace = []


def digest(scene):
    h = hashlib.sha256()
    for m in scene.mobjects:
        for f in m.get_family():
            pass  # the class name changes nothing drawn
            h.update(np.round(np.asarray(f.points, dtype=float), 9).tobytes())
            for attr in ("fill_rgbas", "stroke_rgbas", "background_stroke_rgbas"):
                v = getattr(f, attr, None)
                if v is not None:
                    h.update(np.round(np.asarray(v, dtype=float), 9).tobytes())
            if hasattr(f, "stroke_width"):
                h.update(repr(float(np.round(f.stroke_width, 9))).encode())
    return h.hexdigest()[:16]


orig_play, orig_wait = Scene.play, Scene.wait


import os
STOP = int(os.environ.get("TRACE_STOP", "-1"))


def per_mobject(scene):
    out = []
    for m in scene.mobjects:
        class One: mobjects = [m]
        out.append([type(m).__name__, len(m.get_family()), digest(One)])
    return out


def play(self, *args, **kwargs):
    kinds = [type(a).__name__ for a in args]
    orig_play(self, *args, **kwargs)
    if len(trace) == STOP:
        json.dump(per_mobject(self), open(out + ".mobs", "w"))
    trace.append(["play", kinds, kwargs.get("run_time"), len(self.mobjects), digest(self)])


def wait(self, *args, **kwargs):
    orig_wait(self, *args, **kwargs)
    trace.append(["wait", list(map(float, args)), None, len(self.mobjects), digest(self)])


Scene.play, Scene.wait = play, wait
with tempconfig({"dry_run": True, "quality": "low_quality", "disable_caching": True}):
    cls().render()
json.dump(trace, open(out, "w"))
print(len(trace), "steps")
