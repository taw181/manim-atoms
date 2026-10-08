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
changes. That is a controlled-Z gate, and the scene runs it on |00>, |01>
and |11>.

The traps are on the left, seen from the side, and the three particles'
levels on the right, a molecule either side of the atom as in the traps.
Every population shown, as a disc on a level and as the particles' colours,
is computed from the gate's Hamiltonian (physics.molecule_gate) with the
paper's numbers for CaF and Rb, as is the pulse's envelope.

Not to scale: at a micrometre apart real tweezers overlap, and the atom's
is one of them. The Rydberg electron's orbit is to the gap's scale, a third
of it, though not to the atom's. The levels are schematic
(species.molecule_rydberg). The laser is drawn on the atom alone, though
the molecules would not notice it.

- MoleculeRydbergGate: a beat() once the traps are laid out, then after
  the move, the levels, the field, and each of the three runs of the gate,
  and on the last caption.
"""

import numpy as np
from manim import *

from manim_atoms.tweezers.style import *
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
    gate_populations,
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
# The traps take the left of the frame and the levels the right; the pulse's
# envelope and the gate's table go under the traps, where the levels leave
# room (only the atom's column reaches down to |g>). The traps are drawn
# large, three of them, so the particles and what happens between them show.
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
MG_PLOT = np.array([-6.3, -3.1, 0.0])  # the envelope's origin
MG_PLOT_SIZE = (2.4, 0.9)  # the pulse's length and its peak, as drawn
MG_TABLE = np.array([-1.75, -1.75, 0.0])  # the middle of the table's top row
MG_TABLE_ROW = 0.52  # between its rows
MG_PULSE_TIME = 4.0  # seconds a gate pulse takes on screen
MG_PREPARE_TIME = 1.2  # a microwave pulse on a qubit
MG_TUNE_TIME = 1.5  # the field coming on
MG_SWITCH_TIME = 0.5  # the atom's trap going off or on
MG_SETTLE = 0.6  # the pause before a stop


class MoleculeRydbergGate(Scene):
    """Two molecules are brought either side of an atom by their tweezers,
    a field tunes them into resonance, and a 2 pi laser pulse on the atom
    is run for |00>, |01> and |11>: a controlled-Z. One beat() per step."""

    def beat(self):
        """The pause after each step: nothing here, a click on the slide version."""

    # --- what everything is drawn from ---------------------------------------

    def populations(self):
        """Each particle's populations now: (molecule, atom, molecule)."""
        return gate_populations(self.first.get_value(), self.second.get_value(),
                                self.clock.get_value())

    def drive(self):
        """The laser's Rabi frequency now, as a share of its peak."""
        return float(rabi_frequency(self.clock.get_value()) / rabi_frequency(GATE_TIME / 2))

    def coupled(self):
        """How strongly each molecule exchanges with the atom: it has to be
        in |1>, and the field on."""
        return [q.get_value() * self.field.get_value() for q in (self.first, self.second)]

    # --- the pieces ----------------------------------------------------------

    def build(self):
        """Lay everything out, unadded."""
        self.first, self.second = ValueTracker(0), ValueTracker(0)  # each molecule: 0 or 1
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
            .next_to(MG_PLOT + UP * height, UL, buff=0.05).shift(RIGHT * 0.55),
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
        for molecule, kets, q, at, populations in zip(
                self.molecules, self.kets, (self.first, self.second), where[::2],
                (first, second)):
            color = state_mix(MOLECULE_COLORS, populations)
            molecule.set_fill(color).set_stroke(lighten(color)).move_to(at)
            for ket, share in zip(kets, (1 - q.get_value(), q.get_value())):
                ket.set_opacity(share).move_to(at + DOWN * MG_KET_DROP)
        # The orbit is there as far as the atom is in either Rydberg state,
        # in the colour of whichever it is in.
        excited = atom[1] + atom[2]
        orbit = state_mix(RYDBERG_ATOM_COLORS[1:], atom[1:]) if excited > 1e-6 else None
        self.atom.set_excitation(excited, orbit).move_to(where[1])
        for link, share in zip(self.links, self.coupled()):
            link.set_stroke(opacity=share)

    def refresh_levels(self, _=None):
        """Redraw the level scheme from the same numbers."""
        microwave = [np.sin(PI * q.get_value()) for q in (self.first, self.second)]
        self.levels.tune(self.field.get_value()).show(*self.populations()).light(
            laser=self.drive(), exchange=self.coupled(), microwave=microwave)

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

    def pulse(self, before, after, rows):
        """Run the gate's pulse on the molecules as they are: the atom's trap
        off under the caption ``before``, the pulse, then the trap back on
        and the table's ``rows`` filled in under ``after``."""
        self.play(self.say(before),
                  self.array.off.animate(run_time=MG_SWITCH_TIME).set_value(1))
        self.play(self.clock.animate.set_value(GATE_TIME), rate_func=linear,
                  run_time=MG_PULSE_TIME)
        self.play(self.say(after),
                  self.array.off.animate(run_time=MG_SWITCH_TIME).set_value(0),
                  *[FadeIn(self.rows[k], run_time=MG_SWITCH_TIME) for k in rows])
        self.wait(MG_SETTLE)
        self.beat()
        self.clock.set_value(0)
        self.update_mobjects(0)

    def construct(self):
        self.build()
        array, levels = self.array, self.levels
        self.add(self.first, self.second, self.clock, self.field, *array.trackers, array)
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

        self.refresh_light()
        self.add(self.beam, self.beam_name)
        self.add(self.links, self.particles)  # the particles over the light
        self.beam.add_updater(self.refresh_light)
        self.play(FadeIn(self.plot), FadeIn(self.plot_marker))
        self.pulse(r"both in $|0\rangle$: a $2\pi$ laser pulse takes the atom to "
                   r"$|r\rangle$ and back",
                   r"the state comes back with its sign changed", rows=[0])

        self.play(self.say(r"microwaves put one molecule in $|1\rangle$"),
                  self.second.animate(run_time=MG_PREPARE_TIME).set_value(1))
        self.pulse(r"it exchanges an excitation with the atom, which keeps the atom "
                   r"out of $|r\rangle$",
                   r"the state comes back as it was, whichever molecule it is", rows=[1, 2])

        self.play(self.say(r"microwaves put the other in $|1\rangle$ too"),
                  self.first.animate(run_time=MG_PREPARE_TIME).set_value(1))
        self.pulse(r"the atom is kept out of $|r\rangle$ again",
                   r"and the state comes back as it was", rows=[3])

        self.play(self.say(r"a controlled-$Z$ gate between the molecules, "
                           r"in about a microsecond"))
        self.wait(MG_SETTLE)
        self.beat()
