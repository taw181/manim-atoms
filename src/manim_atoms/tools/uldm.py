"""An oscillating ultralight dark-matter field, and the clock transition it moves.

The field, the phase an excited arm winds up in it, its trace above the
diagram, and the two-level diagram whose upper level rides that trace.
"""

import numpy as np
from manim import *

from aionanim.style import *
from aionanim.tools.clock import (
    CP_T,
    CP_T0,
)
from aionanim.tools.primitives import (
    state_label,
)


# --- an oscillating ultralight dark-matter field --------------------------
# A scalar field light enough to be a coherent wave in the lab oscillates at
# omega_phi = m_phi c^2 / hbar. Coupled to the fundamental constants it drags
# them along with it, and the Sr clock frequency goes with them:
#
#     omega_A -> omega_A [1 + eps cos(omega_phi t + theta)].
#
# That is not a shift the interferometer can throw away. An arm only winds its
# hand while it is excited, and the two arms are excited over different
# windows -- arm 1 over leg 1, and the mirror hands the excitation to arm 2
# for leg 2 -- so each integrates its own stretch of the oscillation. Equal
# window lengths no longer mean equal phase, the hands miss each other and the
# ports split. It is ClockPhase's omega_A T null broken by the source rather
# than by the geometry.
#
# Deliberately off resonance. omega_phi = pi / T would put the three pulses on
# zero crossings with each leg exactly a half-cycle, which reads as if the
# measurement only worked when the field was tuned to the sequence. Here the
# sequence is 1.2 periods long and starts at an arbitrary phase, and the two
# windows still integrate to different amounts -- the response goes as
# sin^2(omega_phi T / 2), which is only zero at omega_phi T = 2 pi m.
DM_OMEGA = 1.2 * PI / CP_T
DM_THETA = -0.15 * PI  # the field's phase at the first pulse
# The fractional swing in omega_A, exaggerated in the same spirit as
# GW_LAG_GAIN: bounds on a scalar coupling in this mass range sit below about
# 1e-16, so this is some fifteen orders of magnitude too big. What the figure
# carries is which part of the cycle each arm sampled, not how large the
# effect is. Set so the hands part by as much as they did on resonance.
DM_EPS = 0.23

# the field's trace, above the diagram and on the diagram's own time axis
DM_TRACE_Z = 2.3
DM_TRACE_AMPLITUDE = 0.32
DM_TRACE_X = (CP_T0 - 0.4, CP_T0 + 2 * CP_T + 0.7)
# --- the transition the field is moving -----------------------------------
# The trace says the field is oscillating and the hands say the phase does not
# cancel; neither says what the atom sees. This is the same two-level system
# the single-photon scenes draw, with |e> riding that trace: the field walks
# omega_A up and down, and the laser, which knows nothing about the field,
# stays exactly where it was tuned. So the arrow is fixed and the level is
# not, and the gap that opens between the arrow's head and |e> is the
# detuning -- which is how a shift in a clock frequency becomes something an
# interferometer can be sensitive to at all.
#
# The swing is DM_EPS's exaggeration carried into the level diagram rather
# than a second one on top of it: both the level and the trace are drawn from
# dm_field, so they are the same curve read at the same instant.
DM_LEVELS = np.array([-5.4, 0.55, 0.0])  # centre of the unmodulated gap
DM_LEVEL_LENGTH = 1.6  # wide enough to hold two arrows and both their labels
DM_LEVEL_GAP = 1.5
DM_LEVEL_SWING = 0.38  # how far |e> rides, in the same spirit as the trace
DM_LEVEL_INSET = 0.1  # how far an arrow stands off a level line
DM_KET_BUFF = 0.2
DM_GAP_X = -0.5  # where the omega_A arrow stands, from the diagram centre
DM_GAP_LABEL_BUFF = 0.14  # and how far its label sits off it
DM_LASER_X = 0.45  # the laser's arrow, far enough right to read as its own
DM_MARK_X = 0.60  # the column the laser's labels and the detuning bar sit in


def dm_field(t):
    """The field's modulation of omega_A at time t, normalised to +-1.

    At DM_THETA at the first pulse: an arbitrary phase, not one picked to
    line the pulses up with the wave.
    """
    return np.sin(DM_OMEGA * (t - CP_T0) + DM_THETA)


def dm_phase(rate, t_from, t_to):
    """What an arm's hand winds up while excited from t_from to t_to.

    The hand turns at the modulated frequency, so what it has accumulated is
    omega_A integrated across the window rather than omega_A times its length.
    Both windows here are one leg long; the integrals differ all the same, and
    that difference is the whole signal.
    """
    def wound(t):
        return t - DM_EPS * np.cos(DM_OMEGA * (t - CP_T0) + DM_THETA) / DM_OMEGA

    return rate * (wound(t_to) - wound(t_from))


def make_field_trace(windows):
    """The driving field along the top of the diagram, on its own time axis.

    Built the way make_strain_trace builds h(t), and for the same reason:
    sharing the x axis with the diagram is the point, so a leg and the stretch
    of the oscillation it was excited during stand in the same column and can
    be read off against each other. The curve is the bare sine at a drawing
    amplitude, carrying the shape and not the size.

    `windows` are the (start, end) of the stretches to wash in, one per leg.
    They go uncaptioned: which arm is excited is already on the page in the
    arm colours and in the marker riding the curve, and a caption under each
    wash only repeats it in words. Returns the curve, those washes, and the
    three pulse markers separately, so a scene can bring each one on at the
    moment it is earned.
    """
    def at(t):
        return [t, DM_TRACE_Z + DM_TRACE_AMPLITUDE * dm_field(t), 0]

    zero = DashedLine(
        [DM_TRACE_X[0], DM_TRACE_Z, 0], [DM_TRACE_X[1], DM_TRACE_Z, 0],
        **GUIDE_STYLE,
    )
    curve = ParametricFunction(
        at, t_range=[*DM_TRACE_X, 0.02],
        color=FIELD_COLOR, stroke_width=FIELD_STROKE_WIDTH,
    )
    tag = MathTex(
        r"\delta\omega_A/\omega_A", font_size=FONT_LEGEND, color=FIELD_COLOR
    ).next_to(curve, RIGHT, buff=0.2)

    top = DM_TRACE_Z + DM_TRACE_AMPLITUDE + 0.2
    bottom = DM_TRACE_Z - DM_TRACE_AMPLITUDE - 0.2
    bands = VGroup()
    for t_from, t_to in windows:
        bands.add(Rectangle(
            width=t_to - t_from, height=top - bottom, **FIELD_WINDOW_STYLE
        ).move_to([0.5 * (t_from + t_to), 0.5 * (top + bottom), 0]))

    dots = VGroup(*[
        Dot(at(CP_T0 + k * CP_T), radius=0.07, color=LASER_COLOR) for k in range(3)
    ])
    return VGroup(zero, curve, tag), bands, dots


def field_marker(now):
    """A dot riding the trace at the instant the level diagram is showing.

    The one thing that ties the two halves of the figure together: without it
    the trace is a curve and the level diagram is a level, and nothing on the
    page says they are the same number.
    """
    def at():
        t = now.get_value()
        return [t, DM_TRACE_Z + DM_TRACE_AMPLITUDE * dm_field(t), 0]

    return always_redraw(
        lambda: Dot(at(), radius=0.08, color=lighten(KICKED_COLOR))
    )


def dm_upper(now, center=DM_LEVELS, scale=1.0):
    """Where |e> sits at time `now`, with the field dragging omega_A around."""
    return center + UP * scale * (
        DM_LEVEL_GAP / 2 + DM_LEVEL_SWING * dm_field(now.get_value())
    )


def make_modulated_levels(now, center=DM_LEVELS, scale=1.0, text_scale=1.0):
    """The clock transition with omega_A modulated, against a fixed laser.

    Everything that moves is an always_redraw off `now`, so the diagram is a
    readout of the same time coordinate the interferometer below it runs on:
    advance `now` over a leg and the level walks over exactly the stretch of
    the oscillation that leg integrated.

    The kets go left of the levels rather than right, which is where the
    single-photon diagram puts them, because the right-hand side is the
    laser's: its arrow, its label, and the detuning bar all live over there
    and the two sides then read as atom and light. Between them stands the
    gap arrow with omega_A beside it, which is the quantity the two sides
    disagree about.

    `scale` stretches the geometry and `text_scale` the labels, separately, so
    a diagram given more room grows without its kets outgrowing the page.
    """
    s, ts = scale, text_scale
    half = RIGHT * s * DM_LEVEL_LENGTH / 2
    lower = center + DOWN * s * DM_LEVEL_GAP / 2
    resonant = center + UP * s * DM_LEVEL_GAP / 2  # where the laser was tuned

    level_g = Line(
        lower - half, lower + half, color=ATOM_COLOR, stroke_width=LEVEL_STROKE_WIDTH
    )
    ket_g = state_label(r"|g\rangle", ATOM_COLOR, FONT_STATE * ts).next_to(
        level_g, LEFT, buff=DM_KET_BUFF * ts
    )
    def moving():
        """|e>, its ket and the gap arrow, wherever the field has put them."""
        top = dm_upper(now, center, s)
        return VGroup(
            Line(
                top - half, top + half,
                color=KICKED_COLOR, stroke_width=LEVEL_STROKE_WIDTH,
            ),
            state_label(r"|e\rangle", KICKED_COLOR, FONT_STATE * ts).next_to(
                top - half, LEFT, buff=DM_KET_BUFF * ts
            ),
            DoubleArrow(
                lower + RIGHT * s * DM_GAP_X + UP * DM_LEVEL_INSET,
                top + RIGHT * s * DM_GAP_X + DOWN * DM_LEVEL_INSET,
                **LEVEL_GAP_ARROW_STYLE,
            ),
            # Beside the arrow rather than under the diagram: the arrow is
            # what is changing length, so the name belongs on it, and it then
            # rides up and down with the level as well.
            MathTex(
                r"\omega_A", font_size=FONT_LEGEND * ts, color=lighten(GUIDE_COLOR)
            ).next_to(
                0.5 * (lower + top) + RIGHT * s * DM_GAP_X, RIGHT,
                buff=DM_GAP_LABEL_BUFF * ts,
            ),
        )

    # The laser: one arrow, tuned to the unmodulated transition, and never
    # redrawn. It is resonant only as the field crosses zero, which is the
    # whole point of drawing it fixed. Double-ended because it is a
    # frequency being compared against another, not a photon going one way --
    # the single-photon diagram's one-way glow is the arrow for that.
    laser = DoubleArrow(
        lower + RIGHT * s * DM_LASER_X + UP * DM_LEVEL_INSET,
        resonant + RIGHT * s * DM_LASER_X + DOWN * DM_LEVEL_INSET,
        **LEVEL_GLOW_ARROW_STYLE,
    )
    resonance = DashedLine(resonant - half, resonant + half, **LEVEL_RESONANCE_STYLE)
    laser_label = MathTex(
        r"\omega_L", font_size=FONT_LEGEND * ts, color=LASER_COLOR
    ).next_to(lower + RIGHT * s * DM_MARK_X + UP * s * 0.45, RIGHT, buff=0.06 * ts)

    def detuning():
        """delta = omega_L - omega_A(t), drawn where it actually opens up."""
        offset = (dm_upper(now, center, s) - resonant)[1]
        if abs(offset) < 0.04 * s:
            return VGroup()
        foot = resonant + RIGHT * s * DM_MARK_X
        bar = Line(foot, foot + UP * offset, color=LASER_COLOR, stroke_width=2)
        label = MathTex(
            r"\delta", font_size=FONT_LEGEND * ts, color=LASER_COLOR
        ).next_to(foot + UP * 0.5 * offset, RIGHT, buff=0.08 * ts)
        group = VGroup(bar, label)
        group.set_opacity(min(1.0, abs(offset) / (0.5 * s * DM_LEVEL_SWING)))
        return group

    # The two halves are handed back as builders rather than as live
    # always_redraws so that a scene can fade a still of the whole diagram in
    # as one thing. An always_redraw rebuilds itself every frame and rewrites
    # its own opacity with it, so it cannot be faded: added straight, the
    # level and its arrow would snap on after the rest had arrived.
    static = VGroup(level_g, ket_g, laser, resonance, laser_label)
    return static, moving, detuning
