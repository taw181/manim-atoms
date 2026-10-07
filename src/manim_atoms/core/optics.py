"""Optics: beams drawn as Gaussian profiles, and an optical cavity.

- gaussian_band, gaussian_spot: a beam seen side on as nested bands,
  brightest along its axis, or end on as nested discs. The trapping
  figures' dipole traps, clock and push beams; a cavity's mode.
- make_cavity: two concave mirrors with the mode between them, a probe
  beam through it and a detector after it; rabi_transmission is what that
  detector sees with atoms coupled to the mode (the vacuum Rabi splitting).
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
