"""Ytterbium as a species (species.scheme): its levels and the lines a Yb
experiment drives.

Ytterbium has strontium's structure -- an alkaline-earth-like singlet and
triplet, a broad blue line that catches atoms, a narrow intercombination
line that cools them, and a clock line to 3P0 -- with its own wavelengths
and widths: 399 nm (29 MHz), 556 nm (182 kHz) and 578 nm. Its broad line
leaks too little to need a repump in a MOT, so it has no repump loop. In
171Yb the ground state's spin is F = 1/2. YbLevels is its level scheme.

The level heights are schematic, as Sr's are: the fine-structure splitting of
3P_J is spread out to fit a label beside each line.
"""

from fractions import Fraction

import numpy as np
from manim import *

from manim_atoms.style import *
from manim_atoms.species.scheme import Level, LevelScheme, Manifold, Species, Transition

# --- the lines' colours ---------------------------------------------------
# Each line in (roughly) its own hue: 399 nm is violet, 556 nm green and the
# 578 nm clock line yellow -- three hues that sample apart from each other and
# from the ground and excited state colours they connect.
TRANSITION_399_COLOR = ManimColor("#9a6bff")
TRANSITION_556_COLOR = ManimColor("#3fcf5a")
TRANSITION_578_COLOR = ManimColor("#f2c200")

# --- the Yb level scheme --------------------------------------------------
# Laid out as Sr's is, so the two read as the same kind of atom.
YB_GROUND = 0.0
YB_1P1 = 3.3
YB_3P = {0: 1.95, 1: 2.3, 2: 2.65}
YB_GROUND_X = (-0.9, 0.9)
YB_1P1_X = (-2.3, -1.1)
YB_3P_X = (1.75, 2.9)

# The broad violet line that catches atoms, the narrow green one that cools
# them to some ten microkelvin, and the clock line: 171Yb's 3P0 lives for
# about twenty seconds.
YB_TRANSITIONS = {
    "399": Transition("399", "1S0", "1P1", TRANSITION_399_COLOR,
                      start=(-0.45, YB_GROUND), end=(-1.6, YB_1P1), side=LEFT,
                      linewidth=r"29\,\mathrm{MHz}"),
    "556": Transition("556", "1S0", "3P", TRANSITION_556_COLOR,
                      start=(0.0, YB_GROUND), end=(1.9, YB_3P[1]), side=LEFT,
                      linewidth=r"182\,\mathrm{kHz}", upper_j=1, label_buff=0.55,
                      fan_at=(0.55, 1.95)),
    "578": Transition("578", "1S0", "3P", TRANSITION_578_COLOR,
                      start=(0.45, YB_GROUND), end=(2.3, YB_3P[0]), side=RIGHT,
                      linewidth=r"{\sim}7\,\mathrm{mHz}", double=True, upper_j=0),
}

YTTERBIUM = Species(
    name="ytterbium", symbol="Yb", isotope=r"{}^{171}\mathrm{Yb}",
    levels={
        "1S0": Level(r"{}^1S_0", YB_GROUND, YB_GROUND_X, ATOM_COLOR, name_side=DOWN),
        "1P1": Level(r"{}^1P_1", YB_1P1, YB_1P1_X, name_side=UP),
        "3P": Manifold(r"{}^3P_J", YB_3P, YB_3P_X, colors={0: KICKED_COLOR}),
    },
    transitions=YB_TRANSITIONS,
    roles={"cooling": "399", "narrow": "556", "clock": "578", "push": "399",
           "imaging": "399"},
    spin=Fraction(1, 2),
)


class YbLevels(LevelScheme):
    """The Yb levels, with its three transitions: the level scheme of
    YTTERBIUM."""

    def __init__(self, **kwargs):
        super().__init__(YTTERBIUM, **kwargs)
