"""A tweezer array seen from an angle: each trap a focused beam.

Starts on a loaded array seen from above, at TweezerRearrangement's spacing
but with fewer than half its traps and drawn larger, and tilts the view over. Each spot turns
out to be the waist of a beam: it narrows to its focus in the plane of the
array, where its atom sits, and spreads again beyond. The beam is drawn as
a solid, cut off square a little way either side of the atom, and a nearer
beam hides the ones behind it, so that the array stays a set of separate
beams; the atoms are drawn over all the light. The array is then
imaged and rearranged exactly as in the top-down scene, with the beams
moving.

The view is an orthographic projection (core.projection), not a camera:
there is no perspective. The beams are not to scale (tools.beams), and
real ones neither end nor hide one another.

- TweezerArray3D: a beat() on the top-down array, then after the tilt, the
  switching off and the move.
- TweezerArray3DLoop: the rearranged block turning a quarter turn about the
  optical axis, which brings it back onto itself, so the clip loops.
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
from manim_atoms.tweezers.tools.beams import (
    TW_AZIMUTH,
    TW_ELEVATION,
    focal_plane,
    hourglass_trap,
)
from manim_atoms.tweezers.tools.tweezer_array import (
    TW_FILL,
    TW_PITCH,
    TweezerArray,
    heading,
    next_step,
    step_caption,
)

# --- tilted-array geometry ---------------------------------------------------
# Seen from the side every beam stands in front of the rows behind it, and
# the top-down scenes' eighty-one are too many to follow. So this array is
# smaller, 6 x 6 at the same spacing, and drawn larger. It loads nineteen
# atoms, enough for the 4 x 4 block at its centre with three to spare; an
# even block in an even array sits on the array's own sites. It sits below
# the middle of the frame and to the right, clear of the heading and the
# step caption in the upper left corner.
T3_ROWS, T3_COLS = 6, 6
T3_TARGET = (4, 4)  # rows and columns of the block wanted
T3_SEED = 3  # of the loading shown: scattered, with no row or column full
T3_CENTER = np.array([0.8, -0.4, 0.0])  # of the array
T3_SCALE = 1.8  # scene units per unit of the array's own
T3_HEADING = np.array([-6.6, 3.6, 0.0])  # the heading's upper left corner
T3_PLANE_MARGIN = 0.5  # of the focal plane's outline beyond the outermost traps
T3_TILT_TIME = 3.0
T3_OFF_TIME = 0.8
T3_TURN_TIME = 10.0  # the loop's quarter turn
T3_SETTLE = 0.6  # the pause before a stop


class TweezerArray3D(Scene):
    """The loaded array tilts from the top-down view into one from an angle,
    each trap a beam through its atom, and is rearranged there. One beat()
    per step."""

    def beat(self):
        """The pause after each step: nothing here, a click on the slide version."""

    def build(self):
        """Lay out the loaded array in a view that starts top-down, unadded."""
        sites = square_sites(T3_ROWS, T3_COLS, TW_PITCH)
        targets = square_sites(*T3_TARGET, TW_PITCH)
        loaded = load_sites(len(sites), TW_FILL, np.random.default_rng(T3_SEED))
        self.plan = plan_rearrangement(sites, loaded, targets)
        self.elevation, self.azimuth = ValueTracker(PI / 2), ValueTracker(0)
        self.plane_shown = ValueTracker(0)
        view = TiltedView(T3_CENTER, T3_SCALE, self.elevation, self.azimuth)
        self.array = TweezerArray(sites, view, draw_trap=hourglass_trap).load(loaded)
        self.array.on.set_value(1)
        self.array.filled.set_value(1)
        self.array.redraw()
        half = (T3_COLS - 1) / 2 * TW_PITCH + T3_PLANE_MARGIN
        self.plane = focal_plane(view, half, half, self.plane_shown)
        self.title = heading("A tweezer array").move_to(T3_HEADING, aligned_edge=UL)
        self.note = step_caption("from above: each trap a spot", self.title)

    def add_all(self):
        """Put everything on, the trackers first so nothing lags them."""
        self.add(self.elevation, self.azimuth, self.plane_shown, *self.array.trackers,
                 self.plane, self.array, self.title, self.note)

    def say(self, text):
        """The animation that swaps the caption for ``text``."""
        self.note, swap = next_step(self.note, text, self.title)
        return swap

    def construct(self):
        self.build()
        self.add_all()
        array = self.array
        self.wait(T3_SETTLE)
        self.beat()

        self.play(self.say("from the side: each trap a focused beam"),
                  self.elevation.animate(run_time=T3_TILT_TIME).set_value(TW_ELEVATION),
                  self.azimuth.animate(run_time=T3_TILT_TIME).set_value(TW_AZIMUTH),
                  self.plane_shown.animate(run_time=T3_TILT_TIME).set_value(1))
        self.wait(T3_SETTLE)
        self.beat()

        self.play(self.say("image, then empty and spare traps off"))
        fluoresce(self, array.atoms)
        array.rearrange(self.plan)
        self.play(array.off.animate.set_value(1), array.ringed.animate.set_value(1),
                  run_time=T3_OFF_TIME)
        self.wait(T3_SETTLE)
        self.beat()

        self.play(self.say("every trap moves at once"))
        self.play(array.moved.animate.set_value(1),
                  run_time=longest_move(self.plan) * T3_SCALE / TWEEZER_SPEED)
        self.play(array.ringed.animate.set_value(0), run_time=0.4)
        self.wait(T3_SETTLE)
        self.beat()


class TweezerArray3DLoop(TweezerArray3D):
    """The rearranged block in the tilted view, turning a quarter turn about
    the optical axis: a square block comes back onto itself, so the clip
    loops."""

    def construct(self):
        self.build()
        array = self.array
        array.rearrange(self.plan)
        array.off.set_value(1)
        array.moved.set_value(1)
        self.elevation.set_value(TW_ELEVATION)
        self.azimuth.set_value(TW_AZIMUTH)
        self.plane_shown.set_value(1)
        array.redraw()
        self.note = step_caption("a defect-free block", self.title)
        self.add_all()
        self.play(self.azimuth.animate.set_value(TW_AZIMUTH + PI / 2),
                  rate_func=linear, run_time=T3_TURN_TIME)
