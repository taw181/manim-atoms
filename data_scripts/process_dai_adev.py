"""Pull the Allan deviations behind the DAI paper's Fig. 4c.

Source: C. Baynham et al., "A Prototype Differential Atom Interferometer for
Fundamental Physics", arXiv:2504.09158 -- data and code at
https://doi.org/10.5281/zenodo.19592552 (CC BY 4.0).

The paper's ``figures/Figure 4.ipynb`` computes the overlapping Allan
deviation of each run's differential phase, and the spread of the same over
its Monte Carlo runs at the standard quantum limit, then writes what it plots
to ``figures/Figure_4_data.xlsx``. This script copies that workbook's
``allan_deviation`` sheet, as it stands, to
``src/aionanim/data/dai_fringes/adev.csv``, which is what
``aionanim.plots.dai_fringes`` reads.

It also works out the figure's inset -- the scatter of the mean differential
phase over each whole run, sigma_<dphi>, beside the standard quantum limit --
as the same notebook does (its cells 26-30), from the bootstrapped per-block
scatter in ``intermediate_data/sigma_delta_phi_*.npy``, the shot counts, and
the paper's single-shot SQL of 43.5(1.6) mrad, and writes it to
``src/aionanim/data/dai_fringes/sigma.csv``.

    .venv/bin/python data_scripts/process_dai_adev.py [data_analysis.zip]

With no argument the zip is downloaded from Zenodo into a temporary directory
and its checksum checked.
"""

import csv
import io
import math
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import numpy as np

from process_dai_fringes import OUT_DIR, RIDS, RUNS, SOURCE as SHOTS, check_md5, fetch_zip

SOURCE = "data_analysis/figures/Figure_4_data.xlsx"
SHEET = "allan_deviation"

# The inset's inputs. The npy files are bootstrap samples of the scatter of
# delta phi over one block of shots; "randomised" is the HLN run. The
# residual timeseries are the blocks themselves, which fix the block size.
SIGMA_SAMPLES = {
    "lln": "data_analysis/data/intermediate_data/sigma_delta_phi_nonrandomised.npy",
    "hln": "data_analysis/data/intermediate_data/sigma_delta_phi_randomised.npy",
}
BLOCKS = {
    "lln": "data_analysis/data/2026-01-20-DAI-Analysis/residual_timeseries_LN.csv",
    "hln": "data_analysis/data/2026-01-20-DAI-Analysis/residual_timeseries_HN.csv",
}
SQL_SINGLE_SHOT = (43.5e-3, 1.6e-3)  # rad, the paper's, entered by hand in the notebook

# Just enough of the xlsx format to read one sheet of numbers and inline
# strings, which is all the notebook's openpyxl writes.
NS = {
    "m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
REL = "{%s}id" % NS["r"]


def read_sheet(workbook, name):
    """The sheet's rows, as lists of strings."""
    with zipfile.ZipFile(workbook) as book:
        sheets = ET.fromstring(book.read("xl/workbook.xml"))
        rels = ET.fromstring(book.read("xl/_rels/workbook.xml.rels"))
        rid = next(s.get(REL) for s in sheets.iter(f"{{{NS['m']}}}sheet") if s.get("name") == name)
        target = next(r.get("Target") for r in rels if r.get("Id") == rid)
        sheet = ET.fromstring(book.read("xl/" + target.lstrip("/").removeprefix("xl/")))
    rows = []
    for row in sheet.iter(f"{{{NS['m']}}}row"):
        cells = []
        for cell in row:
            if cell.get("t") == "inlineStr":
                cells.append(cell.find(".//m:t", NS).text)
            else:
                cells.append(cell.find("m:v", NS).text)
        rows.append(cells)
    return rows


def count_rows(archive, name):
    """Data rows in a CSV in the archive, not counting comments or the header."""
    with archive.open(name) as raw:
        lines = io.TextIOWrapper(raw, encoding="utf-8").read().splitlines()
    return sum(1 for line in lines if line and not line.startswith("#")) - 1


def inset(archive):
    """[(label, sigma, error)] in rad: each run's sigma_<dphi> over the whole
    run, then the SQL over the same number of shots per run."""
    shots = {run: count_rows(archive, SHOTS.format(rids=RIDS, key=key))
             for run, (key, _) in RUNS.items()}
    total = sum(shots.values())
    per_block = math.floor(total / sum(count_rows(archive, f) for f in BLOCKS.values()))
    rows = []
    for run in ("hln", "lln"):
        samples = np.load(io.BytesIO(archive.read(SIGMA_SAMPLES[run])))
        mean = np.mean(samples)
        # the notebook takes the lower of the 16/84 percentile distances
        error = abs(np.percentile(samples, 16) - mean)
        blocks = math.sqrt(shots[run] / per_block)
        rows.append((run.upper(), mean / blocks, error / blocks))
    sql, sql_error = SQL_SINGLE_SHOT
    rows.append(("SQL", sql / math.sqrt(total / 2), sql_error / math.sqrt(total / 2)))
    return rows, total, per_block


def main():
    zip_path = Path(sys.argv[1]) if len(sys.argv) > 1 else fetch_zip()
    check_md5(zip_path)

    with zipfile.ZipFile(zip_path) as archive:
        rows = read_sheet(io.BytesIO(archive.read(SOURCE)), SHEET)
        sigmas, total, per_block = inset(archive)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "adev.csv"
    with open(out, "w", newline="") as f:
        f.write(
            "# Overlapping Allan deviation of the differential phase, low (LLN) "
            "and high (HLN) laser noise runs, against the standard quantum limit\n"
            "# From Baynham et al., arXiv:2504.09158, "
            "doi:10.5281/zenodo.19592552 (CC BY 4.0)\n"
            f"# Source file: {SOURCE}, sheet '{SHEET}', as written by "
            "'data_analysis/figures/Figure 4.ipynb'\n"
            "# Columns, all deviations in mrad:\n"
            "#   tau_s, averaging time; adev_{lln,hln}_mrad and their "
            "err_{neg,pos}, each run's Allan deviation and its error bar;\n"
            "#   mc_tau_s, averaging time of the Monte Carlo runs at the SQL; "
            "mc_{68,95}ci_{lower,upper}_mrad, the spread of their deviations;\n"
            "#   sql_scaling_mrad, the SQL per bin of shots falling as "
            "1/sqrt(tau) from the first mc_tau_s\n"
        )
        csv.writer(f).writerows(rows)
    print(f"wrote {out.relative_to(OUT_DIR.parent.parent)}: {len(rows) - 1} averaging times")

    out = OUT_DIR / "sigma.csv"
    with open(out, "w", newline="") as f:
        f.write(
            "# Fig. 4c inset: scatter of the mean differential phase over each whole "
            "run, sigma_<dphi>, against the standard quantum limit\n"
            "# From Baynham et al., arXiv:2504.09158, "
            "doi:10.5281/zenodo.19592552 (CC BY 4.0)\n"
            "# Computed as 'data_analysis/figures/Figure 4.ipynb' does: "
            f"{', '.join(SIGMA_SAMPLES.values())}, over sqrt(shots per run / "
            f"{per_block} shots per block); SQL {SQL_SINGLE_SHOT[0] * 1e3}"
            f"({SQL_SINGLE_SHOT[1] * 1e3}) mrad per shot over sqrt({total} / 2)\n"
            "# Columns: label; sigma_urad and err_urad, the value and its error bar\n"
        )
        writer = csv.writer(f)
        writer.writerow(["label", "sigma_urad", "err_urad"])
        for label, sigma, error in sigmas:
            writer.writerow([label, 1e6 * sigma, 1e6 * error])
    print(f"wrote {out.relative_to(OUT_DIR.parent.parent)}: "
          + ", ".join(f"{label} {1e6 * s:.0f}({1e6 * e:.0f}) urad" for label, s, e in sigmas))


if __name__ == "__main__":
    main()
