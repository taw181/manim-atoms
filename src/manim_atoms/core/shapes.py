"""Beams drawn as Gaussian profiles: a band seen side on, a spot seen end on.

Shared by the trapping figures (dipole traps, clock and push beams) and the
interferometry ones (a cavity mode).
"""

import numpy as np
from manim import *

from manim_atoms.style import *


def gaussian_band(start, end, width, color, opacity=TRAP_BEAM_OPACITY,
                  layers=TRAP_BEAM_LAYERS):
    """A beam seen side on: nested bands, brightest along its axis, so it
    reads as a Gaussian profile rather than a flat bar."""
    start, end = np.array(start, dtype=float), np.array(end, dtype=float)
    return VGroup(*[
        Rectangle(width=np.linalg.norm(end - start), height=width * (1 - k / layers),
                  stroke_width=0, fill_color=color, fill_opacity=opacity / layers)
        .rotate(angle_of_vector(end - start)).move_to((start + end) / 2)
        for k in range(layers)
    ])


def gaussian_spot(center, radius, color, opacity=TRAP_BEAM_OPACITY,
                  layers=TRAP_BEAM_LAYERS):
    """A beam seen end on, the same way: nested discs."""
    return VGroup(*[
        Circle(radius=radius * (1 - k / layers), stroke_width=0, fill_color=color,
               fill_opacity=opacity / layers).move_to(center)
        for k in range(layers)
    ])
