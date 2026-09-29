"""AION's reach for ultralight scalar dark matter coupled to photons, as numbers.

The curves of Badurina et al., JCAP 05 (2020) 011 (arXiv:1911.11755), Fig. 3
middle panel -- the photon coupling |d_e| each scenario reaches at SNR 1 in
1e8 s, against the scalar's mass m_phi -- and the lower edge of the region
already excluded, read off the PDF's vector paths into
aionanim/data/uldm_sensitivity/ by data_scripts/digitise_uldm_sensitivity.py.

Masses are in eV; a field of mass m oscillates at f = m c^2 / h.
"""

import numpy as np

from aionanim.resources import data_path

DATA_DIR = data_path("uldm_sensitivity")

H_EV = 4.135668e-15  # Planck's constant, eV s

# stem: label, strongest reach last so it is drawn on top: the curves the
# plots draw. The solid curves only: the paper's dotted continuations
# (0.1-0.3 Hz) are left out. AION-10 and AION-100 are their goal scenarios,
# one line per stage as on the gravitational-wave plot; the initial ones
# are in the data too (aion10_initial, aion100_initial) and load by stem.
ULDM_SCENARIOS = {
    "aion10_goal": "AION-10 (goal)",
    "aion100_goal": "AION-100 (goal)",
    "aedge": "AEDGE",
    "aion_km": "AION-km",
}
EXCLUDED = "excluded"  # the grey region's lower edge

# The half interrogation time the paper assumes for AION-10 and AION-100
# (Table 1 and the text under it): a 10 m launch-mode interferometer.
AION10_T = 1.4  # s


# --- below 0.3 Hz: the paper's own model, carried on -------------------------
# The paper draws AION's curves only above 0.3 Hz (dotted to 0.1 Hz), where it
# expects gravity-gradient noise to take over; the gravitational-wave curves
# the talk shows (GW_exclusion_plot.svg) carry each stage on down to the edge
# of their frame with that noise left out. So that the two plots say the same
# thing about the same instrument, the ULDM curves are carried down too, with
# the paper's own signal model -- eqs. (3.6)-(3.7), |sin x| ~ min(x, 1/sqrt 2),
# SNR 1 in 1e8 s with the coherence time of eq. (3.5) -- and Table 1's
# parameters. The model is scaled onto each digitised curve at its low-mass
# end, so the join is exact and the digitised curve is untouched above it.
HBAR_EV = H_EV / (2 * np.pi)  # eV s
C = 2.99792458e8  # m/s
RHO_DM = 0.3e9 * (1.973269804e-5) ** 3  # 0.3 GeV/cm^3, in eV^4
M_PLANCK = 1.220890e28  # eV; G = 1 / M_PLANCK^2
OMEGA_SR = 2 * np.pi * 429.228e12  # the Sr clock transition, rad/s
XI_SR = 2.06  # its sensitivity to alpha, xi_A (text under eq. 3.7)
T_INT = 1e8  # s, the integration time
# stem: (L / m, T / s, delta phi_noise / (1/sqrt Hz), LMT kicks n): Table 1
AION_PARAMETERS = {
    "aion10_initial": (10, 1.4, 1e-3, 100),
    "aion10_goal": (10, 1.4, 1e-4, 1000),
    "aion100_initial": (100, 1.4, 1e-4, 1000),
    "aion100_goal": (100, 1.4, 1e-5, 40000),
    "aion_km": (2000, 5.0, 0.3e-5, 40000),
}
# How far down the curves are carried: past the left edge of any plot of
# them, as the gravitational-wave curves run past theirs.
ULDM_EXTEND_TO = 1e-20  # eV


def _sin(x):
    """The paper's power-averaged |sin x|."""
    return np.minimum(np.abs(x), 1 / np.sqrt(2))


def model_reach(m, L, T, dphi, n):
    """|d_e| reached at SNR 1 by a gradiometer (L, T, dphi, n), eqs. 3.5-3.7.

    Phase-noise limited: SNR = Phi_s sqrt(t) / dphi while the integration
    time t is shorter than the field's coherence time, and
    Phi_s (t tau_c)^(1/4) / dphi once it is longer.
    """
    m = np.asarray(m, dtype=float)
    w = m / HBAR_EV
    tau_c = 6.6 * (1e-10 / m)
    t_eff = np.where(T_INT < tau_c, np.sqrt(T_INT), (T_INT * tau_c) ** 0.25)
    shift = np.sqrt(8 * np.pi * RHO_DM) / M_PLANCK / m * OMEGA_SR * XI_SR
    response = (8 * shift / w * _sin(w * n * L / C / 2)
                * _sin(w * (T - (n - 1) * L / C) / 2) * _sin(w * T / 2))
    return dphi / (t_eff * response)


def _read(stem):
    with open(DATA_DIR / f"{stem}.csv") as f:
        rows = [line for line in f if not line.startswith(("#", "m_eV"))]
    m, d = np.loadtxt(rows, delimiter=",").T
    return m, d


def load_uldm_sensitivity(stem, extend=True):
    """(m_phi / eV, |d_e|) arrays from aionanim/data/uldm_sensitivity/<stem>.csv.

    An AION stage is carried on below the paper's 0.3 Hz down to
    ULDM_EXTEND_TO by model_reach, scaled to meet the digitised curve;
    extend=False gives the digitised curve alone.
    """
    m, d = _read(stem)
    if not extend or stem not in AION_PARAMETERS or m[0] <= ULDM_EXTEND_TO:
        return m, d
    params = AION_PARAMETERS[stem]
    scale = d[0] / model_reach(m[0], *params)
    below = np.logspace(np.log10(ULDM_EXTEND_TO), np.log10(m[0]), 120)[:-1]
    return (np.concatenate([below, m]),
            np.concatenate([scale * model_reach(below, *params), d]))


def mass_from_frequency(f):
    """m_phi / eV of a field oscillating at f / Hz."""
    return H_EV * f


def frequency_from_mass(m):
    """f / Hz of a field of mass m / eV."""
    return m / H_EV


def coupling_at(stem, mass):
    """|d_e| on a curve at `mass` / eV, linear in log-log; nan off its ends."""
    m, d = load_uldm_sensitivity(stem)
    x = np.log10(mass)
    if not m[0] <= mass <= m[-1]:
        return np.nan
    return 10 ** np.interp(x, np.log10(m), np.log10(d))
