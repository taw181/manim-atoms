"""Log-log characteristic-strain plots in manim.

The pieces MergerOnSensitivityPlot and the sensitivity build-up share: axes
in decades with 10^n tick labels, the conversion from (log f, log h) to
scene points, and a detector's curve with its region shaded above it. Each
Axes carries its own log ranges, so every helper takes just the axes.
"""

import numpy as np
from manim import *

from aionanim.physics.gw_signals import load_sensitivity
from aionanim.style import *


def sensitivity_axes(log_f_range, log_h_range, origin, width, height,
                     x_label="Frequency / Hz", y_label="Characteristic strain",
                     tick_font=FONT_TICK, label_font=FONT_AXIS, label_every=(1, 1),
                     buff=0.15):
    """Log-log axes in decades, with 10^n tick labels, as (axes, frame).

    The axes run from 0, not from the log ranges themselves: Axes draws each
    axis through the coordinate origin, which would put the frequency axis at
    h = 1. plot_point does the conversion. Ranges may end on half decades;
    only whole decades get a tick label, and of those only every
    label_every[0]th on x and label_every[1]th on y (the multiples of it).
    The defaults are the strain plots'; another quantity passes its own axis
    labels (Tex), or None to leave one off, and a small plot smaller type.
    """
    (f0, f1), (h0, h1) = log_f_range, log_h_range
    axes = Axes(
        x_range=[0, f1 - f0, 1],
        y_range=[0, h1 - h0, 1],
        x_length=width,
        y_length=height,
        tips=False,
        axis_config=dict(
            color=PLOT_FOREGROUND, stroke_width=2, tick_size=0.06, include_ticks=True
        ),
    )
    axes.log_origin = (f0, h0)
    axes.log_top = h1
    axes.shift(origin - axes.c2p(0, 0))
    decade = lambda n: MathTex(rf"10^{{{n}}}", font_size=tick_font, color=PLOT_FOREGROUND)
    x_ticks = VGroup(*(
        decade(n).next_to(plot_point(axes, n, h0), DOWN, buff=buff)
        for n in range(int(np.ceil(f0)), int(np.floor(f1)) + 1)
        if n % label_every[0] == 0
    ))
    y_ticks = VGroup(*(
        decade(n).next_to(plot_point(axes, f0, n), LEFT, buff=buff)
        for n in range(int(np.ceil(h0)), int(np.floor(h1)) + 1)
        if n % label_every[1] == 0
    ))
    frame = VGroup(axes, x_ticks, y_ticks)
    if x_label is not None:
        x_label = Tex(x_label, font_size=label_font, color=PLOT_FOREGROUND)
        frame.add(x_label.next_to(x_ticks, DOWN, buff=buff).set_x(axes.x_axis.get_center()[0]))
    if y_label is not None:
        y_label = Tex(y_label, font_size=label_font, color=PLOT_FOREGROUND)
        frame.add(y_label.rotate(PI / 2).next_to(y_ticks, LEFT, buff=buff))
    return axes, frame


def plot_point(axes, log_f, log_h):
    return axes.c2p(log_f - axes.log_origin[0], log_h - axes.log_origin[1])


def curve_points(axes, f, h):
    return np.array([plot_point(axes, x, y) for x, y in zip(np.log10(f), np.log10(h))])


def detector_region(axes, stem, color):
    """A detector's curve, and its region shaded up to the top of the axes."""
    points = curve_points(axes, *load_sensitivity(stem))
    curve = VMobject(stroke_color=color, stroke_width=GW_TRACK_WIDTH)
    curve.set_points_as_corners(points)
    top = plot_point(axes, axes.log_origin[0], axes.log_top)[1]
    region = Polygon(
        *points, [points[-1][0], top, 0], [points[0][0], top, 0],
        stroke_width=0, fill_color=color, fill_opacity=GW_REGION_OPACITY,
    )
    return region, curve
