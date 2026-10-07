"""Large momentum transfer: more photon recoils, arms further apart.

After Rudolph et al., PRL 124, 083604 (2020). LargeMomentumTransfer is the
ladder on its own: ten kicks, each after the first driving both arms apart.
LMTMachZehnder puts it to use (their Fig. 1c), stretching each pulse of the
pi/2 - pi - pi/2 sequence into many, beside the plain N = 1 interferometer it
replaces.
"""

import numpy as np
from manim import *

from manim_atoms.interferometry.style import *
from manim_atoms.interferometry.tools.lmt import (
    LMT_KICKS,
    LMT_STEP,
    LMT_T0,
    LMT_TAIL,
    LMT_U,
    LMT_Z,
    LMZ_END,
    LMZ_ORDER,
    LMZ_PORT,
    LMZ_STEP,
    LMZ_T,
    LMZ_T0,
    LMZ_U,
    LMZ_Z,
    lmt_ladder_pulses,
    lmz_pulses,
)
from manim_atoms.interferometry.tools.pulse_sequence import play_sequence, run_sequence
from manim_atoms.core.primitives import make_atom


class LargeMomentumTransfer(Scene):
    """A ladder of single-photon kicks separates the arms by N hbar k."""

    def beat(self):
        """The pause after each step: nothing here, a click on the slide version."""

    def construct(self):
        title = Tex(
            r"Large momentum transfer: $N\hbar k$ from single-photon kicks",
            font_size=FONT_TITLE,
        ).to_corner(UL)
        note = Tex(
            r"colour is the internal state; slope is momentum",
            font_size=FONT_LEGEND,
            color=lighten(GUIDE_COLOR),
        ).next_to(title, DOWN, buff=0.2).align_to(title, LEFT)
        self.play(FadeIn(title), FadeIn(note), run_time=0.9)

        # the first kick (the pi/2) moves the upper arm only; every one after
        # it drives both, pushing them apart by 2 hbar k. Kicks alternate
        # direction: the upper arm absorbs an upward photon, then emits into a
        # downward one, so either way it is pushed up by hbar k, and the lower
        # arm, always in the other state, is pushed down by the same pulses.
        seq = run_sequence(lmt_ladder_pulses(), (LMT_T0, LMT_Z), LMT_U,
                           until=LMT_T0 + (LMT_KICKS - 1) * LMT_STEP + LMT_TAIL)
        upper_pts, lower_pts = seq.paths["1"], seq.paths["0"]

        # --- the atom arrives ---------------------------------------------
        atom = make_atom().move_to([-config.frame_x_radius + 0.3, LMT_Z, 0])
        self.play(FadeIn(atom, scale=0.5), run_time=0.4)
        self.play(
            atom.animate.move_to(upper_pts[0]),
            rate_func=linear,
            run_time=(LMT_T0 - atom.get_center()[0]) / V,
        )
        self.beat()

        # --- the ladder: the first two kicks at full pace, the rest quicker;
        # one kick explained, then the rest of the ladder runs on
        play_sequence(
            self, seq, {"": atom},
            span=(-config.frame_y_radius, note.get_bottom()[1] - 0.15),
            ray_time=0.45, flash_time=0.4, fast_after=2,
            after_step=lambda step, k: self.beat() if k == 0 else None,
        )
        self.beat()

        # --- what the ladder bought -----------------------------------------
        # A single kick, drawn for the same total time, for comparison.
        single = DashedLine(
            upper_pts[0],
            upper_pts[0] + np.array([
                upper_pts[-1][0] - upper_pts[0][0],
                (upper_pts[-1][0] - upper_pts[0][0]) * LMT_U,
                0.0,
            ]),
            dash_length=0.12,
            stroke_width=3,
            color=lighten(GUIDE_COLOR),
            stroke_opacity=0.55,
        )
        single_label = MathTex(
            r"N = 1", font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR)
        ).next_to(single.get_end(), UP, buff=0.14)  # clear of the n*hbar*k arrow

        gap = DoubleArrow(
            [upper_pts[-1][0] + 0.55, lower_pts[-1][1], 0],
            [upper_pts[-1][0] + 0.55, upper_pts[-1][1], 0],
            buff=0,
            stroke_width=3,
            color=lighten(KICKED_COLOR),
            max_tip_length_to_length_ratio=0.05,
        )
        gap_label = MathTex(
            r"N\hbar k", font_size=FONT_STATE, color=lighten(KICKED_COLOR)
        ).next_to(gap, RIGHT, buff=0.18)

        self.play(Create(single), FadeIn(single_label), run_time=0.9)
        self.play(GrowFromCenter(gap), FadeIn(gap_label), run_time=0.7)
        self.beat()

        # bottom left, under the lower arm's start: it ends in the bottom right
        scaling = MathTex(
            r"\Phi \;\propto\; N\,k\,\sin^{2}(\omega T/2)", font_size=FONT_STATE
        ).to_corner(DL)
        self.play(Write(scaling), run_time=1.0)
        self.wait(2.0)




class LMTMachZehnder(Scene):
    """pi/2 - pi - pi/2 with every pulse stretched into many, after Rudolph
    et al., Fig. 1c: an N = LMZ_ORDER interferometer, (N - 1)/2 pulses out,
    N at the mirror and (N - 1)/2 back. Every pulse drives both arms, and
    each is labelled pi/2 or pi along the bottom as it fires.

    Stops (beat) once the atom is in, and after each of the three stages:
    beam splitter, mirror, beam splitter. Then the enclosed area, with the
    N = 1 interferometer over the same time drawn dashed inside it.
    """

    STAGES = (r"beam splitter", r"mirror", r"beam splitter")
    FAST_AFTER = 2  # pulses at full pace, while the idea lands; the rest quicker
    CAPTION_Y = -config.frame_y_radius + 0.35  # the stage captions
    LABEL_Y = -config.frame_y_radius + 0.9  # the pi/2 and pi labels, just above

    def beat(self):
        """The pause after each step: nothing here, a click on the slide version."""

    def construct(self):
        title = Tex(
            rf"Large momentum transfer in the Mach--Zehnder: $N = {LMZ_ORDER}$",
            font_size=FONT_TITLE,
        ).to_corner(UL)
        note = Tex(
            r"colour is the internal state; slope is momentum",
            font_size=FONT_LEGEND,
            color=lighten(GUIDE_COLOR),
        ).next_to(title, DOWN, buff=0.2).align_to(title, LEFT)
        self.play(FadeIn(title), FadeIn(note), run_time=0.9)
        # rays run between the pulse labels and the header
        self.span = (self.LABEL_Y + 0.35, note.get_bottom()[1] - 0.15)

        start = np.array([LMZ_T0, LMZ_Z, 0.0])
        seq = run_sequence(lmz_pulses(LMZ_ORDER, LMZ_STEP, LMZ_T, t0=LMZ_T0), start,
                           LMZ_U, port=LMZ_PORT)
        atom = make_atom().move_to([-config.frame_x_radius + 0.3, start[1], 0])
        self.play(FadeIn(atom, scale=0.5), run_time=0.4)
        self.play(atom.animate.move_to(start), rate_func=linear,
                  run_time=(start[0] - atom.get_center()[0]) / V)
        self.beat()

        shown = set()

        def caption_stage(step, k):
            """Each stage's caption, as its first pulse comes up."""
            if step.pulse.stage not in shown:
                shown.add(step.pulse.stage)
                self.play(FadeIn(self.caption(seq, step.pulse.stage)), run_time=0.3)

        def stop_after_stage(step, k):
            """A stop once a stage's last pulse has flown its legs."""
            if k + 1 == len(seq.steps) or seq.steps[k + 1].pulse.stage != step.pulse.stage:
                self.beat()

        play_sequence(self, seq, {"": atom}, span=self.span, fast_after=self.FAST_AFTER,
                      before_pulse=caption_stage, with_pulse=lambda step: [self.pulse_label(step)],
                      after_step=stop_after_stage)
        paths = seq.paths

        # --- what it bought ---------------------------------------------------
        loop = Polygon(*paths["1"], *reversed(paths["0"]), **LOOP_AREA_STYLE)
        phase = MathTex(r"\Phi", font_size=FONT_PHASE, color=lighten(AREA_COLOR))
        phase.move_to(loop.get_center_of_mass()).shift(UP * 0.8)

        # the N = 1 interferometer over the same time: one recoil
        half = LMZ_END / 2
        plain = DashedVMobject(Polygon(
            start,
            start + [half, half * LMZ_U, 0],
            start + [LMZ_END, half * LMZ_U, 0],
            start + [half, 0, 0],
        ).set_stroke(lighten(GUIDE_COLOR), 3, opacity=0.7), num_dashes=60)
        plain_label = MathTex(r"N = 1", font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR))
        plain_label.next_to(plain, DOWN, buff=0.12)

        self.play(FadeIn(loop), FadeIn(phase), run_time=0.8)
        self.play(Create(plain), FadeIn(plain_label), run_time=1.0)
        self.beat()
        scaling = MathTex(
            r"\Phi \;\propto\; N\,k\,\sin^{2}(\omega T/2)", font_size=FONT_STATE
        ).to_corner(UR)  # clear of the arms, which peak left of centre
        self.play(Write(scaling), run_time=1.0)
        self.wait(2.0)

    def caption(self, seq, stage):
        """The stage's caption, centred under its pulses."""
        xs = [step.x for step in seq.steps if step.pulse.stage == stage]
        return Tex(
            self.STAGES[stage], font_size=FONT_LEGEND, color=LASER_COLOR,
        ).move_to([(xs[0] + xs[-1]) / 2, self.CAPTION_Y, 0])

    def pulse_label(self, step):
        """pi/2 or pi under the pulse's column, as the paper's sequence row."""
        tex = r"\frac{\pi}{2}" if step.pulse.area == 0.5 else r"\pi"
        return MathTex(tex, font_size=FONT_LEGEND - 4, color=LASER_COLOR).move_to(
            [step.x, self.LABEL_Y, 0])
