"""Visual style for the talk's manim animations.

One place for the colour scheme, line styles, type sizes and pacing, so that
every animation in the talk reads as one set of figures:

    from manim import *
    from aionanim.style import *

The ``*_STYLE`` bundles are dicts meant to be splatted into a mobject's
constructor, e.g. ``DashedLine(a, b, **GUIDE_STYLE)``.
"""

import numpy as np
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
FONT_PHASE = 40
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
LOOP_AREA_STYLE = dict(stroke_width=0, fill_color=AREA_COLOR, fill_opacity=0.09)

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
# A burst marks the event, so it is struck at the vertex and stays there
# while the atom flies on -- which is what a space-time diagram says happened.
# It has to be brief for that to read as one moment rather than as the atom
# walking out of its own flash.
STROBE_FLASH = 0.18  # wall seconds
# ...and how long a pulse's worldline, its dashed reference and whatever it
# was captioned with stay up once it has passed. Long enough to be read is
# longer than the pulse itself lasts, so they linger into the next leg and
# go out only as the next pulse comes up behind them.
PULSE_LINGER = 1.2  # lab time

# --- spacetime and gravitational waves ------------------------------------
# The sheet is coloured by height, so it needs three shades that stay apart at
# a 1.5px stroke: a calm slate at rest, a bright crest and a deep trough. The
# holes themselves are warm, which is the one hue nothing else in the talk
# uses -- against the blue sheet they read instantly as the source.
SHEET_COLOR = ManimColor("#33607f")  # undisturbed spacetime
CREST_COLOR = ManimColor("#a8e4ff")  # a wave crest
TROUGH_COLOR = ManimColor("#54367f")  # a trough, and the floor of a gravitational well
HORIZON_COLOR = ManimColor("#000000")  # the event horizon: darker than the background
HORIZON_GLOW = ManimColor("#ffb26b")  # the rim light and the merger burst

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
FIELD_WINDOW_STYLE = dict(stroke_width=0, fill_color=AREA_COLOR, fill_opacity=0.16)

# The bodies a dark-matter wavelength is measured against. Muted, so the field
# drawn across them stays the brightest thing on the page; the Earth takes the
# atoms' blue because it is where the lab is.
EARTH_COLOR = ATOM_COLOR
MOON_COLOR = GREY_B
SUN_COLOR = ManimColor("#f5c542")
BODY_OPACITY = 0.85
BODY_MIN_RADIUS = 0.05  # below this a body drawn to scale is not there at all

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
# Bounded rather than a bare wash, unlike the field and strain windows: those
# mark a stretch of an oscillation that was always there, where this one marks
# a beam being switched on and off, and the two edges are those two moments.
# Something unspecified acting on the atoms for a stretch of the sequence --
# the generic version of the light-shift beam, drawn the same way (bounded:
# it is on for a while, then off) in a colour of its own.
PERTURBATION_COLOR = ManimColor("#e0b04a")
PERTURBATION_STYLE = dict(
    stroke_width=2,
    stroke_color=PERTURBATION_COLOR,
    stroke_opacity=0.6,
    fill_color=PERTURBATION_COLOR,
    fill_opacity=0.16,
)
LIGHT_SHIFT_STYLE = dict(
    stroke_width=2,
    stroke_color=LIGHT_SHIFT_COLOR,
    stroke_opacity=0.55,
    fill_color=LIGHT_SHIFT_COLOR,
    fill_opacity=0.16,
)

# --- phase, drawn as a clock hand -----------------------------------------
# A hand is only legible on an atom about twice the usual size, which crowds a
# figure, so only the atoms that actually carry one are grown. The hand is
# white because it has to read against both state colours.
CLOCK_ATOM_RADIUS = 0.32
CLOCK_HAND_COLOR = WHITE
CLOCK_HAND_WIDTH = 3
CLOCK_HAND_RATIO = 0.8  # of the atom's radius
CLOCK_DIAL_RADIUS = 0.95
CLOCK_SWEEP_OPACITY = 0.4

# --- the phase budget -----------------------------------------------------
# Breaking Phi into its terms sorts them into two kinds, and the colour does
# the sorting: white for the term the measurement is after, and the usual
# laser red for the one the light brings with it, circled or struck depending
# on the instrument. A ring lends its colour to its label; a struck term takes
# the grey instead, since the cross has already said the term is out of play.
SIGNAL_COLOR = WHITE
STRUCK_COLOR = GUIDE_COLOR
STRUCK_OPACITY = 0.45  # what a crossed-out term dims to
CROSS_COLOR = LASER_COLOR
CROSS_STROKE_WIDTH = 4
NOISE_COLOR = LASER_COLOR
RING_STROKE_WIDTH = 3
RING_BUFF = 0.18  # how far a ring stands off the term it circles

# --- output ports ---------------------------------------------------------
# What the last pulse actually produces: two states, each holding a fraction
# of the atoms fixed by the phase. A port that got none of them is still drawn
# -- as a dashed guide with a dimmed label -- because the null only reads as
# "all of them came out here" if the side they did not come out of is visible.
PORT_EMPTY = 0.02  # below this share, a port is drawn as an empty one
PORT_EMPTY_OPACITY = 0.4  # how far an empty port's label is dimmed


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
OPTIC_COLOR = lighten(GUIDE_COLOR)  # test masses, beam splitter, detector
BEAM_STROKE_WIDTH = 3
BEAM_GLOW_WIDTH = 10  # the faint band a beam's wave rides on
BEAM_GLOW_OPACITY = 0.18


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
LOWER_CLOUD_COLOR = CREST_COLOR
UPPER_CLOUD_COLOR = HORIZON_GLOW
LLN_COLOR = ManimColor("#44dd88")
HLN_COLOR = NOISE_COLOR
# The standard quantum limit the two runs' Allan deviations are held against
# is a reference, not a measurement, so it takes the guide grey: the paper's
# grey band of Monte Carlo runs (68% denser inside 95%) and its dotted
# 1/sqrt(tau) line.
SQL_COLOR = GUIDE_COLOR
SQL_BAND_OPACITIES = (0.4, 0.2)  # 68%, 95%
# The imprinted-signal scans (Fig. 5a): the phase the light shift put on takes
# the light shift's green, dashed over the white of what the gradiometer got
# back out of it.
IMPRINTED_SIGNAL_COLOR = LIGHT_SHIFT_COLOR
RECOVERED_SIGNAL_COLOR = SIGNAL_COLOR

# The same data drawn by manim, point by point. Axis text is a notch below the
# legend size because axis labels run long ("Lower interferometer excitation
# / %") and two plots have to share the frame side by side.
FONT_AXIS = 26
FONT_TICK = 24
DATA_DOT_RADIUS = 0.028
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
GW_MERGER_TIME_COLORS = ["#5e8fd9", "#4fc1c1", "#8fd46a", "#f0c24a", "#f06a4a"]


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
# A band edge on a sensitivity plot: a reference, not data, so dashed and
# in the axes' own colour.
GW_BAND_EDGE_STYLE = dict(
    dash_length=0.1, stroke_width=2, stroke_opacity=0.6, color=PLOT_FOREGROUND
)

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
VIDEO_BORDER_STYLE = dict(stroke_width=2, color=lighten(GUIDE_COLOR))
FONT_VIDEO_CLOCK = 24


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


# --- dipole traps ---------------------------------------------------------
# The trap beams are far off every resonance, so they drive nothing on the
# level scheme and take no transition colour: a pale warm white, the colour
# of light that holds atoms rather than addressing them. Drawn as nested
# translucent bands so a beam reads as a Gaussian profile, and faint, because
# the atoms have to show up inside them.
TRAP_BEAM_COLOR = ManimColor("#f3e3c8")
TRAP_BEAM_OPACITY = 0.3  # on the beam axis
TRAP_BEAM_LAYERS = 4
TRANSPARENCY_OPACITY = 0.35
MOT_GLOW_OPACITY = 0.22  # the red MOT's light, at its centre, beside the traps
MOT_GLOW_LAYERS = 8
FONT_CAPTION = FONT_LEGEND  # the step within a stage, under its heading


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


# --- phase-shear readout --------------------------------------------------
# The last pulse drawn as a broad beam rather than a wavepacket, because what
# matters here is its wavefronts: lines of equal laser phase, in the laser red,
# over a faint band of the same red that fades out above the atoms, so it
# reads as light passing on up rather than a slab that stops.
SHEAR_BEAM_OPACITY = 0.14
SHEAR_WAVEFRONT_STYLE = dict(stroke_width=2.5, color=LASER_COLOR, stroke_opacity=0.75)
SHEAR_AXIS_STYLE = dict(dash_length=0.1, stroke_width=2, stroke_opacity=0.6,
                        color=LASER_COLOR)
# A camera image of one output port: the port's state colour, bright where
# the atoms are, framed like the videos. Measured fringes are never full
# contrast, so neither are these.
SHEAR_IMAGE_BORDER_STYLE = VIDEO_BORDER_STYLE
SHEAR_CONTRAST = 0.85
SHEAR_PROFILE_WIDTH = 3.5  # the fitted fringe
SHEAR_DATA_DOT_RADIUS = 0.05  # the binned profile it is fitted to


# --- km-scale challenges table --------------------------------------------
# A table of text: the challenge in white with why it bites under it in the
# guide grey, the prototype's figures in the grey too (where we are), and
# AION-km's in white (where we need to be). A thin grey rule between rows.
FONT_TABLE_HEADING = FONT_LEGEND
FONT_TABLE_NAME = 28
FONT_TABLE_NOTE = 22
FONT_TABLE_CELL = 24
TABLE_RULE_STYLE = dict(stroke_width=1.5, color=GUIDE_COLOR, stroke_opacity=0.5)


# --- spin squeezing -------------------------------------------------------
# The quantum-noise blob of the collective spin. The coherent state is the
# standard quantum limit, which the talk already draws in the guide grey (the
# SQL band on the Allan plot); it stays up as a dashed outline once squeezed,
# as the reference the squeezed state is held against. The squeezed state
# takes the quiet run's green from the same plot: below the grey is where the
# green sat there too.
COHERENT_COLOR = SQL_COLOR
SQUEEZED_COLOR = LLN_COLOR
NOISE_BLOB_OPACITY = 0.3
NOISE_BLOB_STROKE_WIDTH = 3
# (set_stroke() keywords: both are dashed curves, not DashedLines)
COHERENT_OUTLINE_STROKE = dict(color=COHERENT_COLOR, width=2, opacity=0.7)
# The cavity probe counts the atoms in |g> on the 689 nm line, so the probe,
# the cavity mode and the transmission it reads out all take the 689 red; the
# measured value, marked on the spin's noise plane, is that reading too.
PROBE_COLOR = TRANSITION_689_COLOR
CAVITY_MODE_OPACITY = 0.45
MIRROR_STROKE_WIDTH = 7
PROBE_STROKE_WIDTH = 3
MEASURED_STYLE = dict(
    dash_length=0.1, stroke_width=2.5, stroke_opacity=0.9, color=PROBE_COLOR
)
EMPTY_CAVITY_STROKE = dict(color=GUIDE_COLOR, width=2.5, opacity=0.8)
TRANSMISSION_WIDTH = 3.5
# The Bloch sphere and the patch of it zoomed in on: furniture, in the
# lightened construction grey.
BLOCH_STYLE = dict(stroke_width=2, color=lighten(GUIDE_COLOR))
ZOOM_STYLE = dict(dash_length=0.08, stroke_width=1.5, stroke_opacity=0.5,
                  color=GUIDE_COLOR)
