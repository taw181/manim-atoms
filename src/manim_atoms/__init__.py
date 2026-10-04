"""Manim animations of atom interferometry, AION and the gravitational-wave
sources it looks for.

- ``manim_atoms.style``: the house style -- colours, type sizes, line styles and
  pacing -- that every figure draws from.
- ``manim_atoms.physics``: the numbers behind the figures, with no manim in them.
- ``manim_atoms.tools``: drawing and animation helpers, one module per topic.
- ``manim_atoms.scenes``: the scenes themselves. Render one by its file path:

      uv run manim -ql src/manim_atoms/scenes/gradiometer_gw.py GradiometerGW

- ``manim_atoms.plots``: the same data drawn as static matplotlib figures.

This file deliberately imports nothing: manim loads a scene file by path,
under a module name of its own, and anything imported here would be loaded a
second time under the package's name.
"""
