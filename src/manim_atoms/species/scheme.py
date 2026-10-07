"""A species as data, and the level diagram drawn from it.

A Species is what a figure needs to know about an atom: its levels, the
transitions an experiment drives between them, the paths an atom takes
back (repumps, decays), and which transition does which job -- the broad
line that catches atoms, the narrow one that cools them, the clock line,
and so on. Tools and scenes ask a species for a transition by its role
(``species.transition("narrow")``) rather than naming a wavelength, so the
same scene drawn for another atom is a different Species, not new code.

- Level, Manifold: a level, or a fine-structure stack of them (3P_J), drawn
  as horizontal lines with their term beside them.
- Transition: a driven line, an arrow labelled with its wavelength and
  linewidth.
- Path: a repump or a decay, as straight legs; a decay is dashed.
- Extra: levels and paths drawn only when a figure asks for them (a repump
  loop, a transparency beam).
- Species: all of it, with the roles.
- LevelScheme: the diagram, each transition and path drawn twice, idle in
  grey and active in its colour, with ``drive(*keys)`` lighting the ones a
  stage runs.

A species' colours and diagram layout are its own data, in its own module
(species.strontium, species.ytterbium).
"""

from dataclasses import dataclass, field
from fractions import Fraction

import numpy as np
from manim import *

from manim_atoms.style import *


@dataclass(frozen=True)
class Level:
    """One level: its term (TeX), height and horizontal extent on the
    diagram, colour, and where its term goes (side and gap)."""

    term: str
    y: float
    xs: tuple
    color: object = OPTIC_COLOR
    name_side: object = field(default_factory=lambda: DOWN)
    name_buff: float = 0.2


@dataclass(frozen=True)
class Manifold:
    """A fine-structure stack (3P_J): one level per J at ``ys[J]``, sharing
    ``xs``, each labelled with its J. ``colors`` overrides a J's colour
    (default OPTIC_COLOR); the term goes at ``name_side``, or at
    ``name_side_with[extra]`` = (side, buff) while that Extra is drawn."""

    term: str
    ys: dict
    xs: tuple
    colors: dict = field(default_factory=dict)
    name_side: object = field(default_factory=lambda: UP)
    name_buff: float = 0.2
    name_side_with: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Transition:
    """A driven line: an arrow from ``start`` to ``end`` (diagram
    coordinates), double-headed if ``double``, labelled at ``side`` with its
    wavelength (``key``, in nm) and natural linewidth (TeX). ``lower`` and
    ``upper`` are its levels' keys, ``upper_j`` the J in a Manifold.
    ``fan_at`` is where the sawtooth goes when the line is swept (SweepFan)."""

    key: str
    lower: str
    upper: str
    color: object
    start: tuple
    end: tuple
    side: object
    linewidth: str
    double: bool = False
    label_buff: float = 0.3
    upper_j: int | None = None
    fan_at: tuple | None = None


@dataclass(frozen=True)
class Path:
    """A repump or a decay, as a list of straight legs (pairs of points). A
    decay is dashed: the atom's doing, not a beam's. A label, if any, goes
    at ``label_at``, aligned by ``align``."""

    legs: list
    color: object
    decay: bool = False
    label: str | None = None
    label_at: tuple | None = None
    align: object = field(default_factory=lambda: RIGHT)


@dataclass(frozen=True)
class Extra:
    """Levels and paths drawn only when a figure asks for them by name."""

    levels: dict
    paths: dict


@dataclass(frozen=True)
class Species:
    """An atom as a figure needs it.

    ``levels`` maps keys to Level or Manifold, ground state first;
    ``transitions`` maps keys (the wavelength, as printed) to Transition;
    ``extras`` maps names to Extra; ``roles`` maps a job ("cooling",
    "narrow", "clock", "push", "imaging", "transparency") to a transition
    key, and "repump" to a tuple of path keys. ``spin`` is the ground
    state's total angular momentum F in ``isotope``, the one spin-polarised.
    """

    name: str
    symbol: str
    isotope: str
    levels: dict
    transitions: dict
    extras: dict = field(default_factory=dict)
    roles: dict = field(default_factory=dict)
    spin: Fraction = Fraction(0)

    @property
    def ground(self):
        """The ground level."""
        return next(iter(self.levels.values()))

    def transition(self, role):
        """The transition that does ``role``."""
        return self.transitions[self.roles[role]]

    def path(self, role):
        """The repump or decay path that does ``role``, or the path ``role``
        names, wherever its Extra is."""
        key = self.roles.get(role, role)
        return next(extra.paths[key] for extra in self.extras.values() if key in extra.paths)

    def level_y(self, key, j=None):
        """A level's height, or a J's in a Manifold."""
        level = self.levels[key]
        return level.ys[j] if isinstance(level, Manifold) else level.y

    def upper_term(self, key):
        """A transition's upper term, with its J if it ends in a Manifold:
        {}^3P_J and J = 1 give {}^3P_1."""
        spec = self.transitions[key]
        term = self.levels[spec.upper].term
        return term if spec.upper_j is None else term.replace("_J", f"_{spec.upper_j}")


def _level(y, xs, color):
    """A level as a horizontal line."""
    return Line([xs[0], y, 0], [xs[1], y, 0], stroke_width=LEVEL_STROKE_WIDTH,
                color=color)


def transition_arrow(spec, color, width):
    """A transition's arrow and its label, the wavelength over the
    linewidth, in ``color`` at stroke ``width``."""
    cls = DoubleArrow if spec.double else Arrow
    arrow = cls(
        [*spec.start, 0], [*spec.end, 0], buff=0, color=color,
        stroke_width=width, tip_length=0.22, max_tip_length_to_length_ratio=0.12,
        max_stroke_width_to_length_ratio=20,
    )
    label = VGroup(
        Tex(f"{spec.key} nm", font_size=FONT_LEGEND, color=color),
        MathTex(spec.linewidth, font_size=FONT_LINEWIDTH, color=color),
    ).arrange(DOWN, buff=0.1, aligned_edge=-spec.side)
    label.next_to(arrow.get_center(), spec.side, buff=spec.label_buff)
    return VGroup(arrow, label)


def path_arrows(spec, color, width):
    """A repump's arrows, or a spontaneous decay drawn dashed along its
    path, with its label if it has one."""
    group = VGroup()
    for a, b in spec.legs:
        a, b = np.array([*a, 0.0]), np.array([*b, 0.0])
        if spec.decay:
            leg = DashedLine(a, b, dash_length=0.1, color=color, stroke_width=width)
            leg.add_tip(tip_length=0.2, tip_width=0.18)
        else:
            leg = Arrow(a, b, buff=0, color=color, stroke_width=width,
                        tip_length=0.22, max_tip_length_to_length_ratio=0.12,
                        max_stroke_width_to_length_ratio=20)
        group.add(leg)
    if spec.label:
        group.add(Tex(spec.label, font_size=FONT_LEGEND, color=color)
                  .move_to([*spec.label_at, 0], aligned_edge=spec.align))
    return group


class LevelScheme(VGroup):
    """A species' level diagram, with ``extras`` (names of its Extras) drawn
    too.

    The levels come first, ground state first, then their terms and the J
    labels; then each Extra's levels and terms. Every transition and path is
    drawn twice: once in the construction grey, always there, and once over
    it in its own colour and heavier, shown only while a stage is driving it
    (``drive``). ``idle`` and ``active`` map their keys to those drawings.
    """

    def __init__(self, species, extras=(), **kwargs):
        super().__init__(**kwargs)
        self.species = species
        drawn, names, j_labels = [], [], []
        for level in species.levels.values():
            if isinstance(level, Manifold):
                stack = VGroup(*[
                    _level(y, level.xs, level.colors.get(j, OPTIC_COLOR))
                    for j, y in level.ys.items()
                ])
                side, buff = (level.name_side, level.name_buff)
                for extra in extras:
                    side, buff = level.name_side_with.get(extra, (side, buff))
                names.append(MathTex(level.term, font_size=FONT_STATE, color=OPTIC_COLOR)
                             .next_to(stack, side, buff=buff))
                j_labels += [
                    MathTex(str(j), font_size=FONT_LEGEND,
                            color=level.colors.get(j, OPTIC_COLOR))
                    .next_to(line, RIGHT, buff=0.15)
                    for j, line in zip(level.ys, stack)
                ]
                drawn.append(stack)
            else:
                line = _level(level.y, level.xs, level.color)
                names.append(MathTex(level.term, font_size=FONT_STATE, color=level.color)
                             .next_to(line, level.name_side, buff=level.name_buff))
                drawn.append(line)
        self.idle = {k: transition_arrow(spec, TRANSITION_IDLE_STYLE["color"],
                                         TRANSITION_IDLE_STYLE["stroke_width"])
                     for k, spec in species.transitions.items()}
        self.active = {k: transition_arrow(spec, spec.color, TRANSITION_ACTIVE_WIDTH)
                       .set_opacity(0)
                       for k, spec in species.transitions.items()}
        self.add(*drawn, VGroup(*names), VGroup(*j_labels))
        for name in extras:
            extra = species.extras[name]
            lines = [_level(level.y, level.xs, level.color) for level in extra.levels.values()]
            self.add(*lines, *[
                MathTex(level.term, font_size=FONT_STATE, color=level.color)
                .next_to(line, level.name_side, buff=level.name_buff)
                for level, line in zip(extra.levels.values(), lines)
            ])
            for k, spec in extra.paths.items():
                self.idle[k] = path_arrows(spec, TRANSITION_IDLE_STYLE["color"],
                                           TRANSITION_IDLE_STYLE["stroke_width"])
                self.active[k] = path_arrows(spec, spec.color,
                                             TRANSITION_ACTIVE_WIDTH).set_opacity(0)
        self.add(*self.idle.values(), *self.active.values())

    def drive(self, *keys):
        """Animations lighting the transitions and paths ``keys`` and putting
        out the rest."""
        return [group.animate.set_opacity(1 if k in keys else 0)
                for k, group in self.active.items()]
