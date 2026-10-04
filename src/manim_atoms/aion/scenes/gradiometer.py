"""Two clock interferometers on one baseline, driven by one laser.

Drawing the photons with a finite slope is the whole point of this scene --
the light reaches the far cloud later than the near one, so a single laser
writes its phase into the two interferometers at different retarded times.
That is what the single-photon clock scheme buys: the laser's own phase noise
is common to both and cancels in the difference. Each pulse writes its phase
phi_n onto the hands as on the clock slide, so both dials end on the same
laser sector, phi_1 - 2 phi_2 + phi_3.

GradiometerContinuous runs the same figure on one lab clock (see
manim_atoms.core.spacetime), through GradiometerGW's RunsContinuously.
"""

import numpy as np
from manim import *

from manim_atoms.aion.style import *
from manim_atoms.interferometry.tools.clock import (
    clock_rate,
    dial_hand,
    draw_ports,
    leg_slope,
    ground_share,
    live_ports,
    make_clock_hand,
    make_dial,
    phase_sweep,
    show_phase_budget,
)
from manim_atoms.interferometry.scenes.clock import CP_LASER_PHASES
from manim_atoms.aion.scenes.gradiometer_gw import GradiometerGW, RunsContinuously
from manim_atoms.aion.tools.gradiometer import (
    GR_ARM,
    GR_DIALS,
    GR_DIAL_RADIUS,
    GR_LAG,
    GR_LASER_Z,
    GR_LOWER_Z,
    GR_OUT,
    GR_SLOPE,
    GR_T,
    GR_T0,
    GR_TERMS,
    GR_TERMS_WIDTH,
    GR_UPPER_Z,
    fire_pulse,
    gradiometer_frame,
    sweep_pulse,
    vertices,
)
from manim_atoms.core.primitives import (
    draw_legs,
    make_atom,
    state_colors,
)
from manim_atoms.core.spacetime import (
    carry,
    growing_trail,
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



def laser_jumps(v):
    """The laser's phase on each of a cloud's two hands, as (lab time, delta).

    The same bookkeeping as ClockPhase's, at the times each pulse reaches this
    cloud: an arm picks phi_n up when it absorbs from pulse n and gives it
    back when it emits, and the hands count -phase. Index 0 is the arm kicked
    at the mirror, index 1 the arm kicked at the beamsplitter.
    """
    phi1, phi2, phi3 = CP_LASER_PHASES
    return (
        [(v[1][0], -phi2)],
        [(v[0][0], -phi1), (v[1][0], +phi2), (v[3][0], -phi3)],
    )


def launch_time(x_at_lower, z_at=GR_LOWER_Z):
    """When a pulse that crosses height `z_at` at `x_at_lower` leaves the laser."""
    return x_at_lower - GR_SLOPE * (z_at - GR_LASER_Z)


def laser_caption(n, x_at_lower, z_at=GR_LOWER_Z):
    """phi_n on the laser line, just right of where pulse n leaves it."""
    foot = launch_time(x_at_lower, z_at)
    return MathTex(
        rf"\phi_{n}", font_size=FONT_ANNOTATION, color=LASER_COLOR
    ).next_to([foot, GR_LASER_Z, 0], UR, buff=0.12)


class Gradiometer(GradiometerGW):
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

    A subclass of GradiometerGW for its machinery, as LightShiftSignal is:
    that is what lets RunsContinuously drive GradiometerContinuous.
    """

    def construct(self):
        gradiometer_frame(self, r"Differential interferometry: one laser, two interferometers")

        low = vertices(GR_LOWER_Z, 0.0)
        up = vertices(GR_UPPER_Z, GR_LAG)
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
        self.low, self.up = low, up
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
        self.play(FadeIn(laser_caption(1, GR_T0)), run_time=0.3)
        fire_pulse(self, GR_T0, flash=list(self.seeds.values()))
        self.open_arms("low")
        self.open_arms("up")
        self.laser_jump(0)

        draw_legs(self, [
            (atoms["low"][0], low[0], low[1], ATOM_COLOR),
            (atoms["low"][1], low[0], low[2], KICKED_COLOR),
            (atoms["up"][0], up[0], up[1], ATOM_COLOR),
            (atoms["up"][1], up[0], up[2], KICKED_COLOR),
        ], extra=[
            phase[c][1].animate.increment_value(rate * GR_T) for c in ("low", "up")
        ])
        self.beat()

        # --- pulse 2: the mirror ------------------------------------------
        self.play(FadeIn(laser_caption(2, GR_T0 + GR_T)), run_time=0.3)
        fire_pulse(self, GR_T0 + GR_T, flash=[a for p in atoms.values() for a in p])
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
            (atoms["low"][0], low[1], low[3], KICKED_COLOR),
            (atoms["low"][1], low[2], low[3], ATOM_COLOR),
            (atoms["up"][0], up[1], up[3], KICKED_COLOR),
            (atoms["up"][1], up[2], up[3], ATOM_COLOR),
        ], extra=[
            phase[c][0].animate.increment_value(rate * GR_T) for c in ("low", "up")
        ])
        self.beat()

        # --- pulse 3: recombine -------------------------------------------
        # Anchored on the two recombination points, which sit an arm above
        # the clouds' starting heights: a pulse anchored on those heights
        # crosses one arm's light travel time late and misses the atoms.
        self.play(FadeIn(laser_caption(3, *low[3][:2])), run_time=0.3)
        fire_pulse(self, low[3][0], flash=[atoms["low"][0], atoms["up"][0]],
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
        clock = self.clock = ValueTracker(launch_time(GR_T0))
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
            caption = laser_caption(n, x, z)
            launch = launch_time(x, z)
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
        return sweep_pulse(
            self, self.clock, GR_T0 + k * GR_T, near=near, far=far,
            lag=GR_LAG, note=self.pulse_note(k), fade=fade,
            z_near=z_near, z_far=z_far, on_near=on_near, on_far=on_far,
        )
