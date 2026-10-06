"""The AION scenes' style: the interferometry and trapping styles (AION
draws on both) plus the km-scale challenges table.

    from manim import *
    from manim_atoms.aion.style import *
"""

from manim_atoms.interferometry.style import *
from manim_atoms.trapping.style import *

# --- km-scale challenges table --------------------------------------------
# A table of text: the challenge in white with why it bites under it in the
# guide grey, the prototype's figures in the grey too (where we are), and
# AION-km's in white (where we need to be). A thin grey rule between rows.
FONT_TABLE_HEADING = FONT_LEGEND
FONT_TABLE_NAME = 28
FONT_TABLE_NOTE = 22
FONT_TABLE_CELL = 24
TABLE_RULE_STYLE = dict(stroke_width=1.5, color=GUIDE_COLOR, stroke_opacity=0.5)

# --- an atomic fountain ---------------------------------------------------
# The apparatus beside the fountain's space-time diagram. The tube is hardware
# and takes the shaft's grey, a notch thinner, since it shares the frame with
# a diagram. The launch lattice is light that holds atoms, so it takes the
# trap beams' pale warm white: a faint band, with its standing-wave planes a
# little brighter so they are seen to carry the cloud up.
FOUNTAIN_TUBE_WIDTH = 4
LATTICE_BAND_OPACITY = TRAP_BEAM_OPACITY * 0.6
LATTICE_PLANE_STYLE = dict(stroke_width=2, color=TRAP_BEAM_COLOR, stroke_opacity=0.7)
# The dashed line from a cloud in the tube to the same cloud on the diagram:
# a construction line, saying the two share a height axis.
FOUNTAIN_TIE_STYLE = dict(dash_length=0.08, stroke_width=1.5, stroke_opacity=0.35,
                          color=GUIDE_COLOR)
