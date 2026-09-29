"""Two crossed dipole traps loaded from the red MOT, drawn as a cartoon.

Side on, each trap is a thin horizontal beam crossed by a shared vertical
one, the upper trap covered by the transparency beam. The atoms are shared
out between them by LoadingAtoms, whose knobs are the loading steps; a
histogram over the ground state's m_F sublevels shows the optical pumping
that follows, and a pointer marks where the MOT's field zero is.
"""

import numpy as np
from manim import *

from aionanim.style import *
from aionanim.tools.cooling import MOT_AXES, chevron


SPIN_HIST_WIDTH = 2.2
SPIN_HIST_HEIGHT = 1.3  # of a bar holding every atom


# --- trap light -----------------------------------------------------------
def gaussian_band(start, end, width, color, opacity=TRAP_BEAM_OPACITY,
                  layers=TRAP_BEAM_LAYERS):
    """A beam seen side on: nested bands, brightest along its axis, so it
    reads as a Gaussian profile rather than a flat bar."""
    start, end = np.array(start, dtype=float), np.array(end, dtype=float)
    return VGroup(*[
        Rectangle(width=np.linalg.norm(end - start), height=width * (1 - k / layers),
                  stroke_width=0, fill_color=color, fill_opacity=opacity / layers)
        .rotate(angle_of_vector(end - start)).move_to((start + end) / 2)
        for k in range(layers)
    ])


def gaussian_spot(center, radius, color, opacity=TRAP_BEAM_OPACITY,
                  layers=TRAP_BEAM_LAYERS):
    """A beam seen end on, the same way: nested discs."""
    return VGroup(*[
        Circle(radius=radius * (1 - k / layers), stroke_width=0, fill_color=color,
               fill_opacity=opacity / layers).move_to(center)
        for k in range(layers)
    ])


# --- the MOT, next to the traps ------------------------------------------
# The MOT beams are far wider than the traps, so on this scale they are not
# beams but a wash of red light over the whole figure, with the usual
# arrowheads round its edge pointing in along the MOT's three axes.
def make_mot_glow(center, radius, color=TRANSITION_689_COLOR):
    center = np.array(center, dtype=float)
    heads = VGroup(*[
        chevron(-d, center + d * radius * 0.85, color)
        for angle in MOT_AXES for d in (rotate_vector(RIGHT, angle * DEGREES),
                                        rotate_vector(LEFT, angle * DEGREES))
    ]).set_stroke(opacity=MOT_BEAM_EDGE_OPACITY)
    glow = gaussian_spot(center, radius, color, opacity=MOT_GLOW_OPACITY,
                         layers=MOT_GLOW_LAYERS)
    return VGroup(glow, heads)


# --- the magnetic field ---------------------------------------------------
def make_field_zero(y, x, color=lighten(GUIDE_COLOR)):
    """A pointer at the height of the quadrupole field's zero, from the side
    of the figure rather than on the traps, where it would hide the atoms."""
    tip = np.array([x, y, 0.0])
    pointer = Triangle(fill_color=color, fill_opacity=1, stroke_width=0)
    pointer.rotate(-PI / 2).scale(0.1).move_to(tip, aligned_edge=RIGHT)
    label = MathTex(r"B = 0", font_size=FONT_LEGEND, color=color)
    label.next_to(pointer, LEFT, buff=0.12)
    return VGroup(pointer, label)


# --- the atoms ------------------------------------------------------------
# Every atom has a place in the MOT cloud and a place in a trap. In a crossed
# trap most atoms sit where the beams cross and the rest spread out along the
# horizontal beam, which holds them only vertically. The ones that go to the
# lower trap fall all the way down to it when the MOT lets go, spreading as
# they fall, and the MOT then gathers them up round it again.
LOAD_UPPER_SHARE = 0.5
LOAD_MOT_RADIUS = 0.22  # the narrowband MOT's spread
LOAD_FALL_SPREAD = 0.8  # how far the released cloud swells as it drops
TRAP_CORE_SIGMA = 0.12
TRAP_WING_SIGMA = 0.9
TRAP_WING_SHARE = 0.3
TRAP_WING_CLIP = 2.0  # no further out than this, so every atom sits in its beam
TRAP_THICKNESS = 0.025
LOAD_JITTER = 0.02  # in the MOT; a trapped atom jiggles a fifth as much
LOAD_JITTER_TERMS = 3
LOAD_JITTER_FREQ = (3.0, 8.0)  # rad/s


class LoadingAtoms(VGroup):
    """The red MOT's atoms, shared out between two dipole traps.

    Those bound for the upper trap settle into it as ``load_upper`` goes
    0 to 1. The rest stay in the MOT until it is released: they drop to the
    lower trap as ``fall`` goes 0 to 1, are gathered up by the MOT round it as
    ``recapture`` does, and settle into that trap with ``load_lower``.
    ``glow_upper`` and ``glow_lower`` (0 to 1) light each group in the 689 nm
    red while it scatters MOT light; dark, an atom takes the ground-state
    colour it has in every interferometer figure.
    """

    def __init__(self, n, upper, lower, seed=2, **kwargs):
        super().__init__(**kwargs)
        rng = np.random.default_rng(seed)
        self.upper = np.array(upper[:2], dtype=float)
        self.lower = np.array(lower[:2], dtype=float)
        self.is_upper = rng.random(n) < LOAD_UPPER_SHARE
        self.mot = rng.normal(scale=LOAD_MOT_RADIUS, size=(n, 2))
        wide = rng.random(n) < TRAP_WING_SHARE
        self.trap = np.column_stack([
            np.clip(rng.normal(size=n) * np.where(wide, TRAP_WING_SIGMA, TRAP_CORE_SIGMA),
                    -TRAP_WING_CLIP, TRAP_WING_CLIP),
            rng.normal(scale=TRAP_THICKNESS, size=n),
        ])
        self.freq = rng.uniform(*LOAD_JITTER_FREQ, size=(n, 2, LOAD_JITTER_TERMS))
        self.phase = rng.uniform(0, TAU, size=(n, 2, LOAD_JITTER_TERMS))

        self.load_upper = ValueTracker(0.0)
        self.fall = ValueTracker(0.0)
        self.recapture = ValueTracker(0.0)
        self.load_lower = ValueTracker(0.0)
        self.glow_upper = ValueTracker(1.0)
        self.glow_lower = ValueTracker(1.0)
        self.t = 0.0
        self.add(*[Dot(radius=CLOUD_DOT_RADIUS, stroke_width=0) for _ in range(n)])
        self.add_updater(self._move)
        self._move(self, 0)

    def _move(self, m, dt):
        self.t += dt
        jitter = np.sin(self.freq * self.t + self.phase).sum(axis=2)
        jitter *= LOAD_JITTER / np.sqrt(LOAD_JITTER_TERMS)

        a = self.load_upper.get_value()
        upper = self.upper + self.mot * (1 - a) + self.trap * a + jitter * (1 - 0.8 * a)

        f = self.fall.get_value()
        fallen = self.upper + (self.lower - self.upper) * f
        fallen = fallen + self.mot * (1 + LOAD_FALL_SPREAD * f)
        r = self.recapture.get_value()
        caught = fallen + (self.lower + self.mot - fallen) * r
        b = self.load_lower.get_value()
        lower = caught + (self.lower + self.trap - caught) * b + jitter * (1 - 0.8 * b)

        xy = np.where(self.is_upper[:, None], upper, lower)
        colors = {
            True: interpolate_color(ATOM_COLOR, TRANSITION_689_COLOR, self.glow_upper.get_value()),
            False: interpolate_color(ATOM_COLOR, TRANSITION_689_COLOR, self.glow_lower.get_value()),
        }
        for dot, p, up in zip(self.submobjects, xy, self.is_upper):
            dot.move_to([p[0], p[1], 0]).set_fill(colors[bool(up)], opacity=1)


# --- optical pumping ------------------------------------------------------
# The ground state of 87Sr has F = 9/2 and so ten m_F sublevels, which the
# atoms start out spread evenly over. Circularly polarised 689 nm light walks
# them up the ladder until they pile up in the stretched state m_F = +9/2.
# Drawn as a histogram whose populations go as exp(beta m_F), beta climbing
# from zero: a smooth tilt of the whole distribution toward the top rung.
SPIN_M = np.arange(-4.5, 5.0)
SPIN_PUMP_BETA = 7.0  # beta at the end of the pumping
SPIN_BAR_FILL = 0.7  # of each bar's slot


class SpinHistogram(VGroup):
    """How the atoms are spread over m_F, pumped into +9/2 as ``pump`` goes 0 to 1."""

    def __init__(self, width=SPIN_HIST_WIDTH, height=SPIN_HIST_HEIGHT, **kwargs):
        super().__init__(**kwargs)
        self.full_height = height
        slot = width / len(SPIN_M)
        self.baseline = Line(LEFT * width / 2, RIGHT * width / 2,
                             stroke_width=2, color=lighten(GUIDE_COLOR))
        self.bars = VGroup(*[
            Rectangle(width=slot * SPIN_BAR_FILL, height=height, stroke_width=0,
                      fill_color=ATOM_COLOR, fill_opacity=1)
            .move_to([-width / 2 + slot * (k + 0.5), 0, 0], aligned_edge=DOWN)
            for k in range(len(SPIN_M))
        ])
        ends = VGroup(
            MathTex(r"-\tfrac{9}{2}", font_size=FONT_TICK, color=PLOT_FOREGROUND)
            .next_to(self.bars[0], DOWN, buff=0.12),
            MathTex(r"+\tfrac{9}{2}", font_size=FONT_TICK, color=PLOT_FOREGROUND)
            .next_to(self.bars[-1], DOWN, buff=0.12),
        )
        ends.align_to(self.baseline, UP).shift(DOWN * 0.12)
        axis = MathTex(r"m_F", font_size=FONT_AXIS, color=PLOT_FOREGROUND)
        axis.next_to(self.baseline, DOWN, buff=0.15)
        self.add(self.bars, self.baseline, ends, axis)
        self.pump = ValueTracker(0.0)
        self.add_updater(self._fill)
        self._fill(self)

    def _fill(self, m):
        weights = np.exp(SPIN_PUMP_BETA * self.pump.get_value() * SPIN_M)
        shares = weights / weights.sum()
        floor = self.baseline.get_center()
        for bar, share in zip(self.bars, shares):
            bar.stretch_to_fit_height(max(share * self.full_height, 1e-3))
            bar.move_to([bar.get_x(), floor[1], 0], aligned_edge=DOWN)
