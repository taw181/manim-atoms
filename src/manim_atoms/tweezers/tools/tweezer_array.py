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
TW_SPOT_RADIUS = 0.12  # the waist as drawn: a quarter of the spacing, so beams stay apart
TW_ATOM_RADIUS = 0.07  # well inside its trap's spot
TW_RING_RADIUS = 0.17  # a target ring, just outside the spot


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
        """Rebuild the drawing from the trackers: target rings, then the traps,
        far ones first, then the atoms, far ones first, over all the light: a
        beam may hide the beam behind it, never an atom."""
        xy, powers, shown = self.trap_positions(), self.trap_powers(), self.atom_opacities()
        parts, self.atoms = [], []
        ringed = self.ringed.get_value()
        if self.plan is not None and ringed > 1e-3:
            style = {**TARGET_RING_STYLE,
                     "stroke_opacity": TARGET_RING_STYLE["stroke_opacity"] * ringed}
            parts += [self.view.disc(end, TW_RING_RADIUS, **style) for end in self.plan.end]
        far_first = np.argsort([self.view.depth(p) for p in xy], kind="stable")
        parts += [self.draw_trap(self.view, xy[i], powers[i]) for i in far_first
                  if powers[i] > 1e-3]
        for i in far_first:
            if shown[i] > 1e-3:
                atom = make_atom(radius=self.atom_radius * self.view.scale, opacity=shown[i])
                atom[0].set_stroke(opacity=shown[i])
                atom.move_to(self.view.point(xy[i]))
                self.atoms.append(atom)
        parts += self.atoms
        # A scene lists what a play moves when the play begins and paints that
        # list on every frame, so the pieces drawn last time are emptied, not
        # just dropped: left with their points, they would be painted again,
        # frozen, for the rest of the play.
        for piece in self.family_members_with_points():
            piece.points = np.zeros((0, piece.dim))
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
