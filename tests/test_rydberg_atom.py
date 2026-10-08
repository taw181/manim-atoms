"""The Rydberg atom drawing: its orbit is as visible as the atom is excited,
and its animations take the excitation where they say. Builds mobjects but
renders nothing."""

import numpy as np
import pytest
from manim import color_to_rgb

from manim_atoms.core.primitives import RydbergAtom
from manim_atoms.style import ATOM_COLOR, RYDBERG_COLOR, RYDBERG_ORBIT_FILL


def run(animation, alpha):
    """Take an animation ``alpha`` of the way through, without a scene."""
    animation.begin()
    animation.interpolate(alpha)
    return animation.mobject


def test_the_ground_state_shows_no_orbit_and_the_ground_colour():
    atom = RydbergAtom()
    assert atom.orbit.get_fill_opacity() == 0 and atom.orbit.get_stroke_opacity() == 0
    assert np.allclose(color_to_rgb(atom.body.get_fill_color()), color_to_rgb(ATOM_COLOR))


def test_the_orbit_is_as_visible_as_the_atom_is_excited():
    atom = RydbergAtom().set_excitation(0.5)
    assert atom.orbit.get_fill_opacity() == pytest.approx(RYDBERG_ORBIT_FILL / 2)
    atom.set_excitation(1)
    assert atom.orbit.get_fill_opacity() == pytest.approx(RYDBERG_ORBIT_FILL)
    assert np.allclose(color_to_rgb(atom.body.get_fill_color()), color_to_rgb(RYDBERG_COLOR))


def test_the_orbit_is_far_larger_than_the_body_and_centred_on_it():
    atom = RydbergAtom(radius=0.1, orbit_radius=0.5).move_to([1, 2, 0])
    assert atom.orbit.width == pytest.approx(5 * atom.body.width, rel=0.05)
    assert np.allclose(atom.orbit.get_center(), atom.body.get_center())
    assert np.allclose(atom.body.get_center(), [1, 2, 0])


def test_excitation_is_kept_between_nought_and_one():
    assert RydbergAtom().set_excitation(1.3).excitation == 1
    assert RydbergAtom().set_excitation(-0.2).excitation == 0


def test_excite_starts_from_where_the_atom_is_when_it_begins():
    atom = RydbergAtom()
    animation = atom.excite()
    atom.set_excitation(0.5)  # after the animation was made
    assert run(animation, 0.5).excitation == pytest.approx(0.75)
    assert run(atom.excite(), 1).excitation == 1
    assert run(atom.relax(), 1).excitation == 0


def test_a_flop_goes_to_the_rydberg_state_and_back():
    atom = RydbergAtom()
    assert run(atom.flop(), 0.5).excitation == pytest.approx(1)
    assert run(atom.flop(), 1).excitation == pytest.approx(0)
    assert run(atom.flop(cycles=0.5), 1).excitation == pytest.approx(1)
