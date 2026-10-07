"""The atom gradiometer: two clock interferometers on one baseline, one laser.

These are space-time diagrams, not plan views: the horizontal axis is time and
the vertical axis is distance along the baseline, which is also the direction the
lasers propagate and the direction of the photon recoil. An atom at rest is a
horizontal worldline; a photon is a steep diagonal.

Drawing the photons with a finite slope is the whole point of the gradiometer
scene -- the light reaches the far cloud later than the near one, so a single
laser writes its phase into the two interferometers at different retarded
times. That is what the single-photon clock scheme buys: the laser's own phase
noise is common to both and cancels in the difference.

The slope is exaggerated by many orders of magnitude. For a 100 m baseline
L/c is ~0.3 us against an interrogation time T of order a second.

- GR_PULSES, cloud_sequence, corners, cloud_legs: the bookkeeping, done by
  the pulse-sequence engine. Each cloud is one run_sequence over the same
  sloped pulses, timed at the cloud's own arrival, with climb="leg" so the
  corners stay pinned to the arrivals however the timing is modulated;
  corners gives the four (a, b, b_up, c) the scenes index, cloud_legs the
  legs a pulse launches.
- gradiometer_frame: the title, laser line, time axis and baseline every
  gradiometer scene opens with.
- laser_jumps: the laser's phase on a cloud's two hands, at the times each
  pulse reaches it.
- gr_fire_pulse, gr_sweep_pulse, gr_launch_time, gr_laser_caption: the
  sloped pulses of interferometry.tools.pulses with the GR_* geometry below.

The scenes built on these are GradiometerBase and its subclasses, in
interferometry.scenes.gradiometer.
"""

import numpy as np
from manim import *

from manim_atoms.interferometry.style import *
from manim_atoms.core.primitives import make_guide
from manim_atoms.core.spacetime import no_displacement
from manim_atoms.interferometry.tools.clock import CP_LASER_PHASES
from manim_atoms.interferometry.tools.pulse_sequence import Pulse, run_sequence
from manim_atoms.interferometry.tools.pulses import (
    fire_pulse,
    laser_caption,
    launch_time,
    sweep_pulse,
)


# --- gradiometer geometry -------------------------------------------------
GR_T = 2.8  # time between pulses
GR_T0 = -5.0  # time of the first pulse, at the lower cloud
GR_ARM = 1.05  # arm separation, i.e. (hbar k / m) T in real units
GR_LOWER_Z = -2.9
GR_BASELINE = 3.5  # L
GR_UPPER_Z = GR_LOWER_Z + GR_BASELINE
GR_LASER_Z = -3.85  # the laser sits at the bottom of the shaft
GR_LAG = 0.42  # light travel time across L, hugely exaggerated
GR_SLOPE = GR_LAG / GR_BASELINE  # dt/dz for a photon worldline
GR_MID_Z = 0.5 * (GR_LOWER_Z + GR_UPPER_Z)  # tells the two clouds apart
GR_LASER_GAP = GR_LOWER_Z - GR_LASER_Z  # laser to the near cloud
# How far the output ports run past the last pulse. The two ports part only
# at the kicked leg's slope, GR_ARM / GR_T, which is shallow here, so they need
# a long run to end up more than an atom apart (GR_OUT * GR_ARM / GR_T against
# 2 * CLOCK_ATOM_RADIUS); GR_T is kept short enough that this still stops
# short of the dials.
GR_OUT = 2.4


# pi/2, pi, pi/2 from the laser below, each passing the lower cloud at
# GR_T0 + k GR_T and the upper one GR_LAG later
GR_PULSES = [
    Pulse(GR_T0 + k * GR_T, area, slope=GR_SLOPE, z_ref=GR_LOWER_Z)
    for k, area in enumerate((0.5, 1.0, 0.5))
]


def cloud_sequence(pulses, z0, disp=no_displacement):
    """One cloud's interferometer: the atom at height ``z0`` stepped through
    ``pulses``, each acting when it reaches ``z0``. One recoil climbs GR_ARM
    per leg (climb="leg"), so the corners stay pinned to the arrivals even
    when a wave makes the intervals unequal; ``disp`` bows the legs."""
    return run_sequence(pulses, (pulses[0].arrival(z0), z0), GR_ARM, disp=disp,
                        port=GR_OUT, climb="leg")


def corners(seq):
    """A cloud's four corners (a, b, b_up, c): the split, the two arms at the
    mirror (b the one left alone at the split, b_up the one kicked there),
    and the recombination."""
    return seq.paths["0"][0], seq.paths["0"][1], seq.paths["1"][1], seq.paths["0"][2]


def cloud_legs(seq, k, pair, wavy=False):
    """The legs pulse k launches, as draw_legs takes them: (atom, start, end,
    colour) for each arm, ``pair[0]`` flying arm "0" (left alone at the
    split) and ``pair[1]`` arm "1"; with ``wavy``, the displacement too, as
    draw_wavy_legs takes them."""
    colors = {"g": ATOM_COLOR, "e": KICKED_COLOR}
    return [
        (pair[int(name)], start, end, colors[state], *((disp,) if wavy else ()))
        for name, start, end, state, disp in seq.steps[k].legs
    ]


def gradiometer_frame(scene, title_tex):
    """The furniture every gradiometer scene shares, played onto the screen.

    Returns the baseline arrow and its label, which are the only pieces a
    scene goes on to touch.
    """
    title = Tex(title_tex, font_size=FONT_TITLE).to_corner(UL)

    # The laser is a fixed object, so its worldline is horizontal.
    laser = make_guide(
        [-config.frame_x_radius + 0.4, GR_LASER_Z, 0],
        [config.frame_x_radius - 0.4, GR_LASER_Z, 0],
    )
    laser_tag = Tex("laser", font_size=FONT_LEGEND, color=LASER_COLOR).next_to(
        laser, UP, buff=0.12
    ).align_to(laser, LEFT)

    # axes of the space-time diagram
    # above the laser line, not below it -- below is off the bottom edge
    t_axis = Tex("time $\\rightarrow$", font_size=FONT_LEGEND,
                 color=lighten(GUIDE_COLOR))
    t_axis.next_to(laser, UP, buff=0.12).align_to(laser, RIGHT)

    baseline = DoubleArrow(
        [GR_T0 - 0.75, GR_LOWER_Z, 0],
        [GR_T0 - 0.75, GR_UPPER_Z, 0],
        buff=0,
        stroke_width=3,
        color=lighten(GUIDE_COLOR),
        max_tip_length_to_length_ratio=0.06,
    )
    baseline_label = MathTex(
        r"L", font_size=FONT_STATE, color=lighten(GUIDE_COLOR)
    ).next_to(baseline, LEFT, buff=0.12)

    scene.play(
        FadeIn(title), FadeIn(laser), FadeIn(laser_tag),
        FadeIn(t_axis), run_time=1.0,
    )
    scene.play(GrowFromCenter(baseline), FadeIn(baseline_label), run_time=0.7)
    return baseline, baseline_label


# One dial per interferometer, each level with the cloud it belongs to, so the
# two faces sit in the same order on the page as the clouds do on the baseline.
# the open band between the two interferometers, which is where the budget
# goes once the diagram is drawn -- and left of centre, because the right-hand
# end of that band is where the lower interferometer's ports climb into
GR_TERMS = np.array([-1.5, 0.1, 0.0])  # its labels clear of the lower cloud's last leg
GR_TERMS_WIDTH = 7.6  # the clear span between the L arrow and the ports
# Where the wave scenes say what is done with the two dials. Same band and
# same clear span as the budget, so all three gradiometer scenes end in the
# same place with the ports beside them.
# Centred in the band rather than a little above it, which was room enough
# when what went here was one line: the scaling runs to two, and the stretched
# picture bows the upper cloud down into whatever clearance is left.
GR_SIGNAL = np.array([-1.5, -0.62, 0.0])

GR_DIAL_RADIUS = 0.75
GR_DIALS = {
    "low": np.array([5.8, -1.95, 0.0]),  # clear of the time-axis label
    "up": np.array([5.8, 1.2, 0.0]),
}


def laser_jumps(v):
    """The laser's phase on each of a cloud's two hands, as (lab time, delta).

    The same bookkeeping as ClockPhase's, at the times each pulse reaches this
    cloud: an arm picks phi_n up when it absorbs from pulse n and gives it
    back when it emits, and the hands count -phase. Index 0 is the arm kicked
    at the mirror, index 1 the arm kicked at the beamsplitter.
    """
    phi1, phi2, phi3 = CP_LASER_PHASES
    return (
        [(v[1][0], -phi2)],
        [(v[0][0], -phi1), (v[1][0], +phi2), (v[3][0], -phi3)],
    )


# --- the sloped pulses, on this baseline ------------------------------------
def gr_fire_pulse(scene, x_at_lower, flash, lag=GR_LAG, reference=False, note=None,
                  z_near=GR_LOWER_Z, z_far=GR_UPPER_Z, quiet_x=None):
    """fire_pulse on the gradiometer's baseline: from the laser at GR_LASER_Z,
    crossing the lower cloud at ``x_at_lower`` and the upper ``lag`` later.
    ``flash`` is split into the two clouds' atoms at GR_MID_Z. With
    ``reference``, the quiet pulse (crossing at ``quiet_x``, default
    ``x_at_lower``, at GR_SLOPE) is drawn as a dashed ghost across GR_BASELINE."""
    near = [m for m in flash if m.get_center()[1] < GR_MID_Z]
    far = [m for m in flash if m.get_center()[1] >= GR_MID_Z]
    fire_pulse(scene, x_at_lower, near, far, lag, z_near, z_far, GR_LASER_Z,
               reference=_quiet(x_at_lower, quiet_x) if reference else None, note=note)


def gr_sweep_pulse(scene, clock, x_at_lower, near, far, lag=GR_LAG, reference=False,
                   note=None, z_near=GR_LOWER_Z, z_far=GR_UPPER_Z, quiet_x=None,
                   fade=(), on_near=None, on_far=None):
    """sweep_pulse on the gradiometer's baseline, as gr_fire_pulse is
    fire_pulse: ``near`` and ``far`` are the points to flash at the two
    crossings."""
    return sweep_pulse(
        scene, clock, x_at_lower, near, far, lag, z_near, z_far, GR_LASER_Z,
        reference=_quiet(x_at_lower, quiet_x) if reference else None, note=note,
        fade=fade, on_near=on_near, on_far=on_far,
    )


def _quiet(x_at_lower, quiet_x):
    """The quiet pulse's ghost, as fire_pulse's reference takes it."""
    base = x_at_lower if quiet_x is None else quiet_x
    return (base, GR_SLOPE, GR_LOWER_Z, GR_BASELINE)


def gr_launch_time(x_at_lower, z_at=GR_LOWER_Z):
    """When a quiet pulse that crosses height ``z_at`` at ``x_at_lower`` left
    the laser."""
    return launch_time(x_at_lower, GR_SLOPE, z_at, GR_LASER_Z)


def gr_laser_caption(n, x_at_lower, z_at=GR_LOWER_Z):
    """phi_n on the laser line, just right of where quiet pulse n left it."""
    return laser_caption(n, gr_launch_time(x_at_lower, z_at), GR_LASER_Z)
