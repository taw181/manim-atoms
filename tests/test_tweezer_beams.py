"""The beam a tilted tweezer is drawn as: it widens away from its focus, is
cut off at its reach, and seen from straight above it is only its spot.
Builds mobjects but renders nothing."""

import numpy as np
import pytest
from manim import DEGREES

from manim_atoms.core.projection import TiltedView
from manim_atoms.tweezers.tools.beams import (
    TW_EMERGED_RISE, TW_RAYLEIGH, TW_REACH, beam_half_width, hourglass_trap,
)
from manim_atoms.tweezers.tools.tweezer_array import TW_SPOT_RADIUS


def test_the_beam_widens_away_from_its_focus():
    assert beam_half_width(0) == pytest.approx(TW_SPOT_RADIUS)
    assert beam_half_width(TW_RAYLEIGH) == pytest.approx(TW_SPOT_RADIUS * np.sqrt(2))
    z = np.linspace(0, TW_REACH, 50)
    assert np.all(np.diff(beam_half_width(z)) > 0)


def test_looking_straight_down_the_hourglass_is_only_its_spot():
    flat = hourglass_trap(TiltedView([0, 0, 0]), [0, 0], 1.0)
    tilted = hourglass_trap(TiltedView([0, 0, 0], elevation=30 * DEGREES), [0, 0], 1.0)
    assert len(tilted) > len(flat)
    assert flat.width == pytest.approx(2 * TW_SPOT_RADIUS) == flat.height
    # cut off at its reach either side, each end a disc of the beam there
    end = beam_half_width(TW_REACH)
    assert tilted.height == pytest.approx(
        2 * (TW_REACH * np.cos(30 * DEGREES) + end * np.sin(30 * DEGREES)), rel=0.01)
    assert tilted.width == pytest.approx(2 * end, rel=0.01)


def test_the_body_comes_up_as_the_view_tilts():
    def fill(elevation):
        return hourglass_trap(TiltedView([0, 0, 0], elevation=elevation), [0, 0], 1.0)[1]

    barely, half, full = (fill(np.arccos(r * TW_EMERGED_RISE)) for r in (0.1, 0.5, 1.0))
    assert barely.get_fill_opacity() < half.get_fill_opacity() < full.get_fill_opacity()
    assert fill(10 * DEGREES).get_fill_opacity() == pytest.approx(full.get_fill_opacity())
