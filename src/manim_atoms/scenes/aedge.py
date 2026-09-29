"""AEDGE: the same instrument in space, on both of the talk's plots at once.

The gravitational-wave landscape (the detectors of SensitivityBuildUp, without
the merger tracks) and the ultralight dark-matter photon coupling (the
insets' panel, drawn full size) side by side, each as the talk has already
shown it: LIGO, LISA, ET and AION's three stages on the one, AION's stages
against today's limits on the other. Then AEDGE goes onto both in one step.
A baseline of ~4e7 m between two satellites moves the gravitational-wave
reach down in frequency, between LISA and the ground, and the dark-matter
reach down in mass, where the ground stages do not go at all.

    uv run manim -ql src/aionanim/scenes/aedge.py AEDGESensitivity

The one pause, before AEDGE arrives, goes through beat().
"""

import numpy as np
from manim import *

from aionanim.style import *
from aionanim.tools.gw_plot import detector_region, plot_point, sensitivity_axes
from aionanim.tools.layout import slide_title
from aionanim.tools.uldm_plot import (
    ULDM_LABEL_EVERY,
    ULDM_LOG_D,
    ULDM_LOG_M,
    excluded_label,
    excluded_region,
    uldm_curves,
)

# --- layout ---------------------------------------------------------------
# Two panels, each an axes' lower-left corner and size, left for the waves
# and right for the dark matter, clear of the frame edge on the right (its
# last tick label hangs past the axes). Their tick labels and rotated axis
# labels take ~1.3 units left of each axes, which is what the gap is for.
AE_GW_ORIGIN = np.array([-5.3, -2.45, 0.0])
AE_ULDM_ORIGIN = np.array([1.55, -2.45, 0.0])
AE_PANEL_WIDTH = 5.0
AE_PANEL_HEIGHT = 4.6
AE_PANEL_TITLE_BUFF = 0.25

# The gravitational-wave panel: SensitivityBuildUp's frame.
AE_LOG_F = (-6, 4)
AE_LOG_H = (-24, -14.5)
# name: (CSV stem, label anchor (log f, log h), side the label hangs off it).
# Placed for this panel's size rather than taken from SensitivityBuildUp's,
# which are set for a plot twice as wide.
AE_GW_DETECTORS = {
    "LIGO": ("ligo", (1.1, -21.0), RIGHT),
    "LISA": ("lisa", (-3.0, -21.6), ORIGIN),
    "ET": ("et", (2.3, -23.5), ORIGIN),
    "AION-10": ("aion_10", (-0.45, -15.3), DOWN),
    "AION-100": ("aion_100", (2.1, -16.6), ORIGIN),
    "AION-km": ("aion_km", (2.1, -18.9), ORIGIN),
    "AEDGE": ("aedge", (-1.1, -23.2), ORIGIN),
}
AE_GW_BEFORE = ("LISA", "LIGO", "ET", "AION-10", "AION-100", "AION-km")

# The dark-matter panel: the insets' frame and curves.
# name: (stems, label anchor (log m, log d_e), side).
AE_ULDM_STAGES = {
    # in the V of their goal curves, as in the insets (tools/uldm_plot.py)
    "AION-10": (("aion10_goal",), (-15.7, -1.9), ORIGIN),
    "AION-100": (("aion100_goal",), (-15.8, -5.6), ORIGIN),
    "AION-km": (("aion_km",), (-13.2, -9.0), RIGHT),
    "AEDGE": (("aedge",), (-16.2, -13.4), DR),
}

# The grey region's name, over AION-10's label in the V of its curve: this
# panel has the height for both there, which the insets do not.
AE_EXCLUDED_LABEL = (-15.4, -0.65)

AE_STEP_TIME = 1.5


def gw_detector(axes, name):
    """(region, curve, label) for one detector, sized for this panel."""
    stem, (lf, lh), side = AE_GW_DETECTORS[name]
    color = GW_DETECTOR_COLORS[name]
    region, curve = detector_region(axes, stem, color)
    label = Tex(name, font_size=FONT_TICK, color=color)
    label.next_to(plot_point(axes, lf, lh), side, buff=0)
    return region, curve, label


def uldm_stage(axes, curves, name):
    """(curves, label) for one stage of the dark-matter panel."""
    stems, (lm, ld), side = AE_ULDM_STAGES[name]
    label = Tex(name, font_size=FONT_TICK, color=ULDM_COLORS[stems[-1]])
    label.next_to(plot_point(axes, lm, ld), side, buff=0)
    return VGroup(*(curves[s] for s in stems)), label


class AEDGESensitivity(Scene):
    """The talk's two sensitivity plots, then AEDGE on both."""

    TITLE = r"AEDGE: Atom interferometry in space"

    def beat(self):
        """The pause before AEDGE: a click on the slide version."""
        self.wait(1.5)

    def construct(self):
        title = slide_title(self.TITLE)

        # --- gravitational waves ------------------------------------------
        gw_axes, gw_frame = sensitivity_axes(
            AE_LOG_F, AE_LOG_H, AE_GW_ORIGIN, AE_PANEL_WIDTH, AE_PANEL_HEIGHT,
            label_every=(2, 2),
        )
        gw = {name: gw_detector(gw_axes, name) for name in AE_GW_DETECTORS}
        gw_title = Tex(r"Gravitational waves", font_size=FONT_AXIS)
        gw_title.next_to(gw_axes, UP, buff=AE_PANEL_TITLE_BUFF)

        # --- ultralight dark matter ---------------------------------------
        dm_axes, dm_frame = sensitivity_axes(
            ULDM_LOG_M, ULDM_LOG_D, AE_ULDM_ORIGIN, AE_PANEL_WIDTH, AE_PANEL_HEIGHT,
            x_label=r"$m_\phi$ / eV", y_label=r"photon coupling $|d_e|$",
            label_every=ULDM_LABEL_EVERY,
        )
        curves = uldm_curves(dm_axes)
        dm = {name: uldm_stage(dm_axes, curves, name) for name in AE_ULDM_STAGES}
        excluded = excluded_region(dm_axes)
        excluded_name = excluded_label(dm_axes, FONT_TICK, AE_EXCLUDED_LABEL, ORIGIN)
        dm_title = Tex(r"Ultralight dark matter", font_size=FONT_AXIS)
        dm_title.next_to(dm_axes, UP, buff=AE_PANEL_TITLE_BUFF)

        # --- what the talk has shown so far ---------------------------------
        before = [
            *(m for name in AE_GW_BEFORE for m in gw[name]),
            excluded,
            *(m for name, piece in dm.items() if name != "AEDGE" for m in piece),
            excluded_name,  # over the curves
        ]
        self.play(
            FadeIn(title), FadeIn(gw_frame), FadeIn(gw_title),
            FadeIn(dm_frame), FadeIn(dm_title), *(FadeIn(m) for m in before),
            run_time=1.0,
        )
        self.beat()

        # --- AEDGE, on both --------------------------------------------------
        region, curve, label = gw["AEDGE"]
        dm_curve, dm_label = dm["AEDGE"]
        self.play(
            FadeIn(region), Create(curve), FadeIn(label),
            Create(dm_curve), FadeIn(dm_label),
            run_time=AE_STEP_TIME,
        )
        self.wait(2.0)
