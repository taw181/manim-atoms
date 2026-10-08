"""The molecule-molecule gate against what a controlled-Z demands: the laser
pulse is a 2 pi pulse, the atom always comes back to |g>, and the state
changes sign only when both molecules are in |0>. Pure numbers: nothing here
renders."""

import numpy as np
import pytest

from manim_atoms.tweezers.physics.molecule_gate import (
    GATE_TIME, V_DD, gate_hamiltonian, gate_phase, gate_populations, gate_run,
    rabi_frequency,
)


def test_the_pulse_has_area_two_pi_and_is_off_outside_it():
    t = np.linspace(0, GATE_TIME, 20001)
    assert np.sum(rabi_frequency(t)) * (t[1] - t[0]) == pytest.approx(2 * np.pi, rel=1e-6)
    assert rabi_frequency(-0.1) == 0 and rabi_frequency(GATE_TIME + 0.1) == 0
    assert rabi_frequency(GATE_TIME / 2) == pytest.approx(np.pi**2 / GATE_TIME)


def test_two_molecules_in_one_couple_root_two_harder():
    assert gate_hamiltonian(0, 1.0)[1, 2] == 0
    assert gate_hamiltonian(2, 1.0)[1, 2] == pytest.approx(
        np.sqrt(2) * gate_hamiltonian(1, 1.0)[1, 2])


@pytest.mark.parametrize("ones", [0, 1, 2])
def test_the_run_keeps_the_norm_and_returns_the_atom_to_the_ground_state(ones):
    _, amplitudes = gate_run(ones)
    assert np.allclose((np.abs(amplitudes) ** 2).sum(axis=1), 1)
    assert abs(amplitudes[-1, 0]) ** 2 > 0.99


def test_both_in_zero_the_atom_goes_round_a_rabi_cycle_and_the_sign_flips():
    times, amplitudes = gate_run(0)
    middle = len(times) // 2
    assert abs(amplitudes[middle, 1]) ** 2 == pytest.approx(1, abs=1e-6)
    assert np.allclose(amplitudes[:, 2], 0)
    assert abs(gate_phase(0)) == pytest.approx(np.pi, abs=1e-6)


@pytest.mark.parametrize("ones", [1, 2])
def test_a_molecule_in_one_blocks_the_excitation_and_leaves_no_phase(ones):
    _, amplitudes = gate_run(ones)
    assert (np.abs(amplitudes[:, 1]) ** 2).max() < 0.02
    assert abs(gate_phase(ones)) < 0.05


def test_the_gate_is_a_controlled_z():
    assert abs(gate_phase(0) - 2 * gate_phase(1) + gate_phase(2)) == pytest.approx(
        np.pi, abs=0.1)


def test_the_blocked_atom_follows_the_state_with_no_rydberg_r_in_it():
    # |u> = -sin(theta)|g> + cos(theta)|exchanged>, tan(theta) = V_DD / Omega.
    times, amplitudes = gate_run(1)
    middle = len(times) // 2
    theta = np.arctan(V_DD / rabi_frequency(GATE_TIME / 2))
    assert abs(amplitudes[middle, 2]) ** 2 == pytest.approx(np.cos(theta) ** 2, abs=0.03)


@pytest.mark.parametrize("first, second", [(0, 0), (0, 1), (1, 0), (1, 1), (0.3, 1)])
@pytest.mark.parametrize("t", [0.0, 0.4, GATE_TIME / 2, GATE_TIME])
def test_every_particle_s_populations_sum_to_one(first, second, t):
    if t and (first % 1 or second % 1):
        pytest.skip("a molecule is part-way to |1> only between pulses")
    for populations in gate_populations(first, second, t):
        assert sum(populations) == pytest.approx(1)
        assert min(populations) >= -1e-12


def test_the_exchange_is_shared_between_the_molecules_in_one():
    t = GATE_TIME / 2
    lone, atom, other = gate_populations(0, 1, t)
    assert lone == (1, 0, 0)
    assert other[2] == pytest.approx(atom[1])
    left, atom, right = gate_populations(1, 1, t)
    assert left[2] == pytest.approx(right[2]) == pytest.approx(atom[1] / 2)
