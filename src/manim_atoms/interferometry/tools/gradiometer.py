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

- vertices: one interferometer's four corners; gradiometer_frame: the title,
  laser line, time axis and baseline every gradiometer scene opens with.
- laser_jumps: the laser's phase on a cloud's two hands, at the times each
  pulse reaches it.

The pulses that climb the baseline are in interferometry.tools.pulses,
whose defaults bind to the GR_* geometry block below. The scenes built on these
are GradiometerBase and its subclasses, in interferometry.scenes.gradiometer.
"""

import numpy as np
from manim import *

from manim_atoms.interferometry.style import *
from manim_atoms.core.primitives import make_guide
from manim_atoms.interferometry.tools.clock import CP_LASER_PHASES


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


def vertices(z0, lag):
    """The four corners of one interferometer in the (time, baseline) plane."""
    a = np.array([GR_T0 + lag, z0, 0.0])
    b = a + RIGHT * GR_T
    b_up = b + UP * GR_ARM
    c = b_up + RIGHT * GR_T
    return a, b, b_up, c


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
