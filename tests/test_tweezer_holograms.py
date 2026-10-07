"""The hologram scenes' helpers: spots in the hologram's units, the focal
plane's crop, rays through thin lenses, the bar chart, the iteration.
Builds mobjects but renders nothing."""

import numpy as np
import pytest

from manim_atoms.core.holography import illumination, pupil_grid, uniformity
from manim_atoms.tweezers.physics.rearrangement import square_sites
from manim_atoms.tweezers.tools.holograms import (
    HG_N, HG_PAD, HG_VIEW, bar_chart, focal_view, grid_spots, iterate_hologram,
    spots_from_sites, trace_ray,
)


def test_grid_spots_are_centred_and_run_from_the_top_left():
    spots = grid_spots(3, 5, 4)
    assert np.allclose(spots.mean(axis=0), 0)
    assert np.allclose(spots[0], [-8, 4]) and np.allclose(spots[-1], [8, -4])
    assert np.allclose(spots_from_sites(square_sites(3, 5, 0.5), 0.5, 4), spots)


def test_the_focal_view_is_centred_on_the_axis():
    _, _, rho, _ = pupil_grid(HG_N)
    view = focal_view(np.zeros((HG_N, HG_N)), illumination(rho))
    side = 2 * HG_VIEW * HG_PAD + 1
    assert view.shape == (side, side)
    assert np.unravel_index(view.argmax(), view.shape) == (side // 2, side // 2)


def test_a_four_f_relay_images_the_start_onto_the_far_focus_inverted():
    # start a focal length before the first lens; lenses 2f apart; end a focal length after
    points = trace_ray(0.0, 0.1, 0.0, [(2.0, 2.0), (6.0, 2.0)], 8.0)
    assert points[-1] == pytest.approx((8.0, 0.0))
    assert points[2][1] - points[1][1] == pytest.approx(0.0)  # parallel to the axis between
    out = trace_ray(0.3, 0.0, 0.0, [(2.0, 2.0), (6.0, 2.0)], 8.0)
    assert out[-1][1] == pytest.approx(-0.3)


def test_lenses_outside_the_span_are_ignored():
    assert trace_ray(0.2, 0.0, 0.0, [(-1.0, 1.0), (5.0, 1.0)], 4.0) == [(0.0, 0.2), (4.0, 0.2)]


def test_bars_stand_on_the_baseline_and_negative_ones_hang_below():
    baseline, bars = bar_chart([1.0, -0.5, 0.0], full=1.0, width=3.0, height=2.0)
    assert len(bars) == 3 and baseline.width == pytest.approx(3.0)
    assert bars[0].get_bottom()[1] == pytest.approx(0) and bars[0].height == pytest.approx(2.0)
    assert bars[1].get_top()[1] == pytest.approx(0) and bars[1].height == pytest.approx(1.0)


def test_the_iteration_keeps_every_mask_and_ends_evenly_lit():
    x, y, rho, _ = pupil_grid(64)
    masks, intensities = iterate_hologram(x, y, illumination(rho), grid_spots(3, 3), 25)
    assert len(masks) == len(intensities) == 26
    assert uniformity(intensities[-1]) > 0.95 > uniformity(intensities[0])
