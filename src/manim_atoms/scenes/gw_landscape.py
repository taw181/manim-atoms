"""The gravitational-wave sensitivity landscape, built up a piece at a time.

LIGO and one merger (60 Msun at z = 0.1, the track MergerOnSensitivityPlot
rides) first; then the other eight source tracks, 60 to 1e7 Msun at z = 0.1,
1 and 10; then LISA and ET, the space and next-generation ground detectors;
then two dashed lines at 2e-2 and 2 Hz marking the gap between them; then
the detectors that fill it, one step each, in order of sensitivity:
AION-10, AION-100, AION-km and AEDGE, or whichever a subclass lists in
GAP_FILLERS.

The curves are the digitised ones in aionanim/data/gw_sensitivity/ and the tracks come
from aionanim.physics.gw_signals, so this is the same figure as
aionanim.plots.gw_sensitivity, on the source figure's axes.

    uv run manim -qh src/aionanim/scenes/gw_landscape.py SensitivityBuildUp

Every pause between steps goes through beat(), so a manim-slides subclass
that makes beat() a next_slide() turns it into one slide per step, advancing
on the presenter's click instead of a timed hold.
"""

import numpy as np
from manim import *

from aionanim.tools.gw_plot import curve_points, detector_region, plot_point, sensitivity_axes
from aionanim.physics.gw_signals import mass_tex, merger_track, phenom_a_frequencies
from aionanim.style import *

# --- layout ---------------------------------------------------------------
# The source figure's frame: 1e-6 to 1e4 Hz, 1e-24 to ~3e-15.
LOG_F_RANGE = (-6, 4)
LOG_H_RANGE = (-24, -14.5)
PLOT_ORIGIN = np.array([-4.9, -2.75, 0.0])  # lower-left corner of the axes
PLOT_WIDTH = 11.3
PLOT_HEIGHT = 5.9

# name: (CSV stem, where the label's left edge sits as (log f, log h)).
DETECTORS = {
    "LIGO": ("ligo", (1.25, -20.8)),
    "LISA": ("lisa", (-3.7, -20.9)),
    "ET": ("et", (2.05, -23.55)),
    # AION-10 is only the bottom of a V clipped by the frame: labelled just
    # under it, between the band edges.
    "AION-10": ("aion_10", (-1.05, -15.75)),
    "AION-100": ("aion_100", (2.3, -16.5)),
    "AION-km": ("aion_km", (2.3, -18.5)),
    "AEDGE": ("aedge", (-1.6, -23.15)),
}

# (total mass / Msun, redshift); the first is the one shown alone.
FIRST_MERGER = (60, 0.1)
MERGERS = [(M, z) for M in (60, 1e4, 1e7) for z in (0.1, 1, 10)]

# A mass label sits above its track's merger peak unless shifted here: the
# 1e4 Msun peak lands at ~1 Hz, right where LISA's ragged top meets ET's
# wall, so its label moves back along its own track, clear of both.
MASS_LABEL_SHIFT = {1e4: np.array([-0.9, 0.1, 0.0])}

# The dashed lines bounding the mid band, Hz.
BAND_EDGES = (2e-2, 2)

# --- pacing ---------------------------------------------------------------
STEP_TIME = 1.5
BEAT_HOLD = 1.5  # between steps in the plain scene

# Draw order: regions at the back, then detector curves, then the source
# tracks and every label, so a region shaded in later never dims a track.
Z_REGION, Z_CURVE, Z_TRACK, Z_LABEL = 0, 1, 2, 3


def detector(axes, name):
    """(region, curve, label) for one detector, layered."""
    stem, label_at = DETECTORS[name]
    color = GW_DETECTOR_COLORS[name]
    region, curve = detector_region(axes, stem, color)
    label = Tex(name, font_size=FONT_AXIS, color=color)
    label.move_to(plot_point(axes, *label_at), aligned_edge=LEFT)
    region.set_z_index(Z_REGION)
    curve.set_z_index(Z_CURVE)
    label.set_z_index(Z_LABEL)
    return region, curve, label


def merger(axes, M, z, width=GW_TRACK_CROWD_WIDTH):
    f, h = merger_track(M, z)
    track = VMobject(stroke_color=merger_color(z), stroke_width=width)
    track.set_points_as_corners(curve_points(axes, f, h))
    return track.set_z_index(Z_TRACK)


def mass_label(axes, M, z):
    """The mass, centred above where its track turns over at merger."""
    f, h = merger_track(M, z)
    merging = f >= phenom_a_frequencies(M, z)["merger"]
    peak = np.flatnonzero(merging)[np.nanargmax(h[merging])]
    label = MathTex(mass_tex(M), font_size=FONT_TICK, color=PLOT_FOREGROUND)
    label.next_to(plot_point(axes, np.log10(f[peak]), np.log10(h[peak])), UP, buff=0.12)
    label.shift(MASS_LABEL_SHIFT.get(M, ORIGIN))
    return label.set_z_index(Z_LABEL)


def redshift_key(axes, redshifts):
    rows = VGroup(*(
        VGroup(
            Line(ORIGIN, RIGHT * 0.45, stroke_color=merger_color(z),
                 stroke_width=GW_TRACK_WIDTH),
            MathTex(rf"z = {z:g}", font_size=FONT_TICK, color=PLOT_FOREGROUND),
        ).arrange(RIGHT, buff=0.15)
        for z in sorted(redshifts)
    )).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
    rows.next_to(plot_point(axes, LOG_F_RANGE[0], LOG_H_RANGE[0]), UR, buff=0.25)
    return rows.set_z_index(Z_LABEL)


class SensitivityBuildUp(Scene):
    # The mid-band detectors brought in last, in order, one step each.
    GAP_FILLERS = ("AION-10", "AION-100", "AION-km", "AEDGE")

    def beat(self):
        """The pause between steps; a click on the slide version."""
        self.wait(BEAT_HOLD)

    def bring_in(self, axes, *names):
        pieces = [detector(axes, name) for name in names]
        self.play(
            *(FadeIn(region) for region, _, _ in pieces),
            *(Create(curve) for _, curve, _ in pieces),
            *(FadeIn(label) for _, _, label in pieces),
            run_time=STEP_TIME,
        )

    def construct(self):
        axes, frame = sensitivity_axes(
            LOG_F_RANGE, LOG_H_RANGE, PLOT_ORIGIN, PLOT_WIDTH, PLOT_HEIGHT
        )

        # --- 1. LIGO and one merger ---------------------------------------
        first = merger(axes, *FIRST_MERGER, width=GW_TRACK_WIDTH)
        M, z = FIRST_MERGER
        first_label = MathTex(
            rf"{mass_tex(M)},\ z = {z:g}", font_size=FONT_TICK, color=merger_color(z)
        ).set_z_index(Z_LABEL)
        first_label.next_to(first.get_start(), UP, buff=0.15, aligned_edge=LEFT)
        self.play(FadeIn(frame), run_time=1.0)
        self.bring_in(axes, "LIGO")
        self.play(Create(first), FadeIn(first_label), run_time=STEP_TIME)
        self.beat()

        # --- 2. the other mergers -----------------------------------------
        others = VGroup(*(merger(axes, M, z) for M, z in MERGERS if (M, z) != FIRST_MERGER))
        nearest = min(z for _, z in MERGERS)
        masses = VGroup(*(mass_label(axes, M, z) for M, z in MERGERS if z == nearest))
        key = redshift_key(axes, {z for _, z in MERGERS})
        self.play(
            first.animate.set_stroke(width=GW_TRACK_CROWD_WIDTH),
            FadeOut(first_label),
            LaggedStart(*(Create(track) for track in others), lag_ratio=0.1),
            FadeIn(masses),
            FadeIn(key),
            run_time=2 * STEP_TIME,
        )
        self.beat()

        # --- 3. LISA, 4. ET -----------------------------------------------
        self.bring_in(axes, "LISA")
        self.beat()
        self.bring_in(axes, "ET")
        self.beat()

        # --- 5. the gap between them --------------------------------------
        bottom, top = LOG_H_RANGE
        edges = VGroup(*(
            DashedLine(
                plot_point(axes, np.log10(f), bottom), plot_point(axes, np.log10(f), top),
                **GW_BAND_EDGE_STYLE,
            ).set_z_index(Z_LABEL)
            for f in BAND_EDGES
        ))
        self.play(LaggedStart(*(Create(e) for e in edges), lag_ratio=0.3),
                  run_time=STEP_TIME)
        self.beat()

        # --- 6. onwards: what fills it -----------------------------------
        for i, name in enumerate(self.GAP_FILLERS):
            if i:
                self.beat()
            self.bring_in(axes, name)
        self.wait(2.0)
