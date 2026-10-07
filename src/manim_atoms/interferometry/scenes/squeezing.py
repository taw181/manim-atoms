"""Spin squeezing: a cavity measurement takes the phase below the shot-noise limit.

Right, the collective spin of N atoms: a Bloch sphere, |e> up, with the mean
spin on its equator and its quantum noise a patch of the surface round the
tip -- J_z = (N_e - N_g)/2 up the sphere, the phase round the equator. The
coherent state's patch, 1/sqrt(N) across, is the standard quantum limit. Left, the atoms in an optical cavity tuned to the 689 nm
line: coupled to the atoms in |g>, its line splits in two, 2 g sqrt(N_g)
apart -- the vacuum Rabi splitting -- and measuring the splitting counts
them without flipping any, a quantum non-demolition measurement of J_z
(Chen et al., PRL 106, 133601 (2011)). Knowing J_z squeezes the disc
along it, onto a ring of fixed J_z; a rotation about the mean spin turns the
squeezing, ring and all, onto the phase.

    uv run manim -qh src/manim_atoms/interferometry/scenes/squeezing.py SpinSqueezing

Four beat()s: the coherent state, the cavity measurement, the squeezed state,
the rotation onto the phase.
"""

import numpy as np
from manim import *

from manim_atoms.interferometry.style import *
from manim_atoms.core.layout import slide_title
from manim_atoms.core.primitives import state_label
from manim_atoms.core.bloch import BlochView, noise_patch
from manim_atoms.core.optics import make_cavity, rabi_transmission
from manim_atoms.interferometry.tools.squeezing import cavity_atoms

# --- spin-squeezing geometry ------------------------------------------------
# Left column: the cavity, and its transmission under it.
SQ_CAVITY = np.array([-3.8, 1.8, 0.0])
SQ_CAVITY_LENGTH = 3.0
SQ_MIRROR_HEIGHT = 1.4
SQ_MODE_WIDTH = 0.9
SQ_LEAD_IN = 1.3
SQ_LEAD_OUT = 0.9
SQ_CLOUD_RADIUS = 0.3
SQ_PLOT = np.array([-3.6, -0.85, 0.0])  # centre of the transmission axes
SQ_PLOT_SIZE = (4.6, 1.8)
SQ_PLOT_SPAN = 4.0  # probe frequency across the axes, in the plot's units
SQ_EMPTY = SQ_PLOT_SPAN / 2  # the cavity's resonance, and the atoms'
SQ_KAPPA = 0.25  # the cavity line's half-width
SQ_GAMMA = 0.03  # the atoms': 689 nm's 7.5 kHz is far narrower than any cavity's
SQ_COUPLING = 1.1  # g sqrt(N_g): the normal modes sit this far either side

# Right column: the Bloch sphere, looked at from a little above the equator,
# with the mean spin on the equator turned towards the viewer and right, so
# the noise round its tip is seen nearly face on.
SQ_BLOCH = np.array([4.3, 0.6, 0.0])
SQ_BLOCH_RADIUS = 1.7
SQ_TIP_AZIMUTH = 25 * DEGREES  # from the viewer, towards the right
# The coherent state's noise, as an angle on the sphere: 1/sqrt(N) for a
# handful of atoms, which is what it takes to see it.
SQ_SQL_ANGLE = 0.3
# The squeezed state: J_z known to xi of the coherent width, the phase blurred
# by more than the coherent state's -- a real measurement is not lossless, so
# the stretch more than makes up the squeeze.
SQ_XI = 0.3
SQ_ANTI = 1.5
SQ_MEASURED = 0.5 * SQ_SQL_ANGLE  # where this shot's measurement happened to land
SQ_LABELS_X = 1.1  # the left edge of the state's name and the formulas
SQ_FORMULA_Y = -1.95


class SpinSqueezing(Scene):
    """The coherent state, a cavity measurement of J_z, and the squeezed state
    it leaves, turned onto the phase."""

    def beat(self):
        """The pause after each step: nothing here, a click on the slide version."""

    def construct(self):
        # --- 1. the collective spin and its shot noise ---------------------
        title = slide_title(r"Spin squeezing: below the shot-noise limit")

        view = BlochView(SQ_BLOCH, SQ_BLOCH_RADIUS)
        up = np.array([0.0, 0.0, 1.0])
        mean = np.array([np.cos(SQ_TIP_AZIMUTH), np.sin(SQ_TIP_AZIMUTH), 0.0])
        along = np.array([-np.sin(SQ_TIP_AZIMUTH), np.cos(SQ_TIP_AZIMUTH), 0.0])  # phase

        outline = view.outline()
        equator = view.curve(view.ring(up), lighten(GUIDE_COLOR), 2)
        axis = DashedLine(view.point(-up), view.point(up), **BLOCH_AXIS_STYLE)
        poles = VGroup(
            state_label(r"|e\rangle", KICKED_COLOR, FONT_LEGEND).next_to(outline, UP, buff=0.1),
            state_label(r"|g\rangle", ATOM_COLOR, FONT_LEGEND).next_to(outline, DOWN, buff=0.1),
        )
        sphere = VGroup(outline, axis, equator, poles)

        # squeeze runs 0 to 1 from the coherent state to the squeezed one,
        # turn 0 to pi/2 as it is rotated about the mean spin
        squeeze, turn = ValueTracker(0.0), ValueTracker(0.0)

        def axes():
            """The patch's own tangent directions, turned about the mean spin:
            e1 its long one once squeezed, e2 its short one (J_z at first)."""
            psi = turn.get_value()
            return (np.cos(psi) * along + np.sin(psi) * up,
                    -np.sin(psi) * along + np.cos(psi) * up)

        def state():
            """The noise patch: its centre, the tangents there, its half-widths."""
            s = squeeze.get_value()
            e1, e2 = axes()
            d = s * SQ_MEASURED
            center = np.cos(d) * mean + np.sin(d) * e2
            e2_there = -np.sin(d) * mean + np.cos(d) * e2
            return (center, e1, e2_there,
                    SQ_SQL_ANGLE * (1 + (SQ_ANTI - 1) * s),
                    SQ_SQL_ANGLE * (1 + (SQ_XI - 1) * s))

        spin = always_redraw(lambda: Arrow(
            view.center, view.point(state()[0]), buff=0, stroke_width=3, color=WHITE,
            max_tip_length_to_length_ratio=0.12,
        ))
        blob = always_redraw(lambda: noise_patch(
            view, *state(),
            interpolate_color(COHERENT_COLOR, SQUEEZED_COLOR, squeeze.get_value()),
        ))
        state_name = Tex(r"coherent state", font_size=FONT_LEGEND,
                         color=lighten(COHERENT_COLOR))
        state_name.move_to([SQ_LABELS_X, outline.get_top()[1], 0], aligned_edge=LEFT)

        sql = MathTex(r"\Delta\phi_\mathrm{SQL} = \frac{1}{\sqrt{N}}",
                      font_size=FONT_ANNOTATION, color=lighten(COHERENT_COLOR))
        sql.move_to([SQ_LABELS_X, SQ_FORMULA_Y, 0], aligned_edge=LEFT)
        sql_note = Tex(r"$N$ atoms, each\\projected on its own",
                       font_size=FONT_TICK, color=lighten(GUIDE_COLOR))
        sql_note.next_to(sql, RIGHT, buff=0.4)

        self.play(FadeIn(title), FadeIn(sphere), run_time=0.8)
        self.play(GrowArrow(spin), run_time=0.6)
        self.add(spin)
        self.play(FadeIn(blob), FadeIn(state_name), FadeIn(sql), FadeIn(sql_note),
                  run_time=0.8)
        self.beat()

        # --- 2. the cavity counts the atoms in |g> -------------------------
        mirrors, mode, probe, detector = make_cavity(
            SQ_CAVITY, SQ_CAVITY_LENGTH, SQ_MIRROR_HEIGHT, SQ_MODE_WIDTH,
            SQ_LEAD_IN, SQ_LEAD_OUT,
        )
        atoms = cavity_atoms(SQ_CAVITY, SQ_CLOUD_RADIUS)
        probe_label = Tex(r"689\,nm probe", font_size=FONT_LEGEND, color=lighten(PROBE_COLOR))
        probe_label.next_to(mirrors, UP, buff=0.12)
        cavity_label = Tex(r"optical cavity", font_size=FONT_LEGEND,
                           color=lighten(GUIDE_COLOR))
        cavity_label.next_to(mirrors, DOWN, buff=0.15)

        width, height = SQ_PLOT_SIZE
        plot = Axes(
            x_range=[0, SQ_PLOT_SPAN, 1], y_range=[0, 1.15, 1],
            x_length=width, y_length=height, tips=False,
            axis_config=dict(color=PLOT_FOREGROUND, stroke_width=2, include_ticks=False),
        ).move_to(SQ_PLOT)
        span = [0, SQ_PLOT_SPAN, 0.02]
        x_label = Tex(r"probe frequency", font_size=FONT_AXIS, color=PLOT_FOREGROUND)
        x_label.next_to(plot.x_axis, DOWN, buff=0.15)
        y_label = Tex(r"transmission", font_size=FONT_AXIS, color=PLOT_FOREGROUND)
        y_label.rotate(PI / 2).next_to(plot.y_axis, LEFT, buff=0.15)

        empty = DashedVMobject(
            plot.plot(lambda x: rabi_transmission(x, SQ_EMPTY, SQ_KAPPA, SQ_GAMMA, 0),
                      x_range=span),
            num_dashes=40,
        ).set_stroke(**EMPTY_CAVITY_STROKE)
        coupling = ValueTracker(0.0)
        loaded = always_redraw(lambda: plot.plot(
            lambda x: rabi_transmission(x, SQ_EMPTY, SQ_KAPPA, SQ_GAMMA,
                                        coupling.get_value()),
            x_range=[0, SQ_PLOT_SPAN, 0.01], color=PROBE_COLOR,
            stroke_width=TRANSMISSION_WIDTH,
        ))

        self.play(
            FadeIn(mirrors), FadeIn(mode), FadeIn(detector), GrowArrow(probe[0]),
            GrowArrow(probe[1]), FadeIn(probe_label), FadeIn(cavity_label),
            FadeIn(plot), FadeIn(x_label), FadeIn(y_label), FadeIn(empty),
            FadeIn(loaded),
            run_time=0.8,
        )
        self.add(loaded)
        self.play(
            FadeIn(atoms, lag_ratio=0.05), coupling.animate.set_value(SQ_COUPLING),
            run_time=1.5,
        )
        # over the empty cavity's peak, from one normal mode to the other
        shift = DoubleArrow(
            plot.c2p(SQ_EMPTY - SQ_COUPLING, 1.1), plot.c2p(SQ_EMPTY + SQ_COUPLING, 1.1),
            buff=0, stroke_width=3,
            color=lighten(PROBE_COLOR), tip_length=0.15,
            max_tip_length_to_length_ratio=0.3,
        )
        shift_label = MathTex(r"2g\sqrt{N_g}", font_size=FONT_LEGEND,
                              color=lighten(PROBE_COLOR))
        shift_label.next_to(shift, UP, buff=0.08)
        qnd = Tex(
            r"vacuum Rabi splitting: the $|g\rangle$ atoms split the cavity line;\\"
            r"reading the splitting counts them without flipping any",
            font_size=FONT_TICK, color=lighten(GUIDE_COLOR),
        ).next_to(x_label, DOWN, buff=0.18)
        self.play(GrowFromCenter(shift), FadeIn(shift_label), FadeIn(qnd), run_time=0.8)
        self.beat()

        # --- 3. J_z known: the noise squeezes along it -------------------
        # The measurement pins the spin to a ring of fixed J_z; the patch
        # shrinks onto it, and stretches along it.
        reference = DashedVMobject(
            Polygon(*[view.point(v) for v in view.patch(mean, along, up, SQ_SQL_ANGLE,
                                                        SQ_SQL_ANGLE)]),
            num_dashes=30,
        ).set_stroke(**COHERENT_OUTLINE_STROKE)
        measured = always_redraw(lambda: view.curve(
            view.ring(axes()[1], np.sin(SQ_MEASURED)), PROBE_COLOR, MEASURED_WIDTH,
        ))
        measured_label = Tex(r"measured", font_size=FONT_TICK, color=lighten(PROBE_COLOR))
        measured_label.next_to(
            view.point([0, -np.cos(SQ_MEASURED), np.sin(SQ_MEASURED)]), LEFT, buff=0.12
        )
        squeezed_name = Tex(r"squeezed state", font_size=FONT_LEGEND,
                            color=lighten(SQUEEZED_COLOR)).move_to(state_name, aligned_edge=LEFT)
        self.add(reference)
        self.play(FadeIn(measured), FadeIn(measured_label), run_time=0.6)
        self.bring_to_front(blob, spin)  # the ring runs under the patch
        self.play(
            squeeze.animate.set_value(1.0),
            FadeTransform(state_name, squeezed_name),
            run_time=1.5,
        )
        self.beat()

        # --- 4. turn the squeezing onto the phase --------------------------
        # A rotation about the mean spin turns the ring of fixed J_z with the
        # patch: the measured value becomes a known phase offset.
        turn_note = Tex(r"rotate about the mean spin", font_size=FONT_TICK,
                        color=lighten(GUIDE_COLOR))
        turn_note.next_to(squeezed_name, DOWN, buff=0.15, aligned_edge=LEFT)
        self.play(FadeOut(measured_label), FadeIn(turn_note), run_time=0.4)
        self.play(turn.animate.set_value(PI / 2), run_time=1.5)
        gain = MathTex(r"\Delta\phi = \frac{\xi}{\sqrt{N}},\ \xi < 1",
                       font_size=FONT_ANNOTATION, color=lighten(SQUEEZED_COLOR))
        gain.next_to(sql, DOWN, buff=0.2, aligned_edge=LEFT)
        self.play(
            FadeOut(sql_note),
            sql.animate.set_opacity(0.5),
            FadeIn(gain),
            FadeOut(turn_note),
            run_time=1.0,
        )
        self.wait(1.5)
