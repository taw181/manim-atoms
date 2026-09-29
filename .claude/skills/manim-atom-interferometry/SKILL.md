---
name: manim-atom-interferometry
description: Create or edit manim animations for atom interferometry in the user's ~/talks/qsim_visit project — beamsplitter/mirror pulses, Mach–Zehnder geometries, photon recoil, interference fringes. Use this whenever the user asks for a manim animation, scene, or figure-in-motion for a talk, wants to add to or change an existing scene (a new pulse, output ports, a phase sweep), or mentions animating atoms, laser pulses, or an interferometer — even if they just say "animate X" or "make a scene showing Y" without naming manim. Also use it for any other manim work in this project, since the render-and-check loop and the shared style module apply regardless of subject.
---

# Manim animations for atom interferometry

## Where things are

The project is `~/talks/qsim_visit` (uv, manim 0.21, Python 3.13). Run manim
**from the project root** so the root `manim.cfg` applies — it sets
`media_dir=./media`, medium quality, and a `#101010` background.

The general code is the installable package `src/aionanim/`; `talk/` holds
only this talk's slide wrappers. Put new scenes and helpers in the package
unless they only make sense in this deck (CLAUDE.md has the rule).

- `src/aionanim/style.py` — the whole visual vocabulary: colour scheme,
  type sizes, `*_STYLE` dicts to splat into constructors, and pacing (`V`).
- `src/aionanim/tools/primitives.py` — mobject helpers (`make_atom`,
  `make_laser_pulse`, `momentum_arrow`, `make_guide`), pulse primitives
  (`absorb`, `emit`), motion (`draw_legs`, `state_colors`).
- `src/aionanim/scenes/mach_zehnder.py` — `SingleLaserKick` and `MachZehnder`,
  the simplest scenes built from them.
- The rest of `tools/` is one module per topic (`spacetime`, `gradiometer`,
  `clock`, `gradiometer_gw`, `uldm`, `single_photon`, `lmt`, `gw_plot`), each
  paired with the `scenes/` module of the same name.

Read style, primitives and mach_zehnder before writing anything — they are
commented and explain what each piece is for. Everything below is what they
*don't* say.

Scene files start `from manim import *` then `from aionanim.style import *`,
and import everything else by absolute name — relative imports break because
manim loads a scene file by path.

## You can't watch the video, so build a look-at-it loop

This is the single most important habit. Render fast, pull out the frames that
matter, and Read the PNGs — never declare an animation good because it
rendered without error.

```bash
cd ~/talks/qsim_visit
uv run manim -ql src/aionanim/scenes/mach_zehnder.py MachZehnder
.venv/bin/python <skill>/scripts/frames.py \
    media/videos/mach_zehnder/480p15/MachZehnder.mp4 \
    -t 3.6 7.8 9.3 --final -o /tmp/frames
```

Then Read the PNGs. Check one frame per *beat* of the animation (each pulse,
each leg, the final state), not just the end — a mobject can be correct
mid-flight and wrong at rest. That is not hypothetical: `TracedPath` collapses
once the point it follows stops moving, so trajectories drawn with it look
perfect during the motion and then vanish during the closing `wait`. Use
`draw_legs`, which creates a `Line` in step with the atom, instead.

`-ql` is 480p15 and takes seconds; save `-qh` (1080p60) for the final render.
`-s` renders only the last frame if that is all you need.

## Check colours by sampling pixels, not by trusting the names

`frames.py --sample X,Y` takes manim scene coordinates and prints the pixel
there. Manim's palette names are misleading about perceptual distance:
`BLUE_D` and `TEAL` sample as `(93,152,167)` and `(126,195,175)` — all but
identical at a 4px stroke, and useless on a projector. `BLUE_D` vs `PURPLE_B`
gives `(84,158,177)` vs `(172,147,188)`, which separates. When two things must
be told apart, sample them and look at the numbers.

## Physics that is easy to draw wrong

- **A beam from below imparts a *vertical* recoil.** The 45° path is the
  resultant of the forward momentum and ħk, so draw the ħk arrow vertical. A
  45° arrow also gets painted over by the arm's own trajectory.
- **At a π pulse the two arms do different things.** The ground-state arm
  absorbs a photon (`absorb`, +ħk). The excited arm undergoes stimulated
  emission — one photon arrives and *two* leave, into the mode of the driving
  field, so it recoils by −ħk (`emit`). Flashing both atoms with one rising
  beam reads as both absorbing, which is wrong.
- **Equal horizontal velocity on every arm** is what makes the geometry work:
  the arms always share an x coordinate, so one vertical beam catches both at
  each pulse, and every leg takes the same `run_time`. Derive run times as
  `distance / V` rather than hand-tuning them, or the atom appears to speed up
  when it splits.

## Keep the pulse columns clear

Pulses travel straight up a fixed x, so anything sitting at that x gets
crossed: a title, a recoil arrow, a caption. The fixes already in use are
worth copying — the `MachZehnder` title sits in the upper *right* with the
legend on the left to leave the mirror's column open, and the `+ħk` arrow is
offset `LEFT * 0.4` off the beam line. Check this in a frame; it is invisible
in the code.

## Adding a scene

Give it its own geometry block of named constants at module level (see the
`# --- Mach-Zehnder geometry ---` block in `scenes/mach_zehnder.py`), derive
every position from them so the shape can be retuned in one place, and reuse the existing helpers rather
than building atoms or pulses by hand — that is what keeps the talk's
animations looking like one set of figures. Pull anything visual from
`aionanim/style.py`; if you need a new colour or width, add it there rather
than inline. Helpers go in `tools/<topic>.py`, the scene and layout only it
uses in `scenes/<topic>.py`.

Manim 0.21 has `DEGREES` but not the `DEG` alias.
