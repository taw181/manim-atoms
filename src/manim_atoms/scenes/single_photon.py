"""The single-photon Mach-Zehnder sequence, with the photons resolved.

SinglePhotonMachZehnder is the sequence on its own: every pulse is a
wavepacket that climbs the baseline into the atom, and at the mirror the
excited arm is driven the other way by stimulated emission -- one photon
arrives and two leave, so that arm recoils by -hbar k. Beside it is the
two-level system the whole scheme rests on, the Sr clock transition, which
doubles as the figure's key because its levels carry the colours the two
arms are drawn in.
"""

from manim import *

from aionanim.style import *
from aionanim.tools.primitives import (
    absorb,
    arm_ket,
    draw_legs,
    emit,
    grow,
    make_atom,
    make_k_arrow,
    momentum_arrow,
    state_colors,
    state_label,
)
from aionanim.tools.single_photon import (
    make_level_diagram,
    transition_glow,
)
from aionanim.scenes.mach_zehnder import (
    MZ_A,
    MZ_B,
    MZ_B_UP,
    MZ_C,
    MZ_OUT,
    MachZehnder,
)

KET_BUFF = 0.2  # from a leg's midpoint to the state label beside it


class SinglePhotonMachZehnder(MachZehnder):
    """pi/2 - pi - pi/2 driven by single photons, beside the transition it drives.

    Same geometry and the same pulse captions as the Mach-Zehnder in
    mach_zehnder.py, but the two-level system takes the corner the
    legend used to hold, and lights up each time a wavepacket reaches an atom.
    """

    def construct(self):
        # --- 1. setup ----------------------------------------------------
        # Title right, levels left: the two photons stimulated out of the
        # upper arm at the mirror fly straight up x = MZ_B[0] and off the top
        # of the frame, so that column has to stay clear of both.
        title = Tex(
            r"Single-photon Mach--Zehnder: $\pi/2 - \pi - \pi/2$",
            font_size=FONT_TITLE,
        ).to_corner(UR)
        levels = make_level_diagram()
        self.play(FadeIn(title), FadeIn(levels), run_time=1.0)
        self.beat()

        # --- 2. incoming atom --------------------------------------------
        entry = np.array([-config.frame_x_radius + 0.2, MZ_A[1], 0])
        atom = make_atom().move_to(entry)
        # above the way in: below it is the first pulse's caption
        ket_in = arm_ket(False).next_to(midpoint(entry, MZ_A), UP, buff=KET_BUFF)
        ket_in.set_x(max(ket_in.get_x(), -config.frame_x_radius + 0.15 + ket_in.width / 2))
        self.play(FadeIn(atom, scale=0.5), run_time=0.5)
        draw_legs(self, [(atom, entry, MZ_A, ATOM_COLOR)], extra=[FadeIn(ket_in)])

        # --- 3. first pi/2: split ----------------------------------------
        # One photon, one transition: the glow rises with the wavepacket and
        # goes out as the atom takes it up.
        k_arrow = make_k_arrow(MZ_A[0] - 0.9, -config.frame_y_radius + 0.45)
        glow = transition_glow()
        absorb(
            self,
            MZ_A[0],
            atom,
            extras=[self.pulse_caption(r"\pi/2", MZ_A[0]), k_arrow, glow],
            fade=[k_arrow, glow],
        )

        lower = make_atom(opacity=SUPERPOSITION_OPACITY).move_to(MZ_A)
        upper = make_atom(KICKED_COLOR, opacity=SUPERPOSITION_OPACITY).move_to(MZ_A)
        recoil = momentum_arrow(MZ_A, UP, r"\hbar k")

        self.remove(atom)
        self.add(lower, upper)
        self.play(*grow(recoil), run_time=0.6)

        # Each leg is coloured by the state that arm is in while traversing
        # it, and labelled with it.
        kets = [
            arm_ket(False).next_to(midpoint(MZ_A, MZ_B), DOWN, buff=KET_BUFF),
            arm_ket(True).next_to(midpoint(MZ_A, MZ_B_UP), UL, buff=KET_BUFF),
        ]
        draw_legs(
            self,
            [(lower, MZ_A, MZ_B, ATOM_COLOR), (upper, MZ_A, MZ_B_UP, KICKED_COLOR)],
            fade=[recoil],
            extra=[FadeIn(k) for k in kets],
        )
        self.beat()

        # --- 4. pi pulse: the mirror -------------------------------------
        # The two arms do opposite things to the same beam. The ground-state
        # arm absorbs, gains hbar k and climbs; the excited arm is stimulated
        # back down to |g>, emits into the mode of the driving field and
        # recoils by -hbar k, which flattens it out. The level diagram shows
        # which way each one is being driven.
        gain = momentum_arrow(MZ_B, UP, r"+\hbar k")
        lose = momentum_arrow(MZ_B_UP, DOWN, r"-\hbar k", label_dir=RIGHT)

        glow_up = transition_glow()
        absorb(
            self,
            MZ_B[0],
            lower,
            extras=[self.pulse_caption(r"\pi", MZ_B[0]), glow_up],
            fade=[glow_up],
        )
        self.play(state_colors(lower, KICKED_COLOR), *grow(gain), run_time=0.6)

        glow_down = transition_glow(upward=False)
        emit(self, MZ_B_UP[0], upper, extras=[glow_down])
        self.play(
            state_colors(upper, ATOM_COLOR),
            *grow(lose),
            FadeOut(glow_down),
            run_time=0.6,
        )
        kets = [
            arm_ket(True).next_to(midpoint(MZ_B, MZ_C), DR, buff=KET_BUFF),
            arm_ket(False).next_to(midpoint(MZ_B_UP, MZ_C), UP, buff=KET_BUFF),
        ]
        draw_legs(
            self,
            [(lower, MZ_B, MZ_C, KICKED_COLOR), (upper, MZ_B_UP, MZ_C, ATOM_COLOR)],
            fade=[gain, lose],
            extra=[FadeIn(k) for k in kets],
        )
        self.beat()

        # --- 5. second pi/2: recombine -----------------------------------
        # Both arms sit at MZ_C now, so one pulse covers them.
        glow = transition_glow()
        absorb(
            self,
            MZ_C[0],
            lower,
            extras=[self.pulse_caption(r"\pi/2", MZ_C[0]), glow],
            fade=[glow],
        )

        port_g = make_atom(opacity=SUPERPOSITION_OPACITY).move_to(MZ_C)
        port_e = make_atom(KICKED_COLOR, opacity=SUPERPOSITION_OPACITY).move_to(MZ_C)
        self.remove(lower, upper)
        self.add(port_g, port_e)
        out_g, out_e = MZ_C + RIGHT * MZ_OUT, MZ_C + (RIGHT + UP) * MZ_OUT
        kets = [
            arm_ket(False).next_to(midpoint(MZ_C, out_g), DOWN, buff=KET_BUFF),
            arm_ket(True).next_to(midpoint(MZ_C, out_e), DR, buff=KET_BUFF),
        ]
        draw_legs(
            self,
            [(port_g, MZ_C, out_g, ATOM_COLOR), (port_e, MZ_C, out_e, KICKED_COLOR)],
            extra=[FadeIn(k) for k in kets],
        )

        # --- 6. the output ports ---------------------------------------
        p1 = state_label(r"P_g", ATOM_COLOR).next_to(port_g, RIGHT, buff=0.3)
        p2 = state_label(r"P_e", KICKED_COLOR).next_to(port_e, RIGHT, buff=0.3)
        readout = MathTex(
            r"P_{g,e} = \tfrac{1}{2}\left(1 \pm \cos\Phi\right)",
            font_size=FONT_ANNOTATION,
        ).to_corner(DR)
        self.play(Write(p1), Write(p2), Write(readout), run_time=1.3)
        self.wait(2.0)
