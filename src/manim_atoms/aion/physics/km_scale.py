"""What going from the tabletop prototype to AION-km asks for, in numbers.

The prototype's figures are from Baynham et al., Nature 654, 622 (2026) and
its Methods; AION-km's are Table 1 of Badurina et al., JCAP 05 (2020) 011
(via ``uldm_sensitivity.AION_PARAMETERS``), bar the atom number, which is the
AION proposal's. Everything else here follows from those by textbook scaling
-- each function says which.
"""

import numpy as np

from manim_atoms.aion.physics.uldm_sensitivity import AION_PARAMETERS

# --- constants ---------------------------------------------------------------
CLOCK_WAVELENGTH = 698.4e-9  # m, 1S0 -> 3P0

# --- the prototype (Baynham et al. 2026) -------------------------------------
PROTO_BASELINE = 1e-3  # m, the two dipole traps' separation
PROTO_T = 200e-6  # s, dark time between pulses
PROTO_WAIST = 600e-6  # m, the clock beam's
PROTO_POWER = 0.640  # W, the most clock light there is: a 44 us pi pulse
PROTO_PI_TIME = 44e-6  # s
PROTO_ATOMS = 3100 + 2040  # median atoms per shot, top trap + bottom
PROTO_SHOT_RATE = 0.3  # Hz, the typical sampling rate
# K, the atoms that make it through velocity slicing (our figure: the paper
# quotes only the 2 uK of the dipole traps, before slicing)
PROTO_TEMPERATURE = 10e-9
PROTO_INJECTED_NOISE = 4 * np.pi  # rad, s.d. of the phase steps put in (HLN)
KM_LASER_PHASE = 0.71  # rad per shot at T = 5 s: their Methods' estimate
# Best LMT on a strontium clock-type line to date (Rudolph et al. PRL 124,
# 083604 (2020), 689 nm), which the AION paper quotes.
BEST_SR_LMT = 141

# --- AION-km (Badurina et al. 2020, Table 1) ---------------------------------
KM_BASELINE, KM_T, KM_PHASE_NOISE, KM_LMT = AION_PARAMETERS["aion_km"]
# Atoms per shot: from the AION proposal, not the paper.
KM_ATOMS = 1e7


def waist_for_rayleigh_range(z_r, wavelength=CLOCK_WAVELENGTH):
    """The Gaussian waist w0 whose Rayleigh range pi w0^2 / lambda is z_r: the
    narrowest beam that stays collimated (radius within sqrt 2) that far."""
    return np.sqrt(z_r * wavelength / np.pi)


def power_for_same_rabi(waist):
    """The power a beam of this waist needs to drive the prototype's pi pulse
    in the same time: Rabi frequency goes as sqrt(peak intensity), and peak
    intensity as P / w^2, so P scales as w^2."""
    return PROTO_POWER * (waist / PROTO_WAIST) ** 2


def pulse_count(n=KM_LMT, q=1):
    """Pulses in an n-fold LMT sequence with Q mirror stages:
    2 Q (2n - 1) + 1, AION 2020 below its eq. (2.5)."""
    return 2 * q * (2 * n - 1) + 1


def fidelity_for_contrast(pulses, contrast=np.exp(-1)):
    """The per-pulse transfer efficiency f with f^pulses = contrast: what each
    pulse must reach for that much of the atoms to make it through."""
    return contrast ** (1 / pulses)


# --- the figures the challenges slide quotes ---------------------------------
KM_WAIST = waist_for_rayleigh_range(KM_BASELINE)  # ~2.1 cm
KM_POWER = power_for_same_rabi(KM_WAIST)  # ~800 W
KM_PULSES = pulse_count()  # ~1.6e5
KM_FIDELITY = fidelity_for_contrast(KM_PULSES)  # 1 - ~6e-6
