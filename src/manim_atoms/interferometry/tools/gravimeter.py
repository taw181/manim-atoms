"""The atom gravimeter: a Mach-Zehnder in free fall.

A space-time diagram like the gradiometer's: the horizontal axis is time, the
vertical axis is height, and the laser points up, against gravity. Gravity
does the same thing to every arm -- it adds -g t^2 / 2 to the height -- so
each arm is the straight leg it would be in the freely falling frame, bent
down by one common parabola. That is exactly what core.spacetime's displaced
legs are for: `leg_point` takes a leg's corners and a displacement, and keeps
the leg through both corners while bowing it in between. Here the
displacement is the fall, and the corners are where the pulses actually find
the atoms.

The scale is exaggerated, of course: in a real gravimeter g T is metres per
second against a recoil of millimetres per second, and the arms would be two
parabolas a hair apart.
"""

import numpy as np
from manim import *

from manim_atoms.interferometry.style import *
from manim_atoms.core.spacetime import leg_point


# --- gravimeter geometry --------------------------------------------------
# The atoms are released from a trap at the first pulse, so they come in at
# rest (a flat worldline) and the lower arm leaves A with no vertical velocity.
# GV_FALL is chosen so the fall by the mirror pulse is a quarter of the arms'
# free-fall separation, GV_T / 4, and by the last pulse the whole of it --
# which closes the interferometer at the height it opened at, and keeps the
# whole figure inside the frame.
GV_T = 2.8  # time between pulses
GV_A = np.array([-5.4, -0.9, 0.0])  # the first pi/2, at release
GV_FALL = 1.0 / (2 * GV_T)  # g in diagram units: the drop is GV_FALL t^2 / 2
GV_OUT = 1.4  # how far the output ports are drawn past the last pulse


def drop(t, t0=GV_A[0], g=GV_FALL):
    """How far an atom released at lab time t0 has fallen by time t: g t^2 / 2."""
    return 0.5 * g * (t - t0) ** 2


def fall(t, t0=GV_A[0], g=GV_FALL):
    """The fall as a leg displacement for core.spacetime: -drop, zero at release."""
    return -drop(t, t0, g)


def in_lab(p, t0=GV_A[0], g=GV_FALL):
    """A point of the freely falling frame, where the same atom is in the lab."""
    p = np.array(p, dtype=float)
    return p + DOWN * drop(p[0], t0, g)


def free_fall_corners(a=GV_A, T=GV_T):
    """The Mach-Zehnder parallelogram the arms trace in the falling frame:
    first pi/2, the two arms at the pi pulse (lower, upper), the last pi/2.

    The lower arm leaves at rest and the upper with one recoil, which is drawn
    as one unit of height per unit of time -- 45 degrees, as in MachZehnder.
    """
    a = np.array(a, dtype=float)
    return a, a + RIGHT * T, a + (RIGHT + UP) * T, a + RIGHT * 2 * T + UP * T


def curved_loop(corners, disp, n=40):
    """The region a falling interferometer encloses, as a closed polygon.

    `corners` go round the loop in order (A, B, C, B' for a Mach-Zehnder);
    each side is sampled along the same bowed leg the atoms fly, so the shading
    sits exactly inside the drawn arms.
    """
    pts = []
    for start, end in zip(corners, [*corners[1:], corners[0]]):
        pts += [leg_point(start, end, disp, s) for s in np.linspace(0, 1, n)[:-1]]
    return Polygon(*pts, **LOOP_AREA_STYLE)


def drop_arrow(t, top, label_tex, label_dir=RIGHT, g=GV_FALL, t0=GV_A[0]):
    """The fall by lab time t, drawn from where the falling frame would have the
    atom (height `top`) down to where it really is, with its label."""
    start = np.array([t, top, 0.0])
    arrow = Arrow(start, start + DOWN * drop(t, t0, g), **GRAVITY_ARROW_STYLE)
    label = MathTex(label_tex, font_size=FONT_LEGEND, color=lighten(GRAVITY_COLOR))
    return VGroup(arrow, label.next_to(arrow, label_dir, buff=0.12))
