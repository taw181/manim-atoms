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

**Light takes the colour of the transition it drives.** The species owns
those colours: `species.strontium`'s `TRANSITION_461_COLOR`,
`TRANSITION_689_COLOR`, `TRANSITION_698_COLOR` and `TRANSITION_488_COLOR`,
and `REPUMP_COLOR`. That way the cartoon and the level scheme agree on
which light is on. Import them by name; they are not in any style module.

**Far-detuned light drives no transition**, so it takes no transition
colour. The dipole traps' beams are `TRAP_BEAM_COLOR`, a pale warm white.

**Hardware is furniture**: coils, oven, baffle and chamber take
`OPTIC_COLOR`, the grey.

**Drawing weight carries a quantity, never a number on the screen:**
- how heavy the coils are drawn is the field gradient
  (`COIL_STRONG_WIDTH` for the blue MOT, `COIL_WEAK_WIDTH` for the red);
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
- **A species other than Sr** gets its own `species/` module, with its
  levels, transitions and line colours. Don't reuse Sr's colours for its
  lines.
- **A stage table other than the group's sequence** is a new list of
  `Stage`, with `SEQUENCE_STAGE_COLORS` entries in the trapping style.

## Recipes

### 1. A staged sequence: MOT stages beside the levels and timeline

Worked examples: `CoolingSequence` (with a camera pan from the 2D MOT) and
`DipoleTrapLoading`.

```python
from manim_atoms.trapping.style import *
from manim_atoms.species.strontium import SrLevels, TRANSITION_461_COLOR, TRANSITION_689_COLOR
from manim_atoms.trapping.tools.cooling import AtomCloud, Coils, MotBeams
from manim_atoms.trapping.tools.sequence import STAGES, Timeline, stage_heading

class StagedMOT(Scene):
    def stage_break(self):
        """The pause after each stage. A slide wrapper stops here instead."""
        self.wait(1.0)

    def construct(self):
        levels = SrLevels(repump=True).scale(0.7).move_to(M_LEVELS)
        timeline = Timeline(STAGES[:2]).move_to(M_TIMELINE)
        coils, blue = Coils(M_CENTER), MotBeams(TRANSITION_461_COLOR, M_CENTER)
        red = MotBeams(TRANSITION_689_COLOR, M_CENTER)
        cloud = AtomCloud(80, M_CENTER, palette=(TRANSITION_461_COLOR, TRANSITION_689_COLOR),
                          radius=1.0, temperature=1.0)
        cloud.arrived.set_value(0)
        heading = stage_heading(STAGES[0]).move_to(M_HEADING, aligned_edge=UL)

        self.play(FadeIn(levels), FadeIn(timeline), Create(coils), FadeIn(blue))
        self.play(*timeline.activate(0), *levels.drive("461"), FadeIn(heading))
        self.add(cloud)
        self.play(cloud.arrived.animate.set_value(1), rate_func=linear, run_time=2)
        self.stage_break()

        new = stage_heading(STAGES[1]).move_to(M_HEADING, aligned_edge=UL)
        self.play(*timeline.activate(1), *levels.drive("689"),     # everything moves on at once
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
- **`SweepFan`**, added to the levels, shows the red MOT's frequency
  sweep (`shown` 0 to 1).
- **`levels.drive(*keys)`** lights the named lines and puts out the rest:
  `"461"`, `"689"`, `"698"`, `"679"`, `"707"`, `"return"`, `"leak"`,
  `"488"`. Call `SrLevels(repump=True, transparency=True)` to have the
  repump and 488 nm lines at all.
- **`timeline.activate(i)`** lights block i and dims the one before it.

### 2. Beams and traps

```python
from manim_atoms.core.optics import gaussian_band, gaussian_spot
from manim_atoms.trapping.tools.dipole import LoadingAtoms

beams = VGroup(*[gaussian_band([x0, y, 0], [x1, y, 0], 0.16, TRAP_BEAM_COLOR)
                 for y in (UPPER_Y, LOWER_Y)])
atoms = LoadingAtoms(120, upper_trap, lower_trap)
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
- Optical pumping: `SpinHistogram` (`pump` 0 to 1).
- Velocity slicing: `VelocityPlot` and `SlicingCloud`, both driven by
  `excite` and `push`.

### 3. The imaging video on the scene's clock

Worked examples: `ExperimentSequence`, `ExperimentSequenceSimple`.

```python
from manim_atoms.core.video import VideoFrame, load_video_frames
from manim_atoms.resources import data_path
from manim_atoms.trapping.tools.sequence import (IMAGING_CROP, IMAGING_FRAMES_PER_SNAPSHOT,
                                                 IMAGING_T0_MS, IMAGING_VIDEO, snapshot_index)

frames = load_video_frames(data_path(*IMAGING_VIDEO), every=IMAGING_FRAMES_PER_SNAPSHOT,
                           crop=IMAGING_CROP)
video = VideoFrame(frames).set(height=4).to_edge(LEFT)
t_ms = ValueTracker(IMAGING_T0_MS)                            # experiment time, in ms
video.add_updater(lambda m: m.show(snapshot_index(t_ms.get_value())))
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

## Before you finish

At each stop, check that these agree:
- the level scheme's lit lines;
- the beams' colours;
- the heading's transition;
- the lit timeline block.

Check that a cloud's size changes only when its temperature does. Check
nothing crosses the heading: two headings fade out then in, never
together.
