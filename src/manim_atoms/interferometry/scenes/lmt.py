"""Large momentum transfer: more photon recoils, arms further apart.

After Rudolph et al., PRL 124, 083604 (2020). LargeMomentumTransfer is the
ladder on its own: ten kicks, each after the first driving both arms apart.
LMTMachZehnder puts it to use (their Fig. 1c), stretching each pulse of the
pi/2 - pi - pi/2 sequence into many, beside the plain N = 1 interferometer it
replaces. TwelvePulseLMT is the same at N = 7: the plain sequence plus
twelve LMT pulses, counted as they fire, with each arm's state written on it.
"""

import numpy as np
from manim import *

from manim_atoms.interferometry.style import *
from manim_atoms.interferometry.tools.lmt import (
    LMT_KICKS,
    LMT_T0,
    LMT_U,
    LMT_Z,
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
from manim_atoms.core.primitives import (
    draw_legs,
    make_atom,
    state_colors,
    state_label,
)


# --- the twelve-pulse LMT Mach-Zehnder -------------------------------------
# Twelve LMT pulses added to pi/2 - pi - pi/2: three after the first pi/2,
# three either side of the mirror's pi and three before the last pi/2. Every
# one drives both arms, so each opens or closes the gap by 2 hbar k and the
# order is N = 1 + 12 / 2 = 7; 15 pulses in all. (A closed, symmetric sequence
# of this kind always has 4m + 3 pulses, so twelve can only be the added ones.)
TWELVE_ORDER = 7
TWELVE_T0 = -5.9  # the first pi/2
TWELVE_Z = -0.55  # where the atom comes in
TWELVE_STEP = 0.4  # between the pulses of one stage: room for their labels
TWELVE_T = 2.7  # the first pi/2 to the first mirror pulse
TWELVE_U = 0.26  # baseline per unit time per recoil: fills the frame at 7 hbar k
TWELVE_PORT = 2.6  # the ports part by one recoil


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
    # The order and its geometry, as class attributes so that a subclass can
    # draw another order in the same way (TwelvePulseLMT).
    ORDER = LMZ_ORDER
    T0 = LMZ_T0
    Z = LMZ_Z
    STEP = LMZ_STEP
    T = LMZ_T
    U = LMZ_U
    PORT = LMZ_PORT

    def beat(self):
        """The pause after each step: nothing here, a click on the slide version."""

    @property
    def end(self):
        """The first pi/2 to the last."""
        return 2 * self.T + (self.ORDER - 1) * self.STEP

    def make_title(self):
        return Tex(
            rf"Large momentum transfer in the Mach--Zehnder: $N = {self.ORDER}$",
            font_size=FONT_TITLE,
        ).to_corner(UL)

    def construct(self):
        title = self.make_title()
        note = Tex(
            r"colour is the internal state; slope is momentum",
            font_size=FONT_LEGEND,
            color=lighten(GUIDE_COLOR),
        ).next_to(title, DOWN, buff=0.2).align_to(title, LEFT)
        self.play(FadeIn(title), FadeIn(note), run_time=0.9)
        self.header = VGroup(title, note)
        # rays run between the pulse labels and the header
        self.span = (self.LABEL_Y + 0.35, note.get_bottom()[1] - 0.15)

        start = np.array([self.T0, self.Z, 0.0])
        self.history = history = lmt_history(
            lmz_pulses(self.ORDER, self.STEP, self.T),
            self.T0, self.Z, self.U, port=self.PORT)
        paths = self.play_history(history, start)
        self.closing(paths, start)

    def closing(self, paths, start):
        """What it bought: the enclosed area, the N = 1 interferometer over
        the same time inside it, and how the phase scales."""
        loop, phase, plain, plain_label = self.area(paths, start)
        self.play(FadeIn(loop), FadeIn(phase), run_time=0.8)
        self.play(Create(plain), FadeIn(plain_label), run_time=1.0)
        self.beat()
        scaling = MathTex(
            r"\Phi \;\propto\; N\,k\,\sin^{2}(\omega T/2)", font_size=FONT_STATE
        ).to_corner(UR)  # clear of the arms, which peak left of centre
        self.play(Write(scaling), run_time=1.0)
        self.wait(2.0)

    def area(self, paths, start):
        """(loop, its Phi, the dashed N = 1 interferometer, its label)."""
        loop = Polygon(*paths["1"], *reversed(paths["0"]), **LOOP_AREA_STYLE)
        phase = MathTex(r"\Phi", font_size=FONT_PHASE, color=lighten(AREA_COLOR))
        phase.move_to(loop.get_center_of_mass()).shift(UP * 0.8)

        # the N = 1 interferometer over the same time: one recoil
        end = self.end
        half = end / 2
        plain = DashedVMobject(Polygon(
            start,
            start + [half, half * self.U, 0],
            start + [end, half * self.U, 0],
            start + [half, 0, 0],
        ).set_stroke(lighten(GUIDE_COLOR), 3, opacity=0.7), num_dashes=60)
        plain_label = MathTex(r"N = 1", font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR))
        plain_label.next_to(plain, DOWN, buff=0.12)
        return loop, phase, plain, plain_label

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
            self.play(Create(ray), *self.pulse_marks(k, step),
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
                self.stage_done(stage, step)
                self.beat()
        return paths

    def pulse_marks(self, k, step):
        """What goes up with pulse k's ray: its label along the bottom."""
        return [FadeIn(self.pulse_label(step))]

    def stage_done(self, stage, step):
        """Anything to say once a stage's last legs are flown, before its
        stop: nothing here. ``step`` is the stage's last pulse."""


class TwelvePulseLMT(LMTMachZehnder):
    """The Mach-Zehnder with twelve LMT pulses added, N = 7.

    The plain sequence's own three pulses -- the pi/2s and the mirror's middle
    pi, which is what swaps the arms' momenta -- are labelled in the grey of
    the dashed N = 1 interferometer drawn at the end; the twelve LMT pulses in
    the laser red, counted up in the corner as they fire. Each long leg is
    written with its state once its stage has run: the beam splitter leaves
    the arms 7 hbar k apart in opposite states, and the mirror swaps them.

    Stops as LMTMachZehnder: the atom in, each stage, the area, the scaling.
    """

    ORDER = TWELVE_ORDER
    T0 = TWELVE_T0
    Z = TWELVE_Z
    STEP = TWELVE_STEP
    T = TWELVE_T
    U = TWELVE_U
    PORT = TWELVE_PORT
    FAST_AFTER = 4  # the first beam splitter's four at full pace

    def make_title(self):
        return Tex(
            rf"Mach--Zehnder with 12 LMT pulses: $N = {self.ORDER}$",
            font_size=FONT_TITLE,
        ).to_corner(UL)

    def plain_pulses(self):
        """Indices of the plain Mach-Zehnder's pulses: the two pi/2s and the
        middle of the mirror."""
        mirror = [k for k, h in enumerate(self.history) if h["stage"] == 1]
        return {0, mirror[len(mirror) // 2], len(self.history) - 1}

    def pulse_marks(self, k, step):
        label = self.pulse_label(step)
        # the mirror's kets sit right of the legs coming back, in the last
        # beam splitter's columns: they make way for its rays, and come back
        # once the arms have met (closing)
        out = ([FadeOut(self.kets[1])]
               if step["stage"] == 2 and self.kets[1] in self.mobjects else [])
        if k in self.plain_pulses():
            return [FadeIn(label.set_color(lighten(GUIDE_COLOR))), *out]
        lmt = sum(1 for j in range(k + 1) if j not in self.plain_pulses())
        # the count, at the end of the note's row, clear of the rays: one Tex,
        # so the number keeps the words' baseline, rebuilt at each pulse
        count = Tex(rf"LMT pulses: {lmt}", font_size=FONT_LEGEND, color=LASER_COLOR)
        count.to_edge(RIGHT).align_to(self.header[1], DOWN)
        if hasattr(self, "counter"):
            return [FadeIn(label), Transform(self.counter, count), *out]
        self.counter = count
        return [FadeIn(label), FadeIn(count)]

    def stage_done(self, stage, step):
        """Once a beam splitter or the mirror has run, the state on each long
        leg it launched: |internal, p + n hbar k>, with n the leg's slope."""
        if stage == 2:
            return
        labels = VGroup()
        for arm, a, b, state in step["legs"]:
            n = round((b - a)[1] / ((b - a)[0] * self.U))
            color = KICKED_COLOR if state == "e" else ATOM_COLOR
            ket = state_label(
                rf"|{state},\, p {'+' if n > 0 else '-'} {abs(n)}\hbar k\rangle",
                color, FONT_LEGEND)
            # outside the loop: above the upper arm ("1", the kicked one),
            # below the lower -- on the outer side of the corner, which is
            # left of the legs going out and right of the legs coming back
            side = (UP if arm == "1" else DOWN) + (LEFT if stage == 0 else RIGHT)
            labels.add(ket.next_to((a + b) / 2, side, buff=0.1))
        self.kets = getattr(self, "kets", []) + [labels]
        self.play(FadeIn(labels), run_time=0.6)

    def closing(self, paths, start):
        self.play(FadeIn(self.kets[1]), run_time=0.6)
        super().closing(paths, start)
