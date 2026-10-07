"""Holography numbers: a phase mask on an SLM and the focal plane it makes.

No manim. Everything is on a square grid of pixels over the SLM's aperture,
the unit disc: pupil_grid gives the coordinates, zernike the aberration
modes, grating_phase and lens_phase the two masks every hologram is built
from, spot_phase the mask for several spots at once, far_field the
focal-plane intensity of any mask, gs_step and wgs_step one iteration of
the Gerchberg-Saxton algorithm and of its weighted version, and uniformity
and strehl the two numbers a hologram is judged by.

Spots are given in units of the diffraction limit: a spot at (kx, ky) is
made by a grating with kx periods across the aperture in x and ky in y.
"""

from math import factorial

import numpy as np

# The modes of the first five radial orders, by (n, m).
ZERNIKE_NAMES = {
    (0, 0): "piston",
    (1, -1): "tilt", (1, 1): "tip",
    (2, -2): "oblique astigmatism", (2, 0): "defocus", (2, 2): "astigmatism",
    (3, -3): "trefoil", (3, -1): "vertical coma", (3, 1): "coma", (3, 3): "oblique trefoil",
    (4, -4): "oblique quadrafoil", (4, -2): "oblique secondary astigmatism",
    (4, 0): "spherical", (4, 2): "secondary astigmatism", (4, 4): "quadrafoil",
}


def pupil_grid(n):
    """(x, y, rho, theta) at the pixel centres of an n x n grid over the
    square [-1, 1]^2, row 0 at the top (y = +1) as an image has it."""
    c = (np.arange(n) + 0.5) / n * 2 - 1
    x, y = np.meshgrid(c, -c)
    return x, y, np.hypot(x, y), np.arctan2(y, x)


def illumination(rho, waist=None):
    """The light's amplitude on the SLM: uniform over the unit disc and zero
    outside it, or a Gaussian of 1/e^2 intensity radius ``waist`` cut off by it."""
    inside = (np.asarray(rho) <= 1).astype(float)
    return inside if waist is None else inside * np.exp(-(rho / waist) ** 2)


def osa_to_nm(j):
    """The radial order n and azimuthal order m of the mode with OSA/ANSI
    index j, which counts along the rows of the Zernike pyramid: j = 0 is
    piston, 1 and 2 the tilts, 3 to 5 the row with defocus in the middle."""
    n = int(np.ceil((-3 + np.sqrt(9 + 8 * j)) / 2))
    return n, 2 * j - n * (n + 2)


def zernike(n, m, rho, theta):
    """The Zernike polynomial Z_n^m, normalised to unit mean square over the
    unit disc: cosine modes for m > 0, sine modes for m < 0."""
    if (n - abs(m)) % 2 or abs(m) > n:
        raise ValueError(f"no Zernike mode with n = {n}, m = {m}")
    rho = np.asarray(rho, dtype=float)
    k = abs(m)
    radial = sum(
        (-1) ** s * factorial(n - s)
        / (factorial(s) * factorial((n + k) // 2 - s) * factorial((n - k) // 2 - s))
        * rho ** (n - 2 * s)
        for s in range((n - k) // 2 + 1)
    )
    if m == 0:
        return np.sqrt(n + 1) * radial
    angular = np.cos(k * theta) if m > 0 else np.sin(k * theta)
    return np.sqrt(2 * (n + 1)) * radial * angular


def grating_phase(x, y, kx, ky):
    """A blazed grating with kx periods across the aperture in x and ky in y.
    It steers the spot to (kx, ky) diffraction limits off the axis."""
    return np.pi * (kx * x + ky * y)


def lens_phase(rho, waves):
    """A lens: ``waves`` of extra path at the edge of the aperture. It moves
    the focus along the axis, so in the focal plane the spot blurs."""
    return 2 * np.pi * waves * np.asarray(rho) ** 2


def spot_phase(x, y, spots, phases=None, weights=None):
    """The mask for several spots at once: the phase of the sum of the fields
    that would each make one of them, each with its own phase offset and,
    if given, its own weight (0 for a spot switched off)."""
    spots = np.atleast_2d(np.asarray(spots, dtype=float))
    phases = np.zeros(len(spots)) if phases is None else np.asarray(phases, dtype=float)
    weights = np.ones(len(spots)) if weights is None else np.asarray(weights, dtype=float)
    field = sum(w * np.exp(1j * (grating_phase(x, y, kx, ky) + p))
                for (kx, ky), p, w in zip(spots, phases, weights))
    return np.angle(field)


def far_field(phase, amplitude, pad=4):
    """The focal-plane intensity of a mask, on a grid ``pad`` times finer than
    the diffraction limit, scaled so that a flat mask peaks at 1.

    The array is pad * n pixels square with the optical axis at its centre
    pixel; spot_pixel says where a spot lands in it."""
    n = phase.shape[0]
    size = pad * n
    field = np.zeros((size, size), dtype=complex)
    lo = (size - n) // 2
    field[lo:lo + n, lo:lo + n] = amplitude * np.exp(1j * phase)
    out = np.fft.fftshift(np.fft.fft2(np.fft.ifftshift(field)))
    return np.abs(out) ** 2 / amplitude.sum() ** 2


def spot_pixel(spot, n, pad=4):
    """(row, column) of the spot at (kx, ky) in far_field's array."""
    kx, ky = spot
    centre = pad * n // 2
    return int(round(centre - ky * pad)), int(round(centre + kx * pad))


def spot_fields(phase, amplitude, x, y, spots):
    """The complex field a mask puts on each spot, as a share of what a
    grating aimed at that spot alone would put there."""
    spots = np.atleast_2d(np.asarray(spots, dtype=float))
    lit = amplitude * np.exp(1j * phase)
    return np.array([(lit * np.exp(-1j * grating_phase(x, y, kx, ky))).sum()
                     for kx, ky in spots]) / amplitude.sum()


def wgs_step(phase, weights, amplitude, x, y, spots, weighted=True):
    """One iteration of weighted Gerchberg-Saxton.

    Looks at the field the mask puts on each spot, raises the weight of the
    spots that came out dim, and builds the next mask from the weighted sum
    of the spots' fields, each keeping the phase it had. Returns (the next
    mask, the next weights, the intensity the mask it was given put on each
    spot). A spot the mask leaves dark keeps its weight."""
    spots = np.atleast_2d(np.asarray(spots, dtype=float))
    weights = np.asarray(weights, dtype=float)
    v = spot_fields(phase, amplitude, x, y, spots)
    mag = np.abs(v)
    if weighted:
        lit = mag > 1e-12
        weights = np.where(lit, weights * mag[lit].mean() / np.where(lit, mag, 1.0), weights) \
            if lit.any() else weights
    field = sum(w * np.exp(1j * (grating_phase(x, y, kx, ky) + np.angle(f)))
                for w, (kx, ky), f in zip(weights, spots, v))
    return np.angle(field), weights, mag ** 2


def gs_step(phase, amplitude, x, y, spots):
    """One iteration of plain Gerchberg-Saxton: every spot weighted alike.
    Returns (the next mask, the intensity the mask it was given put on each spot)."""
    spots = np.atleast_2d(np.asarray(spots, dtype=float))
    new, _, intensity = wgs_step(phase, np.ones(len(spots)), amplitude, x, y, spots,
                                 weighted=False)
    return new, intensity


def uniformity(intensities):
    """1 - (max - min) / (max + min): 1 when every spot is as bright as the rest."""
    i = np.asarray(intensities, dtype=float)
    return 1 - (i.max() - i.min()) / (i.max() + i.min())


def strehl(phase_error, amplitude):
    """The focal spot's peak with a wavefront error, as a share of its peak
    without one: |<exp(i phi)>|^2 over the illuminated aperture."""
    return np.abs((amplitude * np.exp(1j * phase_error)).sum()) ** 2 / amplitude.sum() ** 2
