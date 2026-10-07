"""Two clock interferometers on one baseline, driven by one laser.

Drawing the photons with a finite slope is the whole point of this scene --
the light reaches the far cloud later than the near one, so a single laser
writes its phase into the two interferometers at different retarded times.
That is what the single-photon clock scheme buys: the laser's own phase noise
is common to both and cancels in the difference. Each pulse writes its phase
phi_n onto the hands as on the clock slide, so both dials end on the same
laser sector, phi_1 - 2 phi_2 + phi_3.

GradiometerContinuous runs the same figure on one lab clock (see
manim_atoms.core.spacetime), through RunsContinuously. GradiometerBase and
RunsContinuously are the machinery the AION scenes (a gravitational wave, a
dark-matter field, a light shift through the gradiometer) build on too.
"""

import numpy as np
from manim import *

from manim_atoms.interferometry.style import *
from manim_atoms.interferometry.tools.clock import (
    clock_rate,
    dial_hand,
    draw_ports,
    fly_ports,
    ground_share,
    leg_slope,
    live_ports,
    make_clock_hand,
    make_dial,
    phase_sweep,
    show_phase_budget,
)
from manim_atoms.interferometry.tools.gradiometer import (
    GR_ARM,
    GR_DIAL_RADIUS,
    GR_DIALS,
    GR_LAG,
    GR_LOWER_Z,
    GR_OUT,
    GR_T,
    GR_T0,
    GR_TERMS,
    GR_TERMS_WIDTH,
    GR_UPPER_Z,
    GR_PULSES,
    cloud_legs,
    cloud_sequence,
    corners,
    gr_fire_pulse,
    gr_laser_caption,
    gr_launch_time,
    gr_sweep_pulse,
    gradiometer_frame,
    laser_jumps,
)
from manim_atoms.core.primitives import (
    draw_legs,
    make_atom,
    state_colors,
)
from manim_atoms.core.spacetime import (
    carry,
    growing_trail,
    no_displacement,
    run_to,
    worldline,
    wound_with_jumps,
)

# Some effect on the atoms, over the middle of each interferometer's second
# leg in that interferometer's own time -- the upper one L/c after the lower.
# A signal that varies in time is caught at two different moments, so the two
# pick up different phases and the difference keeps it: the upper hand sweeps
# on further than the lower. Generic on purpose, as on the clock slide.
GR_EFFECT_SPAN = (0.25, 0.75)  # of the second leg
GR_EFFECT_PAD = 0.2  # the boxes' reach above and below each interferometer
# On top of the laser's 1.3 rad, which leaves both with |g> ports of ~63%:
# the lower one ends near an even split (~44%), the upper one mostly in |e>
# (~17%) -- but not all of it: a |g> port emptied out is drawn as a dashed
# guide, and on screen that reads as the port vanishing, not as a split.
GR_EFFECT_PHASE = {"low": 0.4, "up": 1.0}
GR_EFFECT_TIME = 2.5



class GradiometerBase(Scene):
    """The machinery every gradiometer scene shares: two clouds on one
    baseline, each split into two arms carrying a clock hand, each read out
    on its own dial and closed into a pair of ports.

    A subclass's construct sets ``self.seqs`` (each cloud's run through the
    pulse-sequence engine, from interferometry.tools.gradiometer's
    cloud_sequence), ``self.low`` / ``self.up`` (each cloud's four corners,
    from corners), ``self.atoms`` (two arms per cloud), ``self.seeds``,
    ``self.phase`` (two trackers per cloud), ``self.hands`` and ``self.big``,
    then flies its own pulse sequence. Gradiometer is the quiet one; the AION
    scenes put a wave, a field or a light shift through it.
    """

    def beat(self):
        """The pause after each step: nothing here, a click on the slide version.

        Called from construct and from the stop-start fly, never from close:
        the continuous variants replace close and fly, and a pause in the
        middle of their one running clock would undo what they are for.
        """

    def vertices(self, cloud):
        return self.low if cloud == "low" else self.up

    def nominal(self, cloud):
        """Where on the baseline a cloud belongs."""
        return GR_LOWER_Z if cloud == "low" else GR_UPPER_Z

    def displacement(self, cloud):
        """How something passing through bows this cloud's worldline. Not at
        all, unless a subclass says so (GradiometerGWStretch's wave does)."""
        return no_displacement

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


class RunsContinuously:
    """Mixin: a gradiometer scene whose lab time never stops.

    Only the pulse-and-leg sequence differs between a stop-start scene and a
    continuous one, and it differs the same way whatever passes through. So
    the parts that run on a lab clock -- arms carried along their worldlines,
    a mirror that hands the excitation over on the instant, ports that fly
    while the dials fill -- are written once here and mixed in ahead of
    whichever GradiometerBase scene they are running. Everything they need --
    the vertices, how a cloud's worldlines bow -- they ask the scene for. The
    scene brings its own ``fly`` (starting ``self.clock``) and ``shoot``.

    What the mixin buys these scenes in particular: the one quantity a
    gradiometer figure exists to show -- that the far cloud is split, mirrored
    and recombined L/c after the near one -- is a statement about *when*
    things happen to each of them. Stopping the atoms to draw a pulse makes it
    unshowable, so the stop-start scenes say it in words: a caption reading
    "arrives late" beside a dashed ghost. Here the pulse climbs while the
    atoms fly, the near cloud splits, and the far cloud is still a single seed
    for L/c afterwards. The caption becomes a label on something the frame is
    doing.

    The price is that the pulses are quick: run at V a pulse crosses the frame
    in under a second. With a wave passing through, an early one whose light
    travel time the wave has largely closed up crosses in a fraction of that
    -- which is not a defect but the measurement: the pulses are drawn at the
    ratio the wave put between them rather than dilated to the same length
    and annotated.
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


class Gradiometer(GradiometerBase):
    """Two interferometers, one baseline, one laser -- so, two clocks.

    The quiet twin of GradiometerGW: same geometry, same dials, nothing
    passing through. Each pulse writes the laser's phase onto the hands, as on
    the clock slide, and since one laser drives both interferometers both
    dials end on the same sector: both clocks read the same. Then, without
    replaying, some unspecified effect acts on each interferometer over its
    second leg, in its own time -- the upper one L/c after the lower -- and
    the two hands sweep on by different amounts, so the difference keeps it.
    It ends on what that difference is made of: the propagation term
    survives, the laser's cancels.

    A GradiometerBase, as GradiometerGW and LightShiftSignal are: that is what
    lets RunsContinuously drive GradiometerContinuous.
    """

    def construct(self):
        gradiometer_frame(self, r"Differential interferometry: one laser, two interferometers")

        seqs = {c: cloud_sequence(GR_PULSES, self.nominal(c)) for c in ("low", "up")}
        low, up = corners(seqs["low"]), corners(seqs["up"])
        phase = {
            cloud: (ValueTracker(0.0), ValueTracker(0.0))
            for cloud in ("low", "up")
        }
        self.add(*[t for pair in phase.values() for t in pair])

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

        # The offset between the two interferometers goes unnamed here: with
        # nothing passing through it changes nothing, and DarkMatterGradiometer
        # is where it is named, as the reason the two clocks read differently.
        self.low, self.up, self.seqs = low, up, seqs
        self.rate, self.phase = clock_rate(GR_T), phase
        self.atoms, self.seeds = atoms, seeds
        self.hands, self.big = [], VGroup()
        self.fly()

        # --- the readout ---------------------------------------------------
        # The arms are spent: the last pulse couples the two states each pair
        # is in, so what leaves the last vertex is a pair of ports sharing the
        # atoms out by the angle between the hands. Nothing is passing
        # through and one laser wrote the same phases into both, so both
        # dials show the same sector and both pairs of ports split alike.
        sweeps = [
            phase_sweep(GR_DIALS[c], phase[c][1], phase[c][0], GR_DIAL_RADIUS)[0]
            for c in ("low", "up")
        ]
        self.remove(*atoms["low"], *atoms["up"], *self.hands)
        before = set(self.mobjects)
        self.close(sweeps)
        ports = [m for m in self.mobjects if m not in before and m not in sweeps]
        self.play(
            *[Flash(d[0], **{**FLASH_STYLE, "color": AREA_COLOR}) for d in dials],
            run_time=0.5,
        )
        self.beat()

        # --- some effect on the atoms -----------------------------------------
        # Not replayed: a box on each interferometer, and the hand of the arm
        # excited there (the one kicked at the mirror) sweeping on by what it
        # picked up. The ports follow the
        # hands, so each interferometer's excited port fills in by its own
        # amount -- the two splits come out unequal.
        boxes, live = VGroup(), []
        for cloud, v, z in (("low", low, GR_LOWER_Z), ("up", up, GR_UPPER_Z)):
            start, end = (v[1][0] + f * (v[3][0] - v[1][0]) for f in GR_EFFECT_SPAN)
            box = Rectangle(
                width=end - start, height=GR_ARM + 2 * GR_EFFECT_PAD,
                **PERTURBATION_STYLE,
            ).move_to([(start + end) / 2, z + GR_ARM / 2, 0])
            boxes.add(box)
            live.append(always_redraw(
                lambda c=cloud: phase_sweep(
                    GR_DIALS[c], phase[c][1], phase[c][0], GR_DIAL_RADIUS
                )[0]
            ))
        box_label = Tex(
            r"some effect on the atoms", font_size=FONT_LEGEND,
            color=PERTURBATION_COLOR,
        ).next_to(boxes[1], UP, buff=0.25)
        self.play(FadeIn(boxes), FadeIn(box_label), run_time=0.8)
        self.bring_to_back(boxes)
        # The hands are done with lab time: whatever drove them is spent, and
        # the effect is added on top of where they stand.
        for tracker in (t for pair in phase.values() for t in pair):
            tracker.clear_updaters()
        self.remove(*sweeps)
        self.add(*live)
        self.remove(*ports)
        for cloud, v in (("low", low), ("up", up)):
            live_ports(
                self, [], v[3], GR_OUT,
                lambda c=cloud: ground_share(phase[c][1], phase[c][0]),
                slope=leg_slope(v[1], v[3]),
            )
        self.play(
            *[phase[c][0].animate.increment_value(GR_EFFECT_PHASE[c])
              for c in ("low", "up")],
            rate_func=linear, run_time=GR_EFFECT_TIME,
        )
        self.wait(0.3)
        self.beat()

        show_phase_budget(
            self, GR_TERMS, laser_struck=True, laser_label=r"cancelled",
            difference_lhs=r"\Delta\Phi = \Phi_{\text{upper}} - \Phi_{\text{lower}}",
            max_width=GR_TERMS_WIDTH,
        )
        self.wait(2.5)

    def pulse_note(self, k):
        """Nothing: the pulses go uncaptioned (see construct)."""
        return None

    def laser_jump(self, k):
        """Pulse k writes its phase onto both clouds' hands."""
        self.play(*[
            tracker.animate.increment_value(sum(d for _, d in jumps[k]))
            for c in ("low", "up")
            for tracker, jumps in zip(
                self.phase[c], self.jump_steps(c)
            )
            if jumps[k]
        ], run_time=0.5)

    def jump_steps(self, cloud):
        """laser_jumps per hand, grouped by the pulse that makes them."""
        v = self.vertices(cloud)
        pulse_x = [v[0][0], v[1][0], v[3][0]]
        return [
            [[(t, d) for t, d in hand if t == x] for x in pulse_x]
            for hand in laser_jumps(v)
        ]

    def fly(self):
        """Three pulses and two legs, one at a time."""
        low, up, atoms, phase = self.low, self.up, self.atoms, self.phase
        rate = self.rate

        # --- pulse 1: the beamsplitter -----------------------------------
        self.play(FadeIn(gr_laser_caption(1, GR_T0)), run_time=0.3)
        gr_fire_pulse(self, GR_T0, flash=list(self.seeds.values()))
        self.open_arms("low")
        self.open_arms("up")
        self.laser_jump(0)

        draw_legs(self, [
            *cloud_legs(self.seqs["low"], 0, atoms["low"]),
            *cloud_legs(self.seqs["up"], 0, atoms["up"]),
        ], extra=[
            phase[c][1].animate.increment_value(rate * GR_T) for c in ("low", "up")
        ])
        self.beat()

        # --- pulse 2: the mirror ------------------------------------------
        self.play(FadeIn(gr_laser_caption(2, GR_T0 + GR_T)), run_time=0.3)
        gr_fire_pulse(self, GR_T0 + GR_T, flash=[a for p in atoms.values() for a in p])
        big = self.big
        self.play(
            *[state_colors(p[0], KICKED_COLOR) for p in atoms.values()],
            *[state_colors(p[1], ATOM_COLOR) for p in atoms.values()],
            *[big[k].animate.set_color(lighten(KICKED_COLOR)) for k in (0, 2)],
            *[big[k].animate.set_color(lighten(ATOM_COLOR)) for k in (1, 3)],
            run_time=0.5,
        )
        self.laser_jump(1)
        draw_legs(self, [
            *cloud_legs(self.seqs["low"], 1, atoms["low"]),
            *cloud_legs(self.seqs["up"], 1, atoms["up"]),
        ], extra=[
            phase[c][0].animate.increment_value(rate * GR_T) for c in ("low", "up")
        ])
        self.beat()

        # --- pulse 3: recombine -------------------------------------------
        # Anchored on the two recombination points, which sit an arm above
        # the clouds' starting heights: a pulse anchored on those heights
        # crosses one arm's light travel time late and misses the atoms.
        self.play(FadeIn(gr_laser_caption(3, *low[3][:2])), run_time=0.3)
        gr_fire_pulse(self, low[3][0], flash=[atoms["low"][0], atoms["up"][0]],
                   z_near=low[3][1], z_far=up[3][1])
        self.laser_jump(2)


class GradiometerContinuous(RunsContinuously, Gradiometer):
    """The same two clocks with lab time never stopped.

    The pulse climbs while the atoms fly, so the far cloud is split, mirrored
    and recombined L/c after the near one in front of the audience, and each
    hand jumps by the laser's phase on the instant its pulse arrives. The
    whole sequence, first pulse to ports, is one run.
    """

    def fly(self):
        low, up, phase = self.low, self.up, self.phase

        # Lab time starts as the first pulse leaves the laser.
        clock = self.clock = ValueTracker(gr_launch_time(GR_T0))
        self.add(clock)

        for cloud in ("low", "up"):
            v = self.vertices(cloud)
            start = np.array([clock.get_value(), self.nominal(cloud), 0.0])
            self.add(growing_trail([start, v[0]], ATOM_COLOR, clock))
            carry(self.seeds[cloud], worldline([start, v[0]]), clock)
            mirror_kicked, first_kicked = laser_jumps(v)
            phase[cloud][0].add_updater(
                wound_with_jumps(clock, self.rate, v[1][0], v[3][0], mirror_kicked)
            )
            phase[cloud][1].add_updater(
                wound_with_jumps(clock, self.rate, v[0][0], v[1][0], first_kicked)
            )

        # Each phi_n goes up as its pulse leaves the laser and stays.
        # The last is anchored on the recombination points, an arm above the
        # clouds' starting heights, as in the stop-start fly.
        for n, (x, z) in enumerate(
            ((GR_T0, GR_LOWER_Z), (GR_T0 + GR_T, GR_LOWER_Z), tuple(low[3][:2])),
            start=1,
        ):
            caption = gr_laser_caption(n, x, z)
            launch = gr_launch_time(x, z)
            caption.add_updater(lambda m, t=launch: m.set_opacity(
                1.0 if clock.get_value() >= t - 1e-6 else 0.0
            ))
            self.add(caption)

        drawn = self.shoot(0, near=[low[0]], far=[up[0]],
                           on_near=lambda: self.open_arms("low"),
                           on_far=lambda: self.open_arms("up"))
        drawn = self.shoot(1, near=[low[1], low[2]], far=[up[1], up[2]],
                           fade=drawn,
                           on_near=lambda: self.mirror("low"),
                           on_far=lambda: self.mirror("up"))
        drawn = self.shoot(2, near=[low[3]], far=[up[3]], fade=drawn,
                           z_near=low[3][1], z_far=up[3][1])
        run_to(self, clock, clock.get_value() + PULSE_LINGER,
               *[FadeOut(m) for m in drawn])

    def shoot(self, k, near, far, fade=(), on_near=None, on_far=None,
              z_near=GR_LOWER_Z, z_far=GR_UPPER_Z):
        """One pulse. No wave here, so every one of them is the quiet one."""
        return gr_sweep_pulse(
            self, self.clock, GR_T0 + k * GR_T, near=near, far=far,
            lag=GR_LAG, note=self.pulse_note(k), fade=fade,
            z_near=z_near, z_far=z_far, on_near=on_near, on_far=on_far,
        )
