---
name: manim-atoms
description: Create or edit manim animations in the manim-atoms package — atom interferometry, laser cooling and trapping, AION science, data plots and slides. Use this whenever the user asks for a manim animation, scene, or figure-in-motion, wants to add to or change an existing scene, or mentions animating atoms, laser pulses, traps or an interferometer — even if they just say "animate X" or "make a scene showing Y" without naming manim. It is the base for all manim work in this repo: how to build a scene here, where code goes, the render-and-check loop, and the manim traps. Load the family skill for the kind of scene too (interferometry-scenes, trapping-scenes, aion-scenes, data-plots, slides).
---

# Building scenes in manim-atoms

The repo is `manim-atoms` (uv, manim 0.21, Python 3.13): the package
`src/manim_atoms/`, layered `core` → `species` → {`interferometry`,
`trapping`} → `aion`. CLAUDE.md has the layout and the house rules. This
skill is how to work with them.

## The family skills

Load the one that matches the scene. Each has the recipes and physics
conventions for its kind of figure.

| Scene | Skill |
|---|---|
| atoms, pulses and arms on a space-time diagram: Mach–Zehnder, LMT, clock phase, gradiometer | `interferometry-scenes` |
| MOT stages, dipole traps, a staged sequence beside a level scheme and timeline | `trapping-scenes` |
| a gravitational wave or dark-matter field through the gradiometer, LIGO, signal injection | `aion-scenes` (with `interferometry-scenes`) |
| plots drawn in manim, matplotlib figures, the data behind them | `data-plots` |
| turning scenes into slides and decks | `slides` |
| a change meant to leave every picture as it was | `verify-refactor` |

## Building a scene, step by step

1. **Find what exists.** Read `docs/index.md`; it is organised by what you
   want to draw. Look names up in `docs/reference.md`. Open a source file
   only for the pieces you will use. Find the worked example nearest to
   your scene (the index's last sections list one per pattern) and read
   that scene: copying its structure beats inventing one.
2. **Decide where the code goes**, before writing it:
   - **core** — generic physics or drawing (a Bloch sphere, a cavity, a
     plot axis), even if only your scene uses it so far;
   - **`<topic>/tools/<module>.py`** — what is the topic's own;
   - **`<topic>/scenes/<module>.py`** — the Scene classes and the layout
     nothing else uses;
   - **`species/`** — a species' levels and its line colours.

   Never import from another scene module except to subclass its scene.
3. **Write the geometry block.** Named module constants, one prefix per
   scene (`MZ_*`, `CP_*`, `GR_*`), every position derived from a few of
   them, each commented with what it is and why it has that value.
   Tuning the scene later should mean editing this block, nothing else.
4. **Build from the helpers.** Never draw an atom, pulse, beam or level by
   hand: `make_atom`, `absorb`/`emit`, `draw_legs`, `gaussian_band`,
   `SrLevels` and their kin are what keep the figures one set.
5. **Pace by physics.** A leg's `run_time` is `distance / V`; a pulse
   climbs at `PULSE_SPEED`. Never hand-tune a run time on a moving atom.
6. **Put in the slide stops.** Call the no-op hooks a presenter would stop
   at: `beat()`, `stage_break()` or `hold()`. Define the hook on the scene
   as a no-op, or a wait for a settling pause. The `slides` skill says
   where the stops go.
7. **Render and look** (below), every beat, not just the end.
8. **Finish:**
   - every public function and class gets a docstring whose first
     paragraph says what it is;
   - a new public name goes under its need in `docs/index.md`;
   - run `python scripts/index.py --write` and commit `docs/reference.md`
     with the code. CI fails otherwise.

## A scene file

```python
"""One line: what the scene shows.

A paragraph: what the viewer should come away with, and the physics choices
the drawing makes (what is exaggerated, what is left out). Name the scenes
here and the stops each one makes.
"""

import numpy as np
from manim import *

from manim_atoms.interferometry.style import *      # the topic's style, star-imported
from manim_atoms.core.primitives import draw_legs, make_atom   # everything else by name

# --- my-scene geometry -------------------------------------------------------
# Why the figure is laid out like this: what has to stay clear of what.
MY_A = np.array([-5.0, -2.0, 0.0])  # the first pulse
MY_L = 3.0  # each leg's length in lab time
MY_B = MY_A + RIGHT * MY_L


class MyScene(Scene):
    """What it shows, in a sentence; then the stops it makes."""

    def beat(self):
        """The pause after each step: nothing here, a click on the slide version."""

    def construct(self):
        ...
```

Imports are absolute: manim loads a scene file by path, so relative imports
break. Star-import only `manim` and one style module. Topic modules share
names (`strain`, `make_strain_trace`), so import those by name. Package
`__init__.py` files import nothing.

## Style: where a constant goes

Pull every colour, width and size from a style module, never inline.

**Where a new constant goes:**
- in the topic's `style.py` if it is the topic's own;
- in core `style.py` only if it is generic and generically named;
- a species' line colours go with the species.

**If you want a value another topic happens to use**, define your own
constant with that value. Write `X = Y` only where X *is* Y
(`GW_SOURCE_COLOR = HORIZON_GLOW`: the dot is the black holes).

**When two things must be told apart on a projector**, sample them and
compare the RGB numbers, rather than trusting manim's colour names.

## You can't watch the video, so look at frames

Never call an animation good because it rendered without error.

```bash
uv run manim -ql src/manim_atoms/<topic>/scenes/<module>.py MyScene
.venv/bin/python .claude/skills/manim-atoms/scripts/frames.py \
    media/videos/<module>/480p15/MyScene.mp4 -t 3.6 7.8 --final -o /tmp/frames
```

Then Read the PNGs.

`scripts/stops.py <dotted module> <Scene>` prints the times just before
each of a scene's stops, ready to paste after `-t`.

**Which frames to take:** one per beat — each pulse, each leg, each stop,
the final state. A mobject can be right mid-flight and wrong at rest.

**Rendering:**
- `-ql` (480p15) takes seconds; `-qh` is for the final render;
- `-s` renders only the last frame;
- run from the repo root, so `manim.cfg` sets the background and `media/`;
- `manim --dry_run` runs `construct` without writing frames: the fastest
  way to find a crash.

**Check colours by sampling.** `frames.py --sample X,Y` prints the pixel at
scene coordinates. Manim's names mislead about perceptual distance:
- `BLUE_D` and `TEAL` sample as (93,152,167) and (126,195,175), all but
  identical at a 4 px stroke;
- `BLUE_D` and `PURPLE_B` give (84,158,177) and (172,147,188), which
  separate.

**Check what is crossed.** Anything at a pulse's x is crossed by the pulse:
a title, an arrow, a caption. That is invisible in code and obvious in a
frame. Annotations still belong on the atom they describe. Don't offset a
recoil arrow to dodge an overlap; move the title instead.

## Manim traps (each one has bitten this repo)

- **`TracedPath` vanishes when its point stops.** A trail drawn with it
  collapses during the closing `wait`. Use `draw_legs`, which creates a
  `Line` in step with the atom.
- **`Create` on a curve and an atom moved along it come apart.** `Create`
  paints by point index; the atom moves by arc length. On a bowed leg the
  atom trails the line by a fifth of the leg. `draw_wavy_legs` drives both
  from one parameter.
- **`Tex` wraps silently.** Text longer than LaTeX's line width (about 11
  units at caption size) breaks onto a second line on its own. Break lines
  yourself with `\\`, and check `.width` and `.height` of anything long.
- **A changing number moves.** `DecimalNumber` and `Integer` are placed by
  their centre, and their height changes with the digits. `1,000` is 25%
  taller than `42`, because the comma hangs below the line. Pass
  `group_with_commas=False` to anything that counts. Place it with
  `next_to(label, RIGHT, aligned_edge=DOWN)` in an updater, not
  `move_to`.
- **`Scene.play` kwargs apply to every animation in the call.**
  `run_time=` on a play with a quarter-second `Flash` stretches the flash
  too. Put pacing on the animation that needs it (`core.spacetime.run_to`
  does).
- **A `ValueTracker`'s updaters only run if it is in the scene.** It must
  be added *before* the mobjects that read it, or they lag a frame.
  `self.add(tracker)` first.
- **`Flash` snapshots its target's centre when built.** On a moving atom
  the ring is left behind. Flash the point where the event happens (the
  vertex), not the atom.
- **A `DashedLine` rebuilt every frame shimmers.** Its dashes reshuffle.
  Put a dashed reference on whole.
- **A zero-length `ParametricFunction` fails.** Clamp a growing curve's
  parameter to at least `1e-4`; `growing_trail` does.
- **`draw_wavy_legs` clears the atoms' updaters when it ends.** Don't mix
  it with `carry` on the same atom.
- **A method looks up globals in the module that defines it.** Moving a
  scene or mixin means moving its imports too.
- **Parallel renders share `media/Tex`.** Several manim processes at once
  should each get their own `--media_dir`; the `verify-refactor` scripts
  do this.
- **Manim 0.21 has `DEGREES`, not `DEG`.**
