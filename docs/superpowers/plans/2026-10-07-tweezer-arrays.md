# Tweezer Arrays and SLM Light Delivery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `tweezers` topic to manim-atoms: a tweezer array rearranged by SLM hologram updates, seen top-down and from an angle, and four scenes on how the SLM delivers the light (optical train, phase masks, hologram iteration, Zernike correction), plus one scene joining the two.

**Architecture:** Numbers first, with no manim: the rearrangement plan in `tweezers/physics/` and the holography in `core/holography.py`. Drawing on top: `core/projection.py` (a tilted orthographic view), additions to `core/optics.py` (phase-mask and focal-plane pictures, lens, SLM), and `tweezers/tools/` (the array, the beam, the hologram scenes' layout). Scenes in `tweezers/scenes/` only choreograph.

**Tech Stack:** Python 3.13, manim 0.21 (Cairo), numpy, scipy (`linear_sum_assignment`), pytest, uv.

**Spec:** `docs/superpowers/specs/2026-10-07-tweezer-arrays-design.md`

**State of the code in this plan:** every module and test below was drafted outside the repo before the plan was written. The tests pass (133) and every scene completes a `--dry_run`. No scene has been rendered and looked at: the geometry constants are first guesses, and tuning them from frames is the work that remains in each scene task.

## Global Constraints

- Layering: `core` → `species` → {`interferometry`, `trapping`, `tweezers`} → `aion`. `tweezers` imports `core` only. It never imports `trapping`, `interferometry` or `aion`, and nothing imports `tweezers`.
- Imports are absolute (`from manim_atoms.core.optics import PhaseMask`). Star-import only `manim` and one style module.
- Every `__init__.py` is empty.
- Colours, widths and font sizes come from a style module, never inline. A tweezer constant goes in `tweezers/style.py`; only generic, generically named ones go in `style.py`.
- Every public function, class and module has a docstring whose first paragraph says what it is.
- Every new public function or class, and every Scene class, is cited in `docs/index.md`; `python scripts/index.py --write` regenerates `docs/reference.md`; `python scripts/index.py` must pass before each commit, because CI runs it on every push.
- Before starting: `uv sync --all-extras`. Run manim from the repo root so `manim.cfg` applies. Manim 0.21 has `DEGREES`, not `DEG`.
- Several manim processes at once each need their own `--media_dir`.
- Commit and push after each task. Stage explicit paths; never `git add -A` (an untracked `.gitlab/` directory is not part of this work).
- Work on branch `tweezer-arrays`. End every commit message with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- A scene is not done because it rendered. Read a frame at every stop.

## Review Focus

Conditions the spec implies but does not spell out, each pinned by a test in the task that owns the code:

1. **Fewer atoms load than the block needs** (a different seed, fill or size): `plan_rearrangement` raises a `ValueError` naming both counts, instead of drawing a block with holes. Task 1, `test_too_few_atoms_is_an_error`.
2. **An array or block that is not the default** (non-square, a single row, a block off the array's lattice): the plan is still safe. Task 1, `test_any_shape_of_array_and_block_is_safe_even_off_the_lattice`.
3. **A spot the mask leaves dark** during iteration: its weight stays finite, no division by zero. Task 2, `test_a_dark_spot_keeps_its_weight`.
4. **A phase outside 0 to 2π** (negative, or many turns): the picture wraps it. Task 7, `test_a_mask_is_clipped_to_its_aperture_and_repaints` and `test_the_wheel_wraps`.
5. **The tilted view brought back to straight above**: the beam's two halves have no height; they are left out and the trap is its spot. Task 6, `test_looking_straight_down_the_hourglass_is_only_its_spot`.

## File Structure

| File | Responsibility |
|---|---|
| `src/manim_atoms/tweezers/physics/rearrangement.py` | Sites, loading, the plan. Numbers only. |
| `src/manim_atoms/core/holography.py` | Zernike modes, masks, focal plane, Gerchberg–Saxton. Numbers only. |
| `src/manim_atoms/core/projection.py` | `TiltedView`. |
| `src/manim_atoms/style.py` (modify) | The phase wheel's stops; lens and SLM styles. |
| `src/manim_atoms/core/optics.py` (modify) | `PhaseMask`, `FocalImage`, `phase_wheel`, `make_lens`, `make_slm`. |
| `src/manim_atoms/tweezers/style.py` | The tweezer scenes' constants. |
| `src/manim_atoms/tweezers/tools/tweezer_array.py` | `TweezerArray`, `spot_trap`, the scenes' heading and caption. |
| `src/manim_atoms/tweezers/tools/beams.py` | `hourglass_trap`, `focal_plane`. |
| `src/manim_atoms/tweezers/tools/holograms.py` | The hologram scenes' sampling, pictures' layout, bars, ray tracing. |
| `src/manim_atoms/tweezers/scenes/rearrangement.py` | `TweezerRearrangement`, `TweezerRearrangementLoop`. |
| `src/manim_atoms/tweezers/scenes/array_3d.py` | `TweezerArray3D`, `TweezerArray3DLoop`. |
| `src/manim_atoms/tweezers/scenes/holography.py` | `PhaseMaskBuildingBlocks`, `HologramIteration`, `ZernikeCorrection`, `OpticalTrain`. |
| `src/manim_atoms/tweezers/scenes/rearrangement_hologram.py` | `RearrangementHologram`. |
| `.claude/skills/manim-atoms/scripts/stops.py` | Prints a scene's stop times, for the frame check. |
| `tests/test_rearrangement.py`, `test_holography.py`, `test_projection.py`, `test_tweezer_array.py`, `test_tweezer_beams.py`, `test_phase_colors.py`, `test_tweezer_holograms.py` | One per module above. |

Modules are named `rearrangement` and `tweezer_array`, never `array`: manim loads a scene file under a module name taken from its path, and a module called `array` would shadow the standard library's.

## Order

Tasks 1–4 are the foundation and run in order. After them there are three independent tracks: Task 5 (2D), Task 6 (3D), Tasks 7–11 (light, in order). Task 12 needs Tasks 5 and 8. Task 13 is last. The tracks all edit `docs/index.md` and `tweezers/style.py`; if they run in parallel, merge those two by hand and regenerate `docs/reference.md`.

## The frame check, used by every scene task

```bash
uv run manim -ql src/manim_atoms/tweezers/scenes/<module>.py <Scene>
STOPS=$(uv run python .claude/skills/manim-atoms/scripts/stops.py manim_atoms.tweezers.scenes.<module> <Scene>)
.venv/bin/python .claude/skills/manim-atoms/scripts/frames.py \
    media/videos/<module>/480p15/<Scene>.mp4 -t $STOPS --final -o /tmp/frames/<Scene>
```

Then Read every PNG. `stops.py` is created in Task 4.

---

### Task 1: The `tweezers` topic and the rearrangement plan

**Files:**
- Create: `src/manim_atoms/tweezers/__init__.py`, `src/manim_atoms/tweezers/physics/__init__.py`, `src/manim_atoms/tweezers/tools/__init__.py`, `src/manim_atoms/tweezers/scenes/__init__.py` (all empty)
- Create: `src/manim_atoms/tweezers/physics/rearrangement.py`
- Test: `tests/test_rearrangement.py`
- Modify: `scripts/index.py:48` (`LAYERS`), `docs/index.md`, `docs/reference.md` (generated)

**Interfaces:**
- Consumes: nothing.
- Produces:
  - `square_sites(rows, cols, pitch) -> ndarray (rows*cols, 2)`, row by row from the top left, centred on the origin.
  - `load_sites(n, fill, rng) -> ndarray of bool (n,)`; `rng` is a `numpy.random.Generator`.
  - `plan_rearrangement(sites, loaded, targets) -> Plan`; raises `ValueError` if fewer atoms than targets.
  - `Plan(kept, start, end, dropped)`: `kept` and `dropped` are index arrays into `sites`; `start` and `end` are `(len(kept), 2)`.
  - `positions(plan, share) -> ndarray (len(kept), 2)`.
  - `longest_move(plan) -> float`.

- [ ] **Step 1: Create the empty package files**

```bash
mkdir -p src/manim_atoms/tweezers/physics src/manim_atoms/tweezers/tools src/manim_atoms/tweezers/scenes
touch src/manim_atoms/tweezers/__init__.py src/manim_atoms/tweezers/physics/__init__.py \
      src/manim_atoms/tweezers/tools/__init__.py src/manim_atoms/tweezers/scenes/__init__.py
```

- [ ] **Step 2: Write the failing tests**

`tests/test_rearrangement.py`:

```python
"""The rearrangement plan against what moving every trap at once demands: no
atom lost or invented, every target filled, and no two traps ever close.
Pure numbers: nothing here renders."""

import numpy as np
import pytest

from manim_atoms.tweezers.physics.rearrangement import (
    load_sites, longest_move, plan_rearrangement, positions, square_sites,
)

PITCH = 0.5
SITES = square_sites(9, 9, PITCH)
TARGETS = square_sites(5, 5, PITCH)


def loaded_for(seed, fill=0.5):
    return load_sites(len(SITES), fill, np.random.default_rng(seed))


def test_sites_are_centred_and_run_from_the_top_left():
    assert np.allclose(SITES.mean(axis=0), 0)
    assert np.allclose(SITES[0], [-4 * PITCH, 4 * PITCH])
    assert np.allclose(SITES[1] - SITES[0], [PITCH, 0])
    assert np.allclose(SITES[9] - SITES[0], [0, -PITCH])


def test_loading_is_repeatable_and_near_the_fill():
    assert np.array_equal(loaded_for(3), loaded_for(3))
    assert 0.4 < np.mean([loaded_for(s).mean() for s in range(200)]) < 0.6


SEEDS = [s for s in range(40) if loaded_for(s).sum() >= len(TARGETS)]


@pytest.mark.parametrize("seed", SEEDS)
def test_plan_fills_every_target_once_and_conserves_atoms(seed):
    loaded = loaded_for(seed)
    plan = plan_rearrangement(SITES, loaded, TARGETS)
    assert len(plan.kept) == len(TARGETS)
    assert sorted(map(tuple, plan.end)) == sorted(map(tuple, TARGETS))
    assert np.allclose(plan.start, SITES[plan.kept])
    assert sorted([*plan.kept, *plan.dropped]) == list(np.flatnonzero(loaded))
    assert np.allclose(positions(plan, 0), plan.start)
    assert np.allclose(positions(plan, 1), plan.end)


@pytest.mark.parametrize("seed", SEEDS)
def test_traps_moved_together_stay_apart(seed):
    plan = plan_rearrangement(SITES, loaded_for(seed), TARGETS)
    closest = np.inf
    for share in np.linspace(0, 1, 201):
        p = positions(plan, share)
        d = np.linalg.norm(p[:, None] - p[None, :], axis=-1)
        closest = min(closest, d[~np.eye(len(p), dtype=bool)].min())
    assert closest >= PITCH / np.sqrt(2) - 1e-9


def test_too_few_atoms_is_an_error():
    loaded = np.zeros(len(SITES), dtype=bool)
    loaded[:10] = True
    with pytest.raises(ValueError, match="10 atoms loaded for 25"):
        plan_rearrangement(SITES, loaded, TARGETS)


def test_a_full_block_already_in_place_does_not_move():
    loaded = np.array([any(np.allclose(s, t) for t in TARGETS) for s in SITES])
    plan = plan_rearrangement(SITES, loaded, TARGETS)
    assert longest_move(plan) == 0 and len(plan.dropped) == 0


def test_no_targets_drops_everything():
    plan = plan_rearrangement(SITES, loaded_for(0), np.empty((0, 2)))
    assert len(plan.kept) == 0 and longest_move(plan) == 0
    assert positions(plan, 0.5).shape == (0, 2)


@pytest.mark.parametrize("shape, block", [((6, 8), (3, 4)), ((4, 4), (3, 3)), ((1, 7), (1, 3))])
def test_any_shape_of_array_and_block_is_safe_even_off_the_lattice(shape, block):
    sites, targets = square_sites(*shape, PITCH), square_sites(*block, PITCH)
    plan = plan_rearrangement(sites, np.ones(len(sites), dtype=bool), targets)
    assert len(plan.kept) == len(targets) and len(plan.dropped) == len(sites) - len(targets)
    for share in np.linspace(0, 1, 101):
        p = positions(plan, share)
        d = np.linalg.norm(p[:, None] - p[None, :], axis=-1)
        if len(p) > 1:
            assert d[~np.eye(len(p), dtype=bool)].min() >= PITCH / np.sqrt(2) - 1e-9
```

- [ ] **Step 3: Run them to see them fail**

Run: `uv run pytest tests/test_rearrangement.py -q`
Expected: collection error, `ModuleNotFoundError: No module named 'manim_atoms.tweezers.physics.rearrangement'`.

- [ ] **Step 4: Write the module**

`src/manim_atoms/tweezers/physics/rearrangement.py`:

```python
"""A tweezer array's numbers: its sites, which of them load, and the moves
that rearrange the loaded ones into a defect-free block.

No manim. square_sites lays the traps out, load_sites says which caught an
atom, plan_rearrangement pairs loaded traps with target sites, and positions
is where every kept trap is a share of the way through the move. Every trap
moves at once along a straight line, as it does when the SLM's hologram is
updated.
"""

from dataclasses import dataclass

import numpy as np
from scipy.optimize import linear_sum_assignment


@dataclass(frozen=True)
class Plan:
    """A rearrangement: the traps kept, where each starts and ends, and the
    loaded traps dropped as surplus. ``kept`` and ``dropped`` index the sites;
    ``start`` and ``end`` are (len(kept), 2), in ``kept``'s order."""

    kept: np.ndarray
    start: np.ndarray
    end: np.ndarray
    dropped: np.ndarray


def square_sites(rows, cols, pitch):
    """The (rows * cols, 2) positions of a square lattice of traps ``pitch``
    apart, centred on the origin, row by row from the top left."""
    xs = (np.arange(cols) - (cols - 1) / 2) * pitch
    ys = ((rows - 1) / 2 - np.arange(rows)) * pitch
    return np.array([[x, y] for y in ys for x in xs], dtype=float)


def load_sites(n, fill, rng):
    """Which of n traps caught an atom, each with probability ``fill``.
    ``rng`` is a numpy Generator, seeded so a scene loads the same way every
    render."""
    return rng.random(n) < fill


def plan_rearrangement(sites, loaded, targets):
    """Pair loaded traps with target sites so the summed squared distance is
    least, and drop the loaded traps left over.

    Least squared distance is what makes moving every trap at once safe: no
    pair of moves could be swapped for a shorter one, so no two traps ever
    coincide on the way, and two that start and end at least a pitch apart
    stay at least pitch / sqrt(2) apart throughout."""
    sites = np.asarray(sites, dtype=float)
    targets = np.asarray(targets, dtype=float)
    loaded = np.flatnonzero(np.asarray(loaded, dtype=bool))
    if len(loaded) < len(targets):
        raise ValueError(f"{len(loaded)} atoms loaded for {len(targets)} target sites")
    cost = ((sites[loaded][:, None, :] - targets[None, :, :]) ** 2).sum(axis=-1)
    rows, cols = linear_sum_assignment(cost)
    kept = loaded[rows]
    return Plan(kept=kept, start=sites[kept], end=targets[cols],
                dropped=np.setdiff1d(loaded, kept))


def positions(plan, share):
    """Every kept trap ``share`` of the way from its start to its end."""
    return (1 - share) * plan.start + share * plan.end


def longest_move(plan):
    """The farthest any kept trap travels: what sets how long the move takes."""
    if len(plan.kept) == 0:
        return 0.0
    return float(np.linalg.norm(plan.end - plan.start, axis=1).max())
```

Why squared distance: if two kept traps i and j ever coincided on the way, then (aᵢ − aⱼ)·(bᵢ − bⱼ) < 0 for their starts a and ends b, and swapping their targets would lower the summed squared distance by twice that product. The optimum admits no such swap, so the product is never negative, and the squared separation at share s is at least (1 − s)²p² + s²p² ≥ p²/2.

- [ ] **Step 5: Run the tests**

Run: `uv run pytest tests/test_rearrangement.py -q`
Expected: all pass (about 90, most of them the parametrised seeds).

- [ ] **Step 6: Register the topic with the index**

In `scripts/index.py`, change

```python
LAYERS = ["style", "core", "species", "interferometry", "trapping", "aion",
          "slides", "bibliography", "resources"]
```

to

```python
LAYERS = ["style", "core", "species", "interferometry", "trapping", "tweezers", "aion",
          "slides", "bibliography", "resources"]
```

In `docs/index.md`, in "How the pieces fit", change the Layers bullet's first sentence to:

```markdown
- **Layers.** Imports run one way only: `core` → `species` → {`interferometry`, `trapping`, `tweezers`} → `aion`. `slides` depends on `core` alone. Each topic has these parts:
```

and add a new section between "Trapping apparatus" and "Timelines and staged sequences":

```markdown
## Tweezer arrays

- **The array's numbers**: its sites, which of them load, and the plan that rearranges the loaded ones into a block, every trap moving at once. `tweezers.physics.rearrangement`: `square_sites`, `load_sites`, `plan_rearrangement`, `Plan`, `positions`, `longest_move`.
```

- [ ] **Step 7: Regenerate the reference and check**

Run: `python scripts/index.py --write && python scripts/index.py`
Expected: `docs/index.md and docs/reference.md are up to date.`

- [ ] **Step 8: Commit and push**

```bash
git add src/manim_atoms/tweezers tests/test_rearrangement.py scripts/index.py docs/index.md docs/reference.md
git commit -m "tweezers: the topic, and the plan that rearranges an array"
git push
```

---

### Task 2: Holography numbers

**Files:**
- Create: `src/manim_atoms/core/holography.py`
- Test: `tests/test_holography.py`
- Modify: `docs/index.md`, `docs/reference.md` (generated)

**Interfaces:**
- Consumes: nothing.
- Produces (all arrays are `(n, n)` over the pupil unless said):
  - `pupil_grid(n) -> (x, y, rho, theta)`; row 0 is y = +1.
  - `illumination(rho, waist=None) -> amplitude`.
  - `osa_to_nm(j) -> (n, m)`; `zernike(n, m, rho, theta)`; `ZERNIKE_NAMES: dict[(n, m), str]`.
  - `grating_phase(x, y, kx, ky)`; `lens_phase(rho, waves)`.
  - `spot_phase(x, y, spots, phases=None, weights=None)`; `spots` is `(M, 2)` of `(kx, ky)` in diffraction limits.
  - `far_field(phase, amplitude, pad=4) -> (pad*n, pad*n)` intensity, a flat mask peaking at 1.
  - `spot_pixel(spot, n, pad=4) -> (row, col)`.
  - `spot_fields(phase, amplitude, x, y, spots) -> complex (M,)`.
  - `wgs_step(phase, weights, amplitude, x, y, spots, weighted=True) -> (phase, weights, intensities)`.
  - `gs_step(phase, amplitude, x, y, spots) -> (phase, intensities)`.
  - `uniformity(intensities) -> float`; `strehl(phase_error, amplitude) -> float`.

- [ ] **Step 1: Write the failing tests**

`tests/test_holography.py`:

```python
"""The holography numbers against the optics: a grating steers the spot by its
periods, a lens blurs it, the Zernike modes are orthonormal, weighted
Gerchberg-Saxton evens an array out. Pure numbers: nothing here renders."""

import numpy as np
import pytest

from manim_atoms.core.holography import (
    ZERNIKE_NAMES, far_field, grating_phase, gs_step, illumination, lens_phase, osa_to_nm,
    pupil_grid, spot_fields, spot_phase, spot_pixel, strehl, uniformity, wgs_step, zernike,
)

N = 64
X, Y, RHO, THETA = pupil_grid(N)
A = illumination(RHO)
GRID = np.array([[kx, ky] for ky in (-8, -4, 0, 4, 8) for kx in (-8, -4, 0, 4, 8)], float)


def test_osa_index_counts_along_the_pyramid_rows():
    assert [osa_to_nm(j) for j in range(6)] == [(0, 0), (1, -1), (1, 1), (2, -2), (2, 0), (2, 2)]
    assert osa_to_nm(12) == (4, 0)
    assert all(osa_to_nm(j) in ZERNIKE_NAMES for j in range(15))


def test_zernike_modes_are_orthonormal_over_the_disc():
    _, _, rho, theta = pupil_grid(256)
    inside = rho <= 1
    modes = np.array([zernike(*osa_to_nm(j), rho, theta)[inside] for j in range(15)])
    gram = modes @ modes.T / inside.sum()
    assert np.allclose(gram, np.eye(15), atol=0.03)


def test_zernike_rejects_a_mode_that_does_not_exist():
    with pytest.raises(ValueError):
        zernike(2, 1, RHO, THETA)


def test_flat_mask_peaks_at_one_on_the_axis():
    image = far_field(np.zeros((N, N)), A)
    assert np.unravel_index(image.argmax(), image.shape) == spot_pixel((0, 0), N)
    assert image.max() == pytest.approx(1.0)


@pytest.mark.parametrize("spot", [(5, 0), (0, 7), (5, -3), (-6, 2)])
def test_grating_moves_the_spot_by_its_periods(spot):
    image = far_field(grating_phase(X, Y, *spot), A)
    assert np.unravel_index(image.argmax(), image.shape) == spot_pixel(spot, N)
    assert image.max() == pytest.approx(1.0, abs=1e-6)


def test_lens_lowers_the_peak_in_the_focal_plane():
    image = far_field(lens_phase(RHO, 1.0), A)
    assert image.max() < 0.2


def test_phase_is_only_meaningful_mod_two_pi():
    phase = grating_phase(X, Y, 3, 2)
    assert np.allclose(far_field(phase, A), far_field(np.mod(phase, 2 * np.pi) - 40 * np.pi, A))


def test_strehl_is_one_flat_and_follows_marechal_when_small():
    assert strehl(np.zeros((N, N)), A) == pytest.approx(1.0)
    error = 0.3 * zernike(2, 0, RHO, THETA)
    assert strehl(error, A) == pytest.approx(np.exp(-0.09), abs=0.01)
    assert far_field(error, A)[spot_pixel((0, 0), N)] == pytest.approx(strehl(error, A))


def test_weighted_gs_evens_the_spots_out():
    rng = np.random.default_rng(1)
    start = spot_phase(X, Y, GRID, rng.uniform(0, 2 * np.pi, len(GRID)))
    plain = weighted = start
    weights = np.ones(len(GRID))
    for _ in range(30):
        plain, _ = gs_step(plain, A, X, Y, GRID)
        weighted, weights, _ = wgs_step(weighted, weights, A, X, Y, GRID)
    first = np.abs(spot_fields(start, A, X, Y, GRID)) ** 2
    gs = np.abs(spot_fields(plain, A, X, Y, GRID)) ** 2
    wgs = np.abs(spot_fields(weighted, A, X, Y, GRID)) ** 2
    assert uniformity(wgs) > 0.95
    assert uniformity(wgs) > uniformity(gs) > uniformity(first)


def test_spot_intensities_match_the_far_field():
    mask = spot_phase(X, Y, GRID[:3])
    image = far_field(mask, A)
    direct = np.abs(spot_fields(mask, A, X, Y, GRID[:3])) ** 2
    assert np.allclose([image[spot_pixel(s, N)] for s in GRID[:3]], direct)


def test_one_spot_and_plain_lists_are_fine():
    mask, weights, intensity = wgs_step(np.zeros((N, N)), [1.0], A, X, Y, [(4, 0)])
    assert weights == pytest.approx([1.0])
    assert far_field(mask, A)[spot_pixel((4, 0), N)] == pytest.approx(1.0)
    assert spot_phase(X, Y, [(4, 0)]).shape == (N, N)


def test_a_dark_spot_keeps_its_weight():
    # a grating aimed at (4, 0) puts nothing on a spot at (-9, 9)
    mask = grating_phase(X, Y, 4, 0)
    _, weights, intensity = wgs_step(mask, [1.0, 1.0], A, X, Y, [(4, 0), (20, 20)])
    assert np.all(np.isfinite(weights))


def test_gaussian_illumination_is_cut_off_by_the_aperture():
    a = illumination(RHO, 0.7)
    assert a[RHO > 1].max() == 0 and a.max() <= 1
    assert uniformity([1, 1, 1]) == 1 and uniformity([1, 3]) == pytest.approx(0.5)


def test_a_spot_weighted_to_nothing_is_left_out():
    both = spot_phase(X, Y, [(4, 0), (-4, 0)], weights=[1.0, 0.0])
    image = far_field(both, A)
    assert image[spot_pixel((4, 0), N)] == pytest.approx(1.0)
    assert image[spot_pixel((-4, 0), N)] < 1e-3
```

- [ ] **Step 2: Run them to see them fail**

Run: `uv run pytest tests/test_holography.py -q`
Expected: `ModuleNotFoundError: No module named 'manim_atoms.core.holography'`.

- [ ] **Step 3: Write the module**

`src/manim_atoms/core/holography.py`:

```python
"""Holography numbers: a phase mask on an SLM and the focal plane it makes.

No manim. Everything is on a square grid of pixels over the SLM's aperture,
the unit disc: pupil_grid gives the coordinates, zernike the aberration
modes, grating_phase and lens_phase the two masks every hologram is built
from, spot_phase the mask for several spots at once, far_field the
focal-plane intensity of any mask, gs_step and wgs_step one iteration of
the Gerchberg-Saxton algorithm and of its weighted version, and uniformity
and strehl the two numbers a hologram is judged by.

Spots are given in units of the diffraction limit: a spot at (kx, ky) is
made by a grating with kx periods across the aperture in x and ky in y.
"""

from math import factorial

import numpy as np

# The modes of the first five radial orders, by (n, m).
ZERNIKE_NAMES = {
    (0, 0): "piston",
    (1, -1): "tilt", (1, 1): "tip",
    (2, -2): "oblique astigmatism", (2, 0): "defocus", (2, 2): "astigmatism",
    (3, -3): "trefoil", (3, -1): "vertical coma", (3, 1): "coma", (3, 3): "oblique trefoil",
    (4, -4): "oblique quadrafoil", (4, -2): "oblique secondary astigmatism",
    (4, 0): "spherical", (4, 2): "secondary astigmatism", (4, 4): "quadrafoil",
}


def pupil_grid(n):
    """(x, y, rho, theta) at the pixel centres of an n x n grid over the
    square [-1, 1]^2, row 0 at the top (y = +1) as an image has it."""
    c = (np.arange(n) + 0.5) / n * 2 - 1
    x, y = np.meshgrid(c, -c)
    return x, y, np.hypot(x, y), np.arctan2(y, x)


def illumination(rho, waist=None):
    """The light's amplitude on the SLM: uniform over the unit disc and zero
    outside it, or a Gaussian of 1/e^2 intensity radius ``waist`` cut off by it."""
    inside = (np.asarray(rho) <= 1).astype(float)
    return inside if waist is None else inside * np.exp(-(rho / waist) ** 2)


def osa_to_nm(j):
    """The radial order n and azimuthal order m of the mode with OSA/ANSI
    index j, which counts along the rows of the Zernike pyramid: j = 0 is
    piston, 1 and 2 the tilts, 3 to 5 the row with defocus in the middle."""
    n = int(np.ceil((-3 + np.sqrt(9 + 8 * j)) / 2))
    return n, 2 * j - n * (n + 2)


def zernike(n, m, rho, theta):
    """The Zernike polynomial Z_n^m, normalised to unit mean square over the
    unit disc: cosine modes for m > 0, sine modes for m < 0."""
    if (n - abs(m)) % 2 or abs(m) > n:
        raise ValueError(f"no Zernike mode with n = {n}, m = {m}")
    rho = np.asarray(rho, dtype=float)
    k = abs(m)
    radial = sum(
        (-1) ** s * factorial(n - s)
        / (factorial(s) * factorial((n + k) // 2 - s) * factorial((n - k) // 2 - s))
        * rho ** (n - 2 * s)
        for s in range((n - k) // 2 + 1)
    )
    if m == 0:
        return np.sqrt(n + 1) * radial
    angular = np.cos(k * theta) if m > 0 else np.sin(k * theta)
    return np.sqrt(2 * (n + 1)) * radial * angular


def grating_phase(x, y, kx, ky):
    """A blazed grating with kx periods across the aperture in x and ky in y.
    It steers the spot to (kx, ky) diffraction limits off the axis."""
    return np.pi * (kx * x + ky * y)


def lens_phase(rho, waves):
    """A lens: ``waves`` of extra path at the edge of the aperture. It moves
    the focus along the axis, so in the focal plane the spot blurs."""
    return 2 * np.pi * waves * np.asarray(rho) ** 2


def spot_phase(x, y, spots, phases=None, weights=None):
    """The mask for several spots at once: the phase of the sum of the fields
    that would each make one of them, each with its own phase offset and,
    if given, its own weight (0 for a spot switched off)."""
    spots = np.atleast_2d(np.asarray(spots, dtype=float))
    phases = np.zeros(len(spots)) if phases is None else np.asarray(phases, dtype=float)
    weights = np.ones(len(spots)) if weights is None else np.asarray(weights, dtype=float)
    field = sum(w * np.exp(1j * (grating_phase(x, y, kx, ky) + p))
                for (kx, ky), p, w in zip(spots, phases, weights))
    return np.angle(field)


def far_field(phase, amplitude, pad=4):
    """The focal-plane intensity of a mask, on a grid ``pad`` times finer than
    the diffraction limit, scaled so that a flat mask peaks at 1.

    The array is pad * n pixels square with the optical axis at its centre
    pixel; spot_pixel says where a spot lands in it."""
    n = phase.shape[0]
    size = pad * n
    field = np.zeros((size, size), dtype=complex)
    lo = (size - n) // 2
    field[lo:lo + n, lo:lo + n] = amplitude * np.exp(1j * phase)
    out = np.fft.fftshift(np.fft.fft2(np.fft.ifftshift(field)))
    return np.abs(out) ** 2 / amplitude.sum() ** 2


def spot_pixel(spot, n, pad=4):
    """(row, column) of the spot at (kx, ky) in far_field's array."""
    kx, ky = spot
    centre = pad * n // 2
    return int(round(centre - ky * pad)), int(round(centre + kx * pad))


def spot_fields(phase, amplitude, x, y, spots):
    """The complex field a mask puts on each spot, as a share of what a
    grating aimed at that spot alone would put there."""
    spots = np.atleast_2d(np.asarray(spots, dtype=float))
    lit = amplitude * np.exp(1j * phase)
    return np.array([(lit * np.exp(-1j * grating_phase(x, y, kx, ky))).sum()
                     for kx, ky in spots]) / amplitude.sum()


def wgs_step(phase, weights, amplitude, x, y, spots, weighted=True):
    """One iteration of weighted Gerchberg-Saxton.

    Looks at the field the mask puts on each spot, raises the weight of the
    spots that came out dim, and builds the next mask from the weighted sum
    of the spots' fields, each keeping the phase it had. Returns (the next
    mask, the next weights, the intensity the mask it was given put on each
    spot). A spot the mask leaves dark keeps its weight."""
    spots = np.atleast_2d(np.asarray(spots, dtype=float))
    weights = np.asarray(weights, dtype=float)
    v = spot_fields(phase, amplitude, x, y, spots)
    mag = np.abs(v)
    if weighted:
        lit = mag > 1e-12
        weights = np.where(lit, weights * mag[lit].mean() / np.where(lit, mag, 1.0), weights) \
            if lit.any() else weights
    field = sum(w * np.exp(1j * (grating_phase(x, y, kx, ky) + np.angle(f)))
                for w, (kx, ky), f in zip(weights, spots, v))
    return np.angle(field), weights, mag ** 2


def gs_step(phase, amplitude, x, y, spots):
    """One iteration of plain Gerchberg-Saxton: every spot weighted alike.
    Returns (the next mask, the intensity the mask it was given put on each spot)."""
    spots = np.atleast_2d(np.asarray(spots, dtype=float))
    new, _, intensity = wgs_step(phase, np.ones(len(spots)), amplitude, x, y, spots,
                                 weighted=False)
    return new, intensity


def uniformity(intensities):
    """1 - (max - min) / (max + min): 1 when every spot is as bright as the rest."""
    i = np.asarray(intensities, dtype=float)
    return 1 - (i.max() - i.min()) / (i.max() + i.min())


def strehl(phase_error, amplitude):
    """The focal spot's peak with a wavefront error, as a share of its peak
    without one: |<exp(i phi)>|^2 over the illuminated aperture."""
    return np.abs((amplitude * np.exp(1j * phase_error)).sum()) ** 2 / amplitude.sum() ** 2
```

- [ ] **Step 4: Run the tests**

Run: `uv run pytest tests/test_holography.py -q`
Expected: all pass. For reference, from a random-phase start on a 5 × 5 array the uniformity goes 0.47, 0.57, 0.70, 0.74 over the first three iterations and reaches 0.99 by forty.

- [ ] **Step 5: Index it**

In `docs/index.md`, add a new section after "Optics: beams and cavities":

```markdown
## Holograms and phase masks

- **The pupil's grid, and the light on it.** `core.holography`: `pupil_grid`, `illumination`.
- **A mask's building blocks**: a grating, a lens, and several spots at once. `core.holography`: `grating_phase`, `lens_phase`, `spot_phase`.
- **The focal plane a mask makes**, where a spot lands in it, and the field on each spot. `core.holography`: `far_field`, `spot_pixel`, `spot_fields`.
- **Finding an array's mask** by Gerchberg–Saxton, plain or weighted, a step at a time, and how evenly it lights the spots. `core.holography`: `gs_step`, `wgs_step`, `uniformity`.
- **Zernike modes**, by their place in the pyramid, and the Strehl ratio a wavefront error leaves. `core.holography`: `zernike`, `osa_to_nm`, `strehl`.
```

Run: `python scripts/index.py --write && python scripts/index.py`
Expected: up to date.

- [ ] **Step 6: Commit and push**

```bash
git add src/manim_atoms/core/holography.py tests/test_holography.py docs/index.md docs/reference.md
git commit -m "core: holography numbers (Zernike modes, masks, focal plane, weighted GS)"
git push
```

---

### Task 3: The tilted view

**Files:**
- Create: `src/manim_atoms/core/projection.py`
- Test: `tests/test_projection.py`
- Modify: `docs/index.md`, `docs/reference.md` (generated)

**Interfaces:**
- Consumes: nothing.
- Produces: `TiltedView(center, scale=1.0, elevation=PI/2, azimuth=0.0)`; `elevation` and `azimuth` are numbers or `ValueTracker`s. Methods: `point(v) -> ndarray (3,)` for `v` of 2 or 3 components; `depth(v) -> float` (larger is nearer); `squash() -> float`; `rise() -> float`; `disc(at, radius, **style) -> Ellipse`; `outline(corners, **style) -> Polygon`. Attribute `scale`.

- [ ] **Step 1: Write the failing tests**

`tests/test_projection.py`:

```python
"""The tilted view's geometry: top-down it is the plane, edge on it is the
side view, and what is farther back sorts first. Pure numbers."""

import numpy as np
import pytest
from manim import DEGREES, PI, ValueTracker

from manim_atoms.core.projection import TiltedView


def test_looking_straight_down_is_the_plane_itself():
    view = TiltedView([1, 2, 0], scale=2)
    assert np.allclose(view.point([0.5, -1, 7]), [2, 0, 0])
    assert view.squash() == pytest.approx(1) and view.rise() == pytest.approx(0)


def test_edge_on_shows_height_and_hides_depth():
    view = TiltedView([0, 0, 0], elevation=0)
    assert np.allclose(view.point([1, 2, 3]), [1, 3, 0])


def test_a_point_needs_no_z():
    view = TiltedView([0, 0, 0], elevation=30 * DEGREES)
    assert np.allclose(view.point([1, 2]), view.point([1, 2, 0]))
    assert np.allclose(view.point(np.array([1.0, 2.0])), [1, 1, 0])


def test_farther_back_and_lower_down_sort_first():
    view = TiltedView([0, 0, 0], elevation=30 * DEGREES)
    assert view.depth([0, 1, 0]) < view.depth([0, 0, 0]) < view.depth([0, -1, 0])
    assert view.depth([0, 0, -1]) < view.depth([0, 0, 0]) < view.depth([0, 0, 1])


def test_azimuth_turns_the_plane_about_its_axis():
    view = TiltedView([0, 0, 0], elevation=30 * DEGREES, azimuth=PI / 2)
    assert np.allclose(view.point([1, 0, 0]), [0, 0.5, 0])
    assert np.allclose(view.point([0, 0, 1]), [0, np.cos(30 * DEGREES), 0])


def test_angles_are_read_from_trackers_each_time():
    elevation = ValueTracker(PI / 2)
    view = TiltedView([0, 0, 0], elevation=elevation)
    assert np.allclose(view.point([0, 1, 1]), [0, 1, 0])
    elevation.set_value(0)
    assert np.allclose(view.point([0, 1, 1]), [0, 1, 0])
    assert view.rise() == pytest.approx(1)


def test_a_disc_in_the_plane_is_an_ellipse():
    view = TiltedView([0, 0, 0], scale=2, elevation=30 * DEGREES)
    disc = view.disc([1, 0], 0.5)
    assert disc.width == pytest.approx(2) and disc.height == pytest.approx(1)
    assert np.allclose(disc.get_center(), [2, 0, 0])
```

- [ ] **Step 2: Run them to see them fail**

Run: `uv run pytest tests/test_projection.py -q`
Expected: `ModuleNotFoundError: No module named 'manim_atoms.core.projection'`.

- [ ] **Step 3: Write the module**

`src/manim_atoms/core/projection.py`:

```python
"""A plane seen from an angle, drawn on a flat scene.

TiltedView is an orthographic view of a world whose x-y plane is the plane
of interest (an array of traps, a sample, a chip) and whose z is the axis
out of it. Looking straight down (an elevation of 90 degrees) it is the
plane itself; lowered, the plane is squashed and things along z stand up.
The angles can be ValueTrackers, so the view can tilt and turn in a scene.
"""

import numpy as np
from manim import *

from manim_atoms.style import *


def _read(value):
    """A number, or what a ValueTracker holds."""
    return value.get_value() if hasattr(value, "get_value") else value


class TiltedView:
    """An orthographic view of the x-y plane from ``elevation`` above it,
    turned by ``azimuth`` about z, with the world's origin at ``center`` on
    screen and one world unit drawn ``scale`` long.

    ``elevation`` and ``azimuth`` are numbers or ValueTrackers, read afresh
    on every call. An elevation of PI / 2 looks straight down.
    """

    def __init__(self, center, scale=1.0, elevation=PI / 2, azimuth=0.0):
        self.center = np.array(center, dtype=float)
        self.scale = scale
        self.elevation, self.azimuth = elevation, azimuth

    def _turned(self, v):
        """(x, y, z) with the azimuth applied: y now runs away from the viewer."""
        x, y, z = (*v, 0.0)[:3]
        az = _read(self.azimuth)
        return x * np.cos(az) - y * np.sin(az), x * np.sin(az) + y * np.cos(az), z

    def point(self, v):
        """Where the world point ``v`` (x, y and optionally z) lands on screen."""
        x, y, z = self._turned(v)
        return self.center + self.scale * np.array(
            [x, y * self.squash() + z * self.rise(), 0.0]
        )

    def depth(self, v):
        """How near the viewer ``v`` is: paint in order of increasing depth."""
        _, y, z = self._turned(v)
        el = _read(self.elevation)
        return -y * np.cos(el) + z * np.sin(el)

    def squash(self):
        """How much a length in the plane, running away from the viewer, is
        foreshortened: 1 looking straight down, 0 edge on."""
        return np.sin(_read(self.elevation))

    def rise(self):
        """How long a unit step along z is drawn, before ``scale``: 0 looking
        straight down, 1 edge on."""
        return np.cos(_read(self.elevation))

    def disc(self, at, radius, **style):
        """A circle of ``radius`` lying in the plane about ``at``: an ellipse."""
        size = 2 * radius * self.scale
        return Ellipse(width=size, height=size * self.squash(), **style).move_to(self.point(at))

    def outline(self, corners, **style):
        """The polygon through world points ``corners``."""
        return Polygon(*[self.point(c) for c in corners], **style)
```

- [ ] **Step 4: Run the tests**

Run: `uv run pytest tests/test_projection.py -q`
Expected: 7 passed.

- [ ] **Step 5: Index it**

In `docs/index.md`, add to the "Tweezer arrays" section:

```markdown
- **A plane seen from an angle** on a flat scene, tilting and turning on trackers: where a point lands, what is in front, a circle in the plane. `core.projection`: `TiltedView`, with `TiltedView.point`, `TiltedView.depth`, `TiltedView.squash`, `TiltedView.rise`, `TiltedView.disc` and `TiltedView.outline`.
```

Run: `python scripts/index.py --write && python scripts/index.py`

- [ ] **Step 6: Commit and push**

```bash
git add src/manim_atoms/core/projection.py tests/test_projection.py docs/index.md docs/reference.md
git commit -m "core: TiltedView, a plane seen from an angle on a flat scene"
git push
```

---

### Task 4: The array as a drawing

**Files:**
- Create: `src/manim_atoms/tweezers/style.py`
- Create: `src/manim_atoms/tweezers/tools/tweezer_array.py`
- Create: `.claude/skills/manim-atoms/scripts/stops.py`
- Test: `tests/test_tweezer_array.py`
- Modify: `docs/index.md`, `docs/reference.md` (generated)

**Interfaces:**
- Consumes: `TiltedView` (Task 3); `Plan`, `positions` (Task 1); `gaussian_spot` from `core.optics`; `make_atom` from `core.primitives`.
- Produces:
  - Style: `TWEEZER_COLOR`, `TWEEZER_OPACITY`, `TWEEZER_LAYERS`, `TWEEZER_SPEED`, `TARGET_RING_STYLE`, `FOCAL_PLANE_STYLE`, `FONT_STEP`, `STEP_COLOR`, `FOCAL_SPOT_COLOR`, `BAR_COLOR`, `BAR_BASELINE_STYLE`, `FONT_READOUT`, `FONT_MODE`, `TRANSFORM_ARROW_STYLE`.
  - Geometry: `TW_ROWS`, `TW_COLS`, `TW_TARGET`, `TW_PITCH`, `TW_FILL`, `TW_SEED`, `TW_SPOT_RADIUS`, `TW_ATOM_RADIUS`, `TW_RING_RADIUS`.
  - `spot_trap(view, at, power) -> VGroup`.
  - `TweezerArray(sites, view, draw_trap=spot_trap, atom_radius=TW_ATOM_RADIUS)`: trackers `on`, `filled`, `ringed`, `off`, `moved`; tuple `trackers`; list `atoms`; methods `load(loaded)`, `rearrange(plan)`, `reset()`, `kept()`, `trap_positions()`, `trap_powers()`, `atom_opacities()`, `redraw()`. `load`, `rearrange`, `reset` and `redraw` return the array.
  - `heading(text) -> Tex`; `step_caption(text, under) -> Tex`; `next_step(old, text, under) -> (Tex, Succession)`.

- [ ] **Step 1: Write the failing tests**

`tests/test_tweezer_array.py`:

```python
"""The array drawing's bookkeeping: which traps are lit, where they are and
which hold an atom, at each setting of its trackers. Builds mobjects but
renders nothing."""

import numpy as np
import pytest
from manim import DEGREES

from manim_atoms.core.projection import TiltedView
from manim_atoms.tweezers.physics.rearrangement import plan_rearrangement, square_sites
from manim_atoms.tweezers.tools.tweezer_array import TweezerArray

SITES = square_sites(3, 3, 1.0)
LOADED = np.array([1, 0, 1, 0, 1, 1, 0, 0, 1], dtype=bool)  # five atoms
TARGETS = square_sites(2, 2, 1.0)


def make(view=None):
    return TweezerArray(SITES, view or TiltedView([0, 0, 0]))


def test_nothing_is_drawn_until_the_traps_come_on():
    array = make()
    assert len(array.submobjects) == 0
    array.on.set_value(1)
    assert len(array.redraw().submobjects) == 9 and array.atoms == []


def test_atoms_appear_only_in_loaded_traps():
    array = make().load(LOADED)
    array.on.set_value(1)
    array.filled.set_value(1)
    array.redraw()
    assert len(array.atoms) == 5
    assert np.allclose(sorted(a.get_center()[:2].tolist() for a in array.atoms),
                       sorted(SITES[LOADED].tolist()))


def test_the_wrong_number_of_loading_flags_is_an_error():
    with pytest.raises(ValueError, match="traps"):
        make().load([True, False])


def test_unkept_traps_go_out_with_their_atoms_and_kept_ones_move():
    array = make().load(LOADED)
    plan = plan_rearrangement(SITES, LOADED, TARGETS)
    array.rearrange(plan)
    array.on.set_value(1)
    array.filled.set_value(1)
    assert np.allclose(array.trap_powers(), 1)
    array.off.set_value(1)
    assert array.trap_powers().sum() == 4 and array.atom_opacities().sum() == 4
    array.moved.set_value(1)
    assert np.allclose(array.trap_positions()[plan.kept], plan.end)
    array.redraw()
    assert len(array.atoms) == 4
    assert np.allclose(sorted(a.get_center()[:2].tolist() for a in array.atoms),
                       sorted(TARGETS.tolist()))


def test_target_rings_show_only_with_a_plan():
    array = make()
    array.ringed.set_value(1)
    assert len(array.redraw().submobjects) == 0
    array.rearrange(plan_rearrangement(SITES, LOADED, TARGETS))
    assert len(array.submobjects) == 4


def test_reset_empties_the_array_and_puts_the_traps_back():
    array = make().load(LOADED)
    array.rearrange(plan_rearrangement(SITES, LOADED, TARGETS))
    for tracker in array.trackers:
        tracker.set_value(1)
    array.reset()
    assert array.on.get_value() == 1 and not array.loaded.any()
    assert np.allclose(array.trap_positions(), SITES) and np.allclose(array.trap_powers(), 1)


def test_far_traps_are_painted_first_in_a_tilted_view():
    array = make(TiltedView([0, 0, 0], elevation=30 * DEGREES))
    array.on.set_value(1)
    array.redraw()
    heights = [trap.get_center()[1] for trap in array.submobjects]
    assert heights == sorted(heights, reverse=True)
```

- [ ] **Step 2: Run them to see them fail**

Run: `uv run pytest tests/test_tweezer_array.py -q`
Expected: `ModuleNotFoundError: No module named 'manim_atoms.tweezers.tools.tweezer_array'`.

- [ ] **Step 3: Write the style module**

`src/manim_atoms/tweezers/style.py`:

```python
"""The tweezer scenes' style: the core house style plus the tweezer array,
its beams and the holograms that make it.

    from manim import *
    from manim_atoms.tweezers.style import *
"""

from manim import ManimColor

from manim_atoms.style import *

# --- the tweezers ---------------------------------------------------------
# Tweezer light is far off every resonance: it holds an atom and drives
# nothing, so it takes no transition's colour. A pale warm white. How
# brightly a trap is drawn is its power; a trap switched off is not drawn.
TWEEZER_COLOR = ManimColor("#f3e3c8")
TWEEZER_OPACITY = 0.55  # on the axis, at the focus, at full power
TWEEZER_LAYERS = 4  # nested shapes across the beam, as a Gaussian profile
# Traps move at one speed, so a longer move takes visibly longer.
TWEEZER_SPEED = 0.9
# A site an atom is wanted at: a reference, so a thin ring in the
# construction grey.
TARGET_RING_STYLE = dict(stroke_width=2, stroke_opacity=0.55, color=GUIDE_COLOR)
# The focal plane in the tilted view: the outline of the plane the foci lie in.
FOCAL_PLANE_STYLE = dict(stroke_width=2, stroke_opacity=0.35, color=GUIDE_COLOR)
# The step being shown, under the heading: grey, a notch below the heading.
FONT_STEP = FONT_LEGEND
STEP_COLOR = lighten(GUIDE_COLOR)

# --- holograms ------------------------------------------------------------
# The focal plane as a camera would see it: the tweezer light's own colour.
FOCAL_SPOT_COLOR = TWEEZER_COLOR
# A bar per trap (its brightness) or per Zernike mode (its amplitude): a
# reading, in the plot foreground, on a baseline in the construction grey.
BAR_COLOR = ManimColor(PLOT_FOREGROUND)
BAR_BASELINE_STYLE = dict(stroke_width=2, color=GUIDE_COLOR)
FONT_READOUT = FONT_ANNOTATION  # the number a scene is about (uniformity, Strehl)
FONT_MODE = 20  # a Zernike mode's name under its disc
# The arrows joining the SLM plane to the focal plane.
TRANSFORM_ARROW_STYLE = dict(buff=0.15, stroke_width=3, color=lighten(GUIDE_COLOR),
                             max_tip_length_to_length_ratio=0.12)
```

`TWEEZER_COLOR` has the value trapping's `TRAP_BEAM_COLOR` has, for the same kind of reason (far-detuned light), but it is tweezers' own constant: do not import trapping's.

- [ ] **Step 4: Write the array**

`src/manim_atoms/tweezers/tools/tweezer_array.py`:

```python
"""The tweezer array as a drawing: traps, the atoms in them, and the moves.

TweezerArray draws an array through a core.projection.TiltedView, so the
same array is the top-down picture or the tilted one. What it shows is set
by four trackers (the traps' power, the atoms, the unwanted traps going
out, the move), so a scene animates the array by animating those. How one
trap is drawn is a function it is given: spot_trap here, the beam seen end
on; tools.beams has the beam seen from the side. heading and step_caption
are the scenes' text.
"""

import numpy as np
from manim import *

from manim_atoms.tweezers.style import *
from manim_atoms.core.optics import gaussian_spot
from manim_atoms.core.primitives import make_atom
from manim_atoms.tweezers.physics.rearrangement import positions

# --- the array's geometry ----------------------------------------------------
# A 9 x 9 array loads about forty atoms, enough to fill the 5 x 5 block at
# its centre with a dozen to spare. An odd block in an odd array sits on the
# array's own sites, so the atoms that are already in place stay put.
TW_ROWS, TW_COLS = 9, 9
TW_TARGET = (5, 5)  # rows and columns of the block wanted
TW_PITCH = 0.5  # between neighbouring traps
TW_FILL = 0.5  # the chance a trap catches an atom
TW_SEED = 0  # of the loading the scenes show
TW_SPOT_RADIUS = 0.15  # the waist as drawn: neighbours' spots stay clear of each other
TW_ATOM_RADIUS = 0.08  # well inside its trap's spot
TW_RING_RADIUS = 0.2  # a target ring, just outside the spot


def spot_trap(view, at, power):
    """One trap seen end on: a Gaussian spot at world point ``at``, as bright
    as its ``power`` (0 to 1)."""
    return gaussian_spot(view.point(at), TW_SPOT_RADIUS * view.scale, TWEEZER_COLOR,
                         opacity=TWEEZER_OPACITY * power, layers=TWEEZER_LAYERS)


class TweezerArray(VGroup):
    """An array of traps at ``sites`` ((N, 2), in the view's plane), drawn
    through ``view`` and redrawn every frame from its trackers:

    - ``on``: every trap's power, 0 to 1;
    - ``filled``: the atoms in the loaded traps, 0 (none yet) to 1;
    - ``ringed``: the rings on the plan's target sites, 0 to 1;
    - ``off``: 0 to 1 as the traps the plan does not keep go out, taking any
      atoms in them;
    - ``moved``: how far through the plan's move the kept traps are, 0 to 1.

    load() says which traps hold an atom and rearrange() gives it a plan;
    until it has one, every trap counts as kept. Add ``trackers`` to the
    scene before the array. ``atoms`` is the atoms as last drawn, for
    core.primitives.fluoresce. ``draw_trap(view, at, power)`` draws one trap.
    """

    def __init__(self, sites, view, draw_trap=spot_trap, atom_radius=TW_ATOM_RADIUS):
        super().__init__()
        self.sites = np.asarray(sites, dtype=float)
        self.view, self.draw_trap, self.atom_radius = view, draw_trap, atom_radius
        self.loaded = np.zeros(len(self.sites), dtype=bool)
        self.plan = None
        self.on, self.filled, self.ringed = ValueTracker(0), ValueTracker(0), ValueTracker(0)
        self.off, self.moved = ValueTracker(0), ValueTracker(0)
        self.trackers = (self.on, self.filled, self.ringed, self.off, self.moved)
        self.atoms = []
        self.redraw()
        self.add_updater(lambda m: m.redraw())

    def load(self, loaded):
        """Say which traps hold an atom (a boolean per site)."""
        loaded = np.asarray(loaded, dtype=bool)
        if loaded.shape != (len(self.sites),):
            raise ValueError(f"{loaded.shape} loading flags for {len(self.sites)} traps")
        self.loaded = loaded
        return self.redraw()

    def rearrange(self, plan):
        """Take a physics.rearrangement.Plan: its kept traps move with
        ``moved``, and the rest go out with ``off``."""
        self.plan = plan
        return self.redraw()

    def reset(self):
        """Back to an empty array with no plan, its traps where they started."""
        self.plan = None
        self.loaded = np.zeros(len(self.sites), dtype=bool)
        for tracker in (self.filled, self.ringed, self.off, self.moved):
            tracker.set_value(0)
        return self.redraw()

    def kept(self):
        """Which traps stay on: all of them, until there is a plan."""
        kept = np.ones(len(self.sites), dtype=bool)
        if self.plan is not None:
            kept[:] = False
            kept[self.plan.kept] = True
        return kept

    def trap_positions(self):
        """Where every trap is now, (N, 2)."""
        xy = self.sites.copy()
        if self.plan is not None:
            xy[self.plan.kept] = positions(self.plan, self.moved.get_value())
        return xy

    def trap_powers(self):
        """Every trap's power now, 0 to 1."""
        staying = np.where(self.kept(), 1.0, 1 - self.off.get_value())
        return self.on.get_value() * staying

    def atom_opacities(self):
        """How solidly each trap's atom is drawn: 0 for a trap with none."""
        staying = np.where(self.kept(), 1.0, 1 - self.off.get_value())
        return self.filled.get_value() * self.loaded * staying

    def redraw(self):
        """Rebuild the drawing from the trackers: target rings, then each trap
        and its atom, far ones first."""
        xy, powers, shown = self.trap_positions(), self.trap_powers(), self.atom_opacities()
        parts, self.atoms = [], []
        ringed = self.ringed.get_value()
        if self.plan is not None and ringed > 1e-3:
            style = {**TARGET_RING_STYLE,
                     "stroke_opacity": TARGET_RING_STYLE["stroke_opacity"] * ringed}
            parts += [self.view.disc(end, TW_RING_RADIUS, **style) for end in self.plan.end]
        for i in np.argsort([self.view.depth(p) for p in xy], kind="stable"):
            if powers[i] > 1e-3:
                parts.append(self.draw_trap(self.view, xy[i], powers[i]))
            if shown[i] > 1e-3:
                atom = make_atom(radius=self.atom_radius * self.view.scale, opacity=shown[i])
                atom[0].set_stroke(opacity=shown[i])
                atom.move_to(self.view.point(xy[i]))
                parts.append(atom)
                self.atoms.append(atom)
        self.submobjects = parts
        return self


def heading(text):
    """A scene's heading, for its upper left corner."""
    return Tex(text, font_size=FONT_TITLE)


def step_caption(text, under):
    """The step being shown, in grey under the heading ``under``."""
    return Tex(text, font_size=FONT_STEP, color=STEP_COLOR).next_to(
        under, DOWN, buff=0.2, aligned_edge=LEFT)


def next_step(old, text, under):
    """(the new caption, the animation that swaps ``old`` for it): out, then
    in, so the two are never crossed."""
    new = step_caption(text, under)
    return new, Succession(FadeOut(old, run_time=0.3), FadeIn(new, run_time=0.3))
```

The array rebuilds its submobjects every frame instead of keeping one mobject per trap, because the painting order changes as a tilted view turns. Two consequences a scene must respect: never `FadeIn`, `FadeOut` or `Transform` the array (drive its trackers), and take `array.atoms` at the moment it is used, since each redraw makes new atoms.

- [ ] **Step 5: Run the tests**

Run: `uv run pytest tests/test_tweezer_array.py -q`
Expected: 7 passed.

- [ ] **Step 6: Add the stop-time script**

`.claude/skills/manim-atoms/scripts/stops.py`:

```python
#!/usr/bin/env python3
"""Print when a scene stops, so frames.py can be pointed at each stop.

    uv run python stops.py manim_atoms.tweezers.scenes.rearrangement TweezerRearrangement

Runs the scene without rendering, with beat(), stage_break() and hold()
recording the scene's clock, and prints the times just before each stop:
paste them after frames.py's -t. A stop comes after its settling wait, so
the frame just before it is the picture the presenter stops on.
"""

import importlib
import sys

from manim import tempconfig

module, name = sys.argv[1:3]
scene = getattr(importlib.import_module(module), name)
times = []


class Probe(scene):
    def _mark(self, *args, **kwargs):
        times.append(self.renderer.time)

    beat = stage_break = hold = _mark


with tempconfig({"dry_run": True, "quality": "low_quality", "disable_caching": True,
                 "verbosity": "ERROR", "progress_bar": "none"}):
    Probe().render()
print(" ".join(f"{max(t - 0.1, 0):.2f}" for t in times))
```

In `.claude/skills/manim-atoms/SKILL.md`, under "You can't watch the video, so look at frames", after the `frames.py` code block, add:

```markdown
`scripts/stops.py <dotted module> <Scene>` prints the times just before
each of a scene's stops, ready to paste after `-t`.
```

- [ ] **Step 7: Index it**

In `docs/index.md`, add to "Tweezer arrays":

```markdown
- **A tweezer array**: traps as bright as their power, the atoms in them, and the unwanted traps going out and the rest moving, all on trackers. Drawn through a `core.projection.TiltedView`. `tweezers.tools.tweezer_array`: `TweezerArray`, with `spot_trap` as the trap seen end on.
- **A tweezer scene's heading and the step under it.** `tweezers.tools.tweezer_array`: `heading`, `step_caption`, `next_step`.
```

Run: `python scripts/index.py --write && python scripts/index.py`

- [ ] **Step 8: Commit and push**

```bash
git add src/manim_atoms/tweezers/style.py src/manim_atoms/tweezers/tools/tweezer_array.py \
        tests/test_tweezer_array.py .claude/skills/manim-atoms/scripts/stops.py \
        .claude/skills/manim-atoms/SKILL.md docs/index.md docs/reference.md
git commit -m "tweezers: TweezerArray, an array drawn from its trackers through a view"
git push
```

---

### Task 5 (2D track): `TweezerRearrangement`

**Files:**
- Create: `src/manim_atoms/tweezers/scenes/rearrangement.py`
- Modify: `docs/index.md`, `docs/reference.md` (generated)

**Interfaces:**
- Consumes: `TweezerArray`, `heading`, `step_caption`, `next_step`, the `TW_*` constants (Task 4); `TiltedView` (Task 3); `square_sites`, `load_sites`, `plan_rearrangement`, `longest_move` (Task 1); `fluoresce` from `core.primitives`.
- Produces: `TweezerRearrangement` (Scene; methods `beat`, `build`, `say`, `cycle(seed)`), `TweezerRearrangementLoop`.

- [ ] **Step 1: Write the scene**

`src/manim_atoms/tweezers/scenes/rearrangement.py`:

```python
"""Rearranging a tweezer array by updating its hologram, seen from above.

A tweezer array loads at random: each trap catches one atom or none, about
half and half. An image says which, the empty traps and the spare atoms'
traps are switched off, and the hologram on the SLM is then updated step by
step so that every remaining trap slides, with its atom, to a site of the
block wanted. All the traps move at once.

The traps are drawn as the spots they make in the focal plane, as bright as
their power, and the atoms as the house discs. Nothing is to scale: a real
trap's waist is a tenth of the spacing.

- TweezerRearrangement: one loading, rearranged. A beat() once the traps
  are on, then after the loading, the image, the switching off, the move
  and the second image.
- TweezerRearrangementLoop: three loadings one after another, each released
  at the end. It begins and ends on the empty array, so the clip loops.
"""

import numpy as np
from manim import *

from manim_atoms.tweezers.style import *
from manim_atoms.core.primitives import fluoresce
from manim_atoms.core.projection import TiltedView
from manim_atoms.tweezers.physics.rearrangement import (
    load_sites,
    longest_move,
    plan_rearrangement,
    square_sites,
)
from manim_atoms.tweezers.tools.tweezer_array import (
    TW_COLS,
    TW_FILL,
    TW_PITCH,
    TW_ROWS,
    TW_SEED,
    TW_TARGET,
    TweezerArray,
    heading,
    next_step,
    step_caption,
)

# --- rearrangement geometry --------------------------------------------------
# The array fills the frame under the heading. The heading and the step
# under it sit in the upper left corner, clear of the array's top row.
TR_CENTER = np.array([0.6, -0.55, 0.0])  # of the array
TR_SCALE = 1.3  # scene units per unit of the array's own
TR_HEADING = np.array([-6.6, 3.6, 0.0])  # the heading's upper left corner
TR_ON_TIME = 1.0  # the traps coming on
TR_LOAD_TIME = 1.2  # the atoms arriving
TR_OFF_TIME = 0.8  # the unwanted traps going out
TR_SETTLE = 0.6  # the pause before a stop
TR_LOOP_SEEDS = (0, 1, 2)  # the loadings the loop runs through


class TweezerRearrangement(Scene):
    """A tweezer array seen from above: it loads at random, is imaged, loses
    its empty and spare traps, and the rest slide into a defect-free block.
    One beat() per step."""

    def beat(self):
        """The pause after each step: nothing here, a click on the slide version."""

    def build(self):
        """Lay out the array, the heading and the first caption, unadded."""
        sites = square_sites(TW_ROWS, TW_COLS, TW_PITCH)
        self.targets = square_sites(*TW_TARGET, TW_PITCH)
        self.array = TweezerArray(sites, TiltedView(TR_CENTER, TR_SCALE))
        self.title = heading("Rearranging a tweezer array").move_to(TR_HEADING, aligned_edge=UL)
        self.note = step_caption("the traps", self.title)

    def say(self, text):
        """The animation that swaps the caption for ``text``."""
        self.note, swap = next_step(self.note, text, self.title)
        return swap

    def construct(self):
        self.build()
        array = self.array
        self.add(*array.trackers, array)
        self.play(FadeIn(self.title), FadeIn(self.note),
                  array.on.animate(run_time=TR_ON_TIME).set_value(1))
        self.wait(TR_SETTLE)
        self.beat()
        self.cycle(TW_SEED)

    def cycle(self, seed):
        """Load the array as ``seed`` has it, image it, and rearrange it."""
        array = self.array
        loaded = load_sites(len(array.sites), TW_FILL, np.random.default_rng(seed))
        plan = plan_rearrangement(array.sites, loaded, self.targets)

        array.load(loaded)
        self.play(self.say("each trap catches one atom, or none"),
                  array.filled.animate(run_time=TR_LOAD_TIME).set_value(1))
        self.wait(TR_SETTLE)
        self.beat()

        self.play(self.say("an image shows which"))
        fluoresce(self, array.atoms)
        self.wait(TR_SETTLE)
        self.beat()

        array.rearrange(plan)
        self.play(self.say("empty and spare traps off"),
                  array.off.animate(run_time=TR_OFF_TIME).set_value(1),
                  array.ringed.animate(run_time=TR_OFF_TIME).set_value(1))
        self.wait(TR_SETTLE)
        self.beat()

        self.play(self.say("the hologram is updated: every trap moves at once"))
        self.play(array.moved.animate.set_value(1),
                  run_time=longest_move(plan) * TR_SCALE / TWEEZER_SPEED)
        self.wait(TR_SETTLE)
        self.beat()

        self.play(self.say("a second image: no gaps"),
                  array.ringed.animate(run_time=0.4).set_value(0))
        fluoresce(self, array.atoms)
        self.wait(TR_SETTLE)
        self.beat()


class TweezerRearrangementLoop(TweezerRearrangement):
    """TweezerRearrangement run over several loadings, each released at the
    end: it begins and ends on the empty array, so the clip loops."""

    def construct(self):
        self.build()
        array = self.array
        array.on.set_value(1)
        array.redraw()
        self.add(*array.trackers, array, self.title, self.note)
        self.wait(TR_SETTLE)
        for seed in TR_LOOP_SEEDS:
            self.cycle(seed)
            self.release()

    def release(self):
        """Let the atoms go and bring the whole array back on, empty."""
        array = self.array
        self.play(self.say("the atoms are released"),
                  array.filled.animate(run_time=TR_OFF_TIME).set_value(0))
        self.play(array.on.animate.set_value(0), run_time=TR_OFF_TIME)
        array.reset()
        self.play(self.say("the traps"), array.on.animate(run_time=TR_ON_TIME).set_value(1))
        self.wait(TR_SETTLE)
```

- [ ] **Step 2: Dry-run both scenes**

```bash
uv run manim -ql --dry_run src/manim_atoms/tweezers/scenes/rearrangement.py TweezerRearrangement
uv run manim -ql --dry_run src/manim_atoms/tweezers/scenes/rearrangement.py TweezerRearrangementLoop
```
Expected: `Played 17 animations` and `Played 58 animations`, no traceback.

- [ ] **Step 3: Render and read a frame at every stop**

Run the frame check (top of this plan) for `rearrangement` / `TweezerRearrangement`. Expected stops near 1.5, 3.3, 5.8, 7.2, 9.9 and 12.4 s.

At each frame, check and fix by editing the `TR_*` block or, for the array's own proportions, the `TW_*` block:

| Stop | Must be true |
|---|---|
| 1 traps on | 81 separate spots; neighbours do not merge; the top row is clear of the heading and the caption |
| 2 loaded | about forty atoms, each well inside its spot and clearly darker or lighter than it |
| 3 imaged | the halos are gone; atoms unchanged |
| 4 off | only 25 traps lit; 25 rings in a 5 × 5 block; no atom outside a lit trap |
| 5 moved | every ring holds exactly one trap and atom; nothing left outside the block |
| 6 final | rings gone; a clean 5 × 5 block |

Also take a frame mid-move (`-t 8.6`) and check no two traps overlap.

Sample the colours: a spot's centre and an atom must be told apart.

```bash
.venv/bin/python .claude/skills/manim-atoms/scripts/frames.py \
    media/videos/rearrangement/480p15/TweezerRearrangement.mp4 -t 3.2 --sample 0.6,-0.55 0.92,-0.55
```
Expected: two RGB triples that are plainly different (the atom's blue against the spot's pale warm white). Pick the two points from the frame: one on an atom, one on the same trap's spot just outside the atom.

- [ ] **Step 4: Check the loop closes**

```bash
uv run manim -ql src/manim_atoms/tweezers/scenes/rearrangement.py TweezerRearrangementLoop
.venv/bin/python .claude/skills/manim-atoms/scripts/frames.py \
    media/videos/rearrangement/480p15/TweezerRearrangementLoop.mp4 -t 0.0 --final -o /tmp/frames/loop
```
Read both PNGs. Expected: the same picture, the empty array with "the traps" under the heading.

- [ ] **Step 5: Index it**

In `docs/index.md`, add to "Worked examples by pattern":

```markdown
- **A tweezer array loaded, imaged and rearranged**, from above; and the same as a clip that loops. `tweezers.scenes.rearrangement`: `TweezerRearrangement`, `TweezerRearrangementLoop`.
```

Run: `python scripts/index.py --write && python scripts/index.py`

- [ ] **Step 6: Commit and push**

```bash
git add src/manim_atoms/tweezers/scenes/rearrangement.py src/manim_atoms/tweezers/tools/tweezer_array.py \
        docs/index.md docs/reference.md
git commit -m "tweezers: TweezerRearrangement, an array rearranged seen from above"
git push
```

---

### Task 6 (3D track): the beam and `TweezerArray3D`

**Files:**
- Create: `src/manim_atoms/tweezers/tools/beams.py`
- Create: `src/manim_atoms/tweezers/scenes/array_3d.py`
- Test: `tests/test_tweezer_beams.py`
- Modify: `docs/index.md`, `docs/reference.md` (generated)

**Interfaces:**
- Consumes: `TweezerArray`, `TW_SPOT_RADIUS`, the heading helpers (Task 4); `TiltedView` (Task 3); the rearrangement functions (Task 1); `TWEEZER_*` and `FOCAL_PLANE_STYLE` (Task 4's style).
- Produces: `TW_RAYLEIGH`, `TW_REACH`, `TW_OUTLINE_POINTS`, `TW_STOPS`, `TW_ELEVATION`, `TW_AZIMUTH`; `beam_half_width(z, waist, rayleigh)`; `axial_intensity(z, rayleigh, reach)`; `hourglass_trap(view, at, power, waist, rayleigh, reach) -> VGroup`, usable as `TweezerArray`'s `draw_trap`; `focal_plane(view, half_width, half_height, shown) -> Mobject`; scenes `TweezerArray3D`, `TweezerArray3DLoop`.

- [ ] **Step 1: Write the failing tests**

`tests/test_tweezer_beams.py`:

```python
"""The beam a tilted tweezer is drawn as: it widens and fades away from its
focus, and seen from straight above it is only its spot. Builds mobjects
but renders nothing."""

import numpy as np
import pytest
from manim import DEGREES

from manim_atoms.core.projection import TiltedView
from manim_atoms.tweezers.tools.beams import (
    TW_RAYLEIGH, TW_REACH, axial_intensity, beam_half_width, hourglass_trap,
)
from manim_atoms.tweezers.tools.tweezer_array import TW_SPOT_RADIUS


def test_the_beam_widens_and_fades_away_from_its_focus():
    assert beam_half_width(0) == pytest.approx(TW_SPOT_RADIUS)
    assert beam_half_width(TW_RAYLEIGH) == pytest.approx(TW_SPOT_RADIUS * np.sqrt(2))
    assert axial_intensity(0) == 1 and axial_intensity(TW_RAYLEIGH) < 0.5
    assert axial_intensity(TW_REACH) == 0 and axial_intensity(2 * TW_REACH) == 0
    z = np.linspace(0, TW_REACH, 50)
    assert np.all(np.diff(axial_intensity(z)) < 0)


def test_looking_straight_down_the_hourglass_is_only_its_spot():
    flat = hourglass_trap(TiltedView([0, 0, 0]), [0, 0], 1.0)
    tilted = hourglass_trap(TiltedView([0, 0, 0], elevation=30 * DEGREES), [0, 0], 1.0)
    assert len(tilted) > len(flat)
    assert flat.width == pytest.approx(2 * TW_SPOT_RADIUS) == flat.height
    assert tilted.height == pytest.approx(2 * TW_REACH * np.cos(30 * DEGREES), rel=0.01)
```

- [ ] **Step 2: Run them to see them fail**

Run: `uv run pytest tests/test_tweezer_beams.py -q`
Expected: `ModuleNotFoundError: No module named 'manim_atoms.tweezers.tools.beams'`.

- [ ] **Step 3: Write the beam**

`src/manim_atoms/tweezers/tools/beams.py`:

```python
"""A tweezer seen from the side: a focused Gaussian beam through a tilted view.

hourglass_trap is the trap drawing a TweezerArray takes for the tilted
picture: the beam's silhouette either side of the focus, fading as the
light spreads, over the spot in the focal plane. beam_half_width and
axial_intensity are the Gaussian beam it draws; focal_plane is the outline
of the plane the foci lie in.
"""

import numpy as np
from manim import *

from manim_atoms.tweezers.style import *
from manim_atoms.tweezers.tools.tweezer_array import TW_SPOT_RADIUS

# --- the beam's geometry -----------------------------------------------------
# Not to scale: a real tweezer's waist is a tenth of the spacing and its
# Rayleigh range a few waists, which drawn true would be needles. Here the
# waist is the top-down spot's radius, and the beam widens slowly enough
# that neighbours stay separate columns as far as they are drawn.
TW_RAYLEIGH = 0.9  # distance from the focus at which the beam is sqrt(2) wider
TW_REACH = 1.4  # how far either side of the focus the beam is drawn
TW_OUTLINE_POINTS = 10  # along each half's edge
TW_STOPS = 6  # opacity stops along each half
TW_ELEVATION = 35 * DEGREES  # the tilted view: low enough for the beams to stand up
TW_AZIMUTH = 18 * DEGREES  # turned, so the rows do not hide one another


def beam_half_width(z, waist=TW_SPOT_RADIUS, rayleigh=TW_RAYLEIGH):
    """A Gaussian beam's 1/e^2 radius a distance z from its focus:
    w0 sqrt(1 + (z / z_R)^2)."""
    return waist * np.sqrt(1 + (np.asarray(z, dtype=float) / rayleigh) ** 2)


def axial_intensity(z, rayleigh=TW_RAYLEIGH, reach=TW_REACH):
    """How brightly the beam is drawn a distance z from its focus: the
    on-axis intensity 1 / (1 + (z / z_R)^2), brought to nothing at ``reach``
    so the beam fades out rather than ending."""
    z = np.asarray(z, dtype=float)
    return np.clip(1 - (z / reach) ** 2, 0, None) / (1 + (z / rayleigh) ** 2)


def hourglass_trap(view, at, power, waist=TW_SPOT_RADIUS, rayleigh=TW_RAYLEIGH,
                   reach=TW_REACH):
    """One trap seen through a tilted view: the half of the beam below the
    focal plane, the half above, and the spot in the plane, at world point
    ``at`` and as bright as ``power``.

    Looking straight down the halves have no height and are left out, and
    what remains is spot_trap's drawing: the view can tilt between the two
    without a jump.
    """
    c, s = view.point(at), view.scale
    rise = view.rise() * s
    peak = TWEEZER_OPACITY * power / TWEEZER_LAYERS
    parts = VGroup()
    if rise > 1e-3:
        zs = np.linspace(0, reach, TW_OUTLINE_POINTS)
        widths = beam_half_width(zs, waist, rayleigh) * s
        stops = [peak * axial_intensity(z, rayleigh, reach)
                 for z in np.linspace(0, reach, TW_STOPS)]
        for side in (-1, 1):
            for k in range(TWEEZER_LAYERS):
                share = 1 - k / TWEEZER_LAYERS
                edge = [np.array([w * share, side * z * rise, 0.0]) for w, z in zip(widths, zs)]
                corners = [c + p for p in edge] + [c + p * [-1, 1, 1] for p in edge[::-1]]
                half = VMobject(stroke_width=0).set_points_as_corners([*corners, corners[0]])
                half.set_fill([TWEEZER_COLOR] * TW_STOPS, opacity=stops)
                half.set_sheen_direction(side * UP)
                parts.add(half)
    for k in range(TWEEZER_LAYERS):
        parts.add(view.disc(at, waist * (1 - k / TWEEZER_LAYERS), stroke_width=0,
                            fill_color=TWEEZER_COLOR, fill_opacity=peak))
    return parts


def focal_plane(view, half_width, half_height, shown):
    """The outline of the focal plane, a rectangle about the view's origin,
    redrawn as the view moves and as visible as the tracker ``shown`` (0 to 1)."""
    corners = [[half_width, half_height], [-half_width, half_height],
               [-half_width, -half_height], [half_width, -half_height]]

    def draw():
        style = {**FOCAL_PLANE_STYLE,
                 "stroke_opacity": FOCAL_PLANE_STYLE["stroke_opacity"] * shown.get_value()}
        return view.outline(corners, **style)

    return always_redraw(draw)
```

The fade along the beam is one fill gradient per half: `set_fill` with a list of opacities and `set_sheen_direction` along the axis, which Cairo draws as a linear gradient with evenly spaced stops across the shape's bounding box. That is the technique `interferometry.tools.phase_shear.make_beam` already uses with two stops.

- [ ] **Step 4: Run the tests**

Run: `uv run pytest tests/test_tweezer_beams.py -q`
Expected: 2 passed.

- [ ] **Step 5: Write the scenes**

`src/manim_atoms/tweezers/scenes/array_3d.py`:

```python
"""A tweezer array seen from an angle: each trap a focused beam.

Starts on the loaded array seen from above, as TweezerRearrangement has it,
and tilts the view over. Each spot turns out to be the waist of a beam: it
narrows to its focus in the plane of the array, where its atom sits, and
spreads again beyond, drawn as bright as the light on its axis so that it
fades away from the atom. The array is then imaged and rearranged exactly
as in the top-down scene, with the beams moving.

The view is an orthographic projection (core.projection), not a camera:
there is no perspective. The beams are not to scale (tools.beams).

- TweezerArray3D: a beat() on the top-down array, then after the tilt, the
  switching off and the move.
- TweezerArray3DLoop: the rearranged block turning a quarter turn about the
  optical axis, which brings it back onto itself, so the clip loops.
"""

import numpy as np
from manim import *

from manim_atoms.tweezers.style import *
from manim_atoms.core.primitives import fluoresce
from manim_atoms.core.projection import TiltedView
from manim_atoms.tweezers.physics.rearrangement import (
    load_sites,
    longest_move,
    plan_rearrangement,
    square_sites,
)
from manim_atoms.tweezers.tools.beams import (
    TW_AZIMUTH,
    TW_ELEVATION,
    focal_plane,
    hourglass_trap,
)
from manim_atoms.tweezers.tools.tweezer_array import (
    TW_COLS,
    TW_FILL,
    TW_PITCH,
    TW_ROWS,
    TW_SEED,
    TW_TARGET,
    TweezerArray,
    heading,
    next_step,
    step_caption,
)

# --- tilted-array geometry ---------------------------------------------------
# Tilted, the array is wider than it is tall and the beams stand above and
# below it, so it sits a little below the middle of the frame, clear of the
# heading in the upper left corner.
T3_CENTER = np.array([0.4, -0.5, 0.0])  # of the array
T3_SCALE = 1.3  # scene units per unit of the array's own
T3_HEADING = np.array([-6.6, 3.6, 0.0])  # the heading's upper left corner
T3_PLANE_MARGIN = 0.5  # of the focal plane's outline beyond the outermost traps
T3_TILT_TIME = 3.0
T3_OFF_TIME = 0.8
T3_TURN_TIME = 10.0  # the loop's quarter turn
T3_SETTLE = 0.6  # the pause before a stop


class TweezerArray3D(Scene):
    """The loaded array tilts from the top-down view into one from an angle,
    each trap a beam through its atom, and is rearranged there. One beat()
    per step."""

    def beat(self):
        """The pause after each step: nothing here, a click on the slide version."""

    def build(self):
        """Lay out the loaded array in a view that starts top-down, unadded."""
        sites = square_sites(TW_ROWS, TW_COLS, TW_PITCH)
        targets = square_sites(*TW_TARGET, TW_PITCH)
        loaded = load_sites(len(sites), TW_FILL, np.random.default_rng(TW_SEED))
        self.plan = plan_rearrangement(sites, loaded, targets)
        self.elevation, self.azimuth = ValueTracker(PI / 2), ValueTracker(0)
        self.plane_shown = ValueTracker(0)
        view = TiltedView(T3_CENTER, T3_SCALE, self.elevation, self.azimuth)
        self.array = TweezerArray(sites, view, draw_trap=hourglass_trap).load(loaded)
        self.array.on.set_value(1)
        self.array.filled.set_value(1)
        self.array.redraw()
        half = (TW_COLS - 1) / 2 * TW_PITCH + T3_PLANE_MARGIN
        self.plane = focal_plane(view, half, half, self.plane_shown)
        self.title = heading("A tweezer array").move_to(T3_HEADING, aligned_edge=UL)
        self.note = step_caption("from above: each trap a spot", self.title)

    def add_all(self):
        """Put everything on, the trackers first so nothing lags them."""
        self.add(self.elevation, self.azimuth, self.plane_shown, *self.array.trackers,
                 self.plane, self.array, self.title, self.note)

    def say(self, text):
        """The animation that swaps the caption for ``text``."""
        self.note, swap = next_step(self.note, text, self.title)
        return swap

    def construct(self):
        self.build()
        self.add_all()
        array = self.array
        self.wait(T3_SETTLE)
        self.beat()

        self.play(self.say("from the side: each trap a focused beam"),
                  self.elevation.animate(run_time=T3_TILT_TIME).set_value(TW_ELEVATION),
                  self.azimuth.animate(run_time=T3_TILT_TIME).set_value(TW_AZIMUTH),
                  self.plane_shown.animate(run_time=T3_TILT_TIME).set_value(1))
        self.wait(T3_SETTLE)
        self.beat()

        self.play(self.say("image, then empty and spare traps off"))
        fluoresce(self, array.atoms)
        array.rearrange(self.plan)
        self.play(array.off.animate.set_value(1), array.ringed.animate.set_value(1),
                  run_time=T3_OFF_TIME)
        self.wait(T3_SETTLE)
        self.beat()

        self.play(self.say("every trap moves at once"))
        self.play(array.moved.animate.set_value(1),
                  run_time=longest_move(self.plan) * T3_SCALE / TWEEZER_SPEED)
        self.play(array.ringed.animate.set_value(0), run_time=0.4)
        self.wait(T3_SETTLE)
        self.beat()


class TweezerArray3DLoop(TweezerArray3D):
    """The rearranged block in the tilted view, turning a quarter turn about
    the optical axis: a square block comes back onto itself, so the clip
    loops."""

    def construct(self):
        self.build()
        array = self.array
        array.rearrange(self.plan)
        array.off.set_value(1)
        array.moved.set_value(1)
        self.elevation.set_value(TW_ELEVATION)
        self.azimuth.set_value(TW_AZIMUTH)
        self.plane_shown.set_value(1)
        array.redraw()
        self.note = step_caption("a defect-free block", self.title)
        self.add_all()
        self.play(self.azimuth.animate.set_value(TW_AZIMUTH + PI / 2),
                  rate_func=linear, run_time=T3_TURN_TIME)
```

- [ ] **Step 6: Dry-run both**

```bash
uv run manim -ql --dry_run src/manim_atoms/tweezers/scenes/array_3d.py TweezerArray3D
uv run manim -ql --dry_run src/manim_atoms/tweezers/scenes/array_3d.py TweezerArray3DLoop
```
Expected: `Played 12 animations` and `Played 1 animations`. The second takes over a minute.

- [ ] **Step 7: Render, read a frame at every stop, and tune the beam**

Run the frame check for `array_3d` / `TweezerArray3D`. Also take one frame halfway through the tilt and one mid-move.

| Stop | Must be true |
|---|---|
| 1 top-down | indistinguishable from `TweezerRearrangement`'s loaded frame: round spots, no beams |
| mid-tilt | spots flattening into ellipses, beams growing from them, no jump or flicker |
| 2 tilted | each trap an hourglass, narrowest at its atom, fading to nothing at both ends with no hard edge; the focal plane's outline passes through the atoms |
| 3 off | 25 beams, each separate from its neighbours |
| 4 moved | a 5 × 5 block of beams; atoms at the waists |

The beam's proportions are first guesses, checked only on a rough test frame, where a 0.9 Rayleigh range gave separate columns and 0.42 gave haze. Tune `TW_RAYLEIGH`, `TW_REACH`, `TW_ELEVATION` and `TWEEZER_OPACITY` until, at stop 3:
- sampling on a beam's axis a third of the way up and midway between it and its neighbour at the same height gives values that differ by at least 25 in each channel;
- the pixel at the very end of a beam is within 8 of the background (16, 16, 16).

With all 81 beams lit (stop 2) the back rows will overlap; that is acceptable there, since the stop is about a trap being a beam. If it reads as fog, lower `TWEEZER_OPACITY` rather than narrowing the beams.

If `TW_SPOT_RADIUS` has to change, re-run Task 5's frame check: the top-down scene uses it too.

- [ ] **Step 8: Check the loop closes**

Render `TweezerArray3DLoop`, take `-t 0.0 --final`, read both. Expected: the same picture.

- [ ] **Step 9: Index it**

In `docs/index.md`, add to "Tweezer arrays":

```markdown
- **A tweezer seen from the side**: a focused Gaussian beam through a tilted view, fading away from its focus; and the outline of the focal plane. `tweezers.tools.beams`: `hourglass_trap`, `beam_half_width`, `axial_intensity`, `focal_plane`.
```

and to "Worked examples by pattern":

```markdown
- **A top-down picture tilting into a view from an angle**, and a clip that turns it. `tweezers.scenes.array_3d`: `TweezerArray3D`, `TweezerArray3DLoop`.
```

Run: `python scripts/index.py --write && python scripts/index.py`

- [ ] **Step 10: Commit and push**

```bash
git add src/manim_atoms/tweezers/tools/beams.py src/manim_atoms/tweezers/scenes/array_3d.py \
        src/manim_atoms/tweezers/style.py tests/test_tweezer_beams.py docs/index.md docs/reference.md
git commit -m "tweezers: TweezerArray3D, each trap a focused beam in a tilted view"
git push
```

---

### Task 7 (light track): phase-mask and focal-plane pictures in core

**Files:**
- Modify: `src/manim_atoms/style.py` (append)
- Modify: `src/manim_atoms/core/optics.py` (module docstring; append)
- Test: `tests/test_phase_colors.py`
- Modify: `docs/index.md`, `docs/reference.md` (generated)

**Interfaces:**
- Consumes: nothing new.
- Produces: style `PHASE_COLORS`, `LENS_STYLE`, `SLM_STYLE`; `phase_rgb(phase) -> uint8 (..., 3)`; `PhaseMask(phase, aperture=None)` with `paint(phase)`; `phase_wheel(radius, pixels=160) -> PhaseMask`; `FocalImage(intensity, color, full=1.0, gamma=1.0)` with `paint(intensity)`; `make_lens(center, height, bulge)`; `make_slm(center, height, depth) -> VGroup(body, panel)`.

- [ ] **Step 1: Take the baseline of the scenes that use `core/optics.py`**

Before editing anything:

```bash
S=.claude/skills/verify-refactor/scripts
$S/last_frames.sh /tmp/optics_before 'squeezing|dipole|slicing|signal_injection'
```
Expected: `rendered N last frames into /tmp/optics_before`, no `FAIL` lines.

- [ ] **Step 2: Write the failing tests**

`tests/test_phase_colors.py`:

```python
"""The phase wheel: it wraps, every stop shows on the background, and a
phase mask is clipped to its aperture. Builds images but renders nothing."""

import numpy as np

from manim_atoms.core.optics import FocalImage, PhaseMask, phase_rgb
from manim_atoms.style import PHASE_COLORS, PLOT_BACKGROUND

TAU = 2 * np.pi


def test_the_wheel_wraps():
    assert PHASE_COLORS[0] == PHASE_COLORS[-1]
    phase = np.array([0.3, 1.7, 5.0])
    assert np.array_equal(phase_rgb(phase), phase_rgb(phase + TAU))
    assert np.array_equal(phase_rgb(phase), phase_rgb(phase - 3 * TAU))


def test_there_is_no_step_anywhere_round_the_wheel():
    wheel = phase_rgb(np.linspace(0, TAU, 2000)).astype(int)
    assert np.abs(np.diff(wheel, axis=0)).max() <= 6
    assert np.abs(phase_rgb(TAU - 1e-9).astype(int) - phase_rgb(0.0).astype(int)).max() <= 6


def test_every_colour_is_clear_of_the_background():
    background = int(PLOT_BACKGROUND[1:3], 16)
    wheel = phase_rgb(np.linspace(0, TAU, 256, endpoint=False)).astype(int)
    assert (wheel.max(axis=1) - background).min() > 120


def test_opposite_phases_are_told_apart():
    a, b = phase_rgb(np.array([0.0, 1.0, 2.0])).astype(int), phase_rgb(np.array([3.14, 4.14, 5.14])).astype(int)
    assert np.abs(a - b).sum(axis=1).min() > 150


def test_a_mask_is_clipped_to_its_aperture_and_repaints():
    aperture = np.array([[1.0, 0.0], [0.5, 1.0]])
    mask = PhaseMask(np.zeros((2, 2)), aperture)
    assert mask.pixel_array[..., 3].tolist() == [[255, 0], [127, 255]]
    before = mask.pixel_array.copy()
    mask.paint(np.full((2, 2), np.pi))
    assert not np.array_equal(mask.pixel_array[..., :3], before[..., :3])
    assert np.array_equal(mask.pixel_array[..., 3], before[..., 3])
    assert np.array_equal(PhaseMask(np.full((2, 2), 9 * np.pi)).pixel_array, PhaseMask(np.full((2, 2), np.pi)).pixel_array)


def test_a_focal_image_is_as_opaque_as_the_light_is_bright():
    image = FocalImage(np.array([[0.0, 0.25], [1.0, 4.0]]), "#ffffff", gamma=0.5)
    assert image.pixel_array[..., 3].tolist() == [[0, 127], [255, 255]]
    image.paint(np.zeros((2, 2)))
    assert image.pixel_array[..., 3].max() == 0
```

- [ ] **Step 3: Run them to see them fail**

Run: `uv run pytest tests/test_phase_colors.py -q`
Expected: `ImportError: cannot import name 'FocalImage' from 'manim_atoms.core.optics'`.

- [ ] **Step 4: Add the style constants**

Append to `src/manim_atoms/style.py`:

```python

# --- phase ----------------------------------------------------------------
# A phase is an angle, so its ramp is a wheel: it ends on the colour it began
# with, and a mask that wraps from 2 pi back to 0 shows no edge there. The
# stops run round the hue circle at one muted strength, every one clear of
# the background.
PHASE_COLORS = [ManimColor(c) for c in
                ["#e0625c", "#e6b450", "#7cc470", "#4fc1c1", "#5b8cff", "#b07ce0", "#e0625c"]]
# A lens and a modulator are furniture: the optics grey, with a faint fill so
# they read as glass and as a panel rather than as outlines.
LENS_STYLE = dict(stroke_width=3, stroke_color=OPTIC_COLOR, fill_color=OPTIC_COLOR,
                  fill_opacity=0.12)
SLM_STYLE = dict(stroke_width=3, stroke_color=OPTIC_COLOR, fill_color=OPTIC_COLOR,
                 fill_opacity=0.3)
```

- [ ] **Step 5: Add the pictures and the furniture**

In `src/manim_atoms/core/optics.py`, replace the module docstring with:

```python
"""Optics: beams drawn as Gaussian profiles, an optical cavity, and the
pictures and furniture of a hologram.

- gaussian_band, gaussian_spot: a beam seen side on as nested bands,
  brightest along its axis, or end on as nested discs. The trapping
  figures' dipole traps, clock and push beams; a cavity's mode.
- make_cavity: two concave mirrors with the mode between them, a probe
  beam through it and a detector after it; rabi_transmission is what that
  detector sees with atoms coupled to the mode (the vacuum Rabi splitting).
- PhaseMask: a phase map as a picture, coloured round a wheel that wraps
  (phase_rgb), with phase_wheel as its key; FocalImage: an intensity map as
  a camera would show it. Both repaint from an array.
- make_lens, make_slm: a lens and a spatial light modulator, edge on.
"""
```

and append to the file:

```python


def _phase_lut(size=256):
    """PHASE_COLORS as ``size`` evenly spaced RGB rows, once round the wheel."""
    lut = np.empty((size, 3), dtype=np.uint8)
    for i in range(size):
        t = i / size * (len(PHASE_COLORS) - 1)
        k = int(t)
        lut[i] = color_to_int_rgb(interpolate_color(PHASE_COLORS[k], PHASE_COLORS[k + 1], t - k))
    return lut


_PHASE_LUT = _phase_lut()


def phase_rgb(phase):
    """The phase wheel's colour at each phase, as uint8 RGB: any phase, since
    only its value mod 2 pi counts."""
    share = np.mod(np.asarray(phase, dtype=float), TAU) / TAU
    return _PHASE_LUT[np.minimum((share * len(_PHASE_LUT)).astype(int), len(_PHASE_LUT) - 1)]


class PhaseMask(ImageMobject):
    """A phase map as a picture, coloured round the phase wheel.

    ``phase`` is a 2D array in radians. ``aperture``, if given, is an array of
    the same shape, 0 to 1: how opaque each pixel is, so the picture can be
    clipped to a round pupil. paint(phase) redraws it. Like a VideoFrame,
    don't animate its opacity -- the animation would paint over the redraws.
    """

    def __init__(self, phase, aperture=None, **kwargs):
        self.aperture = None if aperture is None else np.asarray(aperture, dtype=float)
        super().__init__(self._pixels(phase), **kwargs)
        self.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])

    def _pixels(self, phase):
        phase = np.asarray(phase, dtype=float)
        out = np.empty((*phase.shape, 4), dtype=np.uint8)
        out[..., :3] = phase_rgb(phase)
        out[..., 3] = 255 if self.aperture is None else np.clip(255 * self.aperture, 0, 255)
        return out

    def paint(self, phase):
        """Redraw from a new phase array of the same shape."""
        self.pixel_array = self._pixels(phase)
        self.orig_alpha_pixel_array = self.pixel_array[:, :, 3].copy()
        return self


def phase_wheel(radius, pixels=160):
    """The key to a PhaseMask: a ring coloured by angle, 0 at the right and
    rising anticlockwise."""
    c = (np.arange(pixels) + 0.5) / pixels * 2 - 1
    x, y = np.meshgrid(c, -c)
    rho = np.hypot(x, y)
    ring = ((rho <= 1) & (rho >= 0.6)).astype(float)
    wheel = PhaseMask(np.arctan2(y, x), ring)
    wheel.set_resampling_algorithm(RESAMPLING_ALGORITHMS["linear"])
    return wheel.set(height=2 * radius)


class FocalImage(ImageMobject):
    """An intensity map as a picture: one colour, as opaque as the light is
    bright, the way a camera in the focal plane would show it.

    paint(intensity) redraws it from a 2D array; ``full`` is the intensity
    drawn fully opaque, and ``gamma`` below 1 lifts the faint parts (a ghost
    spot, an aberrated spot's skirt) into view. Don't animate its opacity.
    """

    def __init__(self, intensity, color, full=1.0, gamma=1.0, **kwargs):
        self.rgb = np.array(color_to_int_rgb(ManimColor(color)), dtype=np.uint8)
        self.full, self.gamma = full, gamma
        super().__init__(self._pixels(intensity), **kwargs)
        self.set_resampling_algorithm(RESAMPLING_ALGORITHMS["linear"])

    def _pixels(self, intensity):
        level = np.clip(np.asarray(intensity, dtype=float) / self.full, 0, 1) ** self.gamma
        out = np.empty((*level.shape, 4), dtype=np.uint8)
        out[..., :3] = self.rgb
        out[..., 3] = 255 * level
        return out

    def paint(self, intensity):
        """Redraw from a new intensity array of the same shape."""
        self.pixel_array = self._pixels(intensity)
        self.orig_alpha_pixel_array = self.pixel_array[:, :, 3].copy()
        return self


def make_lens(center, height, bulge=40 * DEGREES):
    """A thin lens seen edge on, its axis horizontal: two arcs meeting at the
    rim, ``height`` tall. ``bulge`` is the angle each arc turns through."""
    center = np.array(center, dtype=float)
    top, bottom = center + UP * height / 2, center + DOWN * height / 2
    lens = ArcBetweenPoints(top, bottom, angle=bulge)
    lens.append_points(ArcBetweenPoints(bottom, top, angle=bulge).points)
    return lens.set_style(**LENS_STYLE)


def make_slm(center, height, depth=0.16):
    """A spatial light modulator seen edge on, facing right: the panel the
    light meets, drawn heavy, on the body behind it. Rotate it about its
    centre to turn it."""
    center = np.array(center, dtype=float)
    body = Rectangle(width=depth, height=height, **SLM_STYLE).move_to(center + LEFT * depth / 2)
    panel = Line(center + UP * height / 2, center + DOWN * height / 2,
                 stroke_width=MIRROR_STROKE_WIDTH, color=OPTIC_COLOR)
    return VGroup(body, panel)
```

- [ ] **Step 6: Run the tests**

Run: `uv run pytest tests/test_phase_colors.py -q`
Expected: 6 passed.

- [ ] **Step 7: Look at the wheel and the furniture**

Write `/tmp/wheel_check.py`:

```python
import numpy as np
from manim import *

from manim_atoms.style import *
from manim_atoms.core.holography import grating_phase, illumination, pupil_grid, zernike
from manim_atoms.core.optics import PhaseMask, make_lens, make_slm, phase_wheel


class WheelCheck(Scene):
    def construct(self):
        x, y, rho, theta = pupil_grid(128)
        a = illumination(rho)
        self.add(
            phase_wheel(1.2).move_to([-5, 2, 0]),
            PhaseMask(grating_phase(x, y, 3, 0), a).set(height=3).move_to([-1.5, 2, 0]),
            PhaseMask(2.0 * zernike(3, 1, rho, theta), a).set(height=3).move_to([2.5, 2, 0]),
            make_lens([-4, -2, 0], 2.4),
            make_slm([0, -2, 0], 2.0),
        )
```

```bash
uv run manim -ql -s --media_dir /tmp/wheel_media /tmp/wheel_check.py WheelCheck
```
Read the PNG under `/tmp/wheel_media/images/wheel_check/`. Expected: the ring runs through every colour with no seam; the grating is three smooth cycles with no edge where the phase wraps; the lens is a pointed lens shape; the SLM is a heavy line on a body.

If two neighbouring stops look alike or one is dim, change `PHASE_COLORS` (keep the first and last equal) and re-run Step 6: the tests bound how dark a colour may be and how different opposite phases must be.

- [ ] **Step 8: Prove the existing scenes are unchanged**

```bash
S=.claude/skills/verify-refactor/scripts
$S/last_frames.sh /tmp/optics_after 'squeezing|dipole|slicing|signal_injection'
uv run python $S/compare_frames.py /tmp/optics_before /tmp/optics_after
uv run --with pyflakes python $S/undefined_names.py
```
Expected: no image differs or is missing; nothing in `style` or `core.optics` reported undefined.

- [ ] **Step 9: Index it**

In `docs/index.md`, add to "Holograms and phase masks":

```markdown
- **A phase map as a picture**, coloured round a wheel that wraps so a 2π step shows no edge, and the key to it. `core.optics`: `PhaseMask`, `phase_rgb`, `phase_wheel`.
- **A focal plane as a camera would see it**: one colour, as opaque as the light is bright. `core.optics`: `FocalImage`.
```

and to "Optics: beams and cavities":

```markdown
- **A lens and a spatial light modulator**, edge on. `core.optics`: `make_lens`, `make_slm`.
```

Run: `python scripts/index.py --write && python scripts/index.py`

- [ ] **Step 10: Commit and push**

```bash
git add src/manim_atoms/style.py src/manim_atoms/core/optics.py tests/test_phase_colors.py \
        docs/index.md docs/reference.md
git commit -m "core: PhaseMask on a wrapping colour wheel, FocalImage, a lens and an SLM"
git push
```

---

### Task 8 (light track): the hologram tools and `PhaseMaskBuildingBlocks`

**Files:**
- Create: `src/manim_atoms/tweezers/tools/holograms.py`
- Create: `src/manim_atoms/tweezers/scenes/holography.py`
- Test: `tests/test_tweezer_holograms.py`
- Modify: `docs/index.md`, `docs/reference.md` (generated)

**Interfaces:**
- Consumes: `core.holography` (Task 2); `PhaseMask`, `FocalImage`, `phase_wheel`, `make_lens`, `make_slm` (Task 7); `heading` and the style (Task 4).
- Produces:
  - `HG_N`, `HG_PAD`, `HG_VIEW`, `HG_SPACING`, `HG_GAMMA`, `HG_SEED`.
  - `grid_spots(rows, cols, spacing) -> (rows*cols, 2)`; `spots_from_sites(xy, pitch, spacing)`.
  - `starting_mask(x, y, spots) -> phase`; `iterate_hologram(x, y, amplitude, spots, steps) -> (masks, intensities)`, two lists of `steps + 1`.
  - `focal_view(phase, amplitude, view, pad) -> (2*view*pad + 1,) * 2` intensity.
  - `framed(image)`, `panel_label(text, panel, direction=UP)`, `bar_chart(values, full, width, height, gap) -> VGroup(baseline, bars)`.
  - `trace_ray(height, slope, start, lenses, end) -> [(x, height), ...]`; `beamlet(half_width, slope, start, lenses, end, axis, opacity, color) -> Polygon`.
  - In the scene module: `HOLO_HEADING`, `HOLO_SETTLE`, and `PhaseMaskBuildingBlocks`.

- [ ] **Step 1: Write the failing tests**

`tests/test_tweezer_holograms.py`:

```python
"""The hologram scenes' helpers: spots in the hologram's units, the focal
plane's crop, rays through thin lenses, the bar chart, the iteration.
Builds mobjects but renders nothing."""

import numpy as np
import pytest

from manim_atoms.core.holography import illumination, pupil_grid, uniformity
from manim_atoms.tweezers.physics.rearrangement import square_sites
from manim_atoms.tweezers.tools.holograms import (
    HG_N, HG_PAD, HG_VIEW, bar_chart, focal_view, grid_spots, iterate_hologram,
    spots_from_sites, trace_ray,
)


def test_grid_spots_are_centred_and_run_from_the_top_left():
    spots = grid_spots(3, 5, 4)
    assert np.allclose(spots.mean(axis=0), 0)
    assert np.allclose(spots[0], [-8, 4]) and np.allclose(spots[-1], [8, -4])
    assert np.allclose(spots_from_sites(square_sites(3, 5, 0.5), 0.5, 4), spots)


def test_the_focal_view_is_centred_on_the_axis():
    _, _, rho, _ = pupil_grid(HG_N)
    view = focal_view(np.zeros((HG_N, HG_N)), illumination(rho))
    side = 2 * HG_VIEW * HG_PAD + 1
    assert view.shape == (side, side)
    assert np.unravel_index(view.argmax(), view.shape) == (side // 2, side // 2)


def test_a_four_f_relay_images_the_start_onto_the_far_focus_inverted():
    # start a focal length before the first lens; lenses 2f apart; end a focal length after
    points = trace_ray(0.0, 0.1, 0.0, [(2.0, 2.0), (6.0, 2.0)], 8.0)
    assert points[-1] == pytest.approx((8.0, 0.0))
    assert points[2][1] - points[1][1] == pytest.approx(0.0)  # parallel to the axis between
    out = trace_ray(0.3, 0.0, 0.0, [(2.0, 2.0), (6.0, 2.0)], 8.0)
    assert out[-1][1] == pytest.approx(-0.3)


def test_lenses_outside_the_span_are_ignored():
    assert trace_ray(0.2, 0.0, 0.0, [(-1.0, 1.0), (5.0, 1.0)], 4.0) == [(0.0, 0.2), (4.0, 0.2)]


def test_bars_stand_on_the_baseline_and_negative_ones_hang_below():
    baseline, bars = bar_chart([1.0, -0.5, 0.0], full=1.0, width=3.0, height=2.0)
    assert len(bars) == 3 and baseline.width == pytest.approx(3.0)
    assert bars[0].get_bottom()[1] == pytest.approx(0) and bars[0].height == pytest.approx(2.0)
    assert bars[1].get_top()[1] == pytest.approx(0) and bars[1].height == pytest.approx(1.0)


def test_the_iteration_keeps_every_mask_and_ends_evenly_lit():
    x, y, rho, _ = pupil_grid(64)
    masks, intensities = iterate_hologram(x, y, illumination(rho), grid_spots(3, 3), 25)
    assert len(masks) == len(intensities) == 26
    assert uniformity(intensities[-1]) > 0.95 > uniformity(intensities[0])
```

- [ ] **Step 2: Run them to see them fail**

Run: `uv run pytest tests/test_tweezer_holograms.py -q`
Expected: `ModuleNotFoundError: No module named 'manim_atoms.tweezers.tools.holograms'`.

- [ ] **Step 3: Write the tools**

`src/manim_atoms/tweezers/tools/holograms.py`:

```python
"""What the hologram scenes share: the mask and focal-plane pictures' sizes,
the spots of an array in the hologram's units, the array's mask at each
step of its iteration, a bar chart of trap brightnesses or mode amplitudes,
and light traced through thin lenses.

The numbers are core.holography's and the pictures core.optics'; this is
the tweezer scenes' layout of them.
"""

import numpy as np
from manim import *

from manim_atoms.tweezers.style import *
from manim_atoms.core.holography import far_field, spot_phase, wgs_step

# --- the hologram's sampling -------------------------------------------------
HG_N = 128  # pixels across the mask: fine enough that a grating's steps do not show
HG_PAD = 4  # focal-plane pixels per diffraction limit
HG_VIEW = 14  # the focal plane is shown out to this many diffraction limits
HG_SPACING = 4  # between neighbouring spots: clear of each other's rings
HG_GAMMA = 0.6  # lifts faint light (ghost spots, an aberrated spot's skirt) into view
HG_SEED = 1  # of the spots' starting phases


def grid_spots(rows, cols, spacing=HG_SPACING):
    """The (rows * cols, 2) spots of a square array about the axis, in
    diffraction limits, row by row from the top left."""
    return np.array([[(c - (cols - 1) / 2) * spacing, ((rows - 1) / 2 - r) * spacing]
                     for r in range(rows) for c in range(cols)], dtype=float)


def spots_from_sites(xy, pitch, spacing=HG_SPACING):
    """Trap positions in scene units as spots in diffraction limits: traps a
    ``pitch`` apart are ``spacing`` diffraction limits apart."""
    return np.asarray(xy, dtype=float) / pitch * spacing


def starting_mask(x, y, spots):
    """The mask an array's hologram starts from: the sum of its spots'
    gratings, each with a random phase."""
    phases = np.random.default_rng(HG_SEED).uniform(0, TAU, len(spots))
    return spot_phase(x, y, spots, phases)


def iterate_hologram(x, y, amplitude, spots, steps):
    """Weighted Gerchberg-Saxton from the starting mask: (the mask before
    each step, the spots' intensities under each of those masks)."""
    mask, weights = starting_mask(x, y, spots), np.ones(len(spots))
    masks, intensities = [], []
    for _ in range(steps + 1):
        masks.append(mask)
        mask, weights, lit = wgs_step(mask, weights, amplitude, x, y, spots)
        intensities.append(lit)
    return masks, intensities


def focal_view(phase, amplitude, view=HG_VIEW, pad=HG_PAD):
    """The middle of the focal plane a mask makes, out to ``view`` diffraction
    limits either side of the axis: what a FocalImage is painted from."""
    image = far_field(phase, amplitude, pad)
    centre, half = image.shape[0] // 2, int(round(view * pad))
    return image[centre - half:centre + half + 1, centre - half:centre + half + 1]


def framed(image):
    """A thin frame round a picture, so it reads as set into the slide."""
    return SurroundingRectangle(image, buff=0, **IMAGE_BORDER_STYLE)


def panel_label(text, panel, direction=UP):
    """A picture's label, in grey beside it."""
    return Tex(text, font_size=FONT_STEP, color=STEP_COLOR).next_to(panel, direction, buff=0.2)


def bar_chart(values, full, width, height, gap=0.25):
    """A bar per value on a baseline, ``width`` across, a value of ``full``
    drawn ``height`` tall, with its lower left corner at the origin.
    Negative values hang below the baseline. Returns VGroup(baseline, bars)."""
    values = np.asarray(values, dtype=float)
    slot = width / len(values)
    bars = VGroup()
    for i, value in enumerate(values):
        tall = height * value / full
        bar = Rectangle(width=slot * (1 - gap), height=max(abs(tall), 1e-3), stroke_width=0,
                        fill_color=BAR_COLOR, fill_opacity=1)
        bar.move_to([slot * (i + 0.5), tall / 2, 0])
        bars.add(bar)
    return VGroup(Line(ORIGIN, RIGHT * width, **BAR_BASELINE_STYLE), bars)


def trace_ray(height, slope, start, lenses, end):
    """A paraxial ray through thin lenses: it leaves x = ``start`` at
    ``height`` above the axis with ``slope``, and each lens (x, focal length)
    it meets before x = ``end`` turns it by -height / f. Returns the (x,
    height) at the start, at each lens and at the end."""
    x, points = start, [(start, height)]
    for at, focal in sorted(lenses):
        if not start < at < end:
            continue
        height += slope * (at - x)
        slope -= height / focal
        x = at
        points.append((x, height))
    points.append((end, height + slope * (end - x)))
    return points


def beamlet(half_width, slope, start, lenses, end, axis, opacity, color=TWEEZER_COLOR):
    """A beam ``half_width`` either side of its chief ray, leaving x =
    ``start`` on the optical axis with ``slope`` and traced through
    ``lenses`` to ``end``: the band between its two edge rays. ``axis`` is
    the scene y of the optical axis."""
    upper = trace_ray(half_width, slope, start, lenses, end)
    lower = trace_ray(-half_width, slope, start, lenses, end)
    corners = [[x, axis + h, 0] for x, h in upper] + [[x, axis + h, 0] for x, h in lower[::-1]]
    return Polygon(*corners, stroke_width=0, fill_color=color, fill_opacity=opacity)
```

- [ ] **Step 4: Run the tests**

Run: `uv run pytest tests/test_tweezer_holograms.py -q`
Expected: 6 passed.

- [ ] **Step 5: Start the scene module with its first scene**

`src/manim_atoms/tweezers/scenes/holography.py`. The import block names everything all four scenes use; Tasks 9–11 append their scenes to this file and add nothing to the imports.

```python
"""How a spatial light modulator makes a tweezer array: the optical train,
what a phase mask does to the focus, how the mask is found, and how
aberrations are taken out of it.

An SLM sets the phase of the light across the beam, pixel by pixel, and
leaves its brightness alone. A lens turns that phase pattern into the
pattern of light in its focal plane, which is the Fourier transform of the
field on the SLM. Every picture of a focal plane here is computed from the
mask shown beside it (core.holography), so what the mask does is what is
seen. Phase is coloured round a wheel: 0 and 2 pi are one colour, so a mask
that wraps shows no edge.

- OpticalTrain: the SLM, the relay, the objective and the foci, side on.
  A beat() on the bare train, after the grating steers the focus, after
  the array, and after the label.
- PhaseMaskBuildingBlocks: a flat mask, a grating, a lens and a sum of
  gratings, each beside its focal plane. A beat() after each.
- HologramIteration: weighted Gerchberg-Saxton, step by step and then run
  to the end. A beat() on the loop, on the starting mask, after each of
  three iterations and after the run.
- ZernikeCorrection: the Zernike modes, an aberrated spot, and its
  correction. A beat() on the pyramid, on the aberration, after each mode
  is taken out, and after the array is corrected.

Angles in the train are exaggerated and its relay is two lenses. The
aberration is a few radians, far more than a good objective has.
"""

import numpy as np
from manim import *

from manim_atoms.tweezers.style import *
from manim_atoms.core.holography import (
    grating_phase,
    illumination,
    lens_phase,
    osa_to_nm,
    pupil_grid,
    strehl,
    uniformity,
    zernike,
)
from manim_atoms.core.optics import FocalImage, PhaseMask, make_lens, make_slm, phase_wheel
from manim_atoms.core.primitives import make_atom
from manim_atoms.tweezers.tools.holograms import (
    HG_GAMMA,
    HG_N,
    bar_chart,
    beamlet,
    focal_view,
    framed,
    grid_spots,
    iterate_hologram,
    panel_label,
    starting_mask,
    trace_ray,
)
from manim_atoms.tweezers.tools.tweezer_array import heading

HOLO_HEADING = np.array([-6.6, 3.6, 0.0])  # every hologram scene's heading corner
HOLO_SETTLE = 0.6  # the pause before a stop

# --- building-blocks geometry ------------------------------------------------
# The mask on the left and the focal plane it makes on the right, the same
# size, with the lens that joins them named on an arrow between.
PB_MASK = np.array([-3.4, -0.5, 0.0])
PB_FOCAL = np.array([3.4, -0.5, 0.0])
PB_SIZE = 4.4  # each picture's height
PB_WHEEL = np.array([-6.2, -2.3, 0.0])  # the phase key, beside the mask
PB_PERIODS = 7  # the grating's, across the aperture
PB_WAVES = 1.2  # the lens phase, at the aperture's edge
PB_SWEEP_TIME = 2.5


class PhaseMaskBuildingBlocks(Scene):
    """A phase mask beside the focal plane it makes: flat, a grating that
    steers the spot, a lens that defocuses it, and gratings summed into an
    array. One beat() per mask."""

    def beat(self):
        """The pause after each step: nothing here, a click on the slide version."""

    def construct(self):
        x, y, rho, _ = pupil_grid(HG_N)
        amplitude = illumination(rho)
        periods, angle, waves = ValueTracker(0), ValueTracker(0), ValueTracker(0)

        def phase():
            k, a = periods.get_value(), angle.get_value()
            return (grating_phase(x, y, k * np.cos(a), k * np.sin(a))
                    + lens_phase(rho, waves.get_value()))

        mask = PhaseMask(phase(), amplitude).set(height=PB_SIZE).move_to(PB_MASK)
        focal = FocalImage(focal_view(phase(), amplitude), FOCAL_SPOT_COLOR, gamma=HG_GAMMA)
        focal.set(height=PB_SIZE).move_to(PB_FOCAL)
        frame = framed(focal)
        arrow = Arrow(mask.get_right(), focal.get_left(), **TRANSFORM_ARROW_STYLE)
        lens_label = Tex("lens", font_size=FONT_STEP, color=STEP_COLOR).next_to(arrow, UP, buff=0.1)
        labels = VGroup(panel_label("SLM: phase", mask), panel_label("focal plane", focal))
        wheel = phase_wheel(0.45).move_to(PB_WHEEL)
        wheel_labels = VGroup(
            MathTex("0", font_size=FONT_TICK).next_to(wheel, RIGHT, buff=0.08),
            MathTex(r"\pi", font_size=FONT_TICK).next_to(wheel, LEFT, buff=0.08),
        )
        title = heading("What a phase mask does").move_to(HOLO_HEADING, aligned_edge=UL)
        note = Tex("flat: one spot on the axis", font_size=FONT_STEP, color=STEP_COLOR)
        note.next_to(title, DOWN, buff=0.2, aligned_edge=LEFT)

        def say(text):
            nonlocal note
            new = Tex(text, font_size=FONT_STEP, color=STEP_COLOR)
            new.next_to(title, DOWN, buff=0.2, aligned_edge=LEFT)
            swap = Succession(FadeOut(note, run_time=0.3), FadeIn(new, run_time=0.3))
            note = new
            return swap

        self.add(periods, angle, waves)
        self.play(FadeIn(title), FadeIn(note), FadeIn(mask), FadeIn(focal), FadeIn(frame),
                  FadeIn(labels), GrowArrow(arrow), FadeIn(lens_label), FadeIn(wheel),
                  FadeIn(wheel_labels))
        mask.add_updater(lambda m: m.paint(phase()))
        focal.add_updater(lambda m: m.paint(focal_view(phase(), amplitude)))
        self.wait(HOLO_SETTLE)
        self.beat()

        # a grating steers the spot, as far as it has periods, the way it slopes
        self.play(say("a grating steers it"))
        self.play(periods.animate.set_value(PB_PERIODS), run_time=PB_SWEEP_TIME)
        self.play(angle.animate.set_value(PI / 2), run_time=PB_SWEEP_TIME)
        self.wait(HOLO_SETTLE)
        self.beat()

        # a lens moves the focus along the axis: here, the spot blurs
        self.play(say("a lens moves the focus out of this plane"))
        self.play(periods.animate.set_value(0), run_time=1.0)
        angle.set_value(0)
        self.play(waves.animate.set_value(PB_WAVES), run_time=PB_SWEEP_TIME)
        self.wait(HOLO_SETTLE)
        self.beat()

        # gratings summed: one spot each, but not equally bright
        self.play(say("gratings summed: a spot each, unevenly bright"))
        self.play(waves.animate.set_value(0), run_time=1.0)
        mask.clear_updaters()
        focal.clear_updaters()
        for rows, cols in ((1, 2), (1, 5), (5, 5)):
            spots = grid_spots(rows, cols)
            summed = starting_mask(x, y, spots)
            mask.paint(summed)
            focal.paint(focal_view(summed, amplitude) * len(spots))
            self.wait(1.0)
        self.wait(HOLO_SETTLE)
        self.beat()
```

- [ ] **Step 6: Dry-run**

Run: `uv run manim -ql --dry_run src/manim_atoms/tweezers/scenes/holography.py PhaseMaskBuildingBlocks`
Expected: `Played 16 animations`.

- [ ] **Step 7: Render and read a frame at every stop**

Run the frame check for `holography` / `PhaseMaskBuildingBlocks`. Add frames mid-sweep of the grating and of the lens.

| Stop | Must be true |
|---|---|
| 1 flat | the mask is one colour; one spot dead centre of the focal plane; the labels, arrow and wheel overlap nothing |
| mid grating | the mask is stripes; the spot is off centre, toward the right |
| 2 grating turned | the stripes are horizontal; the spot is straight above centre |
| 3 lens | the mask is rings; the spot is a dim blur |
| 4 array | 25 spots in a square, visibly not all the same brightness; faint ghosts are acceptable |

If the spot at stop 2 is below centre rather than above, the picture and the grid disagree about which way is up: check `pupil_grid` still has row 0 at y = +1, and do not flip the image to compensate.

If the uneven brightness at stop 4 does not show, lower `HG_GAMMA` toward 0.5 or raise the `full` the image is painted against.

- [ ] **Step 8: Index it**

In `docs/index.md`, add to "Tweezer arrays":

```markdown
- **A hologram scene's pieces**: an array's spots in the hologram's units, its mask at each step of the iteration, the crop of the focal plane, a picture's frame and label, and a bar per trap or per mode. `tweezers.tools.holograms`: `grid_spots`, `spots_from_sites`, `starting_mask`, `iterate_hologram`, `focal_view`, `framed`, `panel_label`, `bar_chart`.
- **Light traced through thin lenses**, as a ray or as the band between two. `tweezers.tools.holograms`: `trace_ray`, `beamlet`.
```

and to "Worked examples by pattern":

```markdown
- **A picture recomputed every frame from trackers** (a mask and the focal plane it makes). `tweezers.scenes.holography`: `PhaseMaskBuildingBlocks`.
```

Run: `python scripts/index.py --write && python scripts/index.py`

- [ ] **Step 9: Commit and push**

```bash
git add src/manim_atoms/tweezers/tools/holograms.py src/manim_atoms/tweezers/scenes/holography.py \
        tests/test_tweezer_holograms.py docs/index.md docs/reference.md
git commit -m "tweezers: PhaseMaskBuildingBlocks, a mask beside the focal plane it makes"
git push
```

---

### Task 9 (light track): `HologramIteration`

**Files:**
- Modify: `src/manim_atoms/tweezers/scenes/holography.py` (append)
- Modify: `docs/index.md`, `docs/reference.md` (generated)

**Interfaces:**
- Consumes: `iterate_hologram`, `grid_spots`, `focal_view`, `framed`, `panel_label`, `bar_chart` (Task 8); `uniformity` (Task 2); the module's imports and `HOLO_*` (Task 8).
- Produces: `HologramIteration`.

- [ ] **Step 1: Append the scene**

Append to `src/manim_atoms/tweezers/scenes/holography.py`:

```python
# --- iteration geometry ------------------------------------------------------
# The two planes side by side, joined by an arrow each way; under the focal
# plane a bar per trap, and the uniformity they add up to.
HI_MASK = np.array([-3.6, 0.5, 0.0])
HI_FOCAL = np.array([2.4, 0.5, 0.0])
HI_SIZE = 3.6  # each picture's height
HI_BARS = np.array([0.6, -3.3, 0.0])  # the bar chart's lower left corner
HI_BARS_SIZE = (3.6, 1.0)  # its width, and the height of an evenly lit trap's bar
HI_READOUT = np.array([-6.2, -2.6, 0.0])  # the iteration count's left edge
HI_STEPS = 40  # iterations run in all
HI_SLOW = 3  # of them taken one at a time
HI_RUN_TIME = 6.0  # the rest


class HologramIteration(Scene):
    """Weighted Gerchberg-Saxton finding an array's mask: the loop between
    the SLM plane and the focal plane, three iterations one at a time, then
    the run until the traps are evenly bright. A beat() on the loop, on the
    starting mask, after each slow iteration and after the run."""

    def beat(self):
        """The pause after each step: nothing here, a click on the slide version."""

    def construct(self):
        x, y, rho, _ = pupil_grid(HG_N)
        amplitude = illumination(rho)
        spots = grid_spots(5, 5)
        masks, intensities = iterate_hologram(x, y, amplitude, spots, HI_STEPS)
        even = 1 / len(spots)  # each trap's share if the light were split evenly
        step = ValueTracker(0)

        def now():
            return int(round(step.get_value()))

        mask = PhaseMask(masks[0], amplitude).set(height=HI_SIZE).move_to(HI_MASK)
        focal = FocalImage(focal_view(masks[0], amplitude), FOCAL_SPOT_COLOR, full=even,
                           gamma=HG_GAMMA).set(height=HI_SIZE).move_to(HI_FOCAL)
        frame = framed(focal)
        labels = VGroup(panel_label(r"SLM: brightness fixed, phase free", mask),
                        panel_label(r"focal plane: brightness wanted", focal))
        forward = Arrow(mask.get_right() + UP * 0.5, focal.get_left() + UP * 0.5,
                        **TRANSFORM_ARROW_STYLE)
        back = Arrow(focal.get_left() + DOWN * 0.5, mask.get_right() + DOWN * 0.5,
                     **TRANSFORM_ARROW_STYLE)
        arrow_labels = VGroup(
            Tex("lens", font_size=FONT_STEP, color=STEP_COLOR).next_to(forward, UP, buff=0.08),
            Tex("back", font_size=FONT_STEP, color=STEP_COLOR).next_to(back, DOWN, buff=0.08),
        )
        bars = always_redraw(lambda: bar_chart(intensities[now()], even, *HI_BARS_SIZE)
                             .shift(HI_BARS))
        level = DashedLine(HI_BARS + UP * HI_BARS_SIZE[1],
                           HI_BARS + UP * HI_BARS_SIZE[1] + RIGHT * HI_BARS_SIZE[0],
                           **GUIDE_STYLE)
        bars_label = Tex("each trap's brightness", font_size=FONT_STEP, color=STEP_COLOR)
        bars_label.next_to(level, UP, buff=0.12)
        count_label = Tex("iteration", font_size=FONT_READOUT).move_to(HI_READOUT, aligned_edge=LEFT)
        count = Integer(0, font_size=FONT_READOUT, group_with_commas=False)
        count.add_updater(lambda m: m.set_value(now()).next_to(count_label, RIGHT, buff=0.2,
                                                               aligned_edge=DOWN))
        even_label = Tex("uniformity", font_size=FONT_READOUT)
        even_label.next_to(count_label, DOWN, buff=0.3, aligned_edge=LEFT)
        evenness = DecimalNumber(0, num_decimal_places=2, font_size=FONT_READOUT,
                                 group_with_commas=False)
        evenness.add_updater(lambda m: m.set_value(uniformity(intensities[now()]))
                             .next_to(even_label, RIGHT, buff=0.2, aligned_edge=DOWN))
        title = heading("Finding the mask").move_to(HOLO_HEADING, aligned_edge=UL)

        self.add(step)
        self.play(FadeIn(title), FadeIn(labels), GrowArrow(forward), GrowArrow(back),
                  FadeIn(arrow_labels), FadeIn(framed(mask).set_stroke(opacity=0)), FadeIn(frame))
        self.wait(HOLO_SETTLE)
        self.beat()

        self.play(FadeIn(mask), FadeIn(focal), FadeIn(bars), FadeIn(level), FadeIn(bars_label),
                  FadeIn(count_label), FadeIn(count), FadeIn(even_label), FadeIn(evenness))
        self.wait(HOLO_SETTLE)
        self.beat()

        def show(index):
            mask.paint(masks[index])
            focal.paint(focal_view(masks[index], amplitude))

        for index in range(1, HI_SLOW + 1):
            # back to the SLM with the dim traps weighted up, then forward again
            self.play(ShowPassingFlash(back.copy().set_color(WHITE), time_width=0.6), run_time=0.7)
            mask.paint(masks[index])
            self.play(ShowPassingFlash(forward.copy().set_color(WHITE), time_width=0.6),
                      run_time=0.7)
            focal.paint(focal_view(masks[index], amplitude))
            step.set_value(index)
            self.wait(HOLO_SETTLE)
            self.beat()

        mask.add_updater(lambda m: show(now()))
        self.play(step.animate.set_value(HI_STEPS), rate_func=linear, run_time=HI_RUN_TIME)
        mask.clear_updaters()
        self.wait(HOLO_SETTLE)
        self.beat()
```

- [ ] **Step 2: Dry-run**

Run: `uv run manim -ql --dry_run src/manim_atoms/tweezers/scenes/holography.py HologramIteration`
Expected: `Played 15 animations`.

- [ ] **Step 3: Render and read a frame at every stop**

Run the frame check for `holography` / `HologramIteration`.

| Stop | Must be true |
|---|---|
| 1 the loop | two empty frames, each labelled, an arrow each way with its word; nothing overlaps; both labels fit inside the frame's width (`Tex` wraps silently: check each label is one line) |
| 2 start | the mask, 25 uneven spots, 25 bars of clearly different heights about the dashed line, "iteration 0", uniformity near 0.47 |
| 3–5 | the count reads 1, 2, 3; the bars are nearer the line each time; the uniformity rises (about 0.57, 0.70, 0.74) |
| 6 end | "iteration 40"; the bars level with the dashed line; uniformity 0.99 |

The count and the uniformity must not jump sideways as their digits change: each is placed by `next_to(..., aligned_edge=DOWN)` in its updater. If the labels are too long for the pictures, shorten the words rather than shrinking the type.

- [ ] **Step 4: Index it**

Add to "Worked examples by pattern" in `docs/index.md`:

```markdown
- **An algorithm stepped through, then run** (pictures, bars and a number all read from one step counter). `tweezers.scenes.holography`: `HologramIteration`.
```

Run: `python scripts/index.py --write && python scripts/index.py`

- [ ] **Step 5: Commit and push**

```bash
git add src/manim_atoms/tweezers/scenes/holography.py docs/index.md docs/reference.md
git commit -m "tweezers: HologramIteration, weighted Gerchberg-Saxton step by step"
git push
```

---

### Task 10 (light track): `ZernikeCorrection`

**Files:**
- Modify: `src/manim_atoms/tweezers/scenes/holography.py` (append)
- Modify: `docs/index.md`, `docs/reference.md` (generated)

**Interfaces:**
- Consumes: `zernike`, `osa_to_nm`, `strehl` (Task 2); `PhaseMask`, `FocalImage`, `phase_wheel` (Task 7); `iterate_hologram`, `grid_spots`, `focal_view`, `bar_chart`, `framed`, `panel_label` (Task 8).
- Produces: `ZernikeCorrection`.

- [ ] **Step 1: Append the scene**

Append to `src/manim_atoms/tweezers/scenes/holography.py`:

```python
# --- Zernike geometry --------------------------------------------------------
# First the pyramid: a row per radial order, widening downwards. Then the
# pupil's wavefront on the left, a bar per mode in the middle and the focal
# spot on the right.
ZC_PYRAMID_TOP = np.array([0.6, 2.6, 0.0])  # the centre of the top disc
ZC_DISC = 1.0  # each disc's height
ZC_PITCH = (1.45, 1.38)  # between discs along a row, and between rows
ZC_AMPLITUDE = 2.0  # each pyramid mode's rms, in radians: enough to wrap once or twice
ZC_NAMED = {(1, 1): "tilt", (2, 0): "defocus", (2, 2): "astigmatism",
            (3, 1): "coma", (3, 3): "trefoil", (4, 0): "spherical"}
ZC_ERROR = {(2, 2): 1.3, (3, 1): 1.0, (4, 0): 0.8}  # the aberration, rms radians per mode
ZC_PUPIL = np.array([-4.3, -0.6, 0.0])
ZC_SPOT = np.array([4.3, -0.6, 0.0])
ZC_SIZE = 3.4  # the wavefront's and the spot's height
ZC_BARS = np.array([-1.3, -1.6, 0.0])  # the bar chart's lower left corner
ZC_BARS_SIZE = (2.6, 1.6)  # its width, and the height of the largest mode's bar
ZC_SPOT_VIEW = 7  # the single spot is shown closer in than an array
ZC_FIX_TIME = 1.6  # taking one mode out


class ZernikeCorrection(Scene):
    """The Zernike modes as a pyramid of phase maps; then a wavefront made of
    three of them, the smeared focal spot it gives, and the spot sharpening
    as each mode is taken out of the mask; then the same correction on an
    array. A beat() on the pyramid, on the aberration, per mode and on the
    array."""

    def beat(self):
        """The pause after each step: nothing here, a click on the slide version."""

    def construct(self):
        x, y, rho, theta = pupil_grid(HG_N)
        amplitude = illumination(rho)
        title = heading("Aberrations, in Zernike modes").move_to(HOLO_HEADING, aligned_edge=UL)

        # --- the pyramid ---
        discs, names = Group(), VGroup()
        for j in range(15):
            n, m = osa_to_nm(j)
            at = ZC_PYRAMID_TOP + DOWN * n * ZC_PITCH[1] + RIGHT * m / 2 * ZC_PITCH[0]
            disc = PhaseMask(ZC_AMPLITUDE * zernike(n, m, rho, theta), amplitude)
            discs.add(disc.set(height=ZC_DISC).move_to(at))
            if (n, m) in ZC_NAMED:
                names.add(Tex(ZC_NAMED[n, m], font_size=FONT_MODE, color=STEP_COLOR)
                          .next_to(disc, DOWN, buff=0.04))
        wheel = phase_wheel(0.45).move_to([-5.6, -2.6, 0])
        self.play(FadeIn(title), FadeIn(discs), FadeIn(names), FadeIn(wheel))
        self.wait(HOLO_SETTLE)
        self.beat()

        # --- an aberrated wavefront and its spot ---
        modes = list(ZC_ERROR)
        left = {mode: ValueTracker(ZC_ERROR[mode]) for mode in modes}

        def error():
            return sum(left[mode].get_value() * zernike(*mode, rho, theta) for mode in modes)

        pupil = PhaseMask(error(), amplitude).set(height=ZC_SIZE).move_to(ZC_PUPIL)
        spot = FocalImage(focal_view(error(), amplitude, ZC_SPOT_VIEW), FOCAL_SPOT_COLOR,
                          gamma=HG_GAMMA).set(height=ZC_SIZE).move_to(ZC_SPOT)
        frame = framed(spot)
        labels = VGroup(panel_label("wavefront error", pupil), panel_label("focal spot", spot))
        full = max(ZC_ERROR.values())
        bars = always_redraw(lambda: bar_chart([left[mode].get_value() for mode in modes],
                                               full, *ZC_BARS_SIZE).shift(ZC_BARS))
        slot = ZC_BARS_SIZE[0] / len(modes)
        bar_names = VGroup(*[
            Tex(ZC_NAMED[mode], font_size=FONT_MODE, color=STEP_COLOR)
            .move_to(ZC_BARS + RIGHT * slot * (i + 0.5) + DOWN * 0.25)
            for i, mode in enumerate(modes)
        ])
        strehl_label = Tex("Strehl ratio", font_size=FONT_READOUT)
        strehl_label.next_to(spot, DOWN, buff=0.35).shift(LEFT * 0.5)
        ratio = DecimalNumber(0, num_decimal_places=2, font_size=FONT_READOUT,
                              group_with_commas=False)
        ratio.add_updater(lambda m: m.set_value(strehl(error(), amplitude))
                          .next_to(strehl_label, RIGHT, buff=0.2, aligned_edge=DOWN))
        self.add(*left.values())
        self.play(FadeOut(discs), FadeOut(names))
        self.play(FadeIn(pupil), FadeIn(spot), FadeIn(frame), FadeIn(labels), FadeIn(bars),
                  FadeIn(bar_names), FadeIn(strehl_label), FadeIn(ratio))
        pupil.add_updater(lambda m: m.paint(error()))
        spot.add_updater(lambda m: m.paint(focal_view(error(), amplitude, ZC_SPOT_VIEW)))
        self.wait(HOLO_SETTLE)
        self.beat()

        # --- the correction, a mode at a time ---
        for mode in modes:
            self.play(left[mode].animate.set_value(0), run_time=ZC_FIX_TIME)
            self.wait(HOLO_SETTLE)
            self.beat()

        # --- the same correction on an array's hologram ---
        spots = grid_spots(5, 5)
        hologram = iterate_hologram(x, y, amplitude, spots, 30)[0][-1]
        aberration = sum(ZC_ERROR[mode] * zernike(*mode, rho, theta) for mode in modes)
        corrected = ValueTracker(0)
        even = 1 / len(spots)

        def shown_mask():
            return hologram - corrected.get_value() * aberration

        def seen():
            return focal_view(shown_mask() + aberration, amplitude)

        pupil.clear_updaters()
        spot.clear_updaters()
        array_mask = PhaseMask(shown_mask(), amplitude).set(height=ZC_SIZE).move_to(ZC_PUPIL)
        array_spots = FocalImage(seen(), FOCAL_SPOT_COLOR, full=even, gamma=HG_GAMMA)
        array_spots.set(height=ZC_SIZE).move_to(ZC_SPOT)
        new_labels = VGroup(panel_label("SLM: hologram minus the error", array_mask),
                            panel_label("focal plane", array_spots))
        self.add(corrected)
        self.play(FadeOut(pupil), FadeOut(spot), FadeOut(labels), FadeOut(bars),
                  FadeOut(bar_names), FadeOut(strehl_label), FadeOut(ratio))
        self.play(FadeIn(array_mask), FadeIn(array_spots), FadeIn(new_labels))
        array_mask.add_updater(lambda m: m.paint(shown_mask()))
        array_spots.add_updater(lambda m: m.paint(seen()))
        self.wait(HOLO_SETTLE)
        self.play(corrected.animate.set_value(1), run_time=2 * ZC_FIX_TIME)
        self.wait(HOLO_SETTLE)
        self.beat()
```

- [ ] **Step 2: Dry-run**

Run: `uv run manim -ql --dry_run src/manim_atoms/tweezers/scenes/holography.py ZernikeCorrection`
Expected: `Played 16 animations`.

- [ ] **Step 3: Render and read a frame at every stop**

Run the frame check for `holography` / `ZernikeCorrection`.

| Stop | Must be true |
|---|---|
| 1 pyramid | fifteen discs in rows of 1, 2, 3, 4, 5; the top one a single colour; six of them named, each name under its own disc and clear of the row below; the pyramid clear of the heading and the wheel |
| 2 aberration | a swirled wavefront on the left, three bars with their names, a smeared spot on the right, a Strehl ratio well below 1 |
| 3, 4 | one bar gone each time; the spot tighter; the Strehl ratio higher |
| 5 corrected | no bars; the wavefront one colour; a single sharp spot; Strehl ratio 1.00 |
| 6 array | the mask and 25 sharp spots |

Also take a frame just after the array appears, before the correction runs: its spots must be visibly smeared, or the last stop shows nothing happening. If they are not, the pictures are fine and `ZC_ERROR` is too small for an array's wider view: raise its values together.

In the pyramid the shapes should be recognisable: defocus as rings, astigmatism as a saddle, coma as a lopsided pair of lobes, spherical as a ring inside a ring. If the wraps make them hard to read, lower `ZC_AMPLITUDE`.

- [ ] **Step 4: Index it**

Add to "Worked examples by pattern" in `docs/index.md`:

```markdown
- **A table of pictures, then a quantity taken away term by term.** `tweezers.scenes.holography`: `ZernikeCorrection`.
```

Run: `python scripts/index.py --write && python scripts/index.py`

- [ ] **Step 5: Commit and push**

```bash
git add src/manim_atoms/tweezers/scenes/holography.py docs/index.md docs/reference.md
git commit -m "tweezers: ZernikeCorrection, the modes and an aberration taken out"
git push
```

---

### Task 11 (light track): `OpticalTrain`

**Files:**
- Modify: `src/manim_atoms/tweezers/scenes/holography.py` (append)
- Modify: `docs/index.md`, `docs/reference.md` (generated)

**Interfaces:**
- Consumes: `trace_ray`, `beamlet`, `iterate_hologram`, `focal_view`, `framed`, `panel_label` (Task 8); `make_lens`, `make_slm`, `PhaseMask`, `FocalImage` (Task 7); `grating_phase` (Task 2); `make_atom` from `core.primitives`.
- Produces: `OpticalTrain`.

- [ ] **Step 1: Append the scene**

Append to `src/manim_atoms/tweezers/scenes/holography.py`:

```python
# --- optical-train geometry --------------------------------------------------
# Side on, along the bottom half of the frame: the SLM a focal length before
# the first relay lens, the two relay lenses their focal lengths apart, the
# objective a focal length after the second, and the foci a focal length
# after that. So the SLM is imaged onto the objective, and a tilt of the
# beam at the SLM becomes a sideways shift of the focus. The mask and the
# focal plane are shown face on above their places in the train.
OT_AXIS = -1.9  # the optical axis's height
OT_SLM_X = -6.0
OT_FOCAL = 2.0  # every lens's focal length
OT_LENSES = [(OT_SLM_X + OT_FOCAL, OT_FOCAL), (OT_SLM_X + 3 * OT_FOCAL, OT_FOCAL),
             (OT_SLM_X + 4 * OT_FOCAL, OT_FOCAL)]  # (x, f): relay, relay, objective
OT_PLANE_X = OT_SLM_X + 5 * OT_FOCAL  # the focal plane
OT_BEAM = 0.42  # the beam's half-width at the SLM
OT_LENS_HEIGHT = 1.9
OT_OPACITY = 0.3  # one beam's fill
OT_SLOPE = 0.11  # the steered beam's, at the SLM: exaggerated
OT_PICTURE = 1.9  # the face-on pictures' height
OT_PICTURE_Y = 1.3  # and their centres' height
OT_PERIODS_PER_SLOPE = 40  # grating periods across the mask per unit of slope drawn
OT_INCOMING = np.array([1.5, 2.6, 0.0])  # from the SLM back up the incoming beam
OT_STEER_TIME = 2.0


class OpticalTrain(Scene):
    """The light's path from the SLM to the atoms, side on: a flat mask gives
    one focus, a grating steers it, and an array's mask fans the light out
    to a row of foci. A beat() on the bare train, after the steering, after
    the array and after the label."""

    def beat(self):
        """The pause after each step: nothing here, a click on the slide version."""

    def construct(self):
        x, y, rho, _ = pupil_grid(HG_N)
        amplitude = illumination(rho)
        slm_at = np.array([OT_SLM_X, OT_AXIS, 0.0])
        slope = ValueTracker(0)

        def focus_height(s):
            return trace_ray(0.0, s, OT_SLM_X, OT_LENSES, OT_PLANE_X)[-1][1]

        def steered():
            return beamlet(OT_BEAM, slope.get_value(), OT_SLM_X, OT_LENSES, OT_PLANE_X,
                           OT_AXIS, OT_OPACITY)

        slm = make_slm(slm_at, 2 * OT_BEAM + 0.5)
        incoming = Polygon(slm_at + UP * OT_BEAM, slm_at + DOWN * OT_BEAM,
                           slm_at + DOWN * OT_BEAM + OT_INCOMING,
                           slm_at + UP * OT_BEAM + OT_INCOMING,
                           stroke_width=0, fill_color=TWEEZER_COLOR, fill_opacity=OT_OPACITY)
        lenses = VGroup(*[make_lens([at, OT_AXIS, 0], OT_LENS_HEIGHT) for at, _ in OT_LENSES])
        plane = DashedLine([OT_PLANE_X, OT_AXIS - 1.0, 0], [OT_PLANE_X, OT_AXIS + 1.0, 0],
                           **GUIDE_STYLE)
        names = VGroup(
            Tex("SLM", font_size=FONT_STEP, color=STEP_COLOR).next_to(slm, DOWN, buff=0.25),
            Tex("relay", font_size=FONT_STEP, color=STEP_COLOR)
            .next_to(VGroup(lenses[0], lenses[1]), DOWN, buff=0.2),
            Tex("objective", font_size=FONT_STEP, color=STEP_COLOR)
            .next_to(lenses[2], DOWN, buff=0.2),
            Tex("atoms", font_size=FONT_STEP, color=STEP_COLOR).next_to(plane, DOWN, buff=0.2),
        )
        beam = always_redraw(steered)
        atom = make_atom().add_updater(
            lambda m: m.move_to([OT_PLANE_X, OT_AXIS + focus_height(slope.get_value()), 0]))
        title = heading("From the SLM to the atoms").move_to(HOLO_HEADING, aligned_edge=UL)

        self.add(slope)
        self.play(FadeIn(title), FadeIn(slm), FadeIn(lenses), FadeIn(plane), FadeIn(names))
        self.play(FadeIn(incoming), FadeIn(beam), FadeIn(atom))
        self.wait(HOLO_SETTLE)
        self.beat()

        # the mask, face on above the SLM, and the focal plane above the foci:
        # the grating's periods and the spot's place follow the slope drawn
        def periods():
            return OT_PERIODS_PER_SLOPE * slope.get_value()

        def grating():
            return grating_phase(x, y, 0, -periods())

        mask = PhaseMask(grating(), amplitude).set(height=OT_PICTURE)
        mask.move_to([OT_SLM_X + 0.9, OT_PICTURE_Y, 0])
        focal = FocalImage(focal_view(grating(), amplitude), FOCAL_SPOT_COLOR, gamma=HG_GAMMA)
        focal.set(height=OT_PICTURE).move_to([OT_PLANE_X + 0.9, OT_PICTURE_Y, 0])
        frame = framed(focal)
        leaders = VGroup(
            DashedLine(slm.get_top(), mask.get_bottom(), **GUIDE_STYLE),
            DashedLine(plane.get_top(), focal.get_bottom(), **GUIDE_STYLE),
        )
        labels = VGroup(panel_label("mask", mask), panel_label("focal plane", focal))
        self.play(FadeIn(mask), FadeIn(focal), FadeIn(frame), Create(leaders), FadeIn(labels))
        mask.add_updater(lambda m: m.paint(grating()))
        focal.add_updater(lambda m: m.paint(focal_view(grating(), amplitude)))
        self.play(slope.animate.set_value(OT_SLOPE), run_time=OT_STEER_TIME)
        self.play(slope.animate.set_value(-OT_SLOPE), run_time=2 * OT_STEER_TIME)
        self.wait(HOLO_SETTLE)
        self.beat()

        # an array: the mask sends a beam to every focus at once
        self.play(slope.animate.set_value(0), run_time=OT_STEER_TIME)
        mask.clear_updaters()
        focal.clear_updaters()
        slopes = np.linspace(-OT_SLOPE, OT_SLOPE, 5)
        spots = np.array([[0.0, -OT_PERIODS_PER_SLOPE * s] for s in slopes])
        array_mask = iterate_hologram(x, y, amplitude, spots, 20)[0][-1]
        fan = VGroup(*[beamlet(OT_BEAM, s, OT_SLM_X, OT_LENSES, OT_PLANE_X, OT_AXIS,
                               OT_OPACITY / 2) for s in slopes])
        atoms = VGroup(*[make_atom().move_to([OT_PLANE_X, OT_AXIS + focus_height(s), 0])
                         for s in slopes])
        atom.clear_updaters()
        mask.paint(array_mask)
        focal.paint(focal_view(array_mask, amplitude) * len(spots))
        self.play(FadeOut(beam), FadeOut(atom), FadeIn(fan), FadeIn(atoms))
        self.wait(HOLO_SETTLE)
        self.beat()

        link = CurvedArrow(mask.get_top() + UP * 0.45, focal.get_top() + UP * 0.45, angle=-0.35,
                           color=lighten(GUIDE_COLOR), stroke_width=3, tip_length=0.2)
        law = Tex("the focal plane is the Fourier transform of the SLM plane",
                  font_size=FONT_STEP).next_to(link, UP, buff=0.1)
        self.play(Create(link), FadeIn(law))
        self.wait(HOLO_SETTLE)
        self.beat()
```

- [ ] **Step 2: Dry-run**

Run: `uv run manim -ql --dry_run src/manim_atoms/tweezers/scenes/holography.py OpticalTrain`
Expected: `Played 12 animations`.

- [ ] **Step 3: Render and read a frame at every stop**

Run the frame check for `holography` / `OpticalTrain`. Add a frame at each extreme of the steering.

| Stop | Must be true |
|---|---|
| 1 bare train | the beam arrives at the SLM from above, leaves along the axis, comes to a focus between the relay lenses, is parallel again after the second, and comes to a point on the dashed focal plane, where the atom sits; four names, each under its part |
| steered | the beam leaves the SLM at an angle and still passes through the middle of the objective; the focus and the atom have moved along the focal plane; in the face-on pictures the mask is striped and the spot has moved the same way as the atom |
| 2 after steering | as above at the other extreme |
| 3 array | five beams fanning from the SLM, crossing at the objective, five foci each with an atom; the mask busy; five spots in a column in the focal-plane picture |
| 4 label | the sentence fits on one line and clears the heading |

Three things to check that code cannot show:
- **Direction.** If the atom moves up while the spot in the picture moves down, change the sign in `grating()` (`-periods()` to `periods()`), and the sign in `spots` to match.
- **Scale.** If the five spots in the picture do not span about the same share of their frame as the five foci span of the focal plane, change `OT_PERIODS_PER_SLOPE`.
- **The incoming beam.** It must not cross the first relay lens. If it does, steepen `OT_INCOMING`.

The spec called for a shallow fold at the SLM. A shallow fold would put the incoming beam through the first relay lens at this size, so it is drawn steep; say so in the scene's docstring if it stays that way.

- [ ] **Step 4: Index it**

Add to "Worked examples by pattern" in `docs/index.md`:

```markdown
- **An optical train side on, with light traced through its lenses** and face-on pictures above it. `tweezers.scenes.holography`: `OpticalTrain`.
```

Run: `python scripts/index.py --write && python scripts/index.py`

- [ ] **Step 5: Commit and push**

```bash
git add src/manim_atoms/tweezers/scenes/holography.py docs/index.md docs/reference.md
git commit -m "tweezers: OpticalTrain, from the SLM to the atoms"
git push
```

---

### Task 12 (bridge): `RearrangementHologram`

**Files:**
- Create: `src/manim_atoms/tweezers/scenes/rearrangement_hologram.py`
- Modify: `docs/index.md`, `docs/reference.md` (generated)

**Interfaces:**
- Consumes: `TweezerArray` and its helpers (Task 4); `spots_from_sites`, `panel_label`, `HG_N`, `HG_SEED` (Task 8); `spot_phase`, `pupil_grid`, `illumination` (Task 2); `PhaseMask`, `phase_wheel` (Task 7); the rearrangement functions (Task 1).
- Produces: `RearrangementHologram`.

- [ ] **Step 1: Write the scene**

`src/manim_atoms/tweezers/scenes/rearrangement_hologram.py`:

```python
"""The hologram behind a rearrangement: the SLM's mask beside the array it
makes, repainted as the traps move.

TweezerRearrangement shows the traps sliding; this shows what is changed to
slide them. The mask on the left is the phase of the sum of every lit
trap's field. Switching a trap off takes its term out of the sum, and
moving a trap changes its term's grating, so the whole mask shifts a little
with every step of the move.

Each trap keeps one phase throughout, which is why the mask changes
smoothly. It is a plain sum, not the weighted Gerchberg-Saxton mask an
experiment would display (HologramIteration), so the traps it would make
are not quite evenly bright; the array on the right is drawn from the trap
positions, not computed from the mask.

- RearrangementHologram: a beat() on the loaded array and its mask, after
  the switching off, and after the move.
"""

import numpy as np
from manim import *

from manim_atoms.tweezers.style import *
from manim_atoms.core.holography import illumination, pupil_grid, spot_phase
from manim_atoms.core.optics import PhaseMask, phase_wheel
from manim_atoms.core.primitives import fluoresce
from manim_atoms.core.projection import TiltedView
from manim_atoms.tweezers.physics.rearrangement import (
    load_sites,
    longest_move,
    plan_rearrangement,
    square_sites,
)
from manim_atoms.tweezers.tools.holograms import HG_N, HG_SEED, panel_label, spots_from_sites
from manim_atoms.tweezers.tools.tweezer_array import (
    TW_COLS,
    TW_FILL,
    TW_PITCH,
    TW_ROWS,
    TW_SEED,
    TW_TARGET,
    TweezerArray,
    heading,
    next_step,
    step_caption,
)

# --- hologram-and-array geometry ---------------------------------------------
# The mask on the left, the array on the right, the same height.
RH_MASK = np.array([-3.6, -0.6, 0.0])
RH_ARRAY = np.array([3.4, -0.6, 0.0])
RH_SIZE = 4.6  # the mask's height
RH_SCALE = 1.05  # scene units per unit of the array's own
RH_HEADING = np.array([-6.6, 3.6, 0.0])
RH_OFF_TIME = 1.2
RH_SETTLE = 0.6


class RearrangementHologram(Scene):
    """The SLM's mask beside the array, repainted every frame as the unwanted
    traps go out and the rest move. A beat() on the loaded array, after the
    switching off and after the move."""

    def beat(self):
        """The pause after each step: nothing here, a click on the slide version."""

    def construct(self):
        sites = square_sites(TW_ROWS, TW_COLS, TW_PITCH)
        targets = square_sites(*TW_TARGET, TW_PITCH)
        loaded = load_sites(len(sites), TW_FILL, np.random.default_rng(TW_SEED))
        plan = plan_rearrangement(sites, loaded, targets)
        array = TweezerArray(sites, TiltedView(RH_ARRAY, RH_SCALE)).load(loaded)
        array.on.set_value(1)
        array.filled.set_value(1)
        array.redraw()

        x, y, rho, _ = pupil_grid(HG_N)
        amplitude = illumination(rho)
        phases = np.random.default_rng(HG_SEED).uniform(0, TAU, len(sites))

        def hologram():
            return spot_phase(x, y, spots_from_sites(array.trap_positions(), TW_PITCH),
                              phases, array.trap_powers())

        mask = PhaseMask(hologram(), amplitude).set(height=RH_SIZE).move_to(RH_MASK)
        mask.add_updater(lambda m: m.paint(hologram()))
        wheel = phase_wheel(0.4).next_to(mask, DL, buff=-0.3)
        mask_label = panel_label("SLM: phase", mask)
        array_label = Tex("focal plane", font_size=FONT_STEP, color=STEP_COLOR)
        array_label.move_to([RH_ARRAY[0], mask_label.get_y(), 0])
        labels = VGroup(mask_label, array_label)
        title = heading("Rearranging by updating the hologram").move_to(RH_HEADING, aligned_edge=UL)
        note = step_caption("one grating per trap, summed", title)

        self.add(*array.trackers, array, mask, wheel, labels, title, note)
        self.wait(RH_SETTLE)
        self.beat()

        fluoresce(self, array.atoms)
        array.rearrange(plan)
        note, swap = next_step(note, "a trap switched off leaves the sum", title)
        self.play(swap, array.off.animate(run_time=RH_OFF_TIME).set_value(1),
                  array.ringed.animate(run_time=RH_OFF_TIME).set_value(1))
        self.wait(RH_SETTLE)
        self.beat()

        note, swap = next_step(note, "a trap moved changes its grating", title)
        self.play(swap)
        self.play(array.moved.animate.set_value(1),
                  run_time=longest_move(plan) * RH_SCALE / TWEEZER_SPEED * 2)
        self.play(array.ringed.animate.set_value(0), run_time=0.4)
        self.wait(RH_SETTLE)
        self.beat()
```

- [ ] **Step 2: Dry-run**

Run: `uv run manim -ql --dry_run src/manim_atoms/tweezers/scenes/rearrangement_hologram.py RearrangementHologram`
Expected: `Played 9 animations`.

- [ ] **Step 3: Render and read a frame at every stop**

Run the frame check for `rearrangement_hologram` / `RearrangementHologram`. Add two frames a third and two thirds of the way through the move.

| Stop | Must be true |
|---|---|
| 1 loaded | the mask on the left, the loaded array on the right, the same height; both labelled on one line |
| 2 off | 25 traps; the mask visibly different from stop 1 |
| during the move | the mask differs between the two frames, and from stops 2 and 3 |
| 3 moved | the block; the mask more regular than at stop 1 |

The move runs at half the top-down scene's speed so the mask's change can be followed. If the mask seems to flicker rather than flow, check `phases` is made once, outside `hologram()`.

- [ ] **Step 4: Index it**

Add to "Worked examples by pattern" in `docs/index.md`:

```markdown
- **Two views of one thing kept in step** (the SLM's mask and the array it makes). `tweezers.scenes.rearrangement_hologram`: `RearrangementHologram`.
```

Run: `python scripts/index.py --write && python scripts/index.py`

- [ ] **Step 5: Commit and push**

```bash
git add src/manim_atoms/tweezers/scenes/rearrangement_hologram.py docs/index.md docs/reference.md
git commit -m "tweezers: RearrangementHologram, the mask beside the array as it moves"
git push
```

---

### Task 13: Documentation, the family skill, and the final checks

**Files:**
- Modify: `CLAUDE.md`, `README.md`
- Create: `.claude/skills/tweezer-scenes/SKILL.md`
- Modify: `.claude/skills/manim-atoms/SKILL.md` (the family table)
- Modify: `docs/superpowers/specs/2026-10-07-tweezer-arrays-design.md` (status)

- [ ] **Step 1: `CLAUDE.md`**

Make these replacements.

In the opening paragraph, `laser cooling and trapping, AION's science` becomes `laser cooling and trapping, optical tweezer arrays made with an SLM, AION's science`.

The layer sentence becomes:

```markdown
Topics depend one way only, `core` → `species` → {`interferometry`, `trapping`, `tweezers`} → `aion`; `slides` depends on `core` alone. Never import upward or sideways: `interferometry`, `trapping` and `tweezers` don't know each other, and nothing outside `aion` imports it.
```

The `core/` bullet becomes:

```markdown
- `core/` — building blocks: `primitives` (atoms, absorb/emit, recoil, legs, kets and the state legend), `spacetime` (worldlines on one lab clock), `bloch` (the Bloch sphere, spin noise), `optics` (Gaussian beams, cavities, phase-mask and focal-plane pictures, a lens, an SLM), `holography` (numbers, no manim: Zernike modes, masks, the focal plane, Gerchberg–Saxton), `projection` (a plane seen from an angle), `plots` (log-log axes, fast scatters), `layout` (static-slide furniture), `citations`, `video`.
```

In the topics bullet, `` `interferometry/`, `trapping/`, `aion/` — each has `` becomes `` `interferometry/`, `trapping/`, `tweezers/`, `aion/` — each has ``, and this sub-bullet is added under it:

```markdown
  - `tweezers/` is an array drawn from its trackers: `tools/tweezer_array.py` has `TweezerArray`, which redraws every frame through a `core.projection.TiltedView`, so a scene drives its trackers and never fades or transforms it. The same array is the top-down picture (`spot_trap`) or the tilted one (`tools/beams.py`'s `hourglass_trap`). Every focal plane in the hologram scenes is computed from the mask shown beside it.
```

In the skills bullet, `` `aion-scenes`, `data-plots` or `slides` `` becomes `` `tweezer-scenes`, `aion-scenes`, `data-plots` or `slides` ``.

- [ ] **Step 2: `README.md`**

After the `manim_atoms.trapping` row of the table, add:

```markdown
| `manim_atoms.tweezers` | Optical tweezer arrays made with an SLM: an array loaded, imaged and rearranged, from above and from an angle; the optical train, phase masks, hologram iteration and Zernike aberration correction |
```

- [ ] **Step 3: The family skill**

`.claude/skills/tweezer-scenes/SKILL.md`:

````markdown
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
use it.

**Top-down and tilted are one array in two views.** The view is a
`TiltedView`; the trap drawing is `spot_trap` or `hourglass_trap`. An
elevation of `PI / 2` is the top-down picture exactly.

**Traps move at `TWEEZER_SPEED`**: a move's `run_time` is
`longest_move(plan) * scale / TWEEZER_SPEED`.

**Every focal plane is computed from the mask beside it.** Paint a
`FocalImage` from `focal_view(mask, amplitude)`; never draw spots by hand.

**Phase is coloured round a wheel** that wraps, so a 2π step shows no
edge. Put a `phase_wheel` on any scene that shows a mask.

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
in an odd array does not, and is still safe.

### 2. The same array from an angle

Worked example: `TweezerArray3D`.

```python
from manim_atoms.tweezers.tools.beams import (
    TW_AZIMUTH, TW_ELEVATION, focal_plane, hourglass_trap)

elevation, azimuth, shown = ValueTracker(PI / 2), ValueTracker(0), ValueTracker(0)
view = TiltedView(CENTER, SCALE, elevation, azimuth)
array = TweezerArray(sites, view, draw_trap=hourglass_trap)
plane = focal_plane(view, HALF, HALF, shown)
self.add(elevation, azimuth, shown, *array.trackers, plane, array)
self.play(elevation.animate.set_value(TW_ELEVATION),
          azimuth.animate.set_value(TW_AZIMUTH), shown.animate.set_value(1))
```

There is no perspective and no lighting: it is a projection on a flat scene.

### 3. A mask beside the focal plane it makes

Worked example: `PhaseMaskBuildingBlocks`.

```python
from manim_atoms.core.holography import grating_phase, illumination, pupil_grid
from manim_atoms.core.optics import FocalImage, PhaseMask
from manim_atoms.tweezers.tools.holograms import HG_GAMMA, HG_N, focal_view

x, y, rho, _ = pupil_grid(HG_N)
amplitude = illumination(rho)
periods = ValueTracker(0)
phase = lambda: grating_phase(x, y, periods.get_value(), 0)
mask = PhaseMask(phase(), amplitude).set(height=4).move_to(LEFT * 3.4)
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
the last is 0.99 by forty steps. A wavefront error is a sum of
`zernike(n, m, rho, theta)` times an rms in radians; its Strehl ratio is
`strehl(error, amplitude)`; what the focal plane shows is
`focal_view(mask + error, amplitude)`. Worked examples:
`HologramIteration`, `ZernikeCorrection`.

## Before you finish

- At every stop, the caption says what the frame shows.
- Top-down: neighbouring spots do not merge, and an atom is told apart
  from its spot by sampling, not by eye.
- Tilted: each beam fades to the background at both ends, and neighbours
  are separate once the empty traps are off.
- A loop's first and last frames are the same picture.
- A focal-plane picture and what it is a picture of move the same way.
````

Every recipe above is cut from a scene rendered and checked in Tasks 5, 6 and 8. Before committing, paste each recipe's code into a scratch scene with its imports and placeholder constants filled in, render it at `-ql -s`, and read the frame.

In `.claude/skills/manim-atoms/SKILL.md`, add a row to the family table after the trapping row:

```markdown
| a tweezer array, phase masks and holograms, Zernike aberration correction, an SLM's optical train | `tweezer-scenes` |
```

- [ ] **Step 4: The whole-branch checks**

```bash
S=.claude/skills/verify-refactor/scripts
uv run pytest -q
python -m compileall -q src
uv run --with pyflakes python $S/undefined_names.py
python scripts/index.py
$S/dry_run.sh 'tweezers'
grep -rnE "from manim_atoms\.(trapping|interferometry|aion)" src/manim_atoms/tweezers
grep -rn "manim_atoms.tweezers" src/manim_atoms --include=*.py -l | grep -v "src/manim_atoms/tweezers/"
```
Expected, in order: every test passes; no output; no name in a `tweezers` or `core` module reported undefined or unused, and the `undefined:` count no higher than it is on `main` (run it there first: without the `slides` extra installed it reports the two `slides` modules); up to date; no `FAIL` line; the two greps print nothing.

- [ ] **Step 5: Prove nothing else changed on screen**

```bash
git stash list   # must be empty: the comparison needs a clean tree
git worktree add /tmp/before_tweezers main
(cd /tmp/before_tweezers && uv sync --all-extras -q && .claude/skills/verify-refactor/scripts/last_frames.sh /tmp/all_before)
.claude/skills/verify-refactor/scripts/last_frames.sh /tmp/all_after
uv run python .claude/skills/verify-refactor/scripts/compare_frames.py /tmp/all_before /tmp/all_after
git worktree remove /tmp/before_tweezers
```
Expected: every scene that exists on `main` is pixel-identical. This takes about twenty minutes; run the two renders in the background.

- [ ] **Step 6: Final renders**

```bash
for s in TweezerRearrangement TweezerRearrangementLoop; do
  uv run manim -qh src/manim_atoms/tweezers/scenes/rearrangement.py $s; done
for s in TweezerArray3D TweezerArray3DLoop; do
  uv run manim -qh src/manim_atoms/tweezers/scenes/array_3d.py $s; done
for s in OpticalTrain PhaseMaskBuildingBlocks HologramIteration ZernikeCorrection; do
  uv run manim -qh src/manim_atoms/tweezers/scenes/holography.py $s; done
uv run manim -qh src/manim_atoms/tweezers/scenes/rearrangement_hologram.py RearrangementHologram
```
Read the final frame of each at full size: a thin stroke or a faint beam that read at 480p can vanish or band at 1080p.

- [ ] **Step 7: Mark the spec done, commit and push**

In the spec, change the status line's `approved; plan in` to `implemented; plan in`.

```bash
git add CLAUDE.md README.md .claude/skills/tweezer-scenes/SKILL.md .claude/skills/manim-atoms/SKILL.md \
        docs/superpowers/specs/2026-10-07-tweezer-arrays-design.md
git commit -m "tweezers: CLAUDE.md, README and the tweezer-scenes skill"
git push
```
