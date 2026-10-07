"""How a spatial light modulator makes a tweezer array: the optical train,
what a phase mask does to the focus, how the mask is found, and how
aberrations are taken out of it.

An SLM sets the phase of the light across the beam, pixel by pixel, and
leaves its brightness alone. A lens turns that phase pattern into the
pattern of light in its focal plane, which is the Fourier transform of the
field on the SLM. Every picture of a focal plane here is computed from the
mask shown beside it (core.holography), so what the mask does is what is
seen. Phase is coloured round a wheel: 0 and 2 pi are one colour, so a mask
that wraps shows no edge.

- OpticalTrain: the SLM, the relay, the objective and the foci, side on.
  A beat() on the bare train, after the grating steers the focus, after
  the array, and after the label.
- PhaseMaskBuildingBlocks: a flat mask, a grating, a lens and a sum of
  gratings, each beside its focal plane. A beat() after each.
- HologramIteration: weighted Gerchberg-Saxton, step by step and then run
  to the end. A beat() on the loop, on the starting mask, after each of
  three iterations and after the run.
- ZernikeCorrection: the Zernike modes, an aberrated spot, and its
  correction. A beat() on the pyramid, on the aberration, after each mode
  is taken out, and after the array is corrected.

Angles in the train are exaggerated and its relay is two lenses. The
aberration is a few radians, far more than a good objective has.
"""

import numpy as np
from manim import *

from manim_atoms.tweezers.style import *
from manim_atoms.core.holography import (
    grating_phase,
    illumination,
    lens_phase,
    osa_to_nm,
    pupil_grid,
    strehl,
    uniformity,
    zernike,
)
from manim_atoms.core.optics import (
    FocalImage,
    PhaseMask,
    make_lens,
    make_slm,
    phase_wheel,
    round_aperture,
)
from manim_atoms.core.primitives import make_atom
from manim_atoms.tweezers.tools.holograms import (
    HG_GAMMA,
    HG_N,
    bar_chart,
    beamlet,
    focal_view,
    framed,
    grid_spots,
    iterate_hologram,
    panel_label,
    starting_mask,
    trace_ray,
)
from manim_atoms.tweezers.tools.tweezer_array import heading

HOLO_HEADING = np.array([-6.6, 3.6, 0.0])  # every hologram scene's heading corner
HOLO_SETTLE = 0.6  # the pause before a stop


# --- building-blocks geometry ------------------------------------------------
# The mask on the left and the focal plane it makes on the right, the same
# size, with the lens that joins them named on an arrow between.
PB_MASK = np.array([-3.4, -0.5, 0.0])
PB_FOCAL = np.array([3.4, -0.5, 0.0])
PB_SIZE = 4.4  # each picture's height
PB_WHEEL = np.array([-6.2, -2.3, 0.0])  # the phase key, beside the mask
PB_PERIODS = 7  # the grating's, across the aperture
PB_WAVES = 1.2  # the lens phase, at the aperture's edge
PB_SWEEP_TIME = 2.5


class PhaseMaskBuildingBlocks(Scene):
    """A phase mask beside the focal plane it makes: flat, a grating that
    steers the spot, a lens that defocuses it, and gratings summed into an
    array. One beat() per mask."""

    def beat(self):
        """The pause after each step: nothing here, a click on the slide version."""

    def construct(self):
        x, y, rho, _ = pupil_grid(HG_N)
        amplitude = illumination(rho)
        pupil = round_aperture(HG_N)
        periods, angle, waves = ValueTracker(0), ValueTracker(0), ValueTracker(0)

        def phase():
            k, a = periods.get_value(), angle.get_value()
            return (grating_phase(x, y, k * np.cos(a), k * np.sin(a))
                    + lens_phase(rho, waves.get_value()))

        mask = PhaseMask(phase(), pupil).set(height=PB_SIZE).move_to(PB_MASK)
        focal = FocalImage(focal_view(phase(), amplitude), FOCAL_SPOT_COLOR, gamma=HG_GAMMA)
        focal.set(height=PB_SIZE).move_to(PB_FOCAL)
        frame = framed(focal)
        arrow = Arrow(mask.get_right(), focal.get_left(), **TRANSFORM_ARROW_STYLE)
        lens_label = Tex("lens", font_size=FONT_STEP, color=STEP_COLOR).next_to(arrow, UP, buff=0.1)
        labels = VGroup(panel_label("SLM: phase", mask), panel_label("focal plane", focal))
        wheel = phase_wheel(0.45).move_to(PB_WHEEL)
        wheel_labels = VGroup(
            MathTex("0", font_size=FONT_TICK).next_to(wheel, RIGHT, buff=0.08),
            MathTex(r"\pi", font_size=FONT_TICK).next_to(wheel, LEFT, buff=0.08),
        )
        title = heading("What a phase mask does").move_to(HOLO_HEADING, aligned_edge=UL)
        note = Tex("flat: one spot on the axis", font_size=FONT_STEP, color=STEP_COLOR)
        note.next_to(title, DOWN, buff=0.2, aligned_edge=LEFT)

        def say(text):
            nonlocal note
            new = Tex(text, font_size=FONT_STEP, color=STEP_COLOR)
            new.next_to(title, DOWN, buff=0.2, aligned_edge=LEFT)
            swap = Succession(FadeOut(note, run_time=0.3), FadeIn(new, run_time=0.3))
            note = new
            return swap

        self.add(periods, angle, waves)
        self.play(FadeIn(title), FadeIn(note), FadeIn(mask), FadeIn(focal), FadeIn(frame),
                  FadeIn(labels), GrowArrow(arrow), FadeIn(lens_label), FadeIn(wheel),
                  FadeIn(wheel_labels))
        mask.add_updater(lambda m: m.paint(phase()))
        focal.add_updater(lambda m: m.paint(focal_view(phase(), amplitude)))
        self.wait(HOLO_SETTLE)
        self.beat()

        # a grating steers the spot, as far as it has periods, the way it slopes
        self.play(say("a grating steers it"))
        self.play(periods.animate.set_value(PB_PERIODS), run_time=PB_SWEEP_TIME)
        self.play(angle.animate.set_value(PI / 2), run_time=PB_SWEEP_TIME)
        self.wait(HOLO_SETTLE)
        self.beat()

        # a lens moves the focus along the axis: here, the spot blurs
        self.play(say("a lens moves the focus out of this plane"))
        self.play(periods.animate.set_value(0), run_time=1.0)
        angle.set_value(0)
        self.play(waves.animate.set_value(PB_WAVES), run_time=PB_SWEEP_TIME)
        self.wait(HOLO_SETTLE)
        self.beat()

        # gratings summed: one spot each, but not equally bright
        self.play(say("gratings summed: a spot each, unevenly bright"))
        self.play(waves.animate.set_value(0), run_time=1.0)
        mask.clear_updaters()
        focal.clear_updaters()
        for rows, cols in ((1, 2), (1, 5), (5, 5)):
            spots = grid_spots(rows, cols)
            summed = starting_mask(x, y, spots)
            mask.paint(summed)
            focal.paint(focal_view(summed, amplitude) * len(spots))
            self.wait(1.0)
        self.wait(HOLO_SETTLE)
        self.beat()


# --- iteration geometry ------------------------------------------------------
# The two planes side by side, joined by an arrow each way; under the focal
# plane a bar per trap, and the uniformity they add up to.
HI_MASK = np.array([-3.6, 0.5, 0.0])
HI_FOCAL = np.array([2.4, 0.5, 0.0])
HI_SIZE = 3.6  # each picture's height
HI_BARS = np.array([0.6, -3.0, 0.0])  # the bar chart's lower left corner
HI_BARS_SIZE = (3.6, 0.8)  # its width, and the height of an evenly lit trap's bar
HI_READOUT = np.array([-6.2, -2.6, 0.0])  # the iteration count's left edge
HI_STEPS = 40  # iterations run in all
HI_SLOW = 3  # of them taken one at a time
HI_RUN_TIME = 6.0  # the rest


class HologramIteration(Scene):
    """Weighted Gerchberg-Saxton finding an array's mask: the loop between
    the SLM plane and the focal plane, three iterations one at a time, then
    the run until the traps are evenly bright. A beat() on the loop, on the
    starting mask, after each slow iteration and after the run."""

    def beat(self):
        """The pause after each step: nothing here, a click on the slide version."""

    def construct(self):
        x, y, rho, _ = pupil_grid(HG_N)
        amplitude = illumination(rho)
        pupil = round_aperture(HG_N)
        spots = grid_spots(5, 5)
        masks, intensities = iterate_hologram(x, y, amplitude, spots, HI_STEPS)
        even = 1 / len(spots)  # each trap's share if the light were split evenly
        step = ValueTracker(0)

        def now():
            return int(round(step.get_value()))

        mask = PhaseMask(masks[0], pupil).set(height=HI_SIZE).move_to(HI_MASK)
        focal = FocalImage(focal_view(masks[0], amplitude), FOCAL_SPOT_COLOR, full=even,
                           gamma=HG_GAMMA).set(height=HI_SIZE).move_to(HI_FOCAL)
        frame = framed(focal)
        rim = Circle(radius=HI_SIZE / 2, **IMAGE_BORDER_STYLE).move_to(HI_MASK)
        labels = VGroup(panel_label(r"SLM: brightness fixed, phase free", mask),
                        panel_label(r"focal plane: brightness wanted", focal))
        forward = Arrow(mask.get_right() + UP * 0.5, focal.get_left() + UP * 0.5,
                        **TRANSFORM_ARROW_STYLE)
        back = Arrow(focal.get_left() + DOWN * 0.5, mask.get_right() + DOWN * 0.5,
                     **TRANSFORM_ARROW_STYLE)
        arrow_labels = VGroup(
            Tex("lens", font_size=FONT_STEP, color=STEP_COLOR).next_to(forward, UP, buff=0.08),
            Tex("back", font_size=FONT_STEP, color=STEP_COLOR).next_to(back, DOWN, buff=0.08),
        )
        bars = always_redraw(lambda: bar_chart(intensities[now()], even, *HI_BARS_SIZE)
                             .shift(HI_BARS))
        level = DashedLine(HI_BARS + UP * HI_BARS_SIZE[1],
                           HI_BARS + UP * HI_BARS_SIZE[1] + RIGHT * HI_BARS_SIZE[0],
                           **GUIDE_STYLE)
        bars_label = Tex("each trap's brightness", font_size=FONT_STEP, color=STEP_COLOR)
        bars_label.move_to(HI_BARS + RIGHT * HI_BARS_SIZE[0] / 2 + DOWN * 0.3)
        count_label = Tex("iteration", font_size=FONT_READOUT).move_to(HI_READOUT, aligned_edge=LEFT)
        count = Integer(0, font_size=FONT_READOUT, group_with_commas=False)
        count.add_updater(lambda m: m.set_value(now()).next_to(count_label, RIGHT, buff=0.2,
                                                               aligned_edge=DOWN))
        even_label = Tex("uniformity", font_size=FONT_READOUT)
        even_label.next_to(count_label, DOWN, buff=0.3, aligned_edge=LEFT)
        evenness = DecimalNumber(0, num_decimal_places=2, font_size=FONT_READOUT,
                                 group_with_commas=False)
        evenness.add_updater(lambda m: m.set_value(uniformity(intensities[now()]))
                             .next_to(even_label, RIGHT, buff=0.2, aligned_edge=DOWN))
        title = heading("Finding the mask").move_to(HOLO_HEADING, aligned_edge=UL)

        self.add(step)
        self.play(FadeIn(title), FadeIn(labels), GrowArrow(forward), GrowArrow(back),
                  FadeIn(arrow_labels), FadeIn(rim), FadeIn(frame))
        self.wait(HOLO_SETTLE)
        self.beat()

        self.play(FadeIn(mask), FadeIn(focal), FadeIn(bars), FadeIn(level), FadeIn(bars_label),
                  FadeIn(count_label), FadeIn(count), FadeIn(even_label), FadeIn(evenness))
        self.wait(HOLO_SETTLE)
        self.beat()

        def show(index):
            mask.paint(masks[index])
            focal.paint(focal_view(masks[index], amplitude))

        for index in range(1, HI_SLOW + 1):
            # back to the SLM with the dim traps weighted up, then forward again
            self.play(ShowPassingFlash(back.copy().set_color(WHITE), time_width=0.6), run_time=0.7)
            mask.paint(masks[index])
            self.play(ShowPassingFlash(forward.copy().set_color(WHITE), time_width=0.6),
                      run_time=0.7)
            focal.paint(focal_view(masks[index], amplitude))
            step.set_value(index)
            # a wait runs no updaters unless one of them takes the time step:
            # bring the bars and the numbers up to the new step by hand
            self.update_mobjects(0)
            self.wait(HOLO_SETTLE)
            self.beat()

        mask.add_updater(lambda m: show(now()))
        self.play(step.animate.set_value(HI_STEPS), rate_func=linear, run_time=HI_RUN_TIME)
        mask.clear_updaters()
        self.wait(HOLO_SETTLE)
        self.beat()
