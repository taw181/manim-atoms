"""Stepping an atom through any sequence of laser pulses, and playing it.

run_sequence is the engine. Give it a list of Pulse -- each with an area (a
pi/2 splits every arm it drives, a pi swaps it), a direction (from below or
above) and, if it is selective, the arms it drives -- and it steps one atom
through them, returning a Sequence. What the Sequence holds:

- per pulse, a Step: where it lands, which arms it splits, kicks or merges,
  and the legs flown to the next pulse;
- every arm's corners;
- the output ports.

It covers:
- a plain Mach-Zehnder and LMT Mach-Zehnders of any order (lmt.lmz_pulses);
- the LMT ladder (lmt.lmt_ladder_pulses);
- Ramsey-Borde, with pulses from both sides;
- a gravimeter or a fountain, through ``disp``: a displacement such as
  gravity, which bows every leg as core.spacetime.draw_wavy_legs draws it.

play_sequence animates a Sequence: a ray per pulse, a flash on each arm it
drives, the recolouring and splits, then the legs. Hooks let a scene add
captions and stops.

What happens at a pulse:

- A pi pulse swaps each arm's state, and its velocity changes by
  core.primitives.recoil(state, from_below).
- A pi/2 splits each arm into ``name + "0"`` (left alone) and ``name + "1"``
  (swapped and kicked).
- After a pi/2, outputs that coincide in position, velocity and state are
  one output: they merge into a single arm named for the state. That is how
  an interferometer closes, so there is no special "merge" pulse.

Velocities are in photon recoils, and ``u`` is the height a one-recoil arm
climbs per unit of lab time. Pulses are vertical: they reach every arm at
the instant they fire. Light travel time, as in the gradiometer, would need
an arrival(t, z) per pulse; that is interferometry.tools.pulses' sweep_pulse
for now.
"""

import os
from dataclasses import dataclass, field

import numpy as np
from manim import *

from manim_atoms.interferometry.style import *
from manim_atoms.core.primitives import draw_legs, make_atom, recoil, state_colors
from manim_atoms.core.spacetime import draw_wavy_legs, no_displacement
from manim_atoms.interferometry.tools.pulses import kick_worldline

SEQUENCE_PORT = 0.7  # how far the output ports are drawn past the last pulse
MERGE_TOL = 1e-9  # how close two outputs must be to be one


@dataclass(frozen=True)
class Pulse:
    """One laser pulse: when it fires, its area in units of pi (0.5 splits, 1
    swaps), which side it comes from, which arms it drives (None: all),
    which arms leave the figure after it, and the stage it belongs to."""

    t: float
    area: float = 1.0
    from_below: bool = True
    arms: frozenset | None = None
    drop: frozenset = frozenset()
    stage: int = 0


@dataclass
class Arm:
    """One arm of the atom: its internal state ("g" or "e"), its velocity in
    recoils, and where it is in the free-falling frame (time, height)."""

    name: str
    state: str
    v: float
    t: float
    z: float


@dataclass
class Step:
    """What one pulse did. ``x`` is its lab time.

    - ``driven``: the arms it acted on;
    - ``splits``: (parent, left alone, kicked);
    - ``hits``: (arm, point, new state), for each arm it kicked;
    - ``merges``: (output, members, state), the outputs that coincided;
    - ``legs``: (arm, start, end, state, disp), flown to the next pulse.
    """

    x: float
    pulse: Pulse
    driven: list = field(default_factory=list)
    splits: list = field(default_factory=list)
    hits: list = field(default_factory=list)
    merges: list = field(default_factory=list)
    legs: list = field(default_factory=list)


@dataclass
class Sequence:
    """A run of the engine: one Step per pulse, every arm's corners
    (``paths``: name -> points, from where it was born to where it ended),
    the arms left after the last pulse (``ports``), and ``disp``."""

    steps: list
    paths: dict
    ports: dict
    disp: object = no_displacement


def run_sequence(pulses, start, u, v0=0.0, disp=no_displacement, until=None,
                 port=SEQUENCE_PORT):
    """Step one atom, in |g> at ``start`` (lab time, height) with velocity
    ``v0`` recoils, through ``pulses`` (in time order). After the last pulse
    the arms fly on to ``until`` (default: ``port`` past it): those legs are
    the output ports. ``disp(t)`` displaces everything (gravity: -g t^2 / 2
    from the launch). Returns a Sequence.
    """
    t0, z0 = float(start[0]), float(start[1])
    arms = {"": Arm("", "g", v0, t0, z0)}

    def point(arm):
        return np.array([arm.t, arm.z + disp(arm.t), 0.0])

    paths = {"": [point(arms[""])]}
    steps = []
    for k, pulse in enumerate(pulses):
        if pulse.area not in (0.5, 1.0):
            raise ValueError(f"pulse area {pulse.area}: only pi/2 (0.5) and pi (1) are drawn")
        x = pulse.t
        step = Step(x, pulse)
        step.driven = [n for n in arms if pulse.arms is None or n in pulse.arms]
        if pulse.area == 0.5:
            born = []
            for name in step.driven:
                arm = arms.pop(name)
                dv, state = recoil(arm.state, pulse.from_below)
                step.splits.append((name, name + "0", name + "1"))
                step.hits.append((name + "1", point(arm), state))
                born += [Arm(name + "0", arm.state, arm.v, x, arm.z),
                         Arm(name + "1", state, arm.v + dv, x, arm.z)]
            groups = _coinciding(born)
            if any(len(g) > 1 for g in groups):
                # a closing pulse: its outputs in a fixed order, |g> then |e>
                groups.sort(key=lambda g: g[0].state != "g")
            for group in groups:
                if len(group) == 1:
                    arms[group[0].name] = group[0]
                    continue
                members = [a.name for a in group]
                name = os.path.commonprefix([m[:-1] for m in members]) + group[0].state
                while name in arms:
                    name += "'"
                arms[name] = Arm(name, group[0].state, group[0].v, x, group[0].z)
                step.merges.append((name, members, group[0].state))
            for arm in arms.values():
                paths.setdefault(arm.name, [point(arm)])
        else:
            for name in step.driven:
                arm = arms[name]
                dv, arm.state = recoil(arm.state, pulse.from_below)
                arm.v += dv
                step.hits.append((name, point(arm), arm.state))
        for name in pulse.drop:
            arms.pop(name, None)

        # every arm flies on to the next pulse, or out through its port
        last = k + 1 == len(pulses)
        for arm in arms.values():
            arm_start = point(arm)
            if last and until is None:
                drop = disp(x + port) - disp(x)
                end = arm_start + [port, port * arm.v * u + drop, 0]
                arm.z += arm.v * u * port
                arm.t = x + port
            else:
                dt = (until if last else pulses[k + 1].t) - x
                arm.z += arm.v * u * dt
                arm.t = x + dt
                end = point(arm)
            step.legs.append((arm.name, arm_start, end, arm.state, disp))
            paths[arm.name].append(end)
        steps.append(step)
    return Sequence(steps, paths, dict(arms), disp)


def _coinciding(arms):
    """The arms grouped by what they are: same place, velocity and state."""
    groups = []
    for arm in arms:
        for group in groups:
            other = group[0]
            if (other.state == arm.state and abs(other.v - arm.v) < MERGE_TOL
                    and abs(other.z - arm.z) < MERGE_TOL):
                group.append(arm)
                break
        else:
            groups.append([arm])
    return groups


def play_sequence(scene, seq, atoms, *, span=None, ray_time=0.3, flash_time=0.35,
                  fast_after=None, fast_pace=0.6, colors=None, before_pulse=None,
                  with_pulse=None, after_step=None):
    """Animate ``seq``: one ray per pulse, reaching from its side through to
    the furthest arm; a flash on every arm it kicks, recoloured to its new
    state; then the legs to the next pulse. ``atoms`` maps arm names to the
    atoms already on screen (``{"": atom}`` to start); the dict returned
    maps the arms left at the end.

    - ``span``: (bottom, top) the rays run within, to keep clear of a title;
    - ``ray_time``, ``flash_time``: seconds, scaled by ``fast_pace`` from
      pulse ``fast_after`` on;
    - ``before_pulse(step, k)``: called before each ray (a stage caption);
    - ``with_pulse(step)``: mobjects faded in with the ray (a pi/2 label);
    - ``after_step(step, k)``: called once the legs are flown (a stop).
    """
    colors = colors or {"g": ATOM_COLOR, "e": KICKED_COLOR}
    displaced = seq.disp is not no_displacement
    for k, step in enumerate(seq.steps):
        if before_pulse is not None:
            before_pulse(step, k)
        pace = 1.0 if fast_after is None or k < fast_after else fast_pace
        from_below = step.pulse.from_below
        points = [atoms[n].get_center() for n in step.driven]
        reach = (max if from_below else min)(points, key=lambda p: p[1])
        ray = kick_worldline(reach, from_below, steepness=0.0, span=span)
        extras = with_pulse(step) if with_pulse is not None else ()
        scene.play(Create(ray), *[FadeIn(m) for m in extras], rate_func=linear,
                   run_time=ray_time * pace)

        if step.merges:
            flashes = [Flash(atoms[n], **FLASH_STYLE) for n in step.driven]
            scene.play(*flashes, FadeOut(ray), run_time=flash_time * pace)
            scene.remove(*[atoms.pop(n) for n in step.driven])
            for name, start, _, state, _ in step.legs:
                if name not in atoms:
                    atoms[name] = make_atom(colors[state], opacity=SUPERPOSITION_OPACITY)
                    scene.add(atoms[name].move_to(start))
        else:
            for parent, stay, kicked in step.splits:
                split = atoms.pop(parent)
                at = split.get_center()
                atoms[stay] = make_atom(opacity=SUPERPOSITION_OPACITY).move_to(at)
                atoms[kicked] = make_atom(opacity=SUPERPOSITION_OPACITY).move_to(at)
                scene.remove(split)
                scene.add(atoms[stay], atoms[kicked])
            flashes = [Flash(atoms[arm], **FLASH_STYLE) for arm, _, _ in step.hits]
            recolour = [state_colors(atoms[arm], colors[state]) for arm, _, state in step.hits]
            scene.play(*flashes, *recolour, FadeOut(ray), run_time=flash_time * pace)
        for name in step.pulse.drop:
            if name in atoms:
                scene.remove(atoms.pop(name))

        if displaced:
            draw_wavy_legs(scene, [(atoms[a], s, e, colors[st], d)
                                   for a, s, e, st, d in step.legs])
        else:
            draw_legs(scene, [(atoms[a], s, e, colors[st]) for a, s, e, st, _ in step.legs])
        if after_step is not None:
            after_step(step, k)
    return atoms


# --- pulse sequences --------------------------------------------------------


# A sequence is a list of (time, kind, stage). The kinds:
#   "split"  a pi/2 from below: every arm splits into itself, left alone
#            (name + "0"), and a kicked copy (name + "1"). The two form a pair.
#   "up"     a pi pulse that drives every arm, from whichever side pushes the
#   "down"   kicked arm of each pair up (or down); its partner, in the other
#            state, goes the other way.
#   "merge"  the closing pi/2: each pair, met again, leaves by two ports.
LMT_PORT = 0.7  # how far the output ports are drawn


def lmt_history(pulses, t0, z0, u, port=LMT_PORT):
    """Step through a sequence: for each event, where it lands and what it
    does to each arm, and the legs flown until the next one.

    Starts from one arm, "", in |g> and at rest at (t0, z0). Returns a list of
    dicts: ``x``, ``from_below``, ``stage``, ``kind``,
    ``splits`` [(parent, left alone, kicked)], ``hits`` [(arm, point, new
    state)], and ``legs`` [(arm, start, end, state)] from this event to the
    next -- after the merge, the output ports, named pair + "g"/"e".
    """
    arms = {"": dict(z=z0, v=0, state="g")}
    pairs = []
    history = []
    for k, (t, kind, stage) in enumerate(pulses):
        x = t0 + t
        from_below, splits, hits, legs = True, [], [], []

        def at(arm):
            return np.array([x, arm["z"], 0.0])

        if kind == "split":
            pairs = []
            for name, arm in list(arms.items()):
                dv, state = recoil(arm["state"], True)
                arms[name + "0"] = dict(arm)
                arms[name + "1"] = dict(arm, v=arm["v"] + dv, state=state)
                del arms[name]
                pairs.append((name + "0", name + "1"))
                splits.append((name, name + "0", name + "1"))
                hits.append((name + "1", at(arm), state))
        elif kind in ("up", "down"):
            # the side that gives the kicked arms the push asked for
            dv, _ = recoil(arms[pairs[0][1]]["state"], True)
            from_below = dv == (1 if kind == "up" else -1)
            for name, arm in arms.items():
                dv, arm["state"] = recoil(arm["state"], from_below)
                arm["v"] += dv
                hits.append((name, at(arm), arm["state"]))
        if kind == "merge":
            for stay, kicked in pairs:
                a, b = arms[stay], arms[kicked]
                assert abs(a["z"] - b["z"]) < 1e-9, "the arms have not closed"
                ground = a if a["state"] == "g" else b
                start = at(ground)
                for state, v in (("g", ground["v"]), ("e", ground["v"] + 1)):
                    legs.append((stay[:-1] + state, start,
                                 start + [port, port * v * u, 0], state))
        else:
            dt = pulses[k + 1][0] - t
            for name, arm in arms.items():
                start = at(arm)
                arm["z"] += arm["v"] * u * dt
                legs.append((name, start, np.array([x + dt, arm["z"], 0.0]),
                             arm["state"]))
        history.append(dict(x=x, from_below=from_below, stage=stage, kind=kind,
                            splits=splits, hits=hits, legs=legs))
    return history
