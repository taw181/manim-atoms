"""Pull the 3D MOT loading curves behind the HiFAIS paper's Fig. 5 inset, and
the chamber renders from its Fig. 1.

Source: T. Walker et al., "A high-flux source of cold strontium with a loading
rate of 4x10^10 atoms/s for open release", AVS Quantum Sci. 8, 033201 (2026),
doi:10.1116/5.0338570 -- the paper's Overleaf repository (``hifais_paper``).

Fig. 5 is the MOT loading curves at four oven temperatures; its inset is the
whole of each run, 0-120 ms, with the fit to the first-order loading model
carried on over it (dashed) and the 0.9e9-atom cutoff it was fitted below.
``scripts/mot3d/loading_rate.py`` makes it from
``data/loading_data/atom_number_data_<T>C_RID<rid>.csv``. This script reads
the same files and refits the same model, with the same starting point,
bounds, weights and cutoff:

    dN/dt = R - L N  from N = N0 at t = t0,  N = N0 before it,

which the paper integrates numerically and this solves in closed form. It
writes

    src/aionanim/data/hifais_loading/curves.csv  -- every point, mean and SEM
    src/aionanim/data/hifais_loading/fits.csv    -- R, L, t0, N0 per run
    src/aionanim/data/images/hifais_chamber_{top,side}.png

The renders are Fig. 1(c) and (d) without their labels (the raster images
embedded in figures/Chamber_InkS_4pane.pdf, pulled out with poppler's
pdfimages), with the white page keyed out so they sit on the
talk's dark background.

    .venv/bin/python data_scripts/process_hifais_loading.py [path/to/hifais_paper]
"""

import csv
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.optimize import curve_fit

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "src" / "aionanim" / "data" / "hifais_loading"
IMAGE_DIR = ROOT / "src" / "aionanim" / "data" / "images"
CITATION = (
    "# From Walker et al., AVS Quantum Sci. 8, 033201 (2026), "
    "doi:10.1116/5.0338570, Fig. 5 (inset)\n"
)

# loading_rate.fit_loading_data's, for max_order=1: R, L, t0, N0
P0 = [40, 20, 3e-3, 0.01]
BOUNDS = ([1, 0, 0, 0], [50, 50, 5e-3, 0.02])
MAX_N = 0.9  # 1e9 atoms: the fit stops at the last point below it

# figures/Chamber_InkS_4pane.pdf: pdfimages' order -> the panel it is
RENDERS = {"side": 0, "top": 2}  # panels (d) and (c)
WHITE = 245  # a pixel this light in every channel is page
FRINGE = 2  # px either side of the page's edge that are feathered
FRINGE_SPAN = 60  # how far below white a fringe pixel is fully opaque


def loading(t, rate, loss, onset, offset):
    """The first-order loading model: a steady rate in, a loss rate out."""
    n_inf = rate / loss if loss > 0 else np.inf
    dt = np.clip(t - onset, 0, None)
    if loss > 0:
        return n_inf + (offset - n_inf) * np.exp(-loss * dt)
    return offset + rate * dt


def read_runs(paper):
    runs = []
    for path in sorted((paper / "data" / "loading_data").glob("atom_number_data_*C_RID*.csv")):
        temp = int(path.stem.split("_")[3].rstrip("C"))
        with open(path) as f:
            rows = list(csv.DictReader(f))
        cols = {k: np.array([float(r[k]) for r in rows])
                for k in ("times", "mean_atom_number", "sem_atom_number")}
        runs.append((temp, cols))
    return sorted(runs, key=lambda run: run[0])


def fit(cols):
    t, n, sem = cols["times"], cols["mean_atom_number"], cols["sem_atom_number"]
    t_max = t[n <= MAX_N].max()
    keep = t <= t_max
    popt, pcov = curve_fit(loading, t[keep], n[keep], sigma=sem[keep],
                           absolute_sigma=False, p0=P0, bounds=BOUNDS)
    return popt, np.sqrt(np.diag(pcov)), t_max


def key_out_page(rgb):
    """RGBA with the white page made transparent, and the anti-aliased pixels
    along its edge made part-transparent. Nothing in a render is pure white
    (the viewports are tinted), so every white patch is page: round the
    outside, and wherever it shows through a gap in the hardware."""
    lightest = rgb.min(axis=2)
    page = lightest >= WHITE
    alpha = np.where(page, 0.0, 1.0)
    fringe = ndimage.binary_dilation(page, iterations=FRINGE) & ~page
    alpha[fringe] = np.clip((255.0 - lightest[fringe]) / FRINGE_SPAN, 0, 1)
    return np.dstack([rgb, (255 * alpha).astype(np.uint8)])


def extract_renders(paper):
    pdf = paper / "figures" / "Chamber_InkS_4pane.pdf"
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["pdfimages", "-png", str(pdf), f"{tmp}/img"], check=True)
        for name, index in RENDERS.items():
            rgb = np.asarray(Image.open(f"{tmp}/img-{index:03d}.png").convert("RGB"))
            out = IMAGE_DIR / f"hifais_chamber_{name}.png"
            Image.fromarray(key_out_page(rgb)).save(out, optimize=True)
            print(f"wrote {out.relative_to(ROOT)}")


def main():
    paper = Path(sys.argv[1] if len(sys.argv) > 1 else Path.home() / "hifais_paper")
    runs = read_runs(paper)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(OUT_DIR / "curves.csv", "w", newline="") as f:
        f.write(
            "# 3D MOT loading curves at four oven temperatures\n" + CITATION
            + "# Source: data/loading_data/atom_number_data_<T>C_RID<rid>.csv\n"
            "# Columns: oven_c, oven temperature / degC; t_ms, loading time; "
            "n, mean atom number / 1e9; sem, its standard error / 1e9\n"
        )
        w = csv.writer(f)
        w.writerow(["oven_c", "t_ms", "n", "sem"])
        for temp, cols in runs:
            for t, n, s in zip(cols["times"], cols["mean_atom_number"], cols["sem_atom_number"]):
                w.writerow([temp, f"{1e3 * t:.4g}", f"{n:.6g}", f"{s:.4g}"])

    with open(OUT_DIR / "fits.csv", "w", newline="") as f:
        f.write(
            "# Fits of dN/dt = R - L N (from N = N0 at t = t0) to the curves "
            "in curves.csv, below N = 0.9e9 as in the paper\n" + CITATION
            + "# Refitted by data_scripts/process_hifais_loading.py as "
            "scripts/mot3d/loading_rate.py does\n"
            "# Columns: oven_c; rate, R / 1e9 s^-1; loss, L / s^-1; onset_ms, t0; "
            "offset, N0 / 1e9; fit_max_ms, the last point fitted; *_err, 1 sigma\n"
        )
        w = csv.writer(f)
        w.writerow(["oven_c", "rate", "rate_err", "loss", "loss_err",
                    "onset_ms", "offset", "fit_max_ms"])
        for temp, cols in runs:
            (rate, loss, onset, offset), err, t_max = fit(cols)
            w.writerow([temp, f"{rate:.5g}", f"{err[0]:.2g}", f"{loss:.5g}",
                        f"{err[1]:.2g}", f"{1e3 * onset:.4g}", f"{offset:.4g}",
                        f"{1e3 * t_max:.4g}"])
            print(f"{temp} C: R = {rate:.2f} +- {err[0]:.2f} e9/s, "
                  f"L = {loss:.2f} +- {err[1]:.2f} /s, t0 = {1e3 * onset:.3f} ms, "
                  f"N0 = {offset:.4f} e9, fitted to {1e3 * t_max:.0f} ms")
    print(f"wrote {OUT_DIR.relative_to(ROOT)}/curves.csv, fits.csv")

    extract_renders(paper)


if __name__ == "__main__":
    main()
