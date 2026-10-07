"""Surfaces in 3D: a wireframe sheet whose height is any field z(x, y),
coloured by height, and the camera fixes a sheet needs.

- make_sheet: the flat wireframe, each line's sampling stashed on it;
  refresh_sheet re-evaluates every line at a height function and recolours
  it; height_ramp is the trough-flat-crest colour lookup it colours by.
- SheetLine, BEHIND_EVERYTHING: how the sheet sorts behind everything on it.
- SideCamera: a ThreeDCamera whose frame-fixed overlay ignores frame_center.
- smooth_step: the cubic smoothstep, for tapers and blends across a field.

A wireframe rather than a Surface: a Surface rebuilds thousands of little
quads every frame, while 2 * lines polylines are just point arrays. A
merger's rippling spacetime is one (aion.scenes.gravitational_waves); a
trap's potential or a lattice would be another.
"""

import numpy as np
from manim import *

from manim_atoms.style import *


def height_ramp(trough, flat, crest, scale, steps=33):
    """A colour for each height: ``flat`` at zero, running to ``crest`` at
    ``+scale`` and to ``trough`` at ``-scale``, saturating beyond. Returns a
    function from an array of heights to a list of colours, looked up from
    ``steps`` precomputed stops."""
    lut = [
        interpolate_color(trough, flat, 1.0 + u)
        if u < 0
        else interpolate_color(flat, crest, u)
        for u in np.linspace(-1.0, 1.0, steps)
    ]

    def colors(z):
        """Map an array of heights onto the ramp."""
        idx = (z / scale + 1.0) * 0.5 * (len(lut) - 1)
        return [lut[i] for i in np.clip(idx, 0, len(lut) - 1).astype(int)]

    return colors


def smooth_step(x):
    """The cubic smoothstep, 0 below 0 and 1 above 1, with zero slope at both ends."""
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


# A stand-in reference point far below a sheet. Anything whose z_index_group
# is set to it sorts to the back: its depth is -1000 * cos(phi), which beats
# anything in a scene for any camera above the horizon. Used by the grid
# lines (see SheetLine).
BEHIND_EVERYTHING = VectorizedPoint([0.0, 0.0, -1000.0])


class SheetLine(VMobject):
    """A grid line that sits at the back of the camera's depth sort.

    shade_in_3d is what puts a mobject into ThreeDCamera's depth sort at all;
    anything without it scores np.inf, and np.inf sorts last, so an unshaded
    sheet is painted over whatever sits on it (the merger's black holes,
    which are shaded). But sorting the sheet honestly is no good
    either: each line spans the whole sheet, and the sort has only one depth
    per mobject to work with, so a line whose midpoint is near the camera gets
    drawn over the holes along its entire length. The wireframe ends up
    splattered across them.

    So the flag goes on and z_index_group sends every line to a point far
    behind the scene. All the lines then share one key, which leaves their
    order among themselves exactly as built, and the whole sheet lands behind
    everything on it -- while those, compact enough for one depth each to be
    meaningful, sort properly against each other.

    It also needs the camera's lighting pass off
    (``camera.should_apply_shading = False``): that pass keeps only the first
    two stroke colours of what it touches, cutting each line's height
    gradient to two stops. The depth sort never consults it.

    Setting the flag has one side effect to undo: it reroutes the stroke
    gradient through get_3d_vmob_gradient_start_and_end_points, whose
    end-corner index ((n - 1) // 6) * 3 assumes a four-corner Surface face. On
    a polyline of a hundred-odd anchors that lands near the middle, squashing
    the height colours into the first half of every line.
    """

    def __init__(self, **kwargs):
        super().__init__(shade_in_3d=True, **kwargs)
        self.z_index_group = BEHIND_EVERYTHING

    def get_gradient_start_and_end_points(self):
        """The line's own ends, not a Surface face's corners."""
        return self.points[0], self.points[-1]


def make_sheet(half, lines, samples, stops, color, stroke_width):
    """The wireframe sheet, flat, spanning [-half, half] in x and y: ``lines``
    grid lines each way, each sampled at ``samples`` points and coloured
    through ``stops`` gradient stops (a gradient needs far fewer than the
    points). Each line's sampling is stashed on it for refresh_sheet."""
    grid = VGroup()
    coords = np.linspace(-half, half, lines)
    xs_line = np.linspace(-half, half, samples)
    stop_index = np.linspace(0, samples - 1, stops).astype(int)
    fixed = np.full_like(xs_line, 0.0)

    for c in coords:
        for xs, ys in ((xs_line, fixed + c), (fixed + c, xs_line)):
            line = SheetLine(stroke_width=stroke_width)
            line.set_points_as_corners(np.stack([xs, ys, np.zeros_like(xs)], axis=1))
            line.set_stroke(color, stroke_width)
            line.xs, line.ys, line.stops = xs, ys, stop_index
            grid.add(line)
    return grid


def refresh_sheet(grid, height, colors):
    """Re-evaluate every grid line at ``height(xs, ys)`` and recolour it by
    height through ``colors`` (a height_ramp)."""
    for line in grid:
        z = height(line.xs, line.ys)
        line.set_points_as_corners(np.stack([line.xs, line.ys, z], axis=1))
        line.set_stroke(color=colors(z[line.stops]))


class SideCamera(ThreeDCamera):
    """A ThreeDCamera whose frame-fixed mobjects ignore frame_center.

    The pixel mapping subtracts frame_center from everything, fixed or not, so
    an off-centre frame_center drags the overlay along with the sheet. This
    puts it back at the last step, which keeps working for mobjects whose
    updaters rebuild their points from absolute positions every frame.
    """

    def transform_points_pre_display(self, mobject, points):
        points = super().transform_points_pre_display(mobject, points)
        if mobject in self.fixed_in_frame_mobjects:
            return points + self.frame_center * [1, 1, 0]
        return points
