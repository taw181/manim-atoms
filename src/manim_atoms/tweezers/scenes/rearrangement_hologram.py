"""The hologram behind a rearrangement: the SLM's mask beside the array it
makes, repainted as the traps move.

TweezerRearrangement shows the traps sliding; this shows what is changed to
slide them. The mask on the left is the phase of the sum of every lit
trap's field. Switching a trap off takes its term out of the sum, and
moving a trap changes its term's grating, so the whole mask shifts a little
with every step of the move.

Each trap keeps one phase throughout, which is why the mask changes
smoothly. It is a plain sum, not the weighted Gerchberg-Saxton mask an
experiment would display (HologramIteration), so the traps it would make
are not quite evenly bright; the array on the right is drawn from the trap
positions, not computed from the mask.

- RearrangementHologram: a beat() on the loaded array and its mask, after
  the switching off, and after the move.
"""

import numpy as np
from manim import *

from manim_atoms.tweezers.style import *
from manim_atoms.core.holography import illumination, pupil_grid, spot_phase
from manim_atoms.core.optics import PhaseMask, phase_wheel, round_aperture
from manim_atoms.core.primitives import fluoresce
from manim_atoms.core.projection import TiltedView
from manim_atoms.tweezers.physics.rearrangement import (
    load_sites,
    longest_move,
    plan_rearrangement,
    square_sites,
)
from manim_atoms.tweezers.tools.holograms import HG_N, HG_SEED, panel_label, spots_from_sites
from manim_atoms.tweezers.tools.tweezer_array import (
    TW_COLS,
    TW_FILL,
    TW_PITCH,
    TW_ROWS,
    TW_SEED,
    TW_TARGET,
    TweezerArray,
    heading,
    next_step,
    step_caption,
)

# --- hologram-and-array geometry ---------------------------------------------
# The mask on the left, the array on the right, the same height.
RH_MASK = np.array([-3.6, -0.6, 0.0])
RH_ARRAY = np.array([3.4, -0.6, 0.0])
RH_SIZE = 4.6  # the mask's height
RH_SCALE = 1.05  # scene units per unit of the array's own
RH_HEADING = np.array([-6.6, 3.6, 0.0])
RH_OFF_TIME = 1.2
RH_SETTLE = 0.6


class RearrangementHologram(Scene):
    """The SLM's mask beside the array, repainted every frame as the unwanted
    traps go out and the rest move. A beat() on the loaded array, after the
    switching off and after the move."""

    def beat(self):
        """The pause after each step: nothing here, a click on the slide version."""

    def construct(self):
        sites = square_sites(TW_ROWS, TW_COLS, TW_PITCH)
        targets = square_sites(*TW_TARGET, TW_PITCH)
        loaded = load_sites(len(sites), TW_FILL, np.random.default_rng(TW_SEED))
        plan = plan_rearrangement(sites, loaded, targets)
        array = TweezerArray(sites, TiltedView(RH_ARRAY, RH_SCALE)).load(loaded)
        array.on.set_value(1)
        array.filled.set_value(1)
        array.redraw()

        x, y, rho, _ = pupil_grid(HG_N)
        amplitude = illumination(rho)
        aperture = round_aperture(HG_N)
        phases = np.random.default_rng(HG_SEED).uniform(0, TAU, len(sites))

        def hologram():
            return spot_phase(x, y, spots_from_sites(array.trap_positions(), TW_PITCH),
                              phases, array.trap_powers())

        mask = PhaseMask(hologram(), aperture).set(height=RH_SIZE).move_to(RH_MASK)
        mask.add_updater(lambda m: m.paint(hologram()))
        wheel = phase_wheel(0.4).next_to(mask, DL, buff=-0.3)
        mask_label = panel_label("SLM: phase", mask)
        array_label = Tex("focal plane", font_size=FONT_STEP, color=STEP_COLOR)
        array_label.move_to([RH_ARRAY[0], mask_label.get_y(), 0])
        labels = VGroup(mask_label, array_label)
        title = heading("Rearranging by updating the hologram").move_to(RH_HEADING, aligned_edge=UL)
        note = step_caption("one grating per trap, summed", title)

        self.add(*array.trackers, array, mask, wheel, labels, title, note)
        self.wait(RH_SETTLE)
        self.beat()

        fluoresce(self, array.atoms)
        array.rearrange(plan)
        note, swap = next_step(note, "a trap switched off leaves the sum", title)
        self.play(swap, array.off.animate(run_time=RH_OFF_TIME).set_value(1),
                  array.ringed.animate(run_time=RH_OFF_TIME).set_value(1))
        self.wait(RH_SETTLE)
        self.beat()

        note, swap = next_step(note, "a trap moved changes its grating", title)
        self.play(swap)
        self.play(array.moved.animate.set_value(1),
                  run_time=longest_move(plan) * RH_SCALE / TWEEZER_SPEED * 2)
        self.play(array.ringed.animate.set_value(0), run_time=0.4)
        self.wait(RH_SETTLE)
        self.beat()
