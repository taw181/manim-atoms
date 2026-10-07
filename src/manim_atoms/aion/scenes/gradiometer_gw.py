"""A gravitational wave passing through the gradiometer.

GradiometerGW and GradiometerGWStretch are the same figure with a wave passing
through, drawn the two ways people draw one. GradiometerGW modulates the light
travel time and leaves the freely falling atoms on the worldlines they already
had, which is where the signal actually comes from; GradiometerGWStretch bows
the worldlines so the baseline visibly breathes, which is the picture most
people carry. The same h(t) runs along the top of both, they take their pulse
timing from the same place, and so their dials read the same phase.

The *Continuous variants run the whole diagram on one lab clock (see
manim_atoms.core.spacetime), through WaveRunsContinuously: the gradiometer's
RunsContinuously with the pulses fired where the wave has them arriving.
Both scenes are GradiometerBases (manim_atoms.interferometry.scenes.gradiometer).
"""

import numpy as np
from manim import *

from manim_atoms.aion.style import *
from manim_atoms.interferometry.scenes.gradiometer import GradiometerBase, RunsContinuously
from manim_atoms.core.primitives import (
    draw_legs,
    make_atom,
    make_guide,
    state_colors,
)
from manim_atoms.core.spacetime import (
    run_to,
    worldline,
    wound,
    carry,
    growing_trail,
    draw_wavy_legs,
)
from manim_atoms.interferometry.tools.gradiometer import (
    cloud_legs,
    cloud_sequence,
    corners,
    GR_DIAL_RADIUS,
    GR_DIALS,
    gr_fire_pulse,
    GR_LOWER_Z,
    GR_MID_Z,
    GR_SIGNAL,
    gr_sweep_pulse,
    GR_T,
    GR_TERMS_WIDTH,
    GR_UPPER_Z,
    gradiometer_frame,
)
from manim_atoms.interferometry.tools.clock import (
    clock_rate,
    make_dial,
    phase_sweep,
)
from manim_atoms.aion.tools.gradiometer_gw import (
    arrival_dots,
    arrival_note,
    gw_arrival_lags,
    gw_displacement,
    gw_lag,
    GW_PULSES,
    gw_pulses,
    GW_TRACE_X,
    make_strain_trace,
    quiet_arrival,
    strain_marker,
)


class GradiometerGW(GradiometerBase):
    """A wave modulates the light travel time, so the pulses arrive early or late.

    The honest picture of what AION measures. The atoms are freely falling test
    masses, so their worldlines keep the shape they had in Gradiometer; what
    the wave changes is L/c, and with it the retarded time at which the laser
    writes its phase into the upper interferometer.
    """

    def construct(self):
        gradiometer_frame(
            self, r"A gravitational wave modulates the light travel time"
        )

        trace, dots = make_strain_trace()
        self.play(FadeIn(trace[0]), Create(trace[1]), FadeIn(trace[2]), run_time=1.2)
        self.beat()

        lags = [gw_lag(t) for t in GW_PULSES]  # cloud to cloud, i.e. L/c
        low_lags = gw_arrival_lags(GR_LOWER_Z)
        up_lags = gw_arrival_lags(GR_UPPER_Z)
        seqs = {c: cloud_sequence(gw_pulses(), self.nominal(c)) for c in ("low", "up")}
        low, up = corners(seqs["low"]), corners(seqs["up"])

        # What the wave has done, in one number per interferometer: the upper
        # one's two pulse intervals are no longer equal, so its arms no longer
        # spend equal time excited.
        rate = clock_rate(GR_T)
        excited = {
            cloud: (v[1][0] - v[0][0], v[3][0] - v[2][0])
            for cloud, v in (("low", low), ("up", up))
        }
        phase = {
            cloud: (ValueTracker(0.0), ValueTracker(0.0))
            for cloud in ("low", "up")
        }

        dials = VGroup(*[
            make_dial(GR_DIALS[c], cap, GR_DIAL_RADIUS)
            for c, cap in (
                ("low", r"$\Phi_{\text{lower}}$"),
                ("up", r"$\Phi_{\text{upper}}$"),
            )
        ])
        self.play(FadeIn(dials), run_time=0.6)

        # --- the two clouds ----------------------------------------------
        atoms = {
            "low": [
                make_atom(radius=CLOCK_ATOM_RADIUS).move_to(low[0]),
                make_atom(KICKED_COLOR, radius=CLOCK_ATOM_RADIUS).move_to(low[0]),
            ],
            "up": [
                make_atom(radius=CLOCK_ATOM_RADIUS).move_to(up[0]),
                make_atom(KICKED_COLOR, radius=CLOCK_ATOM_RADIUS).move_to(up[0]),
            ],
        }
        seeds = {
            "low": make_atom(radius=CLOCK_ATOM_RADIUS).move_to(low[0]),
            "up": make_atom(radius=CLOCK_ATOM_RADIUS).move_to(up[0]),
        }
        self.play(
            FadeIn(seeds["low"], scale=0.5), FadeIn(seeds["up"], scale=0.5),
            run_time=0.6,
        )
        self.beat()

        # A tracker only runs its updaters if it is in the scene, and it has to
        # be in it ahead of the hands that read it or they lag a frame behind
        # the phase they are drawing. Invisible either way, and the stop-start
        # sequence neither needs nor minds it.
        self.add(*[t for pair in phase.values() for t in pair])

        self.low, self.up, self.seqs = low, up, seqs
        self.lags, self.low_lags, self.up_lags = lags, low_lags, up_lags
        self.rate, self.excited, self.phase = rate, excited, phase
        self.atoms, self.seeds, self.dots = atoms, seeds, dots
        self.hands, self.big = [], VGroup()
        self.fly()

        # --- the readout ---------------------------------------------------
        # Each face carries its own interferometer's phase, so what is read
        # out is the difference between the two -- which stays the measurement
        # if the lower one's hands ever come apart as well.
        sweeps = []
        for cloud in ("low", "up"):
            sweep, gap = phase_sweep(
                GR_DIALS[cloud], phase[cloud][1], phase[cloud][0], GR_DIAL_RADIUS
            )
            if gap > 0.01:
                sweeps.append(sweep)
        # And the same angle as a population. The wave pulled the far cloud's
        # two pulse intervals further apart than the near cloud's, so the two
        # interferometers split their ports by different amounts. That
        # difference is the signal: one laser, two clocks, and only what is
        # not common to both survives.
        self.remove(*atoms["low"], *atoms["up"], *self.hands)
        self.close(sweeps)
        self.beat()

        signal = VGroup(
            Tex(
                r"the wave changes the light travel time, more for the far cloud",
                font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR),
            ),
            # A proportionality rather than the equation: what a talk needs
            # off this slide is which knobs it turns, and the prefactor
            # 2 omega_A / c is fixed the moment the atom is chosen. What is
            # left is the baseline, the photon kicks, and the interrogation
            # time -- the last through a sin^2 rather than a power: the
            # response peaks at omega_GW T = pi, where the pulses would land on
            # crest, trough and crest, and falls away as T^2 well below it. The
            # wave drawn is off that peak on purpose, so the detector does not
            # read as working only for a tuned wave.
            MathTex(
                r"\Delta\Phi = \Phi_{\text{upper}} - \Phi_{\text{lower}}"
                r" \propto n\,L\,h\,\sin^2(\omega_{\text{GW}} T/2)",
                font_size=FONT_ANNOTATION,
            ),
        ).arrange(DOWN, buff=0.22).move_to(GR_SIGNAL)
        if signal.width > GR_TERMS_WIDTH:
            signal.scale(GR_TERMS_WIDTH / signal.width)
        self.play(FadeIn(signal), run_time=1.0)
        self.wait(2.0)

    # --- what the variants, and the stretched picture, agree on ----------
    # The wave in this scene changes the light travel time and nothing else,
    # so the clouds sit still on the baseline and every pulse crosses them
    # where the baseline says. GradiometerGWStretch draws the other half of
    # the same wave -- it moves the clouds -- and overrides exactly these,
    # with GradiometerBase's displacement, which is the whole difference
    # between the two pictures once the pulse timing is shared.
    REFERENCE = True  # the dashed quiet-baseline ghost beside each pulse

    def rest(self, cloud):
        """Where the cloud is when lab time starts."""
        return self.nominal(cloud) + self.displacement(cloud)(GW_PULSES[0])

    def crossing(self, cloud, k):
        """Where the cloud is when pulse k reaches it."""
        return self.nominal(cloud)

    def dot_times(self):
        """The lab time each trace marker stands for, in self.dots' order:
        here one per pulse, at its firing."""
        return GW_PULSES

    def pulse_dots(self, k):
        """The trace markers that belong to pulse k."""
        return [self.dots[k]]

    def pulse_note(self, k):
        """What pulse k is captioned with, if anything.

        The arrivals are what this picture is about, so the first two are each
        named against the dashed ghost beside them -- and the ghost has to be
        named once too, or "late" is late against nothing in particular. The
        third has nothing left to say that the two before it have not.
        """
        if k == 0:
            return VGroup(
                arrival_note(self.up[0], self.lags[0]),
                Tex(
                    r"no wave", font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR)
                ).move_to([GW_PULSES[0] + 1.25, GR_MID_Z, 0]),
            )
        if k == 1:
            return arrival_note(self.up[1], self.lags[1])
        return None

    def fly(self):
        """Three pulses and two legs, one at a time.

        The atoms wait for each pulse to be drawn, which buys the pulse the
        wall time to be read and costs the wave the right to keep moving while
        it is. GradiometerGWContinuous makes the other trade.
        """
        low, up, lags = self.low, self.up, self.lags
        atoms, phase, rate, excited = self.atoms, self.phase, self.rate, self.excited

        # --- pulse 1: the beamsplitter, arriving late ----------------------
        self.play(FadeIn(self.dots[0], scale=0.4), run_time=0.3)
        gr_fire_pulse(
            self, GW_PULSES[0] + self.low_lags[0],
            flash=[self.seeds["low"], self.seeds["up"]],
            lag=lags[0], reference=True, quiet_x=quiet_arrival(0),
            note=self.pulse_note(0),
        )
        self.open_arms("low")
        self.open_arms("up")

        draw_legs(self, [
            *cloud_legs(self.seqs["low"], 0, atoms["low"]),
            *cloud_legs(self.seqs["up"], 0, atoms["up"]),
        ], extra=[
            phase[c][1].animate.set_value(rate * excited[c][0])
            for c in ("low", "up")
        ])
        self.beat()

        # --- pulse 2: the mirror, arriving early --------------------------
        self.play(FadeIn(self.dots[1], scale=0.4), run_time=0.3)
        gr_fire_pulse(
            self, GW_PULSES[1] + self.low_lags[1],
            flash=[a for p in atoms.values() for a in p],
            lag=lags[1], reference=True, quiet_x=quiet_arrival(1),
            note=self.pulse_note(1),
        )
        big = self.big
        self.play(
            *[state_colors(p[0], KICKED_COLOR) for p in atoms.values()],
            *[state_colors(p[1], ATOM_COLOR) for p in atoms.values()],
            *[big[k].animate.set_color(lighten(KICKED_COLOR)) for k in (0, 2)],
            *[big[k].animate.set_color(lighten(ATOM_COLOR)) for k in (1, 3)],
            run_time=0.5,
        )
        draw_legs(self, [
            *cloud_legs(self.seqs["low"], 1, atoms["low"]),
            *cloud_legs(self.seqs["up"], 1, atoms["up"]),
        ], extra=[
            phase[c][0].animate.set_value(rate * excited[c][1])
            for c in ("low", "up")
        ])
        self.beat()

        # --- pulse 3: recombine -------------------------------------------
        self.play(FadeIn(self.dots[2], scale=0.4), run_time=0.3)
        gr_fire_pulse(
            self, GW_PULSES[2] + self.low_lags[2],
            flash=[atoms["low"][0], atoms["up"][0]],
            lag=lags[2], reference=True, quiet_x=quiet_arrival(2),
        )


class WaveRunsContinuously(RunsContinuously):
    """RunsContinuously for the scenes with a wave passing through: lab time
    starts as the first pulse leaves the laser, the strain trace's marker
    rides on it, and every pulse is fired where the wave has it arriving."""

    def fly(self):
        low, up, lags = self.low, self.up, self.lags

        # Lab time starts when the first pulse leaves the laser, so the first
        # thing the scene does is send it.
        clock = self.clock = ValueTracker(GW_PULSES[0])
        self.add(clock, strain_marker(clock))
        for dot, t in zip(self.dots, self.dot_times()):
            dot.add_updater(lambda m, t=t: m.set_opacity(
                1.0 if clock.get_value() >= t - 1e-6 else 0.0
            ))
        self.add(self.dots)

        for cloud in ("low", "up"):
            v = self.vertices(cloud)
            disp = self.displacement(cloud)
            # The seeds are already falling when the pulse is fired, so they
            # fly the stretch between the laser's column and their own corner
            # rather than waiting on it.
            start = np.array([GW_PULSES[0], self.rest(cloud), 0.0])
            self.add(growing_trail([start, v[0]], ATOM_COLOR, clock, disp))
            carry(self.seeds[cloud], worldline([start, v[0]], disp), clock)
            self.phase[cloud][1].add_updater(
                wound(clock, self.rate, v[0][0], v[1][0])
            )
            self.phase[cloud][0].add_updater(
                wound(clock, self.rate, v[2][0], v[3][0])
            )

        # --- pulse 1: the beamsplitter -------------------------------------
        drawn = self.shoot(
            0, near=[low[0]], far=[up[0]],
            on_near=lambda: self.open_arms("low"),
            on_far=lambda: self.open_arms("up"),
        )

        # --- pulse 2: the mirror, arriving early --------------------------
        # cloud_sequence puts a cloud's two arms at the same time, so one flash
        # does for both even though the upper arm is an arm's height further
        # up the column. The slope that separates them is a fortieth of the
        # one the figure is about.
        drawn = self.shoot(
            1, near=[low[1], low[2]], far=[up[1], up[2]], fade=drawn,
            on_near=lambda: self.mirror("low"),
            on_far=lambda: self.mirror("up"),
        )

        # --- pulse 3: recombine -------------------------------------------
        drawn = self.shoot(2, near=[low[3]], far=[up[3]], fade=drawn)
        run_to(
            self, clock, clock.get_value() + PULSE_LINGER,
            *[FadeOut(m) for m in drawn],
        )

    def shoot(self, k, near, far, fade=(), on_near=None, on_far=None):
        """One pulse, fired the way this scene's geometry has it arriving."""
        return gr_sweep_pulse(
            self, self.clock, GW_PULSES[k] + self.low_lags[k],
            near=near, far=far, lag=self.lags[k],
            reference=self.REFERENCE, quiet_x=quiet_arrival(k),
            note=self.pulse_note(k),
            z_near=self.crossing("low", k), z_far=self.crossing("up", k),
            fade=fade, on_near=on_near, on_far=on_far,
        )


class GradiometerGWContinuous(WaveRunsContinuously, GradiometerGW):
    """GradiometerGW with the pulses climbing while the atoms fly."""


class GradiometerGWStretch(GradiometerGW):
    """The same wave drawn as a stretching baseline, for comparison.

    The picture most people carry: the wave pushes the ends of the baseline
    apart and together, so L breathes. It is drawn from the laser's frame,
    so the near cloud barely moves and the far one swings against it. It is the proper-distance picture rather than the one the
    experiment reads out -- GradiometerGW is what the phase actually comes
    from -- but the two are the same wave, and the same h(t) runs above both.

    A subclass of it for the three things that differ: the clouds move, so a
    pulse crosses them where the wave has put them rather than where the
    baseline says; and with the bow itself on the page there is nothing for a
    dashed ghost to be a reference against.
    """

    REFERENCE = False

    def displacement(self, cloud):
        z0 = self.nominal(cloud)
        return lambda t: gw_displacement(t, z0)

    def crossing(self, cloud, k):
        lags = self.low_lags if cloud == "low" else self.up_lags
        return self.nominal(cloud) + self.displacement(cloud)(GW_PULSES[k] + lags[k])

    def pulse_note(self, k):
        """The bow is the claim here, so it is named once and not again.

        Nothing in this picture arrives early or late -- it is drawn in proper
        distance, where what the wave does is move the clouds -- so the
        arrival captions would be naming something the frame is not showing.

        It hangs off the far cloud's rest line rather than the cloud: the wave
        has the cloud well above that line at the first pulse, and a caption
        placed off the cloud lands on top of the line.
        """
        if k:
            return None
        return Tex(
            r"$L$ stretches and squeezes", font_size=FONT_LEGEND, color=STRAIN_COLOR
        ).next_to([self.up[0][0], GR_UPPER_Z, 0], DOWN, buff=0.2).shift(RIGHT * 0.9)

    def dot_times(self):
        return self.arrivals

    def pulse_dots(self, k):
        return [self.dots[2 * k], self.dots[2 * k + 1]]

    def port_slope(self, cloud):
        """The kicked leg's slope with the bow taken back out.

        The ports are straight lines standing for atoms flying out to be
        imaged, not part of the bowed interferometer, so they carry p + hbar k
        and nothing of the wave: read off the bowed corners, the lower pair
        would leave at whatever the wave had last done to that leg -- flattened
        here, enough to put its two port atoms on top of each other.
        """
        v = self.low if cloud == "low" else self.up
        disp = self.displacement(cloud)
        bow = (disp(v[3][0]) - disp(v[1][0])) / (v[3][0] - v[1][0])
        return super().port_slope(cloud) - bow

    def construct(self):
        baseline, baseline_label = gradiometer_frame(
            self, r"A gravitational wave stretches and squeezes the baseline"
        )

        trace, dots = make_strain_trace(r"\Delta L(t)")
        self.play(FadeIn(trace[0]), Create(trace[1]), FadeIn(trace[2]), run_time=1.2)

        # Where each cloud would sit with nothing passing through, so the bow
        # is visibly a departure from something rather than just a wobble.
        rest = VGroup(*[
            make_guide([GW_TRACE_X[0], z, 0], [GW_TRACE_X[1], z, 0])
            for z in (GR_LOWER_Z, GR_UPPER_Z)
        ])
        self.play(FadeIn(rest), run_time=0.6)
        self.beat()

        def low_disp(t):
            return gw_displacement(t, GR_LOWER_Z)

        def up_disp(t):
            return gw_displacement(t, GR_UPPER_Z)

        lags = [gw_lag(t) for t in GW_PULSES]  # cloud to cloud, i.e. L/c
        low_lags = gw_arrival_lags(GR_LOWER_Z)
        up_lags = gw_arrival_lags(GR_UPPER_Z)
        # Corners ride the wave; the legs between them bow to match.
        seqs = {
            "low": cloud_sequence(gw_pulses(), GR_LOWER_Z, low_disp),
            "up": cloud_sequence(gw_pulses(), GR_UPPER_Z, up_disp),
        }
        low, up = corners(seqs["low"]), corners(seqs["up"])
        # The trace marks each pulse twice, as it reaches each cloud, so the
        # two interferometers' samples of the wave sit L/c apart on it.
        self.arrivals = [
            t for k in range(3)
            for t in (GW_PULSES[k] + low_lags[k], GW_PULSES[k] + up_lags[k])
        ]
        dots = arrival_dots(self.arrivals[0::2], self.arrivals[1::2])

        # The pulses land where they landed in GradiometerGW, so the arms come
        # apart by the same amount and the dial reads the same phase.
        rate = clock_rate(GR_T)
        excited = {
            cloud: (v[1][0] - v[0][0], v[3][0] - v[2][0])
            for cloud, v in (("low", low), ("up", up))
        }
        phase = {
            cloud: (ValueTracker(0.0), ValueTracker(0.0))
            for cloud in ("low", "up")
        }
        dials = VGroup(*[
            make_dial(GR_DIALS[c], cap, GR_DIAL_RADIUS)
            for c, cap in (
                ("low", r"$\Phi_{\text{lower}}$"),
                ("up", r"$\Phi_{\text{upper}}$"),
            )
        ])
        # captioned in their clouds' mark colours: the key to the trace
        dials[0][1].set_color(LOWER_PULSE_MARK_COLOR)
        dials[1][1].set_color(UPPER_PULSE_MARK_COLOR)
        self.play(FadeIn(dials), run_time=0.6)

        atoms = {
            "low": [
                make_atom(radius=CLOCK_ATOM_RADIUS).move_to(low[0]),
                make_atom(KICKED_COLOR, radius=CLOCK_ATOM_RADIUS).move_to(low[0]),
            ],
            "up": [
                make_atom(radius=CLOCK_ATOM_RADIUS).move_to(up[0]),
                make_atom(KICKED_COLOR, radius=CLOCK_ATOM_RADIUS).move_to(up[0]),
            ],
        }
        seeds = {
            "low": make_atom(radius=CLOCK_ATOM_RADIUS).move_to(low[0]),
            "up": make_atom(radius=CLOCK_ATOM_RADIUS).move_to(up[0]),
        }

        # The L arrow is the baseline as it is *now*: the separation of the
        # two clouds at the time the atoms have reached, so it stretches and
        # squeezes while they fly and holds while a pulse is in flight. Read
        # off the far cloud's ground-state atom, which exists from the start
        # and sits wherever the sequence has got to.
        def baseline_now():
            t = atoms["up"][0].get_x()
            x = baseline.get_x()
            return DoubleArrow(
                [x, GR_LOWER_Z + low_disp(t), 0],
                [x, GR_UPPER_Z + up_disp(t), 0],
                buff=0,
                stroke_width=3,
                color=lighten(GUIDE_COLOR),
                max_tip_length_to_length_ratio=0.06,
            )

        self.play(
            FadeIn(seeds["low"], scale=0.5), FadeIn(seeds["up"], scale=0.5),
            Transform(baseline, baseline_now()),
            baseline_label.animate.next_to(baseline_now(), LEFT, buff=0.12),
            run_time=0.6,
        )
        baseline.add_updater(lambda m: m.become(baseline_now()))
        baseline_label.add_updater(lambda m: m.next_to(baseline, LEFT, buff=0.12))
        self.beat()
        self.add(*[t for pair in phase.values() for t in pair])

        self.low, self.up, self.seqs = low, up, seqs
        self.lags, self.low_lags, self.up_lags = lags, low_lags, up_lags
        self.rate, self.excited, self.phase = rate, excited, phase
        self.atoms, self.seeds, self.dots = atoms, seeds, dots
        self.hands, self.big = [], VGroup()
        self.fly()

        # --- the readout -----------------------------------------------------
        # Each face carries its own interferometer's phase, so what is read
        # out is the difference between the two -- which stays the measurement
        # if the lower one's hands ever come apart as well.
        sweeps = []
        for cloud in ("low", "up"):
            sweep, gap = phase_sweep(
                GR_DIALS[cloud], phase[cloud][1], phase[cloud][0], GR_DIAL_RADIUS
            )
            if gap > 0.01:
                sweeps.append(sweep)
        # And the same angle as a population. The wave pulled the far cloud's
        # two pulse intervals further apart than the near cloud's, so the two
        # interferometers split their ports by different amounts. That
        # difference is the signal: one laser, two clocks, and only what is
        # not common to both survives.
        self.remove(*atoms["low"], *atoms["up"], *self.hands)
        self.close(sweeps)
        self.beat()

        signal = VGroup(
            Tex(
                r"the wave changes the light travel time, more for the far cloud",
                font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR),
            ),
            # A proportionality rather than the equation: what a talk needs
            # off this slide is which knobs it turns, and the prefactor
            # 2 omega_A / c is fixed the moment the atom is chosen. What is
            # left is the baseline, the photon kicks, and the interrogation
            # time -- the last through a sin^2 rather than a power: the
            # response peaks at omega_GW T = pi, where the pulses would land on
            # crest, trough and crest, and falls away as T^2 well below it. The
            # wave drawn is off that peak on purpose, so the detector does not
            # read as working only for a tuned wave.
            MathTex(
                r"\Delta\Phi = \Phi_{\text{upper}} - \Phi_{\text{lower}}"
                r" \propto n\,L\,h\,\sin^2(\omega_{\text{GW}} T/2)",
                font_size=FONT_ANNOTATION,
            ),
        ).arrange(DOWN, buff=0.22).move_to(GR_SIGNAL)
        if signal.width > GR_TERMS_WIDTH:
            signal.scale(GR_TERMS_WIDTH / signal.width)
        self.play(FadeIn(signal), run_time=1.0)
        self.wait(2.0)

    def fly(self):
        """Three pulses and two legs, one at a time, on bowed worldlines."""
        low, up, lags = self.low, self.up, self.lags
        atoms, phase, rate, excited = self.atoms, self.phase, self.rate, self.excited
        low_disp, up_disp = self.displacement("low"), self.displacement("up")

        def shoot(k, flash, note=None):
            self.play(*[FadeIn(d, scale=0.4) for d in self.pulse_dots(k)], run_time=0.3)
            gr_fire_pulse(
                self, GW_PULSES[k] + self.low_lags[k], flash=flash, lag=lags[k],
                note=note,
                z_near=self.crossing("low", k), z_far=self.crossing("up", k),
            )

        # --- pulse 1: the beamsplitter -------------------------------------
        shoot(0, [self.seeds["low"], self.seeds["up"]], note=self.pulse_note(0))
        self.open_arms("low")
        self.open_arms("up")

        draw_wavy_legs(self, [
            *cloud_legs(self.seqs["low"], 0, atoms["low"], wavy=True),
            *cloud_legs(self.seqs["up"], 0, atoms["up"], wavy=True),
        ], extra=[
            phase[c][1].animate.set_value(rate * excited[c][0])
            for c in ("low", "up")
        ])
        self.beat()

        # --- pulse 2: the mirror --------------------------------------------
        shoot(1, [a for p in atoms.values() for a in p])
        big = self.big
        self.play(
            *[state_colors(p[0], KICKED_COLOR) for p in atoms.values()],
            *[state_colors(p[1], ATOM_COLOR) for p in atoms.values()],
            *[big[k].animate.set_color(lighten(KICKED_COLOR)) for k in (0, 2)],
            *[big[k].animate.set_color(lighten(ATOM_COLOR)) for k in (1, 3)],
            run_time=0.5,
        )
        draw_wavy_legs(self, [
            *cloud_legs(self.seqs["low"], 1, atoms["low"], wavy=True),
            *cloud_legs(self.seqs["up"], 1, atoms["up"], wavy=True),
        ], extra=[
            phase[c][0].animate.set_value(rate * excited[c][1])
            for c in ("low", "up")
        ])
        self.beat()

        # --- pulse 3: recombine ---------------------------------------------
        shoot(2, [atoms["low"][0], atoms["up"][0]])


class GradiometerGWStretchContinuous(WaveRunsContinuously, GradiometerGWStretch):
    """GradiometerGWStretch with the pulses climbing while the atoms fly.

    Free, once the continuous sequence is a mixin and this picture's two
    differences are methods: the bow goes into the worldlines the atoms are
    carried along and into the trails behind them, exactly as it goes into
    draw_wavy_legs in the stop-start version.
    """
