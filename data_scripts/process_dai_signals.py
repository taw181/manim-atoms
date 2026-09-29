"""Pull the injected-signal likelihood scans behind the DAI paper's Fig. 5a.

Source: C. Baynham et al., "A Prototype Differential Atom Interferometer for
Fundamental Physics", arXiv:2504.09158 -- data and code at
https://doi.org/10.5281/zenodo.19592552 (CC BY 4.0).

Each of seven runs had a sinusoidal phase, 0.1 mHz to 100 mHz, imprinted on
one interferometer by a light shift. The paper's ``figures/Figure 5a.ipynb``
plots, per run, the likelihood of a sinusoid fitted to the differential phase
against trial frequency (the last, finest iteration of
``data/intermediate_data/signal_fitting_results_by_frequency.csv``), over the
Lomb-Scargle periodogram of the light-shift drive itself
(``data/precomputed_true_signals/signal_extraction_*.npz``). This script does
the same reduction -- the window of +-5 FWHM round each peak, each curve
normalised to unit height -- and writes both curves to
``src/aionanim/data/dai_fringes/signals.csv``, which is what
``aionanim.plots.dai_fringes`` reads.

The notebook's own ``Figure_5a_data.xlsx`` isn't used: it writes the
periodogram against the fit's frequencies rather than its own.

    .venv/bin/python data_scripts/process_dai_signals.py [data_analysis.zip]

With no argument the zip is downloaded from Zenodo into a temporary directory
and its checksum checked.
"""

import csv
import io
import sys
import zipfile
from pathlib import Path

import numpy as np

from process_dai_fringes import OUT_DIR, check_md5, fetch_zip

FITS = "data_analysis/data/intermediate_data/signal_fitting_results_by_frequency.csv"
TRUE = "data_analysis/data/precomputed_true_signals/signal_extraction_{stem}.npz"
WINDOW_FWHMS = 5  # the notebook's half-width of each panel


def read_fits(archive):
    """Each run's final-iteration scan, by source file: (injected Hz, rows)."""
    with archive.open(FITS) as raw:
        rows = list(csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8")))
    runs = {}
    for row in rows:
        runs.setdefault(row["dataset_filename"], []).append(row)
    out = {}
    for name, run in runs.items():
        last = max(int(r["iteration"]) for r in run)
        run = [r for r in run if int(r["iteration"]) == last]
        cols = {k: np.array([float(r[k]) for r in run]) for k in ("f_hz", "fit_A_rad", "fit_logL")}
        order = np.argsort(cols["f_hz"])
        out[name] = (float(run[0]["dataset_frequency_hz"]), {k: v[order] for k, v in cols.items()})
    return out


def window(scan):
    """The notebook's panel: +-5 FWHM of logL round the best-fit amplitude."""
    f, logl = scan["f_hz"], scan["fit_logL"]
    peak = np.argmax(scan["fit_A_rad"])
    half = logl[peak] - (logl[peak] - logl.min()) / 2
    above = f[logl >= half]
    fwhm = above.max() - above.min() if len(above) > 1 else 0.1 * (f.max() - f.min())
    return f[peak] - WINDOW_FWHMS * fwhm, f[peak] + WINDOW_FWHMS * fwhm


def main():
    zip_path = Path(sys.argv[1]) if len(sys.argv) > 1 else fetch_zip()
    check_md5(zip_path)

    rows = []
    with zipfile.ZipFile(zip_path) as archive:
        for name, (injected, scan) in sorted(read_fits(archive).items(), key=lambda kv: kv[1][0]):
            lo, hi = window(scan)
            keep = (scan["f_hz"] >= lo) & (scan["f_hz"] <= hi)
            f, logl = scan["f_hz"][keep], scan["fit_logL"][keep]
            logl = (logl - logl.min()) / (logl - logl.min()).max()
            rows += [(injected, "fit", fi, li) for fi, li in zip(f, logl)]

            true = np.load(io.BytesIO(archive.read(TRUE.format(stem=Path(name).stem))))
            f, power = true["freqs"], true["pgram"]
            keep = (f >= lo) & (f <= hi)
            order = np.argsort(f[keep])
            f, power = f[keep][order], power[keep][order]
            rows += [(injected, "true", fi, pi) for fi, pi in zip(f, power / power.max())]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "signals.csv"
    with open(out, "w", newline="") as f:
        f.write(
            "# Recovery of a sinusoidal phase imprinted by a light shift, one run "
            "per injected frequency\n"
            "# From Baynham et al., arXiv:2504.09158, "
            "doi:10.5281/zenodo.19592552 (CC BY 4.0), Fig. 5a\n"
            f"# Sources: {FITS} (final iteration), and {TRUE.format(stem='*')}, "
            "reduced as 'data_analysis/figures/Figure 5a.ipynb' does\n"
            "# Columns: injected_hz, the run's nominal frequency; curve, 'fit' for "
            "the likelihood of a sinusoid fitted to the differential phase\n"
            "#   (logL above its minimum) or 'true' for the periodogram of the "
            "light-shift drive; f_hz, trial frequency; value, normalised to unit peak\n"
        )
        writer = csv.writer(f)
        writer.writerow(["injected_hz", "curve", "f_hz", "value"])
        writer.writerows((f"{i:g}", c, repr(float(fr)), f"{v:.6g}") for i, c, fr, v in rows)
    print(f"wrote {out.relative_to(OUT_DIR.parent.parent)}: {len(rows)} points")


if __name__ == "__main__":
    main()
