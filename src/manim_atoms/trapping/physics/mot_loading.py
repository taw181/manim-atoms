"""The HiFAIS 3D MOT loading curves, as numbers.

Walker et al., AVS Quantum Sci. 8, 033201 (2026), Fig. 5: the atom number in
the science-chamber MOT against loading time, at four oven temperatures, and
the paper's fit to each -- extracted into manim_atoms/data/hifais_loading/ by
data_scripts/process_hifais_loading.py.

Atom numbers are in units of 1e9, times in ms, rates in 1e9 atoms/s.
"""

import csv

import numpy as np

from manim_atoms.resources import data_path

DATA_DIR = data_path("hifais_loading")

# The atom number the fits stop at: above it the MOT goes unstable and the
# curves flatten out faster than one- or two-body losses can account for.
FIT_CUTOFF = 0.9


def _rows(name):
    with open(DATA_DIR / name) as f:
        return list(csv.DictReader(line for line in f if not line.startswith("#")))


def load_loading_curves():
    """{oven temperature / degC: {"t_ms", "n", "sem"} arrays}, coolest first."""
    curves = {}
    for row in _rows("curves.csv"):
        run = curves.setdefault(int(row["oven_c"]), {"t_ms": [], "n": [], "sem": []})
        for key in run:
            run[key].append(float(row[key]))
    return {t: {k: np.array(v) for k, v in run.items()} for t, run in sorted(curves.items())}


def load_loading_fits():
    """{oven temperature / degC: {"rate", "loss", "onset_ms", "offset",
    "fit_max_ms", ...}}: the fitted model's parameters, coolest first."""
    return {
        int(row["oven_c"]): {k: float(v) for k, v in row.items() if k != "oven_c"}
        for row in sorted(_rows("fits.csv"), key=lambda r: int(r["oven_c"]))
    }


def loading_model(t_ms, fit):
    """The fitted N(t): dN/dt = R - L N from N0 at the onset, N0 before it."""
    dt = np.clip(np.asarray(t_ms, dtype=float) - fit["onset_ms"], 0, None) / 1e3
    n_inf = fit["rate"] / fit["loss"]
    return n_inf + (fit["offset"] - n_inf) * np.exp(-fit["loss"] * dt)
