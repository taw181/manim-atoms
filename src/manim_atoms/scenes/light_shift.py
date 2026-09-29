"""A light shift injected into one interferometer of the gradiometer."""

import numpy as np
from manim import *

from aionanim.style import *
from aionanim.tools.clock import (
    clock_rate,
    ground_share,
    make_dial,
    phase_sweep,
)
from aionanim.tools.gradiometer import (
    GR_ARM,
    GR_DIALS,
    GR_DIAL_RADIUS,
    GR_LAG,
    GR_LASER_GAP,
    GR_LASER_Z,
    GR_LOWER_Z,
    GR_SIGNAL,
    GR_SLOPE,
    GR_T,
    GR_T0,
    GR_TERMS_WIDTH,
    GR_UPPER_Z,
    fire_pulse,
    gradiometer_frame,
    sweep_pulse,
    vertices,
)
from aionanim.tools.primitives import (
    draw_legs,
    fluoresce,
    fluorescence,
    make_atom,
    state_colors,
)
from aionanim.tools.spacetime import (
    carry,
    growing_band,
    growing_trail,
    run_to,
    worldline,
    wound,
    wound_with_shift,
)
from aionanim.scenes.gradiometer_gw import (
    GradiometerGW,
    RunsContinuously,
)


# --- a light shift injected into one interferometer -----------------------
# How a gradiometer is tested without waiting for a wave. Between the first
# pi/2 and the pi pulse an off-resonant beam is turned on across the upper
# cloud alone. It is far enough from resonance to drive nothing -- no atom
# changes state, no momentum is handed over, the geometry is untouched -- but
# while it is on it shifts the clock levels, and with them omega_A.
#
# Only one arm picks the shift up, and not because only one arm is lit: the
# beam covers the whole cloud. A hand turns at omega_A only while its arm is
# in |e>, so the arm that has been excited since the beamsplitter accumulates
# the shift and its partner, sitting in |g>, does not. The two hands stop
# agreeing, and that disagreement is the phase.
#
# The lower interferometer never sees the beam and stays on its null, so the
# shift does not cancel in Phi_upper - Phi_lower. That is the whole point: it
# arrives in the difference exactly the way a dark-matter or gravitational-wave
# signal would, which is what makes it a test of whether one would be caught.
# The same figure as GradiometerGW's, with the source on a shutter.
LS_ON, LS_OFF = 0.3, 0.72  # the stretch of the first leg the beam is on for
LS_PAD = 0.38  # how far its band stands off the interferometer it covers
# What the shift is tuned to inject. A third of a turn is chosen to be read
# rather than to be realistic: big enough to see on a dial and to split the
# upper ports plainly (P_g = 1/4), against a lower interferometer that still
# sends everything into |g>.
#
# Negative because delta_LS is signed and a beam below resonance pushes the
# levels together -- and because the sector on the dial is then the angle
# itself rather than the rest of the turn. phase_sweep wraps into one turn and
# sweeps from one hand to the other, so a hand that has run ahead by a third
# of a turn is drawn as two thirds of one. Nothing about the measurement
# changes with the sign: the ports split by cos(Phi) either way.
LS_PHASE = -TAU / 3

# --- the readout: two imaging pulses --------------------------------------
# The ports are read by fluorescence on the 461 nm line, one state at a time:
# a pulse images the atoms in 1S0 (|g>, "S") and blows them away, then the
# atoms in 3P0 (|e>, "P") are repumped and imaged with a second one. One
# camera frame takes both clouds, so each pulse is vertical -- simultaneous
# at the two clouds -- unlike the interferometer's pulses, which climb the
# baseline. Times are where they cross the diagram: late enough that the
# upper cloud's two ports are an atom apart when S is imaged, early enough
# that the P ports stop short of the right-hand side, which the readout image
# takes over.
LS_IMAGE_S = 2.8
LS_IMAGE_P = 3.6
# Every port gets an atom, including one the drawn phase sends (almost)
# nothing to: the camera images both states in both clouds, and the readout
# image the slide ends on shows all four. A port below this share is drawn
# at it rather than left as an empty guide.
LS_PORT_FLOOR = 0.5


def along(start, end, f):
    """A fraction f of the way from one corner to the next."""
    return start + (end - start) * f


def along_port(origin, rise, x):
    """Where a port leaving `origin` at slope `rise` is at time x."""
    return origin + (x - origin[0]) * (RIGHT + UP * rise)


class LightShiftSignal(GradiometerGW):
    """A signal put in on purpose, to see whether the gradiometer catches it.

    Gradiometer ends on a null: nothing is passing through, both clocks read
    the same, and the difference between them is zero. This is that scene with
    one thing added -- an off-resonant beam across the upper cloud, on between
    the first two pulses -- and the null breaks.

    Drawn on the quiet geometry deliberately, as DarkMatterPhase is drawn on
    ClockPhase's: nothing about the instrument has changed and nothing about
    the worldlines has moved. The only new thing on the page is a band of
    light over one of the two interferometers.

    A subclass of GradiometerGW for its machinery and not for its wave: the
    two clouds, the hands they carry, the dials and the ports are the same
    apparatus whatever is being measured with it, and inheriting them is also
    what lets RunsContinuously drive this scene without knowing about it.
    """

    def construct(self):
        gradiometer_frame(
            self, r"A light shift on one interferometer mimics a signal"
        )

        low = vertices(GR_LOWER_Z, 0.0)
        up = vertices(GR_UPPER_Z, GR_LAG)

        rate = clock_rate(GR_T)
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

        # --- the beam, and the stretch of the first leg it is on for -------
        # Its band covers the whole upper interferometer, both arms, because
        # that is what a beam across a cloud does. Only one arm picks the
        # shift up all the same: a hand turns at omega_A while its arm is in
        # |e>, and the other arm is sitting in |g>.
        self.on_x = along(up[0], up[1], LS_ON)[0]
        self.off_x = along(up[0], up[1], LS_OFF)[0]
        self.beam = Rectangle(
            width=self.off_x - self.on_x,
            height=GR_ARM + 2 * LS_PAD,
            **LIGHT_SHIFT_STYLE,
        ).move_to([
            0.5 * (self.on_x + self.off_x), GR_UPPER_Z + GR_ARM / 2, 0,
        ])
        self.beam_label = VGroup(
            Tex(
                r"off-resonant beam, upper cloud only",
                font_size=FONT_LEGEND, color=LIGHT_SHIFT_COLOR,
            ),
            MathTex(
                r"\omega_A \to \omega_A + \delta_{\text{LS}}",
                font_size=FONT_LEGEND, color=LIGHT_SHIFT_COLOR,
            ),
        ).arrange(DOWN, buff=0.14).next_to(self.beam, UP, buff=0.25)

        self.low, self.up = low, up
        self.rate, self.phase = rate, phase
        self.atoms, self.seeds = atoms, seeds
        self.hands, self.big = [], VGroup()
        self.fly()

        # --- the readout ---------------------------------------------------
        # One dial has a sector on it and the other has not, which is the
        # figure: the lower interferometer is exactly where Gradiometer left
        # it, and the upper one is not.
        sweeps = []
        for cloud in ("low", "up"):
            sweep, gap = phase_sweep(
                GR_DIALS[cloud], phase[cloud][1], phase[cloud][0], GR_DIAL_RADIUS
            )
            if gap > 0.01:
                sweeps.append(sweep)
        self.remove(*atoms["low"], *atoms["up"], *self.hands)
        self.close(sweeps)
        self.beat()

        # The picture the two pulses took, in the dials' place: a talk slide
        # supplies it, the package scene has none and keeps the dials.
        image = self.readout_image()
        if image is not None:
            self.play(FadeOut(dials), *[FadeOut(m) for m in self.big],
                      *[FadeOut(m) for m in sweeps], run_time=0.6)
            self.play(FadeIn(image), run_time=0.8)
            self.beat()

        signal = VGroup(
            Tex(
                r"applied to one interferometer, so it survives the difference",
                font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR),
            ),
            MathTex(
                r"\Delta\Phi = \Phi_{\text{upper}} - \Phi_{\text{lower}}"
                r" = \delta_{\text{LS}}\,\tau",
                font_size=FONT_ANNOTATION,
            ),
        ).arrange(DOWN, buff=0.22).move_to(GR_SIGNAL)
        if signal.width > GR_TERMS_WIDTH:
            signal.scale(GR_TERMS_WIDTH / signal.width)
        self.play(FadeIn(signal), run_time=1.0)
        self.wait(2.0)

    def readout_image(self):
        """Hook: a camera image of the two clouds, shown once they are read
        out, in place of the dials. None here."""
        return None

    def close(self, sweeps):
        """Read both dials, then fly the ports into the two imaging pulses.

        The ports' atoms take over from the arms on the frame the arms go, so
        nothing leaves the page. The lower cloud was recombined L/c before the
        upper one, so its ports fly on alone until the pulse reaches the upper
        cloud, and then both clouds fly together to the S pulse, which lights
        the |g> atoms; the |e> atoms fly on to the P pulse.
        """
        ports = [port for cloud in ("low", "up") for port in self.port_atoms(cloud)]
        self.add(*[atom for atom, *_ in ports])
        self.play(*[FadeIn(m) for m in sweeps], run_time=0.7)

        def fly_to(x, which):
            if not which:
                return
            draw_legs(self, [
                (atom, along_port(origin, rise, max(origin[0], atom.get_x())),
                 along_port(origin, rise, x), color)
                for atom, origin, rise, color in which
            ], extra=self.port_extra())

        up_x = self.up[3][0]
        fly_to(up_x, [port for port in ports if port[1][0] < up_x])
        fly_to(LS_IMAGE_S, ports)
        ground = [port for port in ports if port[3] == ATOM_COLOR]
        excited = [port for port in ports if port[3] == KICKED_COLOR]
        for x, name, color, imaged in (
            (LS_IMAGE_S, "S", ATOM_COLOR, ground),
            (LS_IMAGE_P, "P", KICKED_COLOR, excited),
        ):
            if name == "P":
                fly_to(LS_IMAGE_P, excited)
            atoms = [atom for atom, *_ in imaged]
            pulse = self.imaging_pulse(x, name, color, atoms)
            fluoresce(self, atoms, fade=[pulse])

    def port_atoms(self, cloud):
        """A cloud's two ports as (atom, origin, rise, colour), placed at its
        recombination point but not yet on the scene. Each atom's opacity is
        its port's share, floored at LS_PORT_FLOOR."""
        v = self.vertices(cloud)
        p_ground = ground_share(self.phase[cloud][1], self.phase[cloud][0])
        return [
            (make_atom(color, radius=CLOCK_ATOM_RADIUS,
                       opacity=max(p, LS_PORT_FLOOR)).move_to(v[3]),
             v[3], rise, color)
            for p, color, rise in (
                (p_ground, ATOM_COLOR, 0.0),
                (1.0 - p_ground, KICKED_COLOR, self.port_slope(cloud)),
            )
        ]

    def imaging_line(self, x, name, color, atoms):
        """A 461 nm pulse up the baseline at time x, named for the state it
        images. It stops just past the topmost atom it lights, as the clock's
        pulses do, rather than running on up the frame."""
        top = max(a.get_top()[1] for a in atoms) + 0.25
        pulse = Line([x, GR_LASER_Z, 0], [x, top, 0],
                     color=IMAGING_COLOR, stroke_width=PULSE_STROKE_WIDTH)
        caption = Tex(name, font_size=FONT_STATE, color=lighten(color))
        caption.next_to([x, GR_LASER_Z, 0], UR, buff=0.12)
        return VGroup(pulse, caption)

    def imaging_pulse(self, x, name, color, atoms):
        """imaging_line, drawn climbing. Returns it, to go out with the
        fluorescence."""
        pulse, caption = drawn = self.imaging_line(x, name, color, atoms)
        self.play(Create(pulse), FadeIn(caption), rate_func=linear, run_time=0.6)
        return drawn

    def fly(self):
        """Three pulses and two legs, with the beam on across the middle of
        the first.
        """
        low, up, atoms, phase = self.low, self.up, self.atoms, self.phase
        rate = self.rate

        # --- pulse 1: the beamsplitter -----------------------------------
        fire_pulse(self, GR_T0, flash=list(self.seeds.values()))
        self.open_arms("low")
        self.open_arms("up")

        # --- leg 1, flown in three stretches ------------------------------
        # The beam is on for the middle one. Splitting the leg rather than
        # easing a tracker is what puts the shift somewhere on the page: the
        # stretch of flight it covers is a stretch of the drawing, and the
        # upper hand visibly changes pace over exactly that stretch and no
        # other, while the lower one keeps the rate both started at.
        legs = [
            (atoms["low"][0], low[0], low[1], ATOM_COLOR),
            (atoms["low"][1], low[0], low[2], KICKED_COLOR),
            (atoms["up"][0], up[0], up[1], ATOM_COLOR),
            (atoms["up"][1], up[0], up[2], KICKED_COLOR),
        ]

        def stretch(f_from, f_to, extra=()):
            draw_legs(self, [
                (atom, along(a, b, f_from), along(a, b, f_to), color)
                for atom, a, b, color in legs
            ], extra=extra)

        def wound_to(f, shifted):
            """Where each hand has got to a fraction f into the first leg."""
            return [
                phase["low"][1].animate.set_value(rate * GR_T * f),
                phase["up"][1].animate.set_value(
                    rate * GR_T * f + (LS_PHASE if shifted else 0.0)
                ),
            ]

        stretch(0.0, LS_ON, extra=wound_to(LS_ON, shifted=False))
        self.play(FadeIn(self.beam), FadeIn(self.beam_label), run_time=0.6)
        self.bring_to_back(self.beam)
        self.beat()
        stretch(LS_ON, LS_OFF, extra=wound_to(LS_OFF, shifted=True))
        stretch(LS_OFF, 1.0, extra=wound_to(1.0, shifted=True))
        self.beat()

        # --- pulse 2: the mirror ------------------------------------------
        fire_pulse(self, GR_T0 + GR_T, flash=[a for p in atoms.values() for a in p])
        big = self.big
        self.play(
            *[state_colors(p[0], KICKED_COLOR) for p in atoms.values()],
            *[state_colors(p[1], ATOM_COLOR) for p in atoms.values()],
            *[big[k].animate.set_color(lighten(KICKED_COLOR)) for k in (0, 2)],
            *[big[k].animate.set_color(lighten(ATOM_COLOR)) for k in (1, 3)],
            run_time=0.5,
        )
        # The beam is off, so the second leg is the quiet one in both clouds:
        # whatever the shift put in stays in, because nothing takes it out.
        draw_legs(self, [
            (atoms["low"][0], low[1], low[3], KICKED_COLOR),
            (atoms["low"][1], low[2], low[3], ATOM_COLOR),
            (atoms["up"][0], up[1], up[3], KICKED_COLOR),
            (atoms["up"][1], up[2], up[3], ATOM_COLOR),
        ], extra=[
            phase[c][0].animate.set_value(rate * GR_T) for c in ("low", "up")
        ])
        self.beat()

        # --- pulse 3: recombine -------------------------------------------
        # Anchored on the two recombination points, which sit an arm above
        # the clouds' starting heights: a pulse anchored on those heights
        # crosses one arm's light travel time late and misses the atoms.
        fire_pulse(self, low[3][0], flash=[atoms["low"][0], atoms["up"][0]],
                   z_near=low[3][1], z_far=up[3][1])


class LightShiftSignalContinuous(RunsContinuously, LightShiftSignal):
    """The injected signal with lab time never stopped.

    The beam is a duration -- it is on between two pulses, for a stretch of
    one leg -- so it is the scene in this set that gains most from the atoms
    not stopping. The band fills in from its left edge while the beam is on
    and stops growing when the shutter shuts, so what is drawn is the window
    rather than a caption about it, and the upper hand changes pace across
    exactly the span the band covers.
    """

    def fly(self):
        low, up, phase = self.low, self.up, self.phase

        # Lab time starts as the first pulse leaves the laser.
        clock = self.clock = ValueTracker(GR_T0 - GR_SLOPE * GR_LASER_GAP)
        self.add(clock)

        for cloud in ("low", "up"):
            v = self.vertices(cloud)
            start = np.array([clock.get_value(), self.nominal(cloud), 0.0])
            self.add(growing_trail([start, v[0]], ATOM_COLOR, clock))
            carry(self.seeds[cloud], worldline([start, v[0]]), clock)
            # The arm kicked at the mirror is excited over the second leg in
            # both clouds and sees nothing; the arm kicked at the beamsplitter
            # is excited over the first, which is when the beam is on -- so
            # only the upper one of those four hands knows about it.
            phase[cloud][0].add_updater(
                wound(clock, self.rate, v[1][0], v[3][0])
            )
        phase["low"][1].add_updater(
            wound(clock, self.rate, low[0][0], low[1][0])
        )
        phase["up"][1].add_updater(wound_with_shift(
            clock, self.rate, up[0][0], up[1][0],
            self.on_x, self.off_x, LS_PHASE,
        ))

        # The band grows from the moment the shutter opens and stops at the
        # moment it shuts, and is then left where it is: the window it covers
        # is what the readout at the end is about.
        self.add(growing_band(
            self.beam, self.on_x, self.off_x, clock, LIGHT_SHIFT_STYLE
        ))

        # Each pulse goes out in the stretch of flight after it rather than
        # lingering into the next, which is what the wave scenes need and this
        # one does not: nothing here is captioned or set against a dashed
        # ghost, so a worldline that has left the frame has nothing left to
        # say -- and the band is what should have the page while it is on.
        def clear(drawn, to):
            run_to(self, clock, to, *[FadeOut(m) for m in drawn])

        drawn = self.shoot(0, near=[low[0]], far=[up[0]],
                           on_near=lambda: self.open_arms("low"),
                           on_far=lambda: self.open_arms("up"))
        # The label arrives with the beam, not before it, so the run up to the
        # shutter is its own stretch.
        clear(drawn, self.on_x)
        run_to(self, clock, self.off_x, FadeIn(self.beam_label))
        drawn = self.shoot(1, near=[low[1], low[2]], far=[up[1], up[2]],
                           on_near=lambda: self.mirror("low"),
                           on_far=lambda: self.mirror("up"))
        clear(drawn, GR_T0 + 1.5 * GR_T)
        drawn = self.shoot(2, near=[low[3]], far=[up[3]],
                           on_near=lambda: self.recombine("low"),
                           on_far=lambda: self.recombine("up"))
        clear(drawn, clock.get_value() + PULSE_LINGER)

    def recombine(self, cloud):
        """The last pulse turns a cloud's arms into its ports, on arrival.

        The ports are put on their own worldlines at once, out to the pulse
        that images them -- S for |g>, P for |e> -- and park there, so the
        lower cloud's ports are already flying while the pulse is still
        climbing to the upper one.
        """
        clock = self.clock
        pair = self.atoms[cloud]
        k = 0 if cloud == "low" else 2
        for atom in pair:
            atom.clear_updaters()
        self.remove(*pair, *self.hands[k:k + 2])
        ports = self.port_atoms(cloud)
        for atom, origin, rise, color in ports:
            end = along_port(
                origin, rise, LS_IMAGE_S if color == ATOM_COLOR else LS_IMAGE_P
            )
            self.add(growing_trail([origin, end], color, clock))
            carry(atom, worldline([origin, end]), clock)
        self.add(*[atom for atom, *_ in ports])
        self.ports = getattr(self, "ports", []) + ports

    def close(self, sweeps):
        """The imaging readout with lab time running.

        The sectors arrive while the ports fly to S. A vertical pulse is one
        instant in lab time, so each is strobed on whole rather than climbing,
        and the |g> atoms light up while the |e> atoms fly on to P: the one
        place the stop-start readout would freeze them mid-flight. Once they
        are at P nothing is moving any more, and the last imaging is played
        with the clock stood still.
        """
        clock = self.clock
        ground = [atom for atom, *_, color in self.ports if color == ATOM_COLOR]
        excited = [atom for atom, *_, color in self.ports if color == KICKED_COLOR]
        run_to(self, clock, LS_IMAGE_S, *[FadeIn(m) for m in sweeps])

        s_pulse = self.imaging_line(LS_IMAGE_S, "S", ATOM_COLOR, ground)
        s_halos, s_light = fluorescence(ground)
        self.add(s_pulse)
        run_to(self, clock, LS_IMAGE_P, *s_light)

        p_pulse = self.imaging_line(LS_IMAGE_P, "P", KICKED_COLOR, excited)
        p_halos, p_light = fluorescence(excited)
        self.add(p_pulse)
        self.play(*p_light, FadeOut(s_halos), FadeOut(s_pulse), run_time=0.8)
        self.play(FadeOut(p_halos), FadeOut(p_pulse), run_time=0.5)

    def shoot(self, k, near, far, fade=(), on_near=None, on_far=None):
        """One pulse. No wave here, so every one of them is the quiet one."""
        return sweep_pulse(
            self, self.clock, GR_T0 + k * GR_T, near=near, far=far,
            lag=GR_LAG, reference=False, fade=fade,
            on_near=on_near, on_far=on_far,
        )
