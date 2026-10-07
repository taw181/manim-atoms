"""The pulse-sequence engine against the physics: every sequence a scene can
draw closes where it should, kicks the way recoil says, and falls the way
gravity says. Pure numbers: nothing here renders."""

import json
from pathlib import Path

import numpy as np
import pytest

from manim_atoms.core.primitives import recoil
from manim_atoms.interferometry.tools.lmt import (
    LMT_KICKS, LMT_STEP, LMT_T0, LMT_TAIL, LMT_U, LMT_Z,
    LMZ_ORDER, LMZ_PORT, LMZ_STEP, LMZ_T, LMZ_T0, LMZ_U, LMZ_Z,
    lmt_ladder_pulses, lmz_pulses,
)
from manim_atoms.interferometry.tools.pulse_sequence import Pulse, run_sequence

BEFORE = json.loads((Path(__file__).parent / "fixtures" / "lmt_before.json").read_text())
T, U = 2.0, 0.5


def closing(seq):
    """The outputs the last pulse merged, as {name: (state, velocity)}."""
    return {name: (seq.ports[name].state, seq.ports[name].v)
            for name, _, _ in seq.steps[-1].merges}


def test_mach_zehnder_closes_into_two_ports_one_recoil_apart():
    seq = run_sequence([Pulse(0, 0.5), Pulse(T, 1), Pulse(2 * T, 0.5)], (0, 0), U)
    assert closing(seq) == {"g": ("g", 0.0), "e": ("e", 1.0)}
    assert len(seq.ports) == 2


@pytest.mark.parametrize("n", [1, 3, 5, 11])
def test_lmt_mach_zehnder_closes_at_any_order(n):
    pulses = lmz_pulses(n, 0.3, 3.0)
    assert len(pulses) == 2 * n + 1
    seq = run_sequence(pulses, (0, 0), 0.1)
    assert set(closing(seq)) == {"g", "e"}
    # at the mirror the arms are n recoils apart
    mirror = next(s for s in seq.steps if s.pulse.stage == 1)
    v = {name: arm_v for name, arm_v in _velocities_before(seq, mirror).items()}
    assert abs(v["1"] - v["0"]) == pytest.approx(n)


def _velocities_before(seq, step):
    """Each arm's velocity on the leg that ends at ``step``: its slope / u."""
    k = seq.steps.index(step)
    return {name: (end[1] - start[1]) / (end[0] - start[0]) / 0.1
            for name, start, end, _, _ in seq.steps[k - 1].legs}


def test_lmt_mach_zehnder_matches_what_lmt_history_drew():
    seq = run_sequence(lmz_pulses(LMZ_ORDER, LMZ_STEP, LMZ_T, t0=LMZ_T0), (LMZ_T0, LMZ_Z),
                       LMZ_U, port=LMZ_PORT)
    assert len(seq.steps) == len(BEFORE["lmz_history"])
    for old, step in zip(BEFORE["lmz_history"], seq.steps):
        assert step.x == pytest.approx(old["x"], abs=1e-12)
        assert step.pulse.from_below == old["from_below"]
        assert [leg[0] for leg in step.legs] == [leg[0] for leg in old["legs"]]
        for (_, s1, e1, st1), (_, s2, e2, st2, _) in zip(old["legs"], step.legs):
            assert st1 == st2
            np.testing.assert_allclose(s2, s1, atol=1e-12)
            np.testing.assert_allclose(e2, e1, atol=1e-12)


def test_ladder_matches_what_lmt_points_drew():
    end = LMT_T0 + (LMT_KICKS - 1) * LMT_STEP + LMT_TAIL
    seq = run_sequence(lmt_ladder_pulses(), (LMT_T0, LMT_Z), LMT_U, until=end)
    np.testing.assert_allclose(seq.paths["1"], BEFORE["ladder"]["upper"], atol=1e-12)
    np.testing.assert_allclose(seq.paths["0"], BEFORE["ladder"]["lower"], atol=1e-12)


def test_ramsey_borde_closes_two_interferometers_and_leaves_the_rest_open():
    pulses = [Pulse(0, 0.5), Pulse(T, 0.5),
              Pulse(T + 1.0, 0.5, from_below=False), Pulse(2 * T + 1.0, 0.5, from_below=False)]
    seq = run_sequence(pulses, (0, 0), U)
    merges = seq.steps[-1].merges
    assert len(merges) == 4  # two interferometers, two ports each
    assert all(len(members) == 2 for _, members, _ in merges)
    assert len(seq.ports) - len(merges) == 8  # the outputs that met nothing
    assert all(not step.merges for step in seq.steps[:-1])


def fall(g):
    return lambda t: -0.5 * g * t * t


def test_gravimeter_falls_and_still_closes():
    g = 0.2
    seq = run_sequence([Pulse(0, 0.5), Pulse(T, 1), Pulse(2 * T, 0.5)], (0, 1), U, disp=fall(g))
    assert set(closing(seq)) == {"g", "e"}
    # every corner is where it would be without gravity, fallen by g t^2 / 2
    still = run_sequence([Pulse(0, 0.5), Pulse(T, 1), Pulse(2 * T, 0.5)], (0, 1), U)
    for name, corners in still.paths.items():
        for (t, z, _), (t_g, z_g, _) in zip(corners, seq.paths[name]):
            assert t_g == t and z_g == pytest.approx(z - 0.5 * g * t * t)
    # and the legs carry the fall, for draw_wavy_legs to bow
    assert all(leg[4] is seq.disp for step in seq.steps for leg in step.legs)


def test_fountain_rises_and_falls_symmetrically_about_its_apex():
    g, v0 = 0.2, 4.0
    apex = v0 * U / g  # where v u = g t
    pulses = [Pulse(apex - T, 0.5), Pulse(apex, 1), Pulse(apex + T, 0.5)]
    seq = run_sequence(pulses, (0, 0), U, v0=v0, disp=fall(g))
    assert set(closing(seq)) == {"g", "e"}
    corners = {round(t, 9): z for t, z, _ in seq.paths["0"]}
    assert corners[round(apex - T, 9)] == pytest.approx(corners[round(apex, 9)] - 0.5 * g * T * T)


@pytest.mark.parametrize("state", ["g", "e"])
@pytest.mark.parametrize("from_below", [True, False])
def test_a_pi_pulse_kicks_by_recoil(state, from_below):
    first = [Pulse(0, 1)] if state == "e" else []  # a pi pulse puts the atom in |e>
    seq = run_sequence(first + [Pulse(1, 1, from_below)], (0, 0), U)
    before = 1.0 if state == "e" else 0.0
    dv, new_state = recoil(state, from_below)
    assert seq.ports[""].v == before + dv
    assert seq.ports[""].state == new_state


def test_only_the_arms_a_pulse_names_are_driven():
    seq = run_sequence([Pulse(0, 0.5), Pulse(1, 1, arms=frozenset({"1"})), Pulse(2, 1)],
                       (0, 0), U)
    assert [arm for arm, _, _ in seq.steps[1].hits] == ["1"]
    assert {arm for arm, _, _ in seq.steps[2].hits} == {"0", "1"}


def test_dropped_arms_leave_the_figure():
    seq = run_sequence([Pulse(0, 0.5, drop=frozenset({"0"})), Pulse(1, 1)], (0, 0), U)
    assert set(seq.ports) == {"1"}
