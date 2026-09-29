"""The AION DAI data built up shot by shot.

The same shots as aionanim.plots.dai_fringes (Baynham et al.,
arXiv:2504.09158, Fig. 4a,b), drawn in manim so they can arrive one at a time.
The fringe plot on the left sweeps left to right through the clock laser phase
step; each shot lands on it twice -- once per interferometer -- and once on the
Lissajous plot on the right, as upper against lower excitation. The newest shot
is ringed in all three places so the eye can follow one shot across.

FringesToEllipse is the quiet laser: clean fringes, and the ellipse traced
round in order as the phase sweeps. FringesToEllipseNoisy is the run with
common laser phase noise put on: the fringes wash out to a band, but each shot
still lands on the ellipse, just at a random place round it.

FringesFirst (and FringesFirstNoisy) start from the finished fringe plot,
dimmed, and light its shots up left to right as each arrives on the Lissajous
plot -- for when the fringes have already been shown and the point is where
each one goes on the ellipse.

LaserNoiseLissajous is the two runs as one figure, after Fig. 4 itself: the
quiet run lights up across a full-size fringe plot, then shrinks to the top
panel to make room for the noisy one, whose shots land on the same Lissajous
plot -- on top of the quiet ellipse, and on the same curve.

    uv run manim -qh src/aionanim/scenes/dai_data.py FringesToEllipse

Drawing: a few thousand Dots would be a few thousand mobjects for cairo to
walk every frame. Instead each series is one VMobject whose points are every
dot's circle laid end to end -- cairo draws them as subpaths of a single path
-- and an updater slices off as many dots as have arrived. That makes the
point count nearly free, so nothing is down-sampled beyond taking the same
first shots the static figure plots.
"""

import csv

import numpy as np
from manim import *

from aionanim.resources import data_path
from aionanim.style import *

DATA_DIR = data_path("dai_fringes")

# The first shots of the run, as many as the static Lissajous figure plots
# (~20 per phase step), sorted by phase step so the fringe plot fills left to
# right. Within a step they keep shot order.
N_SHOTS = 2000

# --- layout ---------------------------------------------------------------
FRINGE_ORIGIN = np.array([-6.0, -2.6, 0.0])  # lower-left corner of the axes
FRINGE_WIDTH = 6.2
FRINGE_HEIGHT = 4.2
LISSAJOUS_ORIGIN = np.array([1.9, -2.6, 0.0])
LISSAJOUS_SIZE = 4.2

# --- pacing ---------------------------------------------------------------
# Ease in, so the first shots arrive slowly enough to be followed one at a
# time and the rest fill in quickly.
BUILD_TIME = 6.0
SHRINK_TIME = 1.5

# --- LaserNoiseLissajous: the fringe panels stacked -----------------------
# The quiet run's panel shrinks to the top slot; the noisy run's comes in
# below. The top panel keeps its tick labels but not the x-axis label, which
# the bottom panel carries for both.
STACK_HEIGHT = 2.0
STACK_UPPER_ORIGIN = np.array([-6.0, 0.45, 0.0])
STACK_LOWER_ORIGIN = FRINGE_ORIGIN


def load(run):
    with open(DATA_DIR / f"{run}.csv") as f:
        rows = list(csv.DictReader(line for line in f if not line.startswith("#")))
    data = {k: np.array([float(r[k]) for r in rows[:N_SHOTS]]) for k in rows[0]}
    order = np.argsort(data["phi_rad"], kind="stable")
    return {k: v[order] for k, v in data.items()}


def plot_axes(x_range, x_length, y_length, x_ticks, x_label, y_label):
    axes = Axes(
        x_range=x_range,
        y_range=[0, 100, 50],
        x_length=x_length,
        y_length=y_length,
        tips=False,
        axis_config=dict(
            color=PLOT_FOREGROUND, stroke_width=2, tick_size=0.06,
            include_ticks=True,
        ),
        # the x ticks are MathTex set below, so the origin's 0 is the y axis's
        y_axis_config=dict(numbers_to_include=[0, 50, 100],
                           font_size=FONT_TICK, numbers_to_exclude=[]),
        x_axis_config=dict(include_numbers=False),
    )
    """Axes, tick labels and axis labels, as (axes, frame).

    The frame is (axes, x tick labels, y label, x label), x label last so a
    panel that loses it can transform the rest. x_label=None leaves it empty.
    """
    ticks = VGroup(*(
        MathTex(tex, font_size=FONT_TICK, color=PLOT_FOREGROUND)
        .next_to(axes.c2p(x, 0), DOWN, buff=0.18)
        for x, tex in x_ticks
    ))
    axes.y_axis.numbers.set_color(PLOT_FOREGROUND)
    yl = Tex(y_label, font_size=FONT_AXIS, color=PLOT_FOREGROUND).rotate(PI / 2)
    yl.next_to(axes.y_axis.numbers, LEFT, buff=0.2)
    xl = VGroup()
    if x_label is not None:
        xl = Tex(x_label, font_size=FONT_AXIS, color=PLOT_FOREGROUND)
        xl.next_to(ticks, DOWN, buff=0.18).set_x(axes.x_axis.get_center()[0])
    return axes, VGroup(axes, ticks, yl, xl)


def fringe_plot(y_length, origin, x_label=True):
    axes, frame = plot_axes(
        [0, TAU, PI], FRINGE_WIDTH, y_length,
        [(0, "0"), (PI, r"\pi"), (TAU, r"2\pi")],
        "Clock laser phase step / rad" if x_label else None,
        r"Excitation / \%",
    )
    frame.shift(origin - axes.c2p(0, 0))
    return axes, frame


def lissajous_plot():
    axes, frame = plot_axes(
        [0, 100, 50], LISSAJOUS_SIZE, LISSAJOUS_SIZE,
        [(0, "0"), (50, "50"), (100, "100")],
        r"Lower interferometer excitation / \%",
        r"Upper interferometer excitation / \%",
    )
    frame.shift(LISSAJOUS_ORIGIN - axes.c2p(0, 0))
    return axes, frame


def dot_points(axes, xs, ys):
    """Every dot's circle, end to end, in the order the dots arrive."""
    template = Circle(radius=DATA_DOT_RADIUS, num_components=5).points
    centres = np.array([axes.c2p(x, y) for x, y in zip(xs, ys)])
    return (centres[:, None, :] + template[None, :, :]).reshape(-1, 3), len(template)


def dot_cloud(points, per_dot, color, count, opacity):
    cloud = VMobject(fill_color=color, fill_opacity=opacity, stroke_width=0)

    def grow(mob):
        n = int(count.get_value())
        # set_points on an empty array leaves cairo nothing to draw, which is
        # what zero dots should look like.
        mob.set_points(points[: n * per_dot])

    cloud.add_updater(grow)
    return cloud


def static_cloud(points, color, opacity):
    return VMobject(fill_color=color, fill_opacity=opacity,
                    stroke_width=0).set_points(points)


def fringe_series(axes, data):
    """(points, per_dot, colour) for each interferometer's fringe."""
    return [
        (*dot_points(axes, data["phi_rad"], 100 * data[key]), color)
        for key, color in (("excitation_bottom", LOWER_CLOUD_COLOR),
                           ("excitation_top", UPPER_CLOUD_COLOR))
    ]


def arriving_shots(data, fringe_axes, liss_axes, ellipse_color, count,
                   dim=False):
    """Every layer one run's shots are drawn in, all driven by ``count``.

    Returns (clouds, rings, dimmed): the growing lower-fringe, upper-fringe and
    ellipse clouds, a ring on the newest shot in each, and -- with ``dim`` --
    the whole fringe plot drawn faintly underneath for the clouds to light up.
    """
    liss = dot_points(liss_axes, 100 * data["excitation_bottom"],
                      100 * data["excitation_top"])
    series = [(*s, FRINGE_DOT_OPACITY) for s in fringe_series(fringe_axes, data)]
    series.append((*liss, ellipse_color, 1.0))
    clouds, rings, dimmed = VGroup(), VGroup(), VGroup()
    for points, per_dot, color, opacity in series:
        clouds.add(dot_cloud(points, per_dot, color, count, opacity))
        centres = points[::per_dot] - [DATA_DOT_RADIUS, 0, 0]
        rings.add(newest_ring(centres, lighten(color), count))
    if dim:
        dimmed.add(*(static_cloud(points, color, FRINGE_DIM_OPACITY)
                     for points, _, color in fringe_series(fringe_axes, data)))
    return clouds, rings, dimmed


def build(scene, count, clouds, rings):
    """Play one run's shots in, left to right, then freeze them."""
    scene.add(clouds)
    scene.wait(0.3)
    count.set_value(1)
    scene.add(rings)
    scene.play(count.animate.set_value(N_SHOTS), run_time=BUILD_TIME,
               rate_func=rate_functions.ease_in_quad)
    scene.play(FadeOut(rings), run_time=0.6)
    for cloud in clouds:
        cloud.clear_updaters()


def newest_ring(centres, color, count):
    ring = Circle(radius=NEWEST_RING_RADIUS, stroke_color=color,
                  stroke_width=NEWEST_RING_WIDTH)
    ring.add_updater(
        lambda m: m.move_to(centres[max(int(count.get_value()) - 1, 0)])
    )
    return ring


def legend_row(entries):
    rows = VGroup(*(
        VGroup(
            Dot(radius=0.07, color=color),
            Tex(label, font_size=FONT_AXIS, color=PLOT_FOREGROUND),
        ).arrange(RIGHT, buff=0.12)
        for label, color in entries
    ))
    return rows.arrange(RIGHT, buff=0.4)


def fringe_key():
    return legend_row([("Lower", LOWER_CLOUD_COLOR),
                       ("Upper", UPPER_CLOUD_COLOR)])


def over_panel(title, key, axes):
    """A panel's title over its left end and the fringe key over its right."""
    title.next_to(axes, UP, buff=0.3).align_to(axes, LEFT)
    if key is not None:
        key.match_y(title).align_to(axes, RIGHT)


class FringesToEllipse(Scene):
    RUN = "lln"
    TITLE = "Low laser noise"
    ELLIPSE_COLOR = LLN_COLOR
    # Whether the whole fringe plot is up, dimmed, before any shot arrives.
    FRINGES_FIRST = False

    def beat(self):
        """The pause after each step: nothing here, a click on the slide version."""

    def construct(self):
        fringe_axes, fringe_frame = fringe_plot(FRINGE_HEIGHT, FRINGE_ORIGIN)
        liss_axes, liss_frame = lissajous_plot()
        title = Tex(self.TITLE, font_size=FONT_TITLE, color=self.ELLIPSE_COLOR)
        title.to_corner(UL)
        key = fringe_key()
        key.next_to(fringe_axes, UP, buff=0.25).align_to(fringe_axes, RIGHT)

        count = ValueTracker(0)
        clouds, rings, dimmed = arriving_shots(
            load(self.RUN), fringe_axes, liss_axes, self.ELLIPSE_COLOR, count,
            dim=self.FRINGES_FIRST,
        )
        self.play(FadeIn(title), FadeIn(fringe_frame), FadeIn(liss_frame),
                  FadeIn(key), FadeIn(dimmed), run_time=1.0)
        self.beat()
        build(self, count, clouds, rings)
        self.wait(2.0)


class Noisy:
    RUN = "hln"
    TITLE = "High laser noise"
    ELLIPSE_COLOR = HLN_COLOR


class FringesToEllipseNoisy(Noisy, FringesToEllipse):
    pass


class FringesFirst(FringesToEllipse):
    FRINGES_FIRST = True


class FringesFirstNoisy(Noisy, FringesFirst):
    pass


class LaserNoiseLissajous(Scene):
    def beat(self):
        """The pause after each step: nothing here, a click on the slide version."""

    def construct(self):
        quiet, noisy = load("lln"), load("hln")
        liss_axes, liss_frame = lissajous_plot()

        # --- the quiet run, full size
        big_axes, big_frame = fringe_plot(FRINGE_HEIGHT, FRINGE_ORIGIN)
        quiet_title = Tex("Low laser noise", font_size=FONT_AXIS, color=LLN_COLOR)
        key = fringe_key()
        over_panel(quiet_title, key, big_axes)
        # The panel titles are in the run colours, so they already key the
        # ellipse; this repeats it where the ellipse is, in its empty corner.
        runs_key = VGroup(*(
            VGroup(Dot(radius=0.07, color=color),
                   Tex(label, font_size=FONT_TICK, color=PLOT_FOREGROUND))
            .arrange(RIGHT, buff=0.12)
            for label, color in (("Low laser noise", LLN_COLOR),
                                 ("High laser noise", HLN_COLOR))
        )).arrange(DOWN, buff=0.15, aligned_edge=LEFT)
        runs_key.next_to(liss_axes.c2p(0, 100), DR, buff=0.25)

        count = ValueTracker(0)
        clouds, rings, dimmed = arriving_shots(
            quiet, big_axes, liss_axes, LLN_COLOR, count, dim=True
        )
        self.play(FadeIn(quiet_title), FadeIn(key), FadeIn(big_frame),
                  FadeIn(dimmed), FadeIn(liss_frame), FadeIn(runs_key[0]),
                  run_time=1.0)
        self.beat()
        build(self, count, clouds, rings)
        self.wait(1.0)
        self.beat()

        # --- shrink it to the top panel
        top_axes, top_frame = fringe_plot(
            STACK_HEIGHT, STACK_UPPER_ORIGIN, x_label=False
        )
        lit = fringe_series(top_axes, quiet)
        moves = [Transform(big_frame[:3], top_frame[:3]),
                 FadeOut(big_frame[3])]
        for layer, opacity in ((clouds, FRINGE_DOT_OPACITY),
                               (dimmed, FRINGE_DIM_OPACITY)):
            moves += [
                Transform(mob, static_cloud(points, color, opacity))
                for mob, (points, _, color) in zip(layer[:2], lit)
            ]
        for mob in (quiet_title, key):
            mob.generate_target()
        over_panel(quiet_title.target, key.target, top_axes)
        moves += [MoveToTarget(quiet_title), MoveToTarget(key)]
        self.play(*moves, run_time=SHRINK_TIME)

        # --- the noisy run below it, onto the same ellipse
        low_axes, low_frame = fringe_plot(STACK_HEIGHT, STACK_LOWER_ORIGIN)
        noisy_title = Tex("High laser noise", font_size=FONT_AXIS,
                          color=HLN_COLOR)
        over_panel(noisy_title, None, low_axes)
        count = ValueTracker(0)
        clouds, rings, dimmed = arriving_shots(
            noisy, low_axes, liss_axes, HLN_COLOR, count, dim=True
        )
        self.play(FadeIn(noisy_title), FadeIn(low_frame), FadeIn(dimmed),
                  FadeIn(runs_key[1]), run_time=1.0)
        self.beat()
        build(self, count, clouds, rings)
        self.wait(2.0)
