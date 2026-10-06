"""Rabi oscillations on the Sr clock transition: the Bloch vector and P_e together.

Left, one atom's state on the Bloch sphere, |e> up: a laser resonant with the
698 nm 1S0 -> 3P0 line turns it about the drive vector Omega, which lies in
the equator, so from |g> it swings over the top to |e> and back down. Right,
the same motion read off as the excited-state population, P_e = sin^2(Omega t / 2),
traced in step with the tip; above it, the two levels, with the transition
lit up the way the atom is being driven -- upward while it absorbs, downward
while stimulated emission hands the photons back to the beam.

The pulse areas the interferometers are built from fall out of it: pi/2 leaves
the atom on the equator, an equal superposition (the beamsplitter), pi takes
it all the way to |e> (the mirror). The flopping does not decay, because the
clock state lives for minutes -- its linewidth is about a millihertz. Last,
the same drive detuned by Delta = Omega: the axis tilts towards |e>, the
vector turns faster, at Omega' = sqrt(Omega^2 + Delta^2), round a smaller
circle, and P_e never gets past Omega^2 / Omega'^2 = 1/2.

    uv run manim -qh src/manim_atoms/interferometry/scenes/rabi.py RabiOscillations

beat()s: the atom in |g>; the pi/2 pulse; the pi pulse; the free flopping;
the detuned drive.
"""

import numpy as np
from manim import *

from manim_atoms.interferometry.style import *
from manim_atoms.core.layout import slide_title
from manim_atoms.core.primitives import state_label
from manim_atoms.interferometry.tools.rabi import (
    bloch_vector,
    drive_axis,
    excited_population,
    is_absorbing,
)
from manim_atoms.interferometry.tools.squeezing import BlochView
from manim_atoms.species.two_level import (
    SP_LEVEL_GAP,
    make_level_diagram,
    resonance_line,
    transition_glow,
)

# --- Rabi geometry ----------------------------------------------------------
# Left: the Bloch sphere, seen from a little above the equator. The drive
# vector points towards the viewer and left, so the circle the tip sweeps on
# resonance -- the plane through the poles at right angles to it -- is seen
# as an ellipse, its front half solid and its back half dashed, rather than
# edge on or flat against the outline.
RB_BLOCH = np.array([-4.3, -0.15, 0.0])
RB_BLOCH_RADIUS = 2.0
RB_DRIVE_AZIMUTH = -50 * DEGREES
# Right: the population against pulse area, under the level diagram.
RB_PLOT = np.array([2.85, -1.55, 0.0])  # centre of the axes
RB_PLOT_SIZE = (6.4, 2.5)
RB_AREA_MAX = 4 * PI  # pulse area across the axes: two full flops
RB_LEVELS = np.array([0.9, 1.75, 0.0])  # centre of the two-level gap
RB_FORMULA = np.array([3.4, 2.0, 0.0])  # left edge of the formulas
RB_CAPTION_Y = -3.55
# The detuned run: Delta = Omega, which caps P_e at 1/2. On the level diagram
# the laser line drops below |e> by this much -- schematic, not to scale.
RB_DETUNING = 1.0
RB_DETUNING_DRAWN = 0.5
# Pacing: wall seconds per pi of pulse area.
RB_SECONDS_PER_PI = 1.6


class RabiOscillations(Scene):
    """A resonant drive flopping one Sr atom between |g> and |e>, on the Bloch
    sphere and as P_e(t), then the same drive detuned."""

    def beat(self):
        """The pause after each step: nothing here, a click on the slide version."""

    def construct(self):
        # --- 1. the atom in |g>, the drive off -----------------------------
        title = slide_title(r"Rabi oscillations on the Sr clock transition")

        view = BlochView(RB_BLOCH, RB_BLOCH_RADIUS)
        up = np.array([0.0, 0.0, 1.0])
        outline = view.outline()
        equator = view.curve(view.ring(up), lighten(GUIDE_COLOR), 2)
        axis = DashedLine(view.point(-up), view.point(up), **BLOCH_AXIS_STYLE)
        poles = VGroup(
            state_label(r"|e\rangle", KICKED_COLOR, FONT_LEGEND)
            .next_to(outline, UP, buff=0.1),
            state_label(r"|g\rangle", ATOM_COLOR, FONT_LEGEND)
            .next_to(outline, DOWN, buff=0.1),
        )
        sphere = VGroup(outline, axis, equator, poles)

        # area is the pulse area Omega t of the run in progress, detuning its
        # Delta / Omega; on is 1 while the laser is on, fading the drive's
        # marks in and out.
        area, detuning = ValueTracker(0.0), ValueTracker(0.0)

        def tip():
            return bloch_vector(area.get_value(), RB_DRIVE_AZIMUTH, detuning.get_value())

        def pe():
            return excited_population(area.get_value(), detuning.get_value())

        def state_color():
            return interpolate_color(ATOM_COLOR, KICKED_COLOR, pe())

        vector = always_redraw(lambda: Arrow(
            view.center, view.point(tip()), **BLOCH_VECTOR_STYLE))
        tip_dot = always_redraw(lambda: Dot(
            view.point(tip()), radius=BLOCH_TIP_RADIUS, color=state_color()))

        def trace(d):
            """The tip's path on the sphere so far, for detuning d."""
            def draw():
                a = area.get_value()
                n = max(2, int(a / RB_AREA_MAX * 400))
                pts = [bloch_vector(s, RB_DRIVE_AZIMUTH, d) for s in np.linspace(0, a, n)]
                return view.curve(pts, RABI_TRACE_COLOR, RABI_TRACE_WIDTH)
            return always_redraw(draw)

        levels = make_level_diagram(RB_LEVELS, gap_tex=r"698\,\mathrm{nm}")
        level_names = VGroup(
            MathTex(r"{}^3P_0", font_size=FONT_LEGEND, color=lighten(KICKED_COLOR))
            .next_to(levels[1], LEFT, buff=0.2),
            MathTex(r"{}^1S_0", font_size=FONT_LEGEND, color=lighten(ATOM_COLOR))
            .next_to(levels[0], LEFT, buff=0.2),
        )

        width, height = RB_PLOT_SIZE
        plot = Axes(
            x_range=[0, RB_AREA_MAX, PI], y_range=[0, 1.0, 0.5],
            x_length=width, y_length=height, tips=False,
            axis_config=dict(color=PLOT_FOREGROUND, stroke_width=2,
                             tick_size=0.06),
        ).move_to(RB_PLOT)
        x_ticks = VGroup(*[
            MathTex(tex, font_size=FONT_TICK, color=PLOT_FOREGROUND)
            .next_to(plot.c2p(x, 0), DOWN, buff=0.15)
            for x, tex in [(PI / 2, r"\tfrac{\pi}{2}"), (PI, r"\pi"), (2 * PI, r"2\pi"),
                           (3 * PI, r"3\pi"), (4 * PI, r"4\pi")]
        ])
        y_ticks = VGroup(*[
            MathTex(tex, font_size=FONT_TICK, color=PLOT_FOREGROUND)
            .next_to(plot.c2p(0, y), LEFT, buff=0.15)
            for y, tex in [(0, "0"), (0.5, r"\tfrac12"), (1, "1")]
        ])
        x_label = MathTex(r"\Omega t", font_size=FONT_AXIS, color=PLOT_FOREGROUND)
        x_label.next_to(plot.x_axis, RIGHT, buff=0.3)  # clear of the end dot
        y_label = MathTex(r"P_e", font_size=FONT_AXIS, color=PLOT_FOREGROUND)
        y_label.next_to(plot.y_axis, UP, buff=0.15)
        # P_e = 1 drawn faint across the axes, so "all the way" and "only
        # half way" are read off against something.
        full = DashedLine(plot.c2p(0, 1), plot.c2p(RB_AREA_MAX, 1),
                          **PULSE_AREA_MARK_STYLE)
        axes = VGroup(plot, x_ticks, y_ticks, x_label, y_label, full)

        def curve(d):
            """P_e so far, for detuning d, with a dot riding its end."""
            def draw():
                a = max(area.get_value(), 1e-3)
                line = plot.plot(lambda s: excited_population(s, d), x_range=[0, a, 0.02],
                                 color=RABI_TRACE_COLOR, stroke_width=RABI_CURVE_WIDTH)
                return VGroup(line, Dot(plot.c2p(a, excited_population(a, d)),
                                        radius=BLOCH_TIP_RADIUS, color=state_color()))
            return always_redraw(draw)

        resonant = MathTex(r"P_e = \sin^2\frac{\Omega t}{2}", font_size=FONT_ANNOTATION,
                           color=lighten(KICKED_COLOR))
        resonant.move_to(RB_FORMULA, aligned_edge=LEFT)

        self.play(FadeIn(title), FadeIn(sphere), FadeIn(levels), FadeIn(level_names),
                  FadeIn(axes), run_time=1.0)
        self.play(GrowArrow(vector), FadeIn(tip_dot), run_time=0.6)
        self.add(vector, tip_dot)
        caption = self.caption(r"the atom starts in the ground state, $|g\rangle$")
        self.play(FadeIn(caption), run_time=0.5)
        self.beat()

        # --- 2. the laser on: the pi/2 pulse ------------------------------
        # The glow on the level diagram points the way photons are going:
        # up while P_e climbs, down once stimulated emission takes over.
        on = ValueTracker(0.0)
        glow = always_redraw(lambda: transition_glow(
            is_absorbing(area.get_value(), detuning.get_value()), RB_LEVELS,
            RB_DETUNING_DRAWN * detuning.get_value() / RB_DETUNING,
        ).set_opacity(on.get_value()))
        drive_tip = lambda: view.point(drive_axis(RB_DRIVE_AZIMUTH, detuning.get_value()))
        drive = always_redraw(lambda: Arrow(
            view.center, drive_tip(), **DRIVE_VECTOR_STYLE).set_opacity(on.get_value()))
        drive_label = always_redraw(lambda: MathTex(
            r"\Omega'" if detuning.get_value() > 0.5 else r"\Omega",
            font_size=FONT_ANNOTATION, color=LASER_COLOR,
        # below the tip on the equator, where LEFT would sit on the outline;
        # beside it once tilted up, where below would sit on the shaft
        ).next_to(drive_tip(), LEFT if detuning.get_value() > 0.5 else DOWN, buff=0.12)
        .set_opacity(on.get_value()))
        rabi_label = MathTex(r"\Omega", font_size=FONT_ANNOTATION, color=LASER_COLOR)
        rabi_label.next_to(levels[4], LEFT, buff=0.12)
        # the run in progress: tip path and population curve
        sweep, pop = trace(0.0), curve(0.0)
        self.add(sweep, pop, glow, drive, drive_label)
        self.bring_to_front(vector, tip_dot)
        self.play(on.animate.set_value(1.0), FadeIn(rabi_label), FadeIn(resonant),
                  run_time=0.6)

        mark_half = self.run_to(area, PI / 2, plot, r"\pi/2", caption,
                                r"$\pi/2$ pulse: an equal superposition of $|g\rangle$ "
                                r"and $|e\rangle$ -- the beamsplitter")
        caption = mark_half[-1]
        self.beat()

        # --- 3. the pi pulse ----------------------------------------------
        mark_pi = self.run_to(area, PI, plot, r"\pi", caption,
                              r"$\pi$ pulse: every atom in $|e\rangle$ -- the mirror")
        caption = mark_pi[-1]
        self.beat()

        # --- 4. left on: it flops, and does not decay ---------------------
        self.play(area.animate.set_value(RB_AREA_MAX), rate_func=linear,
                  run_time=(RB_AREA_MAX - PI) / PI * RB_SECONDS_PER_PI)
        undamped = self.caption(r"no decay between flops: ${}^3P_0$ lives for minutes "
                                r"(linewidth ${\sim}1\,$mHz)")
        self.play(FadeOut(caption), FadeIn(undamped), on.animate.set_value(0.0),
                  run_time=0.6)
        caption = undamped
        self.beat()

        # --- 5. detuned by Delta = Omega ----------------------------------
        # The resonant run stays up, dimmed, as the reference; a fresh atom
        # in |g> is driven round the tilted axis.
        done = VGroup(sweep.copy().clear_updaters(), pop[0].copy())
        self.remove(sweep, pop)
        self.add(done)
        self.bring_to_front(vector, tip_dot)
        self.play(done.animate.set_stroke(opacity=RABI_DONE_OPACITY),
                  FadeOut(mark_half[:-1]), FadeOut(mark_pi[:-1]), run_time=0.5)
        self.play(area.animate.set_value(0.0), run_time=0.8)

        laser_line = resonance_line(RB_DETUNING_DRAWN, RB_LEVELS)
        delta = MathTex(r"\Delta", font_size=FONT_LEGEND, color=LASER_COLOR)
        # in the gap it names, between the laser's line and |e>, left of the glow
        delta.move_to(RB_LEVELS + UP * (SP_LEVEL_GAP - RB_DETUNING_DRAWN) / 2 + LEFT * 0.3)
        detuned = MathTex(
            r"P_e = \frac{\Omega^2}{\Omega'^2}\sin^2\frac{\Omega' t}{2}",
            font_size=FONT_ANNOTATION, color=lighten(KICKED_COLOR),
        ).move_to(RB_FORMULA, aligned_edge=LEFT)
        generalized = MathTex(r"\Omega' = \sqrt{\Omega^2 + \Delta^2}",
                              font_size=FONT_LEGEND, color=LASER_COLOR)
        generalized.next_to(detuned, DOWN, buff=0.2, aligned_edge=LEFT)
        off = self.caption(r"detuned by $\Delta = \Omega$: faster, round a tilted axis, "
                           r"and never past $P_e = \tfrac12$")
        detuning.set_value(RB_DETUNING)
        sweep, pop = trace(RB_DETUNING), curve(RB_DETUNING)
        self.add(sweep, pop)
        self.bring_to_front(vector, tip_dot)
        self.play(
            Create(laser_line), FadeIn(delta),
            FadeTransform(resonant, detuned), FadeIn(generalized),
            FadeOut(caption), FadeIn(off),
            on.animate.set_value(1.0),
            run_time=0.8,
        )
        self.play(area.animate.set_value(RB_AREA_MAX), rate_func=linear,
                  run_time=RB_AREA_MAX / PI * RB_SECONDS_PER_PI)
        self.play(on.animate.set_value(0.0), run_time=0.5)
        self.wait(1.5)

    def caption(self, text):
        """The line under the figure saying what the step has shown."""
        return Tex(text, font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR)).move_to(
            [0, RB_CAPTION_Y, 0])

    def run_to(self, area, to, plot, label, old_caption, text):
        """Drive on to pulse area ``to``, then mark it on the curve and say
        what it did. Returns (guide, dot, label, caption)."""
        self.play(area.animate.set_value(to), rate_func=linear,
                  run_time=(to - area.get_value()) / PI * RB_SECONDS_PER_PI)
        p = excited_population(to)
        guide = DashedLine(plot.c2p(to, 0), plot.c2p(to, p), **PULSE_AREA_MARK_STYLE)
        dot = Dot(plot.c2p(to, p), radius=PULSE_AREA_DOT_RADIUS,
                  color=lighten(RABI_TRACE_COLOR))
        name = MathTex(label, font_size=FONT_LEGEND, color=lighten(RABI_TRACE_COLOR))
        name.next_to(dot, UR, buff=0.05)
        caption = self.caption(text)
        self.play(Create(guide), FadeIn(dot), FadeIn(name),
                  FadeOut(old_caption), FadeIn(caption), run_time=0.6)
        return VGroup(guide, dot, name, caption)
