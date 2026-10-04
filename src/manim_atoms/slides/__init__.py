"""Scenes as manim-slides slides, and decks of them (needs the ``slides`` extra).

The only part of manim_atoms that imports manim_slides. See
manim_atoms.slides.deck for the slide mixins and deck file, and
manim_atoms.slides.cli for ``manim-atoms-deck``.

Import nothing here: manim loads a scene file by path, and anything imported
here would be loaded a second time under the package's name.
"""
