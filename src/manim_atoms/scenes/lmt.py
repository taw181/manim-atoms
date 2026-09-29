"""Large momentum transfer: more photon recoils, arms further apart.

After Rudolph et al., PRL 124, 083604 (2020). LargeMomentumTransfer is the
ladder on its own: ten kicks, each after the first driving both arms apart.
LMTMachZehnder puts it to use (their Fig. 1c), stretching each pulse of the
pi/2 - pi - pi/2 sequence into many, beside the plain N = 1 interferometer it
replaces.
"""

import numpy as np
from manim import *

from aionanim.style import *
from aionanim.tools.lmt import (
    LMT_KICKS,
    LMT_T0,
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
    kick_worldline,
    lmt_history,
    lmt_points,
    lmz_pulses,
)
from aionanim.tools.primitives import (
    draw_legs,
    make_atom,
    state_colors,
)


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
        # it drives both, pushing them apart by 2 hbar k
        upper_pts = lmt_points(lambda i: (i + 1) * LMT_U)
        lower_pts = lmt_points(lambda i: -i * LMT_U)

        # --- the atom arrives ---------------------------------------------
        atom = make_atom().move_to([-config.frame_x_radius + 0.3, LMT_Z, 0])
        self.play(FadeIn(atom, scale=0.5), run_time=0.4)
        self.play(
            atom.animate.move_to(upper_pts[0]),
            rate_func=linear,
            run_time=(LMT_T0 - atom.get_center()[0]) / V,
        )
        self.beat()

        lower = make_atom(opacity=SUPERPOSITION_OPACITY).move_to(upper_pts[0])
        upper = make_atom(opacity=SUPERPOSITION_OPACITY).move_to(upper_pts[0])
        self.remove(atom)
        self.add(lower, upper)

        # --- the ladder -----------------------------------------------------
        # Kicks alternate direction. The upper arm absorbs an upward photon,
        # then emits into a downward one: either way it is pushed up by hbar k.
        # The lower arm, always in the other state, is pushed down by the same
        # pulses. Both flip their internal state at every kick.
        states = [KICKED_COLOR, ATOM_COLOR]
        for i in range(LMT_KICKS):
            # the first two at full pace, while the idea lands; the rest quicker
            pace = 1.0 if i < 2 else 0.6
            from_below = i % 2 == 0
            # a ray reaches through to the far arm
            reach = upper_pts[i] if from_below else lower_pts[i]
            ray = kick_worldline(reach, from_below, steepness=0.0,
                                 span=(-config.frame_y_radius, note.get_bottom()[1] - 0.15))
            self.play(Create(ray), rate_func=linear, run_time=0.45 * pace)
            upper_color = states[i % 2]
            lower_color = ATOM_COLOR if i == 0 else states[(i + 1) % 2]
            hit = [upper] if i == 0 else [upper, lower]
            self.play(
                *[Flash(atom, **FLASH_STYLE) for atom in hit],
                FadeOut(ray),
                state_colors(upper, upper_color),
                state_colors(lower, lower_color),
                run_time=0.4 * pace,
            )
            draw_legs(self, [
                (upper, upper_pts[i], upper_pts[i + 1], upper_color),
                (lower, lower_pts[i], lower_pts[i + 1], lower_color),
            ])
            if i == 0:  # one kick explained; the rest of the ladder runs on
                self.beat()
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
        history = lmt_history(lmz_pulses(LMZ_ORDER, LMZ_STEP, LMZ_T),
                              LMZ_T0, LMZ_Z, LMZ_U, port=LMZ_PORT)
        paths = self.play_history(history, start)

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

    def caption(self, history, stage):
        """The stage's caption, centred under its pulses."""
        xs = [h["x"] for h in history if h["stage"] == stage]
        return Tex(
            self.STAGES[stage], font_size=FONT_LEGEND, color=LASER_COLOR,
        ).move_to([(xs[0] + xs[-1]) / 2, self.CAPTION_Y, 0])

    def pulse_label(self, step):
        """pi/2 or pi under the pulse's column, as the paper's sequence row."""
        tex = r"\frac{\pi}{2}" if step["kind"] in ("split", "merge") else r"\pi"
        return MathTex(tex, font_size=FONT_LEGEND - 4, color=LASER_COLOR).move_to(
            [step["x"], self.LABEL_Y, 0])

    def play_history(self, history, start):
        """One ray per pulse, reaching through to the far arm, a flash on every
        arm it drives, then the legs to the next pulse. Returns each arm's
        corners, from the split to the merge."""
        colors = {"g": ATOM_COLOR, "e": KICKED_COLOR}
        atom = make_atom().move_to([-config.frame_x_radius + 0.3, start[1], 0])
        self.play(FadeIn(atom, scale=0.5), run_time=0.4)
        self.play(atom.animate.move_to(start), rate_func=linear,
                  run_time=(start[0] - atom.get_center()[0]) / V)
        self.beat()

        atoms = {"": atom}
        paths = {}
        shown = set()
        for k, step in enumerate(history):
            stage = step["stage"]
            if stage not in shown:
                shown.add(stage)
                self.play(FadeIn(self.caption(history, stage)), run_time=0.3)

            pace = 1.0 if k < self.FAST_AFTER else 0.6
            # the ray runs from its side through every arm to the furthest
            points = [a.get_center() for a in atoms.values()]
            furthest = max if step["from_below"] else min
            reach = furthest(points, key=lambda p: p[1])
            ray = kick_worldline(reach, step["from_below"], steepness=0.0,
                                 span=self.span)
            self.play(Create(ray), FadeIn(self.pulse_label(step)),
                      rate_func=linear, run_time=0.3 * pace)

            if step["kind"] == "merge":
                flashes = [Flash(a, **FLASH_STYLE) for a in atoms.values()]
            recolour = []
            for parent, stay, kicked in step["splits"]:
                split = atoms.pop(parent)
                point = split.get_center()
                atoms[stay] = make_atom(opacity=SUPERPOSITION_OPACITY).move_to(point)
                atoms[kicked] = make_atom(opacity=SUPERPOSITION_OPACITY).move_to(point)
                self.remove(split)
                self.add(atoms[stay], atoms[kicked])
                paths[stay], paths[kicked] = [point], [point]
            if step["kind"] != "merge":
                flashes = [Flash(atoms[arm], **FLASH_STYLE) for arm, _, _ in step["hits"]]
                recolour = [state_colors(atoms[arm], colors[state])
                            for arm, _, state in step["hits"]]
            self.play(*flashes, *recolour, FadeOut(ray), run_time=0.35 * pace)
            if step["kind"] == "merge":
                self.remove(*atoms.values())
                atoms = {}
                for arm, point, _, state in step["legs"]:
                    atoms[arm] = make_atom(colors[state], opacity=SUPERPOSITION_OPACITY)
                    self.add(atoms[arm].move_to(point))

            draw_legs(self, [(atoms[arm], a, b, colors[state])
                             for arm, a, b, state in step["legs"]])
            if step["kind"] != "merge":
                for arm, _, b, _ in step["legs"]:
                    paths[arm].append(b)
            if k + 1 == len(history) or history[k + 1]["stage"] != stage:
                self.beat()
        return paths
