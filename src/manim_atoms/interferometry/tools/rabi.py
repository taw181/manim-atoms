"""Rabi oscillations: a two-level atom driven by a laser, on the Bloch sphere.

In the frame rotating with the laser, the atom's state is a point on the
Bloch sphere -- |e> at the north pole, |g> at the south -- and a drive of
Rabi frequency Omega, detuned by Delta from the line, turns it about the
fixed vector (Omega cos phi, Omega sin phi, Delta) at the generalised Rabi
frequency Omega' = sqrt(Omega^2 + Delta^2). The laser's phase phi only sets
where round the equator that axis points. The excited-state population is
the height of the tip,

    P_e = (1 + z) / 2 = (Omega^2 / Omega'^2) sin^2(Omega' t / 2),

so on resonance an atom starting in |g> flops all the way up and back,
sin^2(Omega t / 2), and off resonance it turns faster round a tilted axis
and never gets all the way to |e>.

The helpers do the numbers, in units of Omega: time is the pulse area
Omega t, and the detuning is Delta / Omega. The Bloch sphere itself is drawn
with BlochView (interferometry/tools/squeezing.py).
"""

import numpy as np

SOUTH = np.array([0.0, 0.0, -1.0])  # |g>, where every run starts


def drive_axis(azimuth, detuning=0.0):
    """The unit vector the Bloch vector turns about: in the equatorial plane
    at ``azimuth`` (the laser's phase) on resonance, tilted towards |e> by
    atan(Delta / Omega) off it."""
    v = np.array([np.cos(azimuth), np.sin(azimuth), detuning])
    return v / np.linalg.norm(v)


def generalized_rabi(detuning):
    """Omega' / Omega."""
    return np.sqrt(1.0 + detuning**2)


def bloch_vector(pulse_area, azimuth, detuning=0.0, start=SOUTH):
    """The Bloch vector after a drive of area Omega t, from ``start``:
    ``start`` turned by Omega' t about the drive axis (Rodrigues)."""
    n = drive_axis(azimuth, detuning)
    a = pulse_area * generalized_rabi(detuning)
    r = np.asarray(start, dtype=float)
    return (r * np.cos(a) + np.cross(n, r) * np.sin(a)
            + n * np.dot(n, r) * (1 - np.cos(a)))


def excited_population(pulse_area, detuning=0.0):
    """P_e after a drive of area Omega t, from |g>:
    sin^2(Omega' t / 2) / (1 + (Delta / Omega)^2)."""
    w = generalized_rabi(detuning)
    return np.sin(pulse_area * w / 2) ** 2 / w**2


def is_absorbing(pulse_area, detuning=0.0):
    """True while P_e is rising -- the atom taking photons out of the beam --
    and False while stimulated emission is handing them back."""
    return np.sin(pulse_area * generalized_rabi(detuning)) >= 0
