"""Optics: beams drawn as Gaussian profiles, an optical cavity, and the
pictures and furniture of a hologram.

- gaussian_band, gaussian_spot: a beam seen side on as nested bands,
  brightest along its axis, or end on as nested discs. The trapping
  figures' dipole traps, clock and push beams; a cavity's mode.
- make_cavity: two concave mirrors with the mode between them, a probe
  beam through it and a detector after it; rabi_transmission is what that
  detector sees with atoms coupled to the mode (the vacuum Rabi splitting).
- PhaseMask: a phase map as a picture, coloured round a wheel that wraps
  (phase_rgb), with phase_wheel as its key; FocalImage: an intensity map as
  a camera would show it. Both repaint from an array.
- make_lens, make_slm: a lens and a spatial light modulator, edge on.
"""

import numpy as np
from manim import *

from manim_atoms.style import *


def gaussian_band(start, end, width, color, opacity=BEAM_OPACITY,
                  layers=BEAM_LAYERS):
    """A beam seen side on: nested bands, brightest along its axis, so it
    reads as a Gaussian profile rather than a flat bar."""
    start, end = np.array(start, dtype=float), np.array(end, dtype=float)
    return VGroup(*[
        Rectangle(width=np.linalg.norm(end - start), height=width * (1 - k / layers),
                  stroke_width=0, fill_color=color, fill_opacity=opacity / layers)
        .rotate(angle_of_vector(end - start)).move_to((start + end) / 2)
        for k in range(layers)
    ])


def gaussian_spot(center, radius, color, opacity=BEAM_OPACITY,
                  layers=BEAM_LAYERS):
    """A beam seen end on, the same way: nested discs."""
    return VGroup(*[
        Circle(radius=radius * (1 - k / layers), stroke_width=0, fill_color=color,
               fill_opacity=opacity / layers).move_to(center)
        for k in range(layers)
    ])


def rabi_transmission(x, center, kappa, gamma, coupling):
    """The cavity's transmission at probe frequency x, with the cavity and the
    atoms both resonant at ``center``: |kappa / (kappa - i D + G^2/(gamma - i D))|^2
    at detuning D, for cavity and atomic half-widths kappa and gamma and
    collective coupling G = g sqrt(N_g). One peak of height 1 for an empty
    cavity (G = 0); two, near center +- G, once G outgrows the widths."""
    d = np.asarray(x) - center
    t = kappa / (kappa - 1j * d + coupling**2 / (gamma - 1j * d))
    return np.abs(t) ** 2


def make_cavity(center, length, mirror_height, mode_width, lead_in, lead_out):
    """Two concave mirrors ``length`` apart about ``center``, the cavity mode
    between them, and the probe beam coming in ``lead_in`` from the left and
    going on ``lead_out`` to the right into a detector.

    Returns VGroup(mirrors, mode, probe, detector).
    """
    center = np.array(center, dtype=float)
    left, right = center + LEFT * length / 2, center + RIGHT * length / 2
    # A shallow arc for each mirror, curving in towards the atoms: its ends
    # lean towards the middle of the cavity.
    sag = 0.18

    def mirror(at, facing):
        top, bottom = at + UP * mirror_height / 2, at + DOWN * mirror_height / 2
        return VMobject().set_points_smoothly([top, at - facing * sag, bottom]).set_stroke(
            OPTIC_COLOR, MIRROR_STROKE_WIDTH
        )

    mirrors = VGroup(mirror(left, RIGHT), mirror(right, LEFT))
    mode = gaussian_band(left, right, mode_width, PROBE_COLOR, CAVITY_MODE_OPACITY)
    probe_in = Arrow(left + LEFT * lead_in, left + LEFT * 0.25, buff=0,
                     stroke_width=PROBE_STROKE_WIDTH, color=PROBE_COLOR,
                     max_tip_length_to_length_ratio=0.18)
    end = right + RIGHT * lead_out
    probe_out = Arrow(right + RIGHT * 0.05, end, buff=0,
                      stroke_width=PROBE_STROKE_WIDTH, color=PROBE_COLOR,
                      max_tip_length_to_length_ratio=0.18)
    detector = Rectangle(width=0.22, height=0.55, stroke_width=0, fill_color=OPTIC_COLOR,
                         fill_opacity=1).next_to(end, RIGHT, buff=0.02)
    return VGroup(mirrors, mode, VGroup(probe_in, probe_out), detector)


def _phase_lut(size=256):
    """PHASE_COLORS as ``size`` evenly spaced RGB rows, once round the wheel."""
    lut = np.empty((size, 3), dtype=np.uint8)
    for i in range(size):
        t = i / size * (len(PHASE_COLORS) - 1)
        k = int(t)
        lut[i] = color_to_int_rgb(interpolate_color(PHASE_COLORS[k], PHASE_COLORS[k + 1], t - k))
    return lut


_PHASE_LUT = _phase_lut()


def phase_rgb(phase):
    """The phase wheel's colour at each phase, as uint8 RGB: any phase, since
    only its value mod 2 pi counts."""
    share = np.mod(np.asarray(phase, dtype=float), TAU) / TAU
    return _PHASE_LUT[np.minimum((share * len(_PHASE_LUT)).astype(int), len(_PHASE_LUT) - 1)]


class PhaseMask(ImageMobject):
    """A phase map as a picture, coloured round the phase wheel.

    ``phase`` is a 2D array in radians. ``aperture``, if given, is an array of
    the same shape, 0 to 1: how opaque each pixel is, so the picture can be
    clipped to a round pupil. The wheel has no step in it, so the picture is
    smoothed between pixels without a seam where the phase wraps.
    paint(phase) redraws it. Like a VideoFrame,
    don't animate its opacity -- the animation would paint over the redraws.
    """

    def __init__(self, phase, aperture=None, **kwargs):
        self.aperture = None if aperture is None else np.asarray(aperture, dtype=float)
        super().__init__(self._pixels(phase), **kwargs)
        self.set_resampling_algorithm(RESAMPLING_ALGORITHMS["linear"])

    def _pixels(self, phase):
        phase = np.asarray(phase, dtype=float)
        out = np.empty((*phase.shape, 4), dtype=np.uint8)
        out[..., :3] = phase_rgb(phase)
        out[..., 3] = 255 if self.aperture is None else np.clip(255 * self.aperture, 0, 255)
        return out

    def paint(self, phase):
        """Redraw from a new phase array of the same shape."""
        self.pixel_array = self._pixels(phase)
        self.orig_alpha_pixel_array = self.pixel_array[:, :, 3].copy()
        return self


def phase_wheel(radius, pixels=160):
    """The key to a PhaseMask: a ring coloured by angle, 0 at the right and
    rising anticlockwise."""
    c = (np.arange(pixels) + 0.5) / pixels * 2 - 1
    x, y = np.meshgrid(c, -c)
    rho = np.hypot(x, y)
    ring = ((rho <= 1) & (rho >= 0.6)).astype(float)
    return PhaseMask(np.arctan2(y, x), ring).set(height=2 * radius)


class FocalImage(ImageMobject):
    """An intensity map as a picture: one colour, as opaque as the light is
    bright, the way a camera in the focal plane would show it.

    paint(intensity) redraws it from a 2D array; ``full`` is the intensity
    drawn fully opaque, and ``gamma`` below 1 lifts the faint parts (a ghost
    spot, an aberrated spot's skirt) into view. Don't animate its opacity.
    """

    def __init__(self, intensity, color, full=1.0, gamma=1.0, **kwargs):
        self.rgb = np.array(color_to_int_rgb(ManimColor(color)), dtype=np.uint8)
        self.full, self.gamma = full, gamma
        super().__init__(self._pixels(intensity), **kwargs)
        self.set_resampling_algorithm(RESAMPLING_ALGORITHMS["linear"])

    def _pixels(self, intensity):
        level = np.clip(np.asarray(intensity, dtype=float) / self.full, 0, 1) ** self.gamma
        out = np.empty((*level.shape, 4), dtype=np.uint8)
        out[..., :3] = self.rgb
        out[..., 3] = 255 * level
        return out

    def paint(self, intensity):
        """Redraw from a new intensity array of the same shape."""
        self.pixel_array = self._pixels(intensity)
        self.orig_alpha_pixel_array = self.pixel_array[:, :, 3].copy()
        return self


def make_lens(center, height, bulge=40 * DEGREES):
    """A thin lens seen edge on, its axis horizontal: two arcs meeting at the
    rim, ``height`` tall. ``bulge`` is the angle each arc turns through."""
    center = np.array(center, dtype=float)
    top, bottom = center + UP * height / 2, center + DOWN * height / 2
    lens = ArcBetweenPoints(top, bottom, angle=bulge)
    lens.append_points(ArcBetweenPoints(bottom, top, angle=bulge).points)
    return lens.set_style(**LENS_STYLE)


def make_slm(center, height, depth=0.16):
    """A spatial light modulator seen edge on, facing right: the panel the
    light meets, drawn heavy, on the body behind it. Rotate it about its
    centre to turn it."""
    center = np.array(center, dtype=float)
    body = Rectangle(width=depth, height=height, **SLM_STYLE).move_to(center + LEFT * depth / 2)
    panel = Line(center + UP * height / 2, center + DOWN * height / 2,
                 stroke_width=MIRROR_STROKE_WIDTH, color=OPTIC_COLOR)
    return VGroup(body, panel)
