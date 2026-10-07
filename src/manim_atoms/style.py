"""The house style shared by every manim_atoms figure.

One place for the generic colour scheme, line styles, type sizes and pacing,
so that every animation reads as one set of figures:

    from manim import *
    from manim_atoms.style import *

What lives here is generic and generically named: an atom, a laser, a guide
line, a Gaussian beam, a plot frame. Anything that belongs to one topic --
its scenes' objects, its datasets, its conventions -- lives in
``<topic>/style.py``, which star-imports this one, and a topic that builds
on another (AION on interferometry) sees that topic's style too. A species'
line colours live with the species (``manim_atoms.species.strontium``).
When two places happen to use the same value for unrelated reasons, each
defines its own constant; one is defined as another only where it means
the same thing. A colour goes in a style module, never inline.

The ``*_STYLE`` bundles are dicts meant to be splatted into a mobject's
constructor, e.g. ``DashedLine(a, b, **GUIDE_STYLE)``.
"""

from manim import (
    BLUE_B,
    BLUE_D,
    GREY_B,
    PURPLE_B,
    RED_C,
    WHITE,
    ManimColor,
    interpolate_color,
)

# --- colour scheme --------------------------------------------------------
ATOM_COLOR = BLUE_D  # |g, p>
# |e, p + hbar k>. Purple rather than a second blue-green: TEAL sampled too
# close to ATOM_COLOR to separate on a projector, and telling the two arms
# apart is the whole point of an interferometer figure.
KICKED_COLOR = PURPLE_B
LASER_COLOR = RED_C  # beams, pulses, and every annotation about them
GUIDE_COLOR = GREY_B  # construction lines, e.g. the incoming trajectory


def lighten(color, amount=0.35):
    """The stroke and label shade that goes with a fill colour."""
    return interpolate_color(color, WHITE, amount)


# --- type -----------------------------------------------------------------
FONT_TITLE = 32
FONT_STATE = 36  # a state label beside an atom that has come to rest
FONT_ANNOTATION = 34  # recoil arrows, pulse captions, the readout formula
FONT_LEGEND = 30
FONT_K = 32  # the k-vector marker beside a beam

# --- atoms ----------------------------------------------------------------
ATOM_RADIUS = 0.18
LEGEND_ATOM_RADIUS = 0.13
ATOM_STROKE_WIDTH = 2

# --- laser pulses ---------------------------------------------------------
PULSE_LENGTH = 2.2
PULSE_AMPLITUDE = 0.28
PULSE_CYCLES = 4.5
PULSE_STROKE_WIDTH = 4
PULSE_TAPER = [0.15, 1.0, 0.15]  # stroke opacity along the packet

# --- line styles ----------------------------------------------------------
GUIDE_STYLE = dict(
    dash_length=0.12, stroke_width=2, stroke_opacity=0.3, color=GUIDE_COLOR
)
TRAJECTORY_STYLE = dict(stroke_width=4)
RECOIL_ARROW_STYLE = dict(
    buff=0, stroke_width=4, color=LASER_COLOR, max_tip_length_to_length_ratio=0.22
)
K_ARROW_STYLE = dict(
    buff=0, stroke_width=3, color=LASER_COLOR, max_tip_length_to_length_ratio=0.3
)
FLASH_STYLE = dict(color=LASER_COLOR, flash_radius=0.55, line_length=0.3)

# --- pacing ---------------------------------------------------------------
# Pacing is part of the house style. Every leg's run_time is distance / V, so
# an atom's speed never visibly changes when a pulse splits it -- which is what
# makes a 45 degree kick honest: the recoil is purely vertical and equal in
# magnitude to the forward motion.
V = 2.0
PULSE_SPEED = V * 1.6

# --- a window on a space-time diagram -------------------------------------
# The wash over a stretch of lab time -- a field's half-cycle, a beam's
# on-time: a pale blue, faint enough that the worldlines under it still read.
WINDOW_STYLE = dict(stroke_width=0, fill_color=BLUE_B, fill_opacity=0.16)

# --- plots ----------------------------------------------------------------
# Plots, matplotlib's or manim's, sit on the same background as the
# animations. Axis text is a notch below the legend size because axis labels
# run long ("Lower interferometer excitation / %") and two plots have to
# share the frame side by side.
PLOT_BACKGROUND = "#101010"  # manim.cfg's background_color
PLOT_FOREGROUND = "#dddddd"  # axes, ticks and labels
FONT_AXIS = 26
FONT_TICK = 24
DATA_DOT_RADIUS = 0.028

# --- energy levels --------------------------------------------------------
# A two-level system drawn beside an interferometer doubles as its key, so the
# level lines take the state colours straight: a short horizontal segment has
# to carry its colour at a glance, which needs a heavier stroke than a
# trajectory. The gap arrow is furniture and takes the construction grey; it
# only goes laser red while a pulse is actually driving the transition, which
# is the one moment the light and the atom are the same object.
LEVEL_STROKE_WIDTH = 6
LEVEL_GAP_ARROW_STYLE = dict(
    buff=0,
    stroke_width=3,
    color=lighten(GUIDE_COLOR),
    max_tip_length_to_length_ratio=0.09,
)
LEVEL_GLOW_ARROW_STYLE = dict(
    buff=0,
    stroke_width=5,
    color=LASER_COLOR,
    max_tip_length_to_length_ratio=0.12,
)
# A species' full level scheme: a line not running is grey, and one that is
# takes its own colour (the species defines those) at a heavier stroke.
TRANSITION_IDLE_STYLE = dict(stroke_width=3, color=lighten(GUIDE_COLOR))
TRANSITION_ACTIVE_WIDTH = 7
FONT_LINEWIDTH = FONT_AXIS  # a transition's linewidth, under its wavelength

# --- fluorescence readout -------------------------------------------------
# The imaging light and what the atoms scatter back: a clear mid blue.
IMAGING_COLOR = ManimColor("#5b7cff")
FLUORESCENCE_FLASH = dict(color=IMAGING_COLOR, num_lines=14, flash_radius=0.6,
                          line_length=0.28)
FLUORESCENCE_HALO_OPACITY = 0.55

# --- optics ---------------------------------------------------------------
OPTIC_COLOR = lighten(GUIDE_COLOR)  # mirrors, beam splitters, detectors, vacuum hardware
# A beam drawn as nested translucent bands, so it reads as a Gaussian
# profile, and faint, because the atoms have to show up inside it.
BEAM_OPACITY = 0.3  # on the beam axis
BEAM_LAYERS = 4
# A cavity's probe, its mode and the transmission it reads out take the
# probe's colour, a pure, deep red.
PROBE_COLOR = ManimColor("#f01c24")
CAVITY_MODE_OPACITY = 0.45
MIRROR_STROKE_WIDTH = 7
PROBE_STROKE_WIDTH = 3
LASER_BOX_WIDTH = 1.2  # a laser drawn as a box, its beam leaving the right edge
LASER_BOX_HEIGHT = 0.55
# Light drawn as a wave riding a beam: the band under it, and how finely the
# sine is sampled along it.
BEAM_GLOW_WIDTH = 10
BEAM_GLOW_OPACITY = 0.18
WAVE_SAMPLES_PER_UNIT = 45

# --- the Bloch sphere -----------------------------------------------------
# Furniture, in the lightened construction grey, with its axis through the
# poles a faint dashed guide. A spin's quantum noise is a filled patch on it.
BLOCH_STYLE = dict(stroke_width=2, color=lighten(GUIDE_COLOR))
BLOCH_AXIS_STYLE = dict(dash_length=0.08, stroke_width=1.5, stroke_opacity=0.5,
                        color=GUIDE_COLOR)
NOISE_BLOB_OPACITY = 0.3
NOISE_BLOB_STROKE_WIDTH = 3

# --- static slides --------------------------------------------------------
# The slides between the animations: a title, a contents list, photographs
# and figures. Their headings take FONT_TITLE in the upper left, where every
# animation puts its own, so a photo slide and the scene after it read as one
# deck. The deck's own title is the one heading allowed to be large.
FONT_DECK_TITLE = 50
FONT_DECK_BYLINE = FONT_ANNOTATION
FONT_CONTENTS = 42
# A label drawn over a photograph: bold yellow, bright enough to hold up
# against fields, roads and sky alike, with a dark outline behind its lines
# and text (not its arrowheads, which read as solid shapes without one).
PHOTO_LABEL_COLOR = ManimColor("#ffe135")
PHOTO_LABEL_OUTLINE = dict(color=PLOT_BACKGROUND, width=8, opacity=0.85)
PHOTO_LABEL_STROKE_WIDTH = 7
FONT_PHOTO_LABEL = 40
# A detail called out of a photograph: a box on the photo, joined by two lines
# to a panel beside it that draws what is inside, in the photo labels' yellow.
CALLOUT_COLOR = PHOTO_LABEL_COLOR
CALLOUT_STROKE_WIDTH = 4
CALLOUT_CORNER_RADIUS = 0.12
# A frame round a recorded picture -- a video, a camera image -- so it reads
# as a picture set into the slide rather than as part of the drawing.
IMAGE_BORDER_STYLE = dict(stroke_width=2, color=lighten(GUIDE_COLOR))
# An atom cloud drawn as a cartoon, e.g. in such a panel: a still heap of dots.
CARTOON_CLOUD_N = 70
CARTOON_CLOUD_RADIUS = 0.5
CARTOON_CLOUD_DOT_RADIUS = 0.06
# The deck's footer, on every slide: a thin bar along the bottom edge that
# fills as the talk goes on, and the slide's number in the corner above its
# end. Kept small and grey so it reads as furniture, not content.
PROGRESS_BAR_HEIGHT = 0.05
PROGRESS_TRACK_COLOR = ManimColor("#303030")  # just off the background
PROGRESS_FILL_COLOR = GREY_B
FONT_SLIDE_NUMBER = 18
SLIDE_NUMBER_COLOR = GREY_B
# A citation: furniture too, in the footer's grey and size, bottom left just
# above the progress bar, kept clear of the slide number at the far right.
# Several stack upward; a line too long is shrunk to fit, never wrapped.
FONT_CITATION = FONT_SLIDE_NUMBER
CITATION_COLOR = SLIDE_NUMBER_COLOR
CITATION_EDGE_BUFF = 0.15  # from the left edge, as the number is from the right
CITATION_BOTTOM = PROGRESS_BAR_HEIGHT + 0.1  # above the frame's bottom edge
CITATION_NUMBER_CLEARANCE = 0.7  # a bottom-right one ends this far in, left of it
CITATION_MAX_WIDTH = 12.5
CITATION_LINE_BUFF = 0.06
CITATION_SEPARATOR = r"\enspace$\cdot$\enspace "  # between labelled citations
# a dark halo round the letters, so a line over a photograph still reads
CITATION_OUTLINE = dict(color=PLOT_BACKGROUND, width=7, opacity=0.9)
# A slot for a figure still to come: a reference, not content, so dashed and
# in the construction grey.
PLACEHOLDER_STYLE = dict(
    dash_length=0.15, stroke_width=2, stroke_opacity=0.6, color=GUIDE_COLOR
)
