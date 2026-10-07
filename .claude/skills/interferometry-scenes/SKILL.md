---
name: interferometry-scenes
description: Build or change a light-pulse atom-interferometry scene in manim-atoms — atoms split, kicked and recombined by laser pulses on a space-time diagram. Use it for Mach–Zehnder, Ramsey–Bordé, large-momentum-transfer, gravimeter, fountain or gradiometer sequences, for phase drawn as clock hands and dials, output ports, photon recoil, pulses from above or below, arms bowed by gravity or a wave, and for continuous scenes run on one lab clock. Use it with the base manim-atoms skill.
---

# Interferometry scenes

Read the base `manim-atoms` skill first: the workflow, where code goes, and
the render-and-check loop. This skill covers what is particular to
interferometry: the conventions every figure keeps, and recipes for the
patterns that recur. Each recipe is a working scene, cut down. The full
versions are the worked examples named under each one; read the one nearest
yours before writing.

## Conventions

These hold in every interferometry figure, so that each one reads like the
last. Depart from one only when the physics does, and say so in the scene's
docstring.

**The diagram.** A space-time diagram: **x is lab time, y is height** along
the beam, which is also the direction of the laser and of the recoil.

**The laser.** It sits below and fires up. A pulse is a vertical column
when light travel time doesn't matter. When it does, as in the gradiometer,
the pulse is a steep sloped worldline (`interferometry.tools.pulses`).

**Colour is the internal state.**
- `ATOM_COLOR` is |g, p⟩ and `KICKED_COLOR` is |e, p + ħk⟩.
- A leg is coloured by the state the arm is in *along that leg*, so at the
  mirror the colours swap between legs, not between atoms.
- Once split, each arm is an amplitude, drawn at `SUPERPOSITION_OPACITY`;
  a whole atom is opaque.
- `core.primitives.state_legend` is the key, and `species.two_level`'s
  diagram can double as it.

**Slope is momentum.**
- Every arm moves at the same horizontal speed `V`, so arms share an x and
  one column catches both at each pulse.
- A leg's slope is its momentum in recoils times a scale: 1 per ħk in
  the Mach–Zehnder (45°), `LMT_U` or `LMZ_U` per recoil in the LMT scenes.
- `run_time` is always `dx / V`, and `draw_legs` does it for you.

**A recoil is vertical.** A beam from below gives +ħk straight up: draw the
arrow vertical and on the atom (`momentum_arrow(at, UP, r"\hbar k")`). The
45° leg is the sum of the forward motion and the kick, not the kick.

**Single-photon Sr is the default.** |g⟩ = ¹S₀ and |e⟩ = ³P₀, on the 698 nm
clock line.
- One photon per pulse: a π/2 pulse splits, a π pulse swaps.
- At a π pulse the two arms do opposite things. The |g⟩ arm absorbs
  (`absorb`, +ħk). The |e⟩ arm is stimulated to emit (`emit`: one photon
  in, two out, −ħk).
- Flashing both arms with one rising pulse reads as both absorbing, which
  is wrong. `core.primitives.recoil(state, from_below)` gives the sign for
  any arm and any pulse direction.

**Phase is a clock hand.**
- A hand turns only while its arm is in |e⟩: bookkeeping with E_g = 0.
- The measurement is the angle *between* the two hands, read on a dial
  (`phase_sweep`). The last pulse turns that angle into two port
  populations (`ground_share`, `draw_ports`).
- The laser writes its phase onto an arm at each pulse that drives it
  (`wound_with_jumps`, `laser_jumps`).

**Exaggeration is labelled.** Real light travel times (~0.3 µs over 100 m)
and recoil slopes are invisible at true scale. A scene that exaggerates
them says so in its docstring and keeps the exaggeration in its geometry
block.

**When to depart:**

- **Two-photon (Raman, Bragg).** Each pulse gives 2ħk. In Bragg the
  internal state doesn't change, so colour can no longer carry the arm: use
  the slope, and label the momentum states. Say which it is in the title.
- **Pulses from above.** `kick_worldline(point, from_below=False)` draws
  the photon, and `recoil(state, False)` gives the kick's sign. `absorb`
  and `emit` drive from below only, so a scene that needs one from above
  draws it with `kick_worldline` and `Flash`.
- **Gravity, a passing wave.** Bow the legs with a displacement (recipe 5).
  Pulses stay vertical: the laser hasn't moved.
- **Another species.** Its levels and line colours go in a new `species/`
  module, never in a topic's style.

## Recipes

Imports for all of them:

```python
from manim_atoms.interferometry.style import *
from manim_atoms.core.primitives import (absorb, draw_legs, emit, grow, make_atom,
                                         momentum_arrow, state_colors, state_legend)
from manim_atoms.core.spacetime import (carry, draw_wavy_legs, growing_trail, leg_point,
                                        run_to, worldline, wound)
from manim_atoms.interferometry.tools.clock import (clock_rate, dial_hand, draw_ports,
                                                    ground_share, make_clock_hand,
                                                    make_dial, phase_sweep)
from manim_atoms.interferometry.tools.pulses import (fire_vertical_pulse, kick_worldline,
                                                     pulse_caption, strobe_pulse)
from manim_atoms.interferometry.tools.pulse_sequence import Pulse, play_sequence, run_sequence
```

### 1. A pulse sequence, stop-start

The atoms wait while each pulse is drawn. Use it for explainers, where each
pulse is the point. Worked example: `MachZehnder`.

```python
R_L = 2.8                                   # each leg, in lab time
R_A = np.array([-5.8, -2.6, 0.0])           # the beamsplitter
R_B = R_A + RIGHT * R_L                     # the mirror, lower arm
R_B_UP = R_A + (RIGHT + UP) * R_L           # the mirror, upper arm: one recoil = slope 1
R_C = R_B_UP + RIGHT * R_L                  # the second beamsplitter

absorb(self, R_A[0], atom, extras=[pulse_caption(r"\pi/2", R_A[0])])
lower = make_atom(opacity=SUPERPOSITION_OPACITY).move_to(R_A)
upper = make_atom(KICKED_COLOR, opacity=SUPERPOSITION_OPACITY).move_to(R_A)
self.remove(atom); self.add(lower, upper)
kick = momentum_arrow(R_A, UP, r"\hbar k")
self.play(*grow(kick), run_time=0.6)
draw_legs(self, [(lower, R_A, R_B, ATOM_COLOR), (upper, R_A, R_B_UP, KICKED_COLOR)],
          fade=[kick])
self.beat()                                 # stop as the atoms reach the next pulse

absorb(self, R_B[0], lower)                 # |g> absorbs: +hbar k
self.play(state_colors(lower, KICKED_COLOR), run_time=0.4)
emit(self, R_B_UP[0], upper)                # |e> emits: -hbar k
self.play(state_colors(upper, ATOM_COLOR), run_time=0.4)
draw_legs(self, [(lower, R_B, R_C, KICKED_COLOR), (upper, R_B_UP, R_C, ATOM_COLOR)])
```

`draw_legs` takes `(atom, start, end, colour)` per arm, all the same
length. `extra=[...]` animates anything over exactly that stretch of
flight; recipe 3 uses it to turn a hand.

### 2. Any sequence, through the engine

Don't hand-write arm bookkeeping. Write the pulses down and let
`run_sequence` step the atom through them; `play_sequence` animates the
result. Worked example: `LMTMachZehnder` (stage captions, pulse labels and
stops through the hooks).

A `Pulse` is:
- `t`, the lab time it fires (pulses are vertical: no light travel time);
- `area` in units of π: `0.5` splits every arm it drives into `name+"0"`
  (left alone) and `name+"1"` (swapped and kicked), `1` swaps and kicks;
- `from_below`: the kick is `core.primitives.recoil(state, from_below)`,
  so a |g⟩ arm absorbs and an |e⟩ arm emits;
- `arms`: the names it drives (default: all), and `drop`: the names that
  leave the figure after it (outputs that close nothing);
- `stage`: a grouping for captions.

After a π/2, outputs that coincide in place, velocity and state merge into
one arm (`step.merges`): that is how an interferometer closes, with no
"merge" pulse to write. Velocities are in recoils; `u` is the height one
recoil climbs per unit of lab time.

```python
seq = run_sequence([Pulse(t0, 0.5), Pulse(t0 + T, 1), Pulse(t0 + 2 * T, 0.5)],
                   (t0, z0), u, port=1.5)        # a plain Mach-Zehnder
atom = make_atom().move_to([t0, z0, 0])
self.add(atom)
play_sequence(self, seq, {"": atom}, after_step=lambda step, k: self.beat())
loop = Polygon(*seq.paths["1"], *reversed(seq.paths["0"]), **LOOP_AREA_STYLE)
```

What comes back:
- `seq.steps`, one `Step` per pulse: `x`, `pulse`, `driven`, `splits`
  `(parent, stay, kicked)`, `hits` `(arm, point, new state)`, `merges`
  `(output, members, state)`, `legs` `(arm, start, end, state, disp)`;
- `seq.paths`: every arm's corners, from its birth to its end (for loops);
- `seq.ports`: the arms left after the last pulse.

`play_sequence` takes `span` (keep the rays clear of a title), `ray_time`,
`flash_time`, `fast_after` / `fast_pace` (speed up once the idea has
landed), and three hooks: `before_pulse(step, k)` (a caption),
`with_pulse(step)` (mobjects faded in with the ray, e.g. a π/2 label) and
`after_step(step, k)` (where `self.beat()` goes). Sequences already
written: `lmt.lmz_pulses(n, step, T)` and `lmt.lmt_ladder_pulses()`.

**Ramsey–Bordé**: two pulses from below, two from above. Four arms reach
the third pulse; the outputs that close nothing are dropped after it, and
the last pulse closes two interferometers at once.

```python
pulses = [
    Pulse(t0, 0.5), Pulse(t0 + T, 0.5),                       # a pair from below
    Pulse(t0 + T + gap, 0.5, from_below=False,                # a pair from above
          drop=frozenset({"001", "010", "101", "110"})),
    Pulse(t0 + 2 * T + gap, 0.5, from_below=False),
]
seq = run_sequence(pulses, (t0, z0), u, port=1.2)   # t0, z0, u = -5.6, -1.3, 0.35; T, gap = 2.6, 2.4
```

To find the names to drop, run the sequence without `drop` and print each
step's `legs`; the last step's `merges` name the members that close.

**A gravimeter or a fountain**: pass a displacement. `disp` takes lab
time, so measure the fall from the launch. Every corner falls with it and
the legs bow (`play_sequence` switches to `draw_wavy_legs`); a fountain is
the same with `v0 > 0`, its apex where `v0 * u = g * t`. A loop drawn over
bowed legs has to follow the same curve, through `core.spacetime.leg_point`:

```python
fall = lambda t: -0.5 * g * (t - t0) ** 2          # t0, z0, u, g, T = -5.4, 2.6, 0.35, 0.09, 4.2
seq = run_sequence([Pulse(t0, 0.5), Pulse(t0 + T, 1), Pulse(t0 + 2 * T, 0.5)],
                   (t0, z0), u, disp=fall, port=1.5)
play_sequence(self, seq, {"": atom})

def bowed(corners):
    return [leg_point(a, b, fall, s)
            for a, b in zip(corners, corners[1:]) for s in np.linspace(0, 1, 24)]

loop = Polygon(*bowed(seq.paths["1"]), *reversed(bowed(seq.paths["0"])), **LOOP_AREA_STYLE)
```

The engine's pulses are vertical. Pulses that arrive late with light travel
time (the gradiometer's `sweep_pulse`) are not yet a pulse option: extend
`interferometry.tools.pulse_sequence` rather than hand-writing a one-off.

### 3. Phase as clock hands, stop-start

Worked examples: `ClockPhase`, `DarkMatterPhase`.

```python
rate = clock_rate(H_T)                         # turns per leg, the same in every scene
first, last = ValueTracker(0.0), ValueTracker(0.0)   # the arm excited on leg 1 / leg 2
self.add(first, last)                          # in the scene before anything reads them
dial = make_dial(H_DIAL, r"accumulated phase")
self.add(dial, dial_hand(H_DIAL, last, lighten(ATOM_COLOR)),
         dial_hand(H_DIAL, first, lighten(KICKED_COLOR)))
# ...split as in recipe 1, then each arm carries its hand:
self.add(lo, hi, make_clock_hand(lo, last), make_clock_hand(hi, first))
draw_legs(self, [(lo, H_A, H_B, ATOM_COLOR), (hi, H_A, H_B_UP, KICKED_COLOR)],
          extra=[first.animate.set_value(rate * H_T)])   # only the excited arm turns
# ...the mirror swaps colours; leg 2 turns `last` instead; then the last pulse:
sweep, gap = phase_sweep(H_DIAL, last, first)
self.play(FadeIn(sweep), run_time=0.6)
draw_ports(self, H_C, 1.5, ground_share(last, first), slope=slope_of_kicked_leg)
```

`draw_ports` draws an empty port as a dashed guide: a null only reads as
"they all came out here" if the other port is on the page. The excited port
leaves at the kicked leg's slope (`leg_slope(start, end)`), not at 45°.

### 4. One lab clock driving everything

When something passes *through* the interferometer (a wave, a field, a
beam switched on), stopping the atoms for a pulse stops it too. Run one
`ValueTracker` whose value **is** the diagram's x, and make everything a
function of it: the atoms, their trails, the hands, markers on a trace, a
level diagram. Worked examples: `DarkMatterPhaseContinuous`,
`GradiometerContinuous`.

```python
now = ValueTracker(a[0])
first, last = ValueTracker(0.0), ValueTracker(0.0)
first.add_updater(wound(now, rate, a[0], b[0]))     # turns while excited, holds after
last.add_updater(wound(now, rate, b[0], c[0]))
self.add(now, first, last)

def split():                                         # runs on the instant the pulse arrives
    carry(lo, worldline([a, b, c]), now)             # an arm pinned to its corners
    carry(hi, worldline([a, b_up, c]), now)
    self.add(growing_trail([a, b], ATOM_COLOR, now),       # one trail per leg:
             growing_trail([b, c], KICKED_COLOR, now),     # the colour belongs to
             growing_trail([a, b_up], KICKED_COLOR, now),  # the leg, not the arm
             growing_trail([b_up, c], ATOM_COLOR, now), lo, hi, hand_lo, hand_hi)

strobe_pulse(self, now, a[0], top=a[1], flash_at=[a], on_arrival=split)
strobe_pulse(self, now, b[0], top=b_up[1], flash_at=[b, b_up], on_arrival=swap)
strobe_pulse(self, now, c[0], top=c[1], flash_at=[c])
run_to(self, now, c[0] + 1.0)
```

The rules that make it work:
- **Every `play` between the first pulse and the last advances `now`.**
  `run_to(scene, now, t, *anims)` is the one way to play; anything else is
  the freeze this pattern exists to remove.
- **Anything that would be a beat of its own becomes an updater** or an
  `always_redraw` that switches itself on when `now` passes it. Examples
  are a trace marker lighting up and a band filling in (`growing_band`).
- **Pulses become strobes:** `strobe_pulse` without light travel time,
  `sweep_pulse` with it. What a pulse does to the atoms goes in its
  `on_arrival` / `on_near` / `on_far` callback, which runs on the instant.
- **Flash the vertex, not the atom**: the atom is moving.
- **A continuous variant is a subclass** that rewrites `fly` (and `close`),
  keeping everything either side of the pulse sequence. It is named
  `*Continuous`, and it runs the whole sequence as one stretch with no
  stops inside it.

### 5. Arms bowed by a displacement (gravity, a wave)

A displacement is a function `disp(t)`: how far the cloud has been moved at
lab time t. Move the corners by it, then let each leg bow between them.
`leg_point` subtracts `disp` at a leg's ends and adds it back along the
way, so the bowed leg still passes through both corners. Worked examples:
`GradiometerGWStretch`, and the gradiometer's
`GradiometerBase.displacement` hook.

```python
def fall(t):
    """How far gravity has pulled the cloud below its launch height by lab time t."""
    return -0.5 * G_G * (t - G_A[0]) ** 2

a, b, b_up, c = (v + UP * fall(v[0]) for v in flat_corners)     # corners ride the fall
draw_wavy_legs(self, [(lo, a, b, ATOM_COLOR, fall), (hi, a, b_up, KICKED_COLOR, fall)])
# on one lab clock instead: worldline(corners, fall) and growing_trail(corners, colour, now, fall)
```

- Use `draw_wavy_legs`, never `draw_legs` + `Create` on a curve: see the
  base skill's traps.
- It clears the atoms' updaters when it ends, so don't `carry` the same
  atoms.
- Output ports stand for atoms flying out to be imaged, so they stay
  straight. Take the bow back out of their slope, as
  `GradiometerGWStretch.port_slope` does.

### 6. A gradiometer: two interferometers, one laser

Don't rebuild it. Subclass `interferometry.scenes.gradiometer.GradiometerBase`.

**Its `construct` sets:**
- `self.low`, `self.up` — each cloud's four corners, from
  `vertices(z, lag)`;
- `self.atoms` — `{"low": [ground, kicked], "up": [...]}`;
- `self.seeds`;
- `self.phase` — two trackers per cloud;
- `self.hands = []` and `self.big = VGroup()`.

Then it calls `self.fly()`. `gradiometer_frame(self, title)` draws the
furniture.

**Hooks to override:**
- `displacement(cloud)`: a bow, as in recipe 5;
- `port_slope(cloud)`;
- `pulse_note(k)`: a caption for pulse k;
- `open_arms`, `close`.

**On one lab clock**, mix `RunsContinuously` in *first*
(`class X(RunsContinuously, GradiometerBase)`). Its `fly` must set
`self.clock`, and it writes `shoot(k, ...)` around `sweep_pulse`.

Read `Gradiometer` (quiet, stop-start), `GradiometerContinuous` and
`DarkMatterGradiometer` before writing one.

## Before you finish

Check one frame per pulse:
- every arm is coloured by its state along each leg;
- the arms share an x at each pulse;
- the recoil arrows are vertical and on their atoms;
- nothing sits in a pulse's column.

For a continuous scene, also check a frame in the middle of each leg: the
hands should be turning and the trails should end at the atoms.
