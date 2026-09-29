# /// script
# requires-python = ">=3.11"
# dependencies = ["pymupdf", "numpy"]
# ///
"""Digitise AION's projected sensitivity to scalar ULDM coupled to photons.

Source: L. Badurina et al., "AION: an atom interferometer observatory and
network", JCAP 05 (2020) 011, arXiv:1911.11755 -- Figure 3, middle panel:
the linear photon coupling |d_e| against the scalar's mass m_phi. The figure
is vector graphics in the journal PDF (page 13, journal page 10), so the
curves are read straight off the PDF's paths rather than traced from pixels.

Writes src/aionanim/data/uldm_sensitivity/*.csv, which
aionanim.physics.uldm_sensitivity reads:

- one per scenario: the SOLID curve only (the paper: "the solid line shows
  the sensitivity above 0.3 Hz, while the dotted line shows the sensitivity
  that could be gained by extending the frequency range down to 0.1 Hz"),
  every path of that stroke colour joined in order of mass;
- excluded.csv: the lower edge of the grey region, i.e. the union of the
  three grey fills (torsion balances, MICROSCOPE, atomic clocks), found by
  cutting each fill with vertical lines and keeping the lowest crossing.

pymupdf is not a dependency of the project, so run it with uv's inline
script metadata:

    uv run data_scripts/digitise_uldm_sensitivity.py [paper.pdf]
"""

import sys
from pathlib import Path

import numpy as np
import pymupdf

PDF = Path.home() / (
    "Zotero/storage/NRJ5SW5A/"
    "Badurina et al. - 2020 - AION an atom interferometer observatory and network.pdf"
)
PAGE = 12  # 0-based: PDF page 13
OUT_DIR = Path(__file__).resolve().parents[1] / "src/aionanim/data/uldm_sensitivity"

# --- calibration: the panel's frame and tick marks, PDF points, y down ------
# Bottom-axis ticks every 12.3589 pt from the frame's left edge (x = 256.73,
# m = 1e-19 eV) to its right edge (367.96, 1e-10 eV); the labels 10^-18 ..
# 10^-10 sit under every other one. Left-axis ticks every 4.7582 pt from the
# frame's bottom (171.36, d_e = 1e-16) to its top (90.47, 1e1). Checked
# against the top axis, f_phi = m_phi / h: its 1 Hz tick at x = 313.78 maps to
# 10^-14.3836 eV, and h * 1 Hz = 10^-14.3835 eV.
X0, X1, LOG_M0, LOG_M1 = 256.73, 367.96, -19.0, -10.0
Y0, Y1, LOG_D0, LOG_D1 = 171.36, 90.47, -16.0, 1.0
CALIBRATION = (
    f"log10(m_phi/eV) = {LOG_M0:g} + (x - {X0})/{(X1 - X0) / (LOG_M1 - LOG_M0):.4f} ;  "
    f"log10|d_e| = {LOG_D0:g} - (y - {Y0})/{(Y0 - Y1) / (LOG_D1 - LOG_D0):.4f}"
)


def log_m(x):
    return LOG_M0 + (np.asarray(x) - X0) * (LOG_M1 - LOG_M0) / (X1 - X0)


def log_d(y):
    return LOG_D0 + (np.asarray(y) - Y0) * (LOG_D1 - LOG_D0) / (Y1 - Y0)


# stem: (label, stroke colour in the PDF, as 0-255 RGB)
CURVES = {
    "aion10_initial": ("AION-10 (initial)", (237, 51, 119)),
    "aion10_goal": ("AION-10 (goal)", (237, 119, 51)),
    "aion100_initial": ("AION-100 (initial)", (51, 186, 237)),
    "aion100_goal": ("AION-100 (goal)", (0, 119, 186)),
    "aion_km": ("AION-km", (40, 137, 16)),
    "aedge": ("AEDGE", (168, 70, 200)),
}
GREY = (214, 214, 214)


def rgb(c):
    return tuple(round(255 * v) for v in c) if c else None


def in_panel(rect):
    return rect.x1 > X0 and rect.x0 < X1 and rect.y1 > Y1 and rect.y0 < Y0


def polyline(drawing):
    """The path's vertices; every item is a straight segment ('l') here."""
    items = drawing["items"]
    assert all(it[0] == "l" for it in items), "expected straight segments only"
    return np.array([(it[1].x, it[1].y) for it in items] + [(items[-1][2].x, items[-1][2].y)])


def near(a, b, tol=2):
    return a is not None and all(abs(p - q) <= tol for p, q in zip(a, b))


def bottom_edge(polygon, xs):
    """For each x, the lowest (largest-y) crossing of the closed polygon."""
    p = np.vstack([polygon, polygon[:1]])
    out = np.full(len(xs), -np.inf)
    for (xa, ya), (xb, yb) in zip(p[:-1], p[1:]):
        if xa == xb:
            continue
        lo, hi = min(xa, xb), max(xa, xb)
        sel = (xs >= lo) & (xs <= hi)
        y = ya + (xs[sel] - xa) * (yb - ya) / (xb - xa)
        out[sel] = np.maximum(out[sel], y)
    return out


def rdp(points, tol):
    """Ramer-Douglas-Peucker: the vertices that keep the polyline within tol."""
    keep = np.zeros(len(points), bool)
    keep[[0, -1]] = True
    stack = [(0, len(points) - 1)]
    while stack:
        i, j = stack.pop()
        if j <= i + 1:
            continue
        a, b = points[i], points[j]
        d = b - a
        seg = points[i + 1:j] - a
        dist = np.abs(d[0] * seg[:, 1] - d[1] * seg[:, 0]) / np.hypot(*d)
        k = int(np.argmax(dist))
        if dist[k] > tol:
            keep[i + 1 + k] = True
            stack += [(i, i + 1 + k), (i + 1 + k, j)]
    return points[keep]


def write(stem, header, x, y):
    lines = [f"# {h}" for h in header] + ["m_eV,d_e"]
    lines += [f"{10 ** a:.6e},{10 ** b:.6e}" for a, b in zip(log_m(x), log_d(y))]
    (OUT_DIR / f"{stem}.csv").write_text("\n".join(lines) + "\n")
    print(f"{stem}: {len(x)} points, m {10 ** log_m(x[0]):.3g}..{10 ** log_m(x[-1]):.3g} eV")


SOURCE = (
    "Source: Badurina et al., JCAP 05 (2020) 011 (arXiv:1911.11755), Fig. 3 middle panel "
    "(photon coupling |d_e| vs scalar DM mass m_phi); vector paths of the journal PDF, page 13"
)


def main(pdf=PDF):
    drawings = pymupdf.open(pdf)[PAGE].get_drawings()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for stem, (label, colour) in CURVES.items():
        picked = [
            (i, d) for i, d in enumerate(drawings)
            if d["type"] == "s" and in_panel(d["rect"])
            and near(rgb(d["color"]), colour) and not d["dashes"].startswith("[ .")
        ]
        pts = np.vstack([polyline(d) for _, d in sorted(picked, key=lambda p: p[1]["rect"].x0)])
        # joined end to start, so drop the repeated vertex at each junction
        pts = pts[np.r_[True, np.any(np.abs(np.diff(pts, axis=0)) > 1e-3, axis=1)]]
        assert np.all(np.diff(pts[:, 0]) >= -1e-6), f"{stem} doubles back in x"
        write(stem, [
            f"{label} projected sensitivity to scalar ULDM coupled to photons: |d_e| at SNR 1 "
            "after 1e8 s, the SOLID curve (f_phi >= 0.3 Hz)",
            SOURCE + f"; stroke colour rgb{colour}, drawings {[i for i, _ in picked]} "
            "(solid paths, joined in order of mass).",
            "Left out: the dotted continuation down to 0.1 Hz. Endpoints where the curve meets "
            "the frame (d_e = 10) are the frame, not the curve's end.",
            "Calibration (PDF points, y down; frame 256.73..367.96 x 171.36..90.47, from the tick marks):",
            f"  {CALIBRATION}",
            "Points: the PDF polyline's own vertices, exact (no resampling or fitting); linear in "
            "log-log between them. Accuracy ~0.01 dex (the vector coordinates are to 0.01 pt).",
        ], pts[:, 0], pts[:, 1])

    fills = [
        (i, polyline(d)) for i, d in enumerate(drawings)
        if d["type"] == "fs" and in_panel(d["rect"]) and near(rgb(d["fill"]), GREY)
    ]
    xs = np.linspace(X0, X1, 5562)  # every 0.02 pt
    for _, poly in fills:  # and each vertex, just either side of it
        xs = np.concatenate([xs, poly[:, 0] - 1e-4, poly[:, 0] + 1e-4])
    xs = np.unique(xs[(xs >= X0) & (xs <= X1)])
    edge = np.max([bottom_edge(poly, xs) for _, poly in fills], axis=0)
    ok = np.isfinite(edge)
    xs, edge = xs[ok], np.maximum(edge[ok], Y1)
    points = rdp(np.column_stack([log_m(xs), log_d(edge)]), 0.002)
    write("excluded", [
        "Lower edge of the region already excluded for scalar ULDM coupled to photons (grey in the "
        "source): |d_e| above this is ruled out",
        SOURCE + f"; the union of the grey fills, drawings {[i for i, _ in fills]} "
        "(torsion balances, MICROSCOPE, atomic clocks).",
        "Built: each fill cut every 0.02 pt (and either side of every vertex) by a vertical line, "
        "keeping the lowest crossing of any fill; clipped to the frame (1e-19..1e-10 eV).",
        "Below ~2e-18 eV the edge is the atomic-clock fill's saw-tooth lower edge, kept as drawn; "
        "above, MICROSCOPE's solid line up to ~7e-13 eV, then the torsion balances' dashed one.",
        "Calibration (PDF points, y down; frame 256.73..367.96 x 171.36..90.47, from the tick marks):",
        f"  {CALIBRATION}",
        "Decimation: Ramer-Douglas-Peucker at 0.002 dex on the exact edge; linear in log-log.",
    ], (points[:, 0] - LOG_M0) * (X1 - X0) / (LOG_M1 - LOG_M0) + X0,
        (points[:, 1] - LOG_D0) * (Y1 - Y0) / (LOG_D1 - LOG_D0) + Y0)


if __name__ == "__main__":
    main(*sys.argv[1:])
