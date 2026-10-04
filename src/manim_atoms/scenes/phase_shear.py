"""Phase-shear readout: one image of the cloud gives the interferometer phase.

Sugarbaker et al., PRL 111, 113002 (2013). Left, the expanded cloud at the
last pi/2 pulse, a row of atoms each carrying its phase as a clock hand, with
the pulse drawn as a beam so its wavefronts show. Right, what the camera sees
of the two output ports, and the excited fraction across the cloud.

Square on, every wavefront crosses the whole cloud at once: every atom gets
the same phase, the ports are two smooth blobs, and one shot gives a single
number, P_e = (1 - C cos Phi) / 2 -- blind to the sign of Phi and mixed up
with the contrast. Tilt the pulse by theta and the wavefronts cross the cloud
Lambda = lambda / theta apart: the hands fan out across it, the ports come
out striped, and where the stripes sit gives Phi from the one image.

    uv run manim -qh src/manim_atoms/scenes/phase_shear.py PhaseShearReadout
"""

import numpy as np
from manim import *

from manim_atoms.style import *
from manim_atoms.tools.clock import make_clock_hand
from manim_atoms.tools.phase_shear import (
    PortImage,
    excited_fraction,
    make_beam,
    phase_reading,
    shear_phase,
)
from manim_atoms.tools.primitives import make_atom, make_k_arrow, state_label

# --- phase-shear geometry -------------------------------------------------
# Left half: the cloud, a row of atoms at CLOUD, and the beam rising to it.
CLOUD = np.array([-3.5, 0.5, 0.0])
N_ATOMS = 9
ATOM_SPACING = 0.7  # clears two clock atoms side by side
BEAM_WIDTH = 6.5
BEAM_BELOW = 5.0  # off the bottom of the frame, tilted or not
BEAM_ABOVE = 1.2
# The tilt, exaggerated by a couple of hundred times so it can be seen at all
# (the real one is ~1 mrad), and the wavefront spacing that makes the drawn
# wavefronts cross the row one fringe period apart: two across the cloud.
TILT = 12 * DEGREES
FRINGE = 2.8  # Lambda, on screen
SPACING = FRINGE * np.sin(TILT)
ANGLE_RADIUS = 1.9  # of the arc marking theta, round the cloud's centre
K_ARROW_DEPTH = 3.3  # how far under the cloud the k marker rides the beam
SPAN_DROP = 0.6  # the fringe period's arrow, under the row

# Right half: the two ports imaged, e over g, and the profile under them, all
# on one x axis across the cloud.
PANEL_X = 3.75
IMAGE_WIDTH = 5.4
IMAGE_HEIGHT = 1.0
IMAGE_E_Y = 2.55
IMAGE_G_Y = 1.3
X_RANGE = (-3.0, 3.0)  # of the cloud, in the row's units, across an image
CLOUD_SIGMA = 1.2
PLOT_ORIGIN_Y = -3.0
PLOT_HEIGHT = 2.2
N_BINS = 25

PHI = 1.2  # the interferometer phase


class PhaseShearReadout(Scene):
    """The last pulse square on, then tilted: the fringes it writes on the cloud."""

    def beat(self):
        """The pause after each step: nothing here, a click on the slide version."""

    def construct(self):
        theta = ValueTracker(0.0)

        def phase(x):
            return shear_phase(x, theta.get_value(), PHI, SPACING)

        # --- 1. the cloud at the last pulse, square on --------------------
        title = Tex(r"Phase-shear readout", font_size=FONT_TITLE).to_corner(UL)
        caption = Tex(
            r"expanded cloud at the last $\pi/2$ pulse",
            font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR),
        ).next_to(title, DOWN, buff=0.25, aligned_edge=LEFT)

        beam = make_beam(CLOUD, BEAM_WIDTH, BEAM_BELOW, BEAM_ABOVE, SPACING)
        beam.add(make_k_arrow(CLOUD[0] + 0.35, CLOUD[1] - K_ARROW_DEPTH))

        offsets = (np.arange(N_ATOMS) - (N_ATOMS - 1) / 2) * ATOM_SPACING
        atoms = VGroup(*[
            make_atom(radius=CLOCK_ATOM_RADIUS).move_to(CLOUD + RIGHT * dx)
            for dx in offsets
        ])
        hands = VGroup(*[
            make_clock_hand(atom, phase_reading(lambda dx=dx: phase(dx)))
            for atom, dx in zip(atoms, offsets)
        ])
        phase_label = MathTex(r"\phi(x) = \Phi", font_size=FONT_ANNOTATION)
        phase_label.next_to(atoms, UP, buff=0.45)

        self.play(FadeIn(title), FadeIn(caption), FadeIn(beam), run_time=0.8)
        self.play(FadeIn(atoms), FadeIn(hands), FadeIn(phase_label), run_time=0.8)
        self.beat()

        # --- 2. what the camera sees: one number ---------------------------
        images = Group()
        for color, share, y, ket in (
            (KICKED_COLOR, lambda x: excited_fraction(phase(x)), IMAGE_E_Y, r"|e\rangle"),
            (ATOM_COLOR, lambda x: 1 - excited_fraction(phase(x)), IMAGE_G_Y, r"|g\rangle"),
        ):
            image = PortImage(color, X_RANGE, CLOUD_SIGMA).paint(share)
            image.stretch_to_fit_width(IMAGE_WIDTH).stretch_to_fit_height(IMAGE_HEIGHT)
            image.move_to([PANEL_X, y, 0])
            image.share = share
            border = SurroundingRectangle(image, buff=0, **SHEAR_IMAGE_BORDER_STYLE)
            label = state_label(ket, color).next_to(border, LEFT, buff=0.2)
            images.add(Group(image, border, label))

        # counted from the image's left edge, so the P_e axis stands there
        # rather than up the middle of the cloud
        axes = Axes(
            x_range=[0, X_RANGE[1] - X_RANGE[0], 1],
            y_range=[0, 1, 0.5],
            x_length=IMAGE_WIDTH,
            y_length=PLOT_HEIGHT,
            tips=False,
            axis_config=dict(color=PLOT_FOREGROUND, stroke_width=2),
            y_axis_config=dict(include_ticks=True),
            x_axis_config=dict(include_ticks=False),
        )
        axes.move_to([PANEL_X, PLOT_ORIGIN_Y + PLOT_HEIGHT / 2, 0])
        y_label = MathTex(r"P_e", font_size=FONT_AXIS, color=lighten(KICKED_COLOR))
        y_label.next_to(axes.y_axis, LEFT, buff=0.2)
        x_label = MathTex(r"x", font_size=FONT_AXIS, color=PLOT_FOREGROUND)
        x_label.next_to(axes.x_axis, RIGHT, buff=0.15)

        def at(x, p):
            """Position x across the cloud, share p, on the plot."""
            return axes.c2p(x - X_RANGE[0], p)

        # The profile is binned off the image, so it scatters about the fringe
        # more out in the wings, where there are fewer atoms to count.
        bins = np.linspace(X_RANGE[0] + 0.5, X_RANGE[1] - 0.5, N_BINS)
        weight = np.exp(-bins**2 / (2 * CLOUD_SIGMA**2))
        draws = np.clip(np.random.default_rng(3).normal(size=N_BINS), -1.5, 1.5)
        noise = 0.02 * draws / np.sqrt(weight)

        def place_dots(dots):
            for dot, x, dy in zip(dots, bins, noise):
                dot.move_to(at(x, np.clip(excited_fraction(phase(x)) + dy, 0, 1)))

        data = VGroup(*[
            Dot(radius=SHEAR_DATA_DOT_RADIUS, color=lighten(KICKED_COLOR))
            for _ in bins
        ])
        data.add_updater(place_dots, call_updater=True)
        fit = always_redraw(lambda: axes.plot(
            lambda u: excited_fraction(phase(u + X_RANGE[0])),
            x_range=[0, X_RANGE[1] - X_RANGE[0], 0.02],
            color=KICKED_COLOR,
            stroke_width=SHEAR_PROFILE_WIDTH,
        ))
        formula = MathTex(
            r"P_e = \tfrac{1}{2}\left(1 - C\cos\Phi\right)", font_size=FONT_ANNOTATION
        ).move_to([PANEL_X, (IMAGE_G_Y - IMAGE_HEIGHT / 2 + axes.get_top()[1]) / 2, 0])

        self.play(
            *[FadeIn(g) for g in images],
            FadeIn(axes), FadeIn(y_label), FadeIn(x_label),
            FadeIn(data), FadeIn(fit), FadeIn(formula),
            run_time=0.8,
        )
        # only once they are up: a fade would paint over the redraws
        for group in images:
            image = group[0]
            image.add_updater(lambda m: m.paint(m.share))
        self.beat()

        # --- 3. tilt the pulse: the phase shears across the cloud ----------
        sheared_label = MathTex(
            r"\phi(x) = \Phi + k\theta\, x", font_size=FONT_ANNOTATION
        ).move_to(phase_label)
        sheared_formula = MathTex(
            r"P_e(x) = \tfrac{1}{2}\left(1 - C\cos\phi(x)\right)",
            font_size=FONT_ANNOTATION,
        ).move_to(formula)
        tilted_caption = Tex(
            r"last $\pi/2$ pulse tilted by $\theta$ against the others",
            font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR),
        ).move_to(caption, aligned_edge=LEFT)
        vertical = DashedLine(CLOUD, CLOUD + DOWN * (ANGLE_RADIUS + 0.6), **GUIDE_STYLE)
        self.add(vertical)
        self.play(
            Rotate(beam, -TILT, about_point=CLOUD),
            theta.animate.set_value(TILT),
            TransformMatchingTex(phase_label, sheared_label),
            TransformMatchingTex(formula, sheared_formula),
            FadeTransform(caption, tilted_caption),
            run_time=3.0,
        )
        arc = Arc(
            radius=ANGLE_RADIUS, start_angle=-PI / 2, angle=-TILT,
            arc_center=CLOUD, stroke_width=2, color=lighten(GUIDE_COLOR),
        )
        theta_label = MathTex(r"\theta", font_size=FONT_ANNOTATION, color=lighten(GUIDE_COLOR))
        theta_label.move_to(CLOUD + (ANGLE_RADIUS + 0.35) * rotate_vector(DOWN, -TILT / 2))
        theta_label.set_stroke(PLOT_BACKGROUND, width=5, background=True)
        self.play(Create(arc), FadeIn(theta_label), run_time=0.6)

        # --- 4. the fringe period: where the wavefronts cross the cloud -----
        # straight on from the tilt, in the same click
        # between the two wavefronts that cross the row at its centre and at
        # its right-hand end, just under it
        span = DoubleArrow(
            CLOUD + DOWN * SPAN_DROP, CLOUD + DOWN * SPAN_DROP + RIGHT * FRINGE,
            buff=0, stroke_width=3, color=WHITE, tip_length=0.18,
            max_tip_length_to_length_ratio=0.1,
        )
        span_label = MathTex(r"\Lambda = \lambda/\theta", font_size=FONT_LEGEND)
        span_label.next_to(span, DOWN, buff=0.1)
        for m in (span, span_label):
            m.set_stroke(PLOT_BACKGROUND, width=5, background=True)
        scale = Tex(
            r"$\theta \sim 1$\,mrad: $\Lambda \approx 0.7$\,mm",
            font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR),
        ).next_to(tilted_caption, DOWN, buff=0.15, aligned_edge=LEFT)
        self.play(GrowFromCenter(span), FadeIn(span_label), FadeIn(scale), run_time=0.8)
        self.wait(1.5)
