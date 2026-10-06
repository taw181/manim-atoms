"""Atoms, laser pulses and the recoil they hand over: the atom-interferometry
building blocks every other scene is drawn with.

Mobject helpers (make_atom, make_cloud, make_laser_pulse, momentum_arrow, make_guide),
pulse primitives (absorb, emit) and motion (draw_legs, state_colors).
"""

import numpy as np
from manim import *

from manim_atoms.style import *


def make_atom(color=ATOM_COLOR, radius=ATOM_RADIUS, opacity=1.0):
    """An atom drawn as a flat filled disc.

    A VGroup of one rather than a bare Circle, because every scene reaches for
    atom[0] to recolour the body when the internal state changes.
    """
    body = Circle(
        radius=radius,
        fill_color=color,
        fill_opacity=opacity,
        stroke_color=lighten(color),
        stroke_width=ATOM_STROKE_WIDTH,
    )
    return VGroup(body)


def make_cloud(center, color, n=CARTOON_CLOUD_N, radius=CARTOON_CLOUD_RADIUS, seed=0):
    """A still cartoon of an atom cloud: dots in a round Gaussian heap,
    pulled in to ``radius`` so the cloud has an edge."""
    rng = np.random.default_rng(seed)
    xy = rng.normal(scale=radius / 2.2, size=(n, 2))
    norms = np.linalg.norm(xy, axis=1, keepdims=True)
    xy *= np.minimum(1, radius / np.maximum(norms, 1e-9))
    center = np.array(center, dtype=float)
    return VGroup(*[
        Dot(center + [x, y, 0], radius=CARTOON_CLOUD_DOT_RADIUS, color=color, stroke_width=0)
        for x, y in xy
    ])


def make_laser_pulse(x, y, length=PULSE_LENGTH, n_cycles=PULSE_CYCLES):
    """A Gaussian-enveloped sine wavepacket propagating along +y, centred on (x, y)."""
    sigma = length / 5.0
    k = 2 * PI * n_cycles / length

    packet = FunctionGraph(
        lambda t: PULSE_AMPLITUDE * np.sin(k * t) * np.exp(-((t / sigma) ** 2)),
        x_range=[-length / 2, length / 2, 0.01],
        color=LASER_COLOR,
        stroke_width=PULSE_STROKE_WIDTH,
    )
    packet.rotate(90 * DEGREES).move_to([x, y, 0])
    packet.set_stroke(opacity=PULSE_TAPER)
    return packet


def momentum_arrow(origin, direction, tex, label_dir=LEFT, length=1.1):
    """A recoil arrow with its label, e.g. the hbar k an atom gains from a pulse."""
    arrow = Arrow(origin, origin + direction * length, **RECOIL_ARROW_STYLE)
    label = MathTex(tex, font_size=FONT_ANNOTATION, color=LASER_COLOR).next_to(
        arrow, label_dir, buff=0.15
    )
    return VGroup(arrow, label)


def grow(annotation):
    """Animations that bring a momentum_arrow on screen."""
    return [GrowArrow(annotation[0]), FadeIn(annotation[1])]


def make_k_arrow(x, y):
    """The little vertical k-vector marker that sits beside a beam."""
    arrow = Arrow(ORIGIN, UP * 0.7, **K_ARROW_STYLE)
    label = MathTex(r"\vec{k}", font_size=FONT_K, color=LASER_COLOR)
    return VGroup(arrow, label.next_to(arrow, RIGHT, buff=0.12)).move_to([x, y, 0])


def make_guide(start, end):
    """A dashed construction line, e.g. the trajectory an atom arrives along."""
    return DashedLine(start, end, **GUIDE_STYLE)


def absorb(scene, x, atom, extras=(), fade=(), also=()):
    """A wavepacket rises from below and is absorbed: |g, p> -> |e, p + hbar k>.

    The packet collapses into the atom rather than simply fading, so absorption
    is visibly a different event from the stimulated emission at the mirror.

    `also` is (x, atom) pairs struck by twins of the same pulse, rising in
    step with it: the same event drawn twice, e.g. on a space-time diagram
    and in the apparatus beside it, where the atom is at the same height.
    """
    y0 = -config.frame_y_radius - 0.6
    targets = [(x, atom), *also]
    pulses = [make_laser_pulse(tx, y0) for tx, _ in targets]
    scene.add(*pulses)

    rise = atom.get_center()[1] - y0
    scene.play(
        *[p.animate.shift(UP * (a.get_center()[1] - y0)) for p, (_, a) in zip(pulses, targets)],
        *[FadeIn(m) for m in extras],
        rate_func=linear,
        run_time=rise / PULSE_SPEED,
    )
    scene.play(
        *[Flash(a, **FLASH_STYLE) for _, a in targets],
        *[p.animate.scale(0.02).move_to(a.get_center()).set_stroke(opacity=0)
          for p, (_, a) in zip(pulses, targets)],
        *[FadeOut(m) for m in fade],
        run_time=0.4,
    )
    scene.remove(*pulses)


def emit(scene, x, atom, extras=(), also=()):
    """Stimulated emission: one photon arrives and two leave.

    Both leave in the mode of the driving field, so the pair climbs together
    and the atom recoils the other way, by -hbar k.

    `also` is (x, atom) pairs driven by twins of the same pulse, as in absorb.
    """
    y0 = -config.frame_y_radius - 0.6
    targets = [(x, atom), *also]
    incoming = [make_laser_pulse(tx, y0) for tx, _ in targets]
    scene.add(*incoming)

    rise = atom.get_center()[1] - y0
    scene.play(
        *[p.animate.shift(UP * (a.get_center()[1] - y0)) for p, (_, a) in zip(incoming, targets)],
        *[FadeIn(m) for m in extras],
        rate_func=linear,
        run_time=rise / PULSE_SPEED,
    )

    pairs = [
        VGroup(*[make_laser_pulse(tx + dx, a.get_center()[1] + 1.15) for dx in (-0.22, 0.22)])
        for tx, a in targets
    ]
    scene.play(
        *[Flash(a, **FLASH_STYLE) for _, a in targets],
        *[FadeOut(p, scale=0.3) for p in incoming],
        *[FadeIn(pair, shift=UP * 0.25) for pair in pairs],
        run_time=0.5,
    )

    y = atom.get_center()[1] + 1.15
    climb = config.frame_y_radius + 1.4 - y
    scene.play(
        *[pair.animate.shift(UP * climb) for pair in pairs],
        rate_func=linear,
        run_time=climb / PULSE_SPEED,
    )
    scene.remove(*pairs)


def draw_legs(scene, legs, fade=(), extra=()):
    """Move atoms along straight legs, drawing each trajectory in step.

    Every leg shares the same horizontal extent, so they all take the same
    run_time at speed V -- that is what keeps the kicked arms at 45 degrees.
    A Line created in step is used rather than a TracedPath because a
    TracedPath collapses once the point it follows stops moving.

    `extra` is for anything that has to advance over exactly the same stretch
    of flight, such as the phase an excited arm is accumulating as it goes.
    """
    anims = []
    for atom, start, end, color in legs:
        anims.append(atom.animate.move_to(end))
        anims.append(Create(Line(start, end, color=color, **TRAJECTORY_STYLE)))
    dx = abs(legs[0][2][0] - legs[0][1][0])
    scene.play(
        *anims,
        *extra,
        *[FadeOut(m) for m in fade],
        rate_func=linear,
        run_time=dx / V,
    )


def state_colors(atom, color):
    """Recolour an atom's body to match a new internal state, keeping the highlight."""
    return atom[0].animate.set_fill(color).set_stroke(lighten(color))


def state_label(tex, color, font_size=FONT_STATE):
    return MathTex(tex, font_size=font_size, color=lighten(color))


def arm_ket(excited, phase=None, font_size=FONT_LEGEND, stacked=False):
    """The state an arm is in: |g, p> or |e, p + hbar k>, in that state's colour.

    `phase` is the Tex of the phase the arm has picked up, written in front
    as e^{i(phase)} -- or over the ket, if `stacked`, where a leg has no room
    beside it for the whole line.
    """
    color = KICKED_COLOR if excited else ATOM_COLOR
    ket = r"|e,\, p + \hbar k\rangle" if excited else r"|g,\, p\rangle"
    if phase is None:
        return state_label(ket, color, font_size)
    factor = rf"e^{{i({phase})}}"
    if stacked:
        return VGroup(state_label(factor, color, font_size),
                      state_label(ket, color, font_size)).arrange(DOWN, buff=0.1)
    return state_label(rf"{factor}\,{ket}", color, font_size)


def fluorescence(atoms):
    """What fluoresce plays, unplayed: (halos, the animations lighting them).

    For a scene that has to play them alongside something else -- lab time
    running on, in a continuous one.
    """
    halos = VGroup(*[
        Circle(radius=atom.width * 0.85, stroke_width=0, fill_color=IMAGING_COLOR,
               fill_opacity=FLUORESCENCE_HALO_OPACITY).move_to(atom)
        for atom in atoms
    ])
    return halos, [
        *[FadeIn(h, scale=0.5) for h in halos],
        *[Flash(a, **FLUORESCENCE_FLASH) for a in atoms],
    ]


def fluoresce(scene, atoms, fade=(), run_time=0.8):
    """Atoms caught by an imaging pulse light up in its blue.

    The halo is the scattered light, and goes out again; the atoms stay.
    `fade` goes out with the halo: the pulse that did the imaging, say.
    """
    halos, light = fluorescence(atoms)
    scene.play(*light, run_time=run_time)
    scene.play(*[FadeOut(m) for m in (*halos, *fade)], run_time=0.5)
