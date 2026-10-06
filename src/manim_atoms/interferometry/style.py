"""The interferometry scenes' style: the core house style plus phase drawn
as a clock hand, output ports, phase-shear readout and spin squeezing.

    from manim import *
    from manim_atoms.interferometry.style import *
"""

from manim_atoms.style import *

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
MEASURED_WIDTH = 2.5  # the ring of fixed J_z the measurement pins the spin to
EMPTY_CAVITY_STROKE = dict(color=GUIDE_COLOR, width=2.5, opacity=0.8)
TRANSMISSION_WIDTH = 3.5
# The Bloch sphere: furniture, in the lightened construction grey, with its
# axis through the poles a faint dashed guide.
BLOCH_STYLE = dict(stroke_width=2, color=lighten(GUIDE_COLOR))
BLOCH_AXIS_STYLE = dict(dash_length=0.08, stroke_width=1.5, stroke_opacity=0.5,
                        color=GUIDE_COLOR)

# --- Ramsey-Borde: two loops from four pi/2 pulses ------------------------
# Four beamsplitters open more paths than close. The two loops that do close
# are shaded in the state their arms share through the dark time T' -- the
# upper loop flies it in |e>, the lower in |g> -- which is what tells the two
# apart where they overlap during the first T, which they share. Paths that
# never meet a partner again carry no fringe; they are drawn dashed and faint,
# so the figure says they exist without letting them compete with the loops.
RB_UPPER_LOOP_STYLE = dict(stroke_width=0, fill_color=KICKED_COLOR, fill_opacity=0.14)
RB_LOWER_LOOP_STYLE = dict(stroke_width=0, fill_color=ATOM_COLOR, fill_opacity=0.14)
OPEN_PATH_STYLE = dict(dash_length=0.1, stroke_width=2.5, stroke_opacity=0.5)
OPEN_ATOM_OPACITY = 0.25
# The pulse timing marked along the bottom, a reference rather than content.
TIME_AXIS_STYLE = dict(stroke_width=2, color=lighten(GUIDE_COLOR), stroke_opacity=0.7)

# --- a gravimeter: the interferometer in free fall -------------------------
# Gravity bends every arm by the same parabola, so it is drawn as something
# acting on the atoms -- the perturbation amber, which samples clear of both
# state colours and the laser red. What the arms would have done without it,
# the straight parallelogram of the freely falling frame, is a reference and
# takes the construction grey, dashed but a notch brighter than a guide so it
# still reads beside the solid arms.
GRAVITY_COLOR = PERTURBATION_COLOR
GRAVITY_ARROW_STYLE = dict(
    buff=0, stroke_width=3, color=GRAVITY_COLOR, max_tip_length_to_length_ratio=0.25
)
FREE_FALL_STYLE = dict(
    dash_length=0.12, stroke_width=2.5, stroke_opacity=0.55, color=lighten(GUIDE_COLOR)
)
