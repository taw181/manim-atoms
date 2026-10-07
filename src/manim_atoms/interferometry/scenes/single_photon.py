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

from manim_atoms.interferometry.style import *
from manim_atoms.interferometry.tools.pulse_sequence import play_sequence, run_sequence
from manim_atoms.core.primitives import (
    arm_ket,
    draw_legs,
    make_atom,
    state_label,
)
from manim_atoms.species.two_level import (
    make_level_diagram,
    transition_glow,
)
from manim_atoms.interferometry.scenes.mach_zehnder import (
    MZ_A,
    MZ_OUT,
    MZ_PULSES,
    MachZehnder,
)

KET_BUFF = 0.2  # from a leg's midpoint to the state label beside it
# Which side of each leg its ket goes, per pulse, for the legs that pulse
# launches in the engine's order (left-alone arm first; |g> port first):
# below the ground arms, and out of the parallelogram for the kicked ones.
SP_KET_SIDES = ((DOWN, UL), (DR, UP), (DOWN, DR))


class SinglePhotonMachZehnder(MachZehnder):
    """pi/2 - pi - pi/2 driven by single photons, beside the transition it drives.

    Same geometry and the same pulse captions as the Mach-Zehnder in
    mach_zehnder.py, but the two-level system takes the corner the
    legend used to hold, and lights up each time a wavepacket reaches an atom.
    """

    def construct(self):
        # --- 1. setup ----------------------------------------------------
        # Title top left, as on every slide, levels top right. The two
        # photons stimulated out of the upper arm at the mirror fly straight
        # up x = MZ_B[0] and off the top of the frame, crossing the title on
        # their way out.
        title = Tex(
            r"Single-photon Mach--Zehnder: $\pi/2 - \pi - \pi/2$",
            font_size=FONT_TITLE,
        ).to_corner(UL)
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

        # --- 3. the three pulses, photon by photon -------------------------
        # As in MachZehnder, through the same hooks, each with more on it: a
        # glow on the level diagram rising (or, for the excited arm at the
        # mirror, falling) with each wavepacket, and each leg labelled with
        # the state the arm is in while traversing it.
        seq = run_sequence(MZ_PULSES, MZ_A, 1.0, port=MZ_OUT)
        ports = play_sequence(
            self, seq, {"": atom}, style="photon",
            photon_extras=self.photon_extras, on_kick=self.kick,
            with_legs=self.with_legs, after_step=self.stop,
        )
        port_g, port_e = ports["g"], ports["e"]

        # --- 6. the output ports ---------------------------------------
        p1 = state_label(r"P_g", ATOM_COLOR).next_to(port_g, RIGHT, buff=0.3)
        p2 = state_label(r"P_e", KICKED_COLOR).next_to(port_e, RIGHT, buff=0.3)
        readout = MathTex(
            r"P_{g,e} = \tfrac{1}{2}\left(1 \pm \cos\Phi\right)",
            font_size=FONT_ANNOTATION,
        ).to_corner(DR)
        self.play(Write(p1), Write(p2), Write(readout), run_time=1.3)
        self.wait(2.0)

    def photon_extras(self, step, k, arm):
        """MachZehnder's, and the transition lit while the wavepacket climbs:
        upward as an arm absorbs, downward as the excited arm at the mirror is
        stimulated to emit. Either goes out as the photon is taken up."""
        extras, fade = super().photon_extras(step, k, arm)
        emits = not step.merges and any(
            name == arm and state == "g" for name, _, state in step.hits
        )
        glow = transition_glow(upward=not emits)
        return [*extras, glow], [*fade, glow]

    def with_legs(self, step, k):
        """MachZehnder's, and each leg labelled with its arm's state."""
        fade, extra = super().with_legs(step, k)
        kets = [
            arm_ket(state == "e").next_to(midpoint(start, end), side, buff=KET_BUFF)
            for (_, start, end, state, _), side in zip(step.legs, SP_KET_SIDES[k])
        ]
        return fade, [*extra, *[FadeIn(ket) for ket in kets]]
