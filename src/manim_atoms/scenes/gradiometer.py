"""Two clock interferometers on one baseline, driven by one laser.

Drawing the photons with a finite slope is the whole point of this scene --
the light reaches the far cloud later than the near one, so a single laser
writes its phase into the two interferometers at different retarded times.
That is what the single-photon clock scheme buys: the laser's own phase noise
is common to both and cancels in the difference.
"""

from manim import *

from aionanim.style import *
from aionanim.tools.clock import (
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
from aionanim.tools.gradiometer import (
    GR_ARM,
    GR_DIALS,
    GR_DIAL_RADIUS,
    GR_LAG,
    GR_LOWER_Z,
    GR_OUT,
    GR_T,
    GR_T0,
    GR_TERMS,
    GR_TERMS_WIDTH,
    GR_UPPER_Z,
    fire_pulse,
    gradiometer_frame,
    vertices,
)
from aionanim.tools.primitives import (
    draw_legs,
    make_atom,
    state_colors,
)

# Some effect on the atoms, over the middle of each interferometer's second
# leg in that interferometer's own time -- the upper one L/c after the lower.
# A signal that varies in time is caught at two different moments, so the two
# pick up different phases and the difference keeps it: the upper hand sweeps
# on further than the lower. Generic on purpose, as on the clock slide.
GR_EFFECT_SPAN = (0.25, 0.75)  # of the second leg
GR_EFFECT_PAD = 0.2  # the boxes' reach above and below each interferometer
GR_EFFECT_PHASE = {"low": 1.0, "up": 2.1}  # |e> ports: ~23% and ~75%
GR_EFFECT_TIME = 2.5


class Gradiometer(Scene):
    """Two interferometers, one baseline, one laser -- so, two clocks.

    The quiet twin of GradiometerGW: same geometry, same dials, nothing
    passing through, so both clocks read the same. Then, without replaying,
    some unspecified effect acts on each interferometer over its second leg,
    in its own time -- the upper one L/c after the lower -- and the two hands
    sweep on by different amounts, so the difference keeps it. It ends on what
    that difference is made of: the propagation term survives, the laser's
    cancels.
    """

    def beat(self):
        """The pause after each step: nothing here, a click on the slide version."""

    def construct(self):
        gradiometer_frame(self, r"Differential interferometry: one laser, two interferometers")

        low = vertices(GR_LOWER_Z, 0.0)
        up = vertices(GR_UPPER_Z, GR_LAG)

        # Nothing is passing through, so the two pulse intervals are equal in
        # both interferometers -- but they are still read off the vertices,
        # the same way GradiometerGW reads them, so the two scenes cannot
        # drift apart.
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
            cloud: [
                make_atom(radius=CLOCK_ATOM_RADIUS).move_to(v[0]),
                make_atom(KICKED_COLOR, radius=CLOCK_ATOM_RADIUS).move_to(v[0]),
            ]
            for cloud, v in (("low", low), ("up", up))
        }
        seed_low = make_atom(radius=CLOCK_ATOM_RADIUS).move_to(low[0])
        seed_up = make_atom(radius=CLOCK_ATOM_RADIUS).move_to(up[0])
        self.play(FadeIn(seed_low, scale=0.5), FadeIn(seed_up, scale=0.5), run_time=0.6)
        self.beat()

        # --- pulse 1: the beamsplitter -----------------------------------
        fire_pulse(self, GR_T0, flash=[seed_low, seed_up])
        for pair, v in ((atoms["low"], low), (atoms["up"], up)):
            for a in pair:
                a.set_opacity(SUPERPOSITION_OPACITY).move_to(v[0])
        self.remove(seed_low, seed_up)
        self.add(*atoms["low"], *atoms["up"])

        # index 0 is the arm kicked at the mirror, index 1 the arm kicked now
        hands = [
            make_clock_hand(atoms[cloud][k], phase[cloud][k])
            for cloud in ("low", "up")
            for k in (0, 1)
        ]
        self.add(*hands)
        big = VGroup()
        for cloud in ("low", "up"):
            big.add(
                dial_hand(
                    GR_DIALS[cloud], phase[cloud][0], lighten(ATOM_COLOR),
                    GR_DIAL_RADIUS,
                ),
                dial_hand(
                    GR_DIALS[cloud], phase[cloud][1], lighten(KICKED_COLOR),
                    GR_DIAL_RADIUS,
                ),
            )
        self.add(big)

        # The offset between the two interferometers is the reason for all of
        # this, so name it rather than leaving it as an unexplained shift.
        lag_note = MathTex(
            r"L/c\ \text{later}", font_size=FONT_LEGEND, color=LASER_COLOR
        ).next_to(up[0], UP, buff=0.3)
        self.play(FadeIn(lag_note), run_time=0.5)

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

        # --- pulse 2: the mirror ------------------------------------------
        self.play(FadeOut(lag_note), run_time=0.3)
        fire_pulse(self, GR_T0 + GR_T, flash=[a for p in atoms.values() for a in p])
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
        # Anchored on the two recombination points, which sit an arm above
        # the clouds' starting heights: a pulse anchored on those heights
        # crosses one arm's light travel time late and misses the atoms.
        fire_pulse(self, low[3][0], flash=[atoms["low"][0], atoms["up"][0]],
                   z_near=low[3][1], z_far=up[3][1])

        # --- the ports ------------------------------------------------------
        # The arms are spent: that pulse couples the two states each pair is
        # in, so what leaves the last vertex is a pair of ports sharing the
        # atoms out by the angle between the hands. Nothing is passing
        # through, both interferometers spent equal time excited, and so both
        # send everything into |g, p> -- the null the wave has to break, drawn
        # against an empty excited port so that it reads as one.
        self.remove(*atoms["low"], *atoms["up"], *hands)
        ports = {}
        for cloud, v in (("low", low), ("up", up)):
            ports[cloud] = draw_ports(
                self, v[3], GR_OUT,
                ground_share(phase[cloud][1], phase[cloud][0]),
                slope=leg_slope(v[1], v[3]), labels=False,
            )

        # --- the readout ---------------------------------------------------
        # Both dials have come round to the same place, so say what is done
        # with them -- and then what that difference is made of. The laser term
        # is the one that changes its verdict here: common to both
        # interferometers, so it goes out of the difference entirely.
        self.play(
            *[Flash(d[0], **{**FLASH_STYLE, "color": AREA_COLOR}) for d in dials],
            run_time=0.5,
        )
        self.beat()

        # --- some effect on the atoms -----------------------------------------
        # Not replayed: a box on each interferometer, and the hand of the arm
        # excited there (the one kicked at the mirror) sweeping on by what it
        # picked up, while a line crosses each box. The ports follow the
        # hands, so each interferometer's excited port fills in by its own
        # amount -- the two splits come out unequal.
        boxes, cursors, sweeps = VGroup(), VGroup(), []
        for cloud, v, z in (("low", low, GR_LOWER_Z), ("up", up, GR_UPPER_Z)):
            start, end = (v[1][0] + f * (v[3][0] - v[1][0]) for f in GR_EFFECT_SPAN)
            box = Rectangle(
                width=end - start, height=GR_ARM + 2 * GR_EFFECT_PAD,
                **PERTURBATION_STYLE,
            ).move_to([(start + end) / 2, z + GR_ARM / 2, 0])
            boxes.add(box)
            cursors.add(Line(box.get_corner(DL), box.get_corner(UL),
                             color=PERTURBATION_COLOR, stroke_width=3))
            sweeps.append(always_redraw(
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
        self.add(*sweeps)
        for cloud, v in (("low", low), ("up", up)):
            live_ports(
                self, ports[cloud], v[3], GR_OUT,
                lambda c=cloud: ground_share(phase[c][1], phase[c][0]),
                slope=leg_slope(v[1], v[3]),
            )
        self.play(
            *[phase[c][0].animate.increment_value(GR_EFFECT_PHASE[c])
              for c in ("low", "up")],
            *[cursor.animate.align_to(box, RIGHT) for cursor, box in zip(cursors, boxes)],
            rate_func=linear, run_time=GR_EFFECT_TIME,
        )
        self.play(FadeOut(cursors), run_time=0.3)
        self.beat()

        show_phase_budget(
            self, GR_TERMS, laser_struck=True, laser_label=r"cancelled",
            difference_lhs=r"\Delta\Phi = \Phi_{\text{upper}} - \Phi_{\text{lower}}",
            max_width=GR_TERMS_WIDTH,
        )
        self.wait(2.5)
