"""A plane seen from an angle, drawn on a flat scene.

TiltedView is an orthographic view of a world whose x-y plane is the plane
of interest (an array of traps, a sample, a chip) and whose z is the axis
out of it. Looking straight down (an elevation of 90 degrees) it is the
plane itself; lowered, the plane is squashed and things along z stand up.
The angles can be ValueTrackers, so the view can tilt and turn in a scene.
"""

import numpy as np
from manim import *

from manim_atoms.style import *


def _read(value):
    """A number, or what a ValueTracker holds."""
    return value.get_value() if hasattr(value, "get_value") else value


class TiltedView:
    """An orthographic view of the x-y plane from ``elevation`` above it,
    turned by ``azimuth`` about z, with the world's origin at ``center`` on
    screen and one world unit drawn ``scale`` long.

    ``elevation`` and ``azimuth`` are numbers or ValueTrackers, read afresh
    on every call. An elevation of PI / 2 looks straight down.
    """

    def __init__(self, center, scale=1.0, elevation=PI / 2, azimuth=0.0):
        self.center = np.array(center, dtype=float)
        self.scale = scale
        self.elevation, self.azimuth = elevation, azimuth

    def _turned(self, v):
        """(x, y, z) with the azimuth applied: y now runs away from the viewer."""
        x, y, z = (*v, 0.0)[:3]
        az = _read(self.azimuth)
        return x * np.cos(az) - y * np.sin(az), x * np.sin(az) + y * np.cos(az), z

    def point(self, v):
        """Where the world point ``v`` (x, y and optionally z) lands on screen."""
        x, y, z = self._turned(v)
        return self.center + self.scale * np.array(
            [x, y * self.squash() + z * self.rise(), 0.0]
        )

    def depth(self, v):
        """How near the viewer ``v`` is: paint in order of increasing depth."""
        _, y, z = self._turned(v)
        el = _read(self.elevation)
        return -y * np.cos(el) + z * np.sin(el)

    def squash(self):
        """How much a length in the plane, running away from the viewer, is
        foreshortened: 1 looking straight down, 0 edge on."""
        return np.sin(_read(self.elevation))

    def rise(self):
        """How long a unit step along z is drawn, before ``scale``: 0 looking
        straight down, 1 edge on."""
        return np.cos(_read(self.elevation))

    def disc(self, at, radius, **style):
        """A circle of ``radius`` lying in the plane about ``at``: an ellipse."""
        size = 2 * radius * self.scale
        return Ellipse(width=size, height=size * self.squash(), **style).move_to(self.point(at))

    def outline(self, corners, **style):
        """The polygon through world points ``corners``."""
        return Polygon(*[self.point(c) for c in corners], **style)
