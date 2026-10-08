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
TWEEZER_OPACITY = 0.7  # on the axis, at the focus, at full power
TWEEZER_LAYERS = 4  # nested shapes across the beam, as a Gaussian profile
# A beam seen from the side is a solid with a hard edge, not a glow: a flat
# fill inside a thin outline of the same colour. Under the fill it is backed
# in the background's colour, so a nearer beam hides the ones behind it
# rather than adding to them, and a crowd of beams stays a set of separate
# ones.
TWEEZER_SOLID_OPACITY = 0.3  # the fill, at full power
TWEEZER_EDGE_STYLE = dict(stroke_width=1.5, stroke_opacity=0.75)
TWEEZER_BACKING_COLOR = PLOT_BACKGROUND
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

# --- a gate in the array ---------------------------------------------------
# A static electric field across the array: a control field but not light,
# so an arrow near white rather than a laser's colour.
STATIC_FIELD_COLOR = lighten(GUIDE_COLOR, 0.8)
STATIC_FIELD_ARROW_STYLE = dict(buff=0, stroke_width=4, color=STATIC_FIELD_COLOR,
                                max_tip_length_to_length_ratio=0.18)
# A laser addressing one atom, seen side on: brighter than a trapping
# figure's beams, since here it is the only one and comes and goes.
ADDRESSING_BEAM_OPACITY = 0.75  # on its axis, at the pulse's peak
# Two particles coupled across the gap between their traps.
COUPLING_LINK_STYLE = dict(stroke_width=5)
# A pulse's envelope against time: the curve heavy, its baseline a reference.
ENVELOPE_STROKE_WIDTH = 4
ENVELOPE_AXIS_STYLE = dict(stroke_width=2, color=GUIDE_COLOR)
ENVELOPE_MARKER_RADIUS = 0.08

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
