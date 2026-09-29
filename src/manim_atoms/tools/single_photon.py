"""The Sr clock transition, drawn as a two-level system beside a figure."""

import numpy as np
from manim import *

from aionanim.style import *
from aionanim.tools.primitives import (
    state_label,
)


# --- the clock transition, drawn as a two-level system --------------------
# What makes AION a *single-photon* interferometer is that the transition it
# drives is narrow: in strontium the 1S0 -> 3P0 clock line at 698 nm has a
# natural linewidth of order millihertz, so an atom parked in |e> stays there
# for the whole interrogation time. Elsewhere a pair of Raman photons is
# needed to leave the atom in a long-lived ground-state sublevel; here one
# photon does the work, and the laser's phase is written into the atom once
# per pulse instead of twice.
#
# The diagram sits upper left and doubles as the figure's key: |g> carries
# ATOM_COLOR and |e> carries KICKED_COLOR, which are the colours the two arms
# are drawn in, so it says everything a separate legend would and also says
# what the pulses are resonant with. Upper left is the one corner it can sit
# in -- the mirror's emitted photons climb the column x = MZ_B[0] and out of
# the top of the frame, and the title already occupies the right.
SP_LEVELS = np.array([-5.5, 2.05, 0.0])  # centre of the gap
SP_LEVEL_LENGTH = 1.6
SP_LEVEL_GAP = 1.6  # vertical separation of the two levels
SP_LEVEL_INSET = 0.1  # how far the gap arrow stands off each level line
SP_KET_BUFF = 0.2


def make_level_diagram(center=SP_LEVELS):
    """The Sr clock transition as a two-level system, with the gap labelled.

    |g> and |e> are the atom's internal states only -- the momentum a photon
    hands over lives in the interferometer beside it, not in here. The gap is
    written as the photon's energy, hbar c k, to tie it to the hbar k recoil.
    """
    half = RIGHT * SP_LEVEL_LENGTH / 2
    lower = center + DOWN * SP_LEVEL_GAP / 2
    upper = center + UP * SP_LEVEL_GAP / 2

    level_g = Line(
        lower - half, lower + half, color=ATOM_COLOR, stroke_width=LEVEL_STROKE_WIDTH
    )
    level_e = Line(
        upper - half, upper + half, color=KICKED_COLOR, stroke_width=LEVEL_STROKE_WIDTH
    )
    ket_g = state_label(r"|g\rangle", ATOM_COLOR).next_to(
        level_g, RIGHT, buff=SP_KET_BUFF
    )
    ket_e = state_label(r"|e\rangle", KICKED_COLOR).next_to(
        level_e, RIGHT, buff=SP_KET_BUFF
    )

    gap = DoubleArrow(
        lower + UP * SP_LEVEL_INSET,
        upper + DOWN * SP_LEVEL_INSET,
        **LEVEL_GAP_ARROW_STYLE,
    )
    gap_label = MathTex(
        r"\hbar c k", font_size=FONT_ANNOTATION, color=lighten(GUIDE_COLOR)
    ).next_to(gap, RIGHT, buff=0.15)

    return VGroup(level_g, level_e, ket_g, ket_e, gap, gap_label)


def transition_glow(upward=True, center=SP_LEVELS):
    """The transition lit up in the laser's colour while a pulse drives it.

    Up while a photon is being absorbed, down at the mirror, where the excited
    arm is stimulated back to |g>. It is the same energy gap either way, so
    the glow is drawn over the gap arrow rather than beside it.
    """
    lower = center + DOWN * (SP_LEVEL_GAP / 2 - SP_LEVEL_INSET)
    upper = center + UP * (SP_LEVEL_GAP / 2 - SP_LEVEL_INSET)
    start, end = (lower, upper) if upward else (upper, lower)
    return Arrow(start, end, **LEVEL_GLOW_ARROW_STYLE)
