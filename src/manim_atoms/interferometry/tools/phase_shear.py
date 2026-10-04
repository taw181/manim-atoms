"""Phase-shear readout: a tilted last pulse, and the fringes it writes on a cloud.

Sugarbaker et al., PRL 111, 113002 (2013). Tilt the last beamsplitter by a
small angle theta against the others and its wavevector picks up a component
k theta across the beam. The phase a pulse writes is k . r, so an atom at
transverse position x gets an extra k theta x: the interferometer phase is
sheared across the cloud,

    phi(x) = Phi + k theta x,

and an expanded cloud comes out of the ports striped, with fringes a period
Lambda = lambda / theta apart. Where the stripes sit is Phi, read off one
image -- sign included, and without knowing the contrast or the offset.

The helpers draw that: the beam with its wavefronts, which the scene rotates
about the cloud, and a camera image of a port whose pixels follow phi(x).
"""

from types import SimpleNamespace

import numpy as np
from manim import *

from manim_atoms.interferometry.style import *


def shear_phase(x, theta, phi, spacing):
    """phi(x) = Phi + k theta x, with the drawn wavefront ``spacing`` as the
    wavelength -- so on screen the fringe period is spacing / sin(theta),
    exactly how far apart the tilted wavefronts cross the cloud."""
    return phi + TAU * x * np.sin(theta) / spacing


def excited_fraction(phase, contrast=SHEAR_CONTRAST):
    """P_e = (1 - C cos phi) / 2, the excited port's share at phase phi."""
    return 0.5 * (1 - contrast * np.cos(phase))


def phase_reading(fn):
    """Something make_clock_hand can read a phase from: an object with a
    get_value(), here worked out afresh each frame by ``fn``."""
    return SimpleNamespace(get_value=fn)


def make_beam(center, width, below, above, spacing):
    """The last pulse as a beam rising to ``center``: a band ``width`` wide,
    from ``below`` under the centre to ``above`` over it, with a wavefront
    every ``spacing`` counted from the one through the centre, and a dashed
    axis. Built upright; rotate it about ``center`` to tilt it.

    Returns VGroup(band, wavefronts, axis). The band fades out above the
    centre, and the wavefronts with it, so the beam carries on up rather than
    ending on the atoms.
    """
    center = np.array(center, dtype=float)
    lower = Rectangle(width=width, height=below, stroke_width=0)
    lower.next_to(center, DOWN, buff=0).set_fill(LASER_COLOR, SHEAR_BEAM_OPACITY)
    upper = Rectangle(width=width, height=above, stroke_width=0)
    upper.next_to(center, UP, buff=0)
    upper.set_fill([LASER_COLOR, LASER_COLOR], opacity=[SHEAR_BEAM_OPACITY, 0])
    upper.set_sheen_direction(DOWN)
    band = VGroup(lower, upper)

    wavefronts = VGroup()
    for n in range(-int(below / spacing), int(above / spacing) + 1):
        y = n * spacing
        fade = 1.0 if y <= 0 else max(0.0, 1 - y / above)
        wavefronts.add(
            Line(center + [-width / 2, y, 0], center + [width / 2, y, 0],
                 **SHEAR_WAVEFRONT_STYLE)
            .set_stroke(opacity=SHEAR_WAVEFRONT_STYLE["stroke_opacity"] * fade)
        )
    axis = DashedLine(center + DOWN * below, center, **SHEAR_AXIS_STYLE)
    return VGroup(band, wavefronts, axis)


class PortImage(ImageMobject):
    """A camera image of one output port: a Gaussian cloud, lit in the port's
    colour by the share of the atoms that came out there.

    paint(share) redraws it from ``share(x)``, the port's share at each
    position across the cloud, with x running over ``x_range``. Like a
    VideoFrame, don't animate its opacity -- the animation would paint over
    the redraws.
    """

    def __init__(self, color, x_range, sigma_x, sigma_y=0.3, pixels=(72, 360), **kwargs):
        rows, cols = pixels
        self.x = np.linspace(*x_range, cols)
        y = np.linspace(-1, 1, rows)[:, None]
        self.density = np.exp(-self.x[None, :] ** 2 / (2 * sigma_x**2)
                              - y**2 / (2 * sigma_y**2))
        self.rgb = np.array(color_to_int_rgb(ManimColor(color)), dtype=float)
        super().__init__(self._pixels(np.zeros_like(self.x)), **kwargs)
        self.set_resampling_algorithm(RESAMPLING_ALGORITHMS["linear"])

    def _pixels(self, share):
        level = self.density * share[None, :]
        out = np.empty((*level.shape, 4), dtype=np.uint8)
        out[..., :3] = self.rgb
        out[..., 3] = np.clip(255 * level, 0, 255)
        return out

    def paint(self, share):
        self.pixel_array = self._pixels(share(self.x))
        self.orig_alpha_pixel_array = self.pixel_array[:, :, 3].copy()
        return self
