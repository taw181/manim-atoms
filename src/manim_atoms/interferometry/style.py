"""The interferometry scenes' style: the core house style plus phase drawn
as a clock hand and its budget, output ports, the pulses' pacing, an
injected perturbation, phase-shear readout and spin squeezing.

    from manim import *
    from manim_atoms.interferometry.style import *
"""

from manim_atoms.style import *

# --- type -----------------------------------------------------------------
FONT_PHASE = 40

# --- line styles ----------------------------------------------------------
LOOP_AREA_STYLE = dict(stroke_width=0, fill_color=AREA_COLOR, fill_opacity=0.09)

# --- pacing ---------------------------------------------------------------
# A burst marks the event, so it is struck at the vertex and stays there
# while the atom flies on -- which is what a space-time diagram says happened.
# It has to be brief for that to read as one moment rather than as the atom
# walking out of its own flash.
STROBE_FLASH = 0.18  # wall seconds

# --- an injected light shift ----------------------------------------------
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

# --- the phase budget -----------------------------------------------------
STRUCK_COLOR = GUIDE_COLOR
STRUCK_OPACITY = 0.45  # what a crossed-out term dims to
CROSS_COLOR = LASER_COLOR
CROSS_STROKE_WIDTH = 4
RING_STROKE_WIDTH = 3
RING_BUFF = 0.18  # how far a ring stands off the term it circles

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

# --- output ports ---------------------------------------------------------
# What the last pulse actually produces: two states, each holding a fraction
# of the atoms fixed by the phase. A port that got none of them is still drawn
# -- as a dashed guide with a dimmed label -- because the null only reads as
# "all of them came out here" if the side they did not come out of is visible.
PORT_EMPTY = 0.02  # below this share, a port is drawn as an empty one
PORT_EMPTY_OPACITY = 0.4  # how far an empty port's label is dimmed

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

# --- spin squeezing -------------------------------------------------------
# The quantum-noise blob of the collective spin. The coherent state is the
# standard quantum limit, which the talk already draws in the guide grey (the
# SQL band on the Allan plot); it stays up as a dashed outline once squeezed,
# as the reference the squeezed state is held against. The squeezed state
# takes the quiet run's green from the same plot: below the grey is where the
# green sat there too.
COHERENT_COLOR = SQL_COLOR
SQUEEZED_COLOR = LLN_COLOR
# (set_stroke() keywords: both are dashed curves, not DashedLines)
COHERENT_OUTLINE_STROKE = dict(color=COHERENT_COLOR, width=2, opacity=0.7)
MEASURED_WIDTH = 2.5  # the ring of fixed J_z the measurement pins the spin to
EMPTY_CAVITY_STROKE = dict(color=GUIDE_COLOR, width=2.5, opacity=0.8)
TRANSMISSION_WIDTH = 3.5
