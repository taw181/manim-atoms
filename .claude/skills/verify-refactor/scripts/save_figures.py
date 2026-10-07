"""Save every matplotlib figure the package builds, for before/after comparison.

    uv run python save_figures.py OUTDIR

Fixed dpi and no Software metadata, so the same figure saves to the same
bytes; compare two runs with compare_frames.py. Add a figure here when a
plots/ module gains one.
"""

import sys

import matplotlib

matplotlib.use("Agg")

from manim_atoms.aion.plots import dai_fringes as dai  # noqa: E402
from manim_atoms.aion.plots import gw_sensitivity as gw  # noqa: E402
from manim_atoms.aion.style import HLN_COLOR, LLN_COLOR  # noqa: E402

out = sys.argv[1]
runs = [("lln", LLN_COLOR, "Low laser noise"), ("hln", HLN_COLOR, "High laser noise")]
with dai.deck_fonts():
    lln, hln = dai.load("lln"), dai.load("hln")
    figures = {
        "dai_fringes": dai.fringes_figure(lln, hln),
        "dai_lissajous": dai.lissajous_figure(
            [(lln, LLN_COLOR, "Low laser noise"), (hln, HLN_COLOR, "High laser noise")]),
        "dai_adev": dai.adev_figure(dai.load_adev(), runs, dai.load_sigma()),
        "dai_signals": dai.signals_figure(dai.load_signals()),
        "gw_sensitivity": gw.sensitivity_figure(),
    }
    for name, fig in figures.items():
        fig.savefig(f"{out}/{name}.png", dpi=80, metadata={"Software": None})
print(f"saved {len(figures)} figures to {out}")
