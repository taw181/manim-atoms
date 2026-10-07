"""The phase wheel: it wraps, every stop shows on the background, and a
phase mask is clipped to its aperture. Builds images but renders nothing."""

import numpy as np

from manim_atoms.core.optics import FocalImage, PhaseMask, phase_rgb
from manim_atoms.style import PHASE_COLORS, PLOT_BACKGROUND

TAU = 2 * np.pi


def test_the_wheel_wraps():
    assert PHASE_COLORS[0] == PHASE_COLORS[-1]
    phase = np.array([0.3, 1.7, 5.0])
    assert np.array_equal(phase_rgb(phase), phase_rgb(phase + TAU))
    assert np.array_equal(phase_rgb(phase), phase_rgb(phase - 3 * TAU))


def test_there_is_no_step_anywhere_round_the_wheel():
    wheel = phase_rgb(np.linspace(0, TAU, 2000)).astype(int)
    assert np.abs(np.diff(wheel, axis=0)).max() <= 6
    assert np.abs(phase_rgb(TAU - 1e-9).astype(int) - phase_rgb(0.0).astype(int)).max() <= 6


def test_every_colour_is_clear_of_the_background():
    background = int(PLOT_BACKGROUND[1:3], 16)
    wheel = phase_rgb(np.linspace(0, TAU, 256, endpoint=False)).astype(int)
    assert (wheel.max(axis=1) - background).min() > 120


def test_opposite_phases_are_told_apart():
    a, b = phase_rgb(np.array([0.0, 1.0, 2.0])).astype(int), phase_rgb(np.array([3.14, 4.14, 5.14])).astype(int)
    assert np.abs(a - b).sum(axis=1).min() > 150


def test_a_mask_is_clipped_to_its_aperture_and_repaints():
    aperture = np.array([[1.0, 0.0], [0.5, 1.0]])
    mask = PhaseMask(np.zeros((2, 2)), aperture)
    assert mask.pixel_array[..., 3].tolist() == [[255, 0], [127, 255]]
    before = mask.pixel_array.copy()
    mask.paint(np.full((2, 2), np.pi))
    assert not np.array_equal(mask.pixel_array[..., :3], before[..., :3])
    assert np.array_equal(mask.pixel_array[..., 3], before[..., 3])
    assert np.array_equal(PhaseMask(np.full((2, 2), 9 * np.pi)).pixel_array, PhaseMask(np.full((2, 2), np.pi)).pixel_array)


def test_a_focal_image_is_as_opaque_as_the_light_is_bright():
    image = FocalImage(np.array([[0.0, 0.25], [1.0, 4.0]]), "#ffffff", gamma=0.5)
    assert image.pixel_array[..., 3].tolist() == [[0, 127], [255, 255]]
    image.paint(np.zeros((2, 2)))
    assert image.pixel_array[..., 3].max() == 0
