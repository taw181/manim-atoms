"""HiFAIS: a high-flux source of cold strontium, and the MOT it loads.

Walker et al., AVS Quantum Sci. 8, 033201 (2026). The chamber first, from
its CAD (Fig. 1c,d): top view and side view, labelled. Then the side view
goes and the top view moves over to make room for the loading curves of
Fig. 5's inset: the oven feeds the 2D MOT, the Zeeman slowing beam comes down
the oven's arm against the atoms, and the push beam carries them on into the
science chamber, where the 3D MOT fills while the curves draw out -- all four
oven temperatures at once, against one lab clock in ms. Last, the initial
slope of the hottest run: the 4e10 atoms/s of the title.

    uv run manim -qh src/aionanim/scenes/hifais.py HighFluxLoading

The atoms in the 3D MOT are the hottest run's: as many of the cloud's dots
are lit as its fitted N(t) says, of its N at the end of the run.
"""

import numpy as np
from manim import *

from aionanim.physics.mot_loading import load_loading_curves, load_loading_fits, loading_model
from aionanim.style import *
from aionanim.tools.cooling import AtomBeam, make_push_beam
from aionanim.tools.hifais import (
    CHAMBER_SIDE,
    CHAMBER_TOP,
    LOAD_T_MAX,
    SIDE_PUMP,
    SIDE_SCIENCE,
    SIDE_SOURCE,
    TOP_2D_MOT,
    TOP_3D_MOT,
    TOP_ARM_END,
    TOP_LEFT_EDGE,
    TOP_OVEN,
    TOP_SCIENCE_RIM,
    at,
    chamber_label,
    chamber_view,
    loading_axes,
    loading_cutoff,
    loading_fit,
    loading_points,
    loading_rate_line,
    temperature_key,
)
from aionanim.tools.primitives import make_cloud

# --- layout ---------------------------------------------------------------
VIEW_HEIGHT = 4.9
TOP_VIEW_AT = np.array([-3.45, -0.3, 0.0])  # both views side by side
SIDE_VIEW_AT = np.array([3.35, -0.3, 0.0])
TOP_VIEW_BESIDE_PLOT = np.array([-3.85, -0.3, 0.0])  # with the plot
PLOT_ORIGIN = np.array([1.15, -2.45, 0.0])  # the axes' lower-left corner
PLOT_SIZE = (5.4, 4.3)
SLOW_BEAM_OVERSHOOT = 0.45  # how far above the render the slowing beam starts
PUSH_BEAM_OVERSHOOT = 0.3

# --- the atoms ------------------------------------------------------------
MOT_CLOUD_N = 90
MOT_CLOUD_RADIUS = 0.28
SOURCE_CLOUD_N = 40
SOURCE_CLOUD_RADIUS = 0.16
OVEN_STREAM = dict(speed=2.5, rate=14, spread=0.05, divergence=0.1)
# Fast enough to cross to the 3D MOT in about the fitted onset time (~3 ms of
# lab time at LOAD_RUN_TIME), which is what the onset is: the push beam's
# atoms in flight.
PUSH_STREAM = dict(speed=6.0, rate=16, spread=0.04, divergence=0.01)

# --- pacing ---------------------------------------------------------------
LOAD_RUN_TIME = 8.0  # wall seconds for LOAD_T_MAX of lab time


class HighFluxLoading(Scene):
    def beat(self):
        """The pause after each step: nothing here, a click on the slide version."""

    def construct(self):
        curves, fits = load_loading_curves(), load_loading_fits()
        hottest = max(fits)

        # --- the chamber, top and side
        title = Tex(r"A high-flux source of cold strontium", font_size=FONT_TITLE)
        title.to_corner(UL)
        top = chamber_view(CHAMBER_TOP, VIEW_HEIGHT).move_to(TOP_VIEW_AT)
        side = chamber_view(CHAMBER_SIDE, VIEW_HEIGHT).move_to(SIDE_VIEW_AT)
        captions = VGroup(*(
            Tex(text, font_size=FONT_CHAMBER_CAPTION, color=lighten(GUIDE_COLOR))
            .next_to(view, DOWN, buff=0.15)
            for text, view in (("from above", top), ("from the side", side))
        ))
        top_labels = VGroup(
            chamber_label(r"Sr oven", at(top, TOP_OVEN), LEFT, 0.9),
            chamber_label(r"source chamber", at(top, TOP_2D_MOT) + UP * 0.25, UR, 1.3),
            chamber_label(r"science chamber", at(top, TOP_SCIENCE_RIM), DR, 0.5),
        )
        side_labels = VGroup(
            chamber_label(r"source chamber", at(side, SIDE_SOURCE), UL, 0.6),
            chamber_label(r"science chamber", at(side, SIDE_SCIENCE), UP, 0.9),
            chamber_label(r"pump", at(side, SIDE_PUMP), LEFT, 0.8),
        )
        self.play(FadeIn(title), FadeIn(top), FadeIn(side), FadeIn(captions),
                  FadeIn(top_labels), FadeIn(side_labels), run_time=1.0)
        self.beat()

        # --- the top view beside the plot
        self.play(FadeOut(side), FadeOut(side_labels), FadeOut(captions),
                  FadeOut(top_labels), run_time=0.6)
        self.play(top.animate.move_to(TOP_VIEW_BESIDE_PLOT), run_time=1.0)

        mot2d, mot3d = at(top, TOP_2D_MOT), at(top, TOP_3D_MOT)
        slow_from = at(top, TOP_ARM_END) + UP * SLOW_BEAM_OVERSHOOT
        slow_beam = make_push_beam(TRANSITION_461_COLOR, slow_from, at(top, TOP_OVEN))
        push_from = at(top, TOP_LEFT_EDGE) + LEFT * PUSH_BEAM_OVERSHOOT
        push_beam = make_push_beam(TRANSITION_461_COLOR, push_from, mot3d)
        beam_labels = VGroup(
            Tex(r"Zeeman slowing beam", font_size=FONT_CHAMBER_LABEL,
                color=TRANSITION_461_COLOR).next_to(slow_from, RIGHT, buff=0.3),
            Tex(r"push beam", font_size=FONT_CHAMBER_LABEL, color=TRANSITION_461_COLOR)
            .next_to(push_from, UR, buff=0.25),
        )
        for label in beam_labels:
            label.set_stroke(PLOT_BACKGROUND, width=5, background=True)
        source_cloud = make_cloud(mot2d, TRANSITION_461_COLOR, n=SOURCE_CLOUD_N,
                                  radius=SOURCE_CLOUD_RADIUS, seed=3)
        mot_cloud = make_cloud(mot3d, TRANSITION_461_COLOR, n=MOT_CLOUD_N,
                               radius=MOT_CLOUD_RADIUS, seed=4)
        cloud_labels = VGroup(
            chamber_label(r"2D MOT", mot2d + UR * 0.12, UR, 0.7),
            chamber_label(r"3D MOT", mot3d + UP * 0.25, UP, 0.8),
        )
        oven_stream = AtomBeam(at(top, TOP_OVEN), mot2d,
                               (HOT_ATOM_COLOR, TRANSITION_461_COLOR), **OVEN_STREAM)
        push_stream = AtomBeam(mot2d, mot3d, (TRANSITION_461_COLOR, TRANSITION_461_COLOR),
                               **PUSH_STREAM)

        axes, frame = loading_axes(*PLOT_SIZE)
        frame.shift(PLOT_ORIGIN - axes.c2p(0, 0))
        key = temperature_key(list(curves))
        key.next_to(axes, UP, buff=0.35).align_to(axes, RIGHT)
        cutoff = loading_cutoff(axes)

        clock = ValueTracker(0.0)  # lab time, ms
        n_end = loading_model(LOAD_T_MAX, fits[hottest])

        def fill(cloud):
            share = loading_model(clock.get_value(), fits[hottest]) / n_end
            lit = int(round(MOT_CLOUD_N * np.clip(share, 0, 1)))
            for i, dot in enumerate(cloud):
                dot.set_opacity(1.0 if i < lit else 0.0)

        mot_cloud.add_updater(fill)
        fill(mot_cloud)

        oven_stream.flow.set_value(1)
        self.add(oven_stream, push_stream)
        self.play(FadeIn(slow_beam), FadeIn(push_beam), FadeIn(beam_labels),
                  FadeIn(source_cloud), FadeIn(cloud_labels), FadeIn(mot_cloud),
                  FadeIn(frame), FadeIn(key), FadeIn(cutoff), run_time=1.0)
        self.wait(1.0)  # the oven stream reaches the 2D MOT
        self.beat()

        # --- loading: every run at once, against one lab clock
        data = VGroup()
        for (temperature, run), color in zip(curves.items(), OVEN_TEMPERATURE_COLORS):
            data.add(loading_fit(axes, fits[temperature], color, clock),
                     loading_points(axes, run, color, clock))
        self.add(data)
        push_stream.flow.set_value(1)
        self.play(clock.animate.set_value(LOAD_T_MAX), run_time=LOAD_RUN_TIME,
                  rate_func=linear)
        self.wait(0.5)
        self.beat()

        # --- the loading rate
        hot_color = OVEN_TEMPERATURE_COLORS[-1]
        slope = loading_rate_line(axes, fits[hottest], hot_color)
        rate = fits[hottest]["rate"]
        mantissa, exponent = f"{rate * 1e9:.1e}".split("e")
        rate_tag = VGroup(
            MathTex(rf"{mantissa}\times10^{{{int(exponent)}}}", font_size=FONT_ANNOTATION),
            Tex(r"atoms/s", font_size=FONT_AXIS),
        ).arrange(DOWN, buff=0.1, aligned_edge=LEFT).set_color(lighten(hot_color))
        # in the curves' empty upper left, above the line's end and ending short
        # of the hottest run's dashed fit
        rate_tag.next_to(slope.get_end(), UP, buff=0.12)
        rate_tag.set_x(axes.c2p(0, 0)[0] + 0.2, direction=LEFT)  # the axis, not its numbers
        rate_tag.set_stroke(PLOT_BACKGROUND, width=5, background=True)
        self.play(Create(slope), run_time=0.8)
        self.play(FadeIn(rate_tag, shift=RIGHT * 0.15), run_time=0.6)
        self.wait(1.5)
