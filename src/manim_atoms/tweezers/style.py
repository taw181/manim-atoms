"""The tweezer scenes' style: the core house style plus the tweezer array,
its beams and the holograms that make it.

    from manim import *
    from manim_atoms.tweezers.style import *
"""

from manim import ManimColor

from manim_atoms.style import *

# --- the tweezers ---------------------------------------------------------
# Tweezer light is far off every resonance: it holds an atom and drives
# nothing, so it takes no transition's colour. A pale warm white. How
# brightly a trap is drawn is its power; a trap switched off is not drawn.
TWEEZER_COLOR = ManimColor("#f3e3c8")
TWEEZER_OPACITY = 0.55  # on the axis, at the focus, at full power
TWEEZER_LAYERS = 4  # nested shapes across the beam, as a Gaussian profile
# Traps move at one speed, so a longer move takes visibly longer.
TWEEZER_SPEED = 0.9
# A site an atom is wanted at: a reference, so a thin ring in the
# construction grey.
TARGET_RING_STYLE = dict(stroke_width=2, stroke_opacity=0.55, color=GUIDE_COLOR)
# The focal plane in the tilted view: the outline of the plane the foci lie in.
FOCAL_PLANE_STYLE = dict(stroke_width=2, stroke_opacity=0.35, color=GUIDE_COLOR)
# The step being shown, under the heading: grey, a notch below the heading.
FONT_STEP = FONT_LEGEND
STEP_COLOR = lighten(GUIDE_COLOR)

# --- holograms ------------------------------------------------------------
# The focal plane as a camera would see it: the tweezer light's own colour.
FOCAL_SPOT_COLOR = TWEEZER_COLOR
# A bar per trap (its brightness) or per Zernike mode (its amplitude): a
# reading, in the plot foreground, on a baseline in the construction grey.
BAR_COLOR = ManimColor(PLOT_FOREGROUND)
BAR_BASELINE_STYLE = dict(stroke_width=2, color=GUIDE_COLOR)
FONT_READOUT = FONT_ANNOTATION  # the number a scene is about (uniformity, Strehl)
FONT_MODE = 20  # a Zernike mode's name under its disc
# The arrows joining the SLM plane to the focal plane.
TRANSFORM_ARROW_STYLE = dict(buff=0.15, stroke_width=3, color=lighten(GUIDE_COLOR),
                             max_tip_length_to_length_ratio=0.12)
