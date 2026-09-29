"""Characteristic-strain sensitivity curves of LISA, LIGO, ET, AION-10, AION-100,
AION-km and AEDGE, with black-hole merger tracks laid over them.

All seven curves digitised from ``GW_exclusion_plot.svg`` into
``aionanim/data/gw_sensitivity/`` (see each CSV's header for the shapes it came from),
drawn together on the source figure's axes, each region shaded down to its
curve and labelled beside it.

The merger tracks are computed, not digitised, for any total mass and
redshift in ``MERGERS``, by aionanim.physics.gw_signals (PhenomA at the
Planck 2018 luminosity distance; it reproduces the source figure's nine
tracks to within 0.003 dex). Dots mark the time left to merger.

``sensitivity_figure()`` returns the matplotlib Figure; saving it is the
caller's business.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

from aionanim.style import (
    GW_DETECTOR_COLORS,
    GW_MERGER_TIME_COLORS,
    GW_REGION_OPACITY,
    PLOT_BACKGROUND,
    PLOT_FOREGROUND,
    merger_color,
)
from aionanim.physics.gw_signals import (
    TIME_MARKERS,
    TRACK_START,
    frequency_before_merger,
    load_sensitivity,
    mass_tex,
    merger_strain,
    merger_track,
    phenom_a_frequencies,
)


LABEL_SIZE = 15
TICK_SIZE = 13

# The source figure's frame.
F_RANGE = (1e-6, 1e4)
H_RANGE = (1e-24, 3e-15)

# name: (CSV stem, label position (f / Hz, h_c)).
DETECTORS = {
    "AEDGE": ("aedge", (1.5e-2, 1.5e-23)),
    "LISA": ("lisa", (2e-4, 1.2e-21)),
    "AION-10": ("aion_10", (9e-2, 2.5e-16)),
    "AION-100": ("aion_100", (2e2, 3.5e-17)),
    "AION-km": ("aion_km", (2e2, 3e-19)),
    "ET": ("et", (1.2e2, 3e-24)),
    "LIGO": ("ligo", (1.8e1, 1.5e-21)),
}

# Merger tracks: (total mass / Msun, redshift, mass ratio m2/m1 <= 1). These
# are the source figure's nine.
MERGERS = [(M, z, 1) for M in (60, 1e4, 1e7) for z in (0.1, 1, 10)]


def draw_merger(ax, M, z, q=1, label_mass=False):
    """Draw one merger track, dotted at the TIME_MARKERS it spans."""
    color = merger_color(z).to_hex()
    f, h = merger_track(M, z, q)
    ax.plot(f, h, color=color, lw=1.4, zorder=3)
    for t, dot in zip(TIME_MARKERS.values(), GW_MERGER_TIME_COLORS):
        if t > TRACK_START:
            continue
        ft = frequency_before_merger(t, M, z, q)
        ax.plot(ft, merger_strain(ft, M, z, q), "o", ms=4, color=dot, mec="none", zorder=4)
    if label_mass:
        # Above the merger's peak, where the track turns over.
        merging = f >= phenom_a_frequencies(M, z, q)["merger"]
        peak = np.flatnonzero(merging)[np.nanargmax(h[merging])]
        ax.text(
            f[peak], h[peak] * 1.5, f"${mass_tex(M)}$", color=PLOT_FOREGROUND,
            fontsize=TICK_SIZE, ha="center", va="bottom", zorder=5,
        )


def merger_legends(ax, redshifts):
    tracks = [
        Line2D([], [], color=merger_color(z).to_hex(), lw=1.4, label=f"$z = {z:g}$")
        for z in sorted(redshifts)
    ]
    dots = [
        Line2D([], [], ls="none", marker="o", ms=5, color=c, mec="none", label=t)
        for t, c in zip(TIME_MARKERS, GW_MERGER_TIME_COLORS)
    ]
    style = dict(frameon=False, labelcolor=PLOT_FOREGROUND, fontsize=TICK_SIZE - 2)
    first = ax.legend(handles=tracks, loc="lower left", **style)
    ax.add_artist(first)
    ax.legend(handles=dots, loc="lower left", bbox_to_anchor=(0.14, 0), handletextpad=0.1, **style)


def dark_axes(ax):
    ax.set_facecolor(PLOT_BACKGROUND)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(PLOT_FOREGROUND)
    ax.tick_params(which="both", colors=PLOT_FOREGROUND, labelsize=TICK_SIZE)
    ax.xaxis.label.set_color(PLOT_FOREGROUND)
    ax.yaxis.label.set_color(PLOT_FOREGROUND)
    ax.xaxis.label.set_size(LABEL_SIZE)
    ax.yaxis.label.set_size(LABEL_SIZE)


def sensitivity_figure():
    fig, ax = plt.subplots(figsize=(8, 5.4))
    fig.set_facecolor(PLOT_BACKGROUND)
    for name, (stem, label_at) in DETECTORS.items():
        f, h = load_sensitivity(stem)
        color = GW_DETECTOR_COLORS[name]
        ax.fill_between(f, h, H_RANGE[1], color=color, alpha=GW_REGION_OPACITY, lw=0)
        ax.plot(f, h, color=color, lw=1.6)
        ax.text(
            *label_at, name, color=color, fontsize=LABEL_SIZE, ha="left", va="center"
        )
    # Each mass is labelled once, beside its nearest (loudest) track.
    nearest = {M: min(z for m, z, _ in MERGERS if m == M) for M, _, _ in MERGERS}
    for M, z, q in MERGERS:
        draw_merger(ax, M, z, q, label_mass=z == nearest[M])
    merger_legends(ax, {z for _, z, _ in MERGERS})
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(*F_RANGE)
    ax.set_ylim(*H_RANGE)
    dark_axes(ax)
    ax.set_xlabel("Frequency / Hz")
    ax.set_ylabel("Characteristic strain")
    fig.tight_layout()
    return fig
