"""An ultralight dark-matter field read out by a clock interferometer.

DarkMatterPhase is ClockPhase with its omega_A T null broken. An oscillating ultralight
scalar field modulates the fundamental constants, and with them the Sr clock
frequency: omega_A -> omega_A [1 + eps cos(omega_phi t + theta)]. The mirror
hands the excitation from one arm to the other halfway through, so the two
arms integrate omega_A over different stretches of the oscillation, the hands
come back to different angles and the two output ports split. Same instrument
as the gravitational-wave scenes, pointed at a different source.

DarkMatterField comes before either, and before DarkMatterScale: the field
on its own as a scrolling trace, and the clock transition it walks up and
down, with no interferometer yet. Its pauses go through hold(), one whole oscillation, so a slide can loop
them without a jump.
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
    clock_rate,
    dial_hand,
    draw_ports,
    fire_vertical_pulse,
    make_clock_hand,
    make_dial,
    phase_sweep,
    readout_equation,
    strobe_pulse,
)
from aionanim.tools.primitives import (
    draw_legs,
    make_atom,
    state_colors,
)
from aionanim.tools.spacetime import (
    carry,
    growing_band,
    growing_trail,
    worldline,
)
from aionanim.tools.uldm import (
    DM_OMEGA,
    dm_field,
    dm_phase,
    field_marker,
    make_field_trace,
    make_modulated_levels,
)


# Where the scalings go: the rest of CP_READOUT's strip, right of the readout
# equation. The only clear span left, once the dial and its verdict have taken
# the right-hand side and the trace has taken the top. Wide enough for a
# proportionality and a line naming it, which is all that goes here: a full
# expression had to be shrunk to fit, and a shrunk equation at the bottom of a
# frame is one nobody reads.
CP_SCALING = np.array([1.5, -3.25, 0.0])
CP_SCALING_WIDTH = 8.4
# the band between the field's trace and the interferometer, which is where the
# modulation law goes -- it belongs to both, so it sits between them
DM_LAW = np.array([-1.8, 0.75, 0.0])


class DarkMatterPhase(Scene):
    """The same clock, with a dark-matter field oscillating through it.

    ClockPhase's interferometer is symmetric: omega_A T cancels between its
    hands, and only the laser's phase separates them. Here it does not cancel. The field modulates omega_A; the two arms are excited over
    different windows of the oscillation, so each hand winds up by its own
    integral; the angle left between them is Phi, and the last pulse turns it
    into two populations that are no longer all-or-nothing.

    Drawn on ClockPhase's geometry deliberately: nothing about the instrument
    has changed, only what is passing through it.
    """

    def beat(self):
        """The pause after each step: nothing here, a click on the slide version."""

    def construct(self):
        title = Tex(
            r"Ultralight dark matter: the phase does not cancel",
            font_size=FONT_TITLE,
        ).to_corner(UL)
        self.play(FadeIn(title), run_time=0.9)

        a = np.array([CP_T0, CP_Z, 0.0])
        b = a + RIGHT * CP_T
        b_up = b + UP * CP_ARM
        c = b_up + RIGHT * CP_T
        rate = clock_rate(CP_T)

        # --- what is passing through ---------------------------------------
        trace, bands, dots = make_field_trace([(a[0], b[0]), (b[0], c[0])])
        law = MathTex(
            r"\omega_A \to \omega_A\left[1 + \varepsilon\cos"
            r"(\omega_\phi t + \theta)\right]",
            font_size=FONT_ANNOTATION, color=FIELD_COLOR,
        ).move_to(DM_LAW)
        self.play(FadeIn(trace[0]), Create(trace[1]), FadeIn(trace[2]), run_time=1.2)
        self.play(Write(law), run_time=1.2)
        self.beat()

        # --- and what it is doing to the atom -------------------------------
        # One tracker for lab time, shared by the marker on the trace and by
        # the level diagram, and advanced over each leg by draw_legs at
        # exactly the rate the atoms cross the diagram -- which is what makes
        # the level and the leg beneath it the same instant.
        now = ValueTracker(a[0])
        levels, moving, detuning = make_modulated_levels(now)
        marker = field_marker(now)
        # Faded in as a still and then swapped for the live version, so the
        # diagram arrives as one thing. Lab time is not running yet, so the
        # swap is between two identical pictures and cannot be seen.
        still = VGroup(moving(), detuning())
        self.play(FadeIn(levels), FadeIn(still), run_time=0.8)
        self.remove(still)
        self.add(always_redraw(moving), always_redraw(detuning), marker)
        self.wait(0.4)

        # One tracker per arm, as in ClockPhase, but each advanced by the
        # integral over its own window instead of by rate * T.
        kicked_first = ValueTracker(0.0)  # arm 1: excited on leg 1
        kicked_last = ValueTracker(0.0)  # arm 2: excited on leg 2
        # A tracker only runs its updaters if it is in the scene, and it has
        # to be in it ahead of the hands that read it or they lag a frame
        # behind the phase they are drawing. Invisible either way.
        self.add(kicked_first, kicked_last)

        dial = make_dial(CP_DIAL, r"accumulated phase")
        self.play(FadeIn(dial), run_time=0.6)

        self.seed = make_atom(radius=CLOCK_ATOM_RADIUS).move_to(a)
        self.play(FadeIn(self.seed, scale=0.5), run_time=0.5)

        self.big_lo = dial_hand(CP_DIAL, kicked_last, lighten(ATOM_COLOR))
        self.big_hi = dial_hand(CP_DIAL, kicked_first, lighten(KICKED_COLOR))
        self.add(self.big_lo, self.big_hi)
        self.beat()

        # What the instrument does, which is the one part a continuous
        # variant rewrites. Everything either side of it -- the trace, the
        # levels, the dial, the readout -- is the same figure either way.
        self.corners = (a, b, b_up, c)
        self.rate = rate
        self.now, self.bands, self.dots = now, bands, dots
        self.kicked_first, self.kicked_last = kicked_first, kicked_last
        self.fly()

        # --- the readout ------------------------------------------------------
        # The hands have missed each other, so the sector between them is the
        # measurement rather than a rounding error, and both ports come out
        # populated, from the field alone.
        self.remove(self.arm_lo, self.arm_hi, self.hand_lo, self.hand_hi)
        sweep, gap = phase_sweep(CP_DIAL, kicked_last, kicked_first)
        self.play(Flash(dial[0], **{**FLASH_STYLE, "color": AREA_COLOR}), run_time=0.5)
        self.play(FadeIn(sweep), run_time=0.7)
        draw_ports(self, c, CP_OUT, 0.5 * (1 + np.cos(gap)), extra=self.port_extra())
        self.play(Write(readout_equation()), run_time=1.0)

        result = VGroup(
            MathTex(r"\Phi \neq 0", font_size=FONT_STATE),
            Tex(
                # As short as ClockPhase's, and for the same reason: it has to
                # stay under the dial and clear of the port labels to its left.
                r"different $\omega_A$ per leg",
                font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR),
            ),
        ).arrange(DOWN, buff=0.2).next_to(dial, DOWN, buff=0.5)
        self.play(FadeIn(result), run_time=1.0)
        self.beat()

        # What the instrument gets out of what the figure has drawn. One
        # interferometer has no L in it -- this one is a single clock, and its
        # phase is the oscillation integrated over two windows that no longer
        # agree. Two of them a baseline apart sample that oscillation L/c out
        # of step, and the length scale appears exactly as it does in the
        # wave's own signal: same form, epsilon where h was. That is the point
        # of putting it here rather than only on the gradiometer scenes.
        scaling = VGroup(
            MathTex(
                r"\Delta\Phi \propto n\,L\,\varepsilon\,"
                r"\sin^2(\omega_\phi T/2)",
                font_size=FONT_ANNOTATION,
            ),
            Tex(
                r"measured differentially: the wave's form, with $\varepsilon$ for $h$",
                font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR),
            ),
        ).arrange(DOWN, buff=0.18).move_to(CP_SCALING)
        if scaling.width > CP_SCALING_WIDTH:
            scaling.scale(CP_SCALING_WIDTH / scaling.width)
        self.play(FadeIn(scaling), run_time=1.0)
        self.wait(2.0)

    def split(self, at):
        """The beamsplitter's output: two arms, each carrying its own hand.

        Shared by both variants, because what the pulse produces does not
        depend on how the pulse was drawn.
        """
        self.arm_lo = make_atom(
            radius=CLOCK_ATOM_RADIUS, opacity=SUPERPOSITION_OPACITY
        ).move_to(at)
        self.arm_hi = make_atom(
            KICKED_COLOR, radius=CLOCK_ATOM_RADIUS, opacity=SUPERPOSITION_OPACITY
        ).move_to(at)
        self.hand_lo = make_clock_hand(self.arm_lo, self.kicked_last)
        self.hand_hi = make_clock_hand(self.arm_hi, self.kicked_first)
        self.remove(self.seed)
        self.add(self.arm_lo, self.arm_hi, self.hand_lo, self.hand_hi)
        return self.arm_lo, self.arm_hi

    def port_extra(self):
        """What rides along with the output ports. Nothing, unless lab time does."""
        return ()

    def fly(self):
        """Three pulses and two legs, one at a time.

        The atoms wait for each pulse to be drawn. That is the explainer's
        pacing and it is deliberate here too -- but it stops the field along
        with them, which is what DarkMatterPhaseContinuous is for.
        """
        a, b, b_up, c = self.corners
        now, bands, dots = self.now, self.bands, self.dots
        leg_one = dm_phase(self.rate, a[0], b[0])
        leg_two = dm_phase(self.rate, b[0], c[0])

        # --- the beamsplitter ----------------------------------------------
        self.play(FadeIn(dots[0], scale=0.4), run_time=0.3)
        fire_vertical_pulse(self, a[0], [self.seed])
        arm_lo, arm_hi = self.split(a)

        # --- leg 1: arm 1 is excited, over one stretch of the oscillation ---
        self.play(FadeIn(bands[0]), run_time=0.5)
        draw_legs(self, [
            (arm_lo, a, b, ATOM_COLOR),
            (arm_hi, a, b_up, KICKED_COLOR),
        ], extra=[
            self.kicked_first.animate.set_value(leg_one),
            now.animate.set_value(b[0]),
        ])
        self.beat()

        # --- the mirror: the arms swap, and so does the window ---------------
        # The same pulse that reverses the momenta hands the excitation over,
        # which is what makes the two arms sample the field at different times
        # rather than together.
        self.play(FadeIn(dots[1], scale=0.4), run_time=0.3)
        fire_vertical_pulse(self, b[0], [arm_lo, arm_hi])
        self.play(
            state_colors(arm_lo, KICKED_COLOR),
            state_colors(arm_hi, ATOM_COLOR),
            self.big_lo.animate.set_color(lighten(KICKED_COLOR)),
            self.big_hi.animate.set_color(lighten(ATOM_COLOR)),
            run_time=0.5,
        )

        # --- leg 2: arm 2 is excited, over the next, which differs ---------
        self.play(FadeIn(bands[1]), run_time=0.5)
        draw_legs(self, [
            (arm_lo, b, c, KICKED_COLOR),
            (arm_hi, b_up, c, ATOM_COLOR),
        ], extra=[
            self.kicked_last.animate.set_value(leg_two),
            now.animate.set_value(c[0]),
        ])
        self.beat()

        # --- recombine -------------------------------------------------------
        self.play(FadeIn(dots[2], scale=0.4), run_time=0.3)
        fire_vertical_pulse(self, c[0], [arm_lo])


class DarkMatterPhaseContinuous(DarkMatterPhase):
    """The same figure with lab time never stopped.

    DarkMatterPhase stops the atoms while each pulse is drawn, and since the
    x axis is lab time it stops the field with them: the trace marker, the
    level diagram and the detuning all sit still for seconds at a time while
    the thing the scene is about is supposed to be oscillating. Here one clock
    runs from the first pulse to the last and everything is a function of it,
    so the level and the leg beneath it are the same instant throughout.

    The price is the pulses. A column that is instantaneous in lab time cannot
    be given a drawn-out climb without lying about it, so it strobes: it
    appears whole on the instant and is gone in PULSE_HOLD. ClockPhase has
    already said what a pi/2 pulse does; this figure is about what is passing
    through, and it gets to spend its time on that instead.
    """

    def port_extra(self):
        # By the same amount the ports run, not to the same place: the last
        # strobe has already carried lab time a little past the final corner,
        # and what has to match is the rate, so the trace keeps step with the
        # atoms underneath it.
        return [self.now.animate.set_value(self.now.get_value() + CP_OUT)]

    def close(self, dial, sweep, gap, c):
        """All at once here, because the ports are still the atoms flying.

        The last pulse leaves two populations heading out along the diagram's
        own time axis. Holding them at the vertex while a sector fades onto a
        dial would be the stop-start pacing creeping back in at the one moment
        the scene has left, so instead they fly out of the pulse and the dial
        is read while they go -- which is also the truer picture, the angle
        between the hands and the split between the ports being one fact.
        draw_legs' extra hook already takes anything that has to happen over
        exactly that stretch of flight, so this costs a list rather than a
        mechanism.
        """
        draw_ports(
            self, c, CP_OUT, 0.5 * (1 + np.cos(gap)),
            extra=[
                *self.port_extra(),
                Flash(dial[0], **{**FLASH_STYLE, "color": AREA_COLOR}),
                FadeIn(sweep),
            ],
        )

    def fly(self):
        a, b, b_up, c = self.corners
        now, bands, dots = self.now, self.bands, self.dots

        # The washes fill in behind the legs and the trace markers light as
        # lab time reaches each pulse, so neither one costs a beat of its own.
        self.add(
            growing_band(bands[0], a[0], b[0], now),
            growing_band(bands[1], b[0], c[0], now),
        )
        for k, dot in enumerate(dots):
            dot.add_updater(lambda m, k=k: m.set_opacity(
                1.0 if now.get_value() >= a[0] + k * CP_T else 0.0
            ))
        self.add(dots)

        # Each hand turns at the modulated frequency while its own arm is
        # excited and holds once the mirror hands the excitation over. An
        # updater rather than draw_legs' extra, which is what lets them keep
        # turning through the pulses as well as along the legs.
        rate = self.rate
        self.kicked_first.add_updater(lambda m: m.set_value(
            dm_phase(rate, a[0], float(np.clip(now.get_value(), a[0], b[0])))
        ))
        self.kicked_last.add_updater(lambda m: m.set_value(
            dm_phase(rate, b[0], float(np.clip(now.get_value(), b[0], c[0])))
        ))

        # --- the beamsplitter ----------------------------------------------
        # On the instant, not after it: the arms are put on their worldlines
        # as the pulse arrives, so they are already moving while the column is
        # still on the screen.
        def split():
            arm_lo, arm_hi = self.split(a)
            carry(arm_lo, worldline([a, b, c]), now)
            carry(arm_hi, worldline([a, b_up, c]), now)
            # One trail per leg rather than per arm: the two arms swap states
            # at the mirror, so the colour belongs to the leg.
            self.add(
                growing_trail([a, b], ATOM_COLOR, now),
                growing_trail([b, c], KICKED_COLOR, now),
                growing_trail([a, b_up], KICKED_COLOR, now),
                growing_trail([b_up, c], ATOM_COLOR, now),
            )

        strobe_pulse(self, now, a[0], top=a[1], flash_at=[a], on_arrival=split)

        # --- the mirror -----------------------------------------------------
        def swap():
            self.arm_lo[0].set_fill(KICKED_COLOR).set_stroke(lighten(KICKED_COLOR))
            self.arm_hi[0].set_fill(ATOM_COLOR).set_stroke(lighten(ATOM_COLOR))
            self.big_lo.set_color(lighten(KICKED_COLOR))
            self.big_hi.set_color(lighten(ATOM_COLOR))

        strobe_pulse(
            self, now, b[0], top=b_up[1], flash_at=[b, b_up], on_arrival=swap
        )

        # --- recombine -------------------------------------------------------
        strobe_pulse(self, now, c[0], top=c[1], flash_at=[c])


# --- DarkMatterField geometry ----------------------------------------------
# The field on its own, before any interferometer: a trace scrolling along the
# top strip, what it is on the left below it, and on the right the clock
# transition it drags. The trace is an oscilloscope rather than a space-time
# diagram -- the newest instant sits at its right-hand end, where a marker
# rides it -- so it can run for as long as a slide is held without walking
# off the frame.
DF_TRACE_Z = 2.1
DF_TRACE_AMPLITUDE = 0.55
DF_TRACE_X = (-6.3, 5.9)  # oldest instant on the left, now on the right
DF_TEXT = np.array([-6.3, 0.55, 0.0])  # upper-left corner of the text column
DF_LEVELS = np.array([3.7, -1.25, 0.0])  # the modulated transition
# DarkMatterPhase's level diagram, blown up: here it has the whole right half
# below the trace to itself.
DF_LEVEL_SCALE = 2.0
DF_LEVEL_TEXT_SCALE = 1.35  # its labels grow less, to sit with the text column
# One period of the field, in the lab time that drives both the trace and the
# levels. Advanced at V, so a slide held on this scene loops seamlessly over
# exactly one oscillation.
DF_PERIOD = TAU / DM_OMEGA


class DarkMatterField(Scene):
    """What an ultralight dark-matter field is, and why a clock can see it.

    Light enough and the field has so many quanta per de Broglie volume that
    it acts as one classical wave oscillating at its Compton frequency.
    Coupled to the electron mass or the fine-structure constant, it walks the
    Sr clock transition up and down with it -- which is the modulation
    DarkMatterPhase then feeds into the interferometer. Here there is no
    interferometer yet: only the field, and the level it moves.
    """

    def hold(self):
        """Let the field run through one whole oscillation.

        One period exactly, so the frame it ends on is the one it started on:
        a slide can loop it for as long as it is held without a jump.
        """
        self.play(
            self.now.animate.increment_value(DF_PERIOD),
            rate_func=linear,
            run_time=DF_PERIOD / V,
        )

    def construct(self):
        title = Tex(
            r"Ultralight dark matter: a field that oscillates",
            font_size=FONT_TITLE,
        ).to_corner(UL)

        # --- the field ------------------------------------------------------
        self.now = now = ValueTracker(CP_T0)
        span = DF_TRACE_X[1] - DF_TRACE_X[0]

        def at(t):
            """Where the field at lab time t sits on the scrolling trace."""
            x = DF_TRACE_X[1] - (now.get_value() - t)
            return [x, DF_TRACE_Z + DF_TRACE_AMPLITUDE * dm_field(t), 0]

        zero = DashedLine(
            [DF_TRACE_X[0], DF_TRACE_Z, 0], [DF_TRACE_X[1], DF_TRACE_Z, 0],
            **GUIDE_STYLE,
        )
        tag = MathTex(r"\phi(t)", font_size=FONT_LEGEND, color=FIELD_COLOR)
        tag.next_to(zero, RIGHT, buff=0.2)

        def trace():
            t = now.get_value()
            return ParametricFunction(
                at, t_range=[t - span, t, 0.02],
                color=FIELD_COLOR, stroke_width=FIELD_STROKE_WIDTH,
            )

        def marker():
            return Dot(at(now.get_value()), radius=0.08, color=lighten(KICKED_COLOR))

        field = MathTex(
            r"\phi(t) = \phi_0 \cos\!\left(m_\phi c^2 t/\hbar\right)",
            font_size=FONT_ANNOTATION, color=FIELD_COLOR,
        )
        wave_note = Tex(
            r"light enough to act as one classical wave",
            font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR),
        )
        wave_text = VGroup(field, wave_note).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        wave_text.move_to(DF_TEXT, aligned_edge=UL)

        # Faded in as a still and swapped for the live trace, as the level
        # diagram is in DarkMatterPhase: an always_redraw cannot be faded.
        self.play(
            FadeIn(title), FadeIn(zero), FadeIn(tag),
            FadeIn(VGroup(trace(), marker())),
            run_time=1.0,
        )
        self.remove(*self.mobjects)
        self.add(title, zero, tag, always_redraw(trace), always_redraw(marker))
        self.play(
            FadeIn(wave_text, shift=UP * 0.15),
            now.animate.increment_value(1.0 * V),
            rate_func=linear, run_time=1.0,
        )
        self.hold()

        # --- what it does to a clock ----------------------------------------
        couplings = Tex(
            r"Coupling to standard model fields?",
            font_size=FONT_ANNOTATION,
        )
        law = MathTex(
            r"\omega_A \to \omega_A\left[1 + \varepsilon\cos"
            r"(\omega_\phi t + \theta)\right]",
            font_size=FONT_ANNOTATION, color=FIELD_COLOR,
        )
        clock_text = VGroup(couplings, law).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        clock_text.next_to(wave_text, DOWN, buff=0.45, aligned_edge=LEFT)

        levels, moving, detuning = make_modulated_levels(
            now, DF_LEVELS, scale=DF_LEVEL_SCALE, text_scale=DF_LEVEL_TEXT_SCALE,
        )
        # Swapped for the live version after the fade, for the same reason
        # as the trace -- which is why the field holds still for the fade: a
        # still of a moving level would be out of date by the time it landed.
        still = VGroup(moving(), detuning())
        self.play(
            FadeIn(clock_text, shift=UP * 0.15), FadeIn(levels), FadeIn(still),
            run_time=1.0,
        )
        self.remove(still)
        self.add(always_redraw(moving), always_redraw(detuning))
        self.hold()

        # --- and so --------------------------------------------------------
        verdict = Tex(
            r"a clock transition reads the field directly",
            font_size=FONT_ANNOTATION,
        ).next_to(clock_text, DOWN, buff=0.45, aligned_edge=LEFT)
        self.play(
            FadeIn(verdict, shift=UP * 0.15),
            now.animate.increment_value(1.0 * V),
            rate_func=linear, run_time=1.0,
        )
        self.hold()
