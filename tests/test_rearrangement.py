"""The rearrangement plan against what moving every trap at once demands: no
atom lost or invented, every target filled, and no two traps ever close.
Pure numbers: nothing here renders."""

import numpy as np
import pytest

from manim_atoms.tweezers.physics.rearrangement import (
    load_sites, longest_move, plan_rearrangement, positions, square_sites,
)

PITCH = 0.5
SITES = square_sites(9, 9, PITCH)
TARGETS = square_sites(5, 5, PITCH)


def loaded_for(seed, fill=0.5):
    return load_sites(len(SITES), fill, np.random.default_rng(seed))


def test_sites_are_centred_and_run_from_the_top_left():
    assert np.allclose(SITES.mean(axis=0), 0)
    assert np.allclose(SITES[0], [-4 * PITCH, 4 * PITCH])
    assert np.allclose(SITES[1] - SITES[0], [PITCH, 0])
    assert np.allclose(SITES[9] - SITES[0], [0, -PITCH])


def test_loading_is_repeatable_and_near_the_fill():
    assert np.array_equal(loaded_for(3), loaded_for(3))
    assert 0.4 < np.mean([loaded_for(s).mean() for s in range(200)]) < 0.6


SEEDS = [s for s in range(40) if loaded_for(s).sum() >= len(TARGETS)]


@pytest.mark.parametrize("seed", SEEDS)
def test_plan_fills_every_target_once_and_conserves_atoms(seed):
    loaded = loaded_for(seed)
    plan = plan_rearrangement(SITES, loaded, TARGETS)
    assert len(plan.kept) == len(TARGETS)
    assert sorted(map(tuple, plan.end)) == sorted(map(tuple, TARGETS))
    assert np.allclose(plan.start, SITES[plan.kept])
    assert sorted([*plan.kept, *plan.dropped]) == list(np.flatnonzero(loaded))
    assert np.allclose(positions(plan, 0), plan.start)
    assert np.allclose(positions(plan, 1), plan.end)


@pytest.mark.parametrize("seed", SEEDS)
def test_traps_moved_together_stay_apart(seed):
    plan = plan_rearrangement(SITES, loaded_for(seed), TARGETS)
    closest = np.inf
    for share in np.linspace(0, 1, 201):
        p = positions(plan, share)
        d = np.linalg.norm(p[:, None] - p[None, :], axis=-1)
        closest = min(closest, d[~np.eye(len(p), dtype=bool)].min())
    assert closest >= PITCH / np.sqrt(2) - 1e-9


def test_too_few_atoms_is_an_error():
    loaded = np.zeros(len(SITES), dtype=bool)
    loaded[:10] = True
    with pytest.raises(ValueError, match="10 atoms loaded for 25"):
        plan_rearrangement(SITES, loaded, TARGETS)


def test_a_full_block_already_in_place_does_not_move():
    loaded = np.array([any(np.allclose(s, t) for t in TARGETS) for s in SITES])
    plan = plan_rearrangement(SITES, loaded, TARGETS)
    assert longest_move(plan) == 0 and len(plan.dropped) == 0


def test_no_targets_drops_everything():
    plan = plan_rearrangement(SITES, loaded_for(0), np.empty((0, 2)))
    assert len(plan.kept) == 0 and longest_move(plan) == 0
    assert positions(plan, 0.5).shape == (0, 2)


@pytest.mark.parametrize("shape, block", [((6, 8), (3, 4)), ((4, 4), (3, 3)), ((1, 7), (1, 3))])
def test_any_shape_of_array_and_block_is_safe_even_off_the_lattice(shape, block):
    sites, targets = square_sites(*shape, PITCH), square_sites(*block, PITCH)
    plan = plan_rearrangement(sites, np.ones(len(sites), dtype=bool), targets)
    assert len(plan.kept) == len(targets) and len(plan.dropped) == len(sites) - len(targets)
    for share in np.linspace(0, 1, 101):
        p = positions(plan, share)
        d = np.linalg.norm(p[:, None] - p[None, :], axis=-1)
        if len(p) > 1:
            assert d[~np.eye(len(p), dtype=bool)].min() >= PITCH / np.sqrt(2) - 1e-9
