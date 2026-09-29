"""The clock interferometer's phase, read out as the angle between two hands.

ClockPhase introduces the readout the other scenes lean on. The clock is the
interferometer, not either arm: each arm carries a hand that turns only while
that arm is excited, but what the last pulse reads out is the angle between
the two hands, and a symmetric interferometer comes back to zero. The
gradiometer then compares two such clocks at opposite ends of the baseline
through one laser, and the wave changes the light travel time between them.
The readout is written as what it is made of, Phi = Phi_propagation +
Phi_laser: the symmetric clock zeroes the first term, and the phase the pulses
write in leaves the second on the dial.
ClockPhaseTerms is the same scene with that budget marked up, naming the laser
term the gradiometer exists to cancel.
"""

import numpy as np
from manim import *

from aionanim.style import *
from aionanim.tools.clock import (
    CP_ARM,
    CP_DIAL,
    CP_OUT,
    CP_T,
    CP_T0,
    CP_Z,
    budget_equation,
    clock_rate,
    dial_hand,
    draw_ports,
    fire_vertical_pulse,
    ground_share,
    live_ports,
    make_clock_hand,
    make_dial,
    phase_sweep,
    readout_equation,
    show_phase_budget,
)
from aionanim.scenes.mach_zehnder import MachZehnder
from aionanim.tools.primitives import (
    arm_ket,
    draw_legs,
    make_atom,
    state_colors,
)


# where the budget goes: the open band between the note and
# the interferometer, left of the dial
CP_TERMS = np.array([-2.3, 2.0, 0.0])
# The arms' states, with the phase each has picked up by the end of the leg:
# +phi_n on absorbing pulse n's photon, -phi_n on emitting into it, and
# -omega_A T for a leg spent in |e>. Smaller than the Mach-Zehnder's, since
# the phases make them long.
CP_KET_FONT = FONT_AXIS
# The laser's phase at each pulse, in radians. Arbitrary, but not special: an
# arm picks phi_n up when it absorbs from pulse n and gives it back when it
# emits, so the hands jump at the pulses by exactly the phases the kets carry,
# and what is left between them at the end is phi_1 - 2 phi_2 + phi_3 -- here
# 1.3 rad, a split between the ports that reads at a glance.
CP_LASER_PHASES = (1.2, 0.1, 0.3)
# Something acting on the atoms over the middle of the second leg, as a
# fraction of it, and the extra phase it leaves on the arm excited there.
CP_EFFECT_SPAN = (0.25, 0.75)
CP_EFFECT_PAD = 0.3  # the box's reach above and below the two arms
CP_EFFECT_PHASE = 0.9
CP_EFFECT_TIME = 2.5  # the hand sweeps as the effect acts, not in a jump
CP_KET_BUFF = CLOCK_ATOM_RADIUS + 0.05  # clear of an atom flying past


class ClockPhase(Scene):
    """One interferometer -- one clock -- with the phase on show.

    The hands are drawn per arm, but the clock is not: what the last pulse
    reads out is the angle between them. See the comment above CLOCK_TURNS for
    why a single arm is not a clock and why the hands are still right.

    Both arms spend the same time in |e>, so the atoms' own term is a null:
    omega_A T cancels between the hands. What does not cancel is the laser's.
    Each pulse writes its phase phi_n onto the arm it acts on -- the hand
    jumps as it fires -- so the hands end phi_1 - 2 phi_2 + phi_3 apart, the
    dial shows that sector and the ports split by it. That leftover is the
    laser's phase noise in a real measurement, and the gradiometer exists to
    cancel it; everything it then measures is a departure from the null.
    """

    def beat(self):
        """The pause after each step: nothing here, a click on the slide version."""

    def construct(self):
        title = Tex(
            r"Phase: the interferometer is a clock",
            font_size=FONT_TITLE,
        ).to_corner(UL)
        note = VGroup(*[
            Tex(line, font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR))
            for line in (
                r"a hand turns only while that arm is in $|e\rangle$",
                r"the readout is the angle between them",
            )
        ]).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
        note.next_to(title, DOWN, buff=0.2).align_to(title, LEFT)
        self.play(FadeIn(title), FadeIn(note), run_time=0.9)

        a = np.array([CP_T0, CP_Z, 0.0])
        b = a + RIGHT * CP_T
        b_up = b + UP * CP_ARM
        c = b_up + RIGHT * CP_T
        rate = clock_rate(CP_T)

        # One tracker per arm, advanced only over the leg on which that arm is
        # the excited one.
        kicked_first = ValueTracker(0.0)  # up at the first pulse, down at the mirror
        kicked_last = ValueTracker(0.0)  # the other way round

        dial = make_dial(CP_DIAL, r"accumulated phase")
        self.play(FadeIn(dial), run_time=0.6)

        seed = make_atom(radius=CLOCK_ATOM_RADIUS).move_to(a)
        ket_in = arm_ket(False, font_size=CP_KET_FONT)
        ket_in.next_to(seed, UP, buff=CP_KET_BUFF).to_edge(LEFT, buff=0.15)
        self.play(FadeIn(seed, scale=0.5), FadeIn(ket_in), run_time=0.5)
        self.beat()

        # --- the beamsplitter ----------------------------------------------
        self.pulse(a[0], 1, [seed])
        arm_lo = make_atom(
            radius=CLOCK_ATOM_RADIUS, opacity=SUPERPOSITION_OPACITY
        ).move_to(a)
        arm_hi = make_atom(
            KICKED_COLOR, radius=CLOCK_ATOM_RADIUS, opacity=SUPERPOSITION_OPACITY
        ).move_to(a)
        self.remove(seed)
        self.add(arm_lo, arm_hi)

        # The dial hands take the state colour too, so the one that is turning
        # is always the purple one -- which is the whole rule, shown rather
        # than asserted.
        big_lo = dial_hand(CP_DIAL, kicked_last, lighten(ATOM_COLOR))
        big_hi = dial_hand(CP_DIAL, kicked_first, lighten(KICKED_COLOR))
        hand_lo = make_clock_hand(arm_lo, kicked_last)
        hand_hi = make_clock_hand(arm_hi, kicked_first)
        self.add(hand_lo, hand_hi, big_lo, big_hi)
        # The hands count -phase (they turn forwards while the ket's
        # -omega_A T grows), so a phase the laser adds turns a hand back.
        phi1, phi2, phi3 = CP_LASER_PHASES
        self.laser_jump([(kicked_first, -phi1)])

        # --- leg 1: the kicked arm is the excited one ------------------------
        kets = [
            # inside the parallelogram: below the leg is the readout's row
            arm_ket(False, font_size=CP_KET_FONT)
            .next_to(midpoint(a, b), UP, buff=CP_KET_BUFF).shift(RIGHT * 0.3),
            # stacked: in one line it runs off the left of the frame
            arm_ket(True, r"\phi_1 - \omega_A T", CP_KET_FONT, stacked=True)
            .next_to(midpoint(a, b_up), UL, buff=CP_KET_BUFF),
        ]
        draw_legs(self, [
            (arm_lo, a, b, ATOM_COLOR),
            (arm_hi, a, b_up, KICKED_COLOR),
        ], extra=[kicked_first.animate.increment_value(rate * CP_T),
                  *[FadeIn(k) for k in kets]])
        self.beat()

        # --- the mirror: the arms swap state ----------------------------------
        # Bottom to top, following the beam. The two arms are driven in
        # opposite directions by the same pulse: the ground-state arm absorbs
        # a photon, and the excited one emits, so they swap states.
        # One pulse crosses both arms, so they swap together -- and each
        # arm's hand on the dial takes its new colour with it.
        self.pulse(b[0], 2, [arm_lo, arm_hi])
        self.play(
            state_colors(arm_lo, KICKED_COLOR),
            state_colors(arm_hi, ATOM_COLOR),
            big_lo.animate.set_color(lighten(KICKED_COLOR)),
            big_hi.animate.set_color(lighten(ATOM_COLOR)),
            run_time=0.5,
        )
        self.laser_jump([(kicked_first, +phi2), (kicked_last, -phi2)])

        # --- leg 2: and so the other hand turns --------------------------------
        kets = [
            arm_ket(True, r"\phi_2 - \omega_A T", CP_KET_FONT)
            .next_to(midpoint(b, c), DR, buff=CP_KET_BUFF),
            arm_ket(False, r"\phi_1 - \phi_2 - \omega_A T", CP_KET_FONT)
            .next_to(midpoint(b_up, c), UP, buff=CP_KET_BUFF),
        ]
        draw_legs(self, [
            (arm_lo, b, c, KICKED_COLOR),
            (arm_hi, b_up, c, ATOM_COLOR),
        ], extra=[kicked_last.animate.increment_value(rate * CP_T),
                  *[FadeIn(k) for k in kets]])
        self.beat()

        # --- recombine ----------------------------------------------------------
        self.pulse(c[0], 3, [arm_lo])
        self.laser_jump([(kicked_first, -phi3)])

        # --- and the readout ----------------------------------------------------
        # The arms are spent: the pulse has mixed them into the two output
        # states, so what leaves c is the ports, not the arms. Their hands go
        # with them -- the phase is a population from here on, and the dial is
        # where it is still shown as an angle.
        self.remove(arm_lo, arm_hi, hand_lo, hand_hi)
        # From the lower arm's hand forwards to the upper's: the laser has left
        # the upper one phi_1 - 2 phi_2 + phi_3 ahead.
        sweep, gap = phase_sweep(CP_DIAL, kicked_first, kicked_last)
        self.play(FadeIn(sweep), run_time=0.6)
        ports = draw_ports(self, c, CP_OUT, 0.5 * (1 + np.cos(gap)))
        # bottom right, as the Mach-Zehnder has it: the bottom left is the
        # pulses' captions
        self.play(Write(readout_equation().to_corner(DR)), run_time=1.0)
        self.beat()

        # What the ports have just read out: so far, only the laser's phase.
        # The note has said its piece, and the band it sits in is the only
        # one wide enough for the equation.
        self.play(FadeOut(note), run_time=0.5)
        laser_only = MathTex(
            r"\Phi", "=", r"\,\Phi_{\text{laser}}", "=",
            r"\phi_1 - 2\phi_2 + \phi_3",
            font_size=FONT_STATE,
        ).move_to(CP_TERMS)
        self.play(Write(laser_only), run_time=1.4)
        self.beat()

        # Phi_propagation: something acting on the atoms between the pulses.
        # Not replayed -- the box says where and when, and the hand of the arm
        # that was excited there (the lower one, on the second leg) sweeps on
        # by what it picked up, in step with a line crossing the box, which
        # widens the sector the laser left. The equation gains the term and
        # loses its "= phi_1 - 2 phi_2 + phi_3", which is no longer all of it.
        start, end = (b[0] + f * CP_T for f in CP_EFFECT_SPAN)
        box = Rectangle(
            width=end - start, height=CP_ARM + 2 * CP_EFFECT_PAD,
            **PERTURBATION_STYLE,
        ).move_to([(start + end) / 2, CP_Z + CP_ARM / 2, 0])
        box_label = Tex(
            r"some effect on the atoms", font_size=FONT_LEGEND,
            color=PERTURBATION_COLOR,
        ).next_to(box, UP, buff=0.75)  # clear of the top leg's ket
        budget = budget_equation(r"\Phi").move_to(CP_TERMS)
        self.play(
            FadeIn(box), FadeIn(box_label),
            ReplacementTransform(laser_only[0], budget[0]),
            ReplacementTransform(laser_only[1], budget[1]),
            ReplacementTransform(laser_only[2], budget[4]),
            FadeOut(laser_only[3:]),
            FadeIn(budget[2:4]),
            run_time=1.0,
        )
        self.effect_label = box_label  # the budget's term labels need its band
        self.bring_to_back(box)
        self.remove(sweep)
        live = always_redraw(lambda: phase_sweep(CP_DIAL, kicked_first, kicked_last)[0])
        self.add(live)
        # and the ports re-split with it
        live_ports(self, ports, c, CP_OUT,
                   lambda: ground_share(kicked_first, kicked_last))
        cursor = Line(box.get_corner(DL), box.get_corner(UL),
                      color=PERTURBATION_COLOR, stroke_width=3)
        self.play(
            kicked_last.animate.increment_value(CP_EFFECT_PHASE),
            cursor.animate.align_to(box, RIGHT),
            rate_func=linear, run_time=CP_EFFECT_TIME,
        )
        self.play(FadeOut(cursor), run_time=0.3)
        self.wait(1.0)
        self.phase_budget(budget)

    def laser_jump(self, jumps):
        """The laser writes its phase in: each (tracker, delta) hand turns by
        delta, on the spot, just after the pulse that wrote it."""
        self.play(
            *[t.animate.increment_value(d) for t, d in jumps],
            run_time=0.5,
        )

    def pulse(self, x, n, hits):
        """Pulse n, captioned with the laser phase phi_n it writes in."""
        caption = MachZehnder.pulse_caption(rf"\phi_{n}", x)
        self.play(FadeIn(caption), run_time=0.3)
        fire_vertical_pulse(self, x, hits)

    def phase_budget(self, budget):
        """Hook: ClockPhaseTerms marks up what each term of the phase is worth.

        A no-op in this scene, so the plain version stays the short one.
        """


class ClockPhaseTerms(ClockPhase):
    """ClockPhase, and then what each term of the phase it read out is worth.

    Phi = Phi_propagation + Phi_laser, with the separation term of the
    usual decomposition neglected as it is everywhere else in this talk. The
    first is the signal: omega_A times the difference in time the two arms
    spend excited, which is what a passing wave moves. The laser term is
    circled instead of struck, because it carries the laser's own phase noise
    and can be large enough to bury the first -- and it is exactly the term
    the gradiometer makes common to its two interferometers so that it cancels
    in the difference. That is the argument the gradiometer scenes go on to
    make, and this is where the term it cancels gets named.
    """

    def phase_budget(self, budget):
        self.beat()
        # The box stays to say where the signal came from; its caption goes,
        # since the terms' own labels land in the same band.
        self.play(FadeOut(self.effect_label), run_time=0.4)
        show_phase_budget(
            self, CP_TERMS, laser_struck=False, laser_label=r"noisy", eq=budget
        )
        self.wait(2.5)
