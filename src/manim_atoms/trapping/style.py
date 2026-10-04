"""The trapping scenes' style: the core house style plus laser cooling,
velocity slicing and the HiFAIS source.

    from manim import *
    from manim_atoms.trapping.style import *
"""

from manim_atoms.style import *

# --- laser cooling --------------------------------------------------------
# The MOT stages drawn as a cartoon beside the level scheme. The beams take
# the colour of the transition they drive, so the cartoon and the diagram
# agree on which light is on; they are wide translucent bands, because a MOT
# beam is a fat collimated beam rather than a pulse, and the band's opacity
# stands for its intensity. The coils are furniture, grey like the other
# optics, and how heavily they are drawn stands for the field gradient.
MOT_BEAM_WIDTH = 0.42
MOT_BEAM_OPACITY = 0.2  # fill, at full intensity
MOT_BEAM_EDGE_OPACITY = 0.8  # the arrowhead chevrons, at full intensity
MOT_BEAM_EDGE_WIDTH = 3
COIL_COLOR = OPTIC_COLOR
COIL_STRONG_WIDTH = 7  # the blue MOT's gradient
COIL_WEAK_WIDTH = 3  # the red MOTs', some ten times weaker
# An atom in a MOT glows in the colour of the light it scatters; one that has
# fallen into a state no beam addresses is dark.
CLOUD_DOT_RADIUS = 0.045
DARK_ATOM_COLOR = GUIDE_COLOR
DARK_ATOM_OPACITY = 0.8
FONT_TEMPERATURE = FONT_ANNOTATION
# Upstream of the MOT: the oven, the 2D MOT it feeds, and the push beam that
# sends a stream of atoms from there through the vacuum baffle. The oven and
# the baffle are hardware, so they take the optics grey; the oven gets a warm
# wash inside, in the holes' rim-light orange, because what it does is get hot.
# An atom straight out of the oven has met no light yet and is drawn grey,
# turning the 461 blue as it is caught.
OVEN_COLOR = OPTIC_COLOR
OVEN_HEAT_COLOR = HORIZON_GLOW
OVEN_HEAT_OPACITY = 0.3
BAFFLE_COLOR = OPTIC_COLOR
BAFFLE_WIDTH = 8
HOT_ATOM_COLOR = GUIDE_COLOR

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

# --- velocity slicing -----------------------------------------------------
# The velocity distribution is stacked by internal state, but what the scene
# is about is temperature, so the bands are coloured hot and cold: red for the
# thermal cloud left in |g>, blue for the cold slice the pulse moves to |e>.
# Translucent, so the pulse's line shape shows through them. The line shape is
# the clock laser's, so it takes the 698 nm red; the hot red is a deeper one,
# so the two stay apart where the line shape crosses the band.
SLICE_HOT_COLOR = ManimColor("#d8322a")
SLICE_COLD_COLOR = BLUE_D
SLICE_FILL_OPACITY = 0.55
SLICE_PROFILE_WIDTH = 3.5

# --- a high-flux atom source (HiFAIS) -------------------------------------
# The source's CAD renders, labelled on the page rather than in the image so
# the labels read on the dark background: plot-foreground text, with a thin
# leader in the lightened construction grey ending on a dot at the part.
CHAMBER_LABEL_COLOR = PLOT_FOREGROUND
CHAMBER_LEADER_STYLE = dict(stroke_width=2, color=lighten(GUIDE_COLOR))
CHAMBER_LEADER_DOT_RADIUS = 0.045
FONT_CHAMBER_LABEL = FONT_AXIS
FONT_CHAMBER_CAPTION = FONT_TICK
# The MOT loading curves (Fig. 5 inset), one per oven temperature, coolest to
# hottest on the cool-to-hot ramp the merger tracks' time dots already use --
# its last four stops, which all sample clear of the dark background.
OVEN_TEMPERATURE_COLORS = [ManimColor(c) for c in GW_MERGER_TIME_COLORS[1:]]
LOADING_DOT_RADIUS = 0.04
LOADING_ERROR_WIDTH = 2
LOADING_FIT_WIDTH = 2.5
# A fit carried on past the points it was fitted to is dashed: it is the
# model's prediction there, which the data are held against, not a fit.
LOADING_EXTRAPOLATION_DASH = 0.09
# The atom number the fits stop at: a reference, not data, like a band edge.
LOADING_CUTOFF_STYLE = GW_BAND_EDGE_STYLE
# A dimension drawn across a render: in the photo labels' yellow, which holds
# up against the CAD's greys and blues, outlined dark behind its line and text.
DIMENSION_COLOR = PHOTO_LABEL_COLOR
DIMENSION_STROKE_WIDTH = 3
DIMENSION_TIP_LENGTH = 0.16
DIMENSION_TICK = 0.12  # half the length of the bar across each end
DIMENSION_OUTLINE = dict(color=PLOT_BACKGROUND, width=6, opacity=0.85)
FONT_DIMENSION = FONT_CHAMBER_LABEL
