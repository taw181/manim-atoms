"""What going from the tabletop prototype to AION-km asks for, in numbers.

The prototype's figures are from Baynham et al., Nature 654, 622 (2026) and
its Methods; AION-km's are Table 1 of Badurina et al., JCAP 05 (2020) 011
(via ``uldm_sensitivity.AION_PARAMETERS``). Everything else here follows from
those by textbook scaling -- each function says which.
"""

import numpy as np

from aionanim.physics.uldm_sensitivity import AION_PARAMETERS

# --- constants ---------------------------------------------------------------
K_B = 1.380649e-23  # J/K
AMU = 1.66053907e-27  # kg
G = 9.81  # m/s^2
M_SR87 = 86.9089 * AMU
CLOCK_WAVELENGTH = 698.4e-9  # m, 1S0 -> 3P0

# --- the prototype (Baynham et al. 2026) -------------------------------------
PROTO_BASELINE = 1e-3  # m, the two dipole traps' separation
PROTO_T = 200e-6  # s, dark time between pulses
PROTO_WAIST = 600e-6  # m, the clock beam's
PROTO_POWER = 0.640  # W, the most clock light there is: a 44 us pi pulse
PROTO_PI_TIME = 44e-6  # s
PROTO_ATOMS = 3100 + 2040  # median atoms per shot, top trap + bottom
PROTO_SHOT_RATE = 0.3  # Hz, the typical sampling rate
PROTO_TEMPERATURE = 2e-6  # K, the clouds in the dipole traps
PROTO_INJECTED_NOISE = 4 * np.pi  # rad, s.d. of the phase steps put in (HLN)
KM_LASER_PHASE = 0.71  # rad per shot at T = 5 s: their Methods' estimate
# Best LMT on a strontium clock-type line to date (Rudolph et al. PRL 124,
# 083604 (2020), 689 nm), which the AION paper quotes.
BEST_SR_LMT = 141

# --- AION-km (Badurina et al. 2020, Table 1) ---------------------------------
KM_BASELINE, KM_T, KM_PHASE_NOISE, KM_LMT = AION_PARAMETERS["aion_km"]


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


def flux_for_phase_noise(delta_phi):
    """Atoms per second at the standard quantum limit, 1/sqrt(N) per shot, for
    a phase noise density delta_phi / (rad/sqrt Hz): N-dot = 1 / delta_phi^2."""
    return 1 / delta_phi**2


def temperature_for_spread(size, duration, mass=M_SR87):
    """The temperature whose cloud grows by no more than `size` (rms) in
    `duration`: cloud_spread inverted, m (size / duration)^2 / k_B."""
    return mass * (size / duration) ** 2 / K_B


def cloud_spread(duration, temperature=PROTO_TEMPERATURE, mass=M_SR87):
    """How far an unkicked thermal cloud's rms radius grows in `duration`:
    sigma_v t, with sigma_v = sqrt(k_B T / m)."""
    return np.sqrt(K_B * temperature / mass) * duration


# --- the figures the challenges slide quotes ---------------------------------
KM_WAIST = waist_for_rayleigh_range(KM_BASELINE)  # ~2.1 cm
KM_POWER = power_for_same_rabi(KM_WAIST)  # ~800 W
KM_PULSES = pulse_count()  # ~1.6e5
KM_FIDELITY = fidelity_for_contrast(KM_PULSES)  # 1 - ~6e-6
KM_FLUX = flux_for_phase_noise(KM_PHASE_NOISE)  # ~1e11 atoms/s
PROTO_FLUX = PROTO_ATOMS * PROTO_SHOT_RATE  # ~1.5e3 atoms/s
KM_CLOUD_SPREAD = cloud_spread(2 * KM_T)  # ~14 cm at 2 uK
# None of the three papers sets a temperature, so this one is ours: small
# enough that the cloud stays a tenth of the beam's waist through 2T, where
# the beam's intensity and wavefront are nearly the same for every atom.
KM_CLOUD_FRACTION = 0.1
KM_CLOUD_SIZE = KM_CLOUD_FRACTION * KM_WAIST  # ~2 mm
KM_TEMPERATURE = temperature_for_spread(KM_CLOUD_SIZE, 2 * KM_T)  # ~0.4 nK
