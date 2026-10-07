---
name: data-plots
description: Plot measured or computed data in manim-atoms — a plot drawn in manim (log-log axes, sensitivity curves, shots arriving one by one on a scatter, loading curves with fits) or a static matplotlib figure for a slide — and add, regenerate or cite the datasets behind them. Use it whenever a scene or slide shows data, axes or curves, or when a CSV, image or video under src/manim_atoms/data is added or changed. Use it with the base manim-atoms skill.
---

# Data and plots

Read the base `manim-atoms` skill first. Data appears in two forms:
- **a plot drawn in manim**, when its points have to arrive, be lit or be
  annotated in time;
- **a matplotlib figure**, when the plot is a still on a slide.

Both read the same CSVs through the same loaders and draw in the same
palette, so the two can sit side by side.

## Conventions

**Measured data is shown as measured.**
- Use the paper's axes, ranges and units, and its error bars and bands.
- Nothing is smoothed, binned or trimmed unless the docstring says what
  and why. `load_sensitivity` smooths LISA's and AEDGE's digitising
  jitter, and says so.
- A reference (a limit, a fit carried past its data, a cutoff) is dashed
  or grey; data is solid and coloured.

**The palette is the slides':**
- `PLOT_BACKGROUND` (manim.cfg's background) and `PLOT_FOREGROUND` for
  axes and text;
- `FONT_AXIS` and `FONT_TICK`, a notch under the legend size so two plots
  fit side by side.

Series colours come from the topic's style:
- `LOWER_CLOUD_COLOR` and `UPPER_CLOUD_COLOR` for the gradiometer's two
  clouds;
- `LLN_COLOR` and `HLN_COLOR` for the quiet and noisy runs;
- `GW_DETECTOR_COLORS` for the detectors, matching the figure they were
  digitised from, because the audience may know it.

**Every number has a source.** A dataset lives in
`src/manim_atoms/data/<topic>/`. It has:
- a row in `src/manim_atoms/data/README.md` (what, source, licence);
- a script in `data_scripts/` that regenerates it from the original;
- a header in the CSV saying where it came from.

Code reads data only through `manim_atoms.resources.data_path(...)` and a
loader in the topic's `physics/` or `plots/` module, never by path.

**Matplotlib figures are built, not saved.** A builder returns the
`Figure`; saving is the caller's (a talk, a slide). Builders run inside
`deck_fonts()`, so tick labels keep the deck's fonts until saved.

## Recipes

### 1. Points arriving shot by shot

A few thousand `Dot`s would be a few thousand mobjects for cairo to walk
every frame. `core.plots` makes a series one `VMobject`: every dot's circle
laid end to end as subpaths of one path, and an updater shows the first
`count` of them. That makes the point count nearly free. Worked example:
`FringesToEllipse` (the same shot ringed on two plots at once).

```python
from manim_atoms.core.plots import dot_cloud, dot_points, static_cloud

points, per_dot = dot_points(axes, xs, ys)         # every dot's circle, in arrival order
count = ValueTracker(0)                            # how many have arrived
cloud = dot_cloud(points, per_dot, LLN_COLOR, count, FRINGE_DOT_OPACITY)
self.add(axes, cloud)
self.play(count.animate.set_value(len(xs)), rate_func=linear, run_time=3)
self.remove(cloud)                                 # done: freeze it, no updater left
self.add(static_cloud(points, LLN_COLOR, FRINGE_DOT_OPACITY))
```

Sort the data into the order the dots should arrive before calling
`dot_points`, e.g. by phase step to sweep across a fringe.

### 2. Log-log axes

```python
from manim_atoms.core.plots import curve_points, log_axes, plot_point

axes, frame = log_axes((-19, -10), (-16, 0), origin, 8, 5,
                       x_label=r"$m_\phi$ / eV", y_label=r"$|d_e|$", label_every=(2, 4))
curve = VMobject(stroke_color=color).set_points_as_corners(curve_points(axes, x, y))
dot = Dot(plot_point(axes, np.log10(x0), np.log10(y0)))
```

- Ranges are in decades and may end on half decades; only whole decades
  get a `10^n` label, every `label_every`-th.
- The axes run from 0 internally. Always place points with `plot_point`
  (log values) or `curve_points` (linear arrays), never `axes.c2p`.
- **Nothing clips.** Choose ranges that contain the data, or trim it, as
  `aion.tools.uldm_plot.clipped` does.
- `aion.tools.gw_plot.sensitivity_axes` is these axes labelled for strain.

Linear axes are manim's `Axes`, styled with `PLOT_FOREGROUND`; see
`trapping.tools.hifais.loading_axes` for one with ticks, labels and units.

### 3. A matplotlib figure for a slide

Worked examples: `aion.plots.dai_fringes`, `aion.plots.gw_sensitivity`.

```python
def my_figure(data):
    """One line: what it plots, and from which paper's figure."""
    fig, ax = plt.subplots(figsize=(6.4, 5.4))
    fig.set_facecolor(PLOT_BACKGROUND)
    ax.plot(data["x"], data["y"], color=hexed(LLN_COLOR), lw=1.6, label="...")
    dark_axes(ax)                     # no top/right spine; foreground ticks and labels
    legend(ax)
    ax.set_xlabel("Time / s")
    return fig

with deck_fonts():                    # the caller saves inside the same context
    my_figure(load("lln")).savefig("out.png", dpi=200)
```

`hexed(colour)` turns a manim colour into matplotlib's. Each `plots`
module keeps its own `dark_axes` and `legend`, because its figures differ.
If a third module needs the same ones, move them into a shared plots
module under that topic, not into core: core has no matplotlib.

### 4. Adding a dataset

1. Write `data_scripts/process_<thing>.py`. It fetches or reads the
   original, says where it came from in its docstring, and writes the CSV
   with a `#` header naming the source file and any calibration.
2. Put the CSV under `src/manim_atoms/data/<topic>/`. Its loader is in the
   topic's `physics/` module, which skips `#` lines and returns arrays, as
   `load_sensitivity` does.
3. Add a row to `src/manim_atoms/data/README.md` with what it is, the
   source (paper, DOI, file) and the licence. If the licence isn't
   yours, write "check before redistributing": the repo is private, and
   every such row must be resolved before it is ever made public.

## Before you finish

- Compare the plot to the paper's figure: the same ranges, units and
  error representation.
- Check that a frame with every point in matches the static figure.
- `verify-refactor/scripts/save_figures.py` saves every matplotlib figure.
  Add a new figure to it, so later refactors check it too.
