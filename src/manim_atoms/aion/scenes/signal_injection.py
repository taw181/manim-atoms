"""Injecting a signal into the AION prototype's differential interferometer.

DipoleTrapLoading's two traps again (manim_atoms.trapping.scenes.dipole),
once the atoms are sliced: the two clouds, the clock laser through both, and
a light-shift beam on the upper one only. The lab picture behind
LightShiftSignal.
"""

from manim import *

from manim_atoms.aion.style import *
from manim_atoms.core.optics import gaussian_band
from manim_atoms.species.strontium import (
    SrLevels,
    STRONTIUM,
    TRANSITION_698_COLOR,
)
from manim_atoms.trapping.tools.dipole import (
    DT_HEADING_CORNER,
    DT_HOLD,
    DT_HORIZONTAL_HALF,
    DT_HORIZONTAL_WIDTH,
    DT_LEVELS_CENTER,
    DT_LEVELS_SCALE,
    DT_LOWER,
    DT_LOWER_Y,
    DT_SWITCH_TIME,
    DT_TIMELINE_CENTER,
    DT_UPPER,
    DT_UPPER_Y,
    DT_VERTICAL_SPAN,
    DT_VERTICAL_WIDTH,
    DT_X,
    LoadingAtoms,
)
from manim_atoms.trapping.tools.sequence import (
    caption,
    stage_heading,
    STAGES,
    Timeline,
)

# --- the two clouds, ready to interfere -----------------------------------
# DipoleTrapLoading's traps, as the interferometer finds them: both loaded,
# the MOT long gone. Fewer atoms than were loaded, since velocity slicing has
# kept only a slice of each cloud.
SI_N_ATOMS = 70
SI_CLOCK_BEAM_WIDTH = 0.9  # wider than the trap beam it runs along, so both show
SI_LIGHT_SHIFT_WIDTH = 0.55  # the same, against the upper horizontal trap
SI_BEAM_OPACITY = 0.35
SI_BEAM_LAYERS = 10  # these beams are wide enough that fewer layers show as stripes


class SignalInjection(Scene):
    """The two clouds in their traps, the clock laser through both, and a
    light-shift beam on the upper one only.

    The lab picture behind LightShiftSignal: one vertical clock beam drives
    both clouds, so its phase noise is common to the two interferometers,
    while an off-resonant beam on the upper cloud alone shifts omega_A there
    and nowhere else -- a signal injected on purpose, which the difference
    between the two interferometers keeps.
    """

    def stage_break(self):
        """The pause after each step. A slide wrapper stops here instead."""
        self.wait(DT_HOLD)

    def construct(self):
        levels = SrLevels().scale(DT_LEVELS_SCALE).move_to(DT_LEVELS_CENTER)
        timeline = Timeline(STAGES[6:9]).move_to(DT_TIMELINE_CENTER)
        heading = stage_heading(STAGES[7], STRONTIUM).move_to(DT_HEADING_CORNER, aligned_edge=UL)

        horizontal = VGroup(
            *[
                gaussian_band(
                    [DT_X - DT_HORIZONTAL_HALF, y, 0],
                    [DT_X + DT_HORIZONTAL_HALF, y, 0],
                    DT_HORIZONTAL_WIDTH,
                    TRAP_BEAM_COLOR,
                )
                for y in (DT_UPPER_Y, DT_LOWER_Y)
            ]
        )
        vertical = gaussian_band(
            [DT_X, DT_VERTICAL_SPAN[0], 0],
            [DT_X, DT_VERTICAL_SPAN[1], 0],
            DT_VERTICAL_WIDTH,
            TRAP_BEAM_COLOR,
        )
        traps = VGroup(vertical, horizontal)
        atoms = LoadingAtoms(SI_N_ATOMS, DT_UPPER, DT_LOWER)
        for tracker in (
            atoms.load_upper,
            atoms.fall,
            atoms.recapture,
            atoms.load_lower,
        ):
            tracker.set_value(1)
        for tracker in (atoms.glow_upper, atoms.glow_lower):
            tracker.set_value(0)
        cloud_labels = VGroup(
            *[
                Tex(text, font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR)).next_to(
                    band, RIGHT, buff=0.2
                )
                for text, band in (
                    (r"upper cloud", horizontal[0]),
                    (r"lower cloud", horizontal[1]),
                )
            ]
        )

        # --- two clouds, one above the other ---
        self.play(
            FadeIn(levels),
            FadeIn(timeline),
            *timeline.activate(1),
            FadeIn(heading),
            FadeIn(traps),
            FadeIn(atoms),
            FadeIn(cloud_labels),
            run_time=DT_SWITCH_TIME,
        )
        self.stage_break()

        # --- one clock laser through both ---
        clock_beam = gaussian_band(
            [DT_X, DT_VERTICAL_SPAN[0], 0],
            [DT_X, DT_VERTICAL_SPAN[1], 0],
            SI_CLOCK_BEAM_WIDTH,
            TRANSITION_698_COLOR,
            opacity=SI_BEAM_OPACITY,
            layers=SI_BEAM_LAYERS,
        )
        # beside the beam between the clouds: its top end is under the heading
        clock_label = VGroup(
            *[
                Tex(line, font_size=FONT_LEGEND, color=TRANSITION_698_COLOR)
                for line in (r"698 nm", r"clock laser")
            ]
        ).arrange(DOWN, buff=0.1, aligned_edge=RIGHT)
        clock_label.next_to(clock_beam, LEFT, buff=0.2).set_y(
            (DT_UPPER_Y + DT_LOWER_Y) / 2
        )
        new_step = caption(r"One clock laser drives both: its noise is common", heading)
        self.play(
            FadeIn(clock_beam),
            FadeIn(clock_label),
            *levels.drive("698"),
            FadeIn(new_step),
            run_time=DT_SWITCH_TIME,
        )
        step = new_step
        self.stage_break()

        # --- and a light shift on the upper cloud alone ---
        light_shift = gaussian_band(
            [DT_X - DT_HORIZONTAL_HALF, DT_UPPER_Y, 0],
            [DT_X + DT_HORIZONTAL_HALF, DT_UPPER_Y, 0],
            SI_LIGHT_SHIFT_WIDTH,
            LIGHT_SHIFT_COLOR,
            opacity=SI_BEAM_OPACITY,
            layers=SI_BEAM_LAYERS,
        )
        light_shift_label = Tex(
            r"light-shift beam: $\omega_A \to \omega_A + \delta_{\mathrm{LS}}$",
            font_size=FONT_LEGEND,
            color=LIGHT_SHIFT_COLOR,
        )
        light_shift_label.next_to(light_shift, UP, buff=0.1).align_to(light_shift, LEFT)
        new_step = caption(r"An off-resonant beam on the upper cloud only", heading)
        self.play(
            FadeIn(light_shift),
            FadeIn(light_shift_label),
            FadeOut(step),
            FadeIn(new_step),
            run_time=DT_SWITCH_TIME,
        )
        self.stage_break()
