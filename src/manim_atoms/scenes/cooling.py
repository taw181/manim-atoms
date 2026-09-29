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
three blocks of the sequence timeline say where in the shot this is. No
numbers beyond the wavelengths: this is the shape of the sequence, not
its settings.
"""

from manim import *

from aionanim.style import *
from aionanim.tools.cooling import (
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
from aionanim.tools.sequence import STAGES, SrLevels, Stage, Timeline, stage_heading

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
TWOD_CAMERA = TWOD_CENTER + [2.0, 0.35, 0]  # where the camera starts
TWOD_HEADING_CORNER = TWOD_CAMERA + COOL_HEADING_CORNER
# Two pairs at 45 degrees in the plane across the push axis: up/down and in/out
# of the page, so they cool the atoms across the stream and leave them free
# along it, which is the push beam's to drive. Drawn in the oblique view.
TWOD_DIRECTIONS = (np.array([0, 1, 1]) / np.sqrt(2), np.array([0, 1, -1]) / np.sqrt(2))
TWOD_BEAM_REACH = 1.6
TWOD_NOZZLE = TWOD_CENTER + DOWN * 2.1
TWOD_BAFFLE = TWOD_CENTER + RIGHT * 4.5
TWOD_PUSH_FROM = TWOD_CENTER + LEFT * (config.frame_x_radius - 2.0)  # the frame's left edge
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
    "narrowband_red_mot": r"T \sim 1\,\mu\mathrm{K}",
}

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
        push_stream = self.upstream()
        # ...and follow the stream right, the 3D MOT coming up as it arrives
        heading = stage_heading(stages[0]).move_to(COOL_HEADING_CORNER, aligned_edge=UL)
        tag = temperature_tag("blue_mot")
        self.play(self.camera.frame.animate.move_to(ORIGIN), FadeIn(levels),
                  FadeIn(timeline), Create(coils), FadeIn(blue), run_time=PAN_TIME)
        self.remove(*self.upstream_mobjects)  # out of shot now

        # --- blue MOT ---
        self.play(*timeline.activate(0), *levels.drive("461"), FadeIn(heading),
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
        heading = self.next_stage(timeline, 1, heading, [
            *levels.drive(), fan.shown.animate.set_value(1),
            FadeOut(blue), FadeIn(red), coils.animate.set_gradient(COIL_WEAK_WIDTH),
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

    def upstream(self):
        """The oven filling the 2D MOT, then the push beam switching on and
        the stream setting off for the 3D MOT; returns that stream."""
        self.camera.frame.move_to(TWOD_CAMERA)
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
                  FadeIn(baffle), FadeIn(baffle_label), run_time=COOL_SWITCH_TIME)
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

    def next_stage(self, timeline, i, heading, anims):
        """Move the timeline and heading on to stage ``i``, alongside
        ``anims``; returns the new heading."""
        new_heading = stage_heading(STAGES[i]).move_to(COOL_HEADING_CORNER, aligned_edge=UL)
        self.play(
            *timeline.activate(i), *anims,
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
