"""A single beamsplitter kick, and the full Mach-Zehnder light-pulse sequence.

Each scene keeps its own geometry block; the atoms and pulses they are drawn
with come from aionanim.tools.primitives, and everything visual from
aionanim.style.
"""

import numpy as np
from manim import *

from aionanim.style import *
from aionanim.tools.primitives import (
    make_atom,
    momentum_arrow,
    grow,
    make_k_arrow,
    make_guide,
    absorb,
    emit,
    draw_legs,
    state_colors,
    state_label,
)

# --- single-kick geometry -------------------------------------------------
# The frame is ~14.2 x 8 units. The incoming trajectory sits below centre so
# the 45 degree arm has room to climb without clipping the top edge.
BEAM_Y = -1.0
START_X = -6.0
SPLIT_X = -1.0
ARM_LENGTH = 4.0
SPLIT_POINT = np.array([SPLIT_X, BEAM_Y, 0.0])

# --- Mach-Zehnder geometry ------------------------------------------------
# pi/2 - pi - pi/2 traces a parallelogram: the arms separate, the mirror pulse
# swaps their momenta so they converge, and they overlap again at the
# recombining pulse. Because both arms carry the same horizontal velocity,
# they always share an x coordinate, so one vertical laser line catches both.
MZ_L = 2.8  # horizontal length of each interferometer leg
MZ_OUT = 2.2  # how far the output ports run past the last pulse
MZ_A = np.array([-5.8, -2.6, 0.0])  # first pi/2
MZ_B = MZ_A + RIGHT * MZ_L  # pi pulse, lower arm
MZ_B_UP = MZ_A + (RIGHT + UP) * MZ_L  # pi pulse, upper arm
MZ_C = MZ_B_UP + RIGHT * MZ_L  # second pi/2, where the arms overlap again


class SingleLaserKick(Scene):
    """One beamsplitter pulse: an atom splits into two momentum states."""

    def construct(self):
        # --- 1. setup ----------------------------------------------------
        guide = make_guide(
            [START_X, BEAM_Y, 0], [config.frame_x_radius, BEAM_Y, 0]
        )
        caption = Tex(
            r"Atom interferometry: one beamsplitter pulse", font_size=FONT_TITLE
        ).to_corner(UL)

        self.play(FadeIn(guide), FadeIn(caption), run_time=1.0)

        # --- 2. incoming atom --------------------------------------------
        atom = make_atom().move_to([START_X, BEAM_Y, 0])
        in_label = state_label(r"|g,\,p\rangle", ATOM_COLOR, FONT_ANNOTATION)
        in_label.add_updater(lambda m: m.next_to(atom, UP, buff=0.25))

        self.play(FadeIn(atom, scale=0.5), FadeIn(in_label), run_time=0.6)
        self.play(
            atom.animate.shift(RIGHT * (SPLIT_X - START_X)),
            rate_func=linear,
            run_time=(SPLIT_X - START_X) / V,
        )
        in_label.clear_updaters()

        # --- 3. laser pulse from below -----------------------------------
        pulse_caption = MathTex(
            r"\pi/2\ \text{pulse}", font_size=FONT_ANNOTATION, color=LASER_COLOR
        ).next_to(SPLIT_POINT, DOWN, buff=0.9)
        k_arrow = make_k_arrow(SPLIT_X - 0.9, -config.frame_y_radius + 0.45)
        absorb(self, SPLIT_X, atom, extras=[pulse_caption, k_arrow], fade=[k_arrow])

        # --- 4. the split -------------------------------------------------
        straight = make_atom(opacity=SUPERPOSITION_OPACITY).move_to(SPLIT_POINT)
        kicked = make_atom(KICKED_COLOR, opacity=SUPERPOSITION_OPACITY).move_to(
            SPLIT_POINT
        )

        # The momentum kick is purely vertical -- the 45 degree path is the
        # resultant of the forward momentum p and the recoil hbar k.
        recoil = momentum_arrow(SPLIT_POINT, UP, r"\hbar k", length=1.2)

        self.remove(atom)
        self.add(straight, kicked)
        self.play(*grow(recoil), FadeOut(in_label), run_time=0.7)

        # --- 5. diverging arms -------------------------------------------
        # Equal horizontal component on both arms -> a true 45 degree kick.
        draw_legs(
            self,
            [
                (straight, SPLIT_POINT, SPLIT_POINT + RIGHT * ARM_LENGTH, ATOM_COLOR),
                (
                    kicked,
                    SPLIT_POINT,
                    SPLIT_POINT + ARM_LENGTH * (RIGHT + UP),
                    KICKED_COLOR,
                ),
            ],
        )

        # --- 6. final state labels ---------------------------------------
        straight_label = state_label(r"|g,\,p\rangle", ATOM_COLOR).next_to(
            straight, DOWN, buff=0.3
        )
        kicked_label = state_label(
            r"|e,\,p + \hbar k\rangle", KICKED_COLOR
        ).next_to(kicked, RIGHT, buff=0.3)

        self.play(Write(straight_label), Write(kicked_label), run_time=1.2)
        self.wait(1.5)


class MachZehnder(Scene):
    """The full pi/2 - pi - pi/2 sequence: split, mirror, recombine."""

    def beat(self):
        """The pause after each step: nothing here, a click on the slide version."""

    def construct(self):
        # --- 1. setup ----------------------------------------------------
        # Title right, legend left: the mirror's emitted photons fly straight up
        # the line x = MZ_B[0], and this keeps that column clear of both.
        title = Tex(
            r"Mach--Zehnder atom interferometer: $\pi/2 - \pi - \pi/2$",
            font_size=FONT_TITLE,
        ).to_corner(UR)
        legend = self.make_legend().to_corner(UL)
        guide = make_guide([-config.frame_x_radius, MZ_A[1], 0], MZ_A)
        self.play(FadeIn(title), FadeIn(legend), FadeIn(guide), run_time=1.0)
        self.beat()

        # --- 2. incoming atom --------------------------------------------
        atom = make_atom().move_to([-config.frame_x_radius + 0.2, MZ_A[1], 0])
        self.play(FadeIn(atom, scale=0.5), run_time=0.5)
        self.play(
            atom.animate.move_to(MZ_A),
            rate_func=linear,
            run_time=(MZ_A[0] - atom.get_center()[0]) / V,
        )

        # --- 3. first pi/2: split ----------------------------------------
        k_arrow = make_k_arrow(MZ_A[0] - 0.9, -config.frame_y_radius + 0.45)
        absorb(
            self,
            MZ_A[0],
            atom,
            extras=[self.pulse_caption(r"\pi/2", MZ_A[0]), k_arrow],
            fade=[k_arrow],
        )

        lower = make_atom(opacity=SUPERPOSITION_OPACITY).move_to(MZ_A)
        upper = make_atom(KICKED_COLOR, opacity=SUPERPOSITION_OPACITY).move_to(MZ_A)
        recoil = momentum_arrow(MZ_A, UP, r"\hbar k")

        self.remove(atom)
        self.add(lower, upper)
        self.play(*grow(recoil), run_time=0.6)

        # Each leg is coloured by the state that arm is in while traversing it.
        draw_legs(
            self,
            [(lower, MZ_A, MZ_B, ATOM_COLOR), (upper, MZ_A, MZ_B_UP, KICKED_COLOR)],
            fade=[recoil],
        )
        self.beat()

        # --- 4. pi pulse: the mirror -------------------------------------
        # The pi pulse exchanges the two arms' internal states, and with them
        # their momenta: the upper arm loses hbar k and flattens out, the lower
        # arm gains it and climbs. The arms converge instead of diverging.
        gain = momentum_arrow(MZ_B, UP, r"+\hbar k")
        lose = momentum_arrow(MZ_B_UP, DOWN, r"-\hbar k", label_dir=RIGHT)

        # Bottom to top, following the beam. Both arms share a column, so the
        # pulse rising to the upper arm passes over the lower arm's +hbar k
        # arrow -- that overlap is worth accepting, because each arrow has to
        # stand on the atom it acts on, where the kick actually happens.
        absorb(self, MZ_B[0], lower, extras=[self.pulse_caption(r"\pi", MZ_B[0])])
        self.play(state_colors(lower, KICKED_COLOR), *grow(gain), run_time=0.6)
        # The excited arm is driven the other way: one photon arrives, two
        # leave, and it recoils by -hbar k, which flattens it out.
        emit(self, MZ_B_UP[0], upper)
        self.play(state_colors(upper, ATOM_COLOR), *grow(lose), run_time=0.6)
        draw_legs(
            self,
            [(lower, MZ_B, MZ_C, KICKED_COLOR), (upper, MZ_B_UP, MZ_C, ATOM_COLOR)],
            fade=[gain, lose],
        )
        self.beat()

        # --- 5. second pi/2: recombine -----------------------------------
        # Both arms sit at MZ_C now, so one pulse covers them.
        absorb(self, MZ_C[0], lower, extras=[self.pulse_caption(r"\pi/2", MZ_C[0])])

        port_g = make_atom(opacity=SUPERPOSITION_OPACITY).move_to(MZ_C)
        port_e = make_atom(KICKED_COLOR, opacity=SUPERPOSITION_OPACITY).move_to(MZ_C)
        self.remove(lower, upper)
        self.add(port_g, port_e)
        draw_legs(
            self,
            [
                (port_g, MZ_C, MZ_C + RIGHT * MZ_OUT, ATOM_COLOR),
                (port_e, MZ_C, MZ_C + (RIGHT + UP) * MZ_OUT, KICKED_COLOR),
            ],
        )

        # --- 6. the enclosed area and the output ports -------------------
        loop = Polygon(MZ_A, MZ_B, MZ_C, MZ_B_UP, **LOOP_AREA_STYLE)
        phase = MathTex(
            r"\Phi", font_size=FONT_PHASE, color=lighten(AREA_COLOR)
        ).move_to((MZ_A + MZ_B + MZ_C + MZ_B_UP) / 4)
        p1 = state_label(r"P_g", ATOM_COLOR).next_to(port_g, RIGHT, buff=0.3)
        p2 = state_label(r"P_e", KICKED_COLOR).next_to(port_e, RIGHT, buff=0.3)
        readout = MathTex(
            r"P_{g,e} = \tfrac{1}{2}\left(1 \pm \cos\Phi\right)",
            font_size=FONT_ANNOTATION,
        ).to_corner(DR)

        self.play(FadeIn(loop), FadeIn(phase), run_time=0.8)
        self.beat()
        self.play(Write(p1), Write(p2), Write(readout), run_time=1.3)
        self.wait(2.0)

    # --- helpers ---------------------------------------------------------
    @staticmethod
    def make_legend():
        rows = VGroup()
        for color, tex in (
            (ATOM_COLOR, r"|g,\,p\rangle"),
            (KICKED_COLOR, r"|e,\,p + \hbar k\rangle"),
        ):
            rows.add(
                VGroup(
                    make_atom(color, radius=LEGEND_ATOM_RADIUS),
                    state_label(tex, color, FONT_LEGEND),
                ).arrange(RIGHT, buff=0.22)
            )
        return rows.arrange(DOWN, buff=0.28, aligned_edge=LEFT)

    @staticmethod
    def pulse_caption(tex, x):
        """A pulse label on the caption row, offset clear of the beam it names."""
        return MathTex(tex, font_size=FONT_ANNOTATION, color=LASER_COLOR).move_to(
            [x + 0.5, -config.frame_y_radius + 0.35, 0]
        )
