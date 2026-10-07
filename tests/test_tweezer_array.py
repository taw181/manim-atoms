"""The array drawing's bookkeeping: which traps are lit, where they are and
which hold an atom, at each setting of its trackers. Builds mobjects but
renders nothing."""

import numpy as np
import pytest
from manim import DEGREES

from manim_atoms.core.projection import TiltedView
from manim_atoms.tweezers.physics.rearrangement import plan_rearrangement, square_sites
from manim_atoms.tweezers.tools.tweezer_array import TweezerArray

SITES = square_sites(3, 3, 1.0)
LOADED = np.array([1, 0, 1, 0, 1, 1, 0, 0, 1], dtype=bool)  # five atoms
TARGETS = square_sites(2, 2, 1.0)


def make(view=None):
    return TweezerArray(SITES, view or TiltedView([0, 0, 0]))


def test_nothing_is_drawn_until_the_traps_come_on():
    array = make()
    assert len(array.submobjects) == 0
    array.on.set_value(1)
    assert len(array.redraw().submobjects) == 9 and array.atoms == []


def test_atoms_appear_only_in_loaded_traps():
    array = make().load(LOADED)
    array.on.set_value(1)
    array.filled.set_value(1)
    array.redraw()
    assert len(array.atoms) == 5
    assert np.allclose(sorted(a.get_center()[:2].tolist() for a in array.atoms),
                       sorted(SITES[LOADED].tolist()))


def test_the_wrong_number_of_loading_flags_is_an_error():
    with pytest.raises(ValueError, match="traps"):
        make().load([True, False])


def test_unkept_traps_go_out_with_their_atoms_and_kept_ones_move():
    array = make().load(LOADED)
    plan = plan_rearrangement(SITES, LOADED, TARGETS)
    array.rearrange(plan)
    array.on.set_value(1)
    array.filled.set_value(1)
    assert np.allclose(array.trap_powers(), 1)
    array.off.set_value(1)
    assert array.trap_powers().sum() == 4 and array.atom_opacities().sum() == 4
    array.moved.set_value(1)
    assert np.allclose(array.trap_positions()[plan.kept], plan.end)
    array.redraw()
    assert len(array.atoms) == 4
    assert np.allclose(sorted(a.get_center()[:2].tolist() for a in array.atoms),
                       sorted(TARGETS.tolist()))


def test_target_rings_show_only_with_a_plan():
    array = make()
    array.ringed.set_value(1)
    assert len(array.redraw().submobjects) == 0
    array.rearrange(plan_rearrangement(SITES, LOADED, TARGETS))
    assert len(array.submobjects) == 4


def test_reset_empties_the_array_and_puts_the_traps_back():
    array = make().load(LOADED)
    array.rearrange(plan_rearrangement(SITES, LOADED, TARGETS))
    for tracker in array.trackers:
        tracker.set_value(1)
    array.reset()
    assert array.on.get_value() == 1 and not array.loaded.any()
    assert np.allclose(array.trap_positions(), SITES) and np.allclose(array.trap_powers(), 1)


def test_far_traps_are_painted_first_in_a_tilted_view():
    array = make(TiltedView([0, 0, 0], elevation=30 * DEGREES))
    array.on.set_value(1)
    array.redraw()
    heights = [trap.get_center()[1] for trap in array.submobjects]
    assert heights == sorted(heights, reverse=True)


def test_a_redraw_leaves_nothing_of_the_last_drawing_behind():
    # A scene lists what an animation moves when it begins, and paints that
    # list on every frame: whatever the array had drawn then and has since
    # replaced would be painted again, frozen, over the new drawing.
    array = make().load(LOADED)
    array.on.set_value(1)
    array.filled.set_value(1)
    array.redraw()
    listed_by_the_scene = array.family_members_with_points()
    assert listed_by_the_scene
    array.rearrange(plan_rearrangement(SITES, LOADED, TARGETS))
    array.moved.set_value(0.5)
    array.redraw()
    current = {id(m) for m in array.get_family()}
    left_behind = [m for m in listed_by_the_scene if id(m) not in current and m.has_points()]
    assert left_behind == []
