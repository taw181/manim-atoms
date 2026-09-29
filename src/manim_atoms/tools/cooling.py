"""A magneto-optical trap drawn as a cartoon: its beams, coils and atom cloud.

The cooling stages differ in which light is on, how strong the field
gradient is and how hot and big the cloud is, so each of those is a knob
here: a beam set's intensity, the coils' gradient, the cloud's radius and
temperature. The level-scheme side of the story -- which transition the
light drives -- is SrLevels in aionanim.tools.sequence; SweepFan adds the
red MOT's frequency sweep to it. Upstream of the trap, Oven, AtomBeam,
make_push_beam and make_baffle draw where its atoms come from.
"""

import numpy as np
from manim import *

from aionanim.style import *
from aionanim.tools.sequence import LV_3P, LV_3P_X, TRANSITIONS


# --- the trap -------------------------------------------------------------
# Three counter-propagating pairs, one per axis. The third axis is the line
# of sight, so it is drawn slanted, the way a MOT is usually sketched.
MOT_AXES = (0, 90, 35)  # degrees
MOT_BEAM_REACH = 2.3  # how far each beam runs out from the trap centre
MOT_CHEVRON_AT = 0.7  # of the reach: where a beam's arrowhead sits
COIL_OFFSET = 1.45  # of each coil from the trap centre, along the axis
COIL_SIZE = (2.4, 0.45)
COIL_ARROW_LENGTH = 0.5
UP_BEAM_WIDTH = 0.6 * MOT_BEAM_WIDTH  # narrower, so it shows inside the down beam


# A slightly-off-axis view for beams that leave the page: a unit step out of
# the page (towards the viewer) is drawn as this short step down and to the
# left, and a beam is drawn wider at its near end than at its far one.
OBLIQUE_Z = np.array([-0.42, -0.30, 0.0])
MOT_BEAM_TAPER = 0.45  # fractional width change per unit of depth


def project(v):
    """A 3D direction (x right, y up, z out of the page) on the page."""
    v = np.asarray(v, dtype=float)
    return np.array([v[0], v[1], 0.0]) + v[2] * OBLIQUE_Z


def oblique_ring(center, radius, color=GUIDE_COLOR):
    """A circle in the plane across the push axis (y up, z out of the page),
    in the oblique view: the depth cue for beams that leave the page."""
    center = np.asarray(center, dtype=float)
    ts = np.linspace(0, TAU, 65)
    ring = VMobject(stroke_color=color, stroke_width=2, stroke_opacity=0.45)
    ring.set_points_smoothly([center + project([0, radius * np.cos(t), radius * np.sin(t)])
                              for t in ts])
    return ring


def chevron(direction, tip, color, size=MOT_BEAM_WIDTH * 0.45):
    """An open arrowhead: two strokes meeting at ``tip``, pointing along ``direction``."""
    d = normalize(direction)
    n = rotate_vector(d, PI / 2)
    return VMobject(stroke_color=color, stroke_width=MOT_BEAM_EDGE_WIDTH).set_points_as_corners(
        [tip - d * size + n * size, tip, tip - d * size - n * size]
    )


class MotBeams(VGroup):
    """Counter-propagating beam pairs crossing at ``center``, all one colour.

    Each beam is a translucent band with an arrowhead pointing in toward the
    atoms. ``set_intensity`` scales how bright they are drawn, so a ramp of
    the beam power is ``beams.animate.set_intensity(...)``.
    """

    def __init__(self, color, center, axes=MOT_AXES, reach=MOT_BEAM_REACH,
                 directions=None, **kwargs):
        """``axes`` are in-page angles in degrees. ``directions`` instead are
        3D unit vectors (z out of the page), drawn in the oblique view of
        ``project``: foreshortened, and tapering from near end to far."""
        super().__init__(**kwargs)
        center = np.array(center, dtype=float)
        self.bands = VGroup()
        self.heads = VGroup()
        for v in directions or ():
            d, depth = project(v), v[2]
            n = normalize(rotate_vector(d, PI / 2))
            corners = []
            for sign in (1, -1):
                half = MOT_BEAM_WIDTH / 2 * (1 + sign * MOT_BEAM_TAPER * depth)
                end = center + sign * d * reach
                corners.append((end + n * half, end - n * half))
                self.heads.add(chevron(
                    -sign * d, center + sign * d * reach * MOT_CHEVRON_AT, color,
                    size=MOT_BEAM_WIDTH * 0.45 * (1 + sign * MOT_BEAM_TAPER * depth),
                ))
            (a, b), (c, e) = corners
            self.bands.add(Polygon(a, c, e, b, stroke_width=0, fill_color=color))
        for angle in (axes if directions is None else ()):
            d = rotate_vector(RIGHT, angle * DEGREES)
            self.bands.add(
                Rectangle(width=2 * reach, height=MOT_BEAM_WIDTH, stroke_width=0,
                          fill_color=color)
                .rotate(angle * DEGREES).move_to(center)
            )
            for sign in (1, -1):
                self.heads.add(chevron(-sign * d, center + sign * d * reach * MOT_CHEVRON_AT,
                                        color))
        self.add(self.bands, self.heads)
        self.set_intensity(1.0)

    def set_intensity(self, intensity):
        self.bands.set_fill(opacity=MOT_BEAM_OPACITY * intensity)
        self.heads.set_stroke(opacity=MOT_BEAM_EDGE_OPACITY * intensity)
        return self


def make_up_beam(color, center, reach=MOT_BEAM_REACH):
    """The narrowband red MOT's seventh beam: from below only, holding the
    atoms up against gravity. Brighter than the MOT beams it rides inside,
    because it is the unbalanced one."""
    center = np.array(center, dtype=float)
    band = Rectangle(width=UP_BEAM_WIDTH, height=reach, stroke_width=0,
                     fill_color=color, fill_opacity=2 * MOT_BEAM_OPACITY)
    band.move_to(center + DOWN * reach / 2)
    heads = VGroup(*[
        chevron(UP, center + DOWN * reach * f, color, size=UP_BEAM_WIDTH * 0.45)
        for f in (0.35, 0.5)
    ])
    return VGroup(band, heads)


class Coils(VGroup):
    """An anti-Helmholtz pair above and below the trap, with the current
    running opposite ways round them. How heavily they are drawn stands for
    the field gradient: ``set_gradient(COIL_STRONG_WIDTH)`` or ``COIL_WEAK_WIDTH``."""

    def __init__(self, center, width=COIL_STRONG_WIDTH, **kwargs):
        super().__init__(**kwargs)
        center = np.array(center, dtype=float)
        self.loops = VGroup()
        self.currents = VGroup()
        for sign in (1, -1):
            loop = Ellipse(width=COIL_SIZE[0], height=COIL_SIZE[1], color=COIL_COLOR)
            loop.move_to(center + UP * sign * COIL_OFFSET)
            front = loop.get_bottom() + DOWN * 0.18
            self.currents.add(Arrow(
                front - RIGHT * sign * COIL_ARROW_LENGTH / 2,
                front + RIGHT * sign * COIL_ARROW_LENGTH / 2,
                buff=0, stroke_width=3, color=COIL_COLOR,
                max_tip_length_to_length_ratio=0.35,
            ))
            self.loops.add(loop)
        self.add(self.loops, self.currents)
        self.set_gradient(width)

    def set_gradient(self, width):
        self.loops.set_stroke(width=width)
        return self


def make_sawtooth(color, width=0.9, height=0.3, teeth=3):
    """The shape of the red MOT's frequency modulation."""
    pts = []
    for k in range(teeth):
        x0 = width * k / teeth - width / 2
        pts += [[x0, -height / 2, 0], [x0 + width / teeth, height / 2, 0]]
    return VMobject(stroke_color=color, stroke_width=3).set_points_as_corners(pts)


# --- the red MOT's frequency sweep, drawn on the level scheme -------------
# The modulated MOT's light is swept in a sawtooth from far red of the 689 nm
# line up to it, so atoms at every Doppler shift find it resonant somewhere in
# the sweep. On the diagram that is a fan of arrows ending on the line and
# just below it, with the lit one climbing the fan and dropping back. In
# SrLevels' own coordinates: add the fan to the diagram before scaling it.
FAN_COUNT = 4
FAN_STEP = 0.08  # between neighbouring arrows' ends
# Ends just short of the stack, so no end reads as 3P0, and no further left,
# or the fan swings across the 689 nm label.
FAN_END_X = LV_3P_X[0] - 0.22
FAN_TICK = 0.22  # the dashed marks the arrows end on
FAN_PERIOD = 1.2  # s, one sawtooth
FAN_IDLE_OPACITY = 0.2
FAN_SAWTOOTH_AT = (0.55, 1.95)


class SweepFan(VGroup):
    """The 689 nm light swept in a sawtooth, drawn as a fan of arrows.

    Runs by itself once added to the scene; ``shown`` (0 to 1) fades the whole
    fan, which is how a stage switches the sweep on and off.
    """

    def __init__(self, color=TRANSITION_689_COLOR, **kwargs):
        super().__init__(**kwargs)
        start = np.array([*TRANSITIONS["689"]["start"], 0.0])
        self.arrows = VGroup()
        self.ticks = VGroup()
        for k in range(FAN_COUNT):  # k = 0 is on resonance
            end = np.array([FAN_END_X, LV_3P[1] - k * FAN_STEP, 0.0])
            self.arrows.add(Arrow(
                start, end, buff=0, color=color, stroke_width=TRANSITION_ACTIVE_WIDTH - 2,
                tip_length=0.16, max_tip_length_to_length_ratio=0.1,
                max_stroke_width_to_length_ratio=20,
            ))
            self.ticks.add(DashedLine(end + LEFT * FAN_TICK / 2, end + RIGHT * FAN_TICK / 2,
                                      dash_length=0.04, stroke_width=2, color=color))
        self.sawtooth = make_sawtooth(color, width=0.7, height=0.25).move_to([*FAN_SAWTOOTH_AT, 0])
        self.add(self.arrows, self.ticks, self.sawtooth)
        self.shown = ValueTracker(0.0)
        self.t = 0.0
        self.add_updater(self._sweep)
        self._sweep(self, 0)

    def _sweep(self, m, dt):
        self.t += dt
        phase = (self.t / FAN_PERIOD) % 1
        lit = FAN_COUNT - 1 - int(phase * FAN_COUNT)  # from far red up to resonance
        shown = self.shown.get_value()
        for k, (arrow, tick) in enumerate(zip(self.arrows, self.ticks)):
            op = shown * (1.0 if k == lit else FAN_IDLE_OPACITY)
            arrow.set_opacity(op)
            tick.set_stroke(opacity=op)
        self.sawtooth.set_stroke(opacity=shown)


# --- the cloud ------------------------------------------------------------
# Every atom has a home in the cloud, scaled by the cloud's radius, and
# jiggles about it by an amount scaled by the square root of the temperature
# -- a sum of a few sinusoids at random frequencies and phases, so the
# motion is smooth, deterministic from the seed, and never stops. The atoms
# arrive from the left, decelerating into their homes, which is the trap
# loading. A few of them are the ones that leak into 3P2: they go dark and
# drift off while ``dark`` is up, and come back when it is brought down.
CLOUD_SPREAD = 0.45  # of a home point, in units of the radius
CLOUD_CLIP = 1.25
CLOUD_JITTER_TERMS = 3
CLOUD_JITTER_FREQ = (3.0, 8.0)  # rad/s
CLOUD_JITTER_SCALE = 0.14  # the jitter amplitude at temperature 1
CLOUD_ARRIVAL_STAGGER = 0.7  # of the loading time, the spread in arrival
CLOUD_LEAK_DRIFT = (1.0, 1.8)  # how far a dark atom wanders


class AtomCloud(VGroup):
    """A cloud of ``n`` atoms in a trap at ``center``.

    Knobs, all ValueTrackers: ``radius``, ``temperature`` (in units that put
    the jitter at CLOUD_JITTER_SCALE at temperature 1), ``arrived`` (0: all still
    off-screen to the left; 1: all loaded), ``dark`` (how far the leaking
    atoms have gone dark and drifted off) and ``glow`` (0 to 1 across
    ``palette``, the colour of the light the atoms scatter).

    ``source`` is where the atoms load from, if not from off-screen left;
    ``stretch`` scales the cloud's shape along x and y, e.g. for the cigar
    of a 2D MOT.
    """

    def __init__(self, n, center, palette, n_leak=12, radius=1.0, temperature=0.0,
                 source=None, stretch=(1.0, 1.0), seed=1, **kwargs):
        super().__init__(**kwargs)
        rng = np.random.default_rng(seed)
        self.center = np.array(center, dtype=float)
        self.palette = [ManimColor(c) for c in palette]

        home = rng.normal(scale=CLOUD_SPREAD, size=(n, 2))
        norms = np.linalg.norm(home, axis=1, keepdims=True)
        self.home = home * np.minimum(1, CLOUD_CLIP / norms) * np.array(stretch)
        if source is None:  # off-screen to the left, level with the trap
            self.start = np.column_stack([
                -config.frame_x_radius - 0.3 - rng.uniform(0, 1.5, n),
                self.center[1] + rng.normal(scale=0.2, size=n),
            ])
        else:  # all from one point, e.g. an oven's nozzle
            self.start = np.array(source, dtype=float)[:2] + rng.normal(scale=0.05, size=(n, 2))
        self.delay = rng.uniform(0, CLOUD_ARRIVAL_STAGGER, n)
        self.freq = rng.uniform(*CLOUD_JITTER_FREQ, size=(n, 2, CLOUD_JITTER_TERMS))
        self.phase = rng.uniform(0, TAU, size=(n, 2, CLOUD_JITTER_TERMS))
        self.leaking = np.zeros(n, dtype=bool)
        self.leaking[rng.choice(n, n_leak, replace=False)] = True
        angles = rng.uniform(0, TAU, n)
        self.drift = np.column_stack([np.cos(angles), np.sin(angles)]) * rng.uniform(
            *CLOUD_LEAK_DRIFT, size=(n, 1))

        self.radius = ValueTracker(radius)
        self.temperature = ValueTracker(temperature)
        self.arrived = ValueTracker(1.0)
        self.dark = ValueTracker(0.0)
        self.glow = ValueTracker(0.0)
        self.t = 0.0
        self.add(*[Dot(radius=CLOUD_DOT_RADIUS, stroke_width=0) for _ in range(n)])
        self.add_updater(self._move)
        self._move(self, 0)

    def _move(self, m, dt):
        self.t += dt
        jitter = np.sin(self.freq * self.t + self.phase).sum(axis=2)
        jitter *= CLOUD_JITTER_SCALE * np.sqrt(
            max(self.temperature.get_value(), 0) / CLOUD_JITTER_TERMS)
        # each atom's own share of the loading, eased so it slows as it's caught
        s = self.arrived.get_value() * (1 + CLOUD_ARRIVAL_STAGGER) - self.delay
        e = 1 - (1 - np.clip(s, 0, 1)) ** 3
        target = self.center[:2] + self.home * self.radius.get_value() + jitter
        xy = self.start + (target - self.start) * e[:, None]
        dark = self.dark.get_value()
        xy += self.drift * dark * self.leaking[:, None]

        lit = interpolate_color(*self.palette, self.glow.get_value())
        dimmed = interpolate_color(lit, DARK_ATOM_COLOR, dark)
        dim_opacity = 1 + (DARK_ATOM_OPACITY - 1) * dark
        for dot, p, leaking in zip(self.submobjects, xy, self.leaking):
            dot.move_to([p[0], p[1], 0])
            if leaking:
                dot.set_fill(dimmed, opacity=dim_opacity)
            else:
                dot.set_fill(lit, opacity=1)


# --- upstream of the MOT: oven, 2D MOT and push beam ----------------------
# The MOT loads from a 2D MOT in a chamber of its own, which is fed straight
# from the oven. A push beam along the 2D MOT's long axis sends the atoms it
# has caught on through a baffle -- the small hole that keeps the oven's gas
# load out of the science chamber -- as a steady stream into the MOT.
OVEN_SIZE = (0.9, 0.8)
OVEN_NOZZLE = (0.18, 0.35)  # the tube on top that the atoms leave by
BAFFLE_HEIGHT = 1.6
BAFFLE_GAP = 0.3
PUSH_BEAM_WIDTH = UP_BEAM_WIDTH
PUSH_CHEVRONS_AT = (0.25, 0.4)  # of the beam's length


class Oven(VGroup):
    """A crucible with a nozzle on top, open at ``nozzle`` (the point the
    atoms come out of). Drawn warm inside, because it is hot."""

    def __init__(self, nozzle, **kwargs):
        super().__init__(**kwargs)
        nozzle = np.array(nozzle, dtype=float)
        tube = Rectangle(width=OVEN_NOZZLE[0], height=OVEN_NOZZLE[1])
        tube.move_to(nozzle, aligned_edge=UP)
        body = RoundedRectangle(width=OVEN_SIZE[0], height=OVEN_SIZE[1], corner_radius=0.1)
        body.next_to(tube, DOWN, buff=0)
        for part in (body, tube):
            part.set_stroke(OVEN_COLOR, width=3)
            part.set_fill(OVEN_HEAT_COLOR, opacity=OVEN_HEAT_OPACITY)
        self.add(tube, body)


def make_push_beam(color, start, end):
    """The push beam: narrow and bright like the up beam, running from
    ``start`` to ``end`` with its arrowheads pointing the way it pushes."""
    start, end = np.array(start, dtype=float), np.array(end, dtype=float)
    d = end - start
    band = Rectangle(width=np.linalg.norm(d), height=PUSH_BEAM_WIDTH, stroke_width=0,
                     fill_color=color, fill_opacity=2 * MOT_BEAM_OPACITY)
    band.rotate(angle_of_vector(d)).move_to((start + end) / 2)
    heads = VGroup(*[
        chevron(d, start + d * f, color, size=PUSH_BEAM_WIDTH * 0.45)
        for f in PUSH_CHEVRONS_AT
    ])
    return VGroup(band, heads)


def make_baffle(center, height=BAFFLE_HEIGHT, gap=BAFFLE_GAP):
    """A wall across the beam line with a small hole in it at ``center``."""
    center = np.array(center, dtype=float)
    half = (height - gap) / 2
    return VGroup(*[
        Line(center + sign * UP * gap / 2, center + sign * UP * (gap / 2 + half),
             stroke_width=BAFFLE_WIDTH, color=BAFFLE_COLOR)
        for sign in (1, -1)
    ])


class AtomBeam(VGroup):
    """A steady stream of atoms from ``start`` to ``end``, where they are
    caught: each fades out over the last ``fade`` of the way.

    ``flow`` (a ValueTracker, off at 0 and on at 1) turns the source on and
    off; atoms already launched carry on either way, so switching it off
    lets the stream run dry. Atoms leave ``spread`` either side of the line,
    fanning out by ``divergence`` per unit travelled, and change colour from
    ``colors[0]`` to ``colors[1]`` along the way.
    """

    def __init__(self, start, end, colors, speed, rate, spread=0.08, divergence=0.0,
                 fade=0.6, seed=2, **kwargs):
        super().__init__(**kwargs)
        self.rng = np.random.default_rng(seed)
        self.origin = np.array(start, dtype=float)
        d = np.array(end, dtype=float) - self.origin
        self.length = np.linalg.norm(d)
        self.dir = d / self.length
        self.normal = rotate_vector(self.dir, PI / 2)
        self.colors = [ManimColor(c) for c in colors]
        self.speed, self.rate = speed, rate
        self.spread, self.divergence, self.fade = spread, divergence, fade
        n = int(np.ceil(2 * rate * self.length / (0.8 * speed))) + 2
        self.launched = np.full(n, -np.inf)
        self.offset = np.zeros(n)
        self.pace = np.ones(n)
        self.next = 0  # the pool slot the next atom takes
        self.next_launch = 0.0
        self.t = 0.0
        self.flow = ValueTracker(0.0)
        self.add(*[Dot(radius=CLOUD_DOT_RADIUS, stroke_width=0) for _ in range(n)])
        self.add_updater(self._move)
        self._move(self, 0)

    def _move(self, m, dt):
        self.t += dt
        while self.next_launch <= self.t:
            if self.flow.get_value() > 0.5:
                k = self.next
                self.launched[k] = self.next_launch
                self.offset[k] = self.rng.normal()
                self.pace[k] = self.rng.uniform(0.8, 1.2)
                self.next = (k + 1) % len(self.launched)
            self.next_launch += self.rng.uniform(0.5, 1.5) / self.rate
        s = (self.t - self.launched) * self.speed * self.pace
        for dot, sk, u in zip(self.submobjects, s, self.offset):
            if not 0 <= sk <= self.length:
                dot.set_fill(opacity=0)
                continue
            dot.move_to(self.origin + self.dir * sk
                        + self.normal * u * (self.spread + self.divergence * sk))
            dot.set_fill(interpolate_color(*self.colors, sk / self.length),
                         opacity=min(1.0, (self.length - sk) / self.fade))
