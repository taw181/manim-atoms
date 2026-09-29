"""Digitise the AION-10 and AION-100 characteristic-strain curves from
``GW_exclusion_plot.svg`` into ``src/aionanim/data/gw_sensitivity/``.

The two are solid strokes in the SVG's top-left panel, in the same colours
and panel as the AION-km curve already shipped (``aion_km.csv``), so they are
read with its calibration (svgelements page units, y down):

    log10(f/Hz) = -6 + (x - 102.2)/28.065 ;  log10(h_c) = -15 - (y - 50.24)/18.258

and resampled the way ``aion_km.csv`` was: uniform in log f at its spacing
(301 points over its 9.80 decades), by linear interpolation in log-log, which
is exact for a polyline up to the corners it skips (the largest miss is
printed). Run with ``--check`` to put the SVG's AION-km stroke through the same
code and compare it with the shipped ``aion_km.csv``.

    .venv/bin/python data_scripts/digitise_aion_gw.py [--check]
"""

import sys
from pathlib import Path

import numpy as np
import svgelements as se

ROOT = Path(__file__).resolve().parent.parent
SVG = ROOT / "GW_exclusion_plot.svg"
OUT = ROOT / "src/aionanim/data/gw_sensitivity"

STEP = 9.8028 / 300  # aion_km.csv's spacing in log f, dex

CURVES = {  # stem: (stroke id, colour, header lines)
    "aion_10": ("path529-4", "#47b66d", [
        "AION-10 characteristic-strain sensitivity curve (solid green #47b66d)",
        "Source: GW_exclusion_plot.svg, top-left panel, stroke path id 'path529-4' (fill companion 'path528-2').",
        "  Identified as AION-10 from its label (outlined glyphs path544-3/545-6/546-7, #47b66d, read 'AION-10', sitting on",
        "  this line). The SVG has no GGN variant for AION-10.",
        "Scenario: the SVG does not say; most likely the 'goal' AION-10 of Badurina et al., JCAP 05 (2020) 011, table 1",
        "  (L = 10 m, T = 1.4 s, dphi = 1e-4 /sqrt(Hz), n = 1000): the SVG has one AION-10 curve and its ratio to the AION-100 curve",
        "  (3.84 dex, flat over the shared band) fits goal/goal (~3.6 dex from dphi/(n L)), not any pairing with an",
        "  initial scenario (1.0, 3.0 or 4.6 dex).",
        "Caveats: the curve is clipped by the plot frame (h_c = 10^-14.5) at both ends, so only its bottom",
        "  (0.075 - 6.9 Hz, minimum h_c = 7.0e-16 near 0.3 Hz) exists here.",
    ]),
    "aion_100": ("path525-9", "#eb6235", [
        "AION-100 characteristic-strain sensitivity curve (solid orange #eb6235)",
        "Source: GW_exclusion_plot.svg, top-left panel, stroke path id 'path525-9' (fill companion 'path524-9').",
        "  Identified as AION-100 from its label (outlined glyphs path540-7/541-0/542-2, #eb6235, read 'AION-100', sitting",
        "  on this line). The other #eb6235 curve (dashed, 'path527-5') is the GGN variant labelled 'GGN'; not included here.",
        "Scenario: the SVG does not say; most likely the 'goal' AION-100 of Badurina et al., JCAP 05 (2020) 011, table 1",
        "  (L = 100 m, T = 1.4 s, dphi = 1e-5 /sqrt(Hz), n = 40000): see aion_10.csv for the ratio argument.",
        "Caveats: endpoints are where the line meets the plot frame (top edge at low f, right edge near 1e4 Hz).",
    ]),
}

CROSS_CHECK = [
    "Cross-check against the paper: Badurina et al. (2020) fig. 6 (PDF page 17, vector paths read with pymupdf) plots",
    "  the same quantity, characteristic strain, in the same colours, but only above 0.1 Hz. Its AION-km and",
    "  AION-100 curves have the SVG's slope and sit 0.45-0.50 dex (a factor ~sqrt(10)) BELOW the SVG's over",
    "  0.1-1 Hz, and its AION-10 (#00cc00) 1.6 dex below; so the SVG is not a redraw of that figure but a later",
    "  figure of the same programme. These values are the SVG's, on the same footing as every other curve here.",
]


def stroke_vertices(path_id):
    svg = se.SVG.parse(str(SVG))
    for e in svg.elements():
        if isinstance(e, se.Path) and e.id == path_id:
            pts = []
            for seg in e.segments():
                if isinstance(seg, se.Close):
                    continue
                if not isinstance(seg, (se.Move, se.Line)):
                    raise ValueError(f"{path_id}: non-straight segment {type(seg).__name__}")
                pts.append((seg.end.x, seg.end.y))
            p = np.array(pts)
            log_f = -6 + (p[:, 0] - 102.2) / 28.065
            log_h = -15 - (p[:, 1] - 50.24) / 18.258
            return log_f, log_h
    raise KeyError(path_id)


def resample(log_f, log_h):
    keep = np.r_[True, np.diff(log_f) > 1e-9]
    log_f, log_h = log_f[keep], log_h[keep]
    assert np.all(np.diff(log_f) > 0), "stroke is not single-valued in f"
    n = int(round((log_f[-1] - log_f[0]) / STEP)) + 1
    grid = np.linspace(log_f[0], log_f[-1], n)
    out = np.interp(grid, log_f, log_h)
    miss = np.max(np.abs(np.interp(log_f, grid, out) - log_h))
    return grid, out, len(log_f), miss


def write(stem, path_id, color, header):
    grid, log_h, n_raw, miss = resample(*stroke_vertices(path_id))
    lines = [*header,
             "Calibration (svgelements page units, y down): log10(f/Hz) = -6 + (x-102.2)/28.065 ; "
             "log10(h_c) = -15 - (y-50.24)/18.258",
             f"Sampling: the source is a polyline of {n_raw} vertices; resampled to {len(grid)} points uniform in log f "
             f"(aion_km.csv's spacing) by linear",
             f"  interpolation in log-log (max deviation {miss:.1e} dex). "
             "Written by data_scripts/digitise_aion_gw.py.",
             *CROSS_CHECK]
    with open(OUT / f"{stem}.csv", "w") as f:
        f.writelines(f"# {line}\n" for line in lines)
        f.write("f_Hz,h_c\n")
        for x, y in zip(grid, log_h):
            f.write(f"{10**x:.6e},{10**y:.6e}\n")
    print(f"wrote {stem}.csv: {len(grid)} points from {n_raw} vertices, "
          f"{10**grid[0]:.3g}-{10**grid[-1]:.3g} Hz, min h_c {10**log_h.min():.3g}, max miss {miss:.1e} dex")


def check_aion_km():
    """The same code on AION-km's stroke, against the shipped aion_km.csv."""
    grid, log_h, _, _ = resample(*stroke_vertices("path521-7"))
    rows = [l for l in open(OUT / "aion_km.csv") if not l.startswith(("#", "f_Hz"))]
    f, h = np.loadtxt(rows, delimiter=",").T
    ours = np.interp(np.log10(f), grid, log_h)
    print(f"AION-km: {len(grid)} vs {len(f)} points; max |log h_c difference| "
          f"{np.max(np.abs(ours - np.log10(h))):.1e} dex")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check_aion_km()
    for stem, spec in CURVES.items():
        write(stem, *spec)
