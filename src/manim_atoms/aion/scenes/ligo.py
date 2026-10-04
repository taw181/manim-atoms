"""How LIGO works: a Michelson interferometer read out at its dark port.

Seen from above: a laser, a beam splitter, two perpendicular arms ending on
free-hanging test masses, and a photodetector on the port where the light
coming back from the two arms recombines. With equal arms the two returning
beams arrive exactly out of phase and cancel, so the detector sits in the
dark. A gravitational wave travelling into the screen stretches one arm while
it squeezes the other; the returning beams slide out of step, stop
cancelling, and light reaches the detector.

Everything runs off one lab clock, `now`, so the light keeps flowing through
every beat of the scene. Everything visual comes from manim_atoms.style.

The builders take the wave as `h` and a `panel` to draw into, so another
scene can set the interferometer, already lit, in part of its own frame and
drive it with a wave of its own; each readout block takes its own panel, so
they can be laid out afresh (MergerOnSensitivityPlot does all of this).
"""

import numpy as np
from manim import *

from manim_atoms.aion.style import *
from manim_atoms.core.primitives import make_guide

# --- the apparatus --------------------------------------------------------
# The beam splitter sits left of centre so the right third of the frame is
# free for the readout. Both arms are the same length, which is what puts the
# detector on a dark fringe to begin with.
BS = np.array([-2.6, -1.1, 0.0])
ARM = 3.7  # drawn length of each arm
LASER = BS + LEFT * 3.0  # the box's left edge clear of the frame's
DETECTOR = BS + DOWN * 2.0  # the photodiode's body clear of the footer
X_END = BS + RIGHT * ARM  # the x arm's test mass, at rest
Y_END = BS + UP * ARM  # the y arm's test mass, at rest

MIRROR_LENGTH = 0.9
MIRROR_THICKNESS = 0.18
SPLITTER_LENGTH = 1.0
SPLITTER_THICKNESS = 0.07

# --- the light --------------------------------------------------------------
# The wave drawn on a beam is there to say "light", not to be measured: its
# wavelength is a drawing choice and has nothing to do with the phase shift,
# which is set by PHASE_GAIN below.
LIGHT_WAVELENGTH = 0.45
LIGHT_AMPLITUDE = 0.11
LIGHT_SPEED = 1.4  # units per second of lab time
K_LIGHT = TAU / LIGHT_WAVELENGTH
OMEGA_LIGHT = K_LIGHT * LIGHT_SPEED
SAMPLES_PER_UNIT = 45

# --- the gravitational wave -----------------------------------------------
# Two exaggerations, as in the gradiometer scenes, because no one factor makes
# both readable. MIRROR_SWING is how far a test mass is drawn to move at the
# peak of the wave; PHASE_GAIN is the phase difference the readout shows
# there. PHASE_GAIN = pi takes the detector from fully dark to fully bright,
# which is the whole range there is. The real numbers: h ~ 1e-21 over 4 km is
# a few 1e-18 m, and even after the arm cavities' ~300 round trips the phase
# is ~1e-8 rad.
GW_ON = 6.6  # lab time the wave arrives
GW_DURATION = 9.0
GW_PERIOD = 3.0
MIRROR_SWING = 0.4
PHASE_GAIN = PI
GW_OFF = GW_ON + GW_DURATION

# --- the readout panel ------------------------------------------------------
PANEL_X = (2.75, 6.7)
TRACE_Y = 2.85
TRACE_AMPLITUDE = 0.35
TRACE_T = (GW_ON - 0.6, GW_OFF + 0.6)  # the stretch of lab time the trace spans
RETURN_Y = 1.0  # the two returning beams, overlaid
RETURN_AMPLITUDE = 0.3
SUM_Y = -0.75  # what reaches the detector
# LIGOMichelson's own layout of the column right of the x arm, which it has
# to itself: h(t) across the top, grown and brought down, and the equations
# grown into the middle. The drawing's own coordinates above stay as they are
# because MergerOnSensitivityPlot places its panels by them.
COLUMN_X = 4.45  # the column's centre
MICHELSON_TRACE_SCALE = 1.2
MICHELSON_TRACE_Y = 2.1  # where the trace's zero line goes
MICHELSON_TRACE_AMPLITUDE = 0.55  # before the panel's scale
MICHELSON_EQUATION_Y = -0.5  # the two lines of the equation, centred
MICHELSON_EQUATION_SCALE = 1.4
MICHELSON_SCALE_Y = -2.75  # the line of real numbers under it
MICHELSON_SCALE_SCALE = 1.1
INSET_WAVELENGTH = 1.3
K_INSET = TAU / INSET_WAVELENGTH
OMEGA_INSET = K_INSET * LIGHT_SPEED

# --- lab-time beats ---------------------------------------------------------
T_INPUT = 1.1  # the laser beam reaches the splitter
T_ARMS = 2.6  # the arms are lit
T_READOUT = 3.6  # the returning beams are drawn
T_DARK = 5.6  # held on the dark port
T_END = GW_OFF + 3.5


def strain(t):
    """h(t), normalised to a peak of 1: a few cycles under a smooth envelope."""
    s = t - GW_ON
    if s <= 0 or s >= GW_DURATION:
        return 0.0
    envelope = np.sin(PI * s / GW_DURATION) ** 2
    return envelope * np.sin(TAU * s / GW_PERIOD)


class Panel:
    """Where the drawing goes: shrunk by `scale` about the origin (strokes
    too), then moved by `shift`. The default leaves it filling the frame."""

    def __init__(self, scale=1.0, shift=ORIGIN):
        self.scale = scale
        self.shift = np.asarray(shift, dtype=float)

    @classmethod
    def at(cls, scale, source, target):
        """The panel of `scale` that puts the drawing's point `source` on
        `target`."""
        source, target = (np.append(np.asarray(v, dtype=float), 0.0)[:3]
                          for v in (source, target))
        return cls(scale, target - scale * source)

    def point(self, p):
        return self.scale * np.asarray(p, dtype=float) + self.shift

    def __call__(self, mob):
        if self.scale != 1.0:
            mob.scale(self.scale, scale_stroke=True, about_point=ORIGIN)
        return mob.shift(self.shift)

    def redraw(self, draw):
        """always_redraw, with each redrawn mobject placed."""
        return always_redraw(lambda: self(draw()))


FULL_FRAME = Panel()
MICHELSON_TRACE = Panel.at(
    MICHELSON_TRACE_SCALE, [np.mean(PANEL_X), TRACE_Y],
    [COLUMN_X, MICHELSON_TRACE_Y],
)


# Everything the wave drives takes the strain as `h`, a function of lab time
# normalised to a peak of 1, so a scene can pass a wave of its own.
def phase_difference(t, h=strain):
    """phi_x - phi_y at the detector: 2k (L_x - L_y), which is linear in h."""
    return PHASE_GAIN * h(t)


def mirror_positions(t, h=strain):
    """Plus polarisation: the x arm stretches exactly as the y arm squeezes."""
    swing = MIRROR_SWING * h(t)
    return X_END + RIGHT * swing, Y_END + DOWN * swing


def wave(start, end, amplitude, phase, frac=1.0, k=K_LIGHT):
    """A sine riding the segment start -> end, drawn out to `frac` of its length.

    The phase at the start is `phase`, so a caller chains beams by handing on
    the phase the previous one ended with.
    """
    d = end - start
    length = np.linalg.norm(d)
    u = d / length
    normal = np.array([-u[1], u[0], 0.0])
    reach = max(length * frac, 1e-3)
    s = np.linspace(0, reach, max(2, int(SAMPLES_PER_UNIT * reach)))
    offset = amplitude * np.sin(k * s + phase)
    return VMobject().set_points_as_corners(
        start + np.outer(s, u) + np.outer(offset, normal)
    )


def beam(start, end, frac=1.0, opacity=1.0):
    """The faint band a beam's wave rides on."""
    reach = start + (end - start) * max(frac, 1e-3)
    return Line(
        start, reach, color=LASER_COLOR, stroke_width=BEAM_GLOW_WIDTH,
        stroke_opacity=BEAM_GLOW_OPACITY * opacity,
    )


def make_mirror(vertical):
    w, h = (MIRROR_THICKNESS, MIRROR_LENGTH) if vertical else (
        MIRROR_LENGTH, MIRROR_THICKNESS
    )
    return Rectangle(
        width=w, height=h, stroke_width=2, stroke_color=OPTIC_COLOR,
        fill_color=OPTIC_COLOR, fill_opacity=0.85,
    )


def make_splitter():
    """A half-silvered plate at 45 degrees: it reflects light from the laser up
    the y arm, and light coming back down the x arm into the detector."""
    return Rectangle(
        width=SPLITTER_LENGTH, height=SPLITTER_THICKNESS, stroke_width=2,
        stroke_color=OPTIC_COLOR, fill_color=OPTIC_COLOR, fill_opacity=0.35,
    ).rotate(45 * DEGREES).move_to(BS)


def make_laser():
    box = RoundedRectangle(
        width=1.2, height=0.55, corner_radius=0.08, stroke_color=LASER_COLOR,
        stroke_width=3, fill_color=BLACK, fill_opacity=1,
    ).move_to(LASER + LEFT * 0.6)
    tag = Tex("laser", font_size=FONT_LEGEND, color=LASER_COLOR).next_to(
        box, DOWN, buff=0.15
    )
    return VGroup(box, tag)


def make_detector():
    """A photodiode facing up the output port."""
    face = Rectangle(
        width=0.8, height=0.22, stroke_width=2, stroke_color=OPTIC_COLOR,
        fill_color=OPTIC_COLOR, fill_opacity=0.85,
    ).move_to(DETECTOR + DOWN * 0.11)
    body = Rectangle(
        width=0.5, height=0.3, stroke_width=2, stroke_color=OPTIC_COLOR,
        fill_color=BLACK, fill_opacity=1,
    ).next_to(face, DOWN, buff=0)
    tag = Tex("photodetector", font_size=FONT_LEGEND, color=OPTIC_COLOR).next_to(
        face, RIGHT, buff=0.25
    )
    return VGroup(face, body, tag)


def detector_glow(now, h=strain):
    """Power at the detector, sin^2(dphi / 2), drawn as light pooling on it."""
    power = np.sin(phase_difference(now.get_value(), h) / 2) ** 2
    return Circle(
        radius=0.62, stroke_width=0, fill_color=LASER_COLOR,
        fill_opacity=0.7 * power,
    ).move_to(DETECTOR)


def make_strain_trace(now, h=strain, span=TRACE_T, panel=FULL_FRAME,
                      amplitude=TRACE_AMPLITUDE):
    """h(t) drawn out as it arrives, with a dot on the present; the panel
    spans the stretch `span` of lab time. `amplitude` is the peak's height
    before the panel scales it."""
    zero = DashedLine(
        [PANEL_X[0], TRACE_Y, 0], [PANEL_X[1], TRACE_Y, 0], **GUIDE_STYLE
    )
    tag = MathTex(r"h(t)", font_size=FONT_LEGEND, color=STRAIN_COLOR).next_to(
        zero, LEFT, buff=0.18
    )

    def at(t):
        x = interpolate(*PANEL_X, (t - span[0]) / (span[1] - span[0]))
        return [x, TRACE_Y + amplitude * h(t), 0]

    def curve():
        t_now = float(np.clip(now.get_value(), *span))
        ts = np.linspace(span[0], max(t_now, span[0] + 1e-3), 300)
        return VMobject(
            stroke_color=STRAIN_COLOR, stroke_width=STRAIN_STROKE_WIDTH
        ).set_points_as_corners([at(t) for t in ts])

    def marker():
        return Dot(
            at(float(np.clip(now.get_value(), *span))), radius=0.07,
            color=lighten(STRAIN_COLOR),
        )

    return panel(VGroup(zero, tag)), VGroup(panel.redraw(curve), panel.redraw(marker))


def returning_waves(now, h=strain, panel=FULL_FRAME):
    """The light back from each arm, overlaid where the two recombine.

    E_x = sin(ku - wt + dphi/2) and E_y = -sin(ku - wt - dphi/2): the splitter
    puts the y arm's beam half a cycle behind, so with equal arms the two are
    mirror images and sum to nothing.
    """
    u = np.linspace(0, PANEL_X[1] - PANEL_X[0], 260)

    def row(y, field, color, width=STRAIN_STROKE_WIDTH):
        def draw():
            t = now.get_value()
            return VMobject(stroke_color=color, stroke_width=width).set_points_as_corners(
                np.column_stack([PANEL_X[0] + u, y + field(u, t), 0 * u])
            )
        return panel.redraw(draw)

    def carrier(u, t):
        return K_INSET * u - OMEGA_INSET * t

    def e_x(u, t):
        return RETURN_AMPLITUDE * np.sin(carrier(u, t) + phase_difference(t, h) / 2)

    def e_y(u, t):
        return -RETURN_AMPLITUDE * np.sin(carrier(u, t) - phase_difference(t, h) / 2)

    zero_return = DashedLine(
        [PANEL_X[0], RETURN_Y, 0], [PANEL_X[1], RETURN_Y, 0], **GUIDE_STYLE
    )
    zero_sum = DashedLine(
        [PANEL_X[0], SUM_Y, 0], [PANEL_X[1], SUM_Y, 0], **GUIDE_STYLE
    )
    key = VGroup(
        MathTex(r"\text{from } L_x", font_size=FONT_LEGEND, color=lighten(X_ARM_COLOR)),
        MathTex(r"\text{from } L_y", font_size=FONT_LEGEND, color=lighten(Y_ARM_COLOR)),
    ).arrange(RIGHT, buff=0.6).move_to(
        [np.mean(PANEL_X), RETURN_Y + RETURN_AMPLITUDE + 0.35, 0]
    )
    sum_tag = Tex(
        "at the detector", font_size=FONT_LEGEND, color=OUTPUT_COLOR
    ).move_to([np.mean(PANEL_X), SUM_Y + 2 * RETURN_AMPLITUDE + 0.3, 0])

    return (
        panel(VGroup(zero_return, key)),
        VGroup(row(RETURN_Y, e_x, X_ARM_COLOR), row(RETURN_Y, e_y, Y_ARM_COLOR)),
        panel(VGroup(zero_sum, sum_tag)),
        row(SUM_Y, lambda u, t: e_x(u, t) + e_y(u, t), OUTPUT_COLOR, 4),
    )


def run(scene, now, to, *anims):
    """Advance the lab clock to `to`, playing `anims` over the same stretch."""
    scene.play(
        now.animate.set_value(to), *anims,
        rate_func=linear, run_time=to - now.get_value(),
    )


def make_apparatus(now, h=strain, panel=FULL_FRAME):
    """The title, the optics and their labels, with the test masses riding
    the wave. Returns (the title and labels, the optics, which go over the
    light, the arm labels)."""
    title = Tex(
        "LIGO: a Michelson interferometer", font_size=FONT_TITLE
    ).to_corner(UL)
    laser = make_laser()
    splitter = make_splitter()
    detector = make_detector()
    x_mirror = make_mirror(vertical=True).move_to(X_END)
    y_mirror = make_mirror(vertical=False).move_to(Y_END)
    # where each test mass hangs at rest, so its motion reads against something
    x_rest = make_guide(X_END + UP * 0.7, X_END + DOWN * 0.7)
    y_rest = make_guide(Y_END + LEFT * 0.7, Y_END + RIGHT * 0.7)

    splitter_tag = Tex(
        "beam splitter", font_size=FONT_LEGEND, color=OPTIC_COLOR
    ).next_to(BS, DL, buff=0.4)
    mass_tags = VGroup(
        Tex("test mass", font_size=FONT_LEGEND, color=OPTIC_COLOR).next_to(
            X_END, DOWN, buff=0.85
        ),
        Tex("test mass", font_size=FONT_LEGEND, color=OPTIC_COLOR).next_to(
            Y_END, RIGHT, buff=0.85
        ),
    )
    arm_tags = VGroup(
        MathTex("L_x", font_size=FONT_STATE, color=lighten(X_ARM_COLOR)).move_to(
            BS + RIGHT * ARM / 2 + DOWN * 0.45
        ),
        MathTex("L_y", font_size=FONT_STATE, color=lighten(Y_ARM_COLOR)).move_to(
            BS + UP * ARM / 2 + LEFT * 0.5
        ),
    )
    optics = panel(VGroup(splitter, x_mirror, y_mirror, detector, laser))
    labels = panel(VGroup(title, splitter_tag, x_rest, y_rest, mass_tags))
    x_mirror.add_updater(
        lambda m: m.move_to(panel.point(mirror_positions(now.get_value(), h)[0]))
    )
    y_mirror.add_updater(
        lambda m: m.move_to(panel.point(mirror_positions(now.get_value(), h)[1]))
    )
    return labels, optics, panel(arm_tags)


def make_light(now, lit_in, lit_arm, h=strain, panel=FULL_FRAME):
    """The beams, chained so their phase runs on from one to the next, and
    the glow on the detector. `lit_in` and `lit_arm` say how far the light
    has got down the input beam and the arms."""
    input_length = np.linalg.norm(BS - LASER)

    def carrier():
        return -OMEGA_LIGHT * now.get_value()

    def input_wave():
        return wave(LASER, BS, LIGHT_AMPLITUDE, carrier(), lit_in.get_value())

    def arm_wave(end_index):
        def draw():
            end = mirror_positions(now.get_value(), h)[end_index]
            return wave(
                BS, end, LIGHT_AMPLITUDE, carrier() + K_LIGHT * input_length,
                lit_arm.get_value(),
            )
        return draw

    def arm_beam(end_index):
        return lambda: beam(
            BS, mirror_positions(now.get_value(), h)[end_index], lit_arm.get_value()
        )

    def output_share():
        """The field at the detector, relative to full brightness."""
        return np.sin(phase_difference(now.get_value(), h) / 2)

    def output_wave():
        share = output_share()
        return wave(
            BS, DETECTOR, LIGHT_AMPLITUDE * share,
            carrier() + K_LIGHT * (input_length + 2 * ARM),
        ).set_stroke(opacity=abs(share))

    lights = VGroup(
        panel.redraw(lambda: beam(LASER, BS, lit_in.get_value())),
        panel.redraw(arm_beam(0)),
        panel.redraw(arm_beam(1)),
        panel.redraw(lambda: beam(BS, DETECTOR, opacity=output_share() ** 2)),
        panel.redraw(lambda: input_wave().set_stroke(
            LASER_COLOR, BEAM_STROKE_WIDTH)),
        panel.redraw(lambda: arm_wave(0)().set_stroke(
            LASER_COLOR, BEAM_STROKE_WIDTH)),
        panel.redraw(lambda: arm_wave(1)().set_stroke(
            LASER_COLOR, BEAM_STROKE_WIDTH)),
        panel.redraw(lambda: output_wave().set_stroke(
            LASER_COLOR, BEAM_STROKE_WIDTH)),
    )
    glow = panel.redraw(lambda: detector_glow(now, h))
    return glow, lights


def make_equation(panel=FULL_FRAME):
    """Delta phi in the arm lengths, then in h, under the readout panel; and
    the scale of the real thing under that."""
    readout = MathTex(
        r"\Delta\phi", r"= 2k\,(", "L_x", "-", "L_y", ")",
        font_size=FONT_ANNOTATION,
    )
    readout[2].set_color(lighten(X_ARM_COLOR))
    readout[4].set_color(lighten(Y_ARM_COLOR))
    in_h = MathTex(
        r"= \frac{4\pi L}{\lambda}\, h", font_size=FONT_ANNOTATION
    )
    in_h.next_to(readout, DOWN, buff=0.25).align_to(readout[1], LEFT)
    # high enough that the scale line under it clears the slide number
    VGroup(readout, in_h).move_to([np.mean(PANEL_X), -2.15, 0])
    scale = MathTex(
        r"h \sim 10^{-21},\ L = 4\,\mathrm{km}"
        r"\ \Rightarrow\ \Delta L \sim 10^{-18}\,\mathrm{m}",
        font_size=FONT_LEGEND - 6, color=lighten(GUIDE_COLOR),
    ).next_to(VGroup(readout, in_h), DOWN, buff=0.35)
    return panel(readout), panel(in_h), panel(scale)


class LIGOMichelson(Scene):
    """A Michelson interferometer on a dark fringe, lit up by a passing wave."""

    def beat(self):
        """The pause on the dark port, before the wave: nothing here, a click
        on the slide version."""

    def construct(self):
        now = ValueTracker(0.0)
        lit_in = ValueTracker(0.0)  # how far light has got down each beam
        lit_arm = ValueTracker(0.0)

        # --- the apparatus ---
        labels, optics, arm_tags = make_apparatus(now)
        self.play(FadeIn(labels), FadeIn(optics), run_time=1.2)

        # --- the light ---
        glow, lights = make_light(now, lit_in, lit_arm)
        # light goes under the optics, and the glow under the detector
        self.add(glow, lights)
        self.bring_to_front(*optics)

        run(self, now, T_INPUT, lit_in.animate.set_value(1))
        run(self, now, T_ARMS, lit_arm.animate.set_value(1), FadeIn(arm_tags))

        # --- equal arms: the returning beams cancel ---
        # Said, not drawn: the returning waves (returning_waves) are left to
        # the scenes that set this beside something else.
        detector_tag = optics[3][2]
        dark_note = Tex(
            "equal arms: the beams cancel", font_size=FONT_LEGEND,
            color=lighten(GUIDE_COLOR),
        ).next_to(detector_tag, UP, buff=0.3).align_to(detector_tag, LEFT)
        run(self, now, T_READOUT)
        run(self, now, T_DARK, FadeIn(dark_note))
        self.beat()

        # --- a wave passes ---
        trace_axes, trace = make_strain_trace(
            now, panel=MICHELSON_TRACE, amplitude=MICHELSON_TRACE_AMPLITUDE
        )
        run(
            self, now, GW_ON, FadeOut(dark_note),
            FadeIn(trace_axes), FadeIn(trace),
        )

        readout, in_h, scale = make_equation()
        VGroup(readout, in_h).scale(MICHELSON_EQUATION_SCALE).move_to(
            [COLUMN_X, MICHELSON_EQUATION_Y, 0]
        )
        scale.scale(MICHELSON_SCALE_SCALE).move_to([COLUMN_X, MICHELSON_SCALE_Y, 0])
        run(self, now, GW_ON + 1.5, FadeIn(readout))
        run(self, now, GW_ON + 3.5, FadeIn(in_h))
        run(self, now, GW_OFF)
        run(self, now, GW_OFF + 1.0, FadeIn(scale))
        run(self, now, T_END)
