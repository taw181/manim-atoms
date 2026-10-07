---
name: aion-scenes
description: Build or change an AION scene in manim-atoms — a gravitational wave or an ultralight dark-matter field passing through the single-photon atom gradiometer, a signal injected by a light shift, LIGO's Michelson, a binary merger, the GW and ULDM sensitivity plots, AEDGE or the km-scale detector. Use it whenever the scene is about what the gradiometer detects or how it compares with other detectors. Use it with the base manim-atoms skill, and with interferometry-scenes for anything drawn on the gradiometer.
---

# AION scenes

AION's scenes are interferometry scenes with something passing through
them, or plots of what AION and other detectors can reach. Read the base
`manim-atoms` skill. Read `interferometry-scenes` for the gradiometer
itself: recipes 4 (one lab clock), 5 (bowed arms) and 6 (subclassing
`GradiometerBase`). This skill adds what AION brings: the signals, how each
reaches the atoms, and the plots.

## Conventions

**The instrument.** AION is a single-photon Sr gradiometer: two clouds a
baseline L apart, one laser, every pulse reaching the far cloud L/c after
the near one. The laser's phase noise is common to both and cancels in the
difference. A signal shows up because the two clouds sample it at
different times or places.

**Say how a signal reaches the atoms, and draw only that.**

| Signal | What it changes | How to draw it | Example |
|---|---|---|---|
| gravitational wave, as the readout sees it | the light travel time | pulses arrive early or late: `gw_vertices(z, gw_arrival_lags(z))`, sloped pulses with `lag=gw_lag(t)` | `GradiometerGW` |
| gravitational wave, as proper distance | where the clouds are | arms bowed by `gw_displacement(t, z0)` (interferometry recipe 5) | `GradiometerGWStretch` |
| ultralight dark matter | ω_A, the clock frequency | hands winding by `dm_phase(rate, t1, t2)` over each arm's excited window; the geometry is untouched | `DarkMatterPhase`, `DarkMatterGradiometer` |
| an injected light shift | one cloud's ω_A, while a beam is on | `wound_with_shift` on that cloud's hands, `growing_band` for the beam's window | `LightShiftSignal` |

The two GW pictures are the same wave. A scene picks one and says which in
its title, because mixing them double-counts the effect.

**Signals live on the diagram's own time axis.**
- A trace of h(t) or the field runs along the top of the diagram, on the
  same x as lab time, so a pulse and the moment of the wave it samples line
  up vertically. Use `make_strain_trace` or `make_field_trace`, with a
  marker riding the present (`strain_marker`, `field_marker`).
- Each pulse is marked on the trace once per cloud, in
  `LOWER_PULSE_MARK_COLOR` and `UPPER_PULSE_MARK_COLOR`.
- The two dials' captions take the same colours, which is the key.
- `FIELD_COLOR` is `STRAIN_COLOR` on purpose: a trace above the diagram is
  the same kind of object, whatever oscillates.

**Exaggerate, and say so.**
- Real L/c is ~0.3 µs against T ~ 1 s, and real h ~ 10⁻²¹. The figures
  blow both up by many orders of magnitude.
- The scene's docstring states the exaggeration, and the geometry block
  holds the factor (`GW_LAG_GAIN`, `PHASE_GAIN`).
- Where there is room, the real numbers go on the page, as
  `make_equation`'s scale line does for LIGO.

**Numbers come from `aion.physics`, never typed in:**
- `gw_signals`: sensitivity curves, merger tracks, chirp times, distances;
- `uldm_sensitivity`: reach, mass ↔ frequency;
- `km_scale`: what scaling the prototype to a kilometre asks for.

The source paper goes in the module or scene docstring. Data files are
listed in `src/manim_atoms/data/README.md` with their licences.

**One lab clock is the default** for anything with a signal passing
through. A stop-start scene stops the signal with the atoms, and the signal
is the point. Write the stop-start version only as a first explainer, with
a `*Continuous` subclass beside it.

## Recipes

### 1. A field on the diagram's time axis, driving a level diagram

The trace, the moving clock transition and the washes over each arm's
excited window, all on one clock. Put the interferometer under it as
`interferometry-scenes` recipe 4 does. Worked example:
`DarkMatterPhaseContinuous`.

```python
from manim_atoms.aion.tools.uldm import field_marker, make_field_trace, make_modulated_levels
from manim_atoms.core.spacetime import growing_band, run_to

trace, bands, dots = make_field_trace([(a, b), (b, c)])    # one wash per excited window
now = ValueTracker(a)
levels, moving, detuning = make_modulated_levels(now)      # moving, detuning: draw functions
self.add(now)
self.play(FadeIn(trace), FadeIn(levels))
self.add(always_redraw(moving), always_redraw(detuning), field_marker(now),
         growing_band(bands[0], a, b, now), growing_band(bands[1], b, c, now))
run_to(self, now, c)            # ...the interferometer's strobes and legs run on the same `now`
```

### 2. A new signal through the gradiometer

Subclass `GradiometerBase` with `RunsContinuously` mixed in first
(`interferometry-scenes` recipe 6), then supply:

1. **The signal**, normalised to ±1, as a function of lab time:
   `strain(t)`, `dm_field(t)`. It goes in `aion/tools/<signal>.py`, with
   its exaggeration constants in the geometry block there.
2. **What it does to each cloud.** Choose from the table above, and write
   only that:
   - early or late pulses go in `shoot` (passing `lag` to `sweep_pulse`);
   - a bow goes in `displacement(cloud)`;
   - a phase goes in each hand's tracker updater, as the integral of the
     signal over the arm's excited window.
3. **The trace**, along the top, with a mark per pulse per cloud
   (`arrival_dots`, or `make_field_trace(..., pulses=...)`) and the dials
   captioned in the mark colours.
4. **A caption for the one thing the scene is about**, in `pulse_note(k)`,
   on the first pulse only. Later captions repeat it.

Read `DarkMatterGradiometer` end to end before writing one. It is the
shortest complete example.

### 3. LIGO's Michelson, in a panel of another scene

Every LIGO builder takes the wave as `h` (a function of lab time,
normalised to a peak of 1) and a `Panel` to draw into, so another scene
can set the interferometer in a corner of its frame and drive it with its
own wave. Worked example: `MergerOnSensitivityPlot`.

```python
from manim_atoms.aion.tools.ligo import Panel, make_apparatus, make_light, run

now = ValueTracker(0.0)
panel = Panel.at(0.6, [-2.6, -1.1], [-3.0, 0.0])    # scale 0.6, the splitter put at (-3, 0)
labels, optics, arm_labels = make_apparatus(now, h=my_wave, panel=panel)
lit = ValueTracker(1.0)                              # the light already all the way through
glow, lights = make_light(now, lit, lit, h=my_wave, panel=panel)
self.add(now, glow, lights, labels, arm_labels)
self.bring_to_front(*optics)                         # light under the optics
run(self, now, 8.0)                                  # LIGO's own clock-advancing play
```

`make_strain_trace`, `returning_waves` and `make_equation` take a `panel`
of their own, so the readout can be laid out apart from the apparatus.

### 4. The sensitivity plot, with a merger track

The generic log-log axes are in `core.plots` (see `data-plots`); these are
the GW-specific pieces. Worked examples: `SensitivityBuildUp`,
`AEDGESensitivity`.

```python
from manim_atoms.aion.physics.gw_signals import merger_track
from manim_atoms.aion.tools.gw_plot import detector_region, sensitivity_axes
from manim_atoms.core.plots import curve_points

axes, frame = sensitivity_axes((-6, 4), (-24, -14.5), [-4.9, -2.75, 0], 11.3, 5.9)
region, curve = detector_region(axes, "aion_100", GW_DETECTOR_COLORS["AION-100"])
f, h = merger_track(60, 0.1)                         # 60 solar masses at z = 0.1
track = VMobject(stroke_color=merger_color(0.1), stroke_width=GW_TRACK_WIDTH)
track.set_points_as_corners(curve_points(axes, f, h))
```

**Nothing clips to the axes.** A range narrower than the data puts curves
and shaded regions off the plot and over the labels. Use the source
figure's ranges (`gw_landscape.LOG_F_RANGE` and `LOG_H_RANGE`, 10⁻⁶ to
10⁴ Hz and 10⁻²⁴ to 10⁻¹⁴·⁵), or trim the data yourself as
`uldm_plot.clipped` does.

Detector colours are the source figure's (`GW_DETECTOR_COLORS`), so the
plot still reads as the familiar one. Merger tracks take no hue:
`merger_color(z)` fades white to grey with redshift.

For the ULDM reach, use `uldm_inset` for the whole inset, or its pieces
(`uldm_axes`, `uldm_curves`, `excluded_region`, `mass_mark`).

## Before you finish

**Check, at each pulse:**
- the trace's marks line up vertically with the pulse reaching each cloud;
- the dials' caption colours match the marks.

**Check the claim:**
- the scene draws exactly one of the mechanisms in the table, and its
  title names it;
- a continuous scene never stops the trace's marker between the first
  pulse and the last.
