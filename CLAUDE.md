# manim-atoms

commit and push frequently as you go.

Manim animations of atomic physics, as an installable package (`src/manim_atoms/`, `uv sync --all-extras` installs it editable): light-pulse atom interferometry, laser cooling and trapping, AION's science (gravitational waves and ultralight dark matter through a single-photon gradiometer, the prototype's signal injection and data), and a layer that turns any scene into a manim-slides slide. It began as the animation half of a talk (`github.com/taw181/qsim_visit`), which now depends on it.

## Layout

Topics depend one way only, `core` → `species` → {`interferometry`, `trapping`} → `aion`; `slides` depends on `core` alone. Never import upward or sideways: `interferometry` and `trapping` don't know each other, and nothing outside `aion` imports it.

- `style.py` — the core house style: every shared colour, stroke width, font size, and the pacing constant `V`. A topic's own palettes live in `<topic>/style.py`, which star-imports the core one (`aion/style.py` star-imports the interferometry and trapping ones); a topic's modules star-import their own topic's style. Add to a style module rather than hardcoding inline; a colour more than one topic uses goes in the core one.
- `core/` — building blocks: `primitives` (atoms, pulses, recoil, legs), `spacetime` (worldlines on one lab clock), `shapes` (Gaussian beams), `layout` (static-slide furniture), `citations`, `video`.
- `species/` — level schemes: `two_level` (a generic clock transition beside a figure), `strontium` (Sr levels and lines, `SrLevels`).
- `interferometry/`, `trapping/`, `aion/` — each has `tools/<module>.py` (helpers and the geometry they use; defaults bind at def time) and `scenes/<module>.py` (Scene classes and layout only they use), and where it has them `physics/` (numbers, no manim) and `plots/` (matplotlib figure builders).
  - The gradiometer is generic interferometry: `interferometry/scenes/gradiometer.py` holds `GradiometerBase` (two clouds, their arms, hands, dials and ports), `RunsContinuously` (the same on one lab clock) and the quiet `Gradiometer`. The AION scenes build on them: `GradiometerGW` (with `WaveRunsContinuously` for the wave-driven pulse timing), `LightShiftSignal`, `DarkMatterGradiometer`; `SignalInjection` is the prototype's lab picture behind the light-shift one.
- `slides/` — the only place `manim_slides` is imported (the `slides` extra): `deck.py` (`DeckSlide`, the `Clicks` / `RunsOnIntoLoops` / `LoopingStages` mixins, the deck file), `cli.py` (`manim-atoms-deck`), `player.py` (web player).
- `data/` — CSVs, images, video, read via `manim_atoms.resources.data_path`; sources and licences in `data/README.md`. `data_scripts/` regenerates them.
- `bibliography.py` — BibTeX entries formatted under a `CiteFormat` (`FULL`, `SHORT`, `AUTHOR_YEAR`; vary with `dataclasses.replace`); `core/citations.py` makes one a footer line.

## Slide stops

A scene calls a no-op hook where a presenter would stop — `beat()`, the sequence scenes' `stage_break()`, a self-running scene's `hold()` — and nothing else about slides. `slides.deck`'s mixins turn the hook into `next_slide()`, so a slide is `class XSlide(Clicks, SomeScene)`. Where a subclass rewrites `construct`/`fly` without `super()`, the hook calls go in both. A settling `wait` goes before a stop, never straight after one. Where the stops go: one once the apparatus and atoms are laid out; then one per pulse *and the legs it launches*, stopping as the atoms reach the next pulse; the recombination ends on the ports and readout; then one per annotation. The continuous variants (`*Continuous`) run the whole pulse sequence as one stretch.

## Working rules

- `uv run manim -ql src/manim_atoms/<topic>/scenes/<module>.py <Scene>` — run from the repo root so `manim.cfg` applies; `-qh` for final renders. Output: `media/videos/<module>/<quality>/<Scene>.mp4` (gitignored).
- After any change to a scene, render it at `-ql`, check the frames (the skill's `frames.py`), and for a pure refactor compare last frames (`-s`) against a render from before the change: they should be pixel-identical.
- Imports are absolute (`from manim_atoms.core.primitives import make_atom`), never relative: manim loads a scene file by path under a module name built from that path, so relative imports break. Star-import only `manim` and a style module; import names from topic modules explicitly, since they share names (`strain`, `GW_PERIOD`, ...).
- Every `__init__.py` imports nothing, or a scene file rendered by path gets loaded twice.
- A method looks up globals in the module that defines it: moving a scene or mixin means moving its imports too.
- Annotations belong where the physics happens: don't offset a recoil arrow off its atom to dodge an overlap — the overlap is fine.
- Measured data: `aion/plots/dai_fringes.py` → AION DAI fringes and Lissajous ellipse (Zenodo 19592552); `aion/plots/gw_sensitivity.py` → detector curves with merger tracks.
- Stage explicit paths when committing; don't `git add -A` over work in progress.
- The repo is private. Before it is ever made public, resolve every "check before redistributing" row in `data/README.md`.
- Render-and-check loop, colour sampling, manim traps: the `manim-atoms` skill.
