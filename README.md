# manim-atoms

[Manim](https://www.manim.community/) animations of atomic physics, with one house style.

| Topic | What's in it |
|---|---|
| `manim_atoms.interferometry` | Light-pulse atom interferometry: a single laser kick, Mach–Zehnder and single-photon sequences, the phase read off as a clock hand, the gradiometer (two interferometers, one laser), large momentum transfer, phase-shear readout, spin squeezing |
| `manim_atoms.trapping` | Laser cooling and trapping of Sr: the blue and red MOT stages, dipole-trap loading and spin polarisation, velocity slicing, a high-flux atom source, one shot of an experiment |
| `manim_atoms.aion` | AION: a gravitational wave or an ultralight dark-matter field passing through the gradiometer, signal injection by a light shift, LIGO, the GW sensitivity landscape, AEDGE, the km-scale detector, and the prototype's measured data |
| `manim_atoms.slides` | Any scene as a [manim-slides](https://github.com/jeertmans/manim-slides) slide, decks of them, and a web player |

Under them sit `manim_atoms.core` (atoms, pulses, worldlines, beams, layout, citations, video), `manim_atoms.species` (two-level and Sr level schemes) and `manim_atoms.style`.

## Install

```bash
uv add "manim-atoms[slides,plots] @ git+https://github.com/taw181/manim-atoms"
```

Manim needs Cairo, Pango and a LaTeX install (see manim's docs). The `slides` extra adds manim-slides; `plots` adds matplotlib for the static figures in `aion/plots`.

## Render a scene

Scenes are rendered by file path. From a clone:

```bash
uv sync --all-extras
uv run manim -ql src/manim_atoms/interferometry/scenes/mach_zehnder.py MachZehnder
uv run manim -ql src/manim_atoms/trapping/scenes/cooling.py CoolingSequence
uv run manim -ql src/manim_atoms/aion/scenes/gradiometer_gw.py GradiometerGWStretch
```

The repo's `manim.cfg` sets the dark background (`#101010`) the style is drawn for.

## Make slides

A scene calls `self.beat()` wherever a presenter would stop. The method does nothing on the scene, and the `Clicks` mixin turns each call into a slide break:

```python
# talk/slides.py
from pathlib import Path

from manim_atoms.bibliography import load_bibliography
from manim_atoms.interferometry.scenes.mach_zehnder import MachZehnder
from manim_atoms.slides import deck


class DeckSlide(deck.DeckSlide):
    DECK = deck.load_deck(Path(__file__).parent / "deck.txt")
    BIB = load_bibliography(Path(__file__).parent / "refs.bib")


class Clicks(deck.Clicks, DeckSlide): ...


class MachZehnderSlide(Clicks, MachZehnder):
    CITE = ("kasevichAtomicInterferometryUsing1991",)
```

`deck.txt` lists the slides in order, one per line. The footer draws a progress bar and a slide number from each slide's place in it. Then:

```bash
manim-atoms-deck --deck talk/deck.txt --slides talk/slides.py render -j 4 l
manim-atoms-deck --deck talk/deck.txt present
manim-atoms-deck --deck talk/deck.txt --html talk.html html
```

## Data

`src/manim_atoms/data/README.md` lists every dataset and image with its source and licence. `data_scripts/` regenerates them.
