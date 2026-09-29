"""Pull the shot-by-shot excitation fractions behind the DAI paper's Fig. 4a,b.

Source: C. Baynham et al., "A Prototype Differential Atom Interferometer for
Fundamental Physics", arXiv:2504.09158 -- data and code at
https://doi.org/10.5281/zenodo.19592552 (CC BY 4.0).

That record is one 135 MB zip. The two files this talk needs are its
``excitation_fraction_corrected_with_phi_hln-lnl-repeat_*_{0,2}.csv``: every
shot of the interleaved low- and high-laser-noise runs, with the applied clock
laser phase step and the excitation fraction of each interferometer. This
script cuts them down to those columns and writes one CSV per run to
``src/aionanim/data/dai_fringes/``, which is what ``aionanim.plots.dai_fringes``
reads.

    .venv/bin/python data_scripts/process_dai_fringes.py [data_analysis.zip]

With no argument the zip is downloaded from Zenodo into a temporary directory
and its checksum checked.
"""

import csv
import hashlib
import io
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

ZENODO_URL = (
    "https://zenodo.org/api/records/19592552/files/data_analysis.zip/content"
)
ZENODO_MD5 = "f2898d155564d1ec9e11cdea17e76de6"

RIDS = "63132_63134_63133_63135_63150_63149_63148_63151_63164_63163_63162_63331_63333_63332"
SOURCE = (
    "data_analysis/data/intermediate_data/"
    "excitation_fraction_corrected_with_phi_hln-lnl-repeat_{rids}_{key}.csv"
)
# The paper's keys are the std. dev., in turns, of the extra random phase put
# on the clock laser for both interferometers at once: 0 is the quiet laser,
# 2 scrambles each shot over several fringes to stand in for a noisy one.
RUNS = {
    "lln": ("0", "Low laser noise (LLN): injected common phase noise std. dev. 0 turns"),
    "hln": ("2", "High laser noise (HLN): injected common phase noise std. dev. 2 turns"),
}

OUT_DIR = Path(__file__).resolve().parent.parent / "src" / "aionanim" / "data" / "dai_fringes"
COLUMNS = ["shot", "t_s", "phi_rad", "excitation_bottom", "excitation_top"]


def fetch_zip():
    path = Path(tempfile.mkdtemp()) / "data_analysis.zip"
    print(f"downloading {ZENODO_URL}")
    urllib.request.urlretrieve(ZENODO_URL, path)
    return path


def check_md5(path):
    digest = hashlib.md5()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            digest.update(block)
    if digest.hexdigest() != ZENODO_MD5:
        sys.exit(f"{path}: md5 {digest.hexdigest()} is not Zenodo's {ZENODO_MD5}")


def read_source(archive, key):
    """The source CSV's comment header and its rows, as dicts."""
    with archive.open(SOURCE.format(rids=RIDS, key=key)) as raw:
        lines = io.TextIOWrapper(raw, encoding="utf-8").read().splitlines()
    header = [line for line in lines if line.startswith("#")]
    rows = list(csv.DictReader(line for line in lines if not line.startswith("#")))
    return header, rows


def main():
    zip_path = Path(sys.argv[1]) if len(sys.argv) > 1 else fetch_zip()
    check_md5(zip_path)

    with zipfile.ZipFile(zip_path) as archive:
        runs = {name: read_source(archive, key) for name, (key, _) in RUNS.items()}

    # The two runs were taken interleaved, shot by shot, so they share one
    # clock: t = 0 at the first shot of either.
    t0 = min(float(r["timestamp"]) for _, rows in runs.values() for r in rows)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (header, rows) in runs.items():
        key, description = RUNS[name]
        out = OUT_DIR / f"{name}.csv"
        with open(out, "w", newline="") as f:
            f.write(f"# {description}\n")
            f.write(
                "# From Baynham et al., arXiv:2504.09158, "
                "doi:10.5281/zenodo.19592552 (CC BY 4.0)\n"
            )
            f.write(f"# Source file: {SOURCE.format(rids=RIDS, key=key)}\n")
            f.write("# Its header:\n")
            f.writelines(f"#   {line.lstrip('# ')}\n" for line in header[:-1])
            f.write(
                "# Columns: shot index; t_s, seconds since the first shot of "
                "either run; phi_rad, applied clock laser phase step;\n"
                "#   excitation_bottom / excitation_top, excitation fraction "
                "of the lower ('forward') and upper ('backward') interferometer\n"
            )
            writer = csv.writer(f)
            writer.writerow(COLUMNS)
            for i, r in enumerate(rows):
                writer.writerow([
                    i,
                    f"{float(r['timestamp']) - t0:.3f}",
                    f"{float(r['phi']):.6f}",
                    f"{float(r['excitation_fraction_forward']):.6f}",
                    f"{float(r['excitation_fraction_backward']):.6f}",
                ])
        print(f"wrote {out.relative_to(OUT_DIR.parent.parent)}: {len(rows)} shots")


if __name__ == "__main__":
    main()
