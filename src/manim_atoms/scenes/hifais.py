"""HiFAIS: a high-flux source of cold strontium, and the MOT it loads.

Walker et al., AVS Quantum Sci. 8, 033201 (2026). The chamber first, from
its CAD (Fig. 1c,d): top view and side view, labelled, with the size of the
support frame it comes in. Then the side view goes and the top view moves
over to make room for the loading curves of Fig. 5's inset, with the 2D and
3D MOTs marked on it and the two distances that matter dimensioned: oven
nozzle to 2D MOT, and 2D MOT to 3D MOT. Last, the initial slope of the
hottest run: the 4e10 atoms/s of the title.

    uv run manim -qh src/aionanim/scenes/hifais.py HighFluxLoading
"""

import numpy as np
from manim import *

from aionanim.physics.mot_loading import load_loading_curves, load_loading_fits
from aionanim.style import *
from aionanim.tools.hifais import (
    CHAMBER_SIDE,
    CHAMBER_TOP,
    FRAME_MM,
    MOT_TO_MOT_MM,
    NOZZLE_TO_MOT_MM,
    SIDE_PUMP,
    SIDE_SCIENCE,
    SIDE_SOURCE,
    TOP_2D_MOT,
    TOP_3D_MOT,
    TOP_NOZZLE,
    TOP_OVEN,
    TOP_SCIENCE_RIM,
    at,
    chamber_label,
    chamber_view,
    dimension,
    loading_axes,
    loading_cutoff,
    loading_fit,
    loading_points,
    loading_rate_line,
    temperature_key,
)

# --- layout ---------------------------------------------------------------
VIEW_HEIGHT = 4.9
TOP_VIEW_AT = np.array([-3.45, -0.3, 0.0])  # both views side by side
SIDE_VIEW_AT = np.array([3.35, -0.3, 0.0])
TOP_VIEW_BESIDE_PLOT = np.array([-3.6, -0.3, 0.0])  # with the plot
TOP_VIEW_GROW = 1.1  # alone on the left, it has room to be bigger
PLOT_ORIGIN = np.array([1.15, -2.45, 0.0])  # the axes' lower-left corner
PLOT_SIZE = (5.4, 4.3)


def frame_caption():
    w, d, h = FRAME_MM
    return Tex(
        rf"support frame ${w} \times {d} \times {h}$\,mm (W $\times$ D $\times$ H)",
        font_size=FONT_CHAMBER_CAPTION, color=CHAMBER_LABEL_COLOR,
    )


class HighFluxLoading(Scene):
    def beat(self):
        """The pause after each step: nothing here, a click on the slide version."""

    def construct(self):
        curves, fits = load_loading_curves(), load_loading_fits()
        hottest = max(fits)

        # --- the chamber, top and side, and the frame it sits in
        title = Tex(r"A high-flux source of cold strontium", font_size=FONT_TITLE)
        title.to_corner(UL)
        top = chamber_view(CHAMBER_TOP, VIEW_HEIGHT).move_to(TOP_VIEW_AT)
        side = chamber_view(CHAMBER_SIDE, VIEW_HEIGHT).move_to(SIDE_VIEW_AT)
        captions = VGroup(*(
            Tex(text, font_size=FONT_CHAMBER_CAPTION, color=lighten(GUIDE_COLOR))
            .next_to(view, DOWN, buff=0.15)
            for text, view in (("from above", top), ("from the side", side))
        ))
        frame_size = frame_caption().next_to(captions, DOWN, buff=0.2).set_x(0)
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
                  FadeIn(frame_size), FadeIn(top_labels), FadeIn(side_labels),
                  run_time=1.0)
        self.beat()

        # --- the top view, dimensioned, beside the loading curves
        self.play(FadeOut(side), FadeOut(side_labels), FadeOut(captions),
                  FadeOut(top_labels), run_time=0.6)
        moved = top.copy().scale(TOP_VIEW_GROW).move_to(TOP_VIEW_BESIDE_PLOT)
        self.play(top.animate.scale(TOP_VIEW_GROW).move_to(TOP_VIEW_BESIDE_PLOT),
                  frame_size.animate.next_to(moved, DOWN, buff=0.2), run_time=1.0)

        mot2d, mot3d = at(top, TOP_2D_MOT), at(top, TOP_3D_MOT)
        # the 2D MOT's label straight up its arm, clear of both dimensions and
        # of the frame's left edge
        cloud_labels = VGroup(
            chamber_label(r"2D MOT", mot2d + UP * 0.12, UP, 1.0),
            chamber_label(r"3D MOT", mot3d + UP * 0.25, UP, 0.8),
        )
        dimensions = VGroup(
            dimension(mot2d, mot3d, rf"{MOT_TO_MOT_MM}\,mm", UP),
            dimension(at(top, TOP_NOZZLE), mot2d, rf"{NOZZLE_TO_MOT_MM}\,mm", RIGHT),
        )

        axes, frame = loading_axes(*PLOT_SIZE)
        frame.shift(PLOT_ORIGIN - axes.c2p(0, 0))
        key = temperature_key(list(curves))
        key.next_to(axes, UP, buff=0.35).align_to(axes, RIGHT)
        data = VGroup(*(
            VGroup(loading_fit(axes, fits[temperature], color),
                   loading_points(axes, run, color))
            for (temperature, run), color in zip(curves.items(), OVEN_TEMPERATURE_COLORS)
        ))
        self.play(FadeIn(cloud_labels), FadeIn(dimensions), FadeIn(frame), FadeIn(key),
                  FadeIn(loading_cutoff(axes)), FadeIn(data), run_time=1.0)
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
