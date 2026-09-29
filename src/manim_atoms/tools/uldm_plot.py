"""AION's reach for ultralight dark matter, as a small log-log inset.

The photon-coupling panel of Badurina et al. 2020 (Fig. 3): |d_e| against
the scalar's mass m_phi, with the region other experiments have already
excluded in grey and each AION stage's projected reach as a line -- anything
above a line that is not already grey, that stage would see. A dark-matter
figure puts it beside itself with the mass it is drawing marked across it
(mass_mark), which is what ties an oscillating trace to a place in the
parameter space.

It is an inset, so it is built to be read small: the axes are labelled every
few decades, and there are three curves, one per AION stage (AION-10 and
AION-100 at their goal scenarios), each labelled in its colour. AEDGE is
left to the slide that introduces it.
"""

from functools import lru_cache

import numpy as np
from manim import *

from aionanim.physics.uldm_sensitivity import (
    EXCLUDED,
    ULDM_SCENARIOS,
    load_uldm_sensitivity,
)
from aionanim.style import *
from aionanim.tools.gw_plot import plot_point, sensitivity_axes

# The paper's mass range, and its coupling range cut at 1, above which
# everything is excluded. The bottom stays at the paper's 1e-16, two decades
# under AEDGE's best, so the AEDGE slide draws the same frame.
ULDM_LOG_M = (-19, -10)
ULDM_LOG_D = (-16, 0)
ULDM_LABEL_EVERY = (2, 4)  # 10^-18, -16, ... on x; 10^-16, -12, ... on y, as the paper
ULDM_TICK_BUFF = 0.08
# Where each label goes, in (log10 m, log10 d_e), and which side of that
# point it hangs: AION-10 just above the frame, where its curve leaves the
# top of the plot -- the curve lies wholly in a grey band too thin in an
# inset to hold its label and the grey's name clear of it; AION-100
# centred in the V of its curve (carried below 0.3 Hz, each curve turns
# back up on the left, so there is no open end to label), a little left of
# the middle so the mass the dark-matter slides mark (~1.8e-15 eV) clears
# it; AION-km right of its line, in the empty lower right.
ULDM_LABELS = {
    "AION-10": ((-11.8, 0.0), UP),
    "AION-100": ((-15.8, -5.6), ORIGIN),
    "AION-km": ((-13.3, -8.8), RIGHT),
}
# The grey region's name, centred here: in the V of AION-10's curve, the one
# stretch of the grey no curve crosses. A size down from the curve labels,
# to fit the V's width; in the smallest inset the V's arms still clip its
# corners, which its outline is for.
ULDM_EXCLUDED_LABEL = (-15.4, -1.2)
ULDM_MARK_LABEL_ROOM = 1.0  # decades a mass label needs right of its line
ULDM_LABEL_STEMS = {
    "AION-10": "aion10_goal",
    "AION-100": "aion100_goal",
    "AION-km": "aion_km",
}
# The curves an inset draws: AION's stages only. AEDGE, in space, is kept for
# the slide that introduces it (scenes/aedge.py), which draws it itself.
ULDM_INSET_STEMS = ("aion10_goal", "aion100_goal", "aion_km")


@lru_cache(maxsize=None)
def _log_curve(stem):
    m, d = load_uldm_sensitivity(stem)
    return np.log10(m), np.log10(d)


def clipped(stem, top, x_range=None):
    """A curve's (log m, log d), cut to the stretch under `top` around its
    lowest point: where it comes down through `top` on the left, if it does
    (the AION curves carried below 0.3 Hz do), and goes up through it on the
    right -- and, given `x_range` (log m), to the axes' left and right edges
    too, which the AION curves carried below 0.3 Hz run past."""
    x, y = _log_curve(stem)
    if x_range is not None:
        x, y = _within(x, y, *x_range)
        if len(x) == 0:
            return x, y
    low = int(np.argmin(y))
    if y[low] > top:
        return x[:0], y[:0]
    over = np.nonzero(y > top)[0]
    left = over[over < low]
    right = over[over > low]
    i = left[-1] + 1 if len(left) else 0
    j = right[0] if len(right) else len(x)
    xs, ys = x[i:j], y[i:j]

    def crossing(a, b):
        s = (top - y[a]) / (y[b] - y[a])
        return x[a] + s * (x[b] - x[a])

    if i > 0:
        xs, ys = np.insert(xs, 0, crossing(i - 1, i)), np.insert(ys, 0, top)
    if j < len(x):
        xs, ys = np.append(xs, crossing(j - 1, j)), np.append(ys, top)
    return xs, ys


def _within(x, y, lo, hi):
    """(x, y) cut to lo <= x <= hi, with the ends interpolated onto the edges."""
    keep = (x > lo) & (x < hi)
    if not keep.any():
        return x[:0], y[:0]
    xs, ys = x[keep], y[keep]
    if x[0] < lo:
        xs, ys = np.insert(xs, 0, lo), np.insert(ys, 0, np.interp(lo, x, y))
    if x[-1] > hi:
        xs, ys = np.append(xs, hi), np.append(ys, np.interp(hi, x, y))
    return xs, ys


def log_x_range(axes):
    """The axes' mass range, (log m) at their left and right edges."""
    return axes.log_origin[0], axes.log_origin[0] + axes.x_range[1]


def uldm_axes(origin, width, height):
    """The inset's frame: decades of m_phi / eV and |d_e|, as (axes, frame)."""
    return sensitivity_axes(
        ULDM_LOG_M, ULDM_LOG_D, origin, width, height,
        x_label=r"$m_\phi$ / eV", y_label=r"$|d_e|$",
        tick_font=FONT_INSET_TICK, label_font=FONT_INSET_LABEL,
        label_every=ULDM_LABEL_EVERY, buff=ULDM_TICK_BUFF,
    )


def _polyline(axes, x, y, **style):
    line = VMobject(**style)
    line.set_points_as_corners([plot_point(axes, a, b) for a, b in zip(x, y)])
    return line


def excluded_region(axes):
    """The grey region already ruled out, and the line along its lower edge."""
    x, y = clipped(EXCLUDED, axes.log_top, log_x_range(axes))
    edge = [plot_point(axes, a, b) for a, b in zip(x, y)]
    top = plot_point(axes, axes.log_origin[0], axes.log_top)[1]
    region = Polygon(
        *edge, [edge[-1][0], top, 0], [edge[0][0], top, 0], **ULDM_EXCLUDED_STYLE
    )
    return VGroup(region, _polyline(axes, x, y, **ULDM_EXCLUDED_EDGE))


def uldm_curves(axes, stems=tuple(ULDM_SCENARIOS)):
    """Each stage's reach, stem: line, clipped to the frame of the axes."""
    curves = {}
    for stem in stems:
        curves[stem] = _polyline(
            axes, *clipped(stem, axes.log_top, log_x_range(axes)),
            stroke_color=ULDM_COLORS[stem], stroke_width=ULDM_CURVE_WIDTH,
        )
    return curves


def uldm_labels(axes):
    labels = VGroup()
    for name, ((x, y), side) in ULDM_LABELS.items():
        labels.add(Tex(
            name, font_size=FONT_INSET_LABEL, color=ULDM_COLORS[ULDM_LABEL_STEMS[name]],
        ).next_to(plot_point(axes, x, y), side, buff=0))
    return labels.set_stroke(**ULDM_LABEL_OUTLINE, background=True)


def excluded_label(axes, font_size=FONT_INSET_TICK, at=ULDM_EXCLUDED_LABEL, side=ORIGIN):
    """The grey region named, hung off `at` (log m, log d_e) on `side`."""
    return Tex(
        r"excluded by experiment", font_size=font_size, color=lighten(GUIDE_COLOR),
    ).next_to(plot_point(axes, *at), side, buff=0).set_stroke(
        **ULDM_LABEL_OUTLINE, background=True
    )


def uldm_inset(origin, width, height):
    """The whole inset, its axes' lower-left corner at `origin`.

    A VGroup of the frame, the excluded region, the curves and their labels,
    with `.axes` on it for mass_mark. The curves go over the grey, since
    where a stage's line runs inside it is part of what the plot says.
    """
    axes, frame = uldm_axes(origin, width, height)
    curves = uldm_curves(axes, ULDM_INSET_STEMS)
    # every label over every curve, so their outlines can do their job
    inset = VGroup(
        frame, excluded_region(axes), VGroup(*curves.values()),
        VGroup(*uldm_labels(axes), excluded_label(axes)),
    )
    inset.axes = axes
    return inset


def reach(stem, mass):
    """log10 |d_e| on a stage's curve at `mass`, or None off its ends."""
    x, y = _log_curve(stem)
    lm = np.log10(mass)
    if not x[0] <= lm <= x[-1]:
        return None
    return float(np.interp(lm, x, y))


def deepest_reach(mass, stems=ULDM_INSET_STEMS):
    """(stem, log10 |d_e|) of the curve reaching the smallest coupling at
    `mass`, or (None, None) where no curve covers it."""
    reaches = [(y, stem) for stem in stems if (y := reach(stem, mass)) is not None]
    if not reaches:
        return None, None
    y, stem = min(reaches)
    return stem, y


def mass_mark(axes, mass, on=None, label=r"m_\phi"):
    """A mass marked across the inset.

    A faint line up the plot at m_phi, and a dot where it meets the curve
    `on` -- by default whichever reaches deepest there. From the edge of the
    grey down to that dot the line is drawn at full strength: the couplings
    nothing has ruled out yet that AION would see, which is the point of
    marking a mass at all. (Not AION-10's curve by default: at every mass
    the dark-matter figures draw, it lies inside the grey, so a dot on it
    says only that the prototype's next stage reaches today's limits.)

    `label` goes at the foot of the line (see mass_label); label=None leaves
    it off, for a mark that moves and a label that is swapped instead.
    """
    lm = np.log10(mass)
    bottom = plot_point(axes, lm, axes.log_origin[1])
    top = plot_point(axes, lm, axes.log_top)
    mark = VGroup(Line(bottom, top, **ULDM_MARK_STYLE).set_stroke(
        opacity=ULDM_MARK_FAINT_OPACITY
    ))
    y = reach(on, mass) if on else deepest_reach(mass)[1]
    if y is not None and y <= axes.log_top:
        edge = min(reach(EXCLUDED, mass), axes.log_top)
        if y < edge:
            mark.add(Line(plot_point(axes, lm, edge), plot_point(axes, lm, y),
                          **ULDM_MARK_STYLE))
        mark.add(Dot(plot_point(axes, lm, y), radius=ULDM_MARK_DOT_RADIUS,
                     color=FIELD_COLOR))
    if label is not None:
        mark.add(mass_label(axes, mass, label))
    return mark


def mass_label(axes, mass, label=r"m_\phi"):
    """`label` at the foot of the mark: right of the line, where the plot is
    emptiest at every mass, unless the right-hand edge is too close."""
    lm = np.log10(mass)
    side = LEFT if lm > ULDM_LOG_M[1] - ULDM_MARK_LABEL_ROOM else RIGHT
    return MathTex(label, font_size=FONT_INSET_LABEL, color=FIELD_COLOR).next_to(
        plot_point(axes, lm, axes.log_origin[1]), UP + side, buff=0.04
    )
