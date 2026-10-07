"""The species tables against themselves: every role names something the
species has, every transition joins two of its levels, and the terms a
heading prints come out right. Pure data: nothing here renders."""

import pytest

from manim_atoms.species.scheme import Manifold
from manim_atoms.species.strontium import STRONTIUM

SPECIES = [STRONTIUM]


@pytest.mark.parametrize("species", SPECIES, ids=lambda s: s.symbol)
def test_every_role_names_a_transition_or_a_path(species):
    paths = {k for extra in species.extras.values() for k in extra.paths}
    for role, key in species.roles.items():
        keys = key if isinstance(key, tuple) else (key,)
        for k in keys:
            assert k in species.transitions or k in paths, (role, k)


@pytest.mark.parametrize("species", SPECIES, ids=lambda s: s.symbol)
def test_every_transition_joins_two_of_its_levels(species):
    for key, spec in species.transitions.items():
        assert spec.key == key
        assert spec.lower in species.levels and spec.upper in species.levels
        upper = species.levels[spec.upper]
        if isinstance(upper, Manifold):
            assert spec.upper_j in upper.ys, key
        else:
            assert spec.upper_j is None, key
        # an arrow climbs from its lower level to its upper one
        assert spec.start[1] == species.level_y(spec.lower)
        assert spec.end[1] == species.level_y(spec.upper, spec.upper_j)


@pytest.mark.parametrize("species", SPECIES, ids=lambda s: s.symbol)
def test_the_ground_state_comes_first(species):
    assert species.ground is next(iter(species.levels.values()))
    assert all(spec.lower == next(iter(species.levels)) for spec in species.transitions.values())


def test_strontium_is_strontium():
    assert STRONTIUM.transition("cooling").key == "461"
    assert STRONTIUM.transition("narrow").key == "689"
    assert STRONTIUM.transition("clock").key == "698"
    assert STRONTIUM.upper_term("689") == r"{}^3P_1"
    assert STRONTIUM.upper_term("698") == r"{}^3P_0"
    assert STRONTIUM.upper_term("461") == r"{}^1P_1"
    assert STRONTIUM.spin == 9 / 2
