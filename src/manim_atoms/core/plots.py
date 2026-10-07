"""Plots drawn in manim: log-log and linear axes, keys, and scatters of
thousands of dots.

- log_axes: axes in decades with 10^n tick labels, as (axes, frame); each
  Axes carries its own log ranges, so plot_point and curve_points take just
  the axes to turn (log x, log y) or linear (x, y) arrays into scene points.
- dot_points, dot_cloud, static_cloud: a scatter as one VMobject whose
  points are every dot's circle end to end, so cairo draws one path rather
  than walking thousands of mobjects; dot_cloud shows the first ``count``
  of them, so the dots can arrive one at a time.
- ticked_axes: linear axes with MathTex x ticks, numbered y ticks and axis
  labels, as (axes, frame); legend_row: a row of (label, colour) keys.
"""

import numpy as np
from manim import *

from manim_atoms.style import *


def log_axes(log_x_range, log_y_range, origin, width, height, x_label=None,
             y_label=None, tick_font=FONT_TICK, label_font=FONT_AXIS, label_every=(1, 1),
             buff=0.15):
    """Log-log axes in decades, with 10^n tick labels, as (axes, frame).

    The axes run from 0, not from the log ranges themselves: Axes draws each
    axis through the coordinate origin, which would put the frequency axis at
    h = 1. plot_point does the conversion. Ranges may end on half decades;
    only whole decades get a tick label, and of those only every
    label_every[0]th on x and label_every[1]th on y (the multiples of it).
    The axis labels are Tex, and None leaves one off; a small plot passes
    smaller type.
    """
    (f0, f1), (h0, h1) = log_x_range, log_y_range
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


def plot_point(axes, log_x, log_y):
    """The scene point of (log10 x, log10 y) on ``axes`` from log_axes."""
    return axes.c2p(log_x - axes.log_origin[0], log_y - axes.log_origin[1])


def curve_points(axes, x, y):
    """Scene points of a curve given as linear (x, y) arrays, for set_points_as_corners."""
    return np.array([plot_point(axes, a, b) for a, b in zip(np.log10(x), np.log10(y))])


def dot_points(axes, xs, ys):
    """Every dot's circle, end to end, in the order the dots arrive."""
    template = Circle(radius=DATA_DOT_RADIUS, num_components=5).points
    centres = np.array([axes.c2p(x, y) for x, y in zip(xs, ys)])
    return (centres[:, None, :] + template[None, :, :]).reshape(-1, 3), len(template)


def dot_cloud(points, per_dot, color, count, opacity):
    """A series' dots as one VMobject, showing the first ``count`` of them as it runs."""
    cloud = VMobject(fill_color=color, fill_opacity=opacity, stroke_width=0)

    def grow(mob):
        n = int(count.get_value())
        # set_points on an empty array leaves cairo nothing to draw, which is
        # what zero dots should look like.
        mob.set_points(points[: n * per_dot])

    cloud.add_updater(grow)
    return cloud


def static_cloud(points, color, opacity):
    """Every dot of a series as one still VMobject."""
    return VMobject(fill_color=color, fill_opacity=opacity,
                    stroke_width=0).set_points(points)


# --- linear axes and keys --------------------------------------------------
def ticked_axes(x_range, y_range, x_length, y_length, x_ticks, y_numbers,
                x_label, y_label):
    """Linear axes with tick labels and axis labels, as (axes, frame).

    The x ticks are (value, tex) pairs, set as MathTex, so they can read
    "pi"; the y axis is numbered at ``y_numbers``. The frame is (axes, x
    tick labels, y label, x label), x label last so a panel that loses it
    can transform the rest. x_label=None leaves it empty. Place the frame by
    shifting it so ``axes.c2p(0, 0)`` lands where the origin goes.
    """
    axes = Axes(
        x_range=x_range,
        y_range=y_range,
        x_length=x_length,
        y_length=y_length,
        tips=False,
        axis_config=dict(
            color=PLOT_FOREGROUND, stroke_width=2, tick_size=0.06,
            include_ticks=True,
        ),
        # the x ticks are MathTex set below, so the origin's 0 is the y axis's
        y_axis_config=dict(numbers_to_include=y_numbers,
                           font_size=FONT_TICK, numbers_to_exclude=[]),
        x_axis_config=dict(include_numbers=False),
    )
    ticks = VGroup(*(
        MathTex(tex, font_size=FONT_TICK, color=PLOT_FOREGROUND)
        .next_to(axes.c2p(x, 0), DOWN, buff=0.18)
        for x, tex in x_ticks
    ))
    axes.y_axis.numbers.set_color(PLOT_FOREGROUND)
    yl = Tex(y_label, font_size=FONT_AXIS, color=PLOT_FOREGROUND).rotate(PI / 2)
    yl.next_to(axes.y_axis.numbers, LEFT, buff=0.2)
    xl = VGroup()
    if x_label is not None:
        xl = Tex(x_label, font_size=FONT_AXIS, color=PLOT_FOREGROUND)
        xl.next_to(ticks, DOWN, buff=0.18).set_x(axes.x_axis.get_center()[0])
    return axes, VGroup(axes, ticks, yl, xl)


def legend_row(entries):
    """A row of (label, colour) keys, each a dot and its label."""
    rows = VGroup(*(
        VGroup(
            Dot(radius=0.07, color=color),
            Tex(label, font_size=FONT_AXIS, color=PLOT_FOREGROUND),
        ).arrange(RIGHT, buff=0.12)
        for label, color in entries
    ))
    return rows.arrange(RIGHT, buff=0.4)
