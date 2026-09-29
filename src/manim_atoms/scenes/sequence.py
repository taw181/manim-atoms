"""One shot of the experiment, stage by stage, beside the imaging of it.

A timeline of the sequence runs along the bottom and lights up one stage at
a time; the Sr level scheme lights the transition that stage drives; and the
imaging video plays in the upper right corner through the stages it covers,
from the blue MOT to loading the lower dipole trap. The stages after it --
state preparation, interferometry and readout -- run over its last frame,
dimmed.

ExperimentSequenceSimple is the slide's cut: no level scheme, the sequence
stopped once the lower trap has loaded, and the video in the middle.
"""

from manim import *

from aionanim.resources import data_path
from aionanim.style import *
from aionanim.tools.sequence import (
    IMAGING_CROP,
    IMAGING_FRAMES_PER_SNAPSHOT,
    IMAGING_T0_MS,
    IMAGING_VIDEO,
    REFERENCES,
    STAGES,
    References,
    SrLevels,
    Timeline,
    snapshot_index,
    snapshot_ms,
    stage_heading,
)
from aionanim.tools.video import VideoFrame, load_video_frames

# --- experiment-sequence layout --------------------------------------------
SEQ_VIDEO_SIZE = 3.9
SEQ_VIDEO_CENTER = [4.8, 1.95, 0]
SEQ_LEVELS_CENTER = [-4.35, 1.9, 0]
SEQ_LEVELS_SCALE = 0.85
SEQ_HEADING_CENTER = [0.35, 2.6, 0]
SEQ_TIMELINE_Y = -1.0
# the simple cut: the video centred and larger, the heading to its left
SEQ_SIMPLE_VIDEO_SIZE = 4.3
SEQ_SIMPLE_VIDEO_CENTER = [0, 1.45, 0]
SEQ_SIMPLE_HEADING_CENTER = [-4.65, 1.45, 0]
SEQ_SIMPLE_STAGES = 5  # up to and including loading the lower dipole trap
SEQ_SIMPLE_REFERENCES = 2  # the papers those stages cite

# --- pacing ---------------------------------------------------------------
SEQ_VIDEO_MS_PER_S = 25.0  # the imaging at half a second a snapshot
SEQ_STAGE_TIME = 2.5  # a stage the video doesn't cover
SEQ_SWITCH_TIME = 0.6  # how long the timeline takes to move to the next stage


class ExperimentSequence(Scene):
    STAGES = STAGES
    REFERENCES = REFERENCES
    LEVELS = True
    VIDEO_SIZE = SEQ_VIDEO_SIZE
    VIDEO_CENTER = SEQ_VIDEO_CENTER
    HEADING_CENTER = SEQ_HEADING_CENTER

    def construct(self):
        stages = self.STAGES
        levels = SrLevels().scale(SEQ_LEVELS_SCALE).move_to(SEQ_LEVELS_CENTER)
        timeline = Timeline(stages)
        timeline.move_to([0, SEQ_TIMELINE_Y, 0], aligned_edge=UP)
        timeline.set_x(0)
        refs = References(timeline, stages, self.REFERENCES)

        frames = load_video_frames(
            data_path(*IMAGING_VIDEO), every=IMAGING_FRAMES_PER_SNAPSHOT,
            crop=IMAGING_CROP,
        )
        video = VideoFrame(frames).set(height=self.VIDEO_SIZE).move_to(self.VIDEO_CENTER)
        t_ms = ValueTracker(IMAGING_T0_MS)
        video.add_updater(lambda m: m.show(snapshot_index(t_ms.get_value())))
        clock = always_redraw(lambda: Tex(
            rf"$t = {snapshot_ms(t_ms.get_value()):.0f}$\,ms",
            font_size=FONT_VIDEO_CLOCK,
        ).next_to(video.get_corner(UL), DR, buff=0.15))
        # drawn over the video and its clock, since the frames can't be faded
        veil = Rectangle(width=self.VIDEO_SIZE, height=self.VIDEO_SIZE, stroke_width=0,
                         fill_color=PLOT_BACKGROUND, fill_opacity=1).move_to(video)
        border = SurroundingRectangle(video, buff=0, **VIDEO_BORDER_STYLE)

        self.add(video, clock, veil)
        self.play(*([FadeIn(levels)] if self.LEVELS else []), FadeIn(timeline),
                  FadeIn(refs), Create(border))

        heading = VGroup()
        for i, stage in enumerate(stages):
            new_heading = stage_heading(stage).move_to(self.HEADING_CENTER)
            anims = [
                *timeline.activate(i),
                *(levels.drive(stage.transition) if self.LEVELS else []),
                *refs.cite(stage.reference),
                # out, then in: two headings crossing each other can't be read
                Succession(FadeOut(heading, shift=UP * 0.2),
                           FadeIn(new_heading, shift=UP * 0.2)),
            ]
            heading = new_heading
            filmed = stage.video_ms is not None
            was_filmed = i > 0 and stages[i - 1].video_ms is not None
            if filmed and not was_filmed:
                anims.append(veil.animate.set_fill(opacity=0))
            elif was_filmed and not filmed:
                anims.append(veil.animate.set_fill(opacity=VIDEO_DIM_OPACITY))

            if filmed:
                start, end = stage.video_ms
                t_ms.set_value(start)
                switch_end = start + SEQ_SWITCH_TIME * SEQ_VIDEO_MS_PER_S
                self.play(*anims, t_ms.animate(rate_func=linear).set_value(switch_end),
                          run_time=SEQ_SWITCH_TIME)
                self.play(t_ms.animate.set_value(end), rate_func=linear,
                          run_time=(end - switch_end) / SEQ_VIDEO_MS_PER_S)
            else:
                self.play(*anims, run_time=SEQ_SWITCH_TIME)
                self.wait(SEQ_STAGE_TIME - SEQ_SWITCH_TIME)
        self.wait()


class ExperimentSequenceSimple(ExperimentSequence):
    """The sequence up to loading the lower dipole trap, beside the video
    alone: no level scheme, and only the papers those stages cite."""

    STAGES = STAGES[:SEQ_SIMPLE_STAGES]
    REFERENCES = REFERENCES[:SEQ_SIMPLE_REFERENCES]
    LEVELS = False
    VIDEO_SIZE = SEQ_SIMPLE_VIDEO_SIZE
    VIDEO_CENTER = SEQ_SIMPLE_VIDEO_CENTER
    HEADING_CENTER = SEQ_SIMPLE_HEADING_CENTER
