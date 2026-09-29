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
"""

import numpy as np
from manim import *

from aionanim.style import *
from aionanim.tools.primitives import make_guide
from aionanim.tools.spacetime import run_to


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


def photon_worldline(x_at_lower, z_from, z_to, slope=GR_SLOPE, z_at=GR_LOWER_Z):
    """The segment of a pulse's worldline between two points on the baseline.

    `x_at_lower` is when it passes `z_at` on the baseline, i.e. the lower cloud,
    so the geometry of every pulse is fixed by one number and the two crossings
    stay consistent. The slope is the light travel time per unit baseline: a
    constant in a quiet gradiometer, and the signal itself once a wave is passing.
    """
    start = [x_at_lower + slope * (z_from - z_at), z_from, 0]
    end = [x_at_lower + slope * (z_to - z_at), z_to, 0]
    return Line(start, end, color=LASER_COLOR, stroke_width=PULSE_STROKE_WIDTH)


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
    z_axis = Tex("baseline", font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR))
    z_axis.rotate(90 * DEGREES).to_edge(LEFT, buff=0.18).set_y(0.3)

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
        FadeIn(t_axis), FadeIn(z_axis), run_time=1.0,
    )
    scene.play(GrowFromCenter(baseline), FadeIn(baseline_label), run_time=0.7)
    return baseline, baseline_label


def fire_pulse(scene, x_at_lower, flash, lag=GR_LAG, reference=False, note=None,
               z_near=GR_LOWER_Z, z_far=GR_UPPER_Z, quiet_x=None):
    """Send one pulse up the baseline, reaching the far cloud `lag` later.

    `z_near` and `z_far` are where the two clouds actually are when the pulse
    crosses them, which only differ from the nominal positions on the baseline
    once a wave is
    moving the clouds around. With `reference` the worldline the pulse would
    have followed in a quiet baseline is drawn alongside as a dashed ghost, so
    an arrival is visibly early or late rather than merely shifted; `note` is
    faded in at the far crossing to name it, and fades out with the pulse.
    """
    slope = lag / (z_far - z_near)
    below = photon_worldline(x_at_lower, GR_LASER_Z, z_near, slope, z_near)
    across = photon_worldline(x_at_lower, z_near, z_far, slope, z_near)
    beyond = photon_worldline(
        x_at_lower, z_far, config.frame_y_radius + 0.3, slope, z_near
    )

    low_hits = [m for m in flash if m.get_center()[1] < GR_MID_Z]
    up_hits = [m for m in flash if m.get_center()[1] >= GR_MID_Z]

    drawn = [below, across, beyond]
    ghost = None
    if reference:
        # Anchored on where the pulse would have crossed with no wave passing,
        # which is not where it actually crossed: the wave has already held it
        # up on the way from the laser to the near cloud.
        base = x_at_lower if quiet_x is None else quiet_x
        quiet = photon_worldline(base, z_near, z_near + GR_BASELINE)
        ghost = DashedLine(
            quiet.get_start(), quiet.get_end(),
            **{**GUIDE_STYLE, "stroke_opacity": 0.55},
        )
        drawn.append(ghost)
    if note is not None:
        drawn.append(note)

    scene.play(Create(below), rate_func=linear, run_time=0.45)
    scene.play(*[Flash(m, **FLASH_STYLE) for m in low_hits], run_time=0.35)
    scene.play(
        Create(across),
        *([Create(ghost)] if ghost is not None else []),
        rate_func=linear,
        run_time=0.7,
    )
    scene.play(
        *[Flash(m, **FLASH_STYLE) for m in up_hits],
        *([FadeIn(note)] if note is not None else []),
        run_time=0.35,
    )
    scene.play(Create(beyond), rate_func=linear, run_time=0.3)
    scene.play(*[FadeOut(m) for m in drawn], run_time=0.3)


# One dial per interferometer, each level with the cloud it belongs to, so the
# two faces sit in the same order on the page as the clouds do on the baseline.
# the open band between the two interferometers, which is where the budget
# goes once the diagram is drawn -- and left of centre, because the right-hand
# end of that band is where the lower interferometer's ports climb into
GR_TERMS = np.array([-1.5, -0.3, 0.0])
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


def climbing_pulse(clock, x_at_lower, slope, z_from, z_to, z_at):
    """A photon's worldline, drawn as far up the baseline as it has got.

    The counterpart of Create(photon_worldline(...)): same geometry, but the
    length is read off the clock instead of off an animation's alpha, so the
    pulse and the atoms it is about to hit are both being drawn by the same
    number.
    """
    def reached():
        z = z_at + (clock.get_value() - x_at_lower) / slope
        floor = min(z_from, z_to) + 1e-3  # never a zero-length Line
        return float(np.clip(z, floor, max(z_from, z_to)))

    return always_redraw(
        lambda: photon_worldline(x_at_lower, z_from, reached(), slope, z_at)
    )


def sweep_pulse(scene, clock, x_at_lower, near, far, lag=GR_LAG, reference=False,
                note=None, z_near=GR_LOWER_Z, z_far=GR_UPPER_Z, quiet_x=None,
                fade=(), on_near=None, on_far=None):
    """fire_pulse with lab time running: the pulse climbs, the atoms carry on.

    `near` and `far` are the points to flash at the two crossings -- the
    vertices themselves rather than the atoms sitting on them. Flash snapshots
    a mobject's centre when it is built, so on an atom that is still moving
    the ring would be left behind; the vertex is where the atom is at that
    instant by construction, and flashing it marks the event rather than
    chasing the mobject.

    `on_near` and `on_far` are called as the pulse reaches each cloud, which
    is where whatever it does to those atoms belongs. They are separate
    because in these scenes the two crossings are separate events: the clouds
    are a baseline apart, so the far one is split, mirrored and recombined
    L/c after the near one, and a continuous scene shows that rather than
    asserting it in a caption.

    Returns everything it drew instead of fading it, and `fade` takes the
    previous pulse's return. At V a pulse crosses the frame in well under a
    second, and the arrival notes are the explanatory payload of these scenes
    -- faded out with the pulse that earned them they could not be read. So
    each one stays up until the next pulse is on its way, and goes out over
    the last PULSE_LINGER of lab time before it arrives.
    """
    slope = lag / (z_far - z_near)
    drawn = VGroup(climbing_pulse(
        clock, x_at_lower, slope, GR_LASER_Z, config.frame_y_radius + 0.3, z_near
    ))
    if reference:
        # The ghost goes on whole rather than growing: a DashedLine rebuilt at
        # a new length every frame reshuffles its dashes, which reads as a
        # shimmer instead of as a reference.
        base = x_at_lower if quiet_x is None else quiet_x
        quiet = photon_worldline(base, z_near, z_near + GR_BASELINE)
        drawn.add(DashedLine(
            quiet.get_start(), quiet.get_end(),
            **{**GUIDE_STYLE, "stroke_opacity": 0.55},
        ))

    # The leg, then the last of it with the previous pulse clearing the frame,
    # then one segment per crossing so that each flash is launched at the lab
    # time the pulse actually arrives there.
    lead = min(PULSE_LINGER, max(x_at_lower - clock.get_value(), 0.0))
    run_to(scene, clock, x_at_lower - lead)
    scene.add(drawn)
    run_to(scene, clock, x_at_lower, *[FadeOut(m) for m in fade])
    if on_near is not None:
        on_near()
    run_to(
        scene, clock, x_at_lower + lag,
        *[Flash(p, run_time=STROBE_FLASH, **FLASH_STYLE) for p in near],
    )
    if on_far is not None:
        on_far()
    if note is not None:
        scene.add(note)
        drawn.add(note)
    run_to(
        scene, clock, x_at_lower + lag + PULSE_HOLD,
        *[Flash(p, run_time=STROBE_FLASH, **FLASH_STYLE) for p in far],
    )
    return drawn
