"""The numbers of a gate between two molecules through a Rydberg atom.

No manim. The scheme is Zhang and Tarbutt's (PRX Quantum 3, 030340 (2022)):
an atom sits between two polar molecules, each holding a qubit in |0> and
|1>. An electric field tunes the atom's Rydberg transition |r> <-> |R> into
resonance with the molecules' |1> <-> |2>, so a molecule in |1> and the atom
in |r> exchange an excitation through the dipole-dipole interaction, at
V_DD. A laser then drives the atom |g> <-> |r> with a smooth 2 pi pulse.
With both molecules in |0> nothing couples to |r>: the atom goes round one
Rabi cycle and the state comes back with its sign changed. With a molecule
in |1> the exchange leaves a state with no |r> in it, which the system
follows there and back, picking up no phase. That is a controlled-Z gate.

For each input the atom and molecules stay within three states: the atom in
|g>, the atom in |r>, and the excitation exchanged (a molecule in |2>, the
atom in |R>). gate_run steps their amplitudes through the pulse. A sign
shows only against something else, so the molecules may start in any
superposition (qubit): gate_state is then the three particles' joint state
through the pulse, gate_populations each particle's populations in it, and
bloch_vector what is left of each molecule's own state, which is nothing
once the two are entangled. Times are in microseconds and frequencies in
radians per microsecond.
"""

from functools import lru_cache

import numpy as np

# The paper's example, CaF either side of Rb at 1 um (its Fig. 2):
# V_DD / 2 = 2 pi x 2.02 MHz, and a 1.25 us pulse, which is slow enough
# against V_DD for the atom to follow.
GATE_TIME = 1.25
V_DD = 2 * 2 * np.pi * 2.02
GATE_STEPS = 400  # of the stepping through the pulse


def rabi_frequency(t, duration=GATE_TIME):
    """The laser's Rabi frequency a time ``t`` into the pulse:
    Omega_max sin(pi t / T), with Omega_max = pi^2 / T so its area is 2 pi."""
    t = np.asarray(t, dtype=float)
    inside = (t >= 0) & (t <= duration)
    return np.where(inside, np.pi**2 / duration * np.sin(np.pi * t / duration), 0.0)


def gate_hamiltonian(ones, rabi, coupling=V_DD):
    """The gate's Hamiltonian (the paper's Eq. 1) with ``ones`` of the two
    molecules in |1>, on the states (atom in |g>, atom in |r>, excitation
    exchanged): the laser joins the first two at ``rabi`` / 2, and the
    exchange joins the last two at sqrt(ones) ``coupling`` / 2, since two
    molecules in |1> couple to the atom together."""
    h = np.zeros((3, 3))
    h[0, 1] = h[1, 0] = rabi / 2
    h[1, 2] = h[2, 1] = np.sqrt(ones) * coupling / 2
    return h


@lru_cache(maxsize=None)
def gate_run(ones, duration=GATE_TIME, coupling=V_DD, steps=GATE_STEPS):
    """(times, amplitudes) through the pulse, starting with the atom in |g>:
    ``amplitudes`` is (steps + 1, 3), on gate_hamiltonian's states. Each step
    takes the Hamiltonian at its middle as constant."""
    times = np.linspace(0, duration, steps + 1)
    amplitudes = np.zeros((steps + 1, 3), dtype=complex)
    amplitudes[0, 0] = 1
    dt = duration / steps
    for i in range(steps):
        energies, states = np.linalg.eigh(
            gate_hamiltonian(ones, rabi_frequency(times[i] + dt / 2, duration), coupling))
        step = states @ np.diag(np.exp(-1j * energies * dt)) @ states.T
        amplitudes[i + 1] = step @ amplitudes[i]
    return times, amplitudes


def gate_phase(ones, duration=GATE_TIME, coupling=V_DD):
    """The phase the state comes back with after the pulse, in (-pi, pi]:
    pi with both molecules in |0>, near zero otherwise."""
    _, amplitudes = gate_run(ones, duration, coupling)
    return float(np.angle(amplitudes[-1, 0]))


def qubit(angle):
    """A molecule's qubit after a microwave pulse of area ``angle`` from
    |0>, as its amplitudes in (|0>, |1>): cos(angle / 2)|0> + sin(angle / 2)|1>.
    0 is |0>, pi is |1>, pi / 2 is |0> + |1> and -pi / 2 is |0> - |1>."""
    return np.array([np.cos(angle / 2), np.sin(angle / 2)])


def gate_state(first, second, t, duration=GATE_TIME, coupling=V_DD):
    """The three particles' joint state a time ``t`` into the pulse, with
    the molecules starting in the qubit states ``first`` and ``second``
    (each its amplitudes in |0> and |1>) and the atom in |g>.

    A (3, 3, 3) array of amplitudes, indexed by the first molecule's level
    (|0>, |1>, |2>), the atom's (|g>, |R>, |r>) and the second molecule's.
    Each of the four inputs |00>, |01>, |10>, |11> runs through the pulse on
    its own (gate_run); the exchanged excitation puts a molecule that was in
    |1> into |2> and the atom into |R>, shared equally when both were.
    """
    state = np.zeros((3, 3, 3), dtype=complex)
    for a in (0, 1):
        for b in (0, 1):
            times, amplitudes = gate_run(a + b, duration, coupling)
            ground, rydberg, exchanged = (
                first[a] * second[b] * np.interp(t, times, amplitudes[:, k]) for k in range(3))
            state[a, 0, b] += ground
            state[a, 2, b] += rydberg
            if a:
                state[2, 1, b] += exchanged / np.sqrt(a + b)
            if b:
                state[a, 1, 2] += exchanged / np.sqrt(a + b)
    return state


def gate_populations(state):
    """Each particle's populations in a gate_state, as (molecule, atom,
    molecule): a molecule's are in (|0>, |1>, |2>), the atom's in
    (|g>, |R>, |r>), bottom to top."""
    weights = np.abs(state) ** 2
    return tuple(tuple(float(p) for p in weights.sum(axis=others))
                 for others in ((1, 2), (0, 2), (0, 1)))


def bloch_vector(state, molecule):
    """What a gate_state leaves of one molecule's own qubit (``molecule`` is
    0 or 1), as a Bloch vector (x, y, z): |0> is +z, |0> + |1> is +x.

    Its length is 1 while the molecule has a state of its own and shrinks
    as it becomes entangled with the atom or the other molecule, down to 0
    when nothing of its own is left."""
    rows = np.moveaxis(state, 2 * molecule, 0).reshape(3, 9)
    density = rows @ rows.conj().T
    return np.array([2 * density[0, 1].real, 2 * density[1, 0].imag,
                     (density[0, 0] - density[1, 1]).real])
