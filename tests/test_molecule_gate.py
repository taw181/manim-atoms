"""The molecule-molecule gate against what a controlled-Z demands: the laser
pulse is a 2 pi pulse, the atom always comes back to |g>, and the state
changes sign only when both molecules are in |0>. Pure numbers: nothing here
renders."""

import numpy as np
import pytest

from manim_atoms.tweezers.physics.molecule_gate import (
    GATE_TIME, atom_bloch_vector, overlap, V_DD, bloch_vector, gate_hamiltonian, gate_phase, gate_populations,
    gate_run, gate_state, qubit, rabi_frequency,
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


ZERO, ONE, PLUS, MINUS = qubit(0), qubit(np.pi), qubit(np.pi / 2), qubit(-np.pi / 2)
TIMES = [0.0, 0.4, GATE_TIME / 2, 1.0, GATE_TIME]


def test_a_microwave_pulse_s_area_sets_the_qubit():
    assert np.allclose(ZERO, [1, 0]) and np.allclose(ONE, [0, 1])
    assert np.allclose(PLUS, [1, 1] / np.sqrt(2)) and np.allclose(MINUS, [1, -1] / np.sqrt(2))


@pytest.mark.parametrize("first, second", [(ZERO, ZERO), (ZERO, ONE), (ONE, ONE),
                                           (ZERO, PLUS), (PLUS, PLUS), (MINUS, qubit(0.7))])
@pytest.mark.parametrize("t", TIMES)
def test_the_joint_state_stays_normalised_and_so_does_every_particle(first, second, t):
    state = gate_state(first, second, t)
    assert (np.abs(state) ** 2).sum() == pytest.approx(1)
    for populations in gate_populations(state):
        assert sum(populations) == pytest.approx(1)
        assert min(populations) >= 0


def test_the_exchange_is_shared_between_the_molecules_in_one():
    t = GATE_TIME / 2
    lone, atom, other = gate_populations(gate_state(ZERO, ONE, t))
    assert lone == pytest.approx((1, 0, 0))
    assert other[2] == pytest.approx(atom[1])
    left, atom, right = gate_populations(gate_state(ONE, ONE, t))
    assert left[2] == pytest.approx(right[2]) == pytest.approx(atom[1] / 2)


def test_a_basis_state_has_its_bloch_vector_at_a_pole_throughout():
    for t in TIMES:
        state = gate_state(ZERO, ZERO, t)
        assert np.allclose(bloch_vector(state, 0), [0, 0, 1])
        assert np.allclose(bloch_vector(state, 1), [0, 0, 1])


def test_with_the_first_in_zero_the_second_s_superposition_changes_sign():
    # |0>(|0> + |1>) -> -|0>(|0> - |1>): the vector goes from +x to -x, and
    # through the middle of the sphere, the molecule entangled with the atom.
    assert np.allclose(bloch_vector(gate_state(ZERO, PLUS, 0), 1), [1, 0, 0])
    assert np.linalg.norm(bloch_vector(gate_state(ZERO, PLUS, GATE_TIME / 2), 1)) < 0.1
    assert np.allclose(bloch_vector(gate_state(ZERO, PLUS, GATE_TIME), 1), [-1, 0, 0], atol=0.02)
    assert np.allclose(bloch_vector(gate_state(ZERO, PLUS, GATE_TIME), 0), [0, 0, 1], atol=0.02)


def test_with_the_first_in_one_the_second_s_superposition_is_left_alone():
    for t in TIMES:
        assert bloch_vector(gate_state(ONE, PLUS, t), 1)[0] > 0.9
    assert np.allclose(bloch_vector(gate_state(ONE, PLUS, GATE_TIME), 1), [1, 0, 0], atol=0.02)


def test_the_sign_change_leaves_the_state_a_pulse_from_zero_would():
    # so a scene can go on from |0>(|0> - |1>) with the clock back at nought
    after = gate_state(ZERO, PLUS, GATE_TIME)
    again = gate_state(ZERO, MINUS, 0)
    assert abs(np.vdot(again, after)) == pytest.approx(1, abs=0.01)


def test_both_in_a_superposition_end_up_entangled():
    state = gate_state(PLUS, PLUS, GATE_TIME)
    for molecule in (0, 1):
        assert np.linalg.norm(bloch_vector(state, molecule)) < 0.05
    assert gate_populations(state)[1][0] > 0.99  # and the atom is back out of it


def test_both_in_zero_the_atoms_vector_goes_once_round_and_the_system_flips_sign():
    state = lambda t: gate_state(qubit(0), qubit(0), t)
    assert np.allclose(atom_bloch_vector(state(0)), [0, 0, 1])
    assert atom_bloch_vector(state(GATE_TIME / 2))[2] == pytest.approx(-1, abs=1e-6)
    assert np.allclose(atom_bloch_vector(state(GATE_TIME)), [0, 0, 1], atol=1e-3)
    for t in np.linspace(0, GATE_TIME, 9):
        assert np.linalg.norm(atom_bloch_vector(state(t))) == pytest.approx(1)
    assert overlap(qubit(0), qubit(0), 0) == pytest.approx(1)
    assert overlap(qubit(0), qubit(0), GATE_TIME) == pytest.approx(-1, abs=1e-6)


@pytest.mark.parametrize("angles", [(0, np.pi), (np.pi, 0), (np.pi, np.pi)])
def test_with_a_molecule_in_one_the_system_comes_back_unchanged_and_the_atom_never_turns_over(angles):
    first, second = qubit(angles[0]), qubit(angles[1])
    assert overlap(first, second, GATE_TIME) == pytest.approx(1, abs=0.01)
    for t in np.linspace(0, GATE_TIME, 21):
        assert abs(overlap(first, second, t)) > 0.9
        assert atom_bloch_vector(gate_state(first, second, t))[2] > 0.8
