"""The HiFAIS atom source drawn from its CAD, and its MOT loading curves.

The chamber is the paper's own renders (Walker et al., AVS Quantum Sci. 8,
033201 (2026), Fig. 1(c) top view and (d) side view), shipped without their
labels as aionanim/data/images/hifais_chamber_{top,side}.png; the labels,
beams and atoms are drawn over them here, on points given in the render's own
pixels so they stay put whatever size the image is drawn at.

The plot is Fig. 5's inset, the whole of each loading run, drawn point by
point so it can fill in against a lab clock in ms.
"""

import numpy as np
from manim import *

from aionanim.physics.mot_loading import FIT_CUTOFF, loading_model
from aionanim.resources import data_path
from aionanim.style import *
from aionanim.tools.layout import image_point, load_image

CHAMBER_TOP = data_path("images", "hifais_chamber_top.png")  # 1317 x 1153 px
CHAMBER_SIDE = data_path("images", "hifais_chamber_side.png")  # 1326 x 1105 px

# --- where things are in the renders, in px from the upper left -----------
# Top view: the source chamber's cross is on the left, the oven on its lower
# arm and the Zeeman slowing beam coming down the upper one; the 2D MOT is
# where the arms cross, and the push beam sends its atoms right, through the
# differential pumping tube, to the 3D MOT in the middle of the science
# chamber's octagon.
TOP_2D_MOT = (314, 660)
TOP_3D_MOT = (686, 660)
TOP_OVEN = (314, 1085)  # the oven's flange, which the atoms leave upward from
TOP_ARM_END = (314, 0)  # the heated window the slowing beam comes in through
TOP_LEFT_EDGE = (0, 660)  # where the push beam comes in
TOP_SCIENCE_RIM = (840, 845)  # on the octagon, clear of the 3D MOT
# Side view: the source chamber left, the science chamber (three of the
# octagon's windows) in the middle, and the ion pump on the tee at the right.
SIDE_SOURCE = (250, 400)
SIDE_SCIENCE = (698, 420)
SIDE_PUMP = (1040, 60)

# --- the loading plot -----------------------------------------------------
LOAD_T_MAX = 120  # ms: every run's last point
LOAD_N_MAX = 1.75  # 1e9 atoms: above the hottest fit at LOAD_T_MAX
FIT_SAMPLES = 160


def chamber_view(path, height):
    return load_image(path, height=height)


def chamber_label(text, target, direction, length=0.7):
    """A label joined to ``target`` by a leader ``length`` long, leaving it in
    ``direction``. The text is outlined in the page colour, so it still reads
    where it overlaps the render."""
    target = np.asarray(target, dtype=float)
    d = normalize(np.asarray(direction, dtype=float))
    end = target + d * length
    leader = Line(target, end, **CHAMBER_LEADER_STYLE)
    dot = Dot(target, radius=CHAMBER_LEADER_DOT_RADIUS,
              color=CHAMBER_LEADER_STYLE["color"])
    label = Tex(text, font_size=FONT_CHAMBER_LABEL, color=CHAMBER_LABEL_COLOR)
    label.next_to(end, d, buff=0.1)
    label.set_stroke(PLOT_BACKGROUND, width=5, background=True)
    return VGroup(leader, dot, label)


def at(image, px):
    """A pixel of a render, on screen."""
    return image_point(image, *px)


def loading_axes(x_length, y_length):
    """Axes, tick labels and axis labels, as (axes, frame), in ms and 1e9."""
    axes = Axes(
        x_range=[0, LOAD_T_MAX, 20],
        y_range=[0, LOAD_N_MAX, 0.25],
        x_length=x_length,
        y_length=y_length,
        tips=False,
        axis_config=dict(color=PLOT_FOREGROUND, stroke_width=2, tick_size=0.05,
                         font_size=FONT_TICK),
        x_axis_config=dict(numbers_to_include=[0, 40, 80, 120]),
        # one 0, on the y axis, for the origin
        y_axis_config=dict(numbers_to_include=[0, 0.5, 1.0, 1.5], numbers_to_exclude=[],
                           decimal_number_config=dict(num_decimal_places=1)),
    )
    for axis in (axes.x_axis, axes.y_axis):
        axis.numbers.set_color(PLOT_FOREGROUND)
    xl = Tex(r"Loading time / ms", font_size=FONT_AXIS, color=PLOT_FOREGROUND)
    xl.next_to(axes.x_axis.numbers, DOWN, buff=0.2).set_x(axes.x_axis.get_center()[0])
    yl = Tex(r"Atom number / $10^9$", font_size=FONT_AXIS, color=PLOT_FOREGROUND)
    yl.rotate(PI / 2).next_to(axes.y_axis.numbers, LEFT, buff=0.2)
    yl.set_y(axes.y_axis.get_center()[1])
    return axes, VGroup(axes, xl, yl)


def loading_cutoff(axes):
    """The atom number the fits stop at, across the plot, labelled at its right
    end: above it the MOT goes unstable."""
    line = DashedLine(axes.c2p(0, FIT_CUTOFF), axes.c2p(LOAD_T_MAX, FIT_CUTOFF),
                      **LOADING_CUTOFF_STYLE)
    tag = Tex(r"fit limit", font_size=FONT_TICK, color=PLOT_FOREGROUND)
    tag.next_to(line.get_end(), UP, buff=0.08).align_to(line, RIGHT)
    tag.set_stroke(PLOT_BACKGROUND, width=5, background=True)
    return VGroup(line, tag)


def loading_points(axes, run, color, clock):
    """One run's points with their error bars, each shown once ``clock`` (lab
    time, ms) has reached it."""
    points = VGroup(*(
        VGroup(
            Line(axes.c2p(t, n - s), axes.c2p(t, n + s), color=color,
                 stroke_width=LOADING_ERROR_WIDTH),
            Dot(axes.c2p(t, n), radius=LOADING_DOT_RADIUS, color=color),
        )
        for t, n, s in zip(run["t_ms"], run["n"], run["sem"])
    ))
    times = run["t_ms"]

    def reveal(group):
        now = clock.get_value()
        for point, t in zip(group, times):
            point.set_opacity(1.0 if t <= now + 1e-9 else 0.0)

    points.add_updater(reveal)
    reveal(points)
    return points


def _path(axes, fit, t0, t1):
    ts = np.linspace(t0, t1, FIT_SAMPLES)
    return VMobject().set_points_as_corners(
        [axes.c2p(t, n) for t, n in zip(ts, loading_model(ts, fit))]
    )


def loading_fit(axes, fit, color, clock):
    """The fitted model, drawn out as far as ``clock``: solid over the points
    it was fitted to, dashed where it is carried on past them."""
    end = fit["fit_max_ms"]

    def solid():
        return _path(axes, fit, 0, max(min(clock.get_value(), end), 1e-3)).set_stroke(
            color, LOADING_FIT_WIDTH)

    def dashed():
        now = clock.get_value()
        if now <= end + 0.5:
            return VMobject()
        path = _path(axes, fit, end, now)
        pts = path.get_anchors()
        length = np.sum(np.linalg.norm(np.diff(pts, axis=0), axis=1))
        dashes = max(1, int(length / (2 * LOADING_EXTRAPOLATION_DASH)))
        return DashedVMobject(path.set_stroke(color, LOADING_FIT_WIDTH),
                              num_dashes=dashes)

    return VGroup(always_redraw(solid), always_redraw(dashed))


def loading_rate_line(axes, fit, color, top=1.2):
    """The initial slope, N0 + R (t - t0), from the onset up to ``top``: the
    loading rate the paper quotes, as a line on the plot."""
    t_top = fit["onset_ms"] + 1e3 * (top - fit["offset"]) / fit["rate"]
    return Line(axes.c2p(fit["onset_ms"], fit["offset"]), axes.c2p(t_top, top),
                color=lighten(color), stroke_width=LOADING_FIT_WIDTH)


def temperature_key(temperatures):
    """One swatch per oven temperature, in a row, headed "Oven"."""
    rows = VGroup(*(
        VGroup(Dot(radius=0.07, color=color),
               Tex(rf"{t}\,$^\circ$C", font_size=FONT_TICK, color=PLOT_FOREGROUND))
        .arrange(RIGHT, buff=0.1)
        for t, color in zip(temperatures, OVEN_TEMPERATURE_COLORS)
    )).arrange(RIGHT, buff=0.3)
    head = Tex(r"Oven", font_size=FONT_TICK, color=lighten(GUIDE_COLOR))
    return VGroup(head, rows).arrange(RIGHT, buff=0.3)
