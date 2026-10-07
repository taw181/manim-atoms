"""Rearranging a tweezer array by updating its hologram, seen from above.

A tweezer array loads at random: each trap catches one atom or none, about
half and half. An image says which, the empty traps and the spare atoms'
traps are switched off, and the hologram on the SLM is then updated step by
step so that every remaining trap slides, with its atom, to a site of the
block wanted. All the traps move at once.

The traps are drawn as the spots they make in the focal plane, as bright as
their power, and the atoms as the house discs. Nothing is to scale: a real
trap's waist is a tenth of the spacing.

- TweezerRearrangement: one loading, rearranged. A beat() once the traps
  are on, then after the loading, the image, the switching off, the move
  and the second image.
- TweezerRearrangementLoop: three loadings one after another, each released
  at the end. It begins and ends on the empty array, so the clip loops.
"""

import numpy as np
from manim import *

from manim_atoms.tweezers.style import *
from manim_atoms.core.primitives import fluoresce
from manim_atoms.core.projection import TiltedView
from manim_atoms.tweezers.physics.rearrangement import (
    load_sites,
    longest_move,
    plan_rearrangement,
    square_sites,
)
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

# --- rearrangement geometry --------------------------------------------------
# The array fills the frame under the heading. The heading and the step
# under it sit in the upper left corner, clear of the array's top row.
TR_CENTER = np.array([0.6, -0.55, 0.0])  # of the array
TR_SCALE = 1.3  # scene units per unit of the array's own
TR_HEADING = np.array([-6.6, 3.6, 0.0])  # the heading's upper left corner
TR_ON_TIME = 1.0  # the traps coming on
TR_LOAD_TIME = 1.2  # the atoms arriving
TR_OFF_TIME = 0.8  # the unwanted traps going out
TR_SETTLE = 0.6  # the pause before a stop
TR_LOOP_SEEDS = (0, 1, 2)  # the loadings the loop runs through


class TweezerRearrangement(Scene):
    """A tweezer array seen from above: it loads at random, is imaged, loses
    its empty and spare traps, and the rest slide into a defect-free block.
    One beat() per step."""

    def beat(self):
        """The pause after each step: nothing here, a click on the slide version."""

    def build(self):
        """Lay out the array, the heading and the first caption, unadded."""
        sites = square_sites(TW_ROWS, TW_COLS, TW_PITCH)
        self.targets = square_sites(*TW_TARGET, TW_PITCH)
        self.array = TweezerArray(sites, TiltedView(TR_CENTER, TR_SCALE))
        self.title = heading("Rearranging a tweezer array").move_to(TR_HEADING, aligned_edge=UL)
        self.note = step_caption("the traps", self.title)

    def say(self, text):
        """The animation that swaps the caption for ``text``."""
        self.note, swap = next_step(self.note, text, self.title)
        return swap

    def construct(self):
        self.build()
        array = self.array
        self.add(*array.trackers, array)
        self.play(FadeIn(self.title), FadeIn(self.note),
                  array.on.animate(run_time=TR_ON_TIME).set_value(1))
        self.wait(TR_SETTLE)
        self.beat()
        self.cycle(TW_SEED)

    def cycle(self, seed):
        """Load the array as ``seed`` has it, image it, and rearrange it."""
        array = self.array
        loaded = load_sites(len(array.sites), TW_FILL, np.random.default_rng(seed))
        plan = plan_rearrangement(array.sites, loaded, self.targets)

        array.load(loaded)
        self.play(self.say("each trap catches one atom, or none"),
                  array.filled.animate(run_time=TR_LOAD_TIME).set_value(1))
        self.wait(TR_SETTLE)
        self.beat()

        self.play(self.say("an image shows which"))
        fluoresce(self, array.atoms)
        self.wait(TR_SETTLE)
        self.beat()

        array.rearrange(plan)
        self.play(self.say("empty and spare traps off"),
                  array.off.animate(run_time=TR_OFF_TIME).set_value(1),
                  array.ringed.animate(run_time=TR_OFF_TIME).set_value(1))
        self.wait(TR_SETTLE)
        self.beat()

        self.play(self.say("the hologram is updated: every trap moves at once"))
        self.play(array.moved.animate.set_value(1),
                  run_time=longest_move(plan) * TR_SCALE / TWEEZER_SPEED)
        self.wait(TR_SETTLE)
        self.beat()

        self.play(self.say("a second image: no gaps"),
                  array.ringed.animate(run_time=0.4).set_value(0))
        fluoresce(self, array.atoms)
        self.wait(TR_SETTLE)
        self.beat()


class TweezerRearrangementLoop(TweezerRearrangement):
    """TweezerRearrangement run over several loadings, each released at the
    end: it begins and ends on the empty array, so the clip loops."""

    def construct(self):
        self.build()
        array = self.array
        array.on.set_value(1)
        array.redraw()
        self.add(*array.trackers, array, self.title, self.note)
        self.wait(TR_SETTLE)
        for seed in TR_LOOP_SEEDS:
            self.cycle(seed)
            self.release()

    def release(self):
        """Let the atoms go and bring the whole array back on, empty."""
        array = self.array
        self.play(self.say("the atoms are released"),
                  array.filled.animate(run_time=TR_OFF_TIME).set_value(0))
        self.play(array.on.animate.set_value(0), run_time=TR_OFF_TIME)
        array.reset()
        self.play(self.say("the traps"), array.on.animate(run_time=TR_ON_TIME).set_value(1))
        self.wait(TR_SETTLE)
