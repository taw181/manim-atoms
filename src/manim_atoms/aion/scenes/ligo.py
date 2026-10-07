"""How LIGO works: a Michelson interferometer read out at its dark port.

Seen from above: a laser, a beam splitter, two perpendicular arms ending on
free-hanging test masses, and a photodetector on the port where the light
coming back from the two arms recombines. With equal arms the two returning
beams arrive exactly out of phase and cancel, so the detector sits in the
dark. A gravitational wave travelling into the screen stretches one arm while
it squeezes the other; the returning beams slide out of step, stop
cancelling, and light reaches the detector.

Everything runs off one lab clock, `now`, so the light keeps flowing through
every beat of the scene. Everything visual comes from manim_atoms.style.

The builders take the wave as `h` and a `panel` to draw into, so another
scene can set the interferometer, already lit, in part of its own frame and
drive it with a wave of its own; each readout block takes its own panel, so
they can be laid out afresh (MergerOnSensitivityPlot does all of this).
"""

from manim import *

from manim_atoms.aion.style import *
from manim_atoms.aion.tools.ligo import (
    COLUMN_X,
    GW_OFF,
    GW_ON,
    MICHELSON_EQUATION_SCALE,
    MICHELSON_EQUATION_Y,
    MICHELSON_SCALE_SCALE,
    MICHELSON_SCALE_Y,
    MICHELSON_TRACE,
    MICHELSON_TRACE_AMPLITUDE,
    make_apparatus,
    make_equation,
    make_light,
    make_strain_trace,
    run,
)

# --- lab-time beats ---------------------------------------------------------
T_INPUT = 1.1  # the laser beam reaches the splitter
T_ARMS = 2.6  # the arms are lit
T_READOUT = 3.6  # the returning beams are drawn
T_DARK = 5.6  # held on the dark port
T_END = GW_OFF + 3.5


class LIGOMichelson(Scene):
    """A Michelson interferometer on a dark fringe, lit up by a passing wave."""

    def beat(self):
        """The pause on the dark port, before the wave: nothing here, a click
        on the slide version."""

    def construct(self):
        now = ValueTracker(0.0)
        lit_in = ValueTracker(0.0)  # how far light has got down each beam
        lit_arm = ValueTracker(0.0)

        # --- the apparatus ---
        labels, optics, arm_tags = make_apparatus(now)
        self.play(FadeIn(labels), FadeIn(optics), run_time=1.2)

        # --- the light ---
        glow, lights = make_light(now, lit_in, lit_arm)
        # light goes under the optics, and the glow under the detector
        self.add(glow, lights)
        self.bring_to_front(*optics)

        run(self, now, T_INPUT, lit_in.animate.set_value(1))
        run(self, now, T_ARMS, lit_arm.animate.set_value(1), FadeIn(arm_tags))

        # --- equal arms: the returning beams cancel ---
        # Said, not drawn: the returning waves (returning_waves) are left to
        # the scenes that set this beside something else.
        detector_tag = optics[3][2]
        dark_note = Tex(
            "equal arms: the beams cancel", font_size=FONT_LEGEND,
            color=lighten(GUIDE_COLOR),
        ).next_to(detector_tag, UP, buff=0.3).align_to(detector_tag, LEFT)
        run(self, now, T_READOUT)
        run(self, now, T_DARK, FadeIn(dark_note))
        self.beat()

        # --- a wave passes ---
        trace_axes, trace = make_strain_trace(
            now, panel=MICHELSON_TRACE, amplitude=MICHELSON_TRACE_AMPLITUDE
        )
        run(
            self, now, GW_ON, FadeOut(dark_note),
            FadeIn(trace_axes), FadeIn(trace),
        )

        readout, in_h, scale = make_equation()
        VGroup(readout, in_h).scale(MICHELSON_EQUATION_SCALE).move_to(
            [COLUMN_X, MICHELSON_EQUATION_Y, 0]
        )
        scale.scale(MICHELSON_SCALE_SCALE).move_to([COLUMN_X, MICHELSON_SCALE_Y, 0])
        run(self, now, GW_ON + 1.5, FadeIn(readout))
        run(self, now, GW_ON + 3.5, FadeIn(in_h))
        run(self, now, GW_OFF)
        run(self, now, GW_OFF + 1.0, FadeIn(scale))
        run(self, now, T_END)
