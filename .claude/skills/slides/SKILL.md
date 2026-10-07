---
name: slides
description: Turn manim-atoms scenes into manim-slides slides and decks — where a scene should stop for the presenter, the beat/stage_break/hold hooks, the Clicks, RunsOnIntoLoops and LoopingStages mixins, citations and the footer, the deck file, and rendering, presenting or exporting a deck with manim-atoms-deck. Use it whenever a scene is going into a talk, a slide's stops are wrong, or the user mentions slides, a deck, a presentation, a click or a loop.
---

# Slides

Read the base `manim-atoms` skill first.
- A **scene** knows nothing about slides beyond calling a no-op hook where
  a presenter would stop.
- A **slide** is that scene with a mixin in front that turns the hook into
  a stop.
- A **deck** is a file listing slides in order.
- `manim_atoms.slides` is the only place `manim_slides` is imported (the
  `slides` extra).

## Where a scene stops

A scene calls one of three hooks, and defines it on itself as a no-op (or a
settling `wait`):

| Hook | For | On the slide |
|---|---|---|
| `beat()` | an explainer that waits for the presenter | `Clicks`: a plain stop |
| `stage_break()` | a sequence of stages, each held while it is talked through | `LoopingStages`: loops two seconds of the stage until the click |
| `hold()` | a scene that runs by itself, e.g. a field oscillating; plays exactly one period | the slide loops it: `self.loop(super().hold)` |

**Where the stops go, in an interferometry explainer:**
1. one once the apparatus and atoms are laid out;
2. one per pulse *and the legs it launches*, stopping as the atoms reach
   the next pulse;
3. the recombination, ending on the ports and readout;
4. one per annotation after that.

**The continuous variants (`*Continuous`)** run the whole pulse sequence
as one stretch, with no stop inside it.

**Rules that keep stops clean:**
- **A settling `wait` goes before a stop, never straight after one.** The
  frame the presenter talks over should be the finished one, and a wait
  after the stop is dead time after the click.
- **Where a subclass rewrites `construct` or `fly` without calling
  `super()`, the hook calls go in both.**
- **A `hold()` plays exactly one period**, so it ends on the frame it
  started on and loops without a jump.
- **Never stop inside a lab-clock stretch** (between a continuous scene's
  first pulse and last). A stop freezes the clock, and the clock not
  stopping is what the scene is for.

## Making slides

A talk configures the deck once, then each slide is a one-liner:

```python
# talk/slides.py
from pathlib import Path

from manim_atoms.bibliography import load_bibliography
from manim_atoms.slides import deck
from manim_atoms.interferometry.scenes.mach_zehnder import MachZehnder
from manim_atoms.trapping.scenes.slicing import VelocitySlicing
from manim_atoms.aion.scenes.uldm import DarkMatterField


class DeckSlide(deck.DeckSlide):
    DECK = deck.load_deck(Path(__file__).parent / "deck.txt")   # footer: progress, number
    BIB = load_bibliography(Path(__file__).parent / "refs.bib")


class Clicks(deck.Clicks, DeckSlide): ...
class RunsOnIntoLoops(deck.RunsOnIntoLoops, DeckSlide): ...
class LoopingStages(deck.LoopingStages, RunsOnIntoLoops): ...


class MachZehnderSlide(Clicks, MachZehnder):          # beat() -> a stop
    CITE = ("kasevichAtomicInterferometryUsing1991",)   # keys into BIB, bottom left


class VelocitySlicingSlide(LoopingStages, VelocitySlicing): ...   # stage_break() -> a loop


class DarkMatterFieldSlide(RunsOnIntoLoops, DarkMatterField):
    def hold(self):
        self.loop(super().hold)                          # one period, looped until the click
```

- **The mixin goes first** in the bases, so its hook overrides the scene's
  no-op.
- **`CITE`** holds keys into `BIB`, one line each. Tuples
  `(label, key, ...)` run on together as "label: Author et al. (year)".
- **`CITE_CORNER`** moves the citation off something it would cover.
- **`CITE_FORMAT`** (a `bibliography.CiteFormat`; vary it with
  `dataclasses.replace`) changes how references read.

```
# talk/deck.txt: the slides in order, one class per line; # starts a comment
MachZehnderSlide
VelocitySlicingSlide
extra_slides/backup.py: BackupSlide     # played in place, but not numbered
DarkMatterFieldSlide
```

## Rendering and presenting

Run from the project root so its `manim.cfg` applies:

```bash
manim-atoms-deck --deck talk/deck.txt --slides talk/slides.py render -j 4 l   # l, m or h
manim-atoms-deck --deck talk/deck.txt present
manim-atoms-deck --deck talk/deck.txt --html talk.html html
manim-atoms-deck --deck talk/deck.txt player out/      # a phone-friendly web player
```

- **`render`** renders the whole deck, or only the slides named after the
  quality.
- **`-j N`** renders N slides at once and logs each to
  `media/deck_logs/<Slide>.log`.
- **The default frame rate is 30**; `l` keeps its 15.
- **manim-slides writes `slides/<Slide>.json`** in the working directory.
  In this repo `/slides/` is gitignored.

**Checking a slide's stops.** `--dry_run` doesn't work on a slide:
`next_slide()` needs the movie segments a dry run never opens. Render it
at `l` instead, then read `slides/<Slide>.json`:
- the number of entries is the number of stops;
- a looping stop is a run-on entry (`auto_next`) followed by a `loop`
  entry.

Then look at the last frame of each segment, as the base skill says. That
is the frame the audience sees while you talk.
