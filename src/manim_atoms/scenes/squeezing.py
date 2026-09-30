"""Spin squeezing: a cavity measurement takes the phase below the shot-noise limit.

Right, the collective spin of N atoms: a Bloch sphere with the mean spin on
its equator, and the patch round its tip zoomed in on, J_z = (N_e - N_g)/2
up and the phase across. The coherent state's noise disc, 1/sqrt(N) wide, is the standard
quantum limit. Left, the atoms in an optical cavity tuned to the 689 nm
line: coupled to the atoms in |g>, its line splits in two, 2 g sqrt(N_g)
apart -- the vacuum Rabi splitting -- and measuring the splitting counts
them without flipping any, a quantum non-demolition measurement of J_z
(Chen et al., PRL 106, 133601 (2011)). Knowing J_z squeezes the disc
along it; a rotation about the mean spin turns the squeezing onto the phase.

    uv run manim -qh src/aionanim/scenes/squeezing.py SpinSqueezing

Four beat()s: the coherent state, the cavity measurement, the squeezed state,
the rotation onto the phase.
"""

import numpy as np
from manim import *

from aionanim.style import *
from aionanim.tools.layout import slide_title
from aionanim.tools.squeezing import (
    cavity_atoms,
    rabi_transmission,
    make_bloch,
    make_cavity,
    noise_blob,
)

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

# Right column: the patch round the tip of the collective spin, zoomed in,
# and the Bloch sphere it comes from on its right, the spin pointing back
# towards it so the zoom lines don't cross the sphere.
SQ_BLOCH = np.array([6.15, 1.25, 0.0])
SQ_BLOCH_RADIUS = 0.72
SQ_TIP_ANGLE = -55 * DEGREES
SQ_PLANE = np.array([2.95, 0.4, 0.0])
SQ_PLANE_HALF = 1.75
SQ_INSET_BLOB = 0.1  # the noise disc on the sphere, much magnified already
SQ_SQL_RADIUS = 0.8  # the coherent state's disc, on the zoomed plane
# The squeezed state: J_z known to xi of the coherent width, the phase blurred
# by more than the coherent state's -- a real measurement is not lossless, so
# the stretch more than makes up the squeeze.
SQ_XI = 0.3
SQ_ANTI = 1.5
SQ_MEASURED = 0.4  # the J_z this shot's measurement happened to give


class SpinSqueezing(Scene):
    """The coherent state, a cavity measurement of J_z, and the squeezed state
    it leaves, turned onto the phase."""

    def beat(self):
        """The pause after each step: nothing here, a click on the slide version."""

    def construct(self):
        # --- 1. the collective spin and its shot noise ---------------------
        title = slide_title(r"Spin squeezing: below the shot-noise limit")

        sphere, spin, tip = make_bloch(SQ_BLOCH, SQ_BLOCH_RADIUS, SQ_TIP_ANGLE)
        inset_blob = noise_blob(SQ_INSET_BLOB).move_to(tip)

        frame = Square(side_length=2 * SQ_PLANE_HALF, **BLOCH_STYLE).move_to(SQ_PLANE)
        zoom = VGroup(*[
            DashedLine(inset_blob.get_left(), corner, **ZOOM_STYLE)
            for corner in (frame.get_corner(UR), frame.get_corner(DR))
        ])
        axes = VGroup(
            Line(SQ_PLANE + DOWN * SQ_PLANE_HALF, SQ_PLANE + UP * SQ_PLANE_HALF),
            Line(SQ_PLANE + LEFT * SQ_PLANE_HALF, SQ_PLANE + RIGHT * SQ_PLANE_HALF),
        ).set_stroke(GUIDE_COLOR, 1.5, opacity=0.6)
        # J_z = (N_e - N_g)/2, labelled as the count it is
        jz_label = MathTex(r"N_e - N_g", font_size=FONT_AXIS, color=PLOT_FOREGROUND)
        jz_label.next_to(frame.get_top(), DR, buff=0.1)
        phi_label = MathTex(r"\phi", font_size=FONT_AXIS, color=PLOT_FOREGROUND)
        phi_label.next_to(frame.get_right(), UL, buff=0.1)

        blob = noise_blob(SQ_SQL_RADIUS).move_to(SQ_PLANE)
        state_name = Tex(r"coherent state", font_size=FONT_LEGEND,
                         color=lighten(COHERENT_COLOR))
        state_name.next_to(frame, UP, buff=0.15).align_to(frame, LEFT)

        def phi_span(center_x, half, color):
            """A double arrow across the phase resolution, under the frame."""
            y = SQ_PLANE[1] - SQ_PLANE_HALF - 0.22
            return DoubleArrow(
                [center_x - half, y, 0], [center_x + half, y, 0], buff=0,
                stroke_width=3, color=color, tip_length=0.15,
                max_tip_length_to_length_ratio=0.3,
            )

        sql_span = phi_span(SQ_PLANE[0], SQ_SQL_RADIUS, lighten(COHERENT_COLOR))
        sql = MathTex(r"\Delta\phi_\mathrm{SQL} = \frac{1}{\sqrt{N}}",
                      font_size=FONT_ANNOTATION, color=lighten(COHERENT_COLOR))
        sql.next_to(frame, DOWN, buff=0.5).align_to(frame, LEFT)
        sql_note = Tex(r"$N$ atoms, each\\projected on its own",
                       font_size=FONT_TICK, color=lighten(GUIDE_COLOR))
        sql_note.next_to(sql, RIGHT, buff=0.4)

        self.play(
            FadeIn(title), FadeIn(sphere), GrowArrow(spin), FadeIn(inset_blob),
            run_time=0.8,
        )
        self.play(
            *[Create(z) for z in zoom], FadeIn(frame), FadeIn(axes),
            FadeIn(jz_label), FadeIn(phi_label),
            run_time=0.8,
        )
        self.play(
            FadeIn(blob), FadeIn(state_name), GrowFromCenter(sql_span),
            FadeIn(sql), FadeIn(sql_note),
            run_time=0.8,
        )
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
        empty_label = Tex(r"empty", font_size=FONT_TICK, color=lighten(GUIDE_COLOR))
        empty_label.next_to(plot.c2p(SQ_EMPTY + 0.2, 0.75), RIGHT, buff=0.1)

        self.play(
            FadeIn(mirrors), FadeIn(mode), FadeIn(detector), GrowArrow(probe[0]),
            GrowArrow(probe[1]), FadeIn(probe_label), FadeIn(cavity_label),
            FadeIn(plot), FadeIn(x_label), FadeIn(y_label), FadeIn(empty),
            FadeIn(empty_label), FadeIn(loaded),
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

        # --- 3. J_z known: the disc squeezes along it ----------------------
        reference = DashedVMobject(
            Circle(radius=SQ_SQL_RADIUS).move_to(SQ_PLANE), num_dashes=30,
        ).set_stroke(**COHERENT_OUTLINE_STROKE)
        measured_at = SQ_PLANE + UP * SQ_MEASURED
        measured = DashedLine(
            measured_at + LEFT * SQ_PLANE_HALF, measured_at + RIGHT * SQ_PLANE_HALF,
            **MEASURED_STYLE,
        )
        measured_label = Tex(r"measured", font_size=FONT_TICK, color=lighten(PROBE_COLOR))
        measured_label.next_to(measured, LEFT, buff=0.12)
        squeezed = (
            noise_blob(SQ_SQL_RADIUS, SQUEEZED_COLOR)
            .stretch(SQ_XI, 1).stretch(SQ_ANTI, 0).move_to(measured_at)
        )
        squeezed_name = Tex(r"squeezed state", font_size=FONT_LEGEND,
                            color=lighten(SQUEEZED_COLOR)).move_to(state_name, aligned_edge=LEFT)
        inset_squeezed = (
            noise_blob(SQ_INSET_BLOB, SQUEEZED_COLOR)
            .stretch(SQ_XI, 1).stretch(SQ_ANTI, 0).move_to(tip)
        )
        self.add(reference)
        self.play(Create(measured), FadeIn(measured_label), run_time=0.6)
        self.play(
            Transform(blob, squeezed), Transform(inset_blob, inset_squeezed),
            FadeTransform(state_name, squeezed_name),
            run_time=1.5,
        )
        self.beat()

        # --- 4. turn the squeezing onto the phase --------------------------
        # A rotation about the mean spin turns the whole plane about its
        # centre, the measured value with it: it becomes a known phase offset.
        turn = Tex(r"rotate about the mean spin", font_size=FONT_TICK,
                   color=lighten(GUIDE_COLOR))
        turn.next_to(frame.get_corner(DL), UR, buff=0.12).shift(UP * 0.35)
        self.play(FadeOut(measured_label), FadeIn(turn), run_time=0.4)
        self.play(
            Rotate(VGroup(blob, measured), PI / 2, about_point=SQ_PLANE),
            Rotate(inset_blob, PI / 2),
            run_time=1.5,
        )
        offset = blob.get_center()[0]
        squeezed_span = phi_span(offset, SQ_XI * SQ_SQL_RADIUS, lighten(SQUEEZED_COLOR))
        gain = MathTex(r"\Delta\phi = \frac{\xi}{\sqrt{N}},\ \xi < 1",
                       font_size=FONT_ANNOTATION, color=lighten(SQUEEZED_COLOR))
        gain.next_to(sql, DOWN, buff=0.2, aligned_edge=LEFT)
        self.play(
            ReplacementTransform(sql_span.copy(), squeezed_span),
            sql_span.animate.set_opacity(0.4),
            FadeOut(sql_note),
            sql.animate.set_opacity(0.5),
            FadeIn(gain),
            FadeOut(turn),
            run_time=1.0,
        )
        self.wait(1.5)
