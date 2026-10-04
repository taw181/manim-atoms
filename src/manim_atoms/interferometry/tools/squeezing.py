"""Spin squeezing by a non-demolition measurement in an optical cavity.

N atoms each in the same superposition of |g> and |e> add up to one
collective spin, J = sum of the atoms' spin-1/2s, with its tip on the Bloch
sphere's equator. Each atom still projects on its own at readout, so the tip
is blurred by a disc of quantum noise, Delta J_z = sqrt(N)/2 wide: the
coherent spin state, whose phase resolution 1/sqrt(N) is the standard quantum
limit.

Put the atoms in an optical cavity tuned to the 689 nm line, which only |g>
drives (Chen et al., PRL 106, 133601 (2011), did this on Rb's D2 line). The
atoms in |g> share one excitation with the cavity mode, and that collective
coupling splits the cavity's line into two normal modes 2 g sqrt(N_g) apart:
the vacuum Rabi splitting. Measuring the splitting counts N_g -- which, with
N known, is J_z = (N_e - N_g)/2 -- and a probe on the split modes sits
g sqrt(N_g) off the atoms, so it scatters little and flips no atom: a
quantum non-demolition measurement. Once J_z is
known better than sqrt(N)/2, the disc is squeezed along J_z and stretched
along the phase; a rotation about the mean spin turns the narrow direction
onto the phase, and the interferometer resolves it to xi / sqrt(N), xi < 1.

The helpers draw the pieces: the Bloch sphere in perspective, with the noise
as a patch on its surface, the cavity with its probe, and the transmission
line shape it reads.
"""

import numpy as np
from manim import *

from manim_atoms.style import *
from manim_atoms.core.shapes import gaussian_band
from manim_atoms.core.primitives import make_cloud


def rabi_transmission(x, center, kappa, gamma, coupling):
    """The cavity's transmission at probe frequency x, with the cavity and the
    atoms both resonant at ``center``: |kappa / (kappa - i D + G^2/(gamma - i D))|^2
    at detuning D, for cavity and atomic half-widths kappa and gamma and
    collective coupling G = g sqrt(N_g). One peak of height 1 for an empty
    cavity (G = 0); two, near center +- G, once G outgrows the widths."""
    d = np.asarray(x) - center
    t = kappa / (kappa - 1j * d + coupling**2 / (gamma - 1j * d))
    return np.abs(t) ** 2


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
