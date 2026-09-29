"""A gravitational wave passing through the gradiometer.

GradiometerGW and GradiometerGWStretch are the same figure with a wave passing
through, drawn the two ways people draw one. GradiometerGW modulates the light
travel time and leaves the freely falling atoms on the worldlines they already
had, which is where the signal actually comes from; GradiometerGWStretch bows
the worldlines so the baseline visibly breathes, which is the picture most
people carry. The same h(t) runs along the top of both, they take their pulse
timing from the same place, and so their dials read the same phase.

The *Continuous variants run the whole diagram on one lab clock (see
aionanim.tools.spacetime); RunsContinuously is the mixin that does it, and the
light-shift scenes reuse it.
"""

import numpy as np
from manim import *

from aionanim.style import *
from aionanim.tools.primitives import (
    draw_legs,
    make_atom,
    make_guide,
    state_colors,
)
from aionanim.tools.spacetime import (
    no_displacement,
    run_to,
    worldline,
    wound,
    carry,
    growing_trail,
    draw_wavy_legs,
)
from aionanim.tools.gradiometer import (
    GR_T,
    GR_LOWER_Z,
    GR_UPPER_Z,
    GR_MID_Z,
    GR_OUT,
    gradiometer_frame,
    fire_pulse,
    GR_TERMS_WIDTH,
    GR_SIGNAL,
    GR_DIAL_RADIUS,
    GR_DIALS,
    sweep_pulse,
)
from aionanim.tools.clock import (
    clock_rate,
    make_clock_hand,
    make_dial,
    dial_hand,
    phase_sweep,
    ground_share,
    draw_ports,
    fly_ports,
    leg_slope,
)
from aionanim.tools.gradiometer_gw import (
    GW_PULSES,
    GW_TRACE_X,
    gw_lag,
    gw_arrival_lags,
    quiet_arrival,
    gw_displacement,
    make_strain_trace,
    strain_marker,
    gw_vertices,
    arrival_note,
)


class GradiometerGW(Scene):
    """A wave modulates the light travel time, so the pulses arrive early or late.

    The honest picture of what AION measures. The atoms are freely falling test
    masses, so their worldlines keep the shape they had in Gradiometer; what
    the wave changes is L/c, and with it the retarded time at which the laser
    writes its phase into the upper interferometer.
    """

    def beat(self):
        """The pause after each step: nothing here, a click on the slide version.

        Called from construct and from the stop-start fly, never from close:
        the continuous variants replace close and fly, and a pause in the
        middle of their one running clock would undo what they are for.
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
        low = gw_vertices(GR_LOWER_Z, low_lags)
        up = gw_vertices(GR_UPPER_Z, up_lags)

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

        self.low, self.up = low, up
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
    # the same wave -- it moves the clouds -- and overrides exactly these
    # three, which is the whole difference between the two pictures once the
    # pulse timing is shared.
    REFERENCE = True  # the dashed quiet-baseline ghost beside each pulse

    def vertices(self, cloud):
        return self.low if cloud == "low" else self.up

    def nominal(self, cloud):
        """Where on the baseline a cloud belongs."""
        return GR_LOWER_Z if cloud == "low" else GR_UPPER_Z

    def displacement(self, cloud):
        """How the wave bows this cloud's worldline. Not at all, here."""
        return no_displacement

    def rest(self, cloud):
        """Where the cloud is when lab time starts."""
        return self.nominal(cloud) + self.displacement(cloud)(GW_PULSES[0])

    def crossing(self, cloud, k):
        """Where the cloud is when pulse k reaches it."""
        return self.nominal(cloud)

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

    def open_arms(self, cloud):
        """One cloud's seed becomes two arms, each carrying a hand.

        Per cloud rather than for both at once, because the pulse does not
        reach them at the same time: the far cloud is split L/c after the near
        one, which is the whole quantity this figure is about.
        """
        v = self.vertices(cloud)
        for atom in self.atoms[cloud]:
            atom.set_opacity(SUPERPOSITION_OPACITY).move_to(v[0])
        self.remove(self.seeds[cloud])
        self.add(*self.atoms[cloud])
        # index 0 is the arm kicked at the mirror, index 1 the arm kicked now
        hands = [
            make_clock_hand(self.atoms[cloud][k], self.phase[cloud][k])
            for k in (0, 1)
        ]
        self.hands.extend(hands)
        self.add(*hands)
        big = VGroup(
            dial_hand(
                GR_DIALS[cloud], self.phase[cloud][0], lighten(ATOM_COLOR),
                GR_DIAL_RADIUS,
            ),
            dial_hand(
                GR_DIALS[cloud], self.phase[cloud][1], lighten(KICKED_COLOR),
                GR_DIAL_RADIUS,
            ),
        )
        self.big.add(*big)
        self.add(big)

    def port_extra(self):
        """What rides along with the output ports. Nothing, unless lab time does."""
        return ()

    def port_slope(self, cloud):
        """The slope a cloud's excited port leaves at: its kicked leg's."""
        v = self.low if cloud == "low" else self.up
        return leg_slope(v[1], v[3])

    def close(self, sweeps):
        """Read both dials, then let each pair of ports fly."""
        self.play(*[FadeIn(m) for m in sweeps], run_time=0.7)
        for cloud, v in (("low", self.low), ("up", self.up)):
            draw_ports(
                self, v[3], GR_OUT,
                ground_share(self.phase[cloud][1], self.phase[cloud][0]),
                slope=self.port_slope(cloud), labels=False,
                extra=self.port_extra(),
            )

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
        fire_pulse(
            self, GW_PULSES[0] + self.low_lags[0],
            flash=[self.seeds["low"], self.seeds["up"]],
            lag=lags[0], reference=True, quiet_x=quiet_arrival(0),
            note=self.pulse_note(0),
        )
        self.open_arms("low")
        self.open_arms("up")

        draw_legs(self, [
            (atoms["low"][0], low[0], low[1], ATOM_COLOR),
            (atoms["low"][1], low[0], low[2], KICKED_COLOR),
            (atoms["up"][0], up[0], up[1], ATOM_COLOR),
            (atoms["up"][1], up[0], up[2], KICKED_COLOR),
        ], extra=[
            phase[c][1].animate.set_value(rate * excited[c][0])
            for c in ("low", "up")
        ])
        self.beat()

        # --- pulse 2: the mirror, arriving early --------------------------
        self.play(FadeIn(self.dots[1], scale=0.4), run_time=0.3)
        fire_pulse(
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
            (atoms["low"][0], low[1], low[3], KICKED_COLOR),
            (atoms["low"][1], low[2], low[3], ATOM_COLOR),
            (atoms["up"][0], up[1], up[3], KICKED_COLOR),
            (atoms["up"][1], up[2], up[3], ATOM_COLOR),
        ], extra=[
            phase[c][0].animate.set_value(rate * excited[c][1])
            for c in ("low", "up")
        ])
        self.beat()

        # --- pulse 3: recombine -------------------------------------------
        self.play(FadeIn(self.dots[2], scale=0.4), run_time=0.3)
        fire_pulse(
            self, GW_PULSES[2] + self.low_lags[2],
            flash=[atoms["low"][0], atoms["up"][0]],
            lag=lags[2], reference=True, quiet_x=quiet_arrival(2),
        )


class RunsContinuously:
    """Mixin: a gradiometer scene whose lab time never stops.

    Only the pulse-and-leg sequence differs between a stop-start scene and a
    continuous one, and it differs the same way for both pictures of the wave.
    So it is written once here and mixed in ahead of whichever scene it is
    running, which is what lets the stretched baseline have a continuous
    variant for free. Everything it needs -- the vertices, where each cloud is
    when a pulse crosses it, how its worldlines bow -- it asks the scene for.

    What the mixin buys these scenes in particular: the one quantity a
    gradiometer figure exists to show -- that the far cloud is split, mirrored
    and recombined L/c after the near one -- is a statement about *when*
    things happen to each of them. Stopping the atoms to draw a pulse makes it
    unshowable, so the stop-start scenes say it in words: a caption reading
    "arrives late" beside a dashed ghost. Here the pulse climbs while the
    atoms fly, the near cloud splits, and the far cloud is still a single seed
    for L/c afterwards. The caption becomes a label on something the frame is
    doing.

    The price is that the pulses are quick. Run at V a late pulse crosses the
    frame in under a second and the early one, whose light travel time the
    wave has largely closed up, in a fraction of that -- which is not a defect
    but the measurement: the two are drawn at the ratio the wave put between
    them rather than dilated to the same length and annotated.
    """

    def port_extra(self):
        # By the same amount the ports run, not to the same place: the last
        # pulse has carried lab time a little past the final corner, and what
        # has to match is the rate, so the wave keeps step with the atoms.
        return [self.clock.animate.set_value(self.clock.get_value() + GR_OUT)]

    def close(self, sweeps):
        """The sectors arrive while the ports fly, not before them.

        Same reason the pulses do not stop the atoms: what leaves the last
        vertex is still the interferometer running on in its own time. And the
        angle between a pair of hands and the split between a pair of ports
        are one fact, so they belong in one beat rather than two.
        """
        fly_ports(
            self,
            [
                (
                    v[3],
                    ground_share(self.phase[cloud][1], self.phase[cloud][0]),
                    self.port_slope(cloud),
                )
                for cloud, v in (("low", self.low), ("up", self.up))
            ],
            GR_OUT, labels=False,
            extra=[*self.port_extra(), *[FadeIn(m) for m in sweeps]],
        )

    def open_arms(self, cloud):
        v, clock = self.vertices(cloud), self.clock
        # Trails before atoms, so an atom is never drawn under the line it is
        # drawing. One per leg rather than per arm: the two arms swap states
        # at the mirror, so the colour belongs to the leg.
        self.add(
            growing_trail([v[0], v[1]], ATOM_COLOR, clock, self.displacement(cloud)),
            growing_trail([v[1], v[3]], KICKED_COLOR, clock, self.displacement(cloud)),
            growing_trail([v[0], v[2]], KICKED_COLOR, clock, self.displacement(cloud)),
            growing_trail([v[2], v[3]], ATOM_COLOR, clock, self.displacement(cloud)),
        )
        super().open_arms(cloud)
        pair = self.atoms[cloud]
        carry(pair[0], worldline([v[0], v[1], v[3]], self.displacement(cloud)), clock)
        carry(pair[1], worldline([v[0], v[2], v[3]], self.displacement(cloud)), clock)

    def mirror(self, cloud):
        """The pulse hands the excitation over, on the instant it arrives."""
        pair = self.atoms[cloud]
        pair[0][0].set_fill(KICKED_COLOR).set_stroke(lighten(KICKED_COLOR))
        pair[1][0].set_fill(ATOM_COLOR).set_stroke(lighten(ATOM_COLOR))
        k = 0 if cloud == "low" else 2
        self.big[k].set_color(lighten(KICKED_COLOR))
        self.big[k + 1].set_color(lighten(ATOM_COLOR))

    def fly(self):
        low, up, lags = self.low, self.up, self.lags

        # Lab time starts when the first pulse leaves the laser, so the first
        # thing the scene does is send it.
        clock = self.clock = ValueTracker(GW_PULSES[0])
        self.add(clock, strain_marker(clock))
        for k, dot in enumerate(self.dots):
            dot.add_updater(lambda m, k=k: m.set_opacity(
                1.0 if clock.get_value() >= GW_PULSES[k] else 0.0
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
        # gw_vertices puts a cloud's two arms at the same time, so one flash
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
        return sweep_pulse(
            self, self.clock, GW_PULSES[k] + self.low_lags[k],
            near=near, far=far, lag=self.lags[k],
            reference=self.REFERENCE, quiet_x=quiet_arrival(k),
            note=self.pulse_note(k),
            z_near=self.crossing("low", k), z_far=self.crossing("up", k),
            fade=fade, on_near=on_near, on_far=on_far,
        )


class GradiometerGWContinuous(RunsContinuously, GradiometerGW):
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
        low = gw_vertices(GR_LOWER_Z, low_lags)
        up = gw_vertices(GR_UPPER_Z, up_lags)
        # Corners ride the wave; the legs between them bow to match.
        low = tuple(v + UP * low_disp(v[0]) for v in low)
        up = tuple(v + UP * up_disp(v[0]) for v in up)

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

        self.low, self.up = low, up
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
            self.play(FadeIn(self.dots[k], scale=0.4), run_time=0.3)
            fire_pulse(
                self, GW_PULSES[k] + self.low_lags[k], flash=flash, lag=lags[k],
                note=note,
                z_near=self.crossing("low", k), z_far=self.crossing("up", k),
            )

        # --- pulse 1: the beamsplitter -------------------------------------
        shoot(0, [self.seeds["low"], self.seeds["up"]], note=self.pulse_note(0))
        self.open_arms("low")
        self.open_arms("up")

        draw_wavy_legs(self, [
            (atoms["low"][0], low[0], low[1], ATOM_COLOR, low_disp),
            (atoms["low"][1], low[0], low[2], KICKED_COLOR, low_disp),
            (atoms["up"][0], up[0], up[1], ATOM_COLOR, up_disp),
            (atoms["up"][1], up[0], up[2], KICKED_COLOR, up_disp),
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
            (atoms["low"][0], low[1], low[3], KICKED_COLOR, low_disp),
            (atoms["low"][1], low[2], low[3], ATOM_COLOR, low_disp),
            (atoms["up"][0], up[1], up[3], KICKED_COLOR, up_disp),
            (atoms["up"][1], up[2], up[3], ATOM_COLOR, up_disp),
        ], extra=[
            phase[c][0].animate.set_value(rate * excited[c][1])
            for c in ("low", "up")
        ])
        self.beat()

        # --- pulse 3: recombine ---------------------------------------------
        shoot(2, [atoms["low"][0], atoms["up"][0]])


class GradiometerGWStretchContinuous(RunsContinuously, GradiometerGWStretch):
    """GradiometerGWStretch with the pulses climbing while the atoms fly.

    Free, once the continuous sequence is a mixin and this picture's two
    differences are methods: the bow goes into the worldlines the atoms are
    carried along and into the trails behind them, exactly as it goes into
    draw_wavy_legs in the stop-start version.
    """
