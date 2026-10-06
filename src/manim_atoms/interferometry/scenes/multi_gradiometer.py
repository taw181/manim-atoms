"""Three clock interferometers on one baseline, driven by one laser.

Gradiometer with a third cloud halfway up the baseline: the multi-gradiometer
(see manim_atoms.interferometry.tools.multi_gradiometer). Each pulse climbs
from the one laser at the bottom of the shaft and reaches the three clouds in
turn, L/2c apart, writing the same phase phi_n into all three -- so all three
dials end on the same laser sector, and the laser drops out of any difference
between them. Then an effect that grows linearly along the baseline sweeps the
three hands on by equal steps, and the scene ends on what a third cloud is
for: two gradiometers sharing the middle cloud read the same, so their
difference, Phi_upper - 2 Phi_middle + Phi_lower, cancels a linear signal as
well as the laser, and keeps only what is not linear along the baseline.

MultiGradiometerContinuous runs the same figure on one lab clock, through
RunsContinuously, as GradiometerContinuous does for two clouds.
"""

import numpy as np
from manim import *

from manim_atoms.interferometry.style import *
from manim_atoms.interferometry.tools.clock import (
    clock_rate,
    leg_slope,
    ground_share,
    live_ports,
    make_dial,
    phase_sweep,
)
from manim_atoms.interferometry.scenes.gradiometer import (
    GR_EFFECT_PAD,
    GR_EFFECT_SPAN,
    Gradiometer,
    RunsContinuously,
    laser_caption,
    laser_jumps,
    launch_time,
)
from manim_atoms.interferometry.tools.gradiometer import (
    GR_LOWER_Z,
    GR_T,
    GR_T0,
    gradiometer_frame,
    vertices,
)
from manim_atoms.interferometry.tools.multi_gradiometer import (
    MG_ARM,
    MG_CLOUDS,
    MG_DIAL_CAPTIONS,
    MG_DIAL_RADIUS,
    MG_DIALS,
    MG_EFFECT_PHASE,
    MG_EFFECT_TIME,
    MG_LAG,
    MG_OUT,
    MG_RESULT,
    MG_Z,
    fire_pulse_through,
    sweep_pulse_through,
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


class MultiGradiometer(Gradiometer):
    """Three interferometers, one baseline, one laser -- so, three clocks.

    Gradiometer's figure with a cloud added halfway up: the same dials, the
    same laser phases written by each pulse, the same ports. It inherits the
    laser bookkeeping (laser_jump, jump_steps) and GradiometerBase's arms,
    dials and ports, which run over CLOUDS; what it brings is the third
    cloud's geometry, a pulse that crosses three clouds, and the ending.
    """

    CLOUDS = MG_CLOUDS
    dial_radius = MG_DIAL_RADIUS
    port_length = MG_OUT

    def dial_center(self, cloud):
        return MG_DIALS[cloud]

    def vertices(self, cloud):
        return self.corners[cloud]

    def nominal(self, cloud):
        return MG_Z[cloud]

    def construct(self):
        gradiometer_frame(
            self, r"Differential interferometry: one laser, three interferometers"
        )

        self.corners = {c: vertices(MG_Z[c], MG_LAG[c], MG_ARM) for c in MG_CLOUDS}
        phase = {c: (ValueTracker(0.0), ValueTracker(0.0)) for c in MG_CLOUDS}
        self.add(*[t for pair in phase.values() for t in pair])

        dials = VGroup(*[
            make_dial(MG_DIALS[c], MG_DIAL_CAPTIONS[c], MG_DIAL_RADIUS)
            for c in MG_CLOUDS
        ])
        self.play(FadeIn(dials), run_time=0.6)

        # --- the three clouds --------------------------------------------
        atoms = {
            c: [
                make_atom(radius=CLOCK_ATOM_RADIUS).move_to(self.corners[c][0]),
                make_atom(KICKED_COLOR, radius=CLOCK_ATOM_RADIUS).move_to(
                    self.corners[c][0]
                ),
            ]
            for c in MG_CLOUDS
        }
        seeds = {
            c: make_atom(radius=CLOCK_ATOM_RADIUS).move_to(self.corners[c][0])
            for c in MG_CLOUDS
        }
        self.play(*[FadeIn(m, scale=0.5) for m in seeds.values()], run_time=0.6)
        self.beat()

        self.rate, self.phase = clock_rate(GR_T), phase
        self.atoms, self.seeds = atoms, seeds
        self.hands, self.big = [], VGroup()
        self.fly()

        # --- the readout ---------------------------------------------------
        # One laser wrote the same phases into all three and nothing passed
        # through, so all three dials show the same sector and all three
        # pairs of ports split alike.
        sweeps = [
            phase_sweep(MG_DIALS[c], phase[c][1], phase[c][0], MG_DIAL_RADIUS)[0]
            for c in MG_CLOUDS
        ]
        self.remove(*[a for pair in atoms.values() for a in pair], *self.hands)
        before = set(self.mobjects)
        self.close(sweeps)
        ports = [m for m in self.mobjects if m not in before and m not in sweeps]
        self.play(
            *[Flash(d[0], **{**FLASH_STYLE, "color": AREA_COLOR}) for d in dials],
            run_time=0.5,
        )
        self.beat()

        # --- an effect that grows along the baseline --------------------------
        # As Gradiometer's, not replayed: a box over each interferometer's
        # second leg, and the hand of the arm excited there sweeping on. Here
        # by equal steps in height -- a signal that grows linearly along the
        # baseline, as a single-photon gradiometer's does -- so the three
        # sectors open by equal steps and the three splits follow.
        boxes, live = VGroup(), []
        for c in MG_CLOUDS:
            v = self.corners[c]
            start, end = (v[1][0] + f * (v[3][0] - v[1][0]) for f in GR_EFFECT_SPAN)
            boxes.add(Rectangle(
                width=end - start, height=MG_ARM + 2 * GR_EFFECT_PAD,
                **PERTURBATION_STYLE,
            ).move_to([(start + end) / 2, MG_Z[c] + MG_ARM / 2, 0]))
            live.append(always_redraw(
                lambda c=c: phase_sweep(
                    MG_DIALS[c], phase[c][1], phase[c][0], MG_DIAL_RADIUS
                )[0]
            ))
        box_label = Tex(
            r"an effect that grows along the baseline", font_size=FONT_LEGEND,
            color=PERTURBATION_COLOR,
        ).next_to(boxes[-1], UP, buff=0.25)
        self.play(FadeIn(boxes), FadeIn(box_label), run_time=0.8)
        self.bring_to_back(boxes)
        for tracker in (t for pair in phase.values() for t in pair):
            tracker.clear_updaters()
        self.remove(*sweeps)
        self.add(*live)
        self.remove(*ports)
        for c in MG_CLOUDS:
            v = self.corners[c]
            live_ports(
                self, [], v[3], MG_OUT,
                lambda c=c: ground_share(phase[c][1], phase[c][0]),
                slope=leg_slope(v[1], v[3]),
            )
        self.play(
            *[phase[c][0].animate.increment_value(MG_EFFECT_PHASE[c])
              for c in MG_CLOUDS],
            rate_func=linear, run_time=MG_EFFECT_TIME,
        )
        self.wait(0.3)
        self.beat()

        # --- what three clouds buy --------------------------------------------
        # Two gradiometers sharing the middle cloud, each with the laser gone.
        # A linear signal splits equally between them, so their difference
        # removes it too; what is left is what does not grow linearly along
        # the baseline.
        result = VGroup(
            MathTex(
                r"(\Phi_{\text{upper}} - \Phi_{\text{middle}})",
                r"-",
                r"(\Phi_{\text{middle}} - \Phi_{\text{lower}})",
                r"= 0",
                font_size=FONT_ANNOTATION,
            ),
            Tex(
                r"the laser cancels in each pair, a signal linear along $L$ between them",
                font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR),
            ),
        ).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        result.move_to(MG_RESULT, aligned_edge=UL)
        self.play(FadeOut(box_label), Write(result[0]), run_time=1.4)
        self.play(FadeIn(result[1]), run_time=0.6)
        self.wait(2.5)

    def fly(self):
        """Three pulses and two legs, one at a time, each pulse through three clouds."""
        corners, atoms, phase, rate = self.corners, self.atoms, self.phase, self.rate
        low = corners["low"]

        # --- pulse 1: the beamsplitter -----------------------------------
        self.play(FadeIn(laser_caption(1, GR_T0)), run_time=0.3)
        fire_pulse_through(
            self, GR_T0, GR_LOWER_Z,
            [(MG_Z[c], [self.seeds[c]]) for c in MG_CLOUDS],
        )
        for c in MG_CLOUDS:
            self.open_arms(c)
        self.laser_jump(0)
        draw_legs(self, [
            leg
            for c in MG_CLOUDS
            for leg in (
                (atoms[c][0], corners[c][0], corners[c][1], ATOM_COLOR),
                (atoms[c][1], corners[c][0], corners[c][2], KICKED_COLOR),
            )
        ], extra=[phase[c][1].animate.increment_value(rate * GR_T) for c in MG_CLOUDS])
        self.beat()

        # --- pulse 2: the mirror ------------------------------------------
        self.play(FadeIn(laser_caption(2, GR_T0 + GR_T)), run_time=0.3)
        fire_pulse_through(
            self, GR_T0 + GR_T, GR_LOWER_Z,
            [(MG_Z[c], atoms[c]) for c in MG_CLOUDS],
        )
        big = self.big
        self.play(
            *[state_colors(p[0], KICKED_COLOR) for p in atoms.values()],
            *[state_colors(p[1], ATOM_COLOR) for p in atoms.values()],
            *[big[k].animate.set_color(lighten(KICKED_COLOR))
              for k in range(0, len(big), 2)],
            *[big[k].animate.set_color(lighten(ATOM_COLOR))
              for k in range(1, len(big), 2)],
            run_time=0.5,
        )
        self.laser_jump(1)
        draw_legs(self, [
            leg
            for c in MG_CLOUDS
            for leg in (
                (atoms[c][0], corners[c][1], corners[c][3], KICKED_COLOR),
                (atoms[c][1], corners[c][2], corners[c][3], ATOM_COLOR),
            )
        ], extra=[phase[c][0].animate.increment_value(rate * GR_T) for c in MG_CLOUDS])
        self.beat()

        # --- pulse 3: recombine -------------------------------------------
        # Anchored on the recombination points, an arm above the clouds'
        # starting heights, as in Gradiometer.
        self.play(FadeIn(laser_caption(3, *low[3][:2])), run_time=0.3)
        fire_pulse_through(
            self, low[3][0], low[3][1],
            [(corners[c][3][1], [atoms[c][0]]) for c in MG_CLOUDS],
        )
        self.laser_jump(2)


class MultiGradiometerContinuous(RunsContinuously, MultiGradiometer):
    """The same three clocks with lab time never stopped.

    Each pulse climbs while the atoms fly, so the middle cloud is split,
    mirrored and recombined L/2c after the near one and the far cloud L/2c
    after that, in front of the audience. The whole sequence, first pulse to
    ports, is one run.
    """

    def fly(self):
        phase, corners = self.phase, self.corners
        low = corners["low"]

        # Lab time starts as the first pulse leaves the laser.
        clock = self.clock = ValueTracker(launch_time(GR_T0))
        self.add(clock)

        for c in MG_CLOUDS:
            v = corners[c]
            start = np.array([clock.get_value(), self.nominal(c), 0.0])
            self.add(growing_trail([start, v[0]], ATOM_COLOR, clock))
            carry(self.seeds[c], worldline([start, v[0]]), clock)
            mirror_kicked, first_kicked = laser_jumps(v)
            phase[c][0].add_updater(
                wound_with_jumps(clock, self.rate, v[1][0], v[3][0], mirror_kicked)
            )
            phase[c][1].add_updater(
                wound_with_jumps(clock, self.rate, v[0][0], v[1][0], first_kicked)
            )

        # Each phi_n goes up as its pulse leaves the laser and stays.
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

        drawn = sweep_pulse_through(self, clock, GR_T0, GR_LOWER_Z, [
            (MG_Z[c], [corners[c][0]], lambda c=c: self.open_arms(c))
            for c in MG_CLOUDS
        ])
        drawn = sweep_pulse_through(self, clock, GR_T0 + GR_T, GR_LOWER_Z, [
            (MG_Z[c], [corners[c][1], corners[c][2]], lambda c=c: self.mirror(c))
            for c in MG_CLOUDS
        ], fade=drawn)
        drawn = sweep_pulse_through(self, clock, low[3][0], low[3][1], [
            (corners[c][3][1], [corners[c][3]], None) for c in MG_CLOUDS
        ], fade=drawn)
        run_to(self, clock, clock.get_value() + PULSE_LINGER,
               *[FadeOut(m) for m in drawn])
