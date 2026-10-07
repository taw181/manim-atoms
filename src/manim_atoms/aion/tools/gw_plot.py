"""Log-log characteristic-strain plots in manim.

The pieces MergerOnSensitivityPlot and the sensitivity build-up share, on
core.plots' log-log axes: those axes labelled for strain against
frequency, and a detector's curve with its region shaded above it.
"""

from manim import *

from manim_atoms.aion.physics.gw_signals import load_sensitivity
from manim_atoms.aion.style import *
from manim_atoms.core.plots import curve_points, log_axes, plot_point


def sensitivity_axes(log_f_range, log_h_range, origin, width, height,
                     x_label="Frequency / Hz", y_label="Characteristic strain", **kwargs):
    """log_axes labelled for characteristic strain against frequency."""
    return log_axes(log_f_range, log_h_range, origin, width, height,
                    x_label=x_label, y_label=y_label, **kwargs)


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
