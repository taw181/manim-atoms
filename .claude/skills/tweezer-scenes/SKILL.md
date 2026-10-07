---
name: tweezer-scenes
description: Build or change a tweezer-array or SLM hologram scene in manim-atoms — an array of optical tweezers loaded, imaged and rearranged, seen from above or from an angle with each trap a focused beam; a phase mask beside the focal plane it makes; gratings, lens phases, Gerchberg-Saxton iteration, Zernike modes and aberration correction; the optical train from an SLM to the atoms. Use it whenever the scene is about single atoms in tweezers or about shaping light with a phase mask. Use it with the base manim-atoms skill.
---

# Tweezer scenes

Read the base `manim-atoms` skill first. Tweezer scenes are of two kinds:
the array (traps, atoms, moves) and the light that makes it (masks, focal
planes, the optical train).

## Conventions

**Tweezer light is far-detuned and takes no transition's colour**: the pale
`TWEEZER_COLOR`. How brightly a trap is drawn is its power. A trap switched
off is not drawn.

**The array is drawn from its trackers.** `TweezerArray` rebuilds itself
every frame. Drive `on`, `filled`, `ringed`, `off` and `moved`; never
`FadeIn`, `FadeOut` or `Transform` it. Take `array.atoms` at the moment you
use it: each redraw makes new ones.

**Top-down and tilted are one array in two views.** The view is a
`TiltedView`; the trap drawing is `spot_trap` or `hourglass_trap`. An
elevation of `PI / 2` is the top-down picture exactly.

**Traps move at `TWEEZER_SPEED`**: a move's `run_time` is
`longest_move(plan) * scale / TWEEZER_SPEED`.

**Every focal plane is computed from the mask beside it.** Paint a
`FocalImage` from `focal_view(mask, amplitude)`; never draw spots by hand.

**Phase is coloured round a wheel** that wraps, so a 2π step shows no
edge. Put a `phase_wheel` on any scene that shows a mask, and clip a
pupil's mask to `round_aperture(HG_N)`, not to the light's amplitude: the
amplitude's edge is a staircase.

**Nothing is to scale**, and each scene's docstring says what is not: the
waist against the spacing, the Rayleigh range, the train's angles, the size
of the aberration.

## Recipes

### 1. An array loaded and rearranged

Worked example: `TweezerRearrangement`.

```python
from manim_atoms.tweezers.style import *
from manim_atoms.core.primitives import fluoresce
from manim_atoms.core.projection import TiltedView
from manim_atoms.tweezers.physics.rearrangement import (
    load_sites, longest_move, plan_rearrangement, square_sites)
from manim_atoms.tweezers.tools.tweezer_array import TweezerArray

sites, targets = square_sites(9, 9, 0.5), square_sites(5, 5, 0.5)
loaded = load_sites(len(sites), 0.5, np.random.default_rng(0))
plan = plan_rearrangement(sites, loaded, targets)      # raises if too few loaded
array = TweezerArray(sites, TiltedView(CENTER, SCALE))
self.add(*array.trackers, array)                       # trackers first
self.play(array.on.animate.set_value(1))
array.load(loaded)
self.play(array.filled.animate.set_value(1))
fluoresce(self, array.atoms)
array.rearrange(plan)
self.play(array.off.animate.set_value(1), array.ringed.animate.set_value(1))
self.play(array.moved.animate.set_value(1),
          run_time=longest_move(plan) * SCALE / TWEEZER_SPEED)
```

An odd block in an odd array sits on the array's own sites. An even block
in an odd array does not, and is still safe: the plan keeps traps at least
pitch/√2 apart whatever the block.

### 2. The same array from an angle

Worked example: `TweezerArray3D`.

```python
from manim_atoms.tweezers.tools.beams import (
    TW_AZIMUTH, TW_ELEVATION, focal_plane, hourglass_trap)

elevation, azimuth, shown = ValueTracker(PI / 2), ValueTracker(0), ValueTracker(0)
view = TiltedView(CENTER, SCALE, elevation, azimuth)
array = TweezerArray(sites, view, draw_trap=hourglass_trap)
array.on.set_value(1)                                  # lit from the start
plane = focal_plane(view, HALF, HALF, shown)
self.add(elevation, azimuth, shown, *array.trackers, plane, array)
self.play(elevation.animate.set_value(TW_ELEVATION),
          azimuth.animate.set_value(TW_AZIMUTH), shown.animate.set_value(1))
```

There is no perspective and no lighting: it is a projection on a flat
scene. With every trap lit the back rows' beams overlap; the picture is
clearest once the empty traps are off. To change how a beam looks, change
`TW_RAYLEIGH` (how fast it flares) and `TW_REACH` (how far it is drawn),
and compare candidates side by side in one still before choosing.

### 3. A mask beside the focal plane it makes

Worked example: `PhaseMaskBuildingBlocks`.

```python
from manim_atoms.core.holography import grating_phase, illumination, pupil_grid
from manim_atoms.core.optics import FocalImage, PhaseMask, round_aperture
from manim_atoms.tweezers.tools.holograms import HG_GAMMA, HG_N, focal_view

x, y, rho, _ = pupil_grid(HG_N)
amplitude, aperture = illumination(rho), round_aperture(HG_N)
periods = ValueTracker(0)
phase = lambda: grating_phase(x, y, periods.get_value(), 0)
mask = PhaseMask(phase(), aperture).set(height=4).move_to(LEFT * 3.4)
focal = FocalImage(focal_view(phase(), amplitude), FOCAL_SPOT_COLOR, gamma=HG_GAMMA)
focal.set(height=4).move_to(RIGHT * 3.4)
self.add(periods)
self.play(FadeIn(mask), FadeIn(focal))
mask.add_updater(lambda m: m.paint(phase()))           # after the fade, never before
focal.add_updater(lambda m: m.paint(focal_view(phase(), amplitude)))
self.play(periods.animate.set_value(7))
```

Don't animate a repainting picture's opacity: the repaint wins. Fade it in
first and add its updater after.

### 4. An array's mask, and an aberration

`iterate_hologram(x, y, amplitude, grid_spots(5, 5), steps)` returns the
mask before each step and the trap intensities under it; `uniformity` of
the last is 0.99 by forty steps, from 0.46. A wavefront error is a sum of
`zernike(n, m, rho, theta)` times an rms in radians; its Strehl ratio is
`strehl(error, amplitude)`; what the focal plane shows is
`focal_view(mask + error, amplitude)`. Keep the error near a radian in
all: at three, the Strehl ratio is 0.04 and there is no spot left to
sharpen. Worked examples: `HologramIteration`, `ZernikeCorrection`.

A scene that steps through by hand (`step.set_value(i)` then a `wait`)
must call `self.update_mobjects(0)` after the `set_value`, or the bars and
numbers that read the step stay one behind.

### 5. Light through lenses, side on

`beamlet(half_width, slope, start, lenses, end, axis, opacity)` is the
band between two rays traced through thin lenses (`trace_ray`). Put the
SLM a focal length before the first relay lens and the objective a focal
length after the second, and a tilt at the SLM becomes a shift of the
focus. Worked example: `OpticalTrain`.

## Before you finish

- At every stop, the caption says what the frame shows.
- Take a frame in the middle of every move, not only at the stops.
- Top-down: neighbouring spots do not merge, and an atom is told apart
  from its spot.
- Tilted: each beam fades to the background at both ends, and neighbours
  are separate once the empty traps are off.
- A loop's first and last frames are the same picture (`frames.py --final`
  is 0.3 s early: compare with the true last frame, or check the geometry).
- A focal-plane picture and what it is a picture of move the same way.
