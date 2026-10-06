"""Ramsey-Borde interferometry: every arm split by every pulse, and the
bookkeeping of which of the resulting paths close.

Two pieces the Ramsey-Borde scene is built from, neither tied to its layout:

- ``beamsplitter_tree`` follows one atom through a sequence of pi/2 pulses,
  each from below (+k) or above (-k), splitting every arm at every pulse. It
  says which paths meet a partner again at the last pulse -- the closed
  loops, the only ones with a fringe -- and which never do.
- ``sweep_pulse`` is a wavepacket that crosses a whole column of atoms from
  one side, stopping on each in turn, for a pulse that drives several arms.
"""

import numpy as np
from manim import *

from manim_atoms.interferometry.style import *
from manim_atoms.core.primitives import make_laser_pulse
from manim_atoms.interferometry.tools.lmt import recoil

CLOSE_TOL = 1e-6  # how near two paths have to end to count as one point


def beamsplitter_tree(pulses, start, slope):
    """Every path through a sequence of beamsplitters, and which ones close.

    `pulses` is [(x, from_below)], `start` where the atom (in |g> at rest)
    meets the first, and `slope` the rise per unit x one photon recoil gives.
    Each pulse splits every arm into itself left alone (name + "0") and a copy
    that has made the transition (name + "1"), with the recoil that
    ``lmt.recoil`` gives: a |g> arm absorbs and moves with the photon, an |e>
    arm is stimulated to emit into it and recoils against it.

    The last pulse does not split: it is the readout. The paths that arrive
    there on the same point in pairs are the closed loops; each pair leaves
    by two ports, in the two states its arms arrived in (the pulse couples
    exactly those). Everything else is open: it never meets a partner, so it
    carries no phase anyone can read.

    Returns a dict:
      ``steps``  one per pulse but the last: ``x``, ``from_below``,
                 ``splits`` [(parent, point, stay, kicked, kicked state, dv)],
                 ``legs`` [(name, start, end, state, closed)] to the next pulse;
      ``paths``  each final name's corners, from the first pulse to the last;
      ``states`` each final name's (state, recoils) on arrival at the last;
      ``loops``  [(name_a, name_b)], each pair that meets, lowest first;
      ``open``   the names that meet nobody.
    """
    arms = {"": dict(state="g", n=0, points=[np.array(start, dtype=float)])}
    steps = []
    for k, (x, from_below) in enumerate(pulses[:-1]):
        splits = []
        for name, arm in list(arms.items()):
            point = arm["points"][-1]
            dv, state = recoil(arm["state"], from_below)
            arms[name + "0"] = dict(arm, points=list(arm["points"]))
            arms[name + "1"] = dict(state=state, n=arm["n"] + dv,
                                    points=list(arm["points"]))
            del arms[name]
            splits.append((name, point, name + "0", name + "1", state, dv))
        dx = pulses[k + 1][0] - x
        for arm in arms.values():
            arm["points"].append(arm["points"][-1] + np.array([dx, dx * arm["n"] * slope, 0.0]))
        steps.append(dict(x=x, from_below=from_below, splits=splits))

    # which arrive on a partner
    names = sorted(arms, key=lambda m: arms[m]["points"][-1][1])
    loops, used = [], set()
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if a in used or b in used:
                continue
            if np.linalg.norm(arms[a]["points"][-1] - arms[b]["points"][-1]) < CLOSE_TOL:
                loops.append((a, b))
                used.update((a, b))
    closed = used
    open_ = [m for m in names if m not in closed]

    # A leg is solid if any closed path runs along it: an open path shares
    # its history with a closed one up to the pulse it parts from it at.
    for k, step in enumerate(steps):
        legs, seen = [], set()
        for name, arm in arms.items():
            prefix = name[: k + 1]
            if prefix in seen:
                continue
            seen.add(prefix)
            is_closed = any(m.startswith(prefix) for m in closed)
            # the state flown on this leg is the prefix's: replay it
            state = "g"
            for bit, (_, fb) in zip(prefix, pulses):
                if bit == "1":
                    state = recoil(state, fb)[1]
            legs.append((prefix, arm["points"][k], arm["points"][k + 1], state, is_closed))
        step["legs"] = legs

    return dict(
        steps=steps,
        paths={m: arm["points"] for m, arm in arms.items()},
        states={m: (arm["state"], arm["n"]) for m, arm in arms.items()},
        loops=loops,
        open=open_,
    )


def sweep_pulse(scene, x, stops, from_below=True, extras=(), fade=(),
                hit_time=0.45):
    """A wavepacket crossing a column of atoms from one side, one at a time.

    `stops` is [(y, on_hit)]: the packet travels to each y in the order it
    reaches them -- bottom up from below, top down from above -- and plays
    ``on_hit()`` (a list of animations: the flash, the split) while it sits
    on that atom. After the last it carries on a little way and fades, since
    a travelling wave passes on through rather than ending on the atom.
    `extras` fade in as it enters, `fade` go out as it leaves.
    """
    sign = 1 if from_below else -1
    y = -sign * (config.frame_y_radius + 0.6)
    packet = make_laser_pulse(x, y)
    if not from_below:
        packet.rotate(PI)
    scene.add(packet)
    stops = sorted(stops, key=lambda s: sign * s[0])
    for i, (y_stop, on_hit) in enumerate(stops):
        travel = abs(y_stop - y)
        scene.play(
            packet.animate.move_to([x, y_stop, 0]),
            *([FadeIn(m) for m in extras] if i == 0 else []),
            rate_func=linear,
            run_time=travel / PULSE_SPEED,
        )
        scene.play(*on_hit(), run_time=hit_time)
        y = y_stop
    scene.play(
        packet.animate.shift(UP * sign * 0.9).set_stroke(opacity=0),
        *[FadeOut(m) for m in fade],
        run_time=0.4,
    )
    scene.remove(packet)
