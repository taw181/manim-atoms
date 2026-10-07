"""An ultralight dark-matter field read out by a clock interferometer.

DarkMatterPhase is ClockPhase with its omega_A T null broken. An oscillating ultralight
scalar field modulates the fundamental constants, and with them the Sr clock
frequency: omega_A -> omega_A [1 + eps cos(omega_phi t + theta)]. The mirror
hands the excitation from one arm to the other halfway through, so the two
arms integrate omega_A over different stretches of the oscillation, the hands
come back to different angles and the two output ports split. Same instrument
as the gravitational-wave scenes, pointed at a different source.

DarkMatterField comes before either, and before DarkMatterScalePlot (or
DarkMatterScale): the field
on its own as a scrolling trace, and the clock transition it walks up and
down, with no interferometer yet. Its pauses go through hold(), one whole oscillation, so a slide can loop
them without a jump.
"""

import numpy as np
from manim import *

from manim_atoms.aion.style import *
from manim_atoms.interferometry.tools.clock import (
    CP_ARM,
    CP_DIAL,
    CP_OUT,
    CP_T,
    CP_T0,
    CP_Z,
    clock_rate,
    dial_hand,
    draw_ports,
    make_clock_hand,
    make_dial,
    phase_sweep,
    readout_equation,
)
from manim_atoms.interferometry.scenes.gradiometer import (
    GradiometerBase,
    RunsContinuously,
)
from manim_atoms.interferometry.tools.gradiometer import (
    cloud_sequence,
    corners,
    GR_DIAL_RADIUS,
    GR_DIALS,
    GR_LAG,
    gr_launch_time,
    GR_LOWER_Z,
    GR_PULSES,
    GR_SIGNAL,
    gr_sweep_pulse,
    GR_T,
    GR_T0,
    GR_TERMS_WIDTH,
    GR_UPPER_Z,
    gradiometer_frame,
)
from manim_atoms.interferometry.tools.pulses import fire_vertical_pulse, strobe_pulse
from manim_atoms.core.primitives import (
    draw_legs,
    make_atom,
    state_colors,
)
from manim_atoms.core.spacetime import (
    carry,
    growing_band,
    growing_trail,
    run_to,
    worldline,
)
from manim_atoms.aion.tools.uldm import (
    DG_PULSES,
    DG_T0,
    DG_TRACE_AMPLITUDE,
    DG_TRACE_X,
    DG_TRACE_Z,
    DM_OMEGA,
    dm_field,
    dm_phase,
    field_marker,
    make_field_trace,
    make_modulated_levels,
)


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
            r"Detecting ultralight dark matter",
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
            font_size=FONT_ANNOTATION,
            color=FIELD_COLOR,
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

        # result = (
        #     VGroup(
        #         MathTex(r"\Phi \neq 0", font_size=FONT_STATE),
        #         Tex(
        #             # As short as ClockPhase's, and for the same reason: it has to
        #             # stay under the dial and clear of the port labels to its left.
        #             r"different $\omega_A$ per leg",
        #             font_size=FONT_LEGEND,
        #             color=lighten(GUIDE_COLOR),
        #         ),
        #     )
        #     .arrange(DOWN, buff=0.2)
        #     .next_to(dial, DOWN, buff=0.5)
        # )
        # self.play(FadeIn(result), run_time=1.0)
        # self.beat()

        # It ends on the phase, with no L in it: this is a single clock, and
        # its phase is the oscillation integrated over two windows that no
        # longer agree. The baseline, and the scaling it brings, are
        # DarkMatterGradiometer's.
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
        draw_legs(
            self,
            [
                (arm_lo, a, b, ATOM_COLOR),
                (arm_hi, a, b_up, KICKED_COLOR),
            ],
            extra=[
                self.kicked_first.animate.set_value(leg_one),
                now.animate.set_value(b[0]),
            ],
        )
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
        draw_legs(
            self,
            [
                (arm_lo, b, c, KICKED_COLOR),
                (arm_hi, b_up, c, ATOM_COLOR),
            ],
            extra=[
                self.kicked_last.animate.set_value(leg_two),
                now.animate.set_value(c[0]),
            ],
        )
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
            self,
            c,
            CP_OUT,
            0.5 * (1 + np.cos(gap)),
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
            dot.add_updater(
                lambda m, k=k: m.set_opacity(
                    1.0 if now.get_value() >= a[0] + k * CP_T else 0.0
                )
            )
        self.add(dots)

        # Each hand turns at the modulated frequency while its own arm is
        # excited and holds once the mirror hands the excitation over. An
        # updater rather than draw_legs' extra, which is what lets them keep
        # turning through the pulses as well as along the legs.
        rate = self.rate
        self.kicked_first.add_updater(
            lambda m: m.set_value(
                dm_phase(rate, a[0], float(np.clip(now.get_value(), a[0], b[0])))
            )
        )
        self.kicked_last.add_updater(
            lambda m: m.set_value(
                dm_phase(rate, b[0], float(np.clip(now.get_value(), b[0], c[0])))
            )
        )

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

        strobe_pulse(self, now, b[0], top=b_up[1], flash_at=[b, b_up], on_arrival=swap)

        # --- recombine -------------------------------------------------------
        strobe_pulse(self, now, c[0], top=c[1], flash_at=[c])


class DarkMatterGradiometer(RunsContinuously, GradiometerBase):
    """The field through the gradiometer: where the differential phase comes from.

    DarkMatterPhase ends on one clock whose hands the field has pulled apart.
    Two of them a baseline apart, driven by one laser, see the same field --
    it is uniform over any detector -- but not at the same moment: every
    pulse reaches the far cloud L/c after the near one, so the far cloud's
    windows sit L/c further along the oscillation, it integrates a slightly
    different stretch of it, and its hands part by a different amount. The
    difference between the two dials is that shift, and the length scale
    comes into the signal exactly as it does for a gravitational wave: same
    form, epsilon where h was.

    Continuous only, on RunsContinuously's clock like the other interferometer
    slides: the claim is about *when* each cloud is pulsed, which a scene that
    stops the atoms for every pulse can only assert in a caption. Its phase
    comes from the field (dm_phase, as in DarkMatterPhase) rather than from a
    constant rate, which is why it writes its own fly.
    """

    def construct(self):
        gradiometer_frame(self, r"Ultralight dark matter, measured differentially")

        # the field, on the diagram's own time axis, marked where each pulse
        # reaches each cloud
        trace, _, dots = make_field_trace(
            [], DG_TRACE_Z, DG_TRACE_AMPLITUDE, DG_TRACE_X, DG_T0, DG_PULSES
        )
        # DG_PULSES alternates near cloud, far cloud: one colour per
        # interferometer, so the pairs read as the two clouds L/c apart
        for dot, color in zip(dots, [LOWER_PULSE_MARK_COLOR, UPPER_PULSE_MARK_COLOR] * 3):
            dot.set_color(color)
        self.play(FadeIn(trace[0]), Create(trace[1]), FadeIn(trace[2]), run_time=1.2)

        seqs = {c: cloud_sequence(GR_PULSES, self.nominal(c)) for c in ("low", "up")}
        low, up = corners(seqs["low"]), corners(seqs["up"])
        phase = {
            cloud: (ValueTracker(0.0), ValueTracker(0.0))
            for cloud in ("low", "up")
        }
        # in the scene ahead of the hands that read them (see DarkMatterPhase)
        self.add(*[t for pair in phase.values() for t in pair])

        # captioned in their clouds' mark colours, which is the key to the trace
        dials = VGroup(*[
            make_dial(GR_DIALS[c], cap, GR_DIAL_RADIUS)
            for c, cap in (
                ("low", r"$\Phi_{\text{lower}}$"),
                ("up", r"$\Phi_{\text{upper}}$"),
            )
        ])
        dials[0][1].set_color(LOWER_PULSE_MARK_COLOR)
        dials[1][1].set_color(UPPER_PULSE_MARK_COLOR)
        self.play(FadeIn(dials), run_time=0.6)

        atoms = {
            cloud: [
                make_atom(radius=CLOCK_ATOM_RADIUS).move_to(v[0]),
                make_atom(KICKED_COLOR, radius=CLOCK_ATOM_RADIUS).move_to(v[0]),
            ]
            for cloud, v in (("low", low), ("up", up))
        }
        seeds = {
            cloud: make_atom(radius=CLOCK_ATOM_RADIUS).move_to(v[0])
            for cloud, v in (("low", low), ("up", up))
        }
        self.play(*[FadeIn(m, scale=0.5) for m in seeds.values()], run_time=0.6)
        self.beat()

        # The offset between the two interferometers is where the signal
        # comes from, so it is named on the first pulse, at the far cloud.
        self.lag_note = MathTex(
            r"L/c\ \text{later}", font_size=FONT_LEGEND, color=LASER_COLOR
        ).next_to(up[0], UP, buff=0.3)

        self.low, self.up, self.seqs = low, up, seqs
        self.rate, self.phase = clock_rate(GR_T), phase
        self.atoms, self.seeds, self.dots = atoms, seeds, dots
        self.hands, self.big = [], VGroup()
        self.fly()

        # --- the readout ---------------------------------------------------
        # Each dial reads its own interferometer. The two windows each cloud
        # was excited over differ from the other cloud's by L/c, so the two
        # sectors -- and the two ports' splits -- come out different. Measured
        # from the mirror-kicked hand, as DarkMatterPhase's is, which takes
        # the short way round and leaves the two sectors comparable by eye.
        sweeps = [
            phase_sweep(GR_DIALS[c], phase[c][0], phase[c][1], GR_DIAL_RADIUS)[0]
            for c in ("low", "up")
        ]
        self.remove(*atoms["low"], *atoms["up"], *self.hands)
        self.close(sweeps)
        self.play(
            *[Flash(d[0], **{**FLASH_STYLE, "color": AREA_COLOR}) for d in dials],
            run_time=0.5,
        )
        self.beat()

        # What the instrument gets out of it. A proportionality rather than
        # the equation, as on the wave's slide: the baseline, the photon
        # kicks, and the interrogation time through a sin^2, which peaks at
        # omega_phi T = pi and is zero only at whole periods.
        signal = VGroup(
            Tex(
                r"the far cloud samples the same field $L/c$ later",
                font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR),
            ),
            MathTex(
                r"\Delta\Phi = \Phi_{\text{upper}} - \Phi_{\text{lower}}"
                r" \propto n\,L\,\varepsilon\,\sin^2(\omega_\phi T/2)",
                font_size=FONT_ANNOTATION,
            ),
        ).arrange(DOWN, buff=0.22).move_to(GR_SIGNAL)
        if signal.width > GR_TERMS_WIDTH:
            signal.scale(GR_TERMS_WIDTH / signal.width)
        self.play(FadeIn(signal), run_time=1.0)
        self.wait(2.0)

    def pulse_note(self, k):
        """The lag, named on the first pulse; the rest have nothing to add."""
        return self.lag_note if k == 0 else None

    def fly(self):
        low, up, phase = self.low, self.up, self.phase

        # Lab time starts as the first pulse leaves the laser.
        clock = self.clock = ValueTracker(gr_launch_time(GR_T0))
        self.add(clock, field_marker(
            clock, DG_TRACE_Z, DG_TRACE_AMPLITUDE, DG_TRACE_X, DG_T0
        ))
        # each marker lights as its pulse reaches its cloud
        for dot, t in zip(self.dots, DG_PULSES):
            dot.add_updater(lambda m, t=t: m.set_opacity(
                1.0 if clock.get_value() >= t - 1e-6 else 0.0
            ))
        self.add(self.dots)

        for cloud in ("low", "up"):
            v = self.vertices(cloud)
            start = np.array([clock.get_value(), self.nominal(cloud), 0.0])
            self.add(growing_trail([start, v[0]], ATOM_COLOR, clock))
            carry(self.seeds[cloud], worldline([start, v[0]]), clock)
            # Each hand turns at the field-modulated rate while its arm is
            # excited, over that cloud's own windows: index 1 is kicked at the
            # beamsplitter (excited on leg 1), index 0 at the mirror (leg 2).
            for k, (t_from, t_to) in ((1, (v[0][0], v[1][0])), (0, (v[1][0], v[3][0]))):
                phase[cloud][k].add_updater(
                    lambda m, t_from=t_from, t_to=t_to: m.set_value(dm_phase(
                        self.rate, t_from,
                        float(np.clip(clock.get_value(), t_from, t_to)), DG_T0,
                    ))
                )

        drawn = self.shoot(0, near=[low[0]], far=[up[0]],
                           on_near=lambda: self.open_arms("low"),
                           on_far=lambda: self.open_arms("up"))
        drawn = self.shoot(1, near=[low[1], low[2]], far=[up[1], up[2]],
                           fade=drawn,
                           on_near=lambda: self.mirror("low"),
                           on_far=lambda: self.mirror("up"))
        # anchored on the recombination points, an arm above the clouds'
        # starting heights, as in GradiometerContinuous
        drawn = self.shoot(2, near=[low[3]], far=[up[3]], fade=drawn,
                           z_near=low[3][1], z_far=up[3][1])
        run_to(self, clock, clock.get_value() + PULSE_LINGER,
               *[FadeOut(m) for m in drawn])

    def shoot(self, k, near, far, fade=(), on_near=None, on_far=None,
              z_near=GR_LOWER_Z, z_far=GR_UPPER_Z):
        """One pulse, at the quiet baseline's L/c: nothing here moves the light."""
        return gr_sweep_pulse(
            self, self.clock, GR_T0 + k * GR_T, near=near, far=far,
            lag=GR_LAG, note=self.pulse_note(k), fade=fade,
            z_near=z_near, z_far=z_far, on_near=on_near, on_far=on_far,
        )


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
            [DF_TRACE_X[0], DF_TRACE_Z, 0],
            [DF_TRACE_X[1], DF_TRACE_Z, 0],
            **GUIDE_STYLE,
        )
        tag = MathTex(r"\phi(t)", font_size=FONT_LEGEND, color=FIELD_COLOR)
        tag.next_to(zero, RIGHT, buff=0.2)

        def trace():
            t = now.get_value()
            return ParametricFunction(
                at,
                t_range=[t - span, t, 0.02],
                color=FIELD_COLOR,
                stroke_width=FIELD_STROKE_WIDTH,
            )

        def marker():
            return Dot(at(now.get_value()), radius=0.08, color=lighten(KICKED_COLOR))

        # The usual range: the light end is fuzzy dark matter's bound from
        # dwarf galaxies, and past the heavy end the occupation number per
        # de Broglie volume drops too low for the field to be a classical wave.
        masses = MathTex(
            r"10^{-22}\,\text{eV} \lesssim m_\phi \lesssim 1\,\text{eV}",
            font_size=FONT_ANNOTATION,
        )
        field = MathTex(
            r"\phi(t) = \phi_0 \cos\!\left(m_\phi c^2 t/\hbar\right)",
            font_size=FONT_ANNOTATION,
            color=FIELD_COLOR,
        )
        wave_note = Tex(
            r"light enough to act as one classical wave",
            font_size=FONT_LEGEND,
            color=lighten(GUIDE_COLOR),
        )
        wave_text = VGroup(masses, field, wave_note).arrange(
            DOWN, buff=0.3, aligned_edge=LEFT
        )
        wave_text.move_to(DF_TEXT, aligned_edge=UL)

        # Faded in as a still and swapped for the live trace, as the level
        # diagram is in DarkMatterPhase: an always_redraw cannot be faded.
        self.play(
            FadeIn(title),
            FadeIn(zero),
            FadeIn(tag),
            FadeIn(VGroup(trace(), marker())),
            run_time=1.0,
        )
        self.remove(*self.mobjects)
        self.add(title, zero, tag, always_redraw(trace), always_redraw(marker))
        self.play(
            FadeIn(wave_text, shift=UP * 0.15),
            now.animate.increment_value(1.0 * V),
            rate_func=linear,
            run_time=1.0,
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
            font_size=FONT_ANNOTATION,
            color=FIELD_COLOR,
        )
        clock_text = VGroup(couplings, law).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        clock_text.next_to(wave_text, DOWN, buff=0.45, aligned_edge=LEFT)

        levels, moving, detuning = make_modulated_levels(
            now,
            DF_LEVELS,
            scale=DF_LEVEL_SCALE,
            text_scale=DF_LEVEL_TEXT_SCALE,
        )
        # Swapped for the live version after the fade, for the same reason
        # as the trace -- which is why the field holds still for the fade: a
        # still of a moving level would be out of date by the time it landed.
        still = VGroup(moving(), detuning())
        self.play(
            FadeIn(clock_text, shift=UP * 0.15),
            FadeIn(levels),
            FadeIn(still),
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
            rate_func=linear,
            run_time=1.0,
        )
        self.hold()
