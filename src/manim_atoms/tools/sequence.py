"""One shot of the experiment: the stages, the Sr levels they drive, the timeline.

The sequence goes from a blue MOT through two red MOTs, a pair of dipole
traps and state preparation, to the differential interferometer and its
readout. Each stage is tagged with the transition it drives (if any), the
stretch of the imaging video that shows it (if any) and the paper it is
written up in (if any), and the helpers below turn that table into a Sr
level diagram whose arrows light up, a timeline whose blocks do, and a
reference list whose entries do.
"""

from dataclasses import dataclass

import numpy as np
from manim import *

from aionanim.style import *


# --- the papers each part of the sequence is written up in ----------------
REFERENCES = [
    r"B.~Stray \emph{et al.}, AVS Quantum Sci.\ \textbf{6}, 014409 (2024),"
    r" doi:10.1116/5.0172731",
    r"E.~Pasatembou \emph{et al.}, AVS Quantum Sci.\ \textbf{6}, 014408 (2024),"
    r" doi:10.1116/5.0180043",
    r"C.~F.~A.~Baynham \emph{et al.}, Nature \textbf{654}, 622--628 (2026),"
    r" doi:10.1038/s41586-026-10617-1",
]


# --- the imaging video ----------------------------------------------------
# 48 snapshots of the cloud from t = 10 ms to 599 ms, each held for four
# frames. The burnt-in "t = ... ms" is unreadable once the video is shrunk
# into a corner, so it is cropped off along with the dark frame round the
# image and a strip of empty field, and the scene draws its own clock
# instead.
IMAGING_VIDEO = ("videos", "midway_imaging_b059528_slow.mp4")
IMAGING_FRAMES_PER_SNAPSHOT = 4
IMAGING_CROP = (100, 683, 50, 633)  # top, bottom, left, right in pixels
IMAGING_T0_MS = 10.0
IMAGING_DT_MS = (599.0 - IMAGING_T0_MS) / 47


def snapshot_index(t_ms):
    """Which snapshot shows the cloud at ``t_ms``: the last one taken by then."""
    return int(np.floor((t_ms - IMAGING_T0_MS) / IMAGING_DT_MS + 1e-9))


def snapshot_ms(t_ms):
    """When the snapshot showing the cloud at ``t_ms`` was taken."""
    return IMAGING_T0_MS + max(snapshot_index(t_ms), 0) * IMAGING_DT_MS


# --- the stages -----------------------------------------------------------
@dataclass(frozen=True)
class Stage:
    key: str  # into SEQUENCE_STAGE_COLORS
    label: str  # Tex; "\\" breaks the line
    transition: str | None = None  # into TRANSITIONS
    video_ms: tuple[float, float] | None = None  # the stretch of the imaging it spans
    reference: int | None = None  # into REFERENCES


# The video boundaries are read off the snapshots: the blue MOT loads until
# about 48 ms, and by 60 ms the cloud has dropped some 30 px with the same
# atom number, which is the red MOT taking over; the cloud starts to shrink
# between 123 and 135 ms, the upper trap's line shows inside it from 173 ms,
# the MOT is let go between 223 and 236 ms and falls into the lower trap,
# which has finished loading by 286 ms.
STAGES = [
    Stage("blue_mot", r"Blue MOT", "461", (IMAGING_T0_MS, 54.0), 0),
    Stage("modulated_red_mot", r"Modulated\\red MOT", "689", (54.0, 129.0), 1),
    Stage("narrowband_red_mot", r"Narrowband\\red MOT", "689", (129.0, 179.0), 1),
    Stage("upper_dipole_trap", r"Upper\\dipole trap", None, (179.0, 229.0)),
    Stage("lower_dipole_trap", r"Lower\\dipole trap", None, (229.0, 310.0)),
    Stage("spin_polarization", r"Spin\\polarization", "689"),
    Stage("velocity_slicing", r"Velocity\\slicing", "698"),
    Stage("differential_interferometry", r"Differential\\interferometry", "698", reference=2),
    Stage("state_readout", r"State\\readout", "461", reference=2),
]
# the break in the timeline between preparing the atoms and using them
TIMELINE_BREAK_AFTER = 5


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
                linewidth=r"7.4\,\mathrm{kHz}"),
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
    label.next_to(arrow.get_center(), spec["side"], buff=0.3)
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


# --- the timeline ---------------------------------------------------------
TL_BLOCK_WIDTH = 1.38
TL_BLOCK_HEIGHT = 0.42
TL_SPACING = 0.06
TL_BREAK = 0.45  # extra room at TIMELINE_BREAK_AFTER
TL_LABEL_BUFF = 0.15


def _block_opacity(j, active):
    if j == active:
        return 1.0
    return TIMELINE_DONE_OPACITY if j < active else TIMELINE_AHEAD_OPACITY


class Timeline(VGroup):
    """A row of coloured blocks, one per stage, with the label under each.

    ``activate(i)`` animates stage i to lit and ringed, everything before it
    to half lit and everything after it to faint.
    """

    def __init__(self, stages=STAGES, **kwargs):
        super().__init__(**kwargs)
        self.blocks = VGroup()
        x = 0.0
        for j, stage in enumerate(stages):
            fill, edge = SEQUENCE_STAGE_COLORS[stage.key]
            block = Rectangle(width=TL_BLOCK_WIDTH, height=TL_BLOCK_HEIGHT,
                              fill_color=fill, stroke_color=edge, stroke_width=3)
            block.move_to([x + TL_BLOCK_WIDTH / 2, 0, 0])
            self.blocks.add(block)
            x += TL_BLOCK_WIDTH + TL_SPACING + (TL_BREAK if j == TIMELINE_BREAK_AFTER else 0)
        self.labels = VGroup(*[
            Tex(s.label, font_size=FONT_TIMELINE, color=PLOT_FOREGROUND)
            .next_to(b, DOWN, buff=TL_LABEL_BUFF)
            for s, b in zip(stages, self.blocks)
        ])
        self.ring = SurroundingRectangle(
            self.blocks[0], buff=0.06, stroke_width=TIMELINE_ACTIVE_RING["width"],
            color=TIMELINE_ACTIVE_RING["color"],
        ).set_stroke(opacity=0)
        self.add(self.blocks, self.labels, self.ring)
        self._show(active=-1)

    def _show(self, active):
        for j, (block, label) in enumerate(zip(self.blocks, self.labels)):
            op = _block_opacity(j, active)
            block.set_fill(opacity=op).set_stroke(opacity=op)
            label.set_opacity(0.5 + 0.5 * op)

    def activate(self, i):
        anims = []
        for j, (block, label) in enumerate(zip(self.blocks, self.labels)):
            if j not in (i - 1, i):
                continue
            op = _block_opacity(j, i)
            anims += [block.animate.set_fill(opacity=op).set_stroke(opacity=op),
                      label.animate.set_opacity(0.5 + 0.5 * op)]
        anims.append(self.ring.animate.move_to(self.blocks[i]).set_stroke(opacity=1))
        return anims


class References(VGroup):
    """A brace under each run of stages a paper covers, numbered, and the
    numbered list of papers below. The one covering the running stage is lit.
    """

    def __init__(self, timeline, stages=STAGES, refs=REFERENCES, **kwargs):
        super().__init__(**kwargs)
        floor = timeline.labels.get_bottom()[1]
        self.marks = VGroup()
        for n in range(len(refs)):
            cover = [b for s, b in zip(stages, timeline.blocks) if s.reference == n]
            span = Line([cover[0].get_left()[0], floor, 0],
                        [cover[-1].get_right()[0], floor, 0])
            brace = Brace(span, DOWN, buff=0.1, sharpness=3, color=lighten(GUIDE_COLOR))
            number = Tex(f"[{n + 1}]", font_size=FONT_REFERENCE,
                         color=PLOT_FOREGROUND).next_to(brace, DOWN, buff=0.08)
            self.marks.add(VGroup(brace, number))
        self.entries = VGroup(*[
            # \mbox: Tex's default environment would wrap a line this long
            Tex(rf"\mbox{{[{n + 1}] {ref}}}", font_size=FONT_REFERENCE,
                color=PLOT_FOREGROUND)
            for n, ref in enumerate(refs)
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        self.entries.next_to(self.marks, DOWN, buff=0.2).align_to(timeline, LEFT)
        self.add(self.marks, self.entries)
        for n in range(len(refs)):
            self._pair(n).set_opacity(REFERENCE_IDLE_OPACITY)

    def _pair(self, n):
        return VGroup(self.marks[n], self.entries[n])

    def cite(self, n):
        """Animations lighting reference ``n`` (None for none) and dimming the rest."""
        return [self._pair(k).animate.set_opacity(1 if k == n else REFERENCE_IDLE_OPACITY)
                for k in range(len(self.entries))]


def stage_heading(stage):
    """The running stage's name, and the transition it drives, in big type."""
    name = Tex(stage.label, font_size=FONT_TITLE + 8)
    if stage.transition is None:
        return VGroup(name)
    spec = TRANSITIONS[stage.transition]
    line = MathTex(
        rf"{stage.transition}\,\mathrm{{nm}}:\ {{}}^1S_0 \rightarrow {spec['upper']}",
        font_size=FONT_ANNOTATION, color=spec["color"],
    )
    return VGroup(name, line).arrange(DOWN, buff=0.3)
