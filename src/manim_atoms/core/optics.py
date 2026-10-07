"""Optics: beams drawn as Gaussian profiles, a cavity, the parts of an
interferometer, and light drawn as a wave.

- gaussian_band, gaussian_spot: a beam seen side on as nested bands,
  brightest along its axis, or end on as nested discs. The trapping
  figures' dipole traps, clock and push beams; a cavity's mode.
- make_cavity: two concave mirrors with the mode between them, a probe
  beam through it and a detector after it; rabi_transmission is what that
  detector sees with atoms coupled to the mode (the vacuum Rabi splitting).
- make_mirror, make_beam_splitter, make_laser, make_photodetector: the
  parts of an optical interferometer seen from above, sized and placed by
  the caller (aion.tools.ligo builds LIGO's Michelson from them).
- light_wave, beam_glow: light as a sine riding a beam, its phase chained
  from beam to beam, and the faint band under it.
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


# --- optical components, seen from above ------------------------------------
# Centred where they are put, in the optics' colour; a scene sets their
# positions and sizes (LIGO's are in aion.tools.ligo).
def make_mirror(length, thickness, vertical=True):
    """A flat mirror seen edge on: a slab ``length`` long and ``thickness``
    thick, upright if ``vertical``, else lying flat. A test mass, or a fold
    mirror. Centred on the origin: move it into place."""
    w, h = (thickness, length) if vertical else (length, thickness)
    return Rectangle(
        width=w, height=h, stroke_width=2, stroke_color=OPTIC_COLOR,
        fill_color=OPTIC_COLOR, fill_opacity=0.85,
    )


def make_beam_splitter(center, length, thickness, angle=45 * DEGREES):
    """A half-silvered plate seen edge on, at ``center``, turned by ``angle``.
    At 45 degrees it splits light along x between x and y, and recombines
    what comes back."""
    return Rectangle(
        width=length, height=thickness, stroke_width=2,
        stroke_color=OPTIC_COLOR, fill_color=OPTIC_COLOR, fill_opacity=0.35,
    ).rotate(angle).move_to(center)


def make_laser(exit, label="laser"):
    """A laser: a box whose right edge, where the beam leaves, is at
    ``exit``, with ``label`` under it (None: no label)."""
    box = RoundedRectangle(
        width=LASER_BOX_WIDTH, height=LASER_BOX_HEIGHT, corner_radius=0.08,
        stroke_color=LASER_COLOR, stroke_width=3, fill_color=BLACK, fill_opacity=1,
    ).move_to(exit + LEFT * LASER_BOX_WIDTH / 2)
    if label is None:
        return VGroup(box)
    tag = Tex(label, font_size=FONT_LEGEND, color=LASER_COLOR).next_to(
        box, DOWN, buff=0.15
    )
    return VGroup(box, tag)


def make_photodetector(face, label="photodetector"):
    """A photodiode facing up, the top of its face at ``face``, with
    ``label`` to its right (None: no label)."""
    sensor = Rectangle(
        width=0.8, height=0.22, stroke_width=2, stroke_color=OPTIC_COLOR,
        fill_color=OPTIC_COLOR, fill_opacity=0.85,
    ).move_to(face + DOWN * 0.11)
    body = Rectangle(
        width=0.5, height=0.3, stroke_width=2, stroke_color=OPTIC_COLOR,
        fill_color=BLACK, fill_opacity=1,
    ).next_to(sensor, DOWN, buff=0)
    if label is None:
        return VGroup(sensor, body)
    tag = Tex(label, font_size=FONT_LEGEND, color=OPTIC_COLOR).next_to(
        sensor, RIGHT, buff=0.25
    )
    return VGroup(sensor, body, tag)


# --- light as a wave along a beam -------------------------------------------
def light_wave(start, end, amplitude, phase, k, frac=1.0,
               samples_per_unit=WAVE_SAMPLES_PER_UNIT):
    """A sine of wavenumber ``k`` riding the segment start -> end, drawn out
    to ``frac`` of its length.

    The phase at the start is ``phase``, so a caller chains beams by handing
    on the phase the previous one ended with: the next beam starts at
    ``phase + k * length``. The caller sets its stroke.
    """
    d = end - start
    length = np.linalg.norm(d)
    u = d / length
    normal = np.array([-u[1], u[0], 0.0])
    reach = max(length * frac, 1e-3)
    s = np.linspace(0, reach, max(2, int(samples_per_unit * reach)))
    offset = amplitude * np.sin(k * s + phase)
    return VMobject().set_points_as_corners(
        start + np.outer(s, u) + np.outer(offset, normal)
    )


def beam_glow(start, end, frac=1.0, opacity=1.0):
    """The faint band a beam's wave rides on, drawn out to ``frac`` of the
    way from start to end, at ``opacity`` of its usual strength."""
    reach = start + (end - start) * max(frac, 1e-3)
    return Line(
        start, reach, color=LASER_COLOR, stroke_width=BEAM_GLOW_WIDTH,
        stroke_opacity=BEAM_GLOW_OPACITY * opacity,
    )
