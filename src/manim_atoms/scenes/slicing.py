"""Velocity slicing: the clock pulse that picks out the slowest atoms.

A long, weak pi pulse on the 698 nm clock line has a narrow line shape, so
it excites only the atoms whose Doppler shift keeps them near resonance --
the slowest along the beam -- and leaves the rest in the ground state. A
461 nm pulse then pushes every ground-state atom away, and what is left is a
narrow slice of the velocity distribution, in 3P0, with the pulse's own
sinc-like line shape.

The velocity distribution on the right is stacked by internal state; the
cloud on the left is the same atoms, drifting along the clock beam at their
own velocities. As in the other sequence scenes the level scheme lights the
light that is on and the timeline says where in the shot this is.
"""

from manim import *

from aionanim.style import *
from aionanim.tools.dipole import gaussian_band
from aionanim.tools.sequence import STAGES, SrLevels, Timeline, stage_heading
from aionanim.tools.slicing import CLOUD_WIDTH, SlicingCloud, VelocityPlot

# --- velocity-slicing layout ----------------------------------------------
VS_STAGE = 6  # into STAGES
VS_HEADING_CORNER = [-6.6, 3.7, 0]
VS_TIMELINE_CENTER = [0.9, 3.3, 0]
VS_LEVELS_CENTER = [5.35, 2.55, 0]
VS_LEVELS_SCALE = 0.5
VS_PLOT_CENTER = [1.4, -0.95, 0]
VS_CLOUD_CENTER = np.array([-4.7, -1.2, 0])
VS_CLOCK_BEAM_SPAN = (-4.1, 0.7)  # the vertical clock beam, bottom to top
VS_CLOCK_BEAM_WIDTH = CLOUD_WIDTH + 0.5
VS_PUSH_BEAM_START = -7.3  # the push beam comes in from off the left edge
VS_PUSH_BEAM_WIDTH = 1.4
VS_BEAM_OPACITY = 0.35
VS_BEAM_LAYERS = 10  # these beams are wide enough that fewer layers show as stripes

# --- pacing ---------------------------------------------------------------
VS_SWITCH_TIME = 1.2
VS_PULSE_TIME = 2.5  # the pi pulse transferring the slice
VS_PUSH_TIME = 2.5
VS_HOLD = 1.5  # the pause after each step, where a slide stops instead

# What slicing buys, read out above the plot: the temperature, and the
# fidelity of the interferometer's own pi pulse (44 us, at full clock power).
# Before, T is what the 60 kHz Doppler width of the clock line says (3.3 uK,
# or 2.9 uK with the 20 kHz Fourier width taken out), and a 44 us pulse
# averaged over that spread excites 31 % -- the 0.3 measured. After, T is the
# slice's (see aionanim.tools.slicing) and the fidelity the measured 90 %,
# short of the ~98 % the Doppler spread alone would allow.
VS_BEFORE = (r"3\,\mu\mathrm{K}", r"30\,\%")
VS_AFTER = (r"10\,\mathrm{nK}", r"90\,\%")
VS_READOUT_Y = 1.2  # just above the plot


def caption(text, heading):
    return Tex(text, font_size=FONT_CAPTION, color=lighten(GUIDE_COLOR)).next_to(
        heading, DOWN, buff=0.3, aligned_edge=LEFT)


def readout(when, values, color, plot):
    """'Before slicing  T ~ ...  pi-pulse fidelity ~ ...', over the plot's left end."""
    temperature, fidelity = values
    row = VGroup(
        Tex(when, font_size=FONT_AXIS, color=lighten(GUIDE_COLOR)),
        MathTex(rf"T \approx {temperature}", font_size=FONT_AXIS, color=color),
        Tex(rf"$\pi$-pulse fidelity $\approx {fidelity}$", font_size=FONT_AXIS, color=color),
    ).arrange(RIGHT, buff=0.5)
    return row.move_to([plot.axes.get_left()[0], VS_READOUT_Y, 0], aligned_edge=LEFT)


def recaption(step, text, heading):
    """The next caption, and the animation swapping it in -- played alongside
    whatever the new step does, so the caption never holds the scene still."""
    new_step = caption(text, heading)
    return new_step, Succession(FadeOut(step), FadeIn(new_step))


class VelocitySlicing(Scene):
    def stage_break(self):
        """The pause after each step. A slide wrapper stops here instead."""
        self.wait(VS_HOLD)

    def construct(self):
        levels = SrLevels().scale(VS_LEVELS_SCALE).move_to(VS_LEVELS_CENTER)
        timeline = Timeline(STAGES[VS_STAGE - 1:VS_STAGE + 2]).move_to(VS_TIMELINE_CENTER)
        heading = stage_heading(STAGES[VS_STAGE]).move_to(VS_HEADING_CORNER, aligned_edge=UL)
        plot = VelocityPlot(center=VS_PLOT_CENTER)
        cloud = SlicingCloud(VS_CLOUD_CENTER)

        clock_beam = gaussian_band([VS_CLOUD_CENTER[0], VS_CLOCK_BEAM_SPAN[0], 0],
                                   [VS_CLOUD_CENTER[0], VS_CLOCK_BEAM_SPAN[1], 0],
                                   VS_CLOCK_BEAM_WIDTH, TRANSITION_698_COLOR,
                                   opacity=VS_BEAM_OPACITY, layers=VS_BEAM_LAYERS)
        clock_label = Tex("698 nm", font_size=FONT_LEGEND, color=TRANSITION_698_COLOR)
        clock_label.next_to(clock_beam, UP, buff=0.1)
        push_beam = gaussian_band([VS_PUSH_BEAM_START, VS_CLOUD_CENTER[1], 0],
                                  VS_CLOUD_CENTER + RIGHT * (VS_CLOCK_BEAM_WIDTH / 2 + 0.3),
                                  VS_PUSH_BEAM_WIDTH, TRANSITION_461_COLOR,
                                  opacity=VS_BEAM_OPACITY, layers=VS_BEAM_LAYERS)
        push_label = Tex("461 nm", font_size=FONT_LEGEND, color=TRANSITION_461_COLOR)
        push_label.next_to(push_beam, DOWN, buff=0.15).align_to(push_beam, RIGHT)

        # --- a thermal spread of velocities ---
        step = caption(r"A thermal spread of velocities along the clock beam", heading)
        before = readout("Before slicing", VS_BEFORE, lighten(SLICE_HOT_COLOR), plot)
        self.play(FadeIn(levels), FadeIn(timeline), FadeIn(heading), FadeIn(step),
                  FadeIn(plot), FadeIn(cloud), FadeIn(before), *timeline.activate(1),
                  run_time=VS_SWITCH_TIME)
        self.stage_break()

        # --- the pi pulse ---
        step, swap = recaption(step, r"A long $\pi$ pulse on the clock line excites "
                                     r"only the slowest atoms", heading)
        self.play(swap, FadeIn(clock_beam), FadeIn(clock_label), *levels.drive("698"),
                  Create(plot.line_shape), FadeIn(plot.line_label),
                  run_time=VS_SWITCH_TIME)
        self.play(plot.excite.animate.set_value(1), cloud.excite.animate.set_value(1),
                  run_time=VS_PULSE_TIME)
        self.play(FadeOut(clock_beam), FadeOut(clock_label), *levels.drive(),
                  run_time=0.6)
        self.stage_break()

        # --- the push ---
        step, swap = recaption(step, r"A 461 nm pulse pushes away every atom left "
                                     r"in ${}^1S_0$", heading)
        self.play(swap, FadeIn(push_beam), FadeIn(push_label), *levels.drive("461"),
                  run_time=VS_SWITCH_TIME)
        self.play(plot.push.animate.set_value(1), cloud.push.animate.set_value(1),
                  run_time=VS_PUSH_TIME)
        self.play(FadeOut(push_beam), FadeOut(push_label), *levels.drive(),
                  run_time=0.6)
        self.stage_break()

        # --- what is left ---
        step, swap = recaption(step, r"Left: a narrow slice of slow atoms in ${}^3P_0$",
                               heading)
        after = readout("After slicing", VS_AFTER, lighten(SLICE_COLD_COLOR), plot)
        self.play(swap, FadeOut(plot.line_shape), FadeOut(plot.line_label),
                  Create(plot.outline),
                  Succession(FadeOut(before, shift=UP * 0.15), FadeIn(after, shift=UP * 0.15)),
                  run_time=VS_SWITCH_TIME)
        self.stage_break()
