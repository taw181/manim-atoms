"""Laser pulses on a space-time diagram: lab time across, height up.

- With light travel time, as in the gradiometer: photon_worldline is a
  pulse's line of finite slope, climbing_pulse draws it as far as the lab
  clock has got; fire_pulse sends one up the baseline with lab time
  stopped, sweep_pulse with it running, calling back as the pulse reaches
  each cloud. launch_time is when a pulse left the laser, laser_caption
  names the phase it carries there.
- Without it, where one pulse reaches every arm at once: fire_vertical_pulse
  climbs a column with lab time stopped, strobe_pulse flashes it whole with
  lab time running.
- From either side: kick_worldline, a photon arriving at a point from below
  or from above.
- pulse_caption: a pulse's label on the caption row along the bottom.

Defaults bind to the gradiometer's GR_* geometry (interferometry.tools.gradiometer).
"""

import numpy as np
from manim import *

from manim_atoms.interferometry.style import *
from manim_atoms.core.spacetime import run_to
from manim_atoms.interferometry.tools.gradiometer import (
    GR_BASELINE,
    GR_LAG,
    GR_LASER_Z,
    GR_LOWER_Z,
    GR_MID_Z,
    GR_SLOPE,
    GR_UPPER_Z,
)


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


def launch_time(x_at_lower, z_at=GR_LOWER_Z):
    """When a pulse that crosses height `z_at` at `x_at_lower` leaves the laser."""
    return x_at_lower - GR_SLOPE * (z_at - GR_LASER_Z)


def laser_caption(n, x_at_lower, z_at=GR_LOWER_Z):
    """phi_n on the laser line, just right of where pulse n leaves it."""
    foot = launch_time(x_at_lower, z_at)
    return MathTex(
        rf"\phi_{n}", font_size=FONT_ANNOTATION, color=LASER_COLOR
    ).next_to([foot, GR_LASER_Z, 0], UR, buff=0.12)


def fire_vertical_pulse(scene, x, hits):
    """One pulse climbing the diagram at time `x`, flashing what it crosses.

    A bare worldline, as in the gradiometer, but vertical: nothing in this
    scene turns on the light travel time, and both arms share a column, so one
    pulse reaches them at the same instant -- which is what makes the two legs
    equal and the null exact. It stops at the topmost atom it acts on rather
    than running off the top, because there is nothing above to draw it for.
    """
    hits = sorted(hits, key=lambda m: m.get_center()[1])
    y = -config.frame_y_radius - 0.3
    drawn = []
    for atom in hits:
        y_next = atom.get_center()[1]
        segment = Line(
            [x, y, 0], [x, y_next, 0],
            color=LASER_COLOR, stroke_width=PULSE_STROKE_WIDTH,
        )
        scene.play(
            Create(segment), rate_func=linear, run_time=(y_next - y) / PULSE_SPEED
        )
        scene.play(Flash(atom, **FLASH_STYLE), run_time=0.3)
        drawn.append(segment)
        y = y_next
    scene.play(*[FadeOut(m) for m in drawn], run_time=0.3)


def strobe_pulse(scene, clock, x, top, flash_at, on_arrival=None, hold=PULSE_HOLD):
    """fire_vertical_pulse with lab time running.

    The clock geometry has no light travel time -- one pulse reaches both arms
    at the same instant, which is what makes the two legs equal -- so the
    column is not something that climbs. It is an instant: it appears whole at
    the crossing and fades over `hold` of lab time while the atoms carry on
    through it. `top` is where the column stops, the topmost vertex it acts
    on, for the same reason fire_vertical_pulse stops at the topmost atom.

    `on_arrival` is called once lab time is on the pulse and before anything
    is played, which is where whatever the pulse does to the atoms belongs --
    swapping which arm is excited, say. It happens on the instant because the
    pulse does: there is no window here to animate it over.
    """
    column = Line(
        [x, -config.frame_y_radius - 0.3, 0], [x, top, 0],
        color=LASER_COLOR, stroke_width=PULSE_STROKE_WIDTH,
    )
    run_to(scene, clock, x)
    if on_arrival is not None:
        on_arrival()
    scene.add(column)
    run_to(
        scene, clock, x + hold,
        *[Flash(p, run_time=STROBE_FLASH, **FLASH_STYLE) for p in flash_at],
        FadeOut(column),
    )


def kick_worldline(point, from_below, steepness=0.12, span=None):
    """A photon's worldline arriving at `point` from below or from above:
    from the frame's edge, or from the (bottom, top) of `span`, to keep it
    out of a title or a caption row."""
    bottom, top = span or (-config.frame_y_radius, config.frame_y_radius)
    edge = bottom if from_below else top
    dx = steepness * abs(point[1] - edge)
    return Line(
        [point[0] - dx, edge, 0], point,
        color=LASER_COLOR, stroke_width=PULSE_STROKE_WIDTH,
    )


def pulse_caption(tex, x):
    """A pulse label on the caption row, offset clear of the beam it names."""
    return MathTex(tex, font_size=FONT_ANNOTATION, color=LASER_COLOR).move_to(
        [x + 0.5, -config.frame_y_radius + 0.35, 0]
    )
