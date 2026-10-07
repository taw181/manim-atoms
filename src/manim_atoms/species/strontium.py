"""Strontium as a species (species.scheme): its levels and the lines a Sr
experiment drives.

The singlet and triplet levels, the 461 nm cooling line, the 689 nm
narrow-line one and the 698 nm clock transition, the repump loop and the
488 nm transparency beam, all as STRONTIUM; and SrLevels, its level scheme,
which lights the arrow of whichever line is running.
"""

from fractions import Fraction

import numpy as np
from manim import *

from manim_atoms.style import *
from manim_atoms.species.scheme import (
    Extra,
    Level,
    LevelScheme,
    Manifold,
    Path,
    Species,
    Transition,
)

# --- the lines' colours ---------------------------------------------------
# The transitions take the hues of the usual Sr level diagram -- blue for the
# 461 nm line, red for 689 nm, which is what makes the red MOT red. The clock
# line is the interferometer's laser and so keeps the laser red it has
# everywhere else; that is a salmon red, so 689 nm takes a pure, deeper one,
# which keeps the two lines apart when they sit side by side.
TRANSITION_461_COLOR = ManimColor("#5b7cff")
TRANSITION_689_COLOR = ManimColor("#f01c24")
TRANSITION_698_COLOR = LASER_COLOR
# The transparency beam light-shifts a level out of the 689 light's reach;
# 488 nm is blue-green, and green is the one hue the other lines leave free.
TRANSITION_488_COLOR = GREEN_C
# The blue MOT's two repumps (679 and 707 nm), which are always on together
# and so share one hue: amber, which samples clear of the 461 blue, the 689
# magenta and the clock line's laser red.
REPUMP_COLOR = ManimColor("#f5b400")


# --- the Sr level scheme --------------------------------------------------
# Schematic, not to scale: the fine-structure splitting of 3P_J is spread out
# to fit a label beside each line. 1S0 and 3P0 take the ground and excited
# state colours, since they are the |g> and |e> of every interferometer
# figure in the talk.
LV_GROUND = 0.0
LV_1P1 = 3.3
LV_3P = {0: 1.95, 1: 2.3, 2: 2.65}
LV_GROUND_X = (-0.9, 0.9)
LV_1P1_X = (-2.3, -1.1)
LV_3P_X = (1.75, 2.9)

# The three lines: the broad blue one that catches atoms, the narrow red
# one that cools them to a microkelvin, and the clock line (87Sr's 3P0 lives
# for minutes), their natural linewidths Gamma / 2 pi some ten orders of
# magnitude apart. Each arrow's start and end, and which side of it its
# label goes, are in the diagram's own coordinates.
TRANSITIONS = {
    "461": Transition("461", "1S0", "1P1", TRANSITION_461_COLOR,
                      start=(-0.45, LV_GROUND), end=(-1.6, LV_1P1), side=LEFT,
                      linewidth=r"30\,\mathrm{MHz}"),
    "689": Transition("689", "1S0", "3P", TRANSITION_689_COLOR,
                      start=(0.0, LV_GROUND), end=(1.9, LV_3P[1]), side=LEFT,
                      linewidth=r"7.4\,\mathrm{kHz}", upper_j=1,
                      # further out: the arrow leans under its label, so at
                      # the default the linewidth line runs into it
                      label_buff=0.55,
                      # the sawtooth of its sweep, in the gap left of 3P_J
                      fan_at=(0.55, 1.95)),
    "698": Transition("698", "1S0", "3P", TRANSITION_698_COLOR,
                      start=(0.45, LV_GROUND), end=(2.3, LV_3P[0]), side=RIGHT,
                      linewidth=r"{\sim}1\,\mathrm{mHz}", double=True, upper_j=0),
}


# The repump loop, drawn only when asked for (the cooling cartoon): a 1P1 atom
# now and then decays through 1D2 into 3P2, which the blue MOT can't see, and
# 707 nm and 679 nm light lift it from 3P2 and 3P0 to 3S1, from where it falls
# back through 3P1 to the ground state. The two repumps are always on
# together, so they share a colour and one label, on the far side of them
# from the stack so the right-hand side stays free for 3D2. 3S1 sits right
# over the triplet stack so the repump arrows run straight up through it,
# which moves the 3P_J name to the side of the stack, out of their way.
LV_1D2 = 2.85
LV_3S1 = 4.35
LV_1D2_X = (-0.35, 0.65)
LV_3S1_X = LV_3P_X
#
# Each path is a list of legs, a leg a straight run between two points. A
# decay is dashed and in white when lit: it is the atom's doing, not a beam's.
REPUMP = Extra(
    levels={
        "1D2": Level(r"{}^1D_2", LV_1D2, LV_1D2_X, name_side=DOWN),
        "3S1": Level(r"{}^3S_1", LV_3S1, LV_3S1_X, name_side=UP),
    },
    paths={
        "679": Path([[(1.95, LV_3P[0]), (1.95, LV_3S1)]], REPUMP_COLOR,
                    label=r"679 + 707 nm", label_at=(1.7, 3.7), align=RIGHT),
        "707": Path([[(2.35, LV_3P[2]), (2.35, LV_3S1)]], REPUMP_COLOR),
        "leak": Path([[(LV_1P1_X[1] + 0.05, LV_1P1 - 0.05), (-0.1, LV_1D2 + 0.05)],
                      [(0.4, LV_1D2 - 0.05), (LV_3P_X[0] - 0.05, LV_3P[2])]],
                     WHITE, decay=True),
        "return": Path([[(2.62, LV_3S1), (2.62, LV_3P[1])]], REPUMP_COLOR, decay=True),
    },
)

# The transparency beam, drawn only when asked for (the dipole-trap loading):
# 488 nm light near the 3P1 -> 3D2 line, whose light shift pulls 3P1 out of
# resonance with the 689 nm light for the atoms it covers. 3D2 is up and to
# the right of 3S1, so the arrow climbs clear of the repumps.
LV_3D2 = 5.3
LV_3D2_X = (2.95, 3.95)
TRANSPARENCY = Extra(
    levels={"3D2": Level(r"{}^3D_2", LV_3D2, LV_3D2_X, name_side=UP)},
    paths={
        "488": Path([[(2.8, LV_3P[1]), (3.3, LV_3D2)]], TRANSITION_488_COLOR,
                    label=r"488 nm", label_at=(3.3, 3.8), align=LEFT),
    },
)

STRONTIUM = Species(
    name="strontium", symbol="Sr", isotope=r"{}^{87}\mathrm{Sr}",
    levels={
        "1S0": Level(r"{}^1S_0", LV_GROUND, LV_GROUND_X, ATOM_COLOR, name_side=DOWN),
        "1P1": Level(r"{}^1P_1", LV_1P1, LV_1P1_X, name_side=UP),
        "3P": Manifold(r"{}^3P_J", LV_3P, LV_3P_X, colors={0: KICKED_COLOR},
                       name_side_with={"repump": (RIGHT, 0.55)}),
    },
    transitions=TRANSITIONS,
    extras={"repump": REPUMP, "transparency": TRANSPARENCY},
    roles={"cooling": "461", "narrow": "689", "clock": "698", "push": "461",
           "imaging": "461", "transparency": "488", "repump": ("679", "707")},
    spin=Fraction(9, 2),
)


class SrLevels(LevelScheme):
    """The Sr levels the sequence uses, with its three transitions: the
    level scheme of STRONTIUM.

    ``repump=True`` adds the blue MOT's repump loop, with 1D2 and 3S1;
    ``transparency=True`` adds the 488 nm transparency beam, with 3D2, and
    needs ``repump`` too, since it is laid out round it.
    """

    def __init__(self, repump=False, transparency=False, **kwargs):
        extras = [name for name, on in (("repump", repump), ("transparency", transparency)) if on]
        super().__init__(STRONTIUM, extras, **kwargs)
