"""A long-baseline atom gradiometer in cartoon, for a static slide.

A vertical vacuum shaft with the clock laser running its whole length, and
atom interferometers spaced along it, each fed from a strontium source on the
shaft's side: the source's atoms are carried into the beam, launched upwards
and fall back through it. The baseline L is the distance between the
outermost interferometers, and is what the double arrow beside the shaft
marks. Drawn after the usual sketch of a MAGIS/AION-type detector, with the
beam entering from both ends.
"""

import numpy as np
from manim import *

from manim_atoms.aion.style import *
from manim_atoms.trapping.tools.cooling import chevron
from manim_atoms.core.primitives import make_cloud

BL_SHAFT_WIDTH = 0.75  # between the walls' centres
BL_BEAM_WIDTH = 0.42
BL_END_MARGIN = 0.75  # shaft end to the nearest interferometer: clear of the beam's chevrons
BL_SOURCE_SIZE = (0.6, 0.48)
BL_SOURCE_GAP = 0.45  # source box to the shaft wall: the transfer tube
BL_TUBE_WIDTH = 0.16
BL_CLOUD_RADIUS = 0.14
BL_CLOUD_N = 26
BL_CLOUD_DOT_RADIUS = 0.032  # finer than a cartoon cloud's, at this size
BL_LAUNCH_HEIGHT = 0.45  # how high the launch loop climbs above its cloud
BL_LAUNCH_WIDTH = 0.16  # the loop's spread across the beam
BL_ARROW_GAP = 0.35  # shaft wall to the baseline arrow


def launch_loop(cloud_center, height=BL_LAUNCH_HEIGHT, width=BL_LAUNCH_WIDTH,
                color=ATOM_COLOR):
    """Up from the cloud, over the top and back down: the fountain launch,
    with an arrowhead on the way down."""
    c = np.array(cloud_center, dtype=float)
    up_x, down_x = c[0] - width / 2, c[0] + width / 2
    turn = c[1] + height - width / 2  # where the loop stops rising
    path = VMobject(stroke_color=color, stroke_width=LAUNCH_STROKE_WIDTH)
    path.set_points_as_corners([np.array([up_x, c[1], 0]), np.array([up_x, turn, 0])])
    top = Arc(radius=width / 2, start_angle=PI, angle=-PI,
              arc_center=np.array([c[0], turn, 0]))
    path.append_points(top.points)
    end = np.array([down_x, c[1] + BL_CLOUD_RADIUS + 0.05, 0])
    path.add_line_to(end)
    tip = chevron(DOWN, end, color, size=0.07).set_stroke(width=LAUNCH_STROKE_WIDTH)
    return VGroup(path, tip)


def source(port, label=r"Sr"):
    """An atom source on the shaft's left: a box, a transfer tube from it to
    ``port`` on the wall, and its atoms' path along the tube."""
    port = np.array(port, dtype=float)
    tube_start = port + LEFT * BL_SOURCE_GAP
    box = Rectangle(width=BL_SOURCE_SIZE[0], height=BL_SOURCE_SIZE[1])
    box.move_to(tube_start, aligned_edge=RIGHT)
    box.set_stroke(SHAFT_COLOR, SOURCE_STROKE_WIDTH)
    tube = VGroup(*[
        Line(tube_start + sign * UP * BL_TUBE_WIDTH / 2,
             port + sign * UP * BL_TUBE_WIDTH / 2)
        for sign in (1, -1)
    ]).set_stroke(SHAFT_COLOR, SOURCE_STROKE_WIDTH)
    atoms = make_cloud(box.get_center(), ATOM_COLOR, n=8, radius=0.1, seed=99)
    for dot in atoms:
        dot.scale(BL_CLOUD_DOT_RADIUS / CARTOON_CLOUD_DOT_RADIUS)
    name = Tex(label, font_size=FONT_SOURCE, color=lighten(GUIDE_COLOR))
    name.next_to(box, UP, buff=0.08).align_to(box, LEFT)
    return VGroup(box, tube, atoms, name)


def make_baseline(bottom, top, n=4, label=r"1\,\mathrm{km}", x=0.0):
    """The shaft from ``bottom`` to ``top`` (heights), centred on ``x``, with
    ``n`` interferometers evenly along it and the baseline arrow labelled
    ``label``. Returns a VGroup; its parts are named attributes too."""
    left, right = x - BL_SHAFT_WIDTH / 2, x + BL_SHAFT_WIDTH / 2
    heights = np.linspace(bottom + BL_END_MARGIN, top - BL_END_MARGIN, n)

    beam = Rectangle(width=BL_BEAM_WIDTH, height=top - bottom, stroke_width=0,
                     fill_color=LASER_COLOR, fill_opacity=BASELINE_BEAM_OPACITY)
    beam.move_to([x, 0.5 * (bottom + top), 0])
    heads = VGroup(
        chevron(UP, np.array([x, bottom + 0.25, 0]), LASER_COLOR, size=BL_BEAM_WIDTH * 0.4),
        chevron(DOWN, np.array([x, top - 0.25, 0]), LASER_COLOR, size=BL_BEAM_WIDTH * 0.4),
    ).set_stroke(opacity=MOT_BEAM_EDGE_OPACITY)

    # the left wall is broken where each source's tube comes through
    gaps = sorted((h - BL_TUBE_WIDTH / 2, h + BL_TUBE_WIDTH / 2) for h in heights)
    edges = [bottom, *[e for g in gaps for e in g], top]
    walls = VGroup(
        *[Line([left, edges[i], 0], [left, edges[i + 1], 0])
          for i in range(0, len(edges), 2)],
        Line([right, bottom, 0], [right, top, 0]),
    ).set_stroke(SHAFT_COLOR, SHAFT_WALL_WIDTH)

    sources = VGroup(*[source([left, h, 0]) for h in heights])
    clouds = VGroup(*[
        make_cloud([x, h, 0], ATOM_COLOR, n=BL_CLOUD_N, radius=BL_CLOUD_RADIUS, seed=i)
        for i, h in enumerate(heights)
    ])
    for dot in clouds.family_members_with_points():
        dot.scale(BL_CLOUD_DOT_RADIUS / CARTOON_CLOUD_DOT_RADIUS)
    loops = VGroup(*[launch_loop([x, h, 0]) for h in heights])

    arrow = DoubleArrow(
        [right + BL_ARROW_GAP, heights[0], 0], [right + BL_ARROW_GAP, heights[-1], 0],
        buff=0, stroke_width=4, color=lighten(GUIDE_COLOR),
        max_tip_length_to_length_ratio=0.05,
    )
    tag = MathTex(label, font_size=FONT_ANNOTATION).next_to(arrow, RIGHT, buff=0.15)

    group = VGroup(beam, heads, walls, sources, clouds, loops, arrow, tag)
    group.beam, group.walls, group.sources = VGroup(beam, heads), walls, sources
    group.clouds, group.loops, group.arrow, group.tag = clouds, loops, arrow, tag
    return group
