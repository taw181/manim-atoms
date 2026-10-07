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

from manim_atoms.trapping.style import *
from manim_atoms.species.strontium import TRANSITIONS


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
    """One stage of the sequence: its colour key, its label, and, where it has them, the
    transition it drives, the stretch of imaging video that shows it and the paper
    that covers it."""
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


def caption(text, heading):
    """A grey caption under ``heading``, left-aligned with it."""
    return Tex(text, font_size=FONT_CAPTION, color=lighten(GUIDE_COLOR)).next_to(
        heading, DOWN, buff=0.3, aligned_edge=LEFT
    )
