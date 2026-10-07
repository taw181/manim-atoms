# manim-atoms

commit and push frequently as you go.

Manim animations of atomic physics, as an installable package (`src/manim_atoms/`, `uv sync --all-extras` installs it editable): light-pulse atom interferometry, laser cooling and trapping, AION's science (gravitational waves and ultralight dark matter through a single-photon gradiometer, the prototype's signal injection and data), and a layer that turns any scene into a manim-slides slide. It began as the animation half of a talk (`github.com/taw181/qsim_visit`), which now depends on it.

## Layout

To find what exists, read `docs/index.md` before any source: it is organised by what you want to draw (curved arms, a pulse from above, a Bloch sphere, ...) and names the module and function for each. `docs/reference.md` is every module and public name with its signature and docstring, generated from the source; look a name up there before opening its file.

Topics depend one way only, `core` → `species` → {`interferometry`, `trapping`} → `aion`; `slides` depends on `core` alone. Never import upward or sideways: `interferometry` and `trapping` don't know each other, and nothing outside `aion` imports it.

A tool lives at the level of the most general concept it draws, not with the first scene that needed it. Generic physics and drawing go in `core/` even while one topic uses them (a Bloch sphere is not interferometry's; a cavity is not squeezing's); a topic's `tools/` holds what is that topic's own, and its scenes *use* core rather than owning copies. A scene module holds its Scene classes and the layout only they use: anything another scene needs moves to `tools/`, and no scene module imports from another except to subclass a scene.

- `style.py` — the core house style: what core uses and what more than one topic shares (the shared palette, stroke widths, font sizes, the pacing constant `V`). What one topic alone uses lives in `<topic>/style.py`, which star-imports the core one (`aion/style.py` star-imports the interferometry and trapping ones); a topic's modules star-import their own topic's style. Add to a style module rather than hardcoding inline; when a second topic starts using a topic's constant, move it to the core one.
- `core/` — building blocks: `primitives` (atoms, absorb/emit, recoil, legs, kets and the state legend), `spacetime` (worldlines on one lab clock), `bloch` (the Bloch sphere, spin noise), `optics` (Gaussian beams, cavities), `plots` (log-log axes, fast scatters), `layout` (static-slide furniture), `citations`, `video`.
- `species/` — level schemes: `two_level` (a generic clock transition beside a figure), `strontium` (Sr levels and lines, `SrLevels`).
- `interferometry/`, `trapping/`, `aion/` — each has `tools/<module>.py` (helpers and the geometry they use; defaults bind at def time) and `scenes/<module>.py` (Scene classes and layout only they use), and where it has them `physics/` (numbers, no manim) and `plots/` (matplotlib figure builders).
  - `interferometry/tools/pulses.py` draws every pulse on a space-time diagram (with or without light travel time, from below or above); `interferometry/tools/pulse_sequence.py` is the arm-bookkeeping engine that steps an atom through a pulse sequence.
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
- Every public function, class and module has a docstring whose first paragraph says what it is. A new public function or class in a non-scene module, or a new Scene class, goes in `docs/index.md` under the need it serves. Then run `python scripts/index.py --write` and commit `docs/reference.md` with it. CI runs `python scripts/index.py`, which fails on a stale reference, an unindexed name, a missing docstring, or an index entry that no longer exists.
- The repo is private. Before it is ever made public, resolve every "check before redistributing" row in `data/README.md`.
- Render-and-check loop, colour sampling, manim traps: the `manim-atoms` skill.
