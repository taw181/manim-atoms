"""An atomic fountain: the trajectory, the tube it flies up, and the lattice
that launches it.

The fountain is drawn twice side by side, sharing one height axis: the
apparatus on the left (a MOT at the bottom of a vertical tube) and the
space-time diagram on the right, whose horizontal axis is lab time. A cloud in
the tube and the same cloud on the diagram are always at the same height, so
everything here is a function of lab time -- the diagram's x -- and a scene
drives both from one clock (core.spacetime).

The flight is ballistic. Released at T_REL with velocity FT_V0, the cloud
follows z(t) = z_rel + v0 (t - t_rel) - g (t - t_rel)^2 / 2; in the freely
falling frame, with the parabola -g (t - t_rel)^2 / 2 taken out, every leg is
straight, so the Mach-Zehnder arms are core.spacetime's displaced legs with
``fall`` as the displacement, exactly as in the gravimeter.

The pulses are placed symmetrically about the apex of the *mean* trajectory
(launch velocity plus half a recoil): the pi pulse finds the two arms either
side of their common apex, and the loop closes at the height it opened at.

Not to scale, of course: a recoil of millimetres per second against a launch
of metres per second would put the arms a hair apart, so the recoil is drawn
as a fair fraction of the launch.
"""

import numpy as np
from manim import *

from manim_atoms.aion.style import *


# --- the fountain, in diagram units ---------------------------------------
# Heights are frame y; times are frame x, from where the diagram starts.
FT_TUBE_X = -5.6  # the apparatus' axis
FT_Z_MOT = -2.4  # the MOT, and the height the cloud is launched from
FT_T_START = -3.6  # the diagram's left edge: the cloud still trapped
FT_T_LAUNCH = -3.0  # the lattice starts to accelerate
FT_LAUNCH_TIME = 0.35  # how long it accelerates for
FT_G = 0.7  # g: the parabola's curvature
FT_VR = 0.9  # the recoil hbar k / m
FT_T = 2.0  # the time between pulses
FT_RISE = 1.6  # release to the first pulse
FT_OUT = 0.9  # last pulse to the readout

# The launch velocity follows: the pi pulse at the mean trajectory's apex.
FT_V0 = FT_G * (FT_RISE + FT_T) - FT_VR / 2
FT_T_REL = FT_T_LAUNCH + FT_LAUNCH_TIME
FT_Z_REL = FT_Z_MOT + FT_V0 * FT_LAUNCH_TIME / 2  # uniform acceleration up to v0
FT_PULSE_T = tuple(FT_T_REL + FT_RISE + k * FT_T for k in range(3))
FT_T_READOUT = FT_PULSE_T[2] + FT_OUT


def fall(t):
    """The fall since release, as a core.spacetime leg displacement."""
    return -0.5 * FT_G * (t - FT_T_REL) ** 2


def unkicked(t, recoils=0):
    """Where an atom launched at v0 is at lab time t, with ``recoils`` extra
    hbar k / m of upward velocity carried since release (as a point)."""
    s = t - FT_T_REL
    return np.array([t, FT_Z_REL + (FT_V0 + recoils * FT_VR) * s + fall(t), 0.0])


def before_split(t):
    """The cloud's height from the trap to the first pulse: held, lifted at
    constant acceleration by the lattice, then in free flight."""
    if t <= FT_T_LAUNCH:
        return FT_Z_MOT
    if t <= FT_T_REL:
        return FT_Z_MOT + 0.5 * FT_V0 / FT_LAUNCH_TIME * (t - FT_T_LAUNCH) ** 2
    return unkicked(t)[1]


def mach_zehnder_corners():
    """A, B (lower arm at the pi pulse), B' (upper arm), C, and the two ports
    at the readout, |g, p> then |e, p + hbar k>, as lab points.

    Each arm's falling-frame velocity is v0 or v0 + hbar k / m, so the
    corners are the unkicked trajectory moved up by however many recoils'
    worth of height each one has gained since the first pulse.
    """
    t1, t2, t3 = FT_PULSE_T
    a = unkicked(t1)
    b = unkicked(t2)
    b_up = b + UP * FT_VR * FT_T
    c = unkicked(t3) + UP * FT_VR * FT_T
    port_g = unkicked(FT_T_READOUT) + UP * FT_VR * FT_T
    port_e = port_g + UP * FT_VR * FT_OUT
    return a, b, b_up, c, port_g, port_e


# --- the apparatus --------------------------------------------------------
FT_TUBE_HALF_WIDTH = 0.5
FT_TUBE_SPAN = (FT_Z_MOT + 1.35, 3.5)  # from just above the upper coil
FT_MOT_REACH = 1.3  # how far the MOT beams run out from the cloud
FT_COIL_SCALE = 0.7  # of trapping.tools.cooling's coils, to fit under the tube
FT_LATTICE_SPAN = (FT_Z_MOT - 0.8, FT_Z_MOT + 1.6)
FT_LATTICE_WIDTH = 0.5
FT_LATTICE_PLANE_WIDTH = 0.36
FT_LATTICE_SPACING = 0.13
FT_CLOUD_EXPANSION = 0.015  # radius gained per unit of lab time in flight
FT_TIE_GAP = 0.45  # from the tube axis to the start of a tie line


def make_tube(x=FT_TUBE_X, span=FT_TUBE_SPAN):
    """The vacuum tube the fountain flies up: two walls."""
    return VGroup(*[
        Line([x + sign * FT_TUBE_HALF_WIDTH, span[0], 0],
             [x + sign * FT_TUBE_HALF_WIDTH, span[1], 0])
        for sign in (1, -1)
    ]).set_stroke(SHAFT_COLOR, FOUNTAIN_TUBE_WIDTH)


def make_lattice(offset, x=FT_TUBE_X, span=FT_LATTICE_SPAN):
    """A vertical optical lattice along the tube: a faint band, with its
    standing-wave planes shifted up by ``offset`` (a ValueTracker), which is
    how the cloud held in it is carried up. Planes leave the top of the band
    and come back in at the bottom."""
    band = Rectangle(width=FT_LATTICE_WIDTH, height=span[1] - span[0], stroke_width=0,
                     fill_color=TRAP_BEAM_COLOR, fill_opacity=LATTICE_BAND_OPACITY)
    band.move_to([x, (span[0] + span[1]) / 2, 0])
    height = span[1] - span[0]
    n = int(height / FT_LATTICE_SPACING)

    def planes():
        shift = offset.get_value() % FT_LATTICE_SPACING
        return VGroup(*[
            Line([x - FT_LATTICE_PLANE_WIDTH / 2, y, 0], [x + FT_LATTICE_PLANE_WIDTH / 2, y, 0],
                 **LATTICE_PLANE_STYLE)
            for y in span[0] + shift + FT_LATTICE_SPACING * np.arange(n)
            if y <= span[1]
        ])

    return VGroup(band, always_redraw(planes))


def follow(cloud, height, clock, x=FT_TUBE_X, radius0=None):
    """Pin a trapping.tools.cooling AtomCloud to ``height(t)`` in the tube,
    expanding as it flies: the thermal spread of a cold cloud in free flight.

    Put in front of the cloud's own updater, so the atoms are placed about
    this frame's centre rather than the last one's.
    """
    r0 = cloud.radius.get_value() if radius0 is None else radius0

    def place(m):
        t = clock.get_value()
        m.center = np.array([x, height(t), 0.0])
        m.radius.set_value(r0 + FT_CLOUD_EXPANSION * max(t - FT_T_LAUNCH, 0.0))

    cloud.add_updater(place, index=0)
    place(cloud)
    return cloud


def tie(atom, x=FT_TUBE_X):
    """A faint dashed line from the tube to ``atom`` on the diagram, at its
    height: the cloud there and the atom here are the same thing."""
    def draw():
        y = atom.get_center()[1]
        start = np.array([x + FT_TIE_GAP, y, 0])
        end = np.array([atom.get_left()[0] - 0.08, y, 0])
        if end[0] - start[0] < 0.2:
            return VGroup()
        return DashedLine(start, end, **FOUNTAIN_TIE_STYLE)

    return always_redraw(draw)
