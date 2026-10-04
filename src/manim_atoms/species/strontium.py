"""Strontium's levels and the lines a Sr experiment drives.

The singlet and triplet levels, the 461 nm cooling line, the 689 nm
narrow-line one and the 698 nm clock transition, the repump loop and the
488 nm transparency beam, and SrLevels, which draws them and lights the
arrow of whichever line is running.
"""

import numpy as np
from manim import *

from manim_atoms.style import *


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

# name, upper level, wavelength, colour, arrow start and end, which side of
# the arrow its label goes, and the natural linewidth Gamma / 2 pi written
# under the wavelength: the broad blue line that catches atoms, the narrow red
# one that cools them to a microkelvin, and the clock line (87Sr's 3P0 lives
# for minutes), some ten orders of magnitude apart.
TRANSITIONS = {
    "461": dict(upper=r"{}^1P_1", color=TRANSITION_461_COLOR, double=False,
                start=(-0.45, LV_GROUND), end=(-1.6, LV_1P1), side=LEFT,
                linewidth=r"30\,\mathrm{MHz}"),
    "689": dict(upper=r"{}^3P_1", color=TRANSITION_689_COLOR, double=False,
                start=(0.0, LV_GROUND), end=(1.9, LV_3P[1]), side=LEFT,
                linewidth=r"7.4\,\mathrm{kHz}",
                # further out: the arrow leans under its label, so at the
                # default the linewidth line runs into it
                label_buff=0.55),
    "698": dict(upper=r"{}^3P_0", color=TRANSITION_698_COLOR, double=True,
                start=(0.45, LV_GROUND), end=(2.3, LV_3P[0]), side=RIGHT,
                linewidth=r"{\sim}1\,\mathrm{mHz}"),
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
REPUMP_TRANSITIONS = {
    "679": dict(legs=[[(1.95, LV_3P[0]), (1.95, LV_3S1)]], color=REPUMP_COLOR,
                decay=False, label=r"679 + 707 nm", label_at=(1.7, 3.7), align=RIGHT),
    "707": dict(legs=[[(2.35, LV_3P[2]), (2.35, LV_3S1)]], color=REPUMP_COLOR,
                decay=False),
    "leak": dict(legs=[[(LV_1P1_X[1] + 0.05, LV_1P1 - 0.05), (-0.1, LV_1D2 + 0.05)],
                       [(0.4, LV_1D2 - 0.05), (LV_3P_X[0] - 0.05, LV_3P[2])]],
                 color=WHITE, decay=True),
    "return": dict(legs=[[(2.62, LV_3S1), (2.62, LV_3P[1])]], color=REPUMP_COLOR,
                   decay=True),
}

# The transparency beam, drawn only when asked for (the dipole-trap loading):
# 488 nm light near the 3P1 -> 3D2 line, whose light shift pulls 3P1 out of
# resonance with the 689 nm light for the atoms it covers. 3D2 is up and to
# the right of 3S1, so the arrow climbs clear of the repumps.
LV_3D2 = 5.3
LV_3D2_X = (2.95, 3.95)
TRANSPARENCY_TRANSITIONS = {
    "488": dict(legs=[[(2.8, LV_3P[1]), (3.3, LV_3D2)]], color=TRANSITION_488_COLOR,
                decay=False, label=r"488 nm", label_at=(3.3, 3.8), align=LEFT),
}


def _level(y, xs, color):
    return Line([xs[0], y, 0], [xs[1], y, 0], stroke_width=LEVEL_STROKE_WIDTH,
                color=color)


def _transition(key, color, width):
    spec = TRANSITIONS[key]
    cls = DoubleArrow if spec["double"] else Arrow
    arrow = cls(
        [*spec["start"], 0], [*spec["end"], 0], buff=0, color=color,
        stroke_width=width, tip_length=0.22, max_tip_length_to_length_ratio=0.12,
        max_stroke_width_to_length_ratio=20,
    )
    label = VGroup(
        Tex(f"{key} nm", font_size=FONT_LEGEND, color=color),
        MathTex(spec["linewidth"], font_size=FONT_LINEWIDTH, color=color),
    ).arrange(DOWN, buff=0.1, aligned_edge=-spec["side"])
    label.next_to(arrow.get_center(), spec["side"], buff=spec.get("label_buff", 0.3))
    return VGroup(arrow, label)


def _repump_transition(key, color, width, table=None):
    """A repump arrow, or a spontaneous decay drawn dashed along its path."""
    spec = (table or REPUMP_TRANSITIONS)[key]
    group = VGroup()
    for a, b in spec["legs"]:
        a, b = np.array([*a, 0.0]), np.array([*b, 0.0])
        if spec["decay"]:
            leg = DashedLine(a, b, dash_length=0.1, color=color, stroke_width=width)
            leg.add_tip(tip_length=0.2, tip_width=0.18)
        else:
            leg = Arrow(a, b, buff=0, color=color, stroke_width=width,
                        tip_length=0.22, max_tip_length_to_length_ratio=0.12,
                        max_stroke_width_to_length_ratio=20)
        group.add(leg)
    if spec.get("label"):
        group.add(Tex(spec["label"], font_size=FONT_LEGEND, color=color)
                  .move_to([*spec["label_at"], 0], aligned_edge=spec["align"]))
    return group


class SrLevels(VGroup):
    """The Sr levels the sequence uses, with its three transitions.

    Each transition is drawn twice: once in the construction grey, always
    there, and once over it in its own colour and heavier, shown only while
    a stage is driving it. ``repump=True`` adds the blue MOT's repump loop
    (REPUMP_TRANSITIONS), with 1D2 and 3S1; ``transparency=True`` adds the
    488 nm transparency beam (TRANSPARENCY_TRANSITIONS), with 3D2, and needs
    ``repump`` too, since it is laid out round it.
    """

    def __init__(self, repump=False, transparency=False, **kwargs):
        super().__init__(**kwargs)
        ground = _level(LV_GROUND, LV_GROUND_X, ATOM_COLOR)
        singlet = _level(LV_1P1, LV_1P1_X, OPTIC_COLOR)
        triplet = VGroup(*[
            _level(y, LV_3P_X, KICKED_COLOR if j == 0 else OPTIC_COLOR)
            for j, y in LV_3P.items()
        ])
        names = VGroup(
            MathTex(r"{}^1S_0", font_size=FONT_STATE, color=ATOM_COLOR)
            .next_to(ground, DOWN, buff=0.2),
            MathTex(r"{}^1P_1", font_size=FONT_STATE, color=OPTIC_COLOR)
            .next_to(singlet, UP, buff=0.2),
            MathTex(r"{}^3P_J", font_size=FONT_STATE, color=OPTIC_COLOR)
            .next_to(triplet, RIGHT if repump else UP, buff=0.55 if repump else 0.2),
        )
        j_labels = VGroup(*[
            MathTex(str(j), font_size=FONT_LEGEND,
                    color=KICKED_COLOR if j == 0 else OPTIC_COLOR)
            .next_to(line, RIGHT, buff=0.15)
            for j, line in zip(LV_3P, triplet)
        ])
        self.idle = {k: _transition(k, TRANSITION_IDLE_STYLE["color"],
                                    TRANSITION_IDLE_STYLE["stroke_width"])
                     for k in TRANSITIONS}
        self.active = {k: _transition(k, spec["color"], TRANSITION_ACTIVE_WIDTH)
                       .set_opacity(0)
                       for k, spec in TRANSITIONS.items()}
        self.add(ground, singlet, triplet, names, j_labels)
        if repump:
            d_level = _level(LV_1D2, LV_1D2_X, OPTIC_COLOR)
            s_level = _level(LV_3S1, LV_3S1_X, OPTIC_COLOR)
            self.add(
                d_level, s_level,
                MathTex(r"{}^1D_2", font_size=FONT_STATE, color=OPTIC_COLOR)
                .next_to(d_level, DOWN, buff=0.2),
                MathTex(r"{}^3S_1", font_size=FONT_STATE, color=OPTIC_COLOR)
                .next_to(s_level, UP, buff=0.2),
            )
            for k, spec in REPUMP_TRANSITIONS.items():
                self.idle[k] = _repump_transition(
                    k, TRANSITION_IDLE_STYLE["color"], TRANSITION_IDLE_STYLE["stroke_width"])
                self.active[k] = _repump_transition(
                    k, spec["color"], TRANSITION_ACTIVE_WIDTH).set_opacity(0)
        if transparency:
            level = _level(LV_3D2, LV_3D2_X, OPTIC_COLOR)
            self.add(level, MathTex(r"{}^3D_2", font_size=FONT_STATE, color=OPTIC_COLOR)
                     .next_to(level, UP, buff=0.2))
            table = TRANSPARENCY_TRANSITIONS
            for k, spec in table.items():
                self.idle[k] = _repump_transition(
                    k, TRANSITION_IDLE_STYLE["color"], TRANSITION_IDLE_STYLE["stroke_width"],
                    table)
                self.active[k] = _repump_transition(
                    k, spec["color"], TRANSITION_ACTIVE_WIDTH, table).set_opacity(0)
        self.add(*self.idle.values(), *self.active.values())

    def drive(self, *keys):
        """Animations lighting the transitions ``keys`` and putting out the rest."""
        return [group.animate.set_opacity(1 if k in keys else 0)
                for k, group in self.active.items()]
