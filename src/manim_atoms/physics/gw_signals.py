"""Gravitational-wave signals and detector sensitivities, as numbers.

Shared by aionanim.plots.gw_sensitivity (matplotlib) and the manim scenes
that draw the same curves, so both put a merger in the same place:

- ``load_sensitivity``: a detector's h_c curve digitised from
  GW_exclusion_plot.svg into aionanim/data/gw_sensitivity/, with LISA's and
  AEDGE's jagged stretches smoothed (SMOOTHING).
- ``merger_strain`` / ``merger_track``: a black-hole merger's characteristic
  strain, the PhenomA inspiral-merger-ringdown amplitude of Ajith et al.,
  arXiv:0710.2335, orientation-averaged, as h_c = 2 f |h(f)|, at the Planck
  2018 luminosity distance. With a track running from TRACK_START before
  merger to the ringdown cutoff, this reproduces the nine tracks on the
  source figure (60, 1e4, 1e7 Msun at z = 0.1, 1, 10) to within 0.003 dex.
- ``frequency_before_merger`` / ``time_before_merger``: the leading-order
  chirp, which is what places the time-to-merger dots.

Masses are total source-frame masses in Msun; q = m2/m1 <= 1; frequencies
are detector-frame, in Hz.
"""

import numpy as np

from aionanim.resources import data_path

DATA_DIR = data_path("gw_sensitivity")

YEAR = 365.25 * 86400
TRACK_START = 10 * YEAR
TIME_MARKERS = {  # label: time left to merger / s
    "10 y": 10 * YEAR,
    "1 y": YEAR,
    "1 month": YEAR / 12,
    "1 day": 86400,
    "1 hour": 3600,
}

T_SUN = 4.925490947e-6  # G Msun / c^3, s
MPC = 3.0856775814913673e22
H0 = 67.66  # Planck 2018, km/s/Mpc
OMEGA_M = 0.30966


def mass_tex(M):
    """A total mass as TeX math (no $), e.g. 60\\,M_\\odot or 10^{4}\\,M_\\odot."""
    if M < 1e3:
        return rf"{M:g}\,M_\odot"
    exponent = np.floor(np.log10(M))
    mantissa = M / 10**exponent
    lead = "" if np.isclose(mantissa, 1) else rf"{mantissa:g}\times"
    return rf"{lead}10^{{{exponent:.0f}}}\,M_\odot"


def load_sensitivity(stem, smooth=True):
    """(f, h_c) arrays from aionanim/data/gw_sensitivity/<stem>.csv,
    smoothed as SMOOTHING says unless smooth=False."""
    with open(DATA_DIR / f"{stem}.csv") as f:
        rows = [line for line in f if not line.startswith(("#", "f_Hz"))]
    f, h = np.loadtxt(rows, delimiter=",").T
    if smooth and stem in SMOOTHING:
        f, h = smooth_log_log(f, h, *SMOOTHING[stem])
    return f, h


# stem: (frequency / Hz the smoothing starts at, Gaussian width / dex). LISA's
# high-frequency response wiggles (undersampled in the source figure) and the
# staircase of AEDGE's resonant-mode envelope read as jagged edges on a slide;
# AEDGE starts after its broadband spikes and the drop into resonant mode.
SMOOTHING = {"lisa": (0.03, 0.1), "aedge": (7e-3, 0.06)}


def smooth_log_log(f, h, start, sigma, ramp=0.15, step=0.01):
    """A curve blurred by a Gaussian of width sigma dex in log f, log h.

    Below start the points are kept as they are; above it the curve is
    resampled every step dex and eased from raw to blurred over ramp dex, so
    the two parts join smoothly. The ends are padded by straight-line
    extrapolation, so the blur doesn't pull them in.
    """
    x, y = np.log10(f), np.log10(h)
    grid = np.append(np.arange(x[0], x[-1], step), x[-1])
    y_grid = np.interp(grid, x, y)
    n = int(4 * sigma / step)
    kernel = np.exp(-0.5 * (np.arange(-n, n + 1) * step / sigma) ** 2)
    left = np.polyval(np.polyfit(grid[:n], y_grid[:n], 1), grid[0] - step * np.arange(n, 0, -1))
    right = np.polyval(np.polyfit(grid[-n:], y_grid[-n:], 1), grid[-1] + step * np.arange(1, n + 1))
    blurred = np.convolve(np.concatenate([left, y_grid, right]), kernel / kernel.sum(), "valid")
    t = np.clip((grid - np.log10(start)) / ramp, 0, 1)
    ease = t * t * (3 - 2 * t)
    y_grid = (1 - ease) * y_grid + ease * blurred
    raw, smoothed = x < np.log10(start), grid >= np.log10(start)
    return 10 ** np.concatenate([x[raw], grid[smoothed]]), 10 ** np.concatenate([y[raw], y_grid[smoothed]])


def luminosity_distance(z):
    """Luminosity distance in light-seconds, flat LambdaCDM."""
    x = np.linspace(0, z, 2001)
    comoving = np.trapezoid(1 / np.sqrt(OMEGA_M * (1 + x) ** 3 + 1 - OMEGA_M), x)
    return (1 + z) * comoving * MPC / (H0 * 1e3)


def symmetric_mass_ratio(q):
    return q / (1 + q) ** 2


def phenom_a_frequencies(M, z, q=1):
    """PhenomA merger, ringdown, ringdown-width and cutoff frequencies / Hz,
    in the detector frame (redshifted mass)."""
    eta = symmetric_mass_ratio(q)
    pi_M = np.pi * M * (1 + z) * T_SUN
    coefficients = {  # (a, b, c) of (a eta^2 + b eta + c) / (pi M)
        "merger": (2.9740e-1, 4.4810e-2, 9.5560e-2),
        "ringdown": (5.9411e-1, 8.9794e-2, 1.9111e-1),
        "width": (5.0801e-1, 7.7515e-2, 2.2369e-2),
        "cutoff": (8.4845e-1, 1.2848e-1, 2.7299e-1),
    }
    return {k: (a * eta**2 + b * eta + c) / pi_M for k, (a, b, c) in coefficients.items()}


def merger_strain(f, M, z, q=1):
    """Characteristic strain 2 f |h(f)|; NaN above the ringdown cutoff."""
    eta = symmetric_mass_ratio(q)
    fk = phenom_a_frequencies(M, z, q)
    f1, f2, sigma = fk["merger"], fk["ringdown"], fk["width"]
    Mz = M * (1 + z) * T_SUN
    C = Mz ** (5 / 6) * f1 ** (-7 / 6) / (np.pi ** (2 / 3) * luminosity_distance(z))
    C *= np.sqrt(5 * eta / 24)
    lorentzian = sigma / (2 * np.pi) / ((f - f2) ** 2 + sigma**2 / 4)
    w = np.pi * sigma / 2 * (f2 / f1) ** (-2 / 3)
    shape = np.select(
        [f < f1, f < f2, f < fk["cutoff"]],
        [(f / f1) ** (-7 / 6), (f / f1) ** (-2 / 3), w * lorentzian],
        np.nan,
    )
    return 2 * f * C * shape


def _chirp_time(M, z, q):
    return symmetric_mass_ratio(q) ** (3 / 5) * M * (1 + z) * T_SUN


def frequency_before_merger(t, M, z, q=1):
    """GW frequency / Hz a time t / s before merger (leading-order chirp,
    redshifted chirp mass)."""
    return (5 / 256 / t) ** (3 / 8) * _chirp_time(M, z, q) ** (-5 / 8) / np.pi


def time_before_merger(f, M, z, q=1):
    """Inverse of frequency_before_merger: seconds left at frequency f."""
    return 5 / 256 * _chirp_time(M, z, q) ** (-5 / 3) * (np.pi * f) ** (-8 / 3)


def merger_track(M, z, q=1, t_start=TRACK_START, n=600):
    """(f, h_c) of a merger from t_start before it to the ringdown cutoff."""
    f_start = frequency_before_merger(t_start, M, z, q)
    f_end = phenom_a_frequencies(M, z, q)["cutoff"]
    f = np.geomspace(f_start, f_end * (1 - 1e-9), n)
    return f, merger_strain(f, M, z, q)
