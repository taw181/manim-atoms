"""Manim animations of atomic physics.

- ``manim_atoms.style``: the house style -- colours, type sizes, line styles
  and pacing -- that every figure draws from.
- ``manim_atoms.core``: building blocks every topic draws with: atoms, laser
  pulses, worldlines on a lab clock, Gaussian beams, slide layout, citations,
  video frames.
- ``manim_atoms.species``: level schemes: a generic two-level diagram and
  strontium's levels and lines.
- ``manim_atoms.interferometry``: light-pulse atom interferometry --
  Mach-Zehnder sequences, clock-phase readout, the gradiometer, large
  momentum transfer, phase-shear readout, spin squeezing.
- ``manim_atoms.trapping``: laser cooling and trapping -- the MOT stages,
  dipole traps, velocity slicing, a high-flux source, one shot of an
  experiment.
- ``manim_atoms.aion``: AION's science -- gravitational waves and
  ultralight dark matter through the gradiometer, AEDGE, the km-scale
  detector, and the prototype's signal injection and measured data.
- ``manim_atoms.slides``: any of the scenes as a manim-slides deck (needs the
  ``slides`` extra).

Each topic keeps ``tools/`` (helpers and the geometry they use), ``scenes/``
(Scene classes, rendered by file path) and, where it has numbers or static
figures, ``physics/`` and ``plots/``:

    uv run manim -ql src/manim_atoms/interferometry/scenes/mach_zehnder.py MachZehnder

This file, and every package ``__init__.py``, deliberately imports nothing:
manim loads a scene file by path, under a module name of its own, and anything
imported here would be loaded a second time under the package's name.
"""
