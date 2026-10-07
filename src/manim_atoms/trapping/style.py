"""The trapping scenes' style: the core house style plus the experimental
sequence's timeline, dipole traps, laser cooling, velocity slicing and the
HiFAIS source.

    from manim import *
    from manim_atoms.trapping.style import *
"""

from manim_atoms.style import *

# --- the experimental sequence --------------------------------------------
# One shot of the experiment laid out as a timeline, with the Sr level scheme
# beside it showing which transition each stage drives. The timeline keeps
# the colours of the group's own sequence figure (fill, edge), so it reads as
# the same diagram the audience may already have seen.
SEQUENCE_STAGE_COLORS = {
    "blue_mot": ("#80b3ff", "#0066ff"),
    "modulated_red_mot": ("#ff5555", "#d40000"),
    "narrowband_red_mot": ("#e9afaf", "#c83737"),
    "upper_dipole_trap": ("#afe9dd", "#37c8ab"),
    "lower_dipole_trap": ("#ddafe9", "#ac39c8"),
    "spin_polarization": ("#d7f4d7", "#37c837"),
    "velocity_slicing": ("#ffe680", "#d4aa00"),
    "differential_interferometry": ("#ffaacc", "#aa0044"),
    "state_readout": ("#aaaaff", "#0000ff"),
}
# A stage still to come is faint, one already run half lit, the one running
# fully lit and ringed.
TIMELINE_AHEAD_OPACITY = 0.22
TIMELINE_DONE_OPACITY = 0.5
TIMELINE_ACTIVE_RING = dict(color=WHITE, width=4)
FONT_TIMELINE = 20
FONT_REFERENCE = 18
REFERENCE_IDLE_OPACITY = 0.7  # still legible from the back of a room when idle
# The imaging stops once the lower trap is loaded; the stages after it carry
# on over its last frame, dimmed, so the frame stays as a reminder of where
# the atoms are.
VIDEO_DIM_OPACITY = 0.5  # of the background-coloured veil drawn over it
FONT_VIDEO_CLOCK = 24

# --- dipole traps ---------------------------------------------------------
TRANSPARENCY_OPACITY = 0.35
MOT_GLOW_OPACITY = 0.22  # the red MOT's light, at its centre, beside the traps
MOT_GLOW_LAYERS = 8
FONT_CAPTION = FONT_LEGEND  # the step within a stage, under its heading

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
