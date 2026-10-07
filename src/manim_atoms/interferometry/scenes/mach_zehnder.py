"""A single beamsplitter kick, and the full Mach-Zehnder light-pulse sequence.

Each scene is a geometry block and a list of pulses: the pulse-sequence
engine (interferometry.tools.pulse_sequence) steps the atom through them and
plays them photon by photon, and the scene adds what is its own -- captions,
recoil arrows, the stops -- through the player's hooks. SinglePhotonMachZehnder
subclasses MachZehnder.
"""

import numpy as np
from manim import *

from manim_atoms.interferometry.style import *
from manim_atoms.interferometry.tools.pulses import pulse_caption
from manim_atoms.interferometry.tools.pulse_sequence import Pulse, play_sequence, run_sequence
from manim_atoms.core.primitives import (
    make_atom,
    momentum_arrow,
    grow,
    make_k_arrow,
    make_guide,
    state_label,
    state_legend,
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
MZ_PULSES = [Pulse(MZ_A[0], 0.5), Pulse(MZ_B[0], 1.0), Pulse(MZ_C[0], 0.5)]
MZ_LABELS = (r"\pi/2", r"\pi", r"\pi/2")


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

        # --- 3. one pulse from below, and the arms it launches -------------
        # A sequence of one pi/2, whose two outputs fly on as the arms. One
        # recoil is slope 1: equal horizontal components, a true 45 degree
        # kick, the resultant of the forward momentum p and the recoil hbar k.
        seq = run_sequence([Pulse(SPLIT_X, 0.5)], SPLIT_POINT, 1.0, port=ARM_LENGTH)
        caption = MathTex(
            r"\pi/2\ \text{pulse}", font_size=FONT_ANNOTATION, color=LASER_COLOR
        ).next_to(SPLIT_POINT, DOWN, buff=0.9)
        k_arrow = make_k_arrow(SPLIT_X - 0.9, -config.frame_y_radius + 0.45)

        def kick(step, k, arm):
            """The momentum kick, purely vertical, and the incoming label goes."""
            recoil = momentum_arrow(SPLIT_POINT, UP, r"\hbar k", length=1.2)
            return [*grow(recoil), FadeOut(in_label)]

        arms = play_sequence(
            self, seq, {"": atom}, style="photon", kick_time=0.7,
            photon_extras=lambda step, k, arm: ([caption, k_arrow], [k_arrow]),
            on_kick=kick,
        )
        straight, kicked = arms["0"], arms["1"]

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
        legend = state_legend().to_corner(UL)
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

        # --- 3. the three pulses, photon by photon -------------------------
        # pi/2 splits, pi swaps the arms' internal states and with them their
        # momenta (the upper arm loses hbar k and flattens out, the lower gains
        # it and climbs, so they converge), and the last pi/2 recombines them
        # where they meet. Each leg is coloured by the state that arm is in
        # while traversing it. One recoil is slope 1.
        seq = run_sequence(MZ_PULSES, MZ_A, 1.0, port=MZ_OUT)
        ports = play_sequence(
            self, seq, {"": atom}, style="photon",
            photon_extras=self.photon_extras, on_kick=self.kick,
            with_legs=self.with_legs, after_step=self.stop,
        )
        port_g, port_e = ports["g"], ports["e"]

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

    # --- the player's hooks: what the sequence adds to the engine's ------------
    def photon_extras(self, step, k, arm):
        """The pulse's caption, with its first photon; on the first pulse the
        k-vector marker too, gone as the photon is absorbed."""
        if arm != step.driven[0]:
            return (), ()
        caption = pulse_caption(MZ_LABELS[k], step.x)
        if k > 0:
            return [caption], []
        k_arrow = make_k_arrow(step.x - 0.9, -config.frame_y_radius + 0.45)
        return [caption, k_arrow], [k_arrow]

    def kick(self, step, k, arm):
        """A recoil arrow on the atom it acts on, where the kick happens.

        Bottom to top, following the beam. At the mirror both arms share a
        column, so the pulse rising to the upper arm passes over the lower
        arm's +hbar k arrow -- that overlap is worth accepting, because each
        arrow has to stand on the atom it acts on. The excited arm is driven
        the other way: one photon arrives, two leave, and it recoils by
        -hbar k, which flattens it out.
        """
        at = next(point for name, point, _ in step.hits if name == arm)
        if k == 0:
            arrow = momentum_arrow(at, UP, r"\hbar k")
        elif arm == "0":
            arrow = momentum_arrow(at, UP, r"+\hbar k")
        else:
            arrow = momentum_arrow(at, DOWN, r"-\hbar k", label_dir=RIGHT)
        self.arrows = [*getattr(self, "arrows", []), arrow]
        return grow(arrow)

    def with_legs(self, step, k):
        """The pulse's recoil arrows fade as the arms fly off."""
        fade, self.arrows = getattr(self, "arrows", []), []
        return fade, ()

    def stop(self, step, k):
        """A stop as the atoms reach the next pulse; the ports run on."""
        if k + 1 < len(MZ_PULSES):
            self.beat()
