"""The house style shared by every manim_atoms figure.

One place for the colour scheme, line styles, type sizes and pacing, so that
every animation reads as one set of figures:

    from manim import *
    from manim_atoms.style import *

Only what core uses, or more than one topic shares, lives here. What one
topic alone uses lives in ``<topic>/style.py``, which star-imports this
one; that topic's modules star-import their own style instead
(``from manim_atoms.trapping.style import *``). A colour goes in a style
module, never inline.

The ``*_STYLE`` bundles are dicts meant to be splatted into a mobject's
constructor, e.g. ``DashedLine(a, b, **GUIDE_STYLE)``.
"""

from manim import (
    BLUE_B,
    BLUE_D,
    GREEN_C,
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
AREA_COLOR = BLUE_B  # the area a closed interferometer encloses

# An interferometer arm is an amplitude, not a whole atom.
SUPERPOSITION_OPACITY = 0.65


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

# The scenes with something passing through them -- a wave, a dark-matter field
# -- are space-time diagrams, so the x axis *is* lab time and a pulse that
# freezes the atoms freezes the field along with them. Their continuous
# variants run one clock at V from the first pulse to the last and never stop
# it, which costs them the dilated pulses: a photon crosses the baseline in
# GR_LAG / V, a fifth of a second, so a pulse there is a strobe rather than an
# event. That is the right trade for those scenes only. The explainers have
# already said what a pulse does, and these ones are about what is passing
# through.
PULSE_HOLD = 0.4  # lab time a strobed column is held before it fades
# ...and how long a pulse's worldline, its dashed reference and whatever it
# was captioned with stay up once it has passed. Long enough to be read is
# longer than the pulse itself lasts, so they linger into the next leg and
# go out only as the next pulse comes up behind them.
PULSE_LINGER = 1.2  # lab time

# --- a warm glow ----------------------------------------------------------
# A black hole's rim light, and wherever else a warm accent is wanted: the
# upper cloud in the data plots, a hot oven.
HORIZON_GLOW = ManimColor("#ffb26b")  # the rim light and the merger burst


# --- a window on a space-time diagram -------------------------------------
# The wash over a stretch of lab time: a field's half-cycle, a beam's on-time.
FIELD_WINDOW_STYLE = dict(stroke_width=0, fill_color=AREA_COLOR, fill_opacity=0.16)


# --- an injected light shift ----------------------------------------------
# A second laser, far enough off resonance to drive nothing, turned on across
# one cloud to shift its clock levels. It gets a colour of its own rather than
# the usual laser red, because the one thing the figure has to say about it is
# that it is not the beam the pulses come from: different wavelength,
# different job, one interferometer instead of both. Green is the only hue the
# talk has left, and it samples furthest from everything already in use -- its
# nearest neighbour is the construction grey, which is only ever a thin dashed
# line and cannot be confused with a filled band.
LIGHT_SHIFT_COLOR = GREEN_C

# --- the phase budget -----------------------------------------------------
# Breaking Phi into its terms sorts them into two kinds, and the colour does
# the sorting: white for the term the measurement is after, and the usual
# laser red for the one the light brings with it, circled or struck depending
# on the instrument. A ring lends its colour to its label; a struck term takes
# the grey instead, since the cross has already said the term is out of play.
SIGNAL_COLOR = WHITE
NOISE_COLOR = LASER_COLOR

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


# --- optical hardware -----------------------------------------------------
OPTIC_COLOR = lighten(GUIDE_COLOR)  # mirrors, beam splitters, detectors, vacuum hardware


# --- data plots (matplotlib) ----------------------------------------------
# Measured data shown alongside the animations, so it sits on the same
# background in the same palette. The two interferometers are the two clouds
# of the gradiometer, not two states, so they take neither state colour: the
# lower one gets the cool crest shade and the upper one the warm rim light,
# which sample as far apart as anything in the talk. Across the noise runs
# the split is the phase budget's: green for the quiet laser, whose ellipse
# is the signal, and laser red for the one with phase noise put on it. Green
# rather than white, which sank into the grey of the SQL band; a bluish green,
# kept apart from the light shift's, and further from the red for anyone
# red-green colour-blind.
PLOT_BACKGROUND = "#101010"  # manim.cfg's background_color
PLOT_FOREGROUND = "#dddddd"  # axes, ticks and labels
LLN_COLOR = ManimColor("#44dd88")
# The standard quantum limit the two runs' Allan deviations are held against
# is a reference, not a measurement, so it takes the guide grey: the paper's
# grey band of Monte Carlo runs (68% denser inside 95%) and its dotted
# 1/sqrt(tau) line.
SQL_COLOR = GUIDE_COLOR

# The same data drawn by manim, point by point. Axis text is a notch below the
# legend size because axis labels run long ("Lower interferometer excitation
# / %") and two plots have to share the frame side by side.
FONT_AXIS = 26
FONT_TICK = 24
DATA_DOT_RADIUS = 0.028

GW_MERGER_TIME_COLORS = ["#5e8fd9", "#4fc1c1", "#8fd46a", "#f0c24a", "#f06a4a"]


# A band edge on a sensitivity plot: a reference, not data, so dashed and
# in the axes' own colour.
GW_BAND_EDGE_STYLE = dict(
    dash_length=0.1, stroke_width=2, stroke_opacity=0.6, color=PLOT_FOREGROUND
)


# --- the experimental sequence --------------------------------------------
# The transitions take the hues of the usual Sr level diagram -- blue for the
# 461 nm line, red for 689 nm, which is what makes the red MOT red. The clock
# line is the interferometer's laser and so keeps the laser red it has
# everywhere else; that is a salmon red, so 689 nm takes a pure, deeper one,
# which keeps the two lines apart when they sit side by side.
TRANSITION_461_COLOR = ManimColor("#5b7cff")
TRANSITION_689_COLOR = ManimColor("#f01c24")
TRANSITION_698_COLOR = LASER_COLOR
# The transparency beam is a laser switched on to light-shift a level, which
# is what the light-shift green already means in the talk -- and 488 nm is
# blue-green anyway.
TRANSITION_488_COLOR = LIGHT_SHIFT_COLOR
# Readout is fluorescence on the 461 nm line: the imaging pulses and the
# light the atoms scatter back take its blue.
IMAGING_COLOR = TRANSITION_461_COLOR
FLUORESCENCE_FLASH = dict(color=IMAGING_COLOR, num_lines=14, flash_radius=0.6,
                          line_length=0.28)
FLUORESCENCE_HALO_OPACITY = 0.55
TRANSITION_IDLE_STYLE = dict(stroke_width=3, color=lighten(GUIDE_COLOR))
TRANSITION_ACTIVE_WIDTH = 7
FONT_LINEWIDTH = FONT_AXIS  # a transition's linewidth, under its wavelength
# The blue MOT's two repumps (679 and 707 nm), which are always on together
# and so share one hue: amber, which samples clear of the 461 blue, the 689
# magenta and the clock line's laser red.
REPUMP_COLOR = ManimColor("#f5b400")
VIDEO_BORDER_STYLE = dict(stroke_width=2, color=lighten(GUIDE_COLOR))


# --- dipole traps ---------------------------------------------------------
# The trap beams are far off every resonance, so they drive nothing on the
# level scheme and take no transition colour: a pale warm white, the colour
# of light that holds atoms rather than addressing them. Drawn as nested
# translucent bands so a beam reads as a Gaussian profile, and faint, because
# the atoms have to show up inside them.
TRAP_BEAM_COLOR = ManimColor("#f3e3c8")
TRAP_BEAM_OPACITY = 0.3  # on the beam axis
TRAP_BEAM_LAYERS = 4


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


# --- the Bloch sphere -----------------------------------------------------
# Furniture, in the lightened construction grey, with its axis through the
# poles a faint dashed guide. A spin's quantum noise is a filled patch on it.
BLOCH_STYLE = dict(stroke_width=2, color=lighten(GUIDE_COLOR))
BLOCH_AXIS_STYLE = dict(dash_length=0.08, stroke_width=1.5, stroke_opacity=0.5,
                        color=GUIDE_COLOR)
NOISE_BLOB_OPACITY = 0.3
NOISE_BLOB_STROKE_WIDTH = 3

# --- an optical cavity ----------------------------------------------------
# A cavity's probe, its mode and the transmission it reads out take the
# probe's colour: the 689 red, because the squeezing cavity counts the atoms
# in |g> on the 689 nm line.
PROBE_COLOR = TRANSITION_689_COLOR
CAVITY_MODE_OPACITY = 0.45
MIRROR_STROKE_WIDTH = 7
PROBE_STROKE_WIDTH = 3
