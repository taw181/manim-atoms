"""Excitation-fraction fringes, the Lissajous ellipse and the imprinted-signal
scans from the AION DAI data.

Recreates Fig. 4a-c and 5a of Baynham et al., arXiv:2504.09158, in the house
palette, from the shots ``data_scripts/process_dai_fringes.py``, the Allan
deviations ``data_scripts/process_dai_adev.py`` and the likelihood scans
``data_scripts/process_dai_signals.py`` extracted into the package data:

- ``fringes_figure``: each interferometer's excitation against the clock
  laser phase step, quiet laser above and noisy laser below. Noise on the
  laser washes the single-interferometer fringes out completely.
- ``lissajous_figure``: upper against lower excitation, shot by shot. The
  noise is common to both, so it only slides each shot along one ellipse,
  whose shape still holds the differential phase. Given one run instead of
  both, it draws the same axes with just that run, for building it up.
- ``adev_figure``: the Allan deviation of the differential phase read off
  each run's ellipse, against averaging time. Both runs average down along
  the standard quantum limit, so the laser noise has cancelled. Given the
  inset's numbers too, it adds the paper's inset: the scatter of the mean
  phase over each whole run, sigma_<dphi>, beside the SQL.
- ``signals_figure``: for each of seven sinusoids, 0.1 mHz to 100 mHz,
  imprinted on the phase by a light shift, the likelihood of a sinusoid
  fitted to the differential phase against trial frequency, over the
  periodogram of the drive: the fit finds each one where it was put.

Both return matplotlib Figures; saving them is the caller's business.
"""

import csv

import matplotlib.pyplot as plt
from matplotlib.collections import PathCollection
import numpy as np

from aionanim.resources import data_path
from aionanim.style import (
    IMPRINTED_SIGNAL_COLOR,
    LOWER_CLOUD_COLOR,
    PLOT_BACKGROUND,
    PLOT_FOREGROUND,
    RECOVERED_SIGNAL_COLOR,
    SQL_BAND_OPACITIES,
    SQL_COLOR,
    UPPER_CLOUD_COLOR,
)

DATA_DIR = data_path("dai_fringes")

# As many shots as the paper plots: more just fills the fringe panels in.
FRINGE_SHOTS = 3000
LISSAJOUS_SHOTS = 2000
# The two runs are drawn in alternating chunks so that neither ellipse sits
# wholly on top of the other.
LISSAJOUS_CHUNK = LISSAJOUS_SHOTS // 10

LABEL_SIZE = 15
TICK_SIZE = 13


def hexed(color):
    return color if isinstance(color, str) else color.to_hex()


def load(run):
    with open(DATA_DIR / f"{run}.csv") as f:
        rows = list(csv.DictReader(line for line in f if not line.startswith("#")))
    return {k: np.array([float(r[k]) for r in rows]) for k in rows[0]}


def load_adev():
    return load("adev")


def load_sigma():
    """{label: (sigma, error)} in urad for the Allan deviation's inset: "HLN",
    "LLN" and "SQL"."""
    with open(DATA_DIR / "sigma.csv") as f:
        rows = csv.DictReader(line for line in f if not line.startswith("#"))
        return {r["label"]: (float(r["sigma_urad"]), float(r["err_urad"])) for r in rows}


def load_signals():
    """{injected Hz: {"fit" | "true": (f_hz, value)}}, in frequency order."""
    with open(DATA_DIR / "signals.csv") as f:
        rows = list(csv.DictReader(line for line in f if not line.startswith("#")))
    runs = {}
    for r in rows:
        curve = runs.setdefault(float(r["injected_hz"]), {}).setdefault(r["curve"], ([], []))
        curve[0].append(float(r["f_hz"]))
        curve[1].append(float(r["value"]))
    return {
        hz: {k: tuple(np.array(v) for v in c) for k, c in curves.items()}
        for hz, curves in sorted(runs.items())
    }


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


def legend(ax, markerscale=3, **kwargs):
    leg = ax.legend(
        frameon=False, labelcolor=PLOT_FOREGROUND, fontsize=TICK_SIZE,
        handletextpad=0.1, markerscale=markerscale, **kwargs,
    )
    # See-through shots get solid keys; shaded bands keep their shade.
    for handle in leg.legend_handles:
        if isinstance(handle, PathCollection):
            handle.set_alpha(1)


def fringes_figure(lln, hln):
    fig, axes = plt.subplots(2, 1, figsize=(6.4, 5.4), sharex=True)
    fig.set_facecolor(PLOT_BACKGROUND)
    for ax, run, title in zip(axes, (lln, hln), ("Low laser noise", "High laser noise")):
        n = slice(FRINGE_SHOTS)
        for key, color, label in (
            ("excitation_bottom", LOWER_CLOUD_COLOR, "Lower"),
            ("excitation_top", UPPER_CLOUD_COLOR, "Upper"),
        ):
            ax.scatter(
                run["phi_rad"][n], 100 * run[key][n], s=6, marker=".",
                color=hexed(color), alpha=0.35, edgecolors="none", label=label,
            )
        dark_axes(ax)
        ax.set_ylim(0, 100)
        ax.set_xlim(0, 2 * np.pi)
        ax.set_ylabel("Excitation / %")
        ax.set_title(title, color=PLOT_FOREGROUND, fontsize=LABEL_SIZE, loc="left")
    legend(axes[0], loc="upper right", bbox_to_anchor=(1.0, 1.25), ncols=2)
    axes[1].set_xticks([0, np.pi, 2 * np.pi], ["0", r"$\pi$", r"$2\pi$"])
    axes[1].set_xlabel("Clock laser phase step / rad")
    fig.tight_layout()
    return fig


def lissajous_figure(runs):
    """Upper against lower excitation; runs is a list of (data, color, label)."""
    fig, ax = plt.subplots(figsize=(5.4, 5.4))
    fig.set_facecolor(PLOT_BACKGROUND)
    labelled = set()
    for start in range(0, LISSAJOUS_SHOTS, LISSAJOUS_CHUNK):
        n = slice(start, start + LISSAJOUS_CHUNK)
        for run, color, label in runs:
            ax.scatter(
                100 * run["excitation_bottom"][n], 100 * run["excitation_top"][n],
                s=6, marker=".", color=hexed(color), edgecolors="none",
                label=None if label in labelled else label,
            )
            labelled.add(label)
    dark_axes(ax)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_aspect("equal")
    ax.set_xlabel("Lower interferometer excitation / %")
    ax.set_ylabel("Upper interferometer excitation / %")
    legend(ax, loc="upper left")
    fig.tight_layout()
    return fig


# The inset, upper right, clear of the data falling from upper left to
# lower right. Its rows are the paper's, fixed across the build-up steps: a
# row is only filled and labelled once its run is on the main plot.
ADEV_INSET = [0.68, 0.76, 0.29, 0.20]  # in the main axes' fractions
ADEV_INSET_ROWS = {"hln": (1, "High"), "lln": (2, "Low"), "sql": (3, "SQL")}
ADEV_INSET_XLIM = (235, 300)  # urad


def adev_inset(ax, sigma, runs):
    """sigma_<dphi> of each run in ``runs`` beside the SQL's, as the paper's inset."""
    inset = ax.inset_axes(ADEV_INSET)
    shown = [("sql", PLOT_FOREGROUND)] + [(key, color) for key, color, _ in runs]
    for key, color in shown:
        value, error = sigma[key.upper()]
        inset.errorbar(value, ADEV_INSET_ROWS[key][0], xerr=error, fmt="o", ms=6,
                       elinewidth=1.5, capsize=0, color=hexed(color))
    rows = sorted(ADEV_INSET_ROWS[key] for key, _ in shown)
    inset.set_yticks([y for y, _ in rows], [label for _, label in rows])
    inset.set_ylim(0.5, 3.5)
    inset.set_xlim(*ADEV_INSET_XLIM)
    inset.set_xticks([240, 260, 280, 300])
    dark_axes(inset)
    inset.set_xlabel(r"$\sigma_{\langle\delta\phi\rangle}$ / $\mu$rad")
    return inset


def adev_figure(adev, runs, sigma=None):
    """Allan deviation against averaging time; runs is a list of (key, color, label).

    The key picks a run's columns ("lln" or "hln"). The SQL is always drawn,
    so an empty list gives the bare limit to build up from. With ``sigma``
    (load_sigma()) the inset is drawn too, with the same runs in it.
    """
    fig, ax = plt.subplots(figsize=(6.4, 5.4))
    fig.set_facecolor(PLOT_BACKGROUND)
    tau = adev["mc_tau_s"]
    color = hexed(SQL_COLOR)
    for ci, opacity in zip(("68", "95"), SQL_BAND_OPACITIES):
        ax.fill_between(
            tau, adev[f"mc_{ci}ci_lower_mrad"], adev[f"mc_{ci}ci_upper_mrad"],
            color=color, alpha=opacity, lw=0, label=f"SQL, {ci}%",
        )
    ax.plot(
        tau, adev["sql_scaling_mrad"], ":", color=PLOT_FOREGROUND, lw=1.5,
        label=r"SQL $\propto 1/\sqrt{\tau}$",
    )
    for key, run_color, label in runs:
        ax.errorbar(
            adev["tau_s"], adev[f"adev_{key}_mrad"],
            yerr=[adev[f"adev_{key}_err_neg_mrad"], adev[f"adev_{key}_err_pos_mrad"]],
            ls="none", marker="o", ms=6, capsize=0, elinewidth=1.5,
            color=hexed(run_color), label=label,
        )
    ax.set_xscale("log")
    ax.set_yscale("log")
    # The paper's limits, fixed so the build-up steps share one set of axes.
    ax.set_xlim(7e2, 7e4)
    ax.set_ylim(0.1, 5)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:g}"))
    ax.yaxis.set_minor_formatter(plt.NullFormatter())
    dark_axes(ax)
    ax.set_xlabel("Measurement time / s")
    ax.set_ylabel(r"Allan deviation of $\delta\phi$ / mrad")
    legend(ax, loc="lower left", markerscale=1)
    if sigma is not None:
        adev_inset(ax, sigma, runs)
    fig.tight_layout()
    return fig


# Fig. 5a's tick spacing round each injected frequency, in Hz: the paper's.
SIGNAL_TICK_STEPS = {
    1e-4: 25e-6, 3e-4: 30e-6, 1e-3: 0.1e-3, 3e-3: 0.05e-3,
    1e-2: 0.1e-3, 3e-2: 0.05e-3, 1e-1: 0.05e-3,
}
BREAK_MARK = 0.03  # half-length of the slashes where the axis is cut, in axes widths
# Seven panels across a slide: a wide figure, scaled down, so bigger text.
SIGNALS_LABEL_SIZE = 22
SIGNALS_TICK_SIZE = 18


def frequency_unit(hz):
    """(scale, unit) to show frequencies near hz in: uHz below half a mHz."""
    return (1e6, r"$\mu$Hz") if hz < 5e-4 else (1e3, "mHz")


def signals_figure(runs):
    """One panel per injected frequency, from load_signals()."""
    fig, axes = plt.subplots(
        1, len(runs), figsize=(13, 6.4), sharey=True, gridspec_kw=dict(wspace=0.12),
    )
    fig.set_facecolor(PLOT_BACKGROUND)
    for i, (ax, (hz, curves)) in enumerate(zip(axes, runs.items())):
        # See-through, so a width label can run on over the next panel.
        ax.patch.set_alpha(0)
        f_fit, fit = curves["fit"]
        (recovered,) = ax.plot(
            f_fit, fit, "-", color=hexed(RECOVERED_SIGNAL_COLOR), lw=1.8,
            label="Fitted signal",
        )
        (imprinted,) = ax.plot(
            *curves["true"], "--", color=hexed(IMPRINTED_SIGNAL_COLOR), lw=1.8,
            label="Imprinted signal",
        )
        ax.set_xlim(f_fit[0], f_fit[-1])

        # The fit's full width at half maximum, marked across the peak.
        above = f_fit[fit >= 0.5]
        fwhm = above[-1] - above[0]
        ax.plot([above[0], above[-1]], [0.5, 0.5], color=PLOT_FOREGROUND, lw=1.5)
        ax.text(
            above[-1] + 0.5 * fwhm, 0.5, f"{1e6 * fwhm:.1f} $\\mu$Hz",
            color=PLOT_FOREGROUND, fontsize=SIGNALS_TICK_SIZE, ha="left", va="center",
        )

        dark_axes(ax)
        ax.tick_params(labelsize=SIGNALS_TICK_SIZE)
        scale, unit = frequency_unit(hz)
        step = SIGNAL_TICK_STEPS[hz]
        ax.set_xticks([hz - step, hz, hz + step])
        # Only the injected frequency is labelled: the outer ticks' labels
        # run into the next panel's at slide size, and the widths give scale.
        ax.set_xticklabels(["", f"{scale * hz:g}", ""])
        ax.set_xlabel(unit, fontsize=SIGNALS_LABEL_SIZE)
        ax.set_yticks([])
        if i:
            ax.spines["left"].set_visible(False)
        # The frequency axis is cut between panels: a slash at each cut end.
        ends = ([1] if i == 0 else [0] if i == len(runs) - 1 else [0, 1])
        for x in ends:
            ax.plot(
                [x - BREAK_MARK, x + BREAK_MARK], [-BREAK_MARK * 3, BREAK_MARK * 3],
                transform=ax.transAxes, color=PLOT_FOREGROUND, lw=1, clip_on=False,
            )
    axes[0].set_ylim(0, 1.5)
    axes[0].set_ylabel("Signal likelihood / a.u.", fontsize=SIGNALS_LABEL_SIZE)
    # Fixed margins: tight_layout leaves the figure legend and label out.
    # The last width label runs past its panel, hence the right margin.
    fig.subplots_adjust(left=0.05, right=0.94, bottom=0.2, top=0.97)
    fig.align_xlabels(axes)
    fig.supxlabel("Frequency", color=PLOT_FOREGROUND, fontsize=SIGNALS_LABEL_SIZE, y=0.02)
    fig.legend(
        handles=[recovered, imprinted], loc="upper right", bbox_to_anchor=(0.97, 0.97),
        frameon=False, labelcolor=PLOT_FOREGROUND, fontsize=SIGNALS_TICK_SIZE,
    )
    return fig
