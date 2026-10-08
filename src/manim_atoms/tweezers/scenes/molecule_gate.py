"""A gate between two molecules in tweezers, through a Rydberg atom.

The scheme is Zhang and Tarbutt's (PRX Quantum 3, 030340 (2022), Sec. II).
Two polar molecules, each a qubit in |0> and |1>, sit in tweezers either
side of an atom in a third. The tweezers bring the molecules to about a
micrometre from the atom. An electric field tunes the atom's Rydberg
transition |R> <-> |r> into resonance with the molecules' |1> <-> |2>, so a
molecule in |1> and the atom in |r> exchange an excitation. With the atom's
trap off, a 2 pi laser pulse then drives the atom |g> <-> |r>. With both
molecules in |0> the atom goes to |r> and back and the state changes sign;
with either in |1> the exchange keeps the atom out of |r>, and nothing
changes. That is a controlled-Z gate.

The scene shows it in two halves. First how it works, on |00> and |01>.
With both molecules in |0> the laser turns the atom through a full 2 pi
rotation, |g> to |r> and back, drawn as the atom's own Bloch vector going
once round; and a 2 pi rotation of a two-level system multiplies its state
by -1, so the whole system comes back with its phase shifted by pi. That is
drawn as a dial of the whole state's overlap with where it started: its
hand shrinks to nothing at the pulse's middle and comes back pointing at
-1. With a molecule in |1> the exchange stops the atom making the
rotation, its vector hardly leaves |g>, and the hand stays at +1: no phase
shift. Then what that does, which a sign on a whole state cannot show:
each molecule's qubit is drawn as a Bloch vector, and the pulse is run with
the second molecule in |0> + |1>. With the first in |0> the second's vector
is turned over, to |0> - |1>; with the first in |1> it is left alone; and
with both in |0> + |1> each one's sign depends on the other, so both
vectors shrink to nothing: the molecules are entangled. A vector also
shrinks in the middle of a pulse, while its molecule is entangled with the
atom.

The traps are on the left, seen from the side, and the three particles'
levels on the right, a molecule either side of the atom as in the traps.
Everything shown of the state (the discs on the levels, the particles'
colours, the Rydberg orbit, the Bloch vectors) is computed from the gate's
Hamiltonian (physics.molecule_gate) with the paper's numbers for CaF and
Rb, as is the pulse's envelope.

Not to scale: at a micrometre apart real tweezers overlap, and the atom's
is one of them. The Rydberg electron's orbit is to the gap's scale, a third
of it, though not to the atom's. The levels are schematic
(species.molecule_rydberg). The laser is drawn on the atom alone, though
the molecules would not notice it.

- MoleculeRydbergGate: a beat() once the traps are laid out, then after
  the move, the levels, the field, a beat() for the atom's qubit and the
  phase dial, the two runs on basis states, the second molecule put in a
  superposition, the three runs that follow, and on the
  last caption.
"""

import numpy as np
from manim import *

from manim_atoms.tweezers.style import *
from manim_atoms.core.bloch import BlochVector, BlochView, bloch_sphere
from manim_atoms.core.optics import gaussian_band
from manim_atoms.core.primitives import RydbergAtom, make_molecule, state_label, state_mix
from manim_atoms.core.projection import TiltedView
from manim_atoms.species.molecule_rydberg import (
    EXCHANGE_COLOR,
    MOLECULE_COLORS,
    RYDBERG_ATOM_COLORS,
    GateLevels,
)
from manim_atoms.tweezers.physics.molecule_gate import (
    GATE_TIME,
    bloch_vector,
    atom_bloch_vector,
    gate_populations,
    gate_state,
    overlap,
    qubit,
    rabi_frequency,
)
from manim_atoms.tweezers.physics.rearrangement import Plan, longest_move
from manim_atoms.tweezers.tools.beams import TW_ELEVATION, hourglass_trap
from manim_atoms.tweezers.tools.tweezer_array import (
    TweezerArray,
    heading,
    next_step,
    step_caption,
)

# --- molecule-gate geometry --------------------------------------------------
# The traps take the left of the frame and the levels the right. Under each
# molecule's trap goes its qubit: a ket at first, then a Bloch sphere. The
# gate's table and the pulse's envelope go under the molecules' columns of
# the levels, which stop at |0>; only the atom's reaches down to |g>. The
# traps are drawn large, three of them, so the particles and what happens
# between them show.
MG_CENTER = np.array([-3.9, 0.8, 0.0])  # the atom's trap
MG_SCALE = 2.0  # scene units per unit of the array's own
MG_APART = 1.15  # a molecule's trap from the atom's, at the start
MG_CLOSE = 0.6  # and brought together: "1 um" in the paper's example
MG_PARTICLE_RADIUS = 0.15
# The Rydberg orbit's outer edge, 2 n*^2 a_0: 0.33 um for the paper's 59s,
# against the 1 um to a molecule.
MG_RYDBERG_RADIUS = MG_CLOSE * MG_SCALE / 3
MG_KET_DROP = 1.5  # a molecule's qubit state, below its trap's beam
MG_FIELD = MG_CENTER + LEFT * 2.5  # the field's arrow, left of the traps, along their axis
MG_FIELD_LENGTH = 1.3
# The laser comes in steeply, between the molecules' beams.
MG_LASER_ANGLE = 70 * DEGREES
MG_LASER_REACH = 1.25  # drawn this far either side of the atom
MG_LASER_WIDTH = 0.22
MG_LEVELS = np.array([2.9, -0.2, 0.0])  # the level scheme's centre
MG_HEADING = np.array([-6.6, 3.6, 0.0])  # the heading's upper left corner
MG_PLOT = np.array([4.3, -3.2, 0.0])  # the envelope's origin, under the second molecule's levels
MG_PLOT_SIZE = (2.2, 0.8)  # the pulse's length and its peak, as drawn
MG_TABLE = np.array([0.55, -1.95, 0.0])  # the arrow of the table's top row, under the first's
MG_TABLE_ROW = 0.5  # between its rows
MG_SPHERE_DROP = 2.45  # a molecule's Bloch sphere, below its trap
MG_SPHERE_RADIUS = 0.6
# The phase dial of the whole state, left of the molecule spheres' column and
# under the field's arrow; the atom's own sphere goes under its trap.
MG_DIAL = np.array([-5.95, -1.75, 0.0])
MG_DIAL_RADIUS = 0.5
MG_SIGN_BUFF = 0.12  # the + and - at the ends of a sphere's equator, off its outline
MG_PULSE_TIME = 4.0  # seconds a gate pulse takes on screen
MG_PREPARE_TIME = 1.4  # a microwave pulse on a qubit
MG_TUNE_TIME = 1.5  # the field coming on
MG_SWITCH_TIME = 0.5  # the atom's trap going off or on
MG_SETTLE = 0.6  # the pause before a stop


class MoleculeRydbergGate(Scene):
    """Two molecules are brought either side of an atom by their tweezers,
    a field tunes them into resonance, and a 2 pi laser pulse on the atom
    is run on basis states, to show how it works, and then on
    superpositions, to show the controlled-Z it is. One beat() per step."""

    def beat(self):
        """The pause after each step: nothing here, a click on the slide version."""

    # --- what everything is drawn from ---------------------------------------

    def state(self):
        """The three particles' joint state now."""
        return gate_state(qubit(self.first.get_value()), qubit(self.second.get_value()),
                          self.clock.get_value())

    def populations(self):
        """Each particle's populations now: (molecule, atom, molecule)."""
        return gate_populations(self.state())

    def drive(self):
        """The laser's Rabi frequency now, as a share of its peak."""
        return float(rabi_frequency(self.clock.get_value()) / rabi_frequency(GATE_TIME / 2))

    def coupled(self):
        """How strongly each molecule exchanges with the atom: by its
        amplitude out of |0>, and as far as the field is on."""
        first, _, second = self.populations()
        return [np.sqrt(max(1 - molecule[0], 0.0)) * self.field.get_value()
                for molecule in (first, second)]

    # --- the pieces ----------------------------------------------------------

    def build(self):
        """Lay everything out, unadded."""
        # Each molecule's qubit before the pulse, as the area of the microwave
        # pulse that makes it from |0>: 0 is |0>, pi is |1>, pi / 2 is |0> + |1>.
        self.first, self.second = ValueTracker(0), ValueTracker(0)
        self.microwaves = [ValueTracker(0), ValueTracker(0)]  # on each molecule, 0 to 1
        self.kets_shown = ValueTracker(1)  # the kets under the traps, until the spheres
        self.clock = ValueTracker(0)  # how far into the pulse, in microseconds
        self.field = ValueTracker(0)  # the electric field: 1 is resonance
        sites = np.array([[-MG_APART, 0.0], [0.0, 0.0], [MG_APART, 0.0]])
        self.view = TiltedView(MG_CENTER, MG_SCALE, TW_ELEVATION)
        self.array = TweezerArray(sites, self.view, draw_trap=hourglass_trap)
        # The molecules' traps are the ones kept and moved; the atom's stays
        # where it is, and is the one that goes off.
        self.plan = Plan(kept=np.array([0, 2]), start=sites[[0, 2]],
                         end=np.array([[-MG_CLOSE, 0.0], [MG_CLOSE, 0.0]]),
                         dropped=np.array([], dtype=int))

        self.molecules = [make_molecule(MOLECULE_COLORS[0], MG_PARTICLE_RADIUS)
                          for _ in range(2)]
        self.atom = RydbergAtom(MG_PARTICLE_RADIUS, MG_RYDBERG_RADIUS)
        self.kets = [[state_label(rf"|{k}\rangle", MOLECULE_COLORS[k]) for k in (0, 1)]
                     for _ in range(2)]
        self.particles = VGroup(*self.molecules, self.atom,
                                *[ket for pair in self.kets for ket in pair])
        self.links = VGroup(*[
            Line(self.view.point([side * MG_CLOSE, 0]) - side * RIGHT * 1.6 * MG_PARTICLE_RADIUS,
                 MG_CENTER + side * RIGHT * 1.6 * MG_PARTICLE_RADIUS,
                 color=EXCHANGE_COLOR, **COUPLING_LINK_STYLE)
            for side in (-1, 1)])

        self.levels = GateLevels(MG_LEVELS)

        self.spheres, self.vectors = VGroup(), []
        for side in (-1, 1):
            view = BlochView(self.view.point([side * MG_CLOSE, 0]) + DOWN * MG_SPHERE_DROP,
                             MG_SPHERE_RADIUS)
            sphere = bloch_sphere(
                view, *[state_label(rf"|{k}\rangle", MOLECULE_COLORS[k], FONT_LEGEND)
                        for k in (0, 1)])
            # the equator's ends: |0> + |1> to the right, |0> - |1> to the left
            signs = VGroup(*[MathTex(sign, font_size=FONT_LEGEND, color=STEP_COLOR)
                             .next_to(sphere[0], way, buff=MG_SIGN_BUFF)
                             for sign, way in (("+", RIGHT), ("-", LEFT))])
            self.spheres.add(VGroup(sphere, signs))
            self.vectors.append(BlochVector(view))
        self.qubits = VGroup(self.spheres, *self.vectors)

        # the atom's own qubit, |g> up and |r> down, seen so that its turn about
        # x goes round in the picture's plane
        atom_view = BlochView(self.view.point([0, 0]) + DOWN * MG_SPHERE_DROP, MG_SPHERE_RADIUS)
        atom_sphere = bloch_sphere(
            atom_view, *[state_label(tex, RYDBERG_ATOM_COLORS[k], FONT_LEGEND)
                         for tex, k in ((r"|g\rangle", 0), (r"|r\rangle", 2))])
        self.atom_vector = BlochVector(atom_view)

        # the whole state's phase: a hand from the dial's centre to its overlap
        # with the start, so a shrinking hand is the state turning away from it
        ring = Circle(radius=MG_DIAL_RADIUS, **BLOCH_STYLE).move_to(MG_DIAL)
        cross = VGroup(*[Line(MG_DIAL + d * MG_DIAL_RADIUS, MG_DIAL - d * MG_DIAL_RADIUS,
                              stroke_width=1, color=GUIDE_COLOR, stroke_opacity=0.5)
                         for d in (RIGHT, UP)])
        ends = VGroup(*[MathTex(tex, font_size=FONT_LEGEND, color=PLOT_FOREGROUND)
                        .next_to(MG_DIAL + way * MG_DIAL_RADIUS, way, buff=0.08)
                        for tex, way in (("+1", RIGHT), ("-1", LEFT))])
        label = Tex(r"phase of the\\whole system", font_size=FONT_AXIS,
                    color=PLOT_FOREGROUND).next_to(ring, DOWN, buff=0.45)
        self.dial_hand = Arrow(MG_DIAL, MG_DIAL + RIGHT * MG_DIAL_RADIUS, buff=0,
                               color=PLOT_FOREGROUND, stroke_width=4,
                               max_tip_length_to_length_ratio=0.35)
        self.basis = VGroup(atom_sphere, self.atom_vector, ring, cross, ends, label,
                            self.dial_hand)

        arrow = Arrow(MG_FIELD + DOWN * MG_FIELD_LENGTH / 2, MG_FIELD + UP * MG_FIELD_LENGTH / 2,
                      **STATIC_FIELD_ARROW_STYLE)
        self.field_arrow = VGroup(arrow, MathTex(r"\vec{E}", font_size=FONT_ANNOTATION,
                                                 color=STATIC_FIELD_COLOR)
                                  .next_to(arrow, LEFT, buff=0.15))

        along = np.array([np.cos(MG_LASER_ANGLE), np.sin(MG_LASER_ANGLE), 0.0])
        self.beam = gaussian_band(MG_CENTER - along * MG_LASER_REACH,
                                  MG_CENTER + along * MG_LASER_REACH,
                                  MG_LASER_WIDTH, LASER_COLOR, opacity=ADDRESSING_BEAM_OPACITY)
        self.beam_name = MathTex(r"\Omega_L", font_size=FONT_ANNOTATION, color=LASER_COLOR)
        self.beam_name.next_to(MG_CENTER + along * MG_LASER_REACH, UP, buff=0.12)

        width, height = MG_PLOT_SIZE
        curve = VMobject(color=LASER_COLOR, stroke_width=ENVELOPE_STROKE_WIDTH)
        curve.set_points_smoothly([
            MG_PLOT + RIGHT * width * s + UP * height * np.sin(PI * s)
            for s in np.linspace(0, 1, 41)])
        axis = Line(MG_PLOT + LEFT * 0.15, MG_PLOT + RIGHT * (width + 0.15),
                    **ENVELOPE_AXIS_STYLE)
        self.plot = VGroup(
            axis, curve,
            MathTex(r"\Omega_L(t)", font_size=FONT_AXIS, color=LASER_COLOR)
            .next_to(MG_PLOT + UP * height, UR, buff=0.05),
            Tex(r"$2\pi$ pulse, $1.25\,\mu$s", font_size=FONT_AXIS, color=PLOT_FOREGROUND)
            .next_to(axis, DOWN, buff=0.15))
        self.plot_marker = Dot(MG_PLOT, radius=ENVELOPE_MARKER_RADIUS, color=lighten(LASER_COLOR))

        self.rows = VGroup(*[self.table_row(*row, k) for k, row in enumerate((
            ("00", ["-"]), ("01", []), ("10", []), ("11", [])))])

        self.title = heading("A gate between two molecules, through a Rydberg atom")
        self.title.move_to(MG_HEADING, aligned_edge=UL)
        self.note = step_caption("two molecules and an atom, each in its own tweezer",
                                 self.title)

    def table_row(self, qubits, sign, k):
        """One row of the gate's table: the input, and what comes back, with
        a sign change in the laser's colour, since the laser's pulse made it."""
        row = MathTex(rf"|{qubits}\rangle", r"\;\to\;", *sign, rf"|{qubits}\rangle",
                      font_size=FONT_LEGEND, color=PLOT_FOREGROUND)
        row[2:-1].set_color(LASER_COLOR)
        # lined up on the arrow, so the signed row does not stand out of line
        return row.shift(MG_TABLE + DOWN * k * MG_TABLE_ROW - row[1].get_center())

    def say(self, text):
        """The animation that swaps the caption for ``text``."""
        self.note, swap = next_step(self.note, text, self.title)
        return swap

    # --- redrawing from the trackers -----------------------------------------

    def refresh_particles(self, _=None):
        """Put each particle on its trap, in its state's colours."""
        first, atom, second = self.populations()
        where = [self.view.point(xy) for xy in self.array.trap_positions()]
        shown = self.kets_shown.get_value()
        for molecule, kets, at, populations in zip(
                self.molecules, self.kets, where[::2], (first, second)):
            color = state_mix(MOLECULE_COLORS, populations)
            molecule.set_fill(color).set_stroke(lighten(color)).move_to(at)
            for ket, share in zip(kets, (populations[0], 1 - populations[0])):
                ket.set_opacity(share * shown).move_to(at + DOWN * MG_KET_DROP)
        # The orbit is there as far as the atom is in either Rydberg state,
        # in the colour of whichever it is in.
        excited = atom[1] + atom[2]
        orbit = state_mix(RYDBERG_ATOM_COLORS[1:], atom[1:]) if excited > 1e-6 else None
        self.atom.set_excitation(excited, orbit).move_to(where[1])
        for link, share in zip(self.links, self.coupled()):
            link.set_stroke(opacity=share)

    def refresh_levels(self, _=None):
        """Redraw the level scheme from the same numbers."""
        self.levels.tune(self.field.get_value()).show(*self.populations()).light(
            laser=self.drive(), exchange=self.coupled(),
            microwave=[glow.get_value() for glow in self.microwaves])

    def refresh_qubits(self, _=None):
        """Point each molecule's Bloch vector where its qubit is, in the
        molecule's colour. The sphere is seen with the qubit's x axis to the
        right, so |0> + |1> points right and |0> - |1> left."""
        state = self.state()
        first, _, second = gate_populations(state)
        for k, (vector, populations) in enumerate(zip(self.vectors, (first, second))):
            x, y, z = bloch_vector(state, k)
            vector.point_to([-y, x, z], state_mix(MOLECULE_COLORS, populations))

    def refresh_basis(self, _=None):
        """Point the atom's Bloch vector where its qubit is, and the dial's
        hand at the whole system's overlap with its start."""
        state = self.state()
        _, atom, _ = gate_populations(state)
        self.atom_vector.point_to(
            atom_bloch_vector(state),
            state_mix((RYDBERG_ATOM_COLORS[0], RYDBERG_ATOM_COLORS[2]), (atom[0], atom[2])))
        z = overlap(qubit(self.first.get_value()), qubit(self.second.get_value()),
                    self.clock.get_value())
        # a hand that has shrunk to nothing stays a short stub, not a broken arrow
        end = MG_DIAL + MG_DIAL_RADIUS * np.array([z.real, z.imag, 0.0])
        if np.linalg.norm(end - MG_DIAL) < 0.08:
            end = MG_DIAL + RIGHT * 0.08 * (1 if z.real >= 0 else -1)
        self.dial_hand.put_start_and_end_on(MG_DIAL, end)

    def refresh_light(self, _=None):
        """The laser's beam as bright as its Rabi frequency, and the marker
        on its envelope."""
        drive, (width, height) = self.drive(), MG_PLOT_SIZE
        for layer in self.beam:
            layer.set_fill(opacity=ADDRESSING_BEAM_OPACITY / len(self.beam) * drive)
        self.beam_name.set_opacity(drive)
        self.plot_marker.move_to(
            MG_PLOT + RIGHT * width * self.clock.get_value() / GATE_TIME + UP * height * drive)

    # --- the steps -----------------------------------------------------------

    def prepare(self, text, first=None, second=None):
        """Microwave pulses taking each molecule's qubit to the angle given
        (None leaves it alone), under the caption ``text``."""
        moves = []
        for tracker, glow, angle in zip((self.first, self.second), self.microwaves,
                                        (first, second)):
            if angle is not None:
                moves += [tracker.animate(run_time=MG_PREPARE_TIME).set_value(angle),
                          glow.animate(run_time=MG_PREPARE_TIME, rate_func=there_and_back)
                          .set_value(1)]
        self.play(self.say(text), *moves)

    def pulse(self, before, after, rows=(), leaves=None):
        """Run the gate's pulse on the molecules as they are: the atom's trap
        off under the caption ``before``, the pulse, then the trap back on
        and the table's ``rows`` filled in under ``after``.

        ``leaves`` is the pair of qubit angles the pulse leaves the molecules
        at, when it leaves each a state of its own: the clock goes back to
        nought on those, the same picture, ready for the next pulse."""
        self.play(self.say(before),
                  self.array.off.animate(run_time=MG_SWITCH_TIME).set_value(1))
        self.play(self.clock.animate.set_value(GATE_TIME), rate_func=linear,
                  run_time=MG_PULSE_TIME)
        self.play(self.say(after),
                  self.array.off.animate(run_time=MG_SWITCH_TIME).set_value(0),
                  *[FadeIn(self.rows[k], run_time=MG_SWITCH_TIME) for k in rows])
        self.wait(MG_SETTLE)
        self.beat()
        if leaves is not None:
            self.clock.set_value(0)
            for tracker, angle in zip((self.first, self.second), leaves):
                tracker.set_value(angle)
            self.update_mobjects(0)

    def construct(self):
        self.build()
        array, levels = self.array, self.levels
        self.add(self.first, self.second, self.clock, self.field, *self.microwaves,
                 self.kets_shown, *array.trackers, array)
        self.refresh_particles()
        self.links.set_stroke(opacity=0)
        self.play(FadeIn(self.title), FadeIn(self.note), FadeIn(self.particles),
                  array.on.animate.set_value(1))
        self.add(self.links, self.particles)
        self.particles.add_updater(self.refresh_particles)  # after the fade, never before
        self.wait(MG_SETTLE)
        self.beat()

        array.rearrange(self.plan)
        self.play(self.say(r"the tweezers bring the molecules to about 1\,$\mu$m from the atom"))
        self.play(array.moved.animate.set_value(1),
                  run_time=longest_move(self.plan) * MG_SCALE / TWEEZER_SPEED)
        self.wait(MG_SETTLE)
        self.beat()

        self.play(self.say(r"each molecule holds a qubit in $|0\rangle$ and $|1\rangle$; "
                           r"the atom has two Rydberg states"),
                  FadeIn(levels))
        levels.add_updater(self.refresh_levels)
        self.wait(MG_SETTLE)
        self.beat()

        self.play(self.say(r"an electric field tunes $|R\rangle \leftrightarrow |r\rangle$ "
                           r"into resonance with $|1\rangle \leftrightarrow |2\rangle$"),
                  GrowArrow(self.field_arrow[0]), FadeIn(self.field_arrow[1]))
        self.play(self.field.animate.set_value(1), run_time=MG_TUNE_TIME)
        self.play(FadeIn(levels.guides))
        self.wait(MG_SETTLE)
        self.beat()

        # how it works: on basis states, the atom is excited or it is not
        self.refresh_light()
        self.add(self.beam, self.beam_name)
        self.add(self.links, self.particles)  # the particles over the light
        self.beam.add_updater(self.refresh_light)
        self.refresh_basis()
        self.play(FadeIn(self.plot), FadeIn(self.plot_marker), FadeIn(self.basis),
                  self.say(r"the atom's qubit, and the phase of the whole system, now $+1$"))
        self.basis.add_updater(self.refresh_basis)
        self.wait(MG_SETTLE)
        self.beat()
        self.pulse(r"both in $|0\rangle$: the laser turns the atom through a "
                   r"$2\pi$ rotation",
                   r"a $2\pi$ rotation gives $-1$: the whole system is phase-shifted by $\pi$",
                   rows=[0], leaves=(0, 0))

        self.prepare(r"microwaves put one molecule in $|1\rangle$", second=PI)
        self.pulse(r"a molecule in $|1\rangle$ exchanges with the atom: no rotation",
                   r"no rotation, no phase shift: likewise for $|10\rangle$ and $|11\rangle$",
                   rows=[1, 2, 3], leaves=(0, PI))

        # what it does: a sign shows only in a superposition
        self.refresh_qubits()
        self.basis.remove_updater(self.refresh_basis)
        self.play(self.say(r"the phase shows only against a superposition, "
                           r"$|0\rangle \pm |1\rangle$"),
                  self.kets_shown.animate.set_value(0), FadeOut(self.basis),
                  FadeIn(self.qubits))
        self.qubits.add_updater(self.refresh_qubits)
        self.prepare(r"microwaves put the second molecule in $|0\rangle + |1\rangle$",
                     second=PI / 2)
        self.wait(MG_SETTLE)
        self.beat()

        self.pulse(r"the first in $|0\rangle$: the pulse changes the sign of the second's "
                   r"$|0\rangle$",
                   r"which turns its $|0\rangle + |1\rangle$ into $|0\rangle - |1\rangle$",
                   leaves=(0, -PI / 2))

        self.prepare(r"the first in $|1\rangle$, and the second in "
                     r"$|0\rangle + |1\rangle$ again", first=PI, second=PI / 2)
        self.pulse(r"now the atom is kept out of $|r\rangle$, whatever the second is in",
                   r"and the second comes back as it was", leaves=(PI, PI / 2))

        self.prepare(r"both in $|0\rangle + |1\rangle$", first=PI / 2)
        self.pulse(r"each one's sign now depends on the other",
                   r"neither is left a direction of its own: the two are entangled")

        self.play(self.say(r"a controlled-$Z$ gate between the molecules, "
                           r"in about a microsecond"))
        self.wait(MG_SETTLE)
        self.beat()
