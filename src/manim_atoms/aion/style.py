"""The AION scenes' style: the interferometry and trapping styles (AION
draws on both) plus AION's own palettes: the long-baseline cartoon, the
spacetime sheet and gravitational waves, the dark-matter field and the
solar system, the light-shift beam, LIGO's arms, the data plots (the DAI
fringes, the GW and ULDM sensitivity curves) and the km-scale table.

    from manim import *
    from manim_atoms.aion.style import *
"""

import numpy as np

from manim_atoms.interferometry.style import *
from manim_atoms.trapping.style import *

# --- a long-baseline detector ---------------------------------------------
# A long-baseline detector in cartoon (tools/baseline.py): the vacuum shaft
# and the atom sources on its side are hardware, in the optics grey; the clock
# laser runs the shaft's length in the laser red, and the clouds it drives
# are the ground-state blue.
SHAFT_COLOR = OPTIC_COLOR
SHAFT_WALL_WIDTH = 6
SOURCE_STROKE_WIDTH = 3
BASELINE_BEAM_OPACITY = 0.55
LAUNCH_STROKE_WIDTH = 2.5
FONT_SOURCE = FONT_LEGEND

# --- spacetime and gravitational waves ------------------------------------
# The sheet is coloured by height, so it needs three shades that stay apart at
# a 1.5px stroke: a calm slate at rest, a bright crest and a deep trough. The
# holes themselves are warm, which is the one hue nothing else in the talk
# uses -- against the blue sheet they read instantly as the source.
SHEET_COLOR = ManimColor("#33607f")  # undisturbed spacetime
CREST_COLOR = ManimColor("#a8e4ff")  # a wave crest
TROUGH_COLOR = ManimColor("#54367f")  # a trough, and the floor of a gravitational well
HORIZON_COLOR = ManimColor("#000000")  # the event horizon: darker than the background
SHEET_STROKE_WIDTH = 1.5
HORIZON_MESH_WIDTH = 0.6
HORIZON_MESH_OPACITY = 0.14
BURST_STROKE_WIDTH = 5
# An h(t) trace is the wave measured rather than the wave itself, so it takes
# the crest shade: bright enough to sit above a diagram without competing with
# the laser red that marks everything the pulses do.
STRAIN_COLOR = CREST_COLOR
STRAIN_STROKE_WIDTH = 3

# --- an oscillating background field --------------------------------------
# A trace above the diagram is the same kind of object whether what oscillates
# is the metric or a scalar field driving the fundamental constants, so a
# dark-matter field takes the strain trace's shade and width. What it needs on
# top is the stretch of the oscillation one arm was excited during: a wash
# rather than an outline, because what matters is which part of the cycle it
# covers, not where its edges fall.
FIELD_COLOR = STRAIN_COLOR
FIELD_STROKE_WIDTH = STRAIN_STROKE_WIDTH
# The bodies a dark-matter wavelength is measured against. Muted, so the field
# drawn across them stays the brightest thing on the page; the Earth takes the
# atoms' blue because it is where the lab is.
EARTH_COLOR = ATOM_COLOR
MOON_COLOR = GREY_B
SUN_COLOR = ManimColor("#f5c542")
BODY_OPACITY = 0.85
BODY_MIN_RADIUS = 0.05  # below this a body drawn to scale is not there at all

# --- an injected light shift ----------------------------------------------
LIGHT_SHIFT_STYLE = dict(
    stroke_width=2,
    stroke_color=LIGHT_SHIFT_COLOR,
    stroke_opacity=0.55,
    fill_color=LIGHT_SHIFT_COLOR,
    fill_opacity=0.16,
)

# --- energy levels --------------------------------------------------------
# Where a laser was tuned to, drawn across a two-level diagram whose upper
# level is moving. Laser red, because it belongs to the light, and dashed
# rather than solid because it is a reference the atom has walked away from
# rather than a state anything is in.
LEVEL_RESONANCE_STYLE = dict(
    dash_length=0.09, stroke_width=2, stroke_opacity=0.55, color=LASER_COLOR
)

# --- an optical Michelson interferometer ----------------------------------
# LIGO's light is all one laser, so every beam in the apparatus stays laser
# red. Only in the readout, where the light returning from each arm is drawn
# separately, do the two arms need telling apart. They take the two state
# colours, which already mean "the two arms of an interferometer" everywhere
# else in the talk and sample well apart. What reaches the detector is their
# sum, and that is the signal, so it takes the signal white.
X_ARM_COLOR = ATOM_COLOR
Y_ARM_COLOR = KICKED_COLOR
OUTPUT_COLOR = SIGNAL_COLOR
BEAM_STROKE_WIDTH = 3
BEAM_GLOW_WIDTH = 10  # the faint band a beam's wave rides on
BEAM_GLOW_OPACITY = 0.18

# --- data plots (matplotlib) ----------------------------------------------
LOWER_CLOUD_COLOR = CREST_COLOR
UPPER_CLOUD_COLOR = HORIZON_GLOW
# The differential dark-matter slide's marks on the field, where each pulse
# reaches each cloud, and its dials' captions, which key them. The upper
# cloud's is the data's; the lower's cannot be, as that is the field's own
# colour and its marks would sink into the curve.
LOWER_PULSE_MARK_COLOR = WHITE
UPPER_PULSE_MARK_COLOR = UPPER_CLOUD_COLOR
HLN_COLOR = NOISE_COLOR
SQL_BAND_OPACITIES = (0.4, 0.2)  # 68%, 95%
# The imprinted-signal scans (Fig. 5a): the phase the light shift put on takes
# the light shift's green, dashed over the white of what the gradiometer got
# back out of it.
IMPRINTED_SIGNAL_COLOR = LIGHT_SHIFT_COLOR
RECOVERED_SIGNAL_COLOR = SIGNAL_COLOR
# The two interferometers' fringes lie on top of each other, so they are
# drawn see-through to let the lower one show under the upper. Only across
# the series, mind: each series is one path, so a series never darkens where
# its own points pile up.
FRINGE_DOT_OPACITY = 0.7
# A fringe plot shown in full before its shots are lit up one by one: dim
# enough that a lit shot stands out, bright enough that the fringes still read.
FRINGE_DIM_OPACITY = 0.2
# The newest shot is ringed on both plots at once, which is what ties a fringe
# point to its place on the ellipse.
NEWEST_RING_RADIUS = 0.11
NEWEST_RING_WIDTH = 3
# GW detector sensitivity curves, in the colours of the exclusion plot they
# were digitised from (GW_exclusion_plot.svg), so the figure still reads as
# the familiar one. All mid-tones, so they hold up on the dark background.
GW_DETECTOR_COLORS = {
    "LISA": "#8fb032",
    "LIGO": "#c56e1a",
    "ET": "#ffbf00",
    "AION-10": "#47b66d",
    "AION-100": "#eb6235",
    "AION-km": "#a5609d",
    "AEDGE": "#6685d9",
}
# The region a detector can see is shaded down to its curve: faint, because
# the regions overlap and every curve has to show through the others.
GW_REGION_OPACITY = 0.15
# Black-hole merger tracks cross every detector's region, so they take no hue
# of their own: white for a nearby source, fading to grey with redshift, which
# is also the way the signal fades. The dots along a track mark the time left
# to merger, on a cool-to-hot ramp that ends hottest at the merger itself.
GW_MERGER_NEAR_COLOR = "#ffffff"
GW_MERGER_FAR_COLOR = "#6e6e6e"
GW_MERGER_Z_RANGE = (0.1, 10)  # redshifts the two shades are pinned to
def merger_color(z):
    """A merger track's shade: GW_MERGER_NEAR_COLOR at the low end of
    GW_MERGER_Z_RANGE fading to GW_MERGER_FAR_COLOR at the high end, in log z."""
    lo, hi = np.log10(GW_MERGER_Z_RANGE)
    s = np.clip((np.log10(z) - lo) / (hi - lo), 0, 1)
    return interpolate_color(
        ManimColor(GW_MERGER_NEAR_COLOR), ManimColor(GW_MERGER_FAR_COLOR), s
    )
# The same track animated beside the merger: drawn faint ahead of the source
# and lit up behind it, with the source itself a dot in the holes' own rim
# colour, which is what ties the dot on the plot to the pair on the sheet.
GW_TRACK_WIDTH = 3
GW_TRACK_AHEAD_OPACITY = 0.3
GW_SOURCE_COLOR = HORIZON_GLOW
GW_SOURCE_RADIUS = 0.08
GW_SOURCE_GLOW_RADIUS = 0.2
GW_SOURCE_GLOW_OPACITY = 0.3
# The stretch of the track a recorded event's data covers, once the data is
# shown: the blue of the Livingston trace in LIGO's GW150914 figure, since the
# orange of the Hanford one is already the LIGO curve's and the source dot's.
GW_DATA_WINDOW_COLOR = "#35a8e0"
# Merger tracks in a crowd are drawn a notch thinner than a lone one, so
# nine of them don't outweigh the detector curves they're read against.
GW_TRACK_CROWD_WIDTH = 2
# AION's reach for ultralight dark matter (coupling against mass), drawn as a
# small inset beside the dark-matter figures. Each experiment keeps its
# colour from the GW plot, so AION-10 is the same green on both. The region other experiments have already ruled out
# is the construction grey: a reference, not something AION measures.
ULDM_COLORS = {
    stem: GW_DETECTOR_COLORS[name]
    for stem, name in [
        ("aion10_goal", "AION-10"), ("aion100_goal", "AION-100"),
        ("aion_km", "AION-km"), ("aedge", "AEDGE"),
    ]
}
ULDM_CURVE_WIDTH = 2.5
ULDM_EXCLUDED_STYLE = dict(stroke_width=0, fill_color=GUIDE_COLOR, fill_opacity=0.28)
ULDM_EXCLUDED_EDGE = dict(stroke_width=1.5, color=GUIDE_COLOR, stroke_opacity=0.8)
# The mass a figure is drawing, marked across the plot: in the field's own
# colour, since it is that field's mass, with a dot where it meets a curve.
# Faint across the whole plot, full strength over the couplings still open.
ULDM_MARK_STYLE = dict(stroke_width=2.5, color=FIELD_COLOR, stroke_opacity=1.0)
ULDM_MARK_FAINT_OPACITY = 0.35
ULDM_MARK_DOT_RADIUS = 0.065
# An outline in the page colour round the plot's labels: in a small inset a
# curve can't always be kept out from under one, and this breaks the line
# cleanly round the letters rather than drawing it through them.
ULDM_LABEL_OUTLINE = dict(color=PLOT_BACKGROUND, width=3)
# An inset has to fit beside a full figure, so its type is a notch below the
# footer's-plus: the smallest that still reads from the back of a room.
FONT_INSET_TICK = 22
FONT_INSET_LABEL = 24

# --- km-scale challenges table --------------------------------------------
# A table of text: the challenge in white with why it bites under it in the
# guide grey, the prototype's figures in the grey too (where we are), and
# AION-km's in white (where we need to be). A thin grey rule between rows.
FONT_TABLE_HEADING = FONT_LEGEND
FONT_TABLE_NAME = 28
FONT_TABLE_NOTE = 22
FONT_TABLE_CELL = 24
TABLE_RULE_STYLE = dict(stroke_width=1.5, color=GUIDE_COLOR, stroke_opacity=0.5)
