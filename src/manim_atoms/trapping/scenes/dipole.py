"""Loading the two dipole traps from the red MOT, then spin-polarising them.

Picks up where CoolingSequence leaves off: a small cold red MOT. Two
crossed dipole traps are switched on, one above the other, with a
transparency beam over the upper one. The MOT is held on the upper trap to
load it; the transparency beam then keeps those atoms dark, out of reach of
the 689 nm light. The MOT is let go, the hotter atoms drop, the field zero
is stepped down, and once they reach the lower trap the MOT comes back on
round it to load that. With both traps full, the MOT goes off and the atoms
are optically pumped into m_F = +9/2 with swept, circularly polarised
689 nm light.

As in CoolingSequence, the level scheme lights the light that is on, the
timeline's next three blocks track the stage, and nothing is quantified
beyond the wavelengths.

manim_atoms.aion.scenes.signal_injection comes back to the same traps once
the atoms are sliced, to inject a signal into one of them.
"""

from manim import *

from manim_atoms.trapping.style import *
from manim_atoms.core.optics import gaussian_band, gaussian_spot
from manim_atoms.species.strontium import SrLevels
from manim_atoms.trapping.tools.cooling import SweepFan
from manim_atoms.trapping.tools.dipole import (
    LoadingAtoms,
    SpinHistogram,
    make_field_zero,
    make_mot_glow,
)
from manim_atoms.trapping.tools.sequence import STAGES, Timeline, stage_heading

# --- dipole-trap layout ---------------------------------------------------
DT_X = -3.0  # the vertical beam
DT_UPPER_Y = 0.7
DT_LOWER_Y = -1.6
DT_UPPER = np.array([DT_X, DT_UPPER_Y, 0])
DT_LOWER = np.array([DT_X, DT_LOWER_Y, 0])
DT_HORIZONTAL_HALF = 2.4  # half the drawn length of a horizontal beam
DT_HORIZONTAL_WIDTH = 0.16
DT_VERTICAL_WIDTH = 0.42
DT_VERTICAL_SPAN = (-4.1, 1.9)  # it runs off the bottom and stops short of the heading
DT_TRANSPARENCY_RADIUS = 0.42
DT_ZERO_X = DT_X - DT_HORIZONTAL_HALF - 0.15  # the B = 0 pointer's tip
DT_MOT_RADIUS = 2.6
DT_HISTOGRAM_CENTER = [0.8, -2.5, 0]
DT_LEVELS_CENTER = [3.95, 1.3, 0]
DT_LEVELS_SCALE = 0.72
DT_TIMELINE_CENTER = [4.6, -2.95, 0]
DT_HEADING_CORNER = [-6.6, 3.7, 0]
DT_N_ATOMS = 150

# --- pacing ---------------------------------------------------------------
DT_SWITCH_TIME = 1.2
DT_LOAD_TIME = 3.0  # each trap's loading
DT_FALL_TIME = 2.2
# The field zero sets off only this far into the fall, so the atoms are seen
# to drop under gravity first, not to be carried down by the field.
DT_ZERO_DELAY = 0.4
DT_RECAPTURE_TIME = 1.5
DT_PUMP_TIME = 3.0
DT_HOLD = 1.5  # the pause after each stage, where a slide stops instead


def caption(text, heading):
    """A grey caption under ``heading``, left-aligned with it."""
    return Tex(text, font_size=FONT_CAPTION, color=lighten(GUIDE_COLOR)).next_to(
        heading, DOWN, buff=0.3, aligned_edge=LEFT
    )


class DipoleTrapLoading(Scene):
    """The red MOT shared out into two crossed dipole traps, then the atoms spin-polarised
    into m_F = +9/2, with the levels and the timeline beside them. One
    stage_break() per stage."""
    def stage_break(self):
        """The pause after each stage. A slide wrapper stops here instead."""
        self.wait(DT_HOLD)

    def construct(self):
        levels = SrLevels(repump=True, transparency=True)
        fan = SweepFan()
        levels.add(fan)  # in the diagram's own coordinates, so before scaling
        levels.scale(DT_LEVELS_SCALE).move_to(DT_LEVELS_CENTER)
        stages = STAGES[3:6]
        timeline = Timeline(stages).move_to(DT_TIMELINE_CENTER)

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
        trap_labels = VGroup(
            *[
                Tex("1064 nm", font_size=FONT_LEGEND, color=TRAP_BEAM_COLOR).next_to(
                    band, RIGHT, buff=0.15
                )
                for band in horizontal
            ],
            Tex("813 nm", font_size=FONT_LEGEND, color=TRAP_BEAM_COLOR)
            .next_to(vertical, RIGHT, buff=0.15)
            .set_y(-3.5),
        )
        transparency = gaussian_spot(
            DT_UPPER,
            DT_TRANSPARENCY_RADIUS,
            TRANSITION_488_COLOR,
            opacity=TRANSPARENCY_OPACITY,
        )
        transparency_label = Tex(
            "488 nm", font_size=FONT_LEGEND, color=TRANSITION_488_COLOR
        )
        transparency_label.next_to(transparency, UL, buff=0.0).shift(LEFT * 0.1)
        traps = VGroup(vertical, horizontal, trap_labels)

        mot_center = (DT_UPPER + DT_LOWER) / 2
        mot = make_mot_glow(mot_center, DT_MOT_RADIUS)
        zero = make_field_zero(DT_UPPER_Y, DT_ZERO_X)
        atoms = LoadingAtoms(DT_N_ATOMS, DT_UPPER, DT_LOWER)
        histogram = SpinHistogram().move_to(DT_HISTOGRAM_CENTER)

        # where CoolingSequence left off: a small red MOT, all the light but the 689 off
        self.add(mot, levels, atoms)
        self.play(FadeIn(timeline), FadeIn(zero), *levels.drive("689"))

        # --- the upper trap ---
        heading = stage_heading(stages[0]).move_to(DT_HEADING_CORNER, aligned_edge=UL)
        step = caption(r"traps, transparency beam and repumps on", heading)
        self.play(
            *timeline.activate(0),
            FadeIn(heading),
            FadeIn(step),
            FadeIn(traps),
            FadeIn(transparency),
            FadeIn(transparency_label),
            *levels.drive("689", "488", "679", "707", "return"),
            run_time=DT_SWITCH_TIME,
        )
        step = self.recaption(step, r"MOT held on the upper trap", heading)
        # the transparency beam puts the trapped atoms out of the MOT light's reach
        self.play(
            atoms.load_upper.animate.set_value(1),
            atoms.glow_upper.animate(rate_func=rush_into).set_value(0),
            run_time=DT_LOAD_TIME,
        )
        self.stage_break()

        # --- the lower trap ---
        heading, step = self.next_stage(
            timeline, 1, heading, step, r"MOT released: the hotter atoms fall"
        )
        # the light goes out at once and the atoms fall, gathering speed as
        # they go; the field zero follows them down only once they are on
        # their way, on the same curve started late, so it stays behind them
        # all the way and arrives with them...
        self.play(
            FadeOut(mot, rate_func=rush_from),
            atoms.glow_lower.animate(rate_func=rush_from).set_value(0),
            *levels.drive("488", "679", "707", "return"),
            atoms.fall.animate(rate_func=rush_into).set_value(1),
            zero.animate(rate_func=squish_rate_func(rush_into, DT_ZERO_DELAY, 1)).set_y(
                DT_LOWER_Y
            ),
            run_time=DT_FALL_TIME,
        )
        # ...and only once they are down does the MOT come back on round them
        new_step = caption(r"MOT back on round the lower trap", heading)
        self.play(
            FadeIn(mot),
            atoms.glow_lower.animate.set_value(1),
            atoms.recapture.animate.set_value(1),
            *levels.drive("689", "488", "679", "707", "return"),
            Succession(FadeOut(step), FadeIn(new_step)),
            run_time=DT_RECAPTURE_TIME,
        )
        step = new_step
        self.play(atoms.load_lower.animate.set_value(1), run_time=DT_LOAD_TIME)
        self.stage_break()

        # --- spin polarisation ---
        heading, step = self.next_stage(
            timeline, 2, heading, step, r"MOT off; pumped into $m_F = +\tfrac{9}{2}$"
        )
        self.play(
            FadeOut(mot),
            FadeOut(zero),
            FadeOut(transparency),
            FadeOut(transparency_label),
            atoms.glow_lower.animate.set_value(0),
            FadeIn(histogram),
            *levels.drive("679", "707", "return"),
            run_time=DT_SWITCH_TIME,
        )
        # the atoms light up faintly while they scatter the pumping light
        self.play(
            fan.shown.animate.set_value(1),
            atoms.glow_upper.animate.set_value(0.5),
            atoms.glow_lower.animate.set_value(0.5),
            run_time=0.6,
        )
        self.play(histogram.pump.animate.set_value(1), run_time=DT_PUMP_TIME)
        # the pumping light goes off, leaving only the traps
        self.play(
            fan.shown.animate.set_value(0),
            *levels.drive(),
            atoms.glow_upper.animate.set_value(0),
            atoms.glow_lower.animate.set_value(0),
            run_time=0.6,
        )
        self.stage_break()

    def recaption(self, step, text, heading):
        new_step = caption(text, heading)
        self.play(FadeOut(step), FadeIn(new_step), run_time=0.6)
        return new_step

    def next_stage(self, timeline, i, heading, step, text):
        """Move the timeline, heading and caption on to stage ``i`` of this
        scene's three; returns the new heading and caption."""
        new_heading = stage_heading(STAGES[3 + i]).move_to(
            DT_HEADING_CORNER, aligned_edge=UL
        )
        new_step = caption(text, new_heading)
        self.play(
            *timeline.activate(i),
            # out, then in: two headings crossing each other can't be read
            Succession(
                FadeOut(VGroup(heading, step), shift=UP * 0.2),
                FadeIn(VGroup(new_heading, new_step), shift=UP * 0.2),
            ),
            run_time=DT_SWITCH_TIME,
        )
        return new_heading, new_step
