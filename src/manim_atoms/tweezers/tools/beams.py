"""A tweezer seen from the side: a focused Gaussian beam through a tilted view.

hourglass_trap is the trap drawing a TweezerArray takes for the tilted
picture: the beam's silhouette either side of the focus, fading as the
light spreads, over the spot in the focal plane. beam_half_width and
axial_intensity are the Gaussian beam it draws; focal_plane is the outline
of the plane the foci lie in.
"""

import numpy as np
from manim import *

from manim_atoms.tweezers.style import *
from manim_atoms.tweezers.tools.tweezer_array import TW_SPOT_RADIUS

# --- the beam's geometry -----------------------------------------------------
# Not to scale: a real tweezer's waist is a tenth of the spacing, which
# drawn true would be needles. Here the waist is the top-down spot's radius,
# and the beam flares to three times that within the length drawn, so each
# trap reads as an hourglass; it has faded almost to nothing by the height
# at which it would meet its neighbour.
TW_RAYLEIGH = 0.4  # distance from the focus at which the beam is sqrt(2) wider
TW_REACH = 1.1  # how far either side of the focus the beam is drawn
TW_OUTLINE_POINTS = 10  # along each half's edge
TW_STOPS = 6  # opacity stops along each half
TW_ELEVATION = 40 * DEGREES  # the tilted view: the beams stand up, the rows stay apart
TW_AZIMUTH = 18 * DEGREES  # turned, so the rows do not hide one another


def beam_half_width(z, waist=TW_SPOT_RADIUS, rayleigh=TW_RAYLEIGH):
    """A Gaussian beam's 1/e^2 radius a distance z from its focus:
    w0 sqrt(1 + (z / z_R)^2)."""
    return waist * np.sqrt(1 + (np.asarray(z, dtype=float) / rayleigh) ** 2)


def axial_intensity(z, rayleigh=TW_RAYLEIGH, reach=TW_REACH):
    """How brightly the beam is drawn a distance z from its focus: the
    on-axis intensity 1 / (1 + (z / z_R)^2), brought to nothing at ``reach``
    so the beam fades out rather than ending."""
    z = np.asarray(z, dtype=float)
    return np.clip(1 - (z / reach) ** 2, 0, None) / (1 + (z / rayleigh) ** 2)


def hourglass_trap(view, at, power, waist=TW_SPOT_RADIUS, rayleigh=TW_RAYLEIGH,
                   reach=TW_REACH):
    """One trap seen through a tilted view: the half of the beam below the
    focal plane, the half above, and the spot in the plane, at world point
    ``at`` and as bright as ``power``.

    Looking straight down the halves have no height and are left out, and
    what remains is spot_trap's drawing: the view can tilt between the two
    without a jump.
    """
    c, s = view.point(at), view.scale
    rise = view.rise() * s
    peak = TWEEZER_OPACITY * power / TWEEZER_LAYERS
    parts = VGroup()
    if rise > 1e-3:
        zs = np.linspace(0, reach, TW_OUTLINE_POINTS)
        widths = beam_half_width(zs, waist, rayleigh) * s
        stops = [peak * axial_intensity(z, rayleigh, reach)
                 for z in np.linspace(0, reach, TW_STOPS)]
        for side in (-1, 1):
            for k in range(TWEEZER_LAYERS):
                share = 1 - k / TWEEZER_LAYERS
                edge = [np.array([w * share, side * z * rise, 0.0]) for w, z in zip(widths, zs)]
                corners = [c + p for p in edge] + [c + p * [-1, 1, 1] for p in edge[::-1]]
                half = VMobject(stroke_width=0).set_points_as_corners([*corners, corners[0]])
                half.set_fill([TWEEZER_COLOR] * TW_STOPS, opacity=stops)
                half.set_sheen_direction(side * UP)
                parts.add(half)
    for k in range(TWEEZER_LAYERS):
        parts.add(view.disc(at, waist * (1 - k / TWEEZER_LAYERS), stroke_width=0,
                            fill_color=TWEEZER_COLOR, fill_opacity=peak))
    return parts


def focal_plane(view, half_width, half_height, shown):
    """The outline of the focal plane, a rectangle about the view's origin,
    redrawn as the view moves and as visible as the tracker ``shown`` (0 to 1)."""
    corners = [[half_width, half_height], [-half_width, half_height],
               [-half_width, -half_height], [half_width, -half_height]]

    def draw():
        style = {**FOCAL_PLANE_STYLE,
                 "stroke_opacity": FOCAL_PLANE_STYLE["stroke_opacity"] * shown.get_value()}
        return view.outline(corners, **style)

    return always_redraw(draw)
