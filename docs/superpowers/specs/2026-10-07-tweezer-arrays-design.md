# Tweezer arrays and SLM light delivery: design

Date: 2026-10-07. Status: awaiting review.

## What this adds

Animations of an optical tweezer array made with a spatial light modulator
(SLM), for an experiment that rearranges atoms by updating the SLM hologram:

- the array seen top-down (2D), atoms as the house discs, moving between
  sites as it is rearranged;
- the same array seen from an angle (3D), each tweezer a translucent
  Gaussian beam that is brightest at the atom and fades away from the focus;
- the light delivery: the optical train, how a phase mask makes spots, how
  the hologram is computed, and aberration correction with Zernike
  polynomials.

They are for talks and for standalone clips. Every scene calls `beat()`
where a presenter would stop and runs straight through as it is; a slide is
`class XSlide(Clicks, X)`. The rearrangement scenes also get a looping
variant.

## Decisions

| Question | Decision |
|---|---|
| How atoms move | The SLM hologram updates: empty traps go out, all loaded traps move at once. No AOD tweezer. |
| 3D method | Orthographic projection drawn on a flat scene, as `BlochView` and the MOT's oblique view are. No `ThreeDScene`. |
| Where it lives | A new top-level topic, `manim_atoms.tweezers`, beside `interferometry` and `trapping`. |
| Phase colours | One cyclic (wrapping) ramp for every phase map: 0 and 2π are the same colour, so a wrap shows no edge. |
| Species | None named. Tweezer light is far-detuned and takes its own pale colour; no level scheme. |

## Layering

`core` → `species` → {`interferometry`, `trapping`, `tweezers`} → `aion`.

`tweezers` imports `core` only. It does not import `trapping`: where it
wants a value trapping also uses (the pale trap-beam colour), it defines
its own constant in `tweezers/style.py`, because the two are the same value
for parallel reasons, not the same thing. Nothing imports `tweezers`.

Generic optics goes in `core` even though only tweezers uses it so far:
Zernike polynomials, phase masks, the Fourier relation between an SLM and a
focal plane, and a tilted view of a plane are not the tweezers' own.

## Files

```
src/manim_atoms/
  style.py                      + the cyclic phase ramp, lens/SLM furniture
  core/holography.py            new: numbers only, no manim
  core/optics.py                + PhaseMask, FocalImage, make_lens, make_slm
  core/projection.py            new: TiltedView
  tweezers/
    __init__.py                 empty
    style.py                    star-imports the core style
    physics/array.py            sites, loading, the rearrangement plan
    tools/array.py              TweezerArray, the trap drawings
    scenes/array.py             TweezerRearrangement, TweezerArray3D, loops
    scenes/holography.py        OpticalTrain, PhaseMaskBuildingBlocks,
                                HologramIteration, ZernikeCorrection
    scenes/rearrangement_hologram.py   RearrangementHologram
tests/test_holography.py
tests/test_tweezer_array.py
```

Also touched: `scripts/index.py` (`LAYERS` gains `tweezers`), `docs/index.md`,
`docs/reference.md` (generated), `CLAUDE.md` (the layer line and layout),
`README.md` (a row for the topic), and a new family skill
`.claude/skills/tweezer-scenes/`.

## Foundation

### `tweezers/physics/array.py` (numbers)

- `square_sites(rows, cols, pitch)`: site positions, centred on the origin.
- `load_sites(n, fill, rng)`: which sites caught an atom, from a seeded
  generator, so a scene is the same every render.
- `plan_rearrangement(sites, loaded, targets)` returns a `Plan`: for each
  kept trap its start and end position, and which loaded traps are dropped
  as surplus. It raises if fewer atoms loaded than there are targets.
- `positions(plan, s)`: every kept trap a share `s` of the way along its
  straight line.

The assignment minimises the summed *squared* distance (scipy's
`linear_sum_assignment`). That choice is what makes moving every trap at
once safe: under it no two traps ever coincide, and two traps that start
and end at least a pitch apart never come closer than pitch/√2. The test
holds the plan to that bound.

### `core/holography.py` (numbers)

All on a square pixel grid over the SLM aperture.

- `pupil_grid(n)`: x, y, ρ, θ, with the unit disc as the aperture.
- `zernike(n, m, rho, theta)`, `noll_index`, `ZERNIKE_NAMES`.
- `grating_phase`, `lens_phase`: the two building blocks.
- `spot_phase(spots, phases)`: the phase of a sum of fields, one per spot.
- `far_field(phase, amplitude, pad)`: focal-plane intensity by FFT.
- `gs_step`, `wgs_step`: one iteration of Gerchberg–Saxton and of the
  weighted version, returning the new mask and each spot's intensity.
- `uniformity(intensities)`, `strehl(phase_error, amplitude)`.

### `core/optics.py` and the core style

- `PhaseMask`: an image repainted from a phase array through the cyclic
  ramp, clipped to the aperture. Built like `PortImage`.
- `FocalImage`: an image repainted from an intensity array, in one colour
  with intensity as alpha.
- `make_lens`, `make_slm`: furniture in `OPTIC_COLOR`.
- `PHASE_COLORS`: the ramp's stops, first equal to last. The stops are
  chosen by rendering and sampling: every one clear of the background, and
  neighbours distinguishable.

### `core/projection.py`

`TiltedView(center, scale, elevation, azimuth)`: an orthographic view of a
world with the array in the x–y plane and the optical axis along z.
`point(v)` is where a world point lands on screen; `depth(v)` orders
things back to front. Elevation and azimuth can be read from trackers, so
the view can tilt and turn. At an elevation of 90° it is the top-down
picture. `BlochView` is left as it is.

### `tweezers/tools/array.py`

`TweezerArray`: the traps and the atoms riding them, drawn through a view.

- Each trap has a position and a power; a beam's opacity is its intensity,
  as in the trapping figures.
- Atoms are `make_atom` discs, imaged with `fluoresce`.
- Traps are painted far to near, each with its atom.
- How a trap is drawn is a function passed in. `spot_trap` is the top-down
  drawing, a `gaussian_spot`. `hourglass_trap` is the tilted one (below).

## Scenes

### 2D: `TweezerRearrangement` (`TweezerRearrangementLoop`)

An 8×8 loading array into a 5×5 target; both are arguments.

1. The array comes on as spots.
2. About half the traps catch an atom.
3. An imaging flash: which traps are full is now known.
4. Empty and surplus traps go out; the target sites are ringed faintly.
5. Every kept trap slides to its target with its atom, at one speed
   constant.
6. A second image shows the block is defect-free.

The loop releases the atoms, resets, and runs again with the next seed.

### 3D: `TweezerArray3D` (`TweezerArray3DLoop`)

1. The loaded array, top-down, as the 2D scene has it.
2. The view tilts. Each spot becomes an hourglass beam, and the focal plane
   is outlined.
3. Image; empty traps go out.
4. The same rearrangement, in the tilted view.

The loop turns the view slowly about the optical axis.

`hourglass_trap` draws the beam's silhouette, half-width
w(z) = w₀√(1 + (z/z_R)²), in nested layers for the transverse Gaussian,
with opacity falling along the axis as the on-axis intensity does,
1/(1 + (z/z_R)²), to nothing at each end. Its drawn height scales with the
cosine of the elevation, over a waist ellipse that is always drawn, so the
beam closes down continuously into the 2D spot as the view comes back to
top-down. The waist and Rayleigh range are exaggerated to be visible.

### Light: `OpticalTrain`

Side on. Laser, SLM (reflective, a shallow fold), relay, objective, foci.

1. A flat mask: one beam, one focus.
2. The mask is shown enlarged beside the SLM. A grating on it deflects the
   beam and the focus moves sideways.
3. An array mask: beamlets fan out to a row of foci, each with an atom.
4. The label: the objective makes the focal plane the Fourier transform of
   the SLM plane.

Angles are exaggerated and the relay is two lenses.

### Light: `PhaseMaskBuildingBlocks`

The mask on the left, its focal plane on the right, computed from it.

1. Flat phase: one spot at the centre.
2. A blazed grating: the spot slides as the period changes, and turns as
   the grating turns.
3. A lens phase: the spot blurs in this plane, and a side-on inset shows
   the waist moving along the axis.
4. Two gratings summed give two spots; many give the array, with uneven
   brightnesses. That unevenness is what the next scene fixes.

### Light: `HologramIteration`

1. The loop: the SLM plane (amplitude fixed by the laser, phase free) and
   the focal plane (amplitude wanted, phase free), joined by a transform
   each way.
2. The starting mask and its uneven spots, with a bar per trap.
3. Three iterations, one step at a time.
4. The run to convergence: the bars level and the uniformity counts up.

### Light: `ZernikeCorrection`

1. The first fifteen modes as a pyramid of phase discs, named.
2. An aberrated wavefront, the sum of a few modes with a bar per
   coefficient, and its smeared focal spot.
3. The correction, one mode per stop: the bar falls to zero and the spot
   sharpens, with the Strehl ratio rising.
4. The correction added to the array's hologram: every spot sharpens.

### Bridge: `RearrangementHologram`

The mask beside the top-down array, repainted every frame as the traps
move. The mask is the sum of each trap's field with the trap phases held
fixed, so it evolves smoothly rather than flickering between unrelated
solutions.

## Order of work

1. **Foundation**: everything under that heading, with its tests, and
   `TweezerArray` drawing `spot_trap`.
2. **Three tracks**, independent of each other once the foundation is in:
   - 2D: `TweezerRearrangement` and its loop;
   - 3D: `hourglass_trap`, `TweezerArray3D` and its loop;
   - light: the `core/optics.py` additions and the four holography scenes.
3. **Bridge**: `RearrangementHologram`, which needs the 2D and light tracks.
4. **Finish**: the index, the reference, `CLAUDE.md`, the README, and the
   `tweezer-scenes` skill, whose recipes are rendered before they go in.

The tracks share two files, `tweezers/style.py` and `docs/index.md`; each
track adds its own section and they are merged by hand.

## Checks

- `uv run pytest`:
  - Zernike modes are orthonormal over the disc;
  - a grating moves the spot by the amount its period predicts;
  - a lens phase lowers the on-axis peak;
  - weighted GS raises the uniformity;
  - the Strehl ratio is 1 for a flat wavefront;
  - a plan conserves atoms, fills every target, and keeps traps at least
    pitch/√2 apart.
- Every scene rendered at `-ql` and a frame read at each stop.
- The scenes that already use `core/optics.py` (`SpinSqueezing`,
  `DipoleTrapLoading`, `VelocitySlicing`, `SignalInjection`) have
  pixel-identical last frames before and after, since the changes there
  are additions.
- `python scripts/index.py` passes.

## Left out

An AOD tweezer; a species and its level scheme; perspective and lighting in
the 3D view; loss during moves and light-assisted collisions in loading;
SLM calibration (lookup table, pixel crosstalk, the zero order); measured
camera data.
