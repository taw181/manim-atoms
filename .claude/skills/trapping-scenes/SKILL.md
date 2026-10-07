---
name: trapping-scenes
description: Build or change a laser cooling and trapping scene in manim-atoms — MOTs (blue, red, 2D), dipole traps, an oven and atom beam, optical pumping, velocity slicing, a high-flux source, or any stage-by-stage experimental sequence shown beside a level scheme and a timeline, with or without the imaging video. Use it whenever the scene is about getting atoms cold and trapped rather than interfering them. Use it with the base manim-atoms skill.
---

# Trapping scenes

Read the base `manim-atoms` skill first. Trapping scenes are cartoons of
apparatus, not space-time diagrams. Each shows a stage of an experiment
with three things beside it:
- the level scheme, lit where the light is on;
- a timeline of where the stage sits in the shot;
- a heading naming the stage and the transition it drives.

## Conventions

**Light takes the colour of the transition it drives.**
- The species owns those colours. Ask it for a line by its job, so the
  cartoon and the level scheme agree on which light is on:
  `sr.transition("narrow").color`, `.key` (its wavelength, as printed).
- The jobs: "cooling" (the broad line), "narrow", "clock", "push",
  "imaging", "transparency" (a path: `sr.path("transparency")`) and
  "repump".
- Species: `species.strontium.STRONTIUM` and
  `species.ytterbium.YTTERBIUM`. Both are `species.scheme.Species`.
- The colours are not in any style module.

**Far-detuned light drives no transition**, so it takes no transition
colour. The dipole traps' beams are `TRAP_BEAM_COLOR`, a pale warm white.

**Hardware is furniture**: coils, oven, baffle and chamber take
`OPTIC_COLOR`, the grey.

**Drawing weight carries a quantity, never a number on the screen:**
- how heavy the coils are drawn is the field gradient
  (`COIL_STRONG_WIDTH` for a broad-line MOT, `COIL_WEAK_WIDTH` for a
  narrow-line one);
- a beam's opacity is its intensity;
- a cloud's size and jitter are its temperature.

**An atom shows the light it scatters:**
- it glows in the beam's colour while scattering;
- an atom in a state no beam addresses is dark (`DARK_ATOM_COLOR`);
- an atom that has met no light yet is grey;
- out of the light, an atom takes the ground-state colour it has in every
  interferometer figure.

**One stage per stop.** The level scheme, the timeline and the heading move
on together, in one `play`. Quantities appear only where the stage is
about them (a temperature, a gradient, a duration). Otherwise only the
wavelengths are named.

**To depart:**
- **A species other than Sr or Yb** gets its own `species/` module, as
  `ytterbium` has. It holds a `Species`: levels (a fine-structure stack is
  one `Manifold`), transitions, extras such as a repump loop, roles, and
  the ground state's spin, with its own line colours. Don't reuse another
  species' colours for its lines.
- **A different experiment** is configuration, not code (recipe 5):
  - `CoolingSequence` takes `SPECIES`, `STAGES` (a list of `CoolingStage`)
    and `EXTRAS`;
  - `ExperimentSequence` takes `SPECIES`, `STAGES` (a list of `Stage`),
    `REFERENCES`, `IMAGING` and `BREAK_AFTER`.
  - A `Stage` that isn't Sr's carries its own timeline colours,
    `colors=(fill, edge)`.
- **`DipoleTrapLoading` and `VelocitySlicing`** read their lines from
  `SPECIES`, but their story (the 488 nm transparency beam, 87Sr's
  F = 9/2) is Sr's own.

## Recipes

### 1. A staged sequence: MOT stages beside the levels and timeline

Worked examples: `CoolingSequence` (with a camera pan from the 2D MOT) and
`DipoleTrapLoading`.

```python
from manim_atoms.trapping.style import *
from manim_atoms.species.strontium import STRONTIUM, SrLevels
from manim_atoms.trapping.tools.cooling import AtomCloud, Coils, MotBeams
from manim_atoms.trapping.tools.sequence import STAGES, Timeline, stage_heading

class StagedMOT(Scene):
    def stage_break(self):
        """The pause after each stage. A slide wrapper stops here instead."""
        self.wait(1.0)

    def construct(self):
        sr = STRONTIUM
        broad, narrow = sr.transition("cooling"), sr.transition("narrow")
        levels = SrLevels(repump=True).scale(0.7).move_to(M_LEVELS)
        timeline = Timeline(STAGES[:2]).move_to(M_TIMELINE)
        coils, blue = Coils(M_CENTER), MotBeams(broad.color, M_CENTER)
        red = MotBeams(narrow.color, M_CENTER)
        cloud = AtomCloud(80, M_CENTER, palette=(broad.color, narrow.color),
                          radius=1.0, temperature=1.0)
        cloud.arrived.set_value(0)
        heading = stage_heading(STAGES[0], sr).move_to(M_HEADING, aligned_edge=UL)

        self.play(FadeIn(levels), FadeIn(timeline), Create(coils), FadeIn(blue))
        self.play(*timeline.activate(0), *levels.drive(broad.key), FadeIn(heading))
        self.add(cloud)
        self.play(cloud.arrived.animate.set_value(1), rate_func=linear, run_time=2)
        self.stage_break()

        new = stage_heading(STAGES[1], sr).move_to(M_HEADING, aligned_edge=UL)
        self.play(*timeline.activate(1), *levels.drive(narrow.key),   # everything moves on at once
                  FadeOut(blue), FadeIn(red), coils.animate.set_gradient(COIL_WEAK_WIDTH),
                  cloud.glow.animate.set_value(1),
                  Succession(FadeOut(heading), FadeIn(new)))      # out, then in: never crossed
        self.play(cloud.radius.animate.set_value(0.45), cloud.temperature.animate.set_value(0.2))
        self.stage_break()
```

**The knobs:**
- **`AtomCloud`** has trackers for everything: `arrived` (0 means all still
  off-screen, 1 means loaded), `radius`, `temperature`, `dark` (leaking
  atoms gone dark) and `glow` (0 to 1 across `palette`, the colour of
  the light scattered). It can load from a `source` point and be stretched
  into a cigar (`stretch=(sx, sy)`).
- **`MotBeams.set_intensity`** dims a beam; **`Coils.set_gradient`**
  changes how heavily the coils are drawn.
- **`SweepFan(species)`**, added to the levels, shows a narrow-line
  MOT's frequency sweep (`shown` 0 to 1).
- **`levels.drive(*keys)`** lights the named lines and puts out the rest.
  The keys are the species' transitions and paths. Sr's are `"461"`,
  `"689"`, `"698"`, `"679"`, `"707"`, `"return"`, `"leak"` and `"488"`.
- **Extras are drawn only on request:**
  `LevelScheme(species, ("repump", "transparency"))`, or for Sr
  `SrLevels(repump=True, transparency=True)`. Without them, the repump
  and 488 nm lines aren't there at all.
- **`timeline.activate(i)`** lights block i and dims the one before it.

### 2. Beams and traps

```python
from manim_atoms.core.optics import gaussian_band, gaussian_spot
from manim_atoms.trapping.tools.dipole import LoadingAtoms

beams = VGroup(*[gaussian_band([x0, y, 0], [x1, y, 0], 0.16, TRAP_BEAM_COLOR)
                 for y in (UPPER_Y, LOWER_Y)])
atoms = LoadingAtoms(120, upper_trap, lower_trap, sr.transition("narrow").color)
self.play(atoms.glow_upper.animate.set_value(1))      # lit while it scatters MOT light
self.play(atoms.load_upper.animate.set_value(1))      # settles into the upper trap
self.play(atoms.fall.animate.set_value(1))            # the rest drop when the MOT lets go
```

- A beam seen side on is `gaussian_band(start, end, width, colour)`; seen
  end on it is `gaussian_spot(center, radius, colour)`. Both are nested
  translucent layers, so a beam reads as a Gaussian profile.
- MOT beams with arrowheads are `MotBeams(colour, center)`. They take
  in-page `axes` in degrees, or 3D `directions` drawn obliquely (with
  `oblique_ring` as the depth cue).
- `make_up_beam`, `make_push_beam` and `make_baffle` are the narrow
  beams and the wall.
- Upstream of the trap: `Oven` and `AtomBeam` (`flow` turns the stream on).
- Optical pumping: `SpinHistogram(species.spin)` (`pump` 0 to 1).
- Velocity slicing: `VelocityPlot(sigma, clock.color)` and
  `SlicingCloud(center, sigma)`, both driven by `excite` and `push`;
  `sigma` is the thermal width in units of the pulse's Rabi frequency.

### 3. The imaging video on the scene's clock

Worked examples: `ExperimentSequence`, `ExperimentSequenceSimple`.

```python
from manim_atoms.core.video import VideoFrame, load_video_frames
from manim_atoms.resources import data_path
from manim_atoms.trapping.tools.sequence import SR_IMAGING

imaging = SR_IMAGING                                          # an Imaging: the file, crop, timing
frames = load_video_frames(data_path(*imaging.video), every=imaging.frames_per_snapshot,
                           crop=imaging.crop)
video = VideoFrame(frames).set(height=4).to_edge(LEFT)
t_ms = ValueTracker(imaging.t0_ms)                            # experiment time, in ms
video.add_updater(lambda m: m.show(imaging.snapshot_index(t_ms.get_value())))
self.add(video, SurroundingRectangle(video, buff=0, **IMAGE_BORDER_STYLE))
self.play(t_ms.animate.set_value(200), rate_func=linear, run_time=3)
```

The frames are decoded up front. Which one shows is a function of a
tracker, so the video can be paused, held, or run on the same clock as the
stages. Each `Stage` names the stretch of video (`video_ms`) that shows it.

### 4. A CAD render, labelled

Worked example: `HighFluxLoading`.
- `chamber_view(path, height)` loads the render.
- `chamber_label(text, at(image, (px, py)), direction)` hangs a label off a
  point given in the render's own pixels, so it stays put whatever size
  the image is drawn at.
- `dimension(start, end, text, side)` draws a dimension across it.

### 5. Another species, as configuration

`CoolingSequence` and `ExperimentSequence` are written once and configured
by class attributes. A different atom or experiment is a subclass with
different data.

This is Yb's sequence, rendered and checked. It shows:
- the oven feeding a 399 nm 2D MOT;
- a blue MOT, a broadened green MOT with its sweep, and a green MOT;
- the whole shot's timeline, with no video and no references.

```python
from manim_atoms.species.ytterbium import YTTERBIUM
from manim_atoms.trapping.scenes.cooling import CoolingSequence
from manim_atoms.trapping.scenes.sequence import ExperimentSequence
from manim_atoms.trapping.tools.cooling import CoolingStage
from manim_atoms.trapping.tools.sequence import Stage

YB_STAGES = [                    # Yb's own keys, so each brings its timeline colours
    Stage("yb_blue_mot", r"Blue MOT", "399", colors=("#c9b3ff", "#7a44ff")),
    Stage("yb_broad_green_mot", r"Broadened\\green MOT", "556", colors=("#a8e8b4", "#2fa043")),
    Stage("yb_green_mot", r"Green MOT", "556", colors=("#d9f5de", "#3fcf5a")),
    Stage("yb_lattice", r"Optical\\lattice", colors=("#afe9dd", "#37c8ab")),
    Stage("yb_spin_polarization", r"Spin\\polarization", "556", colors=("#d7f4d7", "#37c837")),
    Stage("yb_clock", r"Clock\\spectroscopy", "578", colors=("#fff0a8", "#d4aa00")),
    Stage("yb_readout", r"State\\readout", "399", colors=("#c9b3ff", "#7a44ff")),
]
YB_COOLING = [                   # illustrative numbers: take yours from your experiment
    CoolingStage(YB_STAGES[0], "cooling", ("399",), r"T \sim 1\,\mathrm{mK}",
                 r"3\,\mathrm{mT/cm}", r"1\,\mathrm{s}", COIL_STRONG_WIDTH, (1.0, 1.0)),
    CoolingStage(YB_STAGES[1], "narrow", (), r"T \sim 30\,\mu\mathrm{K}",
                 r"0.8\,\mathrm{mT/cm}", r"100\,\mathrm{ms}", COIL_WEAK_WIDTH, (0.55, 0.15),
                 sweep=r"4\,\mathrm{MHz\ modulation}", glow=True),
    CoolingStage(YB_STAGES[2], "narrow", ("556",), r"T \sim 10\,\mu\mathrm{K}",
                 r"0.8\,\mathrm{mT/cm}", r"50\,\mathrm{ms}", COIL_WEAK_WIDTH, (0.25, 0.02),
                 glow=True, intensity=0.85),
]

class YbCooling(CoolingSequence):
    SPECIES = YTTERBIUM
    STAGES = YB_COOLING
    EXTRAS = ()                  # no repump loop: Yb's blue MOT barely leaks

class YbSequence(ExperimentSequence):
    SPECIES = YTTERBIUM
    STAGES = YB_STAGES
    REFERENCES = []              # nothing to cite: no braces, no list
    IMAGING = None               # no video panel
    BREAK_AFTER = 4              # preparing the atoms, then using them
```

A `CoolingStage` describes one stage:
- `beams`: the job of its MOT light (a new job swaps the beam set);
- `drive`: the lines it lights (none while a `sweep` stands in for the
  line);
- `temperature`, `gradient`, `duration` and `coil_width`;
- `cloud`: (radius, temperature) at its end;
- flags: `glow`, `up_beam` (a beam from below, as Sr's narrowband MOT has),
  `intensity` (ramp the beams);
- `leak`: (leak keys, repump keys), for Sr's dark-state story.

The first stage loads the trap; each later one takes over from the one
before, changing only what differs.

## Before you finish

At each stop, check that these agree:
- the level scheme's lit lines;
- the beams' colours;
- the heading's transition;
- the lit timeline block.

Check that a cloud's size changes only when its temperature does. Check
nothing crosses the heading: two headings fade out then in, never
together.
