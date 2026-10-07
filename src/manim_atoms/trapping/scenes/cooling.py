"""Laser cooling, stage by stage, as a cartoon: Sr's three MOTs, or any
species' sequence written as configuration.

CoolingSequence plays a list of CoolingStage (trapping.tools.cooling) for a
Species: the beams, the coils and the cloud for each stage, its level scheme
lighting the light that is on, and the timeline. As written it is Sr's.

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
    CoolingStage,
    make_baffle,
    make_push_beam,
    make_up_beam,
    MotBeams,
    oblique_ring,
    Oven,
    SweepFan,
)
from manim_atoms.species.scheme import LevelScheme
from manim_atoms.species.strontium import STRONTIUM
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
COOL_GRADIENT_BUFF = 0.3  # right of the upper coil
COOL_DURATION_BUFF = 0.15

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

# --- Sr's three MOTs ----------------------------------------------------------
# The cloud at the end of each stage: (radius, temperature). Cartoon values,
# chosen to read as "big and hot", "smaller and cooler", "small and cold".
# The coils' field gradient is strong for the blue MOT, and ten times weaker
# once the narrow red line takes over, where it stays for both red stages.
# The blue MOT's atoms leak through 1D2 into 3P2, dark to it, until the 679
# and 707 nm repumps bring them back; the modulated red MOT's light is swept
# 6 MHz; the narrowband one adds a beam from below against gravity and turns
# its beams down.
SR_COOLING = [
    CoolingStage(
        STAGES[0], "cooling", ("461",), r"T \sim 1\,\mathrm{mK}",
        r"3.5\,\mathrm{mT/cm}", r"1.5\,\mathrm{s}", COIL_STRONG_WIDTH, (1.0, 1.0),
        leak=(("461", "leak"), ("461", "679", "707", "return")),
    ),
    CoolingStage(
        STAGES[1], "narrow", (), r"T \sim 10\,\mu\mathrm{K}",
        r"0.4\,\mathrm{mT/cm}", r"200\,\mathrm{ms}", COIL_WEAK_WIDTH, (0.55, 0.12),
        sweep=r"6\,\mathrm{MHz\ modulation}", glow=True, run_time=COOL_SWEEP_TIME,
    ),
    CoolingStage(
        STAGES[2], "narrow", ("689",), r"T \sim 2\,\mu\mathrm{K}",
        r"0.4\,\mathrm{mT/cm}", r"100\,\mathrm{ms}", COIL_WEAK_WIDTH, (0.2, 0.008),
        glow=True, up_beam=True, intensity=COOL_NARROWBAND_INTENSITY,
        run_time=COOL_RAMP_TIME,
    ),
]


def temperature_tag(stage):
    """The cloud's temperature at a CoolingStage, as MathTex in its corner."""
    return MathTex(stage.temperature, font_size=FONT_TEMPERATURE,
                   color=lighten(GUIDE_COLOR)).move_to(COOL_TEMPERATURE_AT)


def gradient_tag(stage, coils):
    """A CoolingStage's field gradient, beside the upper coil it is drawn with."""
    return MathTex(stage.gradient, font_size=FONT_LEGEND,
                   color=COIL_COLOR).next_to(coils.loops[0], RIGHT,
                                             buff=COOL_GRADIENT_BUFF)


def duration_tag(stage, block):
    """How long a CoolingStage runs, over its block of the timeline."""
    return MathTex(stage.duration, font_size=FONT_LEGEND,
                   color=PLOT_FOREGROUND).next_to(block, UP, buff=COOL_DURATION_BUFF)


class CoolingSequence(MovingCameraScene):
    """A species' cooling stages as a cartoon: the light, the field gradient
    and the cloud at each, with its level scheme and the timeline beside
    them. One stage_break() per stage.

    Configured by class attributes: ``SPECIES``; ``STAGES``, a list of
    CoolingStage (trapping.tools.cooling); ``EXTRAS``, the level scheme's
    extras to draw. As written: Sr's blue MOT, modulated red MOT and
    narrowband red MOT.
    """

    SPECIES = STRONTIUM
    STAGES = SR_COOLING
    EXTRAS = ("repump",)

    def stage_break(self):
        """The pause after each stage. A slide wrapper stops here instead."""
        self.wait(COOL_HOLD)

    def construct(self):
        species, stages = self.SPECIES, self.STAGES
        levels = LevelScheme(species, self.EXTRAS)
        fan = SweepFan(species) if any(st.sweep for st in stages) else None
        if fan is not None:
            levels.add(fan)  # in the diagram's own coordinates, so before scaling
        levels.scale(COOL_LEVELS_SCALE).move_to(COOL_LEVELS_CENTER)
        timeline = Timeline([st.stage for st in stages]).move_to(COOL_TIMELINE_CENTER)

        narrow = species.transition("narrow").color
        coils = Coils(COOL_MOT_CENTER, width=stages[0].coil_width)
        beams = {role: MotBeams(species.transition(role).color, COOL_MOT_CENTER)
                 for role in dict.fromkeys(st.beams for st in stages)}
        up = make_up_beam(narrow, COOL_MOT_CENTER)
        up_label = Tex("up beam", font_size=FONT_LEGEND, color=narrow)
        up_label.next_to(up[0].get_bottom(), RIGHT, buff=0.3).shift(UP * 0.05)

        first = stages[0]
        radius, temperature = first.cloud
        cloud = AtomCloud(COOL_N_ATOMS, COOL_MOT_CENTER,
                          palette=(species.transition("cooling").color, narrow),
                          n_leak=12 if any(st.leak for st in stages) else 0,
                          radius=radius, temperature=temperature)
        cloud.arrived.set_value(0)

        # --- 2D MOT, fed from the oven ---
        push_stream = self.upstream(levels)
        # ...and follow the stream right, the 3D MOT coming up as it arrives;
        # the level scheme rides with the camera, so it holds its corner
        heading = self.heading(0)
        tag = temperature_tag(first)
        gradient = gradient_tag(first, coils)
        self.play(self.camera.frame.animate.move_to(ORIGIN),
                  levels.animate.move_to(COOL_LEVELS_CENTER),
                  FadeIn(timeline), Create(coils), FadeIn(beams[first.beams]),
                  run_time=PAN_TIME)
        self.remove(*self.upstream_mobjects)  # out of shot now

        # --- the first stage loads the trap ---
        self.play(*timeline.activate(0), *levels.drive(*first.drive), FadeIn(heading),
                  FadeIn(gradient), FadeIn(duration_tag(first, timeline.blocks[0])),
                  run_time=COOL_SWITCH_TIME)
        self.add(cloud)
        self.play(cloud.arrived.animate.set_value(1), rate_func=linear,
                  run_time=COOL_LOAD_TIME)
        push_stream.flow.set_value(0)  # loaded: the stream runs dry
        self.play(FadeIn(tag))
        if first.leak is not None:
            leak, repump = first.leak
            # a few atoms fall out of the cooling cycle and go dark...
            self.play(*levels.drive(*leak), cloud.dark.animate.set_value(1),
                      run_time=COOL_LEAK_TIME)
            # ...until the repumps bring them back
            self.play(*levels.drive(*repump), run_time=0.6)
            self.play(cloud.dark.animate.set_value(0), run_time=COOL_REPUMP_TIME)
        self.stage_break()

        # --- and each stage after it takes over from the one before ---
        for i, stage in enumerate(stages[1:], start=1):
            before = stages[i - 1]
            anims = [*levels.drive(*stage.drive)]
            if fan is not None and bool(stage.sweep) != bool(before.sweep):
                anims.append(fan.shown.animate.set_value(1 if stage.sweep else 0))
            if stage.beams != before.beams:
                anims += [FadeOut(beams[before.beams]), FadeIn(beams[stage.beams])]
            if stage.coil_width != before.coil_width:
                anims.append(coils.animate.set_gradient(stage.coil_width))
            if stage.gradient != before.gradient:
                new_gradient = gradient_tag(stage, coils)
                anims.append(FadeTransform(gradient, new_gradient))
                gradient = new_gradient
            if stage.glow and not before.glow:
                anims.append(cloud.glow.animate.set_value(1))
            heading = self.next_stage(timeline, i, heading, anims)
            if stage.up_beam and not before.up_beam:
                self.play(FadeIn(up), FadeIn(up_label), run_time=COOL_SWITCH_TIME)
            ramp = ([beams[stage.beams].animate.set_intensity(stage.intensity)]
                    if stage.intensity is not None else [])
            tag = self.cool(cloud, stage, tag, *ramp, run_time=stage.run_time)
            self.stage_break()

    def upstream(self, levels):
        """The oven filling the 2D MOT, then the push beam switching on and
        the stream setting off for the 3D MOT; returns that stream.

        ``levels`` comes up here already driving the cooling line, the 2D
        MOT's light, in the corner of the frame it holds for the 3D MOT."""
        species = self.SPECIES
        cooling = species.transition("cooling")
        self.camera.frame.move_to(TWOD_CAMERA)
        levels.move_to(TWOD_CAMERA + COOL_LEVELS_CENTER)
        for key, group in levels.active.items():
            group.set_opacity(1 if key == cooling.key else 0)
        twod = Stage(self.STAGES[0].stage.key, r"2D MOT", cooling.key)
        heading = stage_heading(twod, species).move_to(TWOD_HEADING_CORNER, aligned_edge=UL)
        oven = Oven(TWOD_NOZZLE)
        oven_label = Tex(rf"{species.symbol} oven", font_size=FONT_LEGEND,
                         color=lighten(GUIDE_COLOR))
        oven_label.next_to(oven, RIGHT, buff=0.3)
        beams = MotBeams(cooling.color, TWOD_CENTER, directions=TWOD_DIRECTIONS,
                         reach=TWOD_BEAM_REACH)
        # the plane the beams lie in, so they read as leaving the page
        beams.add_to_back(oblique_ring(TWOD_CENTER, TWOD_BEAM_REACH * 0.85))
        baffle = make_baffle(TWOD_BAFFLE)
        baffle_label = Tex(r"baffle", font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR))
        baffle_label.next_to(baffle, DOWN, buff=0.2)
        push_color = species.transition("push").color
        push = make_push_beam(push_color, TWOD_PUSH_FROM, TWOD_CENTER + RIGHT * 1.2)
        push_label = Tex(r"push beam", font_size=FONT_LEGEND, color=push_color)
        push_label.next_to(push[0], UP, buff=0.2).set_x(TWOD_PUSH_FROM[0] + 1.6)

        cloud = AtomCloud(palette=(cooling.color, cooling.color),
                          center=TWOD_CENTER, source=TWOD_NOZZLE, n_leak=0, seed=3,
                          **TWOD_CLOUD)
        cloud.arrived.set_value(0)
        oven_stream = AtomBeam(TWOD_NOZZLE, TWOD_CENTER, (HOT_ATOM_COLOR, cooling.color),
                               **OVEN_BEAM)
        push_stream = AtomBeam(TWOD_CENTER, COOL_MOT_CENTER,
                               (cooling.color, cooling.color), **PUSH_BEAM)
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
        """Stage ``i``'s heading, in the upper left; a swept stage's carries
        the depth of its sweep under the transition it drives."""
        stage = self.STAGES[i]
        heading = stage_heading(stage.stage, self.SPECIES)
        if stage.sweep:
            heading.add(MathTex(
                stage.sweep, font_size=FONT_LEGEND,
                color=self.SPECIES.transition("narrow").color,
            ).next_to(heading[1], DOWN, buff=0.2))
        return heading.move_to(COOL_HEADING_CORNER, aligned_edge=UL)

    def next_stage(self, timeline, i, heading, anims):
        """Move the timeline and heading on to stage ``i``, alongside
        ``anims``, and put up its duration; returns the new heading."""
        new_heading = self.heading(i)
        self.play(
            *timeline.activate(i), *anims,
            FadeIn(duration_tag(self.STAGES[i], timeline.blocks[i])),
            # out, then in: two headings crossing each other can't be read
            Succession(FadeOut(heading, shift=UP * 0.2), FadeIn(new_heading, shift=UP * 0.2)),
            run_time=COOL_SWITCH_TIME,
        )
        return new_heading

    def cool(self, cloud, stage, tag, *anims, run_time):
        """Shrink and cool the cloud to where ``stage`` leaves it, the
        temperature tag changing over halfway; returns the new tag."""
        radius, temperature = stage.cloud
        new_tag = temperature_tag(stage)
        self.play(
            cloud.radius.animate.set_value(radius),
            cloud.temperature.animate.set_value(temperature),
            Succession(FadeOut(tag), FadeIn(new_tag)),
            *anims, run_time=run_time,
        )
        return new_tag
