"""Spin squeezing by a non-demolition measurement in an optical cavity.

N atoms each in the same superposition of |g> and |e> add up to one
collective spin, J = sum of the atoms' spin-1/2s, with its tip on the Bloch
sphere's equator. Each atom still projects on its own at readout, so the tip
is blurred by a disc of quantum noise, Delta J_z = sqrt(N)/2 wide: the
coherent spin state, whose phase resolution 1/sqrt(N) is the standard quantum
limit.

Put the atoms in an optical cavity and probe it far off the 689 nm line: the
atoms in |g> pull the cavity's resonance by an amount proportional to how many
there are, and the light scatters almost nothing, so it counts N_g -- which,
with N known, is J_z = (N_e - N_g)/2 -- without flipping an atom or spoiling
the superposition. That is a quantum non-demolition measurement. Once J_z is
known better than sqrt(N)/2, the disc is squeezed along J_z and stretched
along the phase; a rotation about the mean spin turns the narrow direction
onto the phase, and the interferometer resolves it to xi / sqrt(N), xi < 1.

The helpers draw the pieces: the Bloch sphere, a noise blob on its tangent
plane, the cavity with its probe, and the transmission line shape it reads.
"""

import numpy as np
from manim import *

from aionanim.style import *
from aionanim.tools.dipole import gaussian_band
from aionanim.tools.primitives import make_cloud, state_label


def lorentzian(x, center, width):
    """The cavity's transmission at probe frequency x: peak 1 at ``center``,
    half-width ``width``."""
    return 1 / (1 + ((x - center) / width) ** 2)


def noise_blob(radius, color=COHERENT_COLOR):
    """The collective spin's quantum noise seen head-on: a translucent disc,
    ``radius`` across. Stretch it to squeeze it."""
    return Circle(
        radius=radius,
        fill_color=color,
        fill_opacity=NOISE_BLOB_OPACITY,
        stroke_color=lighten(color),
        stroke_width=NOISE_BLOB_STROKE_WIDTH,
    )


def make_bloch(center, radius, tip_angle, tilt=0.28):
    """A Bloch sphere, |e> at the top and |g> at the bottom, with the mean
    spin on the equator ``tip_angle`` round from the front, towards the right.

    ``tilt`` is how far open the equator is drawn (its height over its width).
    Returns (sphere, arrow, tip): the sphere with its equator and pole labels,
    the mean-spin arrow, and the point the arrow ends at.
    """
    center = np.array(center, dtype=float)
    circle = Circle(radius=radius, **BLOCH_STYLE).move_to(center)
    equator = Ellipse(width=2 * radius, height=2 * radius * tilt, **BLOCH_STYLE)
    equator.move_to(center).set_stroke(opacity=0.6)
    poles = VGroup(
        state_label(r"|e\rangle", KICKED_COLOR, FONT_LEGEND).next_to(circle, UP, buff=0.08),
        state_label(r"|g\rangle", ATOM_COLOR, FONT_LEGEND).next_to(circle, DOWN, buff=0.08),
    )
    tip = center + radius * np.array([np.sin(tip_angle), -tilt * np.cos(tip_angle), 0])
    arrow = Arrow(center, tip, buff=0, stroke_width=3, color=WHITE,
                  max_tip_length_to_length_ratio=0.25)
    return VGroup(circle, equator, poles), arrow, tip


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


def cavity_atoms(center, radius, n=40, seed=4):
    """The atoms in the cavity mode, each in the same superposition of |g>
    and |e>, so drawn halfway between the two states' colours."""
    color = interpolate_color(ATOM_COLOR, KICKED_COLOR, 0.5)
    return make_cloud(center, color, n=n, radius=radius, seed=seed)
