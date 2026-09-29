"""Manim animations of atom interferometry, AION and the gravitational-wave
sources it looks for.

- ``aionanim.style``: the house style -- colours, type sizes, line styles and
  pacing -- that every figure draws from.
- ``aionanim.physics``: the numbers behind the figures, with no manim in them.
- ``aionanim.tools``: drawing and animation helpers, one module per topic.
- ``aionanim.scenes``: the scenes themselves. Render one by its file path:

      uv run manim -ql src/aionanim/scenes/gradiometer_gw.py GradiometerGW

- ``aionanim.plots``: the same data drawn as static matplotlib figures.

This file deliberately imports nothing: manim loads a scene file by path,
under a module name of its own, and anything imported here would be loaded a
second time under the package's name.
"""
