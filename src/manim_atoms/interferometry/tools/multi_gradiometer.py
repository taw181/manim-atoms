"""The multi-gradiometer: three clock interferometers on one baseline, one laser.

The gradiometer of tools/gradiometer.py with a third cloud halfway up the
baseline. The same space-time diagram -- time across, distance along the
baseline up -- and the same light: one laser at the bottom of the shaft,
whose pulses climb at GR_SLOPE and so reach the middle cloud L/2c and the far
one L/c after the near one. Every pulse writes its phase into all three
interferometers, so it drops out of every difference between them.

A third cloud buys a second, independent difference sharing the first's
middle cloud. A signal that grows linearly along the baseline -- which is how
a single-photon gradiometer's gravitational-wave and dark-matter phases scale,
in proportion to the separation -- splits equally between the two pairs, and
their difference, Phi_upper - 2 Phi_middle + Phi_lower, removes it along with
the laser. What survives that is whatever does not grow linearly along the
baseline, which is how the multi-gradiometer proposals tell gravity-gradient
noise from signal.

Only the geometry and the pulse helpers that cross any number of clouds live
here; the two-cloud pieces are reused from tools/gradiometer.py.
"""

import numpy as np
from manim import *

from manim_atoms.interferometry.style import *
from manim_atoms.interferometry.tools.gradiometer import (
    GR_BASELINE,
    GR_LASER_Z,
    GR_LOWER_Z,
    GR_SLOPE,
    climbing_pulse,
    photon_worldline,
)
from manim_atoms.core.spacetime import run_to


# --- multi-gradiometer geometry ---------------------------------------------
# Bottom to top, which is also the order each pulse reaches them in. The outer
# two sit where the two-cloud gradiometer's do, so gradiometer_frame's L arrow
# spans the same baseline, and the light keeps the same speed; the third
# splits it in half, so each pair is L/2 apart and L/2c late.
MG_CLOUDS = ("low", "mid", "up")
MG_SPACING = GR_BASELINE / 2
MG_Z = {c: GR_LOWER_Z + k * MG_SPACING for k, c in enumerate(MG_CLOUDS)}
MG_LAG = {c: GR_SLOPE * (MG_Z[c] - GR_LOWER_Z) for c in MG_CLOUDS}
# Shorter arms than GR_ARM, so three interferometers fit where two did: with
# a clock atom's radius each side of a leg, GR_ARM-high interferometers half a
# baseline apart would touch.
MG_ARM = 0.75
# The ports part only at the kicked leg's slope, MG_ARM / GR_T, which is
# shallower still than the two-cloud scene's, so they run further to end up
# more than an atom apart (MG_OUT * MG_ARM / GR_T against 2 *
# CLOCK_ATOM_RADIUS) -- and still stop short of the dials.
MG_OUT = 3.0

# One dial per interferometer, level with its cloud's arms as in the
# two-cloud scene, and smaller, so three faces and their captions fit down
# the right-hand side with the lowest caption clear of the time-axis label.
MG_DIAL_RADIUS = 0.55
MG_DIALS = {
    "low": np.array([5.8, -2.3, 0.0]),
    "mid": np.array([5.8, -0.55, 0.0]),
    "up": np.array([5.8, 1.2, 0.0]),
}
MG_DIAL_CAPTIONS = {
    "low": r"$\Phi_{\text{lower}}$",
    "mid": r"$\Phi_{\text{middle}}$",
    "up": r"$\Phi_{\text{upper}}$",
}

# Something on the atoms that grows linearly along the baseline, over the
# middle of each interferometer's second leg (as Gradiometer's effect): equal
# steps in height, so equal steps in phase. On top of the laser's 1.3 rad the
# |g> ports come out at ~49%, ~27% and ~10% -- visibly a progression, and none
# emptied into a dashed guide.
MG_EFFECT_PHASE = {"low": 0.3, "mid": 0.75, "up": 1.2}
MG_EFFECT_TIME = 2.5
# Where the result goes: the open strip above the upper interferometer's
# first leg and under the title, left of where its ports climb.
MG_RESULT = np.array([-6.6, 2.85, 0.0])  # upper-left corner


def stop_x(x_at, z_at, z, slope=GR_SLOPE):
    """When a pulse that crosses `z_at` at `x_at` crosses height `z`."""
    return x_at + slope * (z - z_at)


def fire_pulse_through(scene, x_at, z_at, stops, slope=GR_SLOPE):
    """fire_pulse for any number of clouds on the baseline.

    `stops` is a list of (z, mobjects to flash), bottom to top, one per cloud
    the pulse crosses; the pulse crosses `z_at` at time `x_at`. Paced as
    fire_pulse is -- the run up from the laser, the climb across the baseline,
    the run off the top -- with the climb shared out between the gaps by
    their height, and a flash at each crossing.
    """
    heights = [GR_LASER_Z, *[z for z, _ in stops], config.frame_y_radius + 0.3]
    segments = [
        photon_worldline(x_at, z0, z1, slope, z_at)
        for z0, z1 in zip(heights, heights[1:])
    ]
    for k, segment in enumerate(segments):
        if k == 0:
            run_time = 0.45
        elif k == len(segments) - 1:
            run_time = 0.3
        else:
            run_time = 0.7 * (heights[k + 1] - heights[k]) / GR_BASELINE
        scene.play(Create(segment), rate_func=linear, run_time=run_time)
        if k < len(stops):
            scene.play(*[Flash(m, **FLASH_STYLE) for m in stops[k][1]],
                       run_time=0.35)
    scene.play(*[FadeOut(m) for m in segments], run_time=0.3)


def sweep_pulse_through(scene, clock, x_at, z_at, stops, slope=GR_SLOPE, fade=()):
    """sweep_pulse for any number of clouds: the pulse climbs, the atoms fly.

    `stops` is a list of (z, points to flash, on_arrival or None), bottom to
    top. As in sweep_pulse, each crossing gets a segment of lab time of its
    own, so a cloud's flash is launched -- and whatever the pulse does to it
    is done -- at the lab time the pulse reaches that cloud, and the previous
    pulse's drawing (`fade`) goes out over the last PULSE_LINGER before this
    one arrives. Returns what it drew, for the next pulse to fade.
    """
    drawn = VGroup(climbing_pulse(
        clock, x_at, slope, GR_LASER_Z, config.frame_y_radius + 0.3, z_at
    ))
    times = [stop_x(x_at, z_at, z, slope) for z, _, _ in stops]
    lead = min(PULSE_LINGER, max(times[0] - clock.get_value(), 0.0))
    run_to(scene, clock, times[0] - lead)
    scene.add(drawn)
    run_to(scene, clock, times[0], *[FadeOut(m) for m in fade])
    ends = [*times[1:], times[-1] + PULSE_HOLD]
    for (_, points, on_arrival), end in zip(stops, ends):
        if on_arrival is not None:
            on_arrival()
        run_to(
            scene, clock, end,
            *[Flash(p, run_time=STROBE_FLASH, **FLASH_STYLE) for p in points],
        )
    return drawn
