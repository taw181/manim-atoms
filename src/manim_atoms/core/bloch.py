"""The Bloch sphere: a two-level state, or a collective spin, as a direction.

BlochView draws the sphere in perspective on a flat scene, |e> up: any
direction on it (point), the circle at a given height about any axis
(ring), a patch round a direction (patch), and curves through them that
come out solid in front and dashed and faint behind (curve).
noise_patch fills a patch as a spin's quantum noise -- the disc of a
coherent spin state, or the ellipse of a squeezed one.
"""

import numpy as np
from manim import *

from manim_atoms.style import *


class BlochView:
    """A Bloch sphere drawn in perspective on a flat scene: |e> up, the viewer
    a little above the equator, looking down by ``elevation``.

    World coordinates have x towards the viewer, y to the right and z up
    (towards |e>); every point is a direction on the unit sphere, scaled to
    ``radius`` on screen. Curves on the sphere come out split into the part
    in front, drawn solid, and the part behind it, dashed and faint.
    """

    def __init__(self, center, radius, elevation=15 * DEGREES):
        self.center = np.array(center, dtype=float)
        self.radius = radius
        self.cos_el, self.sin_el = np.cos(elevation), np.sin(elevation)

    def point(self, v):
        """Where the direction ``v`` lands on screen."""
        x, y, z = v
        return self.center + self.radius * np.array(
            [y, z * self.cos_el - x * self.sin_el, 0.0]
        )

    def depth(self, v):
        """> 0 for a point on the side of the sphere facing the viewer."""
        return v[0] * self.cos_el + v[2] * self.sin_el

    def curve(self, points, color, width, back_opacity=0.35):
        """A curve through directions on the sphere: solid in front, dashed
        and faint behind."""
        front, back = VGroup(), VGroup()
        run, facing = [], None
        for v in points:
            f = self.depth(v) >= 0
            if facing is not None and f != facing:
                (front if facing else back).add(self._path(run + [v]))
                run = []
            run.append(v)
            facing = f
        (front if facing else back).add(self._path(run))
        front.set_stroke(color, width)
        back = VGroup(*[
            DashedVMobject(m, num_dashes=max(2, int(m.get_arc_length() / 0.12)))
            for m in back
        ])
        back.set_stroke(color, width * 0.8, opacity=back_opacity)
        return VGroup(back, front)

    def _path(self, dirs):
        return VMobject().set_points_as_corners([self.point(v) for v in dirs])

    def ring(self, axis, height=0.0, n=160):
        """The circle of directions v with v . axis = height."""
        axis = np.asarray(axis, dtype=float)
        u = np.cross(axis, [0, 0, 1] if abs(axis[2]) < 0.9 else [1, 0, 0])
        u /= np.linalg.norm(u)
        w = np.cross(axis, u)
        r = np.sqrt(max(0.0, 1 - height**2))
        return [height * axis + r * (np.cos(s) * u + np.sin(s) * w)
                for s in np.linspace(0, TAU, n)]

    def outline(self):
        return Circle(radius=self.radius, **BLOCH_STYLE).move_to(self.center)

    def patch(self, center, e1, e2, a, b, n=90):
        """The outline of a patch of the sphere round the direction ``center``:
        an ellipse of angular half-widths ``a`` along the tangent ``e1`` and
        ``b`` along ``e2``, wrapped onto the surface."""
        return [
            normalize(center + np.tan(a) * np.cos(t) * e1 + np.tan(b) * np.sin(t) * e2)
            for t in np.linspace(0, TAU, n)
        ]


def noise_patch(view, center, e1, e2, a, b, color):
    """The collective spin's quantum noise, a filled patch on the sphere."""
    return Polygon(
        *[view.point(v) for v in view.patch(center, e1, e2, a, b)],
        fill_color=color,
        fill_opacity=NOISE_BLOB_OPACITY,
        stroke_color=lighten(color),
        stroke_width=NOISE_BLOB_STROKE_WIDTH,
    )
