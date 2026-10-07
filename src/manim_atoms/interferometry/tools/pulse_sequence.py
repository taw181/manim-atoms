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
climbs per unit of lab time.

Light travel time: a Pulse with a ``slope`` (lab time per unit height) is
sloped, passing height ``z_ref`` at its ``t``; ``Pulse.arrival(z)`` is when
it reaches height z. run_sequence times each pulse at its arrival at the
atom's starting height: one pulse reaches every arm of one cloud at once,
the arm separation being negligible against the baseline the light
crosses. A gradiometer is then one run_sequence per cloud over the same
pulses, each cloud's corners late by its own light travel time.

``climb="leg"`` (instead of the default ``"time"``) makes ``u`` the height a
one-recoil arm climbs per leg, however long the leg lasts. With equal pulse
intervals the two agree. With unequal ones -- a light travel time a wave is
modulating, exaggerated far past the real 1e-21 so it can be seen -- "time"
would draw the loop failing to close, which reads as a bug; "leg" pins every
corner to its pulse's arrival and keeps the loop closed, at the price of
kicked legs whose slopes differ. That is a drawing convention, not physics:
the recoil velocity never changes, and the wave's signal is a phase.
"""

import os
from dataclasses import dataclass, field

import numpy as np
from manim import *

from manim_atoms.interferometry.style import *
from manim_atoms.core.primitives import (
    absorb,
    draw_legs,
    emit,
    make_atom,
    recoil,
    state_colors,
)
from manim_atoms.core.spacetime import draw_wavy_legs, no_displacement
from manim_atoms.interferometry.tools.pulses import fire_vertical_pulse, kick_worldline

SEQUENCE_PORT = 0.7  # how far the output ports are drawn past the last pulse
MERGE_TOL = 1e-9  # how close two outputs must be to be one


@dataclass(frozen=True)
class Pulse:
    """One laser pulse: when it fires, its area in units of pi (0.5 splits, 1
    swaps), which side it comes from, which arms it drives (None: all),
    which arms leave the figure after it, and the stage it belongs to.

    With light travel time, ``slope`` is the lab time the light takes per
    unit height and ``t`` is when it passes height ``z_ref``; a slope of 0
    (the default) is a vertical pulse, reaching every height at ``t``."""

    t: float
    area: float = 1.0
    from_below: bool = True
    arms: frozenset | None = None
    drop: frozenset = frozenset()
    stage: int = 0
    slope: float = 0.0
    z_ref: float = 0.0

    def arrival(self, z):
        """When the pulse reaches height ``z``."""
        return self.t + self.slope * (z - self.z_ref)


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
                 port=SEQUENCE_PORT, climb="time"):
    """Step one atom, in |g> at ``start`` (lab time, height) with velocity
    ``v0`` recoils, through ``pulses`` (in time order). Each pulse acts at its
    arrival at the starting height. After the last pulse the arms fly on to
    ``until`` (default: ``port`` past it): those legs are the output ports.
    ``disp(t)`` displaces everything (gravity: -g t^2 / 2 from the launch).
    ``climb`` is "time" (``u`` per unit time) or "leg" (``u`` per leg, the
    ports going on at the last leg's rate; see the module docstring).
    Returns a Sequence.
    """
    if climb not in ("time", "leg"):
        raise ValueError(f"climb {climb!r}: 'time' or 'leg'")
    t0, z0 = float(start[0]), float(start[1])
    times = [pulse.arrival(z0) for pulse in pulses]
    if climb == "leg":
        if len(pulses) < 2:
            raise ValueError("climb='leg' needs two pulses, to set the ports' rate")
        out_rate = u / (times[-1] - times[-2])  # the ports go on at the last leg's
    arms = {"": Arm("", "g", v0, t0, z0)}

    def point(arm):
        return np.array([arm.t, arm.z + disp(arm.t), 0.0])

    paths = {"": [point(arms[""])]}
    steps = []
    for k, pulse in enumerate(pulses):
        if pulse.area not in (0.5, 1.0):
            raise ValueError(f"pulse area {pulse.area}: only pi/2 (0.5) and pi (1) are drawn")
        x = times[k]
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
                rate = u if climb == "time" else out_rate
                drop = disp(x + port) - disp(x)
                end = arm_start + [port, port * arm.v * rate + drop, 0]
                arm.z += arm.v * rate * port
                arm.t = x + port
            else:
                dt = (until if last else times[k + 1]) - x
                if climb == "time":
                    arm.z += arm.v * u * dt
                elif last:
                    arm.z += arm.v * out_rate * dt
                else:
                    arm.z += arm.v * u
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


def play_sequence(scene, seq, atoms, *, style="ray", span=None, ray_time=0.3,
                  flash_time=0.35, fast_after=None, fast_pace=0.6, kick_time=0.6,
                  colors=None, atom=None, ports=True, before_pulse=None,
                  with_pulse=None, photon_extras=None, on_kick=None,
                  before_legs=None, with_legs=None, after_step=None):
    """Animate ``seq``, pulse by pulse: the pulse, what it does to each arm it
    drives, then the legs to the next pulse (bowed, if the sequence is
    displaced). ``atoms`` maps arm names to the atoms already on screen
    (``{"": atom}`` to start); it is updated in place, so a hook can read the
    arms from it, and returned.

    The pulse, by ``style``:

    - "ray": one ray from its side through to the furthest arm; a flash on
      every arm it kicks, recoloured with the flash. Quick, for long
      sequences (LMT).
    - "photon": one wavepacket per driven arm, in arm order -- absorbed by a
      |g> arm, stimulating emission from an |e> arm (core.primitives' absorb
      and emit, from the pulse's side) -- each followed by its own play
      recolouring that arm. At a split the halves are born in their final
      colours; at a closing pi/2 one packet reaches the meeting point. For
      explainers, where each pulse is the point (MachZehnder).
    - "column": the pulse climbs a column through the arms it drives
      (fire_vertical_pulse), then one play recolours them all (ClockPhase).

    Options:

    - ``span``: (bottom, top) the rays run within, to keep clear of a title;
    - ``ray_time``, ``flash_time``: seconds, scaled by ``fast_pace`` from
      pulse ``fast_after`` on ("ray");
    - ``kick_time``: the recolouring play's seconds ("photon", "column");
    - ``atom(color, opacity)``: makes the halves and the ports (default
      make_atom);
    - ``ports``: False stops after the last pulse, with no ports drawn, for
      a scene that reads its ports out itself.

    Hooks, each optional:

    - ``before_pulse(step, k)``: before the pulse (a caption, a marker);
    - ``with_pulse(step)``: mobjects faded in with the ray ("ray");
    - ``photon_extras(step, k, arm)``: (extras, fade) for the packet sent to
      ``arm``, as absorb takes them (a caption, the k-vector marker, a
      level-diagram glow); an emission fades its ``fade`` in the recolouring
      play that follows it;
    - ``on_kick(step, k, arm)``: animations played with ``arm``'s
      recolouring (a recoil arrow growing, a dial hand changing colour); at
      a split, called for the kicked half;
    - ``before_legs(step, k)``: once the pulse is done, before the legs (a
      laser phase written in, a band faded in);
    - ``with_legs(step, k)``: (fade, extra) for the legs, as draw_legs takes
      them (arrows fading, kets fading in, hands turning);
    - ``after_step(step, k)``: once the legs are flown (a stop).
    """
    colors = colors or {"g": ATOM_COLOR, "e": KICKED_COLOR}
    if atom is None:
        def atom(color, opacity):
            return make_atom(color, opacity=opacity)
    if style not in ("ray", "photon", "column"):
        raise ValueError(f"style {style!r}: 'ray', 'photon' or 'column'")
    displaced = seq.disp is not no_displacement
    kicks = on_kick or (lambda step, k, arm: ())
    for k, step in enumerate(seq.steps):
        last = k + 1 == len(seq.steps)
        if before_pulse is not None:
            before_pulse(step, k)
        if style == "ray":
            _ray(scene, step, k, atoms, colors, atom, span, with_pulse,
                 ray_time, flash_time,
                 1.0 if fast_after is None or k < fast_after else fast_pace)
        else:
            _photons(scene, step, k, atoms, colors, atom, style, kick_time,
                     photon_extras, kicks, ports or not last)
        for name in step.pulse.drop:
            if name in atoms:
                scene.remove(atoms.pop(name))
        if before_legs is not None:
            before_legs(step, k)

        if last and not ports:
            break
        fade, extra = with_legs(step, k) if with_legs is not None else ((), ())
        if displaced:
            draw_wavy_legs(scene, [(atoms[a], s, e, colors[st], d)
                                   for a, s, e, st, d in step.legs],
                           fade=fade, extra=extra)
        else:
            draw_legs(scene, [(atoms[a], s, e, colors[st]) for a, s, e, st, _ in step.legs],
                      fade=fade, extra=extra)
        if after_step is not None:
            after_step(step, k)
    return atoms


def _ray(scene, step, k, atoms, colors, atom, span, with_pulse, ray_time, flash_time, pace):
    """One pulse as a ray, with its flashes, splits, merges and recolouring."""
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
        _ports(scene, step, atoms, colors, atom)
        return
    kicked_to = {arm: state for arm, _, state in step.hits}
    for parent, stay, kicked in step.splits:
        split = atoms.pop(parent)
        at = split.get_center()
        # both halves start in the parent's state; the kicked one is
        # recoloured with the flash
        kept = colors[_other(kicked_to[kicked])]
        atoms[stay] = atom(kept, SUPERPOSITION_OPACITY).move_to(at)
        atoms[kicked] = atom(kept, SUPERPOSITION_OPACITY).move_to(at)
        scene.remove(split)
        scene.add(atoms[stay], atoms[kicked])
    flashes = [Flash(atoms[arm], **FLASH_STYLE) for arm, _, _ in step.hits]
    recolour = [state_colors(atoms[arm], colors[state]) for arm, _, state in step.hits]
    scene.play(*flashes, *recolour, FadeOut(ray), run_time=flash_time * pace)


def _photons(scene, step, k, atoms, colors, atom, style, kick_time, photon_extras,
             kicks, ports):
    """One pulse as photons ("photon") or a column ("column")."""
    x, from_below = step.x, step.pulse.from_below

    def extras_for(arm):
        return photon_extras(step, k, arm) if photon_extras is not None else ((), ())

    def photon(arm, old_state):
        """One packet to ``arm``; returns what the following play fades."""
        extras, fade = extras_for(arm)
        if old_state == "g" or step.merges:
            absorb(scene, x, atoms[arm], extras=extras, fade=fade, from_below=from_below)
            return ()
        emit(scene, x, atoms[arm], extras=extras, from_below=from_below)
        return fade

    def column(targets):
        """The column through ``targets``, captioned as photon_extras says."""
        extras, fade = extras_for(step.driven[0])
        if extras or fade:
            raise ValueError("photon_extras is for style='photon'")
        fire_vertical_pulse(scene, x, [atoms[n] for n in targets])

    if step.merges:
        # the arms meet: one packet reaches the meeting point
        if style == "photon":
            photon(step.driven[0], None)
        else:
            column([step.driven[0]])
        if ports:
            _ports(scene, step, atoms, colors, atom)
        return

    kicked_to = {arm: state for arm, _, state in step.hits}
    if step.splits:
        if style == "column":
            column([parent for parent, _, _ in step.splits])
        for parent, stay, kicked in step.splits:
            kept = _other(kicked_to[kicked])
            fade = photon(parent, kept) if style == "photon" else ()
            split = atoms.pop(parent)
            at = split.get_center()
            atoms[stay] = atom(colors[kept], SUPERPOSITION_OPACITY).move_to(at)
            atoms[kicked] = atom(colors[kicked_to[kicked]], SUPERPOSITION_OPACITY).move_to(at)
            scene.remove(split)
            scene.add(atoms[stay], atoms[kicked])
            anims = [*kicks(step, k, kicked), *[FadeOut(m) for m in fade]]
            if anims:
                scene.play(*anims, run_time=kick_time)
        return

    if style == "photon":
        for arm, _, state in step.hits:
            fade = photon(arm, _other(state))
            scene.play(state_colors(atoms[arm], colors[state]), *kicks(step, k, arm),
                       *[FadeOut(m) for m in fade], run_time=kick_time)
    else:
        column([arm for arm, _, _ in step.hits])
        scene.play(*[state_colors(atoms[arm], colors[state]) for arm, _, state in step.hits],
                   *[a for arm, _, _ in step.hits for a in kicks(step, k, arm)],
                   run_time=kick_time)


def _ports(scene, step, atoms, colors, atom):
    """The arms a closing pulse merged give way to its output ports."""
    scene.remove(*[atoms.pop(n) for n in step.driven])
    for name, start, _, state, _ in step.legs:
        if name not in atoms:
            atoms[name] = atom(colors[state], SUPERPOSITION_OPACITY)
            scene.add(atoms[name].move_to(start))


def _other(state):
    """The other internal state."""
    return "e" if state == "g" else "g"
