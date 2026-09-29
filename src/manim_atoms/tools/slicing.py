"""Velocity slicing: a long clock pulse picks the slowest atoms out of a cloud.

A pi pulse of duration tau on the clock line is resonant only for atoms whose
Doppler shift is within about 1/tau of zero, so it excites a narrow slice of
the velocity distribution and leaves the rest in the ground state, to be
pushed away afterwards. The slice has the pulse's own line shape: the Rabi
excitation probability

    P(u) = sin^2(pi/2 sqrt(1 + u^2)) / (1 + u^2),   u = k v / Omega,

which is one at resonance and falls off in sinc-like sidelobes.

VelocityPlot draws the distribution and that line shape on one pair of axes;
SlicingCloud draws the same atoms as a cloud, moving along the clock beam at
their own velocities.
"""

import numpy as np
from manim import *

from aionanim.style import *


# --- the physics, in units of the Rabi frequency --------------------------
# The thermal width is what sets how much narrower the slice is. Before
# slicing the clock line is Doppler broadened to 60 kHz FWHM, which at 698 nm
# is a 3 uK cloud of 87Sr. A 200 us slicing pulse has Omega = 2 pi x 2.5 kHz,
# and in those units the 3 uK cloud has sigma = 9.7, while the pulse's core
# (FWHM 1.6, sigma ~0.68) is some fourteen times narrower: a velocity spread
# that corresponds to ~10 nK.
SLICE_THERMAL_SIGMA = 9.7
SLICE_U_RANGE = (-27.0, 27.0)
SLICE_SAMPLES = 1081


def excitation(u):
    """The pi pulse's excitation probability at Doppler detuning u (in Omega)."""
    s = 1 + np.asarray(u, dtype=float) ** 2
    return np.sin(PI / 2 * np.sqrt(s)) ** 2 / s


def thermal(u, sigma=SLICE_THERMAL_SIGMA):
    """The velocity distribution before the pulse, peak normalised to one."""
    return np.exp(-np.asarray(u, dtype=float) ** 2 / (2 * sigma**2))


# --- the plot -------------------------------------------------------------
PLOT_WIDTH = 7.0  # wide, so the slice's sidelobes still show against a 3 uK cloud
PLOT_HEIGHT = 3.3
PLOT_Y_MAX = 1.12  # a little headroom over the peak
LINE_LABEL_AT = (5.5, 1.02)  # (u, height): clear of the thermal curve's shoulder


class VelocityPlot(VGroup):
    """The velocity distribution, stacked by internal state, with the pulse's
    excitation probability over it on the same scale.

    ``excite`` (0 to 1) moves the excited share, G(u) P(u), from the ground
    band into the excited band below it, so the total stays the thermal
    curve; ``push`` (0 to 1) then empties the ground band. ``outline`` is the
    thermal curve dashed, for comparing the slice against at the end.
    """

    def __init__(self, center=ORIGIN, **kwargs):
        super().__init__(**kwargs)
        # placed before anything is drawn from it: the curves that come and go
        # are built in the axes' coordinates and aren't part of this group. The
        # x axis runs from 0 rather than from SLICE_U_RANGE[0], which would put
        # the y axis at zero velocity, through the middle of the distribution;
        # c2p shifts u onto it.
        self.axes = Axes(
            x_range=[0, SLICE_U_RANGE[1] - SLICE_U_RANGE[0], 1], y_range=[0, PLOT_Y_MAX, 1],
            x_length=PLOT_WIDTH, y_length=PLOT_HEIGHT, tips=False,
            axis_config=dict(color=PLOT_FOREGROUND, stroke_width=2, include_ticks=False),
        ).move_to(center)
        zero = self.c2p(0, 0)
        tick = Line(zero, zero + DOWN * 0.12, color=PLOT_FOREGROUND, stroke_width=2)
        zero_label = MathTex("0", font_size=FONT_TICK, color=PLOT_FOREGROUND)
        zero_label.next_to(tick, DOWN, buff=0.08)
        x_label = Tex("velocity along the clock beam", font_size=FONT_AXIS,
                      color=PLOT_FOREGROUND).next_to(self.axes.x_axis, DOWN, buff=0.45)
        y_label = Tex("atoms", font_size=FONT_AXIS, color=PLOT_FOREGROUND)
        y_label.rotate(PI / 2).next_to(self.axes.y_axis, LEFT, buff=0.2)
        self.frame = VGroup(self.axes, tick, zero_label, x_label, y_label)

        self.u = np.linspace(*SLICE_U_RANGE, SLICE_SAMPLES)
        self.g = thermal(self.u)
        self.p = excitation(self.u)
        self.excite = ValueTracker(0.0)
        self.push = ValueTracker(0.0)

        self.excited_band = VMobject(stroke_width=0, fill_color=SLICE_COLD_COLOR,
                                     fill_opacity=SLICE_FILL_OPACITY)
        self.ground_band = VMobject(stroke_width=0, fill_color=SLICE_HOT_COLOR,
                                    fill_opacity=SLICE_FILL_OPACITY)
        self.top_edge = VMobject(stroke_color=lighten(SLICE_HOT_COLOR), stroke_width=3)
        self.slice_edge = VMobject(stroke_color=lighten(SLICE_COLD_COLOR), stroke_width=3)
        self.bands = VGroup(self.excited_band, self.ground_band, self.top_edge,
                            self.slice_edge)
        self.bands.add_updater(lambda m: self._fill())
        self._fill()

        self.line_shape = self._curve(self.p, stroke_color=TRANSITION_698_COLOR,
                                      stroke_width=SLICE_PROFILE_WIDTH)
        # just "excitation": the scene's own readout of pi-pulse fidelity is about
        # the interferometer's pulse, not this one
        self.line_label = Tex(r"excitation\\probability", font_size=FONT_AXIS,
                              color=TRANSITION_698_COLOR)
        self.line_label.next_to(self.c2p(*LINE_LABEL_AT), RIGHT, buff=0.1)
        self.outline = DashedVMobject(
            self._curve(self.g, stroke_color=lighten(SLICE_HOT_COLOR), stroke_width=2.5),
            num_dashes=70,
        )
        self.add(self.bands, self.frame)

    def c2p(self, u, y):
        return self.axes.c2p(u - SLICE_U_RANGE[0], y)

    def _points(self, u, y):
        # The axes are linear, so c2p is affine: three calls rather than one
        # per sample (per sample, the band updater was most of the render).
        origin = self.c2p(0, 0)
        du = self.c2p(1, 0) - origin
        dy = self.c2p(0, 1) - origin
        return origin + np.outer(u, du) + np.outer(y, dy)

    def _curve(self, y, **style):
        return VMobject(**style).set_points_smoothly(self._points(self.u, y))

    def _band(self, band, lower, upper):
        pts = np.concatenate([self._points(self.u, upper),
                              self._points(self.u[::-1], lower[::-1])])
        band.set_points_as_corners(np.concatenate([pts, pts[:1]]))

    def _fill(self):
        excited = self.g * self.p * self.excite.get_value()
        top = excited + (self.g - excited) * (1 - self.push.get_value())
        self._band(self.excited_band, np.zeros_like(self.u), excited)
        self._band(self.ground_band, excited, top)
        self.top_edge.set_points_as_corners(self._points(self.u, top))
        self.top_edge.set_stroke(opacity=float(np.max(top - excited) > 1e-3))
        self.slice_edge.set_points_as_corners(self._points(self.u, excited))
        self.slice_edge.set_stroke(opacity=self.excite.get_value())


# --- the cloud ------------------------------------------------------------
# The same atoms seen side on: each drifts along the (vertical) clock beam at
# its own velocity, drawn from the thermal distribution, and is excited by the
# pulse with probability P(u) -- so the purple ones are the slow ones. The
# push beam comes in from the side and sweeps the rest out of the frame.
CLOUD_N = 260  # a slice is ~7 % of them, so enough that the slice is a crowd
CLOUD_WIDTH = 2.4  # the spread across the beam
CLOUD_HEIGHT = 1.2  # the spread along it, at the start
CLOUD_DRIFT = 0.005  # scene units per second per unit of u
PUSH_DISTANCE = 3.0  # how far a pushed atom goes, across the beam


class SlicingCloud(VGroup):
    """``excite`` and ``push`` as on VelocityPlot; the drift runs by itself."""

    def __init__(self, center, seed=3, **kwargs):
        super().__init__(**kwargs)
        rng = np.random.default_rng(seed)
        self.center = np.array(center[:2], dtype=float)
        self.home = np.column_stack([
            rng.uniform(-CLOUD_WIDTH / 2, CLOUD_WIDTH / 2, CLOUD_N),
            rng.normal(scale=CLOUD_HEIGHT / 4, size=CLOUD_N),
        ])
        self.v = rng.normal(scale=SLICE_THERMAL_SIGMA, size=CLOUD_N)
        self.is_slow = rng.random(CLOUD_N) < excitation(self.v)
        self.push_rate = rng.uniform(0.8, 1.2, CLOUD_N)  # so they don't leave as a block
        self.excite = ValueTracker(0.0)
        self.push = ValueTracker(0.0)
        self.t = 0.0
        self.add(*[Dot(radius=CLOUD_DOT_RADIUS * 1.3, stroke_width=0) for _ in range(CLOUD_N)])
        self.add_updater(self._move)
        self._move(self, 0)

    def _move(self, m, dt):
        self.t += dt
        push = self.push.get_value()
        xy = self.center + self.home + np.column_stack([
            np.where(self.is_slow, 0.0, PUSH_DISTANCE * push**2 * self.push_rate),
            CLOUD_DRIFT * self.v * self.t,
        ])
        excited = interpolate_color(SLICE_HOT_COLOR, SLICE_COLD_COLOR, self.excite.get_value())
        gone = 1 - np.clip(push * 1.4 - 0.2, 0, 1)  # a pushed atom fades as it goes
        for dot, p, slow in zip(self.submobjects, xy, self.is_slow):
            dot.move_to([p[0], p[1], 0])
            if slow:
                dot.set_fill(excited, opacity=1)
            else:
                dot.set_fill(SLICE_HOT_COLOR, opacity=gone)
