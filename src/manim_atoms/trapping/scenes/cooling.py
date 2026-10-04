"""Cooling Sr: the three MOT stages that open every shot, as a cartoon.

It opens upstream, one frame to the left: the oven feeds a 2D MOT without
pause, and once the push beam comes on the camera follows the stream of
atoms it sends through the baffle into the 3D MOT, which is where the
stages begin.

A blue MOT on the broad 461 nm line catches the atoms, with the repumps
fetching back the ones that leak into 3P2; a red MOT on the narrow 689 nm
line, its frequency swept so it catches atoms at every Doppler shift the
blue MOT leaves them with, takes over; and with the sweep off and the beams
turned down, the narrowband red MOT squeezes the cloud small and cold,
with a seventh beam from below holding it up against gravity.

The Sr level scheme in the corner shows which light is on, and the first
three blocks of the sequence timeline say where in the shot this is, each
with its duration over it from when it starts. The settings that define each
stage are written beside it: the coils' field gradient, the modulation
depth of the red MOT's sweep, and the temperature the cloud ends at.
"""

from manim import *

from manim_atoms.trapping.style import *
from manim_atoms.trapping.tools.cooling import (
    AtomBeam,
    AtomCloud,
    Coils,
    MotBeams,
    Oven,
    SweepFan,
    make_baffle,
    make_push_beam,
    make_up_beam,
    oblique_ring,
)
from manim_atoms.species.strontium import SrLevels
from manim_atoms.trapping.tools.sequence import STAGES, Stage, Timeline, stage_heading

# --- cooling layout -------------------------------------------------------
COOL_MOT_CENTER = np.array([-3.0, -0.35, 0])
COOL_LEVELS_CENTER = [3.75, 1.3, 0]
COOL_LEVELS_SCALE = 0.85
COOL_TIMELINE_CENTER = [3.75, -2.85, 0]
COOL_HEADING_CORNER = [-6.6, 3.7, 0]  # upper left of the stage heading
COOL_TEMPERATURE_AT = COOL_MOT_CENTER + [2.9, -1.55, 0]
COOL_N_ATOMS = 140
COOL_NARROWBAND_INTENSITY = 0.85  # of the beams' starting brightness

# --- upstream: oven, 2D MOT, push beam -----------------------------------
# One frame and a bit to the left of the 3D MOT, on the same beam line, so
# the camera pans straight along the stream.
TWOD_CENTER = COOL_MOT_CENTER + LEFT * 12.0
# Where the camera starts: right of the 2D MOT by enough that the baffle
# clears the level scheme, which is up from the start in its usual corner.
TWOD_CAMERA_OFFSET = 3.6
TWOD_CAMERA = TWOD_CENTER + [TWOD_CAMERA_OFFSET, 0.35, 0]
TWOD_HEADING_CORNER = TWOD_CAMERA + COOL_HEADING_CORNER
# Two pairs at 45 degrees in the plane across the push axis: up/down and in/out
# of the page, so they cool the atoms across the stream and leave them free
# along it, which is the push beam's to drive. Drawn in the oblique view.
TWOD_DIRECTIONS = (np.array([0, 1, 1]) / np.sqrt(2), np.array([0, 1, -1]) / np.sqrt(2))
TWOD_BEAM_REACH = 1.6
TWOD_NOZZLE = TWOD_CENTER + DOWN * 2.1
TWOD_BAFFLE = TWOD_CENTER + RIGHT * 4.5
TWOD_PUSH_FROM = TWOD_CENTER + LEFT * (config.frame_x_radius - TWOD_CAMERA_OFFSET)  # the frame's left edge
TWOD_CLOUD = dict(n=70, radius=0.45, temperature=0.3, stretch=(2.2, 0.5))
OVEN_BEAM = dict(speed=2.5, rate=14, spread=0.06, divergence=0.12)
PUSH_BEAM = dict(speed=3.5, rate=12, spread=0.05, divergence=0.01)
TWOD_STAGE = Stage("blue_mot", r"2D MOT", "461")

# The cloud at the end of each stage: (radius, temperature). Cartoon values,
# chosen to read as "big and hot", "smaller and cooler", "small and cold".
COOL_CLOUD = {
    "blue_mot": (1.0, 1.0),
    "modulated_red_mot": (0.55, 0.12),
    "narrowband_red_mot": (0.2, 0.008),
}
COOL_TEMPERATURE_TEX = {
    "blue_mot": r"T \sim 1\,\mathrm{mK}",
    "modulated_red_mot": r"T \sim 10\,\mu\mathrm{K}",
    "narrowband_red_mot": r"T \sim 2\,\mu\mathrm{K}",
}
# The coils' field gradient: strong for the blue MOT, and ten times weaker
# once the narrow red line takes over, where it stays for both red stages.
COOL_GRADIENT_TEX = {
    "blue_mot": r"3.5\,\mathrm{mT/cm}",
    "modulated_red_mot": r"0.4\,\mathrm{mT/cm}",
    "narrowband_red_mot": r"0.4\,\mathrm{mT/cm}",
}
COOL_GRADIENT_BUFF = 0.3  # right of the upper coil
# How long each stage runs, over its block of the timeline.
COOL_DURATION_TEX = {
    "blue_mot": r"1.5\,\mathrm{s}",
    "modulated_red_mot": r"200\,\mathrm{ms}",
    "narrowband_red_mot": r"100\,\mathrm{ms}",
}
COOL_DURATION_BUFF = 0.15
# the red MOT's frequency sweep, under the 689 nm line of its heading
COOL_MODULATION_TEX = r"6\,\mathrm{MHz\ modulation}"

# --- pacing ---------------------------------------------------------------
COOL_SWITCH_TIME = 1.2  # one stage's light and field giving way to the next
COOL_LOAD_TIME = 3.0  # atoms arriving into the blue MOT
COOL_LEAK_TIME = 1.5
COOL_REPUMP_TIME = 1.5
COOL_SWEEP_TIME = 3.0  # the modulated MOT at work
COOL_RAMP_TIME = 3.0  # the narrowband MOT's intensity ramp
COOL_HOLD = 1.5  # the pause after each stage, where a slide stops instead
TWOD_LOAD_TIME = 3.0  # the oven filling the 2D MOT
PUSH_LEAD = 0.6  # the push stream's head start on the camera
PAN_TIME = 3.4  # following the stream to the 3D MOT


def temperature_tag(key):
    return MathTex(COOL_TEMPERATURE_TEX[key], font_size=FONT_TEMPERATURE,
                   color=lighten(GUIDE_COLOR)).move_to(COOL_TEMPERATURE_AT)


def gradient_tag(key, coils):
    """The field gradient, beside the upper coil it is drawn with."""
    return MathTex(COOL_GRADIENT_TEX[key], font_size=FONT_LEGEND,
                   color=COIL_COLOR).next_to(coils.loops[0], RIGHT,
                                             buff=COOL_GRADIENT_BUFF)


def duration_tag(key, block):
    """How long a stage runs, over its block of the timeline."""
    return MathTex(COOL_DURATION_TEX[key], font_size=FONT_LEGEND,
                   color=PLOT_FOREGROUND).next_to(block, UP, buff=COOL_DURATION_BUFF)


class CoolingSequence(MovingCameraScene):
    def stage_break(self):
        """The pause after each stage. A slide wrapper stops here instead."""
        self.wait(COOL_HOLD)

    def construct(self):
        levels = SrLevels(repump=True)
        fan = SweepFan()
        levels.add(fan)  # in the diagram's own coordinates, so before scaling
        levels.scale(COOL_LEVELS_SCALE).move_to(COOL_LEVELS_CENTER)
        stages = STAGES[:3]
        timeline = Timeline(stages).move_to(COOL_TIMELINE_CENTER)

        coils = Coils(COOL_MOT_CENTER)
        blue = MotBeams(TRANSITION_461_COLOR, COOL_MOT_CENTER)
        red = MotBeams(TRANSITION_689_COLOR, COOL_MOT_CENTER)
        up = make_up_beam(TRANSITION_689_COLOR, COOL_MOT_CENTER)
        up_label = Tex("up beam", font_size=FONT_LEGEND, color=TRANSITION_689_COLOR)
        up_label.next_to(up[0].get_bottom(), RIGHT, buff=0.3).shift(UP * 0.05)

        radius, temperature = COOL_CLOUD["blue_mot"]
        cloud = AtomCloud(COOL_N_ATOMS, COOL_MOT_CENTER,
                          palette=(TRANSITION_461_COLOR, TRANSITION_689_COLOR),
                          radius=radius, temperature=temperature)
        cloud.arrived.set_value(0)

        # --- 2D MOT, fed from the oven ---
        push_stream = self.upstream(levels)
        # ...and follow the stream right, the 3D MOT coming up as it arrives;
        # the level scheme rides with the camera, so it holds its corner
        heading = self.heading(0)
        tag = temperature_tag("blue_mot")
        gradient = gradient_tag("blue_mot", coils)
        self.play(self.camera.frame.animate.move_to(ORIGIN),
                  levels.animate.move_to(COOL_LEVELS_CENTER),
                  FadeIn(timeline), Create(coils), FadeIn(blue), run_time=PAN_TIME)
        self.remove(*self.upstream_mobjects)  # out of shot now

        # --- blue MOT ---
        self.play(*timeline.activate(0), *levels.drive("461"), FadeIn(heading),
                  FadeIn(gradient), FadeIn(duration_tag("blue_mot", timeline.blocks[0])),
                  run_time=COOL_SWITCH_TIME)
        self.add(cloud)
        self.play(cloud.arrived.animate.set_value(1), rate_func=linear,
                  run_time=COOL_LOAD_TIME)
        push_stream.flow.set_value(0)  # loaded: the stream runs dry
        self.play(FadeIn(tag))
        # a few atoms fall out of the cooling cycle into 3P2 and go dark...
        self.play(*levels.drive("461", "leak"), cloud.dark.animate.set_value(1),
                  run_time=COOL_LEAK_TIME)
        # ...until the repumps bring them back
        self.play(*levels.drive("461", "679", "707", "return"), run_time=0.6)
        self.play(cloud.dark.animate.set_value(0), run_time=COOL_REPUMP_TIME)
        self.stage_break()

        # --- modulated red MOT ---
        weak = gradient_tag("modulated_red_mot", coils)
        heading = self.next_stage(timeline, 1, heading, [
            *levels.drive(), fan.shown.animate.set_value(1),
            FadeOut(blue), FadeIn(red), coils.animate.set_gradient(COIL_WEAK_WIDTH),
            FadeTransform(gradient, weak),
            cloud.glow.animate.set_value(1),
        ])
        tag = self.cool(cloud, "modulated_red_mot", tag, run_time=COOL_SWEEP_TIME)
        self.stage_break()

        # --- narrowband red MOT ---
        heading = self.next_stage(timeline, 2, heading, [
            *levels.drive("689"), fan.shown.animate.set_value(0),
        ])
        self.play(FadeIn(up), FadeIn(up_label), run_time=COOL_SWITCH_TIME)
        tag = self.cool(cloud, "narrowband_red_mot", tag,
                        red.animate.set_intensity(COOL_NARROWBAND_INTENSITY),
                        run_time=COOL_RAMP_TIME)
        self.stage_break()

    def upstream(self, levels):
        """The oven filling the 2D MOT, then the push beam switching on and
        the stream setting off for the 3D MOT; returns that stream.

        ``levels`` comes up here already driving the 461 nm line, the 2D
        MOT's light, in the corner of the frame it holds for the 3D MOT."""
        self.camera.frame.move_to(TWOD_CAMERA)
        levels.move_to(TWOD_CAMERA + COOL_LEVELS_CENTER)
        for key, group in levels.active.items():
            group.set_opacity(1 if key == "461" else 0)
        heading = stage_heading(TWOD_STAGE).move_to(TWOD_HEADING_CORNER, aligned_edge=UL)
        oven = Oven(TWOD_NOZZLE)
        oven_label = Tex(r"Sr oven", font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR))
        oven_label.next_to(oven, RIGHT, buff=0.3)
        beams = MotBeams(TRANSITION_461_COLOR, TWOD_CENTER, directions=TWOD_DIRECTIONS,
                         reach=TWOD_BEAM_REACH)
        # the plane the beams lie in, so they read as leaving the page
        beams.add_to_back(oblique_ring(TWOD_CENTER, TWOD_BEAM_REACH * 0.85))
        baffle = make_baffle(TWOD_BAFFLE)
        baffle_label = Tex(r"baffle", font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR))
        baffle_label.next_to(baffle, DOWN, buff=0.2)
        push = make_push_beam(TRANSITION_461_COLOR, TWOD_PUSH_FROM, TWOD_CENTER + RIGHT * 1.2)
        push_label = Tex(r"push beam", font_size=FONT_LEGEND, color=TRANSITION_461_COLOR)
        push_label.next_to(push[0], UP, buff=0.2).set_x(TWOD_PUSH_FROM[0] + 1.6)

        cloud = AtomCloud(palette=(TRANSITION_461_COLOR, TRANSITION_461_COLOR),
                          center=TWOD_CENTER, source=TWOD_NOZZLE, n_leak=0, seed=3,
                          **TWOD_CLOUD)
        cloud.arrived.set_value(0)
        oven_stream = AtomBeam(TWOD_NOZZLE, TWOD_CENTER, (HOT_ATOM_COLOR, TRANSITION_461_COLOR),
                               **OVEN_BEAM)
        push_stream = AtomBeam(TWOD_CENTER, COOL_MOT_CENTER,
                               (TRANSITION_461_COLOR, TRANSITION_461_COLOR), **PUSH_BEAM)
        self.upstream_mobjects = [heading, oven, oven_label, beams, baffle, baffle_label,
                                  push, push_label, cloud, oven_stream]

        self.play(FadeIn(heading), FadeIn(oven), FadeIn(oven_label), FadeIn(beams),
                  FadeIn(baffle), FadeIn(baffle_label), FadeIn(levels),
                  run_time=COOL_SWITCH_TIME)
        self.add(oven_stream, cloud)
        oven_stream.flow.set_value(1)
        self.play(cloud.arrived.animate.set_value(1), rate_func=linear,
                  run_time=TWOD_LOAD_TIME)
        self.stage_break()

        self.play(FadeIn(push), FadeIn(push_label), run_time=COOL_SWITCH_TIME / 2)
        self.add(push_stream)
        push_stream.flow.set_value(1)
        self.wait(PUSH_LEAD)
        return push_stream

    def heading(self, i):
        """Stage ``i``'s heading, in the upper left; the modulated red MOT's
        carries the depth of its sweep under the transition it drives."""
        heading = stage_heading(STAGES[i])
        if STAGES[i].key == "modulated_red_mot":
            heading.add(MathTex(
                COOL_MODULATION_TEX, font_size=FONT_LEGEND, color=TRANSITION_689_COLOR,
            ).next_to(heading[1], DOWN, buff=0.2))
        return heading.move_to(COOL_HEADING_CORNER, aligned_edge=UL)

    def next_stage(self, timeline, i, heading, anims):
        """Move the timeline and heading on to stage ``i``, alongside
        ``anims``, and put up its duration; returns the new heading."""
        new_heading = self.heading(i)
        self.play(
            *timeline.activate(i), *anims,
            FadeIn(duration_tag(STAGES[i].key, timeline.blocks[i])),
            # out, then in: two headings crossing each other can't be read
            Succession(FadeOut(heading, shift=UP * 0.2), FadeIn(new_heading, shift=UP * 0.2)),
            run_time=COOL_SWITCH_TIME,
        )
        return new_heading

    def cool(self, cloud, key, tag, *anims, run_time):
        """Shrink and cool the cloud to where stage ``key`` leaves it, the
        temperature tag changing over halfway; returns the new tag."""
        radius, temperature = COOL_CLOUD[key]
        new_tag = temperature_tag(key)
        self.play(
            cloud.radius.animate.set_value(radius),
            cloud.temperature.animate.set_value(temperature),
            Succession(FadeOut(tag), FadeIn(new_tag)),
            *anims, run_time=run_time,
        )
        return new_tag
