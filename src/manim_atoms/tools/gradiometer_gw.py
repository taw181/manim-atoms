"""A gravitational wave passing through the gradiometer.

The strain h(t), the light travel time it modulates, the displacement it would
be drawn as if it stretched the baseline instead, and the h(t) trace that runs
along the top of the diagram on the diagram's own time axis.
"""

import numpy as np
from manim import *

from aionanim.style import *
from aionanim.tools.gradiometer import (
    GR_ARM,
    GR_BASELINE,
    GR_LAG,
    GR_LASER_GAP,
    GR_LASER_Z,
    GR_SLOPE,
    GR_T,
    GR_T0,
)


# --- a gravitational wave passing through ---------------------------------
# Deliberately off resonance. A wave of period 2T would put the three pulses
# on crest, trough and crest, which reads as if the detector only worked for a
# wave tuned to the sequence. Here the sequence is 1.2 periods long and starts
# at an arbitrary phase: the pulses still sample the wave at different points,
# so it survives the difference that a static gradient -- or the laser's own
# phase noise -- drops out of. The response goes as sin^2(omega T / 2).
#
# Two exaggerations, because the diagram draws L and L/c at wildly different
# scales, and a single factor cannot make both readable. GW_LAG_GAIN is the
# swing in light travel time, GW_STRETCH_GAIN the swing in the baseline drawn
# as a displacement. Both stand for the same dimensionless h, ~1e-21 in reality.
# Every scene takes its pulse timing from GW_LAG_GAIN, including the stretch
# one, so that the two pictures of the wave read out the same phase.
#
# GW_LAG_GAIN is also what sets how the output ports split, and that is what
# fixes its value. A pulse is held up in proportion to how far it has come, so
# the near cloud -- sitting close to the laser -- always responds about five
# times less than the far one, and no single gain can drive both to a half
# and half split. At 0.7 every port has something in it (the near pair splits
# about 79/21, the far pair about 39/61) and the two ends still read visibly
# differently, which is the whole claim of the figure. Much below 0.65 the far
# cloud's ground port empties; above it the far cloud wraps round towards the
# near one's split and the two ends stop reading differently.
GW_OMEGA = 1.2 * PI / GR_T
GW_PERIOD = TAU / GW_OMEGA
GW_THETA = -0.25 * PI  # the wave's phase at the first pulse
GW_LAG_GAIN = 0.7
GW_STRETCH_GAIN = 0.07
GW_PULSES = [GR_T0, GR_T0 + GR_T, GR_T0 + 2 * GR_T]

# the h(t) trace, drawn on the diagram's own time axis
GW_TRACE_Z = 2.75
GW_TRACE_AMPLITUDE = 0.28
GW_TRACE_X = (GR_T0 - 0.6, GR_T0 + 2 * GR_T + 0.8)


def strain(t):
    """h(t) at the detector, normalised to +-1, at GW_THETA at the first pulse."""
    return np.cos(GW_OMEGA * (t - GR_T0) + GW_THETA)


def gw_lag(t, gain=GW_LAG_GAIN):
    """Light travel time across the baseline while the wave is passing."""
    return GR_LAG * (1.0 + gain * strain(t))


def gw_arrival_lags(z):
    """How late each pulse reaches the point z on the baseline once the wave is
    passing.

    The wave stretches every stretch of the shaft by the same fraction, so a
    pulse is held up in proportion to how far it has come. The near cloud is
    not immune, only nearer: it picks up a smaller shift than the far one.
    What is left in the difference is the part that scales with the separation
    between the two clouds, which is the whole point of the instrument.
    """
    span = z - GR_LASER_Z
    return [gw_lag(t) / GR_BASELINE * span for t in GW_PULSES]


def quiet_arrival(k):
    """When pulse k would have reached the lower cloud with no wave passing."""
    return GW_PULSES[k] + GR_SLOPE * GR_LASER_GAP


def gw_displacement(t, z0):
    """How far the wave has moved a cloud nominally at z0 on the baseline.

    Drawn in the laser's frame. Only the change in separation is physical: in
    the local frame of any freely falling observer the wave moves each mass in
    proportion to its distance from that observer, and which point is held
    still is a choice. The laser is the one to hold, because gw_arrival_lags
    already times every pulse from it. The near cloud, just above the laser,
    then barely moves, and the far cloud carries nearly all of the change in L.
    """
    return (z0 - GR_LASER_Z) * GW_STRETCH_GAIN * strain(t)


def make_strain_trace(label=r"h(t)"):
    """The wave above the diagram, on the diagram's own time axis.

    The curve is the bare cosine at a drawing amplitude, so it carries which
    part of the wave each pulse samples and nothing about how big the wave is.
    That is why the label is a caller's choice: h(t) and Delta L(t) = L h(t)
    are the same shape, and a scene should name whichever one it is drawing.

    Sharing the x axis is the point: a pulse and the phase of the wave it
    samples sit in the same column, so where each pulse caught the wave can be
    read off against the pulse that caught it. Returns the curve and its three pulse
    markers separately, so a scene can light each marker as that pulse fires.
    """
    def at(t):
        return [t, GW_TRACE_Z + GW_TRACE_AMPLITUDE * strain(t), 0]

    zero = DashedLine(
        [GW_TRACE_X[0], GW_TRACE_Z, 0], [GW_TRACE_X[1], GW_TRACE_Z, 0],
        **GUIDE_STYLE,
    )
    curve = ParametricFunction(
        at, t_range=[*GW_TRACE_X, 0.02],
        color=STRAIN_COLOR, stroke_width=STRAIN_STROKE_WIDTH,
    )
    tag = MathTex(
        label, font_size=FONT_LEGEND, color=STRAIN_COLOR
    ).next_to(curve, LEFT, buff=0.18)
    dots = VGroup(*[Dot(at(t), radius=0.07, color=LASER_COLOR) for t in GW_PULSES])
    return VGroup(zero, curve, tag), dots


def strain_marker(clock):
    """field_marker's twin: where on the wave the diagram has got to.

    The three pulse dots say which part of the wave each pulse sampled, which
    is all a stop-start scene can show. Once lab time is running the trace can
    say it continuously, and without this it would be the one thing in the
    frame standing still. Held at the ends of the drawn curve, as the field
    marker is, because the output ports run on past the last pulse.
    """
    def at():
        t = float(np.clip(clock.get_value(), *GW_TRACE_X))
        return [t, GW_TRACE_Z + GW_TRACE_AMPLITUDE * strain(t), 0]

    return always_redraw(
        lambda: Dot(at(), radius=0.08, color=lighten(KICKED_COLOR))
    )


def gw_vertices(z0, lags):
    """The four corners when the three pulses arrive `lags` after they are fired.

    Every corner is anchored on its own pulse's arrival, which keeps the loop
    closed and keeps each flash centred on its atom. The price is that the two
    kicked legs pick up slightly different slopes, i.e. a recoil velocity that
    ought to be identical differs by a few per cent. That is the right trade:
    the real effect is a phase, not a change in the shape of the loop, and an
    interferometer drawn failing to close would read as a bug rather than as
    physics. The skew that is left is an artefact of the exaggeration.
    """
    t = [GW_PULSES[k] + lags[k] for k in range(3)]
    a = np.array([t[0], z0, 0.0])
    b = np.array([t[1], z0, 0.0])
    b_up = b + UP * GR_ARM
    c = np.array([t[2], z0 + GR_ARM, 0.0])
    return a, b, b_up, c


def arrival_note(point, lag):
    """Names an arrival early or late against the quiet baseline's own L/c.

    It sits below the cloud, which is the one direction that stays clear: the
    arms climb away above it and the pulse is only passing through underneath.
    """
    word = "arrives late" if lag > GR_LAG else "arrives early"
    return Tex(word, font_size=FONT_LEGEND, color=LASER_COLOR).next_to(
        point, DOWN, buff=0.3
    ).shift(RIGHT * 1.1)
