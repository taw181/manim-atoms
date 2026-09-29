"""Space-time diagrams: worldlines, and running one on a single lab clock.

Every AION scene is a space-time diagram -- the horizontal axis is lab time,
the vertical axis is position along the baseline -- and these are the pieces
for drawing and animating one: legs and worldlines that can be displaced by a
passing wave, the ValueTracker clock the continuous variants run on, atoms
and trails carried along by it, and the phase each arm winds up on the way.
"""

import numpy as np
from manim import *

from aionanim.style import *


# --- running the diagram continuously -------------------------------------
# Every AION scene draws a space-time diagram: x is lab time and y is where
# on the baseline something is. Stop-start rendering therefore stops lab time
# itself -- the atoms wait for a pulse to be drawn, and so does the wave or
# the field that is passing through, which is the one thing those scenes are
# about. The continuous variants run a single ValueTracker whose value *is*
# the diagram's x coordinate, and make everything a function of it: atom
# positions, the trails behind them, the photon worldlines, the marker on the
# trace, the phase each arm has wound up. Nothing can then disagree with
# anything else, because there is only one number.
#
# The corollary is a discipline rather than a helper: between the first pulse
# and the last, every scene.play has to advance the clock. One that does not
# is exactly the freeze these variants exist to remove, so a beat that cannot
# be folded into a clock-advancing play has to become an always_redraw that
# switches itself on as lab time passes it.


def leg_point(start, end, disp, s):
    """Where an atom on a bowed leg is, a fraction s of the way along it.

    The displacement is subtracted at the two ends and added back along the
    way, so the leg still passes exactly through both corners -- the pulses
    have to land on the atoms.

    With a disp that returns zero this is straight interpolation, which is
    what lets one set of helpers carry both the bowed legs of the stretched
    gradiometer and the straight ones everywhere else.
    """
    x = interpolate(start[0], end[0], s)
    y = interpolate(start[1] - disp(start[0]), end[1] - disp(end[0]), s) + disp(x)
    return np.array([x, y, 0.0])


def wavy_path(start, end, color, disp, s_max=1.0):
    """The leg bowed by the wave, drawn a fraction s_max of the way along."""
    return ParametricFunction(
        lambda s: leg_point(start, end, disp, s),
        t_range=[0.0, max(s_max, 1e-4), 0.01],
        color=color,
        **TRAJECTORY_STYLE,
    )


def no_displacement(_):
    """A quiet baseline: the legs are straight and the corners are where they say."""
    return 0.0


def leg_share(start, end, t):
    """How far along the leg from `start` to `end` lab time `t` has got.

    Clamped at both ends, which is what lets one arm's whole worldline be
    written as a sequence of legs and evaluated at any time: before its first
    corner it sits at the start, after its last it sits at the end.
    """
    return float(np.clip((t - start[0]) / (end[0] - start[0]), 0.0, 1.0))


def run_to(scene, clock, to, *anims, **kwargs):
    """Advance lab time to `to` at V, playing `anims` while it runs.

    The one primitive the continuous scenes are built out of. Everything that
    has to happen between the first pulse and the last goes through here, so
    that it happens *while* the diagram is being drawn rather than instead of
    it.

    Asking for a time lab time is already at plays the animations on the spot.
    The only call that should ever land there is the run-up to the first
    pulse, which is where the clock starts; anywhere else it is the freeze
    this helper exists to avoid, and it will show.

    The pacing goes on the sweep itself and never as a play() kwarg, because
    Scene.play sets every kwarg it is given on every animation in the call --
    which would stretch a quarter-second flash to the length of a whole leg.
    Anything handed in that is longer than the sweep is cut back to it for the
    same reason in reverse: Scene.play runs for the longest animation it has,
    so lab time would arrive at `to` and then sit there for the remainder.
    """
    run_time = (to - clock.get_value()) / V
    if run_time <= 1e-6:
        return scene.play(*anims, **kwargs) if anims else None
    for anim in anims:
        anim.run_time = min(anim.run_time, run_time)
    return scene.play(
        clock.animate(run_time=run_time, rate_func=linear).set_value(to),
        *anims,
        **kwargs,
    )


def worldline(corners, disp=no_displacement):
    """A function from lab time to where an arm is, given the corners it turns at.

    `corners` are in lab-time order. Outside the arm's own span the value is
    held at the nearer end, so an arm can be built and put on the screen
    before the beamsplitter has made it and left parked after it recombines,
    without the caller having to guard either edge.
    """
    def at(t):
        for start, end in zip(corners, corners[1:]):
            if t <= end[0]:
                return leg_point(start, end, disp, leg_share(start, end, t))
        start, end = corners[-2], corners[-1]
        return leg_point(start, end, disp, 1.0)

    return at


def wound(clock, rate, t_from, t_to):
    """An updater for the angle an arm excited from t_from to t_to has reached.

    The continuous counterpart of draw_legs' extra=[tracker.animate...]: the
    phase is read off the clock rather than advanced leg by leg, so a hand
    keeps turning through a pulse as well as along a leg, and holds of its own
    accord once the mirror has handed the excitation over.
    """
    def turn(tracker):
        tracker.set_value(
            rate * (float(np.clip(clock.get_value(), t_from, t_to)) - t_from)
        )

    return turn


def growing_band(band, t_from, t_to, now, style=FIELD_WINDOW_STYLE):
    """A band over a stretch of the diagram, filling in as that stretch is flown.

    Takes the finished band's height and redraws its width off the clock, so
    it keeps pace with the atoms underneath it instead of arriving all at once
    in a beat of its own -- which in a continuous scene would be a beat with
    lab time stopped. Used for the washes over an oscillation's windows, and
    for a beam that is switched on and off, which is why the style is the
    caller's: a bounded band cannot be drawn at zero width without its own
    left edge standing there before it is due, so nothing is returned at all
    until lab time is inside the window.
    """
    top, bottom = band.get_top()[1], band.get_bottom()[1]

    def draw():
        t = float(np.clip(now.get_value(), t_from, t_to))
        if t - t_from < 1e-3:
            return VGroup()
        return Rectangle(
            width=t - t_from, height=top - bottom, **style
        ).move_to([0.5 * (t_from + t), 0.5 * (top + bottom), 0])

    return always_redraw(draw)


def wound_with_shift(clock, rate, t_from, t_to, on, off, shift):
    """wound(), with `shift` accrued on top of it across the window [on, off].

    What a light shift does to a hand. The arm is in |e> for the whole leg, so
    it turns at omega_A throughout; for the stretch the beam is on it turns at
    omega_A + delta_LS instead, and the difference is what is left in the
    hand afterwards. Linear across the window because a shutter is open or
    shut, not ramped.
    """
    def turn(tracker):
        t = float(np.clip(clock.get_value(), t_from, t_to))
        held = float(np.clip((t - on) / (off - on), 0.0, 1.0))
        tracker.set_value(rate * (t - t_from) + shift * held)

    return turn


def carry(atom, path, clock):
    """Pin an atom to its worldline for as long as lab time is running.

    Deliberately an updater on the atom rather than an animation: an animation
    would have to be restarted at every corner, which is the stop-start
    structure again. Note that draw_wavy_legs clears an atom's updaters when
    it finishes, so the two movers cannot be mixed on one atom.
    """
    atom.add_updater(lambda m: m.move_to(path(clock.get_value())))
    return atom


def growing_trail(corners, color, clock, disp=no_displacement):
    """The trajectory behind an arm, drawn as far as lab time has got.

    One always_redraw per leg clipped by a clamped share, rather than one
    polyline for the whole arm: that is what wavy_path's s_max already does,
    and it keeps the bowed and the straight cases the same code. A leg lab
    time has not reached yet draws as a stub of length 1e-4, which is
    invisible and, unlike a zero-length path, does not upset ParametricFunction.
    """
    return VGroup(*[
        always_redraw(
            lambda start=start, end=end: wavy_path(
                start, end, color, disp, leg_share(start, end, clock.get_value())
            )
        )
        for start, end in zip(corners, corners[1:])
    ])


def draw_wavy_legs(scene, legs, fade=(), extra=()):
    """draw_legs for clouds whose worldlines carry the wave's displacement.

    draw_legs creates a straight Line and walks the atom to the far end. That
    will not do on a bowed leg: Create paints a curve by point index while an
    atom animated along it moves by arc length, and the two come apart by
    something like a fifth of the leg -- the atom visibly trails the end of
    the line it is supposed to be drawing. So the atom and the trail behind it
    are both redrawn from the one parameter, and stay together by construction.
    """
    s = ValueTracker(0.0)
    trails = [
        always_redraw(
            lambda leg=leg: wavy_path(leg[1], leg[2], leg[3], leg[4], s.get_value())
        )
        for leg in legs
    ]
    for atom, start, end, _, disp in legs:
        atom.add_updater(
            lambda m, start=start, end=end, disp=disp: m.move_to(
                leg_point(start, end, disp, s.get_value())
            )
        )
    scene.add(*trails)

    dx = abs(legs[0][2][0] - legs[0][1][0])
    scene.play(
        s.animate.set_value(1.0),
        *extra,
        *[FadeOut(m) for m in fade],
        rate_func=linear,
        run_time=dx / V,
    )

    # Freeze the finished legs: a live trail would be rebuilt against the next
    # leg's tracker, and an atom left with its updater would be pinned to the
    # end of the leg it has just finished.
    for atom, *_ in legs:
        atom.clear_updaters()
    scene.remove(*trails)
    scene.add(*[wavy_path(l[1], l[2], l[3], l[4]) for l in legs])
    scene.bring_to_front(*[l[0] for l in legs])
