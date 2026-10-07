"""The holography numbers against the optics: a grating steers the spot by its
periods, a lens blurs it, the Zernike modes are orthonormal, weighted
Gerchberg-Saxton evens an array out. Pure numbers: nothing here renders."""

import numpy as np
import pytest

from manim_atoms.core.holography import (
    ZERNIKE_NAMES, far_field, grating_phase, gs_step, illumination, lens_phase, osa_to_nm,
    pupil_grid, spot_fields, spot_phase, spot_pixel, strehl, uniformity, wgs_step, zernike,
)

N = 64
X, Y, RHO, THETA = pupil_grid(N)
A = illumination(RHO)
GRID = np.array([[kx, ky] for ky in (-8, -4, 0, 4, 8) for kx in (-8, -4, 0, 4, 8)], float)


def test_osa_index_counts_along_the_pyramid_rows():
    assert [osa_to_nm(j) for j in range(6)] == [(0, 0), (1, -1), (1, 1), (2, -2), (2, 0), (2, 2)]
    assert osa_to_nm(12) == (4, 0)
    assert all(osa_to_nm(j) in ZERNIKE_NAMES for j in range(15))


def test_zernike_modes_are_orthonormal_over_the_disc():
    _, _, rho, theta = pupil_grid(256)
    inside = rho <= 1
    modes = np.array([zernike(*osa_to_nm(j), rho, theta)[inside] for j in range(15)])
    gram = modes @ modes.T / inside.sum()
    assert np.allclose(gram, np.eye(15), atol=0.03)


def test_zernike_rejects_a_mode_that_does_not_exist():
    with pytest.raises(ValueError):
        zernike(2, 1, RHO, THETA)


def test_flat_mask_peaks_at_one_on_the_axis():
    image = far_field(np.zeros((N, N)), A)
    assert np.unravel_index(image.argmax(), image.shape) == spot_pixel((0, 0), N)
    assert image.max() == pytest.approx(1.0)


@pytest.mark.parametrize("spot", [(5, 0), (0, 7), (5, -3), (-6, 2)])
def test_grating_moves_the_spot_by_its_periods(spot):
    image = far_field(grating_phase(X, Y, *spot), A)
    assert np.unravel_index(image.argmax(), image.shape) == spot_pixel(spot, N)
    assert image.max() == pytest.approx(1.0, abs=1e-6)


def test_lens_lowers_the_peak_in_the_focal_plane():
    image = far_field(lens_phase(RHO, 1.0), A)
    assert image.max() < 0.2


def test_phase_is_only_meaningful_mod_two_pi():
    phase = grating_phase(X, Y, 3, 2)
    assert np.allclose(far_field(phase, A), far_field(np.mod(phase, 2 * np.pi) - 40 * np.pi, A))


def test_strehl_is_one_flat_and_follows_marechal_when_small():
    assert strehl(np.zeros((N, N)), A) == pytest.approx(1.0)
    error = 0.3 * zernike(2, 0, RHO, THETA)
    assert strehl(error, A) == pytest.approx(np.exp(-0.09), abs=0.01)
    assert far_field(error, A)[spot_pixel((0, 0), N)] == pytest.approx(strehl(error, A))


def test_weighted_gs_evens_the_spots_out():
    rng = np.random.default_rng(1)
    start = spot_phase(X, Y, GRID, rng.uniform(0, 2 * np.pi, len(GRID)))
    plain = weighted = start
    weights = np.ones(len(GRID))
    for _ in range(30):
        plain, _ = gs_step(plain, A, X, Y, GRID)
        weighted, weights, _ = wgs_step(weighted, weights, A, X, Y, GRID)
    first = np.abs(spot_fields(start, A, X, Y, GRID)) ** 2
    gs = np.abs(spot_fields(plain, A, X, Y, GRID)) ** 2
    wgs = np.abs(spot_fields(weighted, A, X, Y, GRID)) ** 2
    assert uniformity(wgs) > 0.95
    assert uniformity(wgs) > uniformity(gs) > uniformity(first)


def test_spot_intensities_match_the_far_field():
    mask = spot_phase(X, Y, GRID[:3])
    image = far_field(mask, A)
    direct = np.abs(spot_fields(mask, A, X, Y, GRID[:3])) ** 2
    assert np.allclose([image[spot_pixel(s, N)] for s in GRID[:3]], direct)


def test_one_spot_and_plain_lists_are_fine():
    mask, weights, intensity = wgs_step(np.zeros((N, N)), [1.0], A, X, Y, [(4, 0)])
    assert weights == pytest.approx([1.0])
    assert far_field(mask, A)[spot_pixel((4, 0), N)] == pytest.approx(1.0)
    assert spot_phase(X, Y, [(4, 0)]).shape == (N, N)


def test_a_dark_spot_keeps_its_weight():
    # a grating aimed at (4, 0) puts nothing on a spot at (-9, 9)
    mask = grating_phase(X, Y, 4, 0)
    _, weights, intensity = wgs_step(mask, [1.0, 1.0], A, X, Y, [(4, 0), (20, 20)])
    assert np.all(np.isfinite(weights))


def test_gaussian_illumination_is_cut_off_by_the_aperture():
    a = illumination(RHO, 0.7)
    assert a[RHO > 1].max() == 0 and a.max() <= 1
    assert uniformity([1, 1, 1]) == 1 and uniformity([1, 3]) == pytest.approx(0.5)


def test_a_spot_weighted_to_nothing_is_left_out():
    both = spot_phase(X, Y, [(4, 0), (-4, 0)], weights=[1.0, 0.0])
    image = far_field(both, A)
    assert image[spot_pixel((4, 0), N)] == pytest.approx(1.0)
    assert image[spot_pixel((-4, 0), N)] < 1e-3
