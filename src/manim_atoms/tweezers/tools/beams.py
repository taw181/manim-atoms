"""A tweezer seen from the side: a focused Gaussian beam through a tilted view.

hourglass_trap is the trap drawing a TweezerArray takes for the tilted
picture: the beam either side of its focus as a solid with a hard edge, cut
off square at both ends, over the spot in the focal plane. beam_half_width
is the Gaussian beam it draws; focal_plane is the outline of the plane the
foci lie in.
"""

import numpy as np
from manim import *

from manim_atoms.tweezers.style import *
from manim_atoms.tweezers.tools.tweezer_array import TW_SPOT_RADIUS

# --- the beam's geometry -----------------------------------------------------
# Not to scale: a real tweezer's waist is a tenth of the spacing, which
# drawn true would be needles. Here the waist is the top-down spot's radius,
# and the beam is cut off where it has flared to five thirds of that, so
# each trap reads as an hourglass and is still narrower than the gap to its
# neighbour. The cut is hard: a beam that fades out has no edge to tell it
# from the one behind.
TW_RAYLEIGH = 0.45  # distance from the focus at which the beam is sqrt(2) wider
TW_REACH = 0.6  # how far either side of the focus the beam is drawn
TW_OUTLINE_POINTS = 21  # along each side of the beam, end to end
TW_CAP_POINTS = 15  # round each end's half ellipse
# Looking straight down, a beam is seen end on and is its spot alone; the
# body comes up as the view tilts, and is all there once a step along the
# axis is drawn this long (an elevation of 60 degrees).
TW_EMERGED_RISE = 0.5
# The tilted view: low, so the beams stand well up out of the plane, and
# turned, so each row shows between the beams of the row in front.
TW_ELEVATION = 25 * DEGREES
TW_AZIMUTH = 18 * DEGREES


def beam_half_width(z, waist=TW_SPOT_RADIUS, rayleigh=TW_RAYLEIGH):
    """A Gaussian beam's 1/e^2 radius a distance z from its focus:
    w0 sqrt(1 + (z / z_R)^2)."""
    return waist * np.sqrt(1 + (np.asarray(z, dtype=float) / rayleigh) ** 2)


def hourglass_trap(view, at, power, waist=TW_SPOT_RADIUS, rayleigh=TW_RAYLEIGH,
                   reach=TW_REACH):
    """One trap seen through a tilted view: the beam from ``reach`` below the
    focal plane to ``reach`` above it, as a solid with a hard edge, and the
    spot in the plane, at world point ``at`` and as bright as ``power``.

    The solid is its silhouette (the two sides, the far half of the upper end
    and the near half of the lower), backed in the background's colour so it
    hides what is behind it, and the upper end's face. Looking straight down
    it is left out and what remains is the spot, a disc of the waist: the
    body comes up as the view tilts, so there is no jump between the two.
    """
    c, s = view.point(at), view.scale
    rise, squash = view.rise() * s, view.squash()
    parts = VGroup()
    if view.rise() > 1e-3:
        emerged = power * min(1.0, view.rise() / TW_EMERGED_RISE)
        zs = np.linspace(-reach, reach, TW_OUTLINE_POINTS)
        widths = beam_half_width(zs, waist, rayleigh) * s
        end = widths[-1]  # the beam's radius where it is cut off
        turn = np.linspace(0, PI, TW_CAP_POINTS + 2)[1:-1]
        arc = [np.array([end * np.cos(t), end * squash * np.sin(t), 0.0]) for t in turn]
        top, bottom = c + UP * reach * rise, c + DOWN * reach * rise
        corners = [*[c + np.array([w, z * rise, 0.0]) for w, z in zip(widths, zs)],
                   *[top + p for p in arc],
                   *[c + np.array([-w, z * rise, 0.0]) for w, z in zip(widths[::-1], zs[::-1])],
                   *[bottom - p for p in arc]]
        corners.append(corners[0])
        solid = dict(fill_color=TWEEZER_COLOR, fill_opacity=TWEEZER_SOLID_OPACITY * emerged,
                     stroke_color=TWEEZER_COLOR, stroke_width=TWEEZER_EDGE_STYLE["stroke_width"],
                     stroke_opacity=TWEEZER_EDGE_STYLE["stroke_opacity"] * emerged)
        parts.add(VMobject(stroke_width=0, fill_color=TWEEZER_BACKING_COLOR,
                           fill_opacity=emerged).set_points_as_corners(corners),
                  VMobject(**solid).set_points_as_corners(corners),
                  Ellipse(width=2 * end, height=2 * end * squash, **solid).move_to(top))
    parts.add(view.disc(at, waist, stroke_width=0, fill_color=TWEEZER_COLOR,
                        fill_opacity=TWEEZER_OPACITY * power))
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
