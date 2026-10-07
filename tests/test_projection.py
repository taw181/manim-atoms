"""The tilted view's geometry: top-down it is the plane, edge on it is the
side view, and what is farther back sorts first. Pure numbers."""

import numpy as np
import pytest
from manim import DEGREES, PI, ValueTracker

from manim_atoms.core.projection import TiltedView


def test_looking_straight_down_is_the_plane_itself():
    view = TiltedView([1, 2, 0], scale=2)
    assert np.allclose(view.point([0.5, -1, 7]), [2, 0, 0])
    assert view.squash() == pytest.approx(1) and view.rise() == pytest.approx(0)


def test_edge_on_shows_height_and_hides_depth():
    view = TiltedView([0, 0, 0], elevation=0)
    assert np.allclose(view.point([1, 2, 3]), [1, 3, 0])


def test_a_point_needs_no_z():
    view = TiltedView([0, 0, 0], elevation=30 * DEGREES)
    assert np.allclose(view.point([1, 2]), view.point([1, 2, 0]))
    assert np.allclose(view.point(np.array([1.0, 2.0])), [1, 1, 0])


def test_farther_back_and_lower_down_sort_first():
    view = TiltedView([0, 0, 0], elevation=30 * DEGREES)
    assert view.depth([0, 1, 0]) < view.depth([0, 0, 0]) < view.depth([0, -1, 0])
    assert view.depth([0, 0, -1]) < view.depth([0, 0, 0]) < view.depth([0, 0, 1])


def test_azimuth_turns_the_plane_about_its_axis():
    view = TiltedView([0, 0, 0], elevation=30 * DEGREES, azimuth=PI / 2)
    assert np.allclose(view.point([1, 0, 0]), [0, 0.5, 0])
    assert np.allclose(view.point([0, 0, 1]), [0, np.cos(30 * DEGREES), 0])


def test_angles_are_read_from_trackers_each_time():
    elevation = ValueTracker(PI / 2)
    view = TiltedView([0, 0, 0], elevation=elevation)
    assert np.allclose(view.point([0, 1, 1]), [0, 1, 0])
    elevation.set_value(0)
    assert np.allclose(view.point([0, 1, 1]), [0, 1, 0])
    assert view.rise() == pytest.approx(1)


def test_a_disc_in_the_plane_is_an_ellipse():
    view = TiltedView([0, 0, 0], scale=2, elevation=30 * DEGREES)
    disc = view.disc([1, 0], 0.5)
    assert disc.width == pytest.approx(2) and disc.height == pytest.approx(1)
    assert np.allclose(disc.get_center(), [2, 0, 0])
