"""A polar molecule's levels beside a Rydberg atom's: the level scheme of a
gate between two molecules through an atom.

The scheme is Zhang and Tarbutt's (PRX Quantum 3, 030340 (2022)). A molecule
holds a qubit in |0> and |1> and has a third state |2>, an electric dipole
transition above |1>. The atom has a ground state |g> and two Rydberg
states, |R> and above it |r>. An electric field tunes |R> until the atom's
|r> <-> |R> is resonant with the molecule's |1> <-> |2>; the two then
exchange an excitation through the dipole-dipole interaction. A laser
drives |g> <-> |r>, and microwaves the qubit's |0> <-> |1>.

GateLevels draws a molecule either side of the atom, with a disc on every
level whose area is that level's population. It is redrawn from numbers a
scene gives it: tune (how far the field has brought |R>), show (the
populations) and light (which couplings are running). Schematic, not to
scale: the laser's transition is optical, the others microwave.
"""

import numpy as np
from manim import *

from manim_atoms.style import *
from manim_atoms.core.primitives import make_atom, make_molecule, state_label

# --- the states' colours --------------------------------------------------
# The qubit's two states take two hues the atom's leave free. The atom's
# ground state is the house |g>, and its Rydberg state |r> the house
# Rydberg violet. The pair of states the dipole-dipole exchange leads to,
# the molecule's |2> and the atom's |R>, share the exchange's blue with the
# arcs that mark it: they are only ever populated together, and by it.
QUBIT_0_COLOR = ManimColor("#7cc470")
QUBIT_1_COLOR = ManimColor("#e6b450")
EXCHANGE_COLOR = ManimColor("#5b8cff")
# Microwaves on the qubit transition: a single-qubit gate, not this gate's
# business, so near white rather than another hue.
MICROWAVE_COLOR = lighten(GUIDE_COLOR, 0.8)

MOLECULE_COLORS = (QUBIT_0_COLOR, QUBIT_1_COLOR, EXCHANGE_COLOR)  # |0>, |1>, |2>
RYDBERG_ATOM_COLORS = (ATOM_COLOR, EXCHANGE_COLOR, RYDBERG_COLOR)  # |g>, |R>, |r>

# --- the level scheme's geometry ------------------------------------------
# Three columns, a molecule either side of the atom as in the traps. On
# resonance the molecule's |1> and |2> are level with the atom's |R> and
# |r>, which is the resonance drawn. In a molecule's column the population
# discs sit towards the outside, where the kets are, and the dipole arc
# towards the atom; in the atom's the laser's arrow is left of the discs and
# the arc right, with the kets above and below the lines, out of the way of
# the guides that join the columns.
MR_COLUMN = 2.4  # from the atom's column to a molecule's
MR_LEVEL_LENGTH = 1.2
MR_ZERO, MR_ONE, MR_UPPER = -0.75, 0.0, 1.7  # |0>; |1>; |2> and |r>
MR_GROUND = -2.7  # the atom's |g>: an optical transition below, cut short
MR_DETUNED = 0.45  # how far |R> sits above |1> with no field
MR_HEADER = 2.5  # each column's picture and name
MR_MARKER_RADIUS = 0.18  # of a level's disc when all the population is in it
MR_MARKER_EDGE = 0.8  # how far towards white a disc's edge is: it sits on a line of its own colour
MR_MARKER_X = 0.12  # a molecule's discs, out from its column's middle
MR_ARC_X = 0.32  # a dipole arc, in from a molecule's column's middle
MR_LASER_X = -0.38  # the laser's arrow, in the atom's column
MR_ARC_ANGLE = 70 * DEGREES  # how far an arc bows
MR_INSET = 0.08  # how far an arrow stands off each level line
MR_KET_BUFF = 0.18
MR_TUNED_KET_X = 0.2  # |R>'s ket, right of its column's middle: clear of the laser's arrow
MR_EXCHANGE_X = MR_COLUMN / 2 + 0.1  # the V_DD label, between an arc and the atom's column
FONT_COLUMN = FONT_AXIS  # a column's name

ARC_STYLE = dict(tip_length=0.16, stroke_width=3)
ARC_ACTIVE_WIDTH = 5


def _full(group):
    """Note every piece's opacities as built, for _dim to scale."""
    group.full = [(piece, piece.get_stroke_opacity(), piece.get_fill_opacity())
                  for piece in group.family_members_with_points()]
    return group


def _dim(group, share):
    """Show ``group`` at ``share`` of the opacities it was built with. Piece
    by piece, since an arc given a fill opacity would fill in."""
    for piece, stroke, fill in group.full:
        piece.set_stroke(opacity=stroke * share).set_fill(opacity=fill * share)


def _arc(x, low, high, bows, color, width):
    """A dipole transition's arc at ``x`` between two levels, bowing to the
    side ``bows`` (+1 right, -1 left)."""
    return CurvedDoubleArrow([x, low + MR_INSET, 0], [x, high - MR_INSET, 0],
                             angle=bows * MR_ARC_ANGLE, color=color,
                             **{**ARC_STYLE, "stroke_width": width})


class GateLevels(VGroup):
    """A molecule's levels either side of a Rydberg atom's, about ``center``.

    Each level carries a disc whose area is its population. Every coupling
    is drawn twice: once in the construction grey, always there, and once
    over it in its own colour, as bright as light() says. ``guides`` are
    the dashed lines joining the columns' levels on resonance; they are not
    part of the group, so a scene brings them on once tune() has reached 1.
    """

    def __init__(self, center=ORIGIN, **kwargs):
        super().__init__(**kwargs)
        self.center = np.array(center, dtype=float)
        self.unit_circle = Circle(radius=1).points.copy()
        self.tuned = None
        half = MR_LEVEL_LENGTH / 2
        idle = TRANSITION_IDLE_STYLE["color"]

        def line(x, y, color):
            return Line([x - half, y, 0], [x + half, y, 0], color=color,
                        stroke_width=LEVEL_STROKE_WIDTH)

        def marker(color):
            return Circle(radius=MR_MARKER_RADIUS, fill_color=lighten(color),
                          fill_opacity=1, stroke_color=lighten(color, MR_MARKER_EDGE),
                          stroke_width=ATOM_STROKE_WIDTH)

        # the molecules, left (-1) and right (+1)
        fixed, self.markers, self.anchors = VGroup(), [], []
        self.microwave, self.exchange_idle, self.exchange = [], [], []
        heights = (MR_ZERO, MR_ONE, MR_UPPER)
        for side in (-1, 1):
            x = side * MR_COLUMN
            for k, (y, color) in enumerate(zip(heights, MOLECULE_COLORS)):
                level = line(x, y, color)
                fixed.add(level, state_label(rf"|{k}\rangle", color).next_to(
                    level, side * RIGHT, buff=MR_KET_BUFF))
            self.anchors.append([np.array([x + side * MR_MARKER_X, y, 0.0]) for y in heights])
            self.markers.append(VGroup(*[marker(c) for c in MOLECULE_COLORS]))
            arc_x = x - side * MR_ARC_X
            self.exchange_idle.append(_arc(arc_x, MR_ONE, MR_UPPER, -side, idle,
                                           ARC_STYLE["stroke_width"]))
            fixed.add(DoubleArrow([arc_x, MR_ZERO + MR_INSET, 0], [arc_x, MR_ONE - MR_INSET, 0],
                                  **{**LEVEL_GAP_ARROW_STYLE, "stroke_width": 2,
                                     "max_tip_length_to_length_ratio": 0.2}))
            drive = DoubleArrow([arc_x, MR_ZERO + MR_INSET, 0], [arc_x, MR_ONE - MR_INSET, 0],
                                **{**LEVEL_GAP_ARROW_STYLE, "stroke_width": 4,
                                   "color": MICROWAVE_COLOR,
                                   "max_tip_length_to_length_ratio": 0.2})
            name = MathTex(r"\mu\mathrm{w}", font_size=FONT_LEGEND, color=MICROWAVE_COLOR)
            self.microwave.append(_full(VGroup(drive, name.next_to(drive, -side * RIGHT,
                                                                   buff=0.12))))
            label = MathTex(r"V_{\mathrm{DD}}", font_size=FONT_LEGEND, color=EXCHANGE_COLOR)
            label.move_to([side * MR_EXCHANGE_X, (MR_ONE + MR_UPPER) / 2, 0])
            self.exchange.append(_full(VGroup(
                _arc(arc_x, MR_ONE, MR_UPPER, -side, EXCHANGE_COLOR, ARC_ACTIVE_WIDTH), label)))
            fixed.add(self._header(make_molecule(OPTIC_COLOR, radius=LEGEND_ATOM_RADIUS),
                                   "molecule", x))

        # the atom, between them: |g> and |r> stay put, |R> is tuned
        ground, rydberg = line(0, MR_GROUND, ATOM_COLOR), line(0, MR_UPPER, RYDBERG_COLOR)
        fixed.add(ground, rydberg,
                  state_label(r"|g\rangle", ATOM_COLOR).next_to(ground, DOWN, buff=MR_KET_BUFF),
                  state_label(r"|r\rangle", RYDBERG_COLOR).next_to(rydberg, UP,
                                                                    buff=MR_KET_BUFF),
                  self._header(make_atom(OPTIC_COLOR, radius=LEGEND_ATOM_RADIUS), "atom", 0))
        self.tuned_line = line(0, MR_ONE, EXCHANGE_COLOR)
        self.tuned_ket = state_label(r"|R\rangle", EXCHANGE_COLOR)
        self.atom_anchors = [np.array([0.0, y, 0.0]) for y in (MR_GROUND, MR_ONE, MR_UPPER)]
        self.atom_markers = VGroup(*[marker(c) for c in RYDBERG_ATOM_COLORS])
        self.atom_arc_idle = _arc(MR_ARC_X, MR_ONE, MR_UPPER, 1, idle, ARC_STYLE["stroke_width"])
        self.atom_arc = _full(_arc(MR_ARC_X, MR_ONE, MR_UPPER, 1, EXCHANGE_COLOR,
                                   ARC_ACTIVE_WIDTH))

        def laser(style, color):
            arrow = DoubleArrow([MR_LASER_X, MR_GROUND + MR_INSET, 0],
                                [MR_LASER_X, MR_UPPER - MR_INSET, 0],
                                **{**style, "color": color,
                                   "max_tip_length_to_length_ratio": 0.05})
            name = MathTex(r"\Omega_L", font_size=FONT_LEGEND, color=color)
            return VGroup(arrow, name.next_to(arrow, LEFT, buff=0.15).shift(DOWN * 0.9))

        self.laser = _full(laser(LEVEL_GLOW_ARROW_STYLE, LASER_COLOR))
        fixed.add(laser(LEVEL_GAP_ARROW_STYLE, idle))

        self.guides = VGroup(*[
            DashedLine([side * half, y, 0], [side * (MR_COLUMN - half), y, 0], **GUIDE_STYLE)
            for side in (-1, 1) for y in (MR_ONE, MR_UPPER)])

        self.add(fixed, *self.exchange_idle, self.atom_arc_idle, self.tuned_line,
                 self.tuned_ket, *self.microwave, self.laser, *self.exchange, self.atom_arc,
                 *self.markers, self.atom_markers)
        self.shift(self.center)
        self.guides.shift(self.center)
        for anchors in (*self.anchors, self.atom_anchors):
            for anchor in anchors:
                anchor += self.center
        self.tune(0)
        self.show((1, 0, 0), (1, 0, 0), (1, 0, 0))
        self.light()

    def _header(self, picture, name, x):
        """A column's picture and name, over it."""
        return VGroup(picture, Tex(name, font_size=FONT_COLUMN, color=OPTIC_COLOR)).arrange(
            RIGHT, buff=0.15).move_to([x, MR_HEADER, 0])

    def tune(self, share):
        """Put |R> ``share`` of the way from where it sits with no field
        (0) to resonance (1), with its ket, its disc and the atom's arc."""
        if share == self.tuned:
            return self
        self.tuned = share
        y = MR_ONE + MR_DETUNED * (1 - share)
        at = self.center + UP * y
        half = RIGHT * MR_LEVEL_LENGTH / 2
        self.tuned_line.put_start_and_end_on(at - half, at + half)
        self.tuned_ket.next_to(self.tuned_line, DOWN, buff=MR_KET_BUFF).shift(
            RIGHT * MR_TUNED_KET_X)
        self.atom_anchors[1] = at
        for arc, color, width in ((self.atom_arc_idle, TRANSITION_IDLE_STYLE["color"],
                                   ARC_STYLE["stroke_width"]),
                                  (self.atom_arc, EXCHANGE_COLOR, ARC_ACTIVE_WIDTH)):
            arc.become(_arc(MR_ARC_X, y, MR_UPPER, 1, color, width).shift(self.center))
        return self

    def show(self, first, atom, second):
        """Size every level's disc to its population: ``first`` and
        ``second`` are the molecules' in (|0>, |1>, |2>), ``atom`` the
        atom's in (|g>, |R>, |r>)."""
        for markers, anchors, populations in (
                (self.markers[0], self.anchors[0], first),
                (self.atom_markers, self.atom_anchors, atom),
                (self.markers[1], self.anchors[1], second)):
            for disc, anchor, population in zip(markers, anchors, populations):
                radius = MR_MARKER_RADIUS * np.sqrt(max(population, 0.0))
                disc.set_points(anchor + radius * self.unit_circle)
                disc.set_stroke(opacity=float(radius > 1e-3))
        return self

    def light(self, laser=0.0, exchange=(0.0, 0.0), microwave=(0.0, 0.0)):
        """Light the couplings, each from 0 to 1: the ``laser`` on
        |g> <-> |r>, each molecule's ``exchange`` with the atom, and the
        ``microwave`` on each molecule's qubit."""
        _dim(self.laser, laser)
        for group, share in zip(self.exchange, exchange):
            _dim(group, share)
        _dim(self.atom_arc, max(exchange))
        for group, share in zip(self.microwave, microwave):
            _dim(group, share)
        return self
