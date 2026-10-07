"""Large momentum transfer: sequences of single-photon pulses, each driving
every arm it crosses (after Rudolph et al., PRL 124, 083604 (2020), Fig. 1c).

What is LMT's own: lmt_points, the ladder's corners one arm at a time, and
lmz_pulses, the sequence of an LMT Mach-Zehnder of any odd order, for the
engine in interferometry.tools.pulse_sequence to step through (it uses
core.primitives.recoil for each kick). Pulses from either side are
interferometry.tools.pulses.kick_worldline. Defaults bind to the LMT_* and
LMZ_* geometry blocks below.
"""

import numpy as np
from manim import *

from manim_atoms.interferometry.style import *
from manim_atoms.core.primitives import recoil
from manim_atoms.interferometry.tools.pulse_sequence import Pulse


# --- large momentum transfer geometry -------------------------------------
# Same space-time frame. The first kick is the pi/2 that splits the atom; every
# kick after it drives both arms, which reach it in opposite internal states,
# so one pulse pushes them opposite ways -- one absorbs, the other is
# stimulated to emit -- and the arms end up (2n - 1) hbar k apart after n.
LMT_T0 = -5.3
LMT_Z = -0.75
LMT_STEP = 1.0  # time between kicks in the ladder
LMT_TAIL = 1.3  # free flight after the last kick
LMT_U = 0.052  # baseline covered per unit time, per photon recoil
LMT_KICKS = 10


def lmt_points(slope_per_kick):
    """Worldline corners for an arm gaining `slope_per_kick(i)` on kick i."""
    pts = [np.array([LMT_T0, LMT_Z, 0.0])]
    for i in range(LMT_KICKS):
        dt = LMT_TAIL if i == LMT_KICKS - 1 else LMT_STEP
        pts.append(pts[-1] + np.array([dt, dt * slope_per_kick(i), 0.0]))
    return pts


# --- LMT sequences ----------------------------------------------------------


def lmz_pulses(n, step, T, t0=0.0, stage=0):
    """The LMT Mach-Zehnder of order n (odd), as Pulse objects for
    run_sequence: a pi/2 and (n - 1)/2 pulses out, a mirror of n pulses,
    (n - 1)/2 pulses back and a pi/2. Every pulse drives both arms, from
    whichever side opens (or, at the mirror and after it, closes) the gap by
    2 hbar k; the sequence is symmetric in time about the middle of the
    mirror, so the arms close. Stages ``stage`` to ``stage + 2``: beam
    splitter, mirror, beam splitter."""
    m = (n - 1) // 2
    end = 2 * T + (n - 1) * step
    pushes = [(0.0, 0.5, +1, stage)]  # (time, area, which way the kicked arm goes, stage)
    pushes += [(j * step, 1.0, +1, stage) for j in range(1, m + 1)]
    pushes += [(T + j * step, 1.0, -1, stage + 1) for j in range(n)]
    pushes += [(end - j * step, 1.0, +1, stage + 2) for j in range(m, 0, -1)]
    pushes.append((end, 0.5, +1, stage + 2))
    pulses, kicked = [], "g"  # the state of the arm the first pulse kicks
    for t, area, way, s in pushes:
        # the beam splitters come from below; each pi pulse from whichever
        # side's photon pushes the kicked arm `way`
        from_below = area == 0.5 or recoil(kicked, True)[0] == way
        pulses.append(Pulse(t0 + t, area, from_below, stage=s))
        kicked = "e" if kicked == "g" else "g"
    return pulses


def lmt_ladder_pulses(kicks=LMT_KICKS, step=LMT_STEP, t0=LMT_T0):
    """A pi/2 that splits the atom, then pi pulses alternating from below
    and above: each drives both arms, which reach it in opposite states, so
    one absorbs and the other is stimulated to emit and they are pushed
    apart by 2 hbar k a pulse."""
    pulses, t = [], t0
    for i in range(kicks):
        pulses.append(Pulse(t, 0.5 if i == 0 else 1.0, from_below=i % 2 == 0))
        t += step
    return pulses


# --- the LMT Mach-Zehnder (Rudolph et al., Fig. 1c) -------------------------
LMZ_ORDER = 11
LMZ_T0 = -5.9  # the first pi/2
LMZ_Z = -0.3  # where the atom comes in
LMZ_STEP = 0.3  # between the pulses of one stage
LMZ_T = 3.0  # the first pi/2 to the first mirror pulse
LMZ_U = 0.15  # baseline covered per unit time, per photon recoil
LMZ_END = 2 * LMZ_T + (LMZ_ORDER - 1) * LMZ_STEP  # the last pi/2, from the first
# The ports part by one recoil only, so they are drawn long enough for the
# two atoms to come apart.
LMZ_PORT = 3.4
