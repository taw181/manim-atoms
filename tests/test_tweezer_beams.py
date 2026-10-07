"""The beam a tilted tweezer is drawn as: it widens and fades away from its
focus, and seen from straight above it is only its spot. Builds mobjects
but renders nothing."""

import numpy as np
import pytest
from manim import DEGREES

from manim_atoms.core.projection import TiltedView
from manim_atoms.tweezers.tools.beams import (
    TW_RAYLEIGH, TW_REACH, axial_intensity, beam_half_width, hourglass_trap,
)
from manim_atoms.tweezers.tools.tweezer_array import TW_SPOT_RADIUS


def test_the_beam_widens_and_fades_away_from_its_focus():
    assert beam_half_width(0) == pytest.approx(TW_SPOT_RADIUS)
    assert beam_half_width(TW_RAYLEIGH) == pytest.approx(TW_SPOT_RADIUS * np.sqrt(2))
    assert axial_intensity(0) == 1 and axial_intensity(TW_RAYLEIGH) < 0.5
    assert axial_intensity(TW_REACH) == 0 and axial_intensity(2 * TW_REACH) == 0
    z = np.linspace(0, TW_REACH, 50)
    assert np.all(np.diff(axial_intensity(z)) < 0)


def test_looking_straight_down_the_hourglass_is_only_its_spot():
    flat = hourglass_trap(TiltedView([0, 0, 0]), [0, 0], 1.0)
    tilted = hourglass_trap(TiltedView([0, 0, 0], elevation=30 * DEGREES), [0, 0], 1.0)
    assert len(tilted) > len(flat)
    assert flat.width == pytest.approx(2 * TW_SPOT_RADIUS) == flat.height
    assert tilted.height == pytest.approx(2 * TW_REACH * np.cos(30 * DEGREES), rel=0.01)
