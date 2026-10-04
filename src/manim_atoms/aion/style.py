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
