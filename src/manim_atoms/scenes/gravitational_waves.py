"""Gravitational waves from a binary black hole merger.

A flat sheet of spacetime, drawn as a wireframe grid, is dented by two black
holes and rippled by the radiation they emit. As the pair spirals in, both the
frequency and the amplitude of the ripples climb, until the holes merge and the
sheet rings down to a single well.

The field is evaluated at retarded time, so at any instant the rim of the sheet
is still showing the slow, weak waves emitted seconds earlier while the centre
shows the fast, strong ones -- that contrast across the sheet *is* the chirp.

MergerOnSensitivityPlot runs the merger beside LIGO's sensitivity curve, with a dot riding the source's characteristic-strain track in step with the
sheet. The track is real (a 60 Msun binary at z = 0.1, from aionanim.physics.gw_signals);
the dot's timing is not -- ten years of inspiral are squeezed into the
sheet's fourteen seconds, with a readout saying how long is really left.
With WITH_LIGO it first runs the merger beside LIGO itself (the
interferometer of aionanim.scenes.ligo, drawn into the right half, already
lit, its test masses swinging to this merger's own chirp), then flattens the
sheet and runs it again beside the plot.

Everything visual comes from aionanim.style.
"""

import numpy as np
from manim import *
from PIL import Image

from aionanim.tools.gw_plot import curve_points, detector_region, plot_point, sensitivity_axes
from aionanim.physics.gw_signals import (
    TRACK_START,
    YEAR,
    frequency_before_merger,
    merger_strain,
    merger_track,
    phenom_a_frequencies,
    time_before_merger,
)
from aionanim.resources import data_path
from aionanim.scenes.ligo import (
    Panel,
    make_apparatus,
    make_equation,
    make_light,
    make_strain_trace,
    returning_waves,
)
from aionanim.style import *

# --- sheet geometry -------------------------------------------------------
# The sheet is a wireframe rather than a Surface: a Surface rebuilds thousands
# of little quads every frame, while 2 * GRID_LINES polylines are just point
# arrays. GRID_LINES sets the line spacing, and the shortest wavelength the
# sheet has to carry (see WAVE_SPEED below) needs about four lines to resolve.
GRID_HALF = 5.5  # the sheet spans [-GRID_HALF, GRID_HALF] in x and y
GRID_LINES = 41  # grid lines per direction -> 0.275 spacing
GRID_SAMPLES = 111  # sample points along each line
GRADIENT_STOPS = 21  # colour stops per line; a gradient needs far fewer than
#                      samples, and each stop costs real time per frame
EDGE_FADE = 1.3  # width of the taper that flattens the sheet at the rim
HEIGHT_COLOR_SCALE = 0.45  # the height at which the colour ramp saturates

# --- the binary -----------------------------------------------------------
# Separation collapses from R_START to R_MERGE over T_INSPIRAL, and the orbital
# frequency rises with it. The exponent is derived from CHIRP_RATIO rather than
# set to Kepler's 3/2: a true 3/2 takes the frequency up by a factor of ~14 in
# the last second, which aliases against the grid and the frame rate. A factor
# of 3.5 is the most the sheet can actually draw, and it still reads as a chirp.
R_START = 2.2
R_MERGE = 0.38
T_INSPIRAL = 14.0
T_RINGDOWN = 4.5
INSPIRAL_SHARPNESS = 1.7  # how late in the inspiral the collapse happens
CHIRP_RATIO = 3.5  # final orbital frequency / initial
OMEGA_START = 1.2  # initial orbital angular frequency, rad/s
KEPLER_EXPONENT = np.log(CHIRP_RATIO) / np.log(R_START / R_MERGE)

BH_RADIUS = 0.38
REMNANT_RADIUS = 0.52
BH_SIT = 0.55  # fraction of its radius a hole sits above the sheet

# --- the radiation --------------------------------------------------------
# A quadrupole pattern: two arms rotating at twice the orbital frequency. The
# wavelength is WAVE_SPEED * pi / omega, so WAVE_SPEED is really a choice of
# how many ripples fit across the sheet -- 1.5 puts ~1.7 wavelengths across the
# radius at the start and ~5 at merger.
WAVE_SPEED = 1.5
H_START = 0.17  # strain amplitude while the binary is still wide
H_GROWTH = 0.8  # h ~ omega**H_GROWTH; 2/3 is the real chirp, 0.8 is legible
NEAR_ZONE = 1.0  # radius inside which the field is not retarded
# A true 1/rho falloff leaves the outer half of the sheet visibly flat, which
# buries the story. The profile below only zeroes the field inside the orbit
# and then fades gently, so a ripple is still legible when it reaches the rim.
RHO_SOFT = 1.1  # radius over which the field ramps up out of the near zone
RHO_FALL = 6.0  # scale of the 1/(1 + rho/RHO_FALL) decay beyond it
WAVE_ONSET = 0.8  # seconds over which the radiation switches on at t = 0
TAU_RINGDOWN = 0.9  # e-folding time of the post-merger amplitude

# --- the wells ------------------------------------------------------------
WELL_DEPTH = 0.62
WELL_WIDTH = 0.7
REMNANT_WELL_DEPTH = 1.15
REMNANT_WELL_WIDTH = 0.95
MERGE_BLEND = 1.0  # seconds over which two wells become one

T_END = T_INSPIRAL + T_RINGDOWN


# --- the source's history -------------------------------------------------
# Orbital phase is the integral of a frequency that changes the whole time, so
# it is tabulated once here and interpolated. The table runs from well before
# t = 0 because the rim of the sheet asks about retarded times that far back.
def separation(t):
    """Orbital separation (half the distance between the holes) at time t."""
    s = np.clip(t / T_INSPIRAL, 0.0, 1.0)
    return R_MERGE + (R_START - R_MERGE) * (1.0 - s) ** INSPIRAL_SHARPNESS


def omega(t):
    """Orbital angular frequency at time t, frozen at both ends."""
    return OMEGA_START * (R_START / separation(t)) ** KEPLER_EXPONENT


_T_TABLE = np.linspace(-15.0, T_END + 5.0, 30001)
_OMEGA_TABLE = omega(_T_TABLE)
_PHASE_TABLE = np.concatenate(
    [[0.0], np.cumsum(0.5 * (_OMEGA_TABLE[1:] + _OMEGA_TABLE[:-1]) * np.diff(_T_TABLE))]
)
_PHASE_TABLE -= np.interp(0.0, _T_TABLE, _PHASE_TABLE)


def orbital_phase(t):
    """Accumulated orbital phase, zero at t = 0."""
    return np.interp(t, _T_TABLE, _PHASE_TABLE)


def hole_positions(t):
    """Centres of the two holes, diametrically opposite on the orbit."""
    r = separation(t)
    phi = orbital_phase(t)
    offset = np.array([r * np.cos(phi), r * np.sin(phi), 0.0])
    return offset, -offset


# --- the field ------------------------------------------------------------
def smooth_step(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


def strain(t_emit):
    """Wave amplitude emitted at time t_emit: switches on, chirps, rings down."""
    growing = H_START * (omega(t_emit) / OMEGA_START) ** H_GROWTH
    decay = np.exp(-np.maximum(t_emit - T_INSPIRAL, 0.0) / TAU_RINGDOWN)
    return growing * decay * smooth_step(t_emit / WAVE_ONSET)


def wells(x, y, t, gain=1.0):
    """The static dent each hole makes, blended into one well at the merger."""
    p1, p2 = hole_positions(t)
    pair = sum(
        np.exp(-((x - p[0]) ** 2 + (y - p[1]) ** 2) / (2 * WELL_WIDTH**2))
        for p in (p1, p2)
    )
    single = (
        REMNANT_WELL_DEPTH
        / WELL_DEPTH
        * np.exp(-(x**2 + y**2) / (2 * REMNANT_WELL_WIDTH**2))
    )
    w = smooth_step((t - T_INSPIRAL) / MERGE_BLEND)
    return -gain * WELL_DEPTH * ((1.0 - w) * pair + w * single)


def sheet_height(x, y, t, gain=1.0):
    """Height of the spacetime sheet at (x, y) and scene time t."""
    rho = np.hypot(x, y)
    # Outside the near zone the sheet reports what the source was doing a
    # light-crossing time ago; that delay is what curls the pattern into arms.
    t_emit = t - np.maximum(rho - NEAR_ZONE, 0.0) / WAVE_SPEED
    radial = smooth_step(rho / RHO_SOFT) / (1.0 + rho / RHO_FALL)
    edge = smooth_step((GRID_HALF - rho) / EDGE_FADE)
    quadrupole = np.cos(2.0 * np.arctan2(y, x) - 2.0 * orbital_phase(t_emit))
    return wells(x, y, t, gain) + gain * strain(t_emit) * radial * edge * quadrupole


# --- colour by height -----------------------------------------------------
_LUT = [
    interpolate_color(TROUGH_COLOR, SHEET_COLOR, 1.0 + u)
    if u < 0
    else interpolate_color(SHEET_COLOR, CREST_COLOR, u)
    for u in np.linspace(-1.0, 1.0, 33)
]


def height_colors(z):
    """Map an array of heights onto the trough-sheet-crest ramp."""
    idx = (z / HEIGHT_COLOR_SCALE + 1.0) * 0.5 * (len(_LUT) - 1)
    return [_LUT[i] for i in np.clip(idx, 0, len(_LUT) - 1).astype(int)]


# --- mobjects -------------------------------------------------------------
# A stand-in reference point far below the sheet. Anything whose z_index_group
# is set to it sorts to the back: its depth is -1000 * cos(phi), which beats
# anything in the scene for any camera above the horizon. Used by the grid
# lines (see SheetLine).
BEHIND_EVERYTHING = VectorizedPoint([0.0, 0.0, -1000.0])


class SheetLine(VMobject):
    """A grid line that sits at the back of the camera's depth sort.

    shade_in_3d is what puts a mobject into ThreeDCamera's depth sort at all;
    anything without it scores np.inf, and np.inf sorts last, so an unshaded
    sheet is painted over the holes. But sorting the sheet honestly is no good
    either: each line spans the whole sheet, and the sort has only one depth
    per mobject to work with, so a line whose midpoint is near the camera gets
    drawn over the holes along its entire length. The wireframe ends up
    splattered across them.

    So the flag goes on and z_index_group sends every line to a point far
    behind the scene. All the lines then share one key, which leaves their
    order among themselves exactly as built, and the whole sheet lands behind
    both holes -- while the holes, which are compact enough for one depth each
    to be meaningful, sort properly against each other.

    Setting the flag has one side effect to undo: it reroutes the stroke
    gradient through get_3d_vmob_gradient_start_and_end_points, whose
    end-corner index ((n - 1) // 6) * 3 assumes a four-corner Surface face. On
    a polyline of a hundred-odd anchors that lands near the middle, squashing
    the height colours into the first half of every line.
    """

    def __init__(self, **kwargs):
        super().__init__(shade_in_3d=True, **kwargs)
        self.z_index_group = BEHIND_EVERYTHING

    def get_gradient_start_and_end_points(self):
        return self.points[0], self.points[-1]


def make_sheet():
    """The wireframe sheet, flat, with each line's sampling stashed on it."""
    grid = VGroup()
    coords = np.linspace(-GRID_HALF, GRID_HALF, GRID_LINES)
    samples = np.linspace(-GRID_HALF, GRID_HALF, GRID_SAMPLES)
    stops = np.linspace(0, GRID_SAMPLES - 1, GRADIENT_STOPS).astype(int)
    fixed = np.full_like(samples, 0.0)

    for c in coords:
        for xs, ys in ((samples, fixed + c), (fixed + c, samples)):
            line = SheetLine(stroke_width=SHEET_STROKE_WIDTH)
            line.set_points_as_corners(np.stack([xs, ys, np.zeros_like(xs)], axis=1))
            line.set_stroke(SHEET_COLOR, SHEET_STROKE_WIDTH)
            line.xs, line.ys, line.stops = xs, ys, stops
            grid.add(line)
    return grid


def refresh_sheet(grid, t, gain=1.0):
    """Re-evaluate every grid line at time t and recolour it by height."""
    for line in grid:
        z = sheet_height(line.xs, line.ys, t, gain)
        line.set_points_as_corners(np.stack([line.xs, line.ys, z], axis=1))
        line.set_stroke(color=height_colors(z[line.stops]))


def make_black_hole(radius=BH_RADIUS):
    """A black sphere with a warm rim mesh.

    It keeps manim's default shade_in_3d, which is what earns it a place in the
    camera's depth sort: ThreeDCamera.get_mobjects_to_display scores every
    mobject without that flag as np.inf, so unshaded mobjects are painted in
    scene order and two unshaded holes would never swap over as they orbit.
    The lighting pass itself is switched off at the camera (see construct), so
    the fill stays properly black instead of being brightened to grey.

    Nothing else is needed to make it read against the background: the hole
    sits in a well ringed by bright grid lines, so its silhouette is a gap
    punched in the wireframe, and the mesh supplies the curvature.
    """
    horizon = Sphere(radius=radius, resolution=(16, 16), checkerboard_colors=False)
    horizon.set_fill(HORIZON_COLOR, 1.0)
    horizon.set_stroke(HORIZON_GLOW, HORIZON_MESH_WIDTH, HORIZON_MESH_OPACITY)
    return horizon


def follow_orbit(hole, clock, which, gain, radius=BH_RADIUS):
    """Keep a hole on its orbit and resting in the bottom of its own well."""

    def update(m):
        t = clock.get_value()
        x, y = hole_positions(t)[which][:2]
        m.move_to([x, y, sheet_height(x, y, t, gain.get_value()) + BH_SIT * radius])

    hole.add_updater(update)
    update(hole)
    return hole


# --- the chirp trace ------------------------------------------------------
# The same field, sampled by one distant observer: the strip along the bottom
# is the waveform a detector would record, and it makes "frequency and
# amplitude both climb" a thing you can read off rather than infer.
TRACE_WIDTH = 9.0
TRACE_HEIGHT = 0.45
TRACE_CENTER = np.array([0.0, -3.45, 0.0])
TRACE_SAMPLES = 600


def observed_strain(t):
    """h(t) for an observer far out along +x, in the sheet's own height units."""
    return strain(t) * np.cos(2.0 * orbital_phase(t))


def make_trace(clock, center=TRACE_CENTER, width=TRACE_WIDTH):
    """A polyline of h(t) up to the current clock, pinned to the bottom edge."""
    curve = VMobject(stroke_width=3)
    scale = TRACE_HEIGHT / (H_START * CHIRP_RATIO**H_GROWTH)

    def update(m):
        t = max(clock.get_value(), 1e-3)
        ts = np.linspace(0.0, t, TRACE_SAMPLES)
        xs = center[0] - width / 2 + width * ts / T_END
        ys = center[1] + scale * observed_strain(ts)
        m.set_points_as_corners(np.stack([xs, ys, np.zeros_like(xs)], axis=1))
        m.set_stroke(color=height_colors(observed_strain(ts[::40]) * 3.0))

    curve.add_updater(update)
    update(curve)
    return curve


class BlackHoleMerger(ThreeDScene):
    """Two black holes spiral in, radiating, and merge into one ringing remnant."""

    # frame_center lifts the sheet off the bottom of the frame so the chirp
    # trace has a clear strip to live in.
    CAMERA = dict(
        phi=67 * DEGREES,
        theta=-60 * DEGREES,
        zoom=0.84,
        frame_center=[0.0, 0.0, -0.45],
    )
    AMBIENT_ROTATION = 0.02  # rad/s
    TITLE = r"Gravitational waves from a binary black hole merger"

    def entrance(self, clock):
        """Animations to play as the sheet and the title come in."""
        return []

    def show_signal(self, clock):
        """Bring in whatever reads the waves off the sheet, driven by clock."""
        trace = make_trace(clock)
        self.add_fixed_in_frame_mobjects(trace)
        self.play(FadeIn(trace), run_time=0.8)

    def after_ringdown(self, spacetime):
        """Anything to do once the sheet has settled; spacetime is the sheet
        and the remnant, updaters already stopped on the sheet."""

    def beat(self):
        """The pause once the signal is up and once the ringdown has settled
        (after the settling, so a click never lands on a still sheet):
        nothing here, a click on the slide version."""

    def construct(self):
        clock = ValueTracker(0.0)
        gain = ValueTracker(0.0)  # how strongly the sheet feels the holes

        # Depth sorting and lighting are both keyed off shade_in_3d, but only
        # the sorting is wanted here. The lighting pass keeps just the first two
        # stroke colours of whatever it touches, which would cut every grid
        # line's height gradient down to two stops, and it only ever brightens,
        # which turns a black horizon grey. Switching it off at the camera
        # leaves the sort untouched -- z_key never consults this flag.
        self.camera.should_apply_shading = False

        self.set_camera_orientation(**self.CAMERA)

        # --- 1. flat spacetime -------------------------------------------
        sheet = make_sheet()
        title = Tex(self.TITLE, font_size=FONT_TITLE).to_corner(UL)
        self.add_fixed_in_frame_mobjects(title)
        self.play(
            FadeIn(sheet, run_time=1.5), FadeIn(title, run_time=1.0), *self.entrance(clock)
        )

        # The sheet redraws from the clock from here on; everything below just
        # moves the clock and lets the field do the work.
        sheet.add_updater(
            lambda m: refresh_sheet(m, clock.get_value(), gain.get_value())
        )
        if self.AMBIENT_ROTATION:
            self.begin_ambient_camera_rotation(rate=self.AMBIENT_ROTATION)

        remnant = self.merge(sheet, clock, gain)

        # --- 6. one hole, one well, a sheet nearly flat again -------------
        sheet.clear_updaters()
        if self.AMBIENT_ROTATION:
            self.stop_ambient_camera_rotation()
        self.after_ringdown(VGroup(sheet, remnant))
        self.wait(1.0)

    def merge(self, sheet, clock, gain):
        """Stages 2-5 on a live, flat sheet with the clock at zero: two holes
        dent it, spiral in and merge, and the remnant rings down. Ends held
        on the settled sheet, still live; returns the remnant."""
        # --- 2. two holes dent it ----------------------------------------
        pair = VGroup(
            *[follow_orbit(make_black_hole(), clock, i, gain) for i in (0, 1)]
        )
        self.play(FadeIn(pair, scale=0.4), gain.animate.set_value(1.0), run_time=1.6)

        self.show_signal(clock)
        self.beat()

        # --- 3. the inspiral ---------------------------------------------
        # One linear sweep of the clock: the separation, the orbital frequency
        # and the retardation all follow from it, so the ripples tighten and
        # brighten on their own.
        self.play(
            clock.animate.set_value(T_INSPIRAL),
            rate_func=linear,
            run_time=T_INSPIRAL,
        )

        # --- 4. merger ----------------------------------------------------
        remnant = make_black_hole(REMNANT_RADIUS)
        remnant.add_updater(
            lambda m: m.move_to(
                [
                    0.0,
                    0.0,
                    sheet_height(0.0, 0.0, clock.get_value(), gain.get_value())
                    + BH_SIT * REMNANT_RADIUS,
                ]
            )
        )
        # Two rings leaving at different speeds read as a burst rather than as
        # one more ripple; they lie in the sheet's own plane, so they spread
        # across it instead of hanging in front of it.
        burst = VGroup(
            *[
                Circle(radius=0.5, color=HORIZON_GLOW, stroke_width=BURST_STROKE_WIDTH)
                for _ in range(2)
            ]
        )
        self.add(burst)
        self.play(
            clock.animate.set_value(T_INSPIRAL + MERGE_BLEND),
            FadeOut(pair, scale=0.5),
            FadeIn(remnant, scale=0.6),
            burst[0].animate.scale(7.0).set_stroke(opacity=0.0),
            burst[1].animate.scale(4.0).set_stroke(opacity=0.0),
            rate_func=linear,
            run_time=MERGE_BLEND,
        )
        self.remove(burst)

        # --- 5. ringdown --------------------------------------------------
        self.play(
            clock.animate.set_value(T_END),
            rate_func=linear,
            run_time=T_END - T_INSPIRAL - MERGE_BLEND,
        )
        self.wait(2.0)
        self.beat()
        return remnant


# --- the merger on a sensitivity plot -------------------------------------
SOURCE_MASS = 60  # Msun, total
SOURCE_Z = 0.1

# The plot sits on the right; the sheet is shrunk and pushed left to make room.
SENS_ORIGIN = np.array([1.35, -2.3, 0.0])  # lower-left corner of the axes
SENS_WIDTH = 5.2
SENS_HEIGHT = 4.0
LOG_F_RANGE = (-2, 4)  # the track starts ten years out, at ~0.01 Hz
LOG_H_RANGE = (-23, -18)
SIDE_SHEET_X = -3.6  # screen x of the sheet's centre
SIDE_ZOOM = 0.5
SIDE_TRACE_CENTER = np.array([SIDE_SHEET_X, -3.05, 0.0])  # the h(t) strip
SIDE_TRACE_WIDTH = 6.4

# Once the sheet settles, the left panel becomes what LIGO actually recorded
# from GW150914 -- a 36 + 29 Msun merger at z = 0.09, so a near twin of the
# track on the right. Its pure black is lifted to the talk's background so
# the image has no visible edge. Its time axis ends clear of the footer's
# citation line.
LIGO_DATA_IMAGE = data_path("images", "ligo20160211a.jpg")
LIGO_DATA_HEIGHT = 5.9
LIGO_DATA_CENTER = np.array([SIDE_SHEET_X, -0.5, 0.0])
# The figure runs from t = 0.25 s to 0.46 s with the peak at 0.42 s: from
# 0.17 s before merger (36 Hz on this track, the 35 Hz LIGO quote) on through
# the ringdown. That stretch of the track is recoloured as the data comes in.
LIGO_DATA_BEFORE_MERGER = 0.17

# The first run of the merger plays beside LIGO: the interferometer of
# aionanim.scenes.ligo in the right half, where the plot will go. It is up,
# already lit, from the first frame, and runs off the merger's clock, with the
# merger's own h(t) as its wave, scaled so the peak takes the detector from
# dark to fully bright. ligo.py draws for the whole frame, the readout in a
# column on the right; here the interferometer fills the top of the half and
# the readout goes in a band under it, clear of the citation line: h(t) and
# the equations on the left, the returning beams on the right. Each panel
# puts a point of ligo.py's drawing (a block's top or centre, measured off
# it) on a point of this frame.
LIGO_APPARATUS = Panel.at(0.68, [-2.635, 2.70], [3.65, 2.95])  # its top centre
LIGO_TRACE = Panel.at(0.5, [4.39, 2.85], [2.15, -2.0])
LIGO_EQUATION = Panel.at(0.5, [4.725, -2.71], [2.15, -2.84])  # and scale line
LIGO_RETURNS = Panel.at(0.5, [4.725, 0.23], [5.75, -2.65])
LIGO_TRACE_SPAN = (-0.3, T_END + 0.3)  # the stretch of the clock its h(t) spans
_PEAK_STRAIN = np.max(np.abs(observed_strain(np.linspace(0.0, T_END, 20001))))


def ligo_strain(t):
    """The merger's h at clock time t, normalised to a peak of 1."""
    return observed_strain(t) / _PEAK_STRAIN

# Ten years into T_INSPIRAL: the time left to merger is squeezed as
# (fraction of the inspiral left) ** CHIRP_WARP, so the dot crawls through
# the years and races through the last seconds, as the real chirp does. 8
# leaves it ~1.5 s inside LIGO's band (above 10 Hz), long enough to follow.
CHIRP_WARP = 8.0

# The readout steps down through these as the dot passes them.
TIME_LEFT = [
    (TRACK_START, r"10 years"),
    (YEAR, r"$<$ 1 year"),
    (YEAR / 12, r"$<$ 1 month"),
    (86400, r"$<$ 1 day"),
    (3600, r"$<$ 1 hour"),
    (60, r"$<$ 1 minute"),
    (1, r"$<$ 1 second"),
]


def side_frame_center(camera, zoom, screen_x):
    """The frame_center that puts the sheet's centre at screen_x.

    ThreeDCamera takes frame_center off twice: once before rotating and
    zooming the scene, and again, unrotated, when it maps the result to
    pixels. So the origin lands at -(zoom R + P) fc on screen, where R is the
    camera's rotation and P drops z; that is linear in fc's x and y (the
    perspective factor is ~1 at the sheet's centre), so solve it for them,
    keeping fc's z and the sheet's original screen height.
    """
    R = rotation_matrix(-camera["phi"], RIGHT) @ rotation_matrix(
        -camera["theta"] - 90 * DEGREES, OUT
    )
    fc = np.array(camera["frame_center"], dtype=float)
    M = zoom * R[:2] + np.eye(3)[:2]
    target = -(camera["zoom"] * R[:2] @ fc + fc[:2]) * zoom / camera["zoom"]
    target[0] = screen_x
    a, b = np.linalg.solve(M[:, :2], -target - M[:, 2] * fc[2])
    return np.array([a, b, fc[2]])


def source_frequency(t):
    """(f / Hz, real seconds left) of the source at scene time t: the chirp
    up to the merger frequency over the inspiral, then on through the
    ringdown to the track's cutoff while the holes merge."""
    fk = phenom_a_frequencies(SOURCE_MASS, SOURCE_Z)
    f_merge, f_cut = fk["merger"], fk["cutoff"] * (1 - 1e-6)
    if t <= T_INSPIRAL:
        left = np.clip(1 - t / T_INSPIRAL, 0, 1) ** CHIRP_WARP
        tau_merge = time_before_merger(f_merge, SOURCE_MASS, SOURCE_Z)
        tau = tau_merge + (TRACK_START - tau_merge) * left
        return frequency_before_merger(tau, SOURCE_MASS, SOURCE_Z), tau
    s = smooth_step((t - T_INSPIRAL) / MERGE_BLEND)
    return f_merge * (f_cut / f_merge) ** s, 0.0


class SideCamera(ThreeDCamera):
    """A ThreeDCamera whose frame-fixed mobjects ignore frame_center.

    The pixel mapping subtracts frame_center from everything, fixed or not, so
    an off-centre frame_center drags the overlay along with the sheet. This
    puts it back at the last step, which keeps working for mobjects whose
    updaters rebuild their points from absolute positions every frame.
    """

    def transform_points_pre_display(self, mobject, points):
        points = super().transform_points_pre_display(mobject, points)
        if mobject in self.fixed_in_frame_mobjects:
            return points + self.frame_center * [1, 1, 0]
        return points


class MergerOnSensitivityPlot(BlackHoleMerger):
    """The merger on the left; on the right, its signal crossing LIGO's band.

    WITH_LIGO runs it beside the LIGO interferometer first.
    """

    WITH_LIGO = False

    CAMERA = dict(
        BlackHoleMerger.CAMERA,
        zoom=SIDE_ZOOM,
        frame_center=side_frame_center(BlackHoleMerger.CAMERA, SIDE_ZOOM, SIDE_SHEET_X),
    )
    # The camera orbits frame_center, which is no longer the sheet's centre,
    # so any rotation would swing the sheet across the frame.
    AMBIENT_ROTATION = 0

    def __init__(self, **kwargs):
        super().__init__(camera_class=SideCamera, **kwargs)
        self.beside_ligo = False

    def merge(self, sheet, clock, gain):
        """Once beside LIGO, then, the sheet let go flat and the clock wound
        back, again beside the plot."""
        if not self.WITH_LIGO:
            return super().merge(sheet, clock, gain)
        self.beside_ligo = True
        remnant = super().merge(sheet, clock, gain)
        self.beside_ligo = False
        self.ligo.clear_updaters()
        self.trace.clear_updaters()
        self.play(
            FadeOut(remnant), FadeOut(self.ligo), FadeOut(self.trace),
            gain.animate.set_value(0.0), run_time=1.5,
        )
        clock.set_value(0.0)  # the sheet is flat whatever the clock says
        return super().merge(sheet, clock, gain)

    def show_signal(self, clock):
        if self.beside_ligo:
            self.show_ligo(clock)
        else:
            self.show_plot(clock)

    def entrance(self, clock):
        """LIGO on the right, lit, standing still until the clock runs."""
        if not self.WITH_LIGO:
            return []
        labels, optics, arm_tags = make_apparatus(clock, ligo_strain, LIGO_APPARATUS)
        labels.remove(labels[0])  # its title: the scene's own says enough
        on = ValueTracker(1.0)  # the beams are lit all the way from the start
        glow, lights = make_light(clock, on, on, ligo_strain, LIGO_APPARATUS)
        return_axes, return_waves, sum_axes, sum_wave = returning_waves(
            clock, ligo_strain, LIGO_RETURNS
        )
        trace_axes, trace = make_strain_trace(
            clock, ligo_strain, LIGO_TRACE_SPAN, LIGO_TRACE
        )
        # light under the optics, the glow under the detector
        self.ligo = VGroup(
            labels, glow, lights, optics, arm_tags,
            return_axes, return_waves, sum_axes, sum_wave,
            trace_axes, trace, *make_equation(LIGO_EQUATION),
        )
        self.add_fixed_in_frame_mobjects(self.ligo)
        return [FadeIn(self.ligo, run_time=1.5)]

    def show_ligo(self, clock):
        """The chirp strip under the sheet; LIGO is already up."""
        self.trace = make_trace(clock, SIDE_TRACE_CENTER, SIDE_TRACE_WIDTH)
        self.add_fixed_in_frame_mobjects(self.trace)
        self.play(FadeIn(self.trace), run_time=0.8)

    def show_plot(self, clock):
        axes, frame = sensitivity_axes(
            LOG_F_RANGE, LOG_H_RANGE, SENS_ORIGIN, SENS_WIDTH, SENS_HEIGHT
        )
        ligo_color = GW_DETECTOR_COLORS["LIGO"]
        region, ligo = detector_region(axes, "ligo", ligo_color)
        ligo_label = Tex("LIGO", font_size=FONT_AXIS, color=ligo_color)
        ligo_label.move_to(plot_point(axes, 3.3, -19.4))

        f, h = merger_track(SOURCE_MASS, SOURCE_Z)
        log_f = np.log10(f)
        ahead = VMobject(stroke_color=GW_MERGER_NEAR_COLOR, stroke_width=GW_TRACK_WIDTH,
                         stroke_opacity=GW_TRACK_AHEAD_OPACITY)
        ahead.set_points_as_corners(curve_points(axes, f, h))
        source_label = MathTex(
            rf"{SOURCE_MASS}\,M_\odot,\ z = {SOURCE_Z:g}",
            font_size=FONT_TICK, color=GW_MERGER_NEAR_COLOR,
        ).next_to(plot_point(axes, log_f[0], np.log10(h[0])), UP, buff=0.2, aligned_edge=LEFT)

        def reached(t):
            return (np.log10(source_frequency(t)[0]) - log_f[0]) / (log_f[-1] - log_f[0])

        lit = ahead.copy().set_stroke(opacity=1.0)
        lit.add_updater(
            lambda m: m.pointwise_become_partial(ahead, 0, reached(clock.get_value()))
            .set_stroke(opacity=1.0)
        )
        source = VGroup(
            Dot(radius=GW_SOURCE_GLOW_RADIUS, color=GW_SOURCE_COLOR,
                fill_opacity=GW_SOURCE_GLOW_OPACITY),
            Dot(radius=GW_SOURCE_RADIUS, color=GW_SOURCE_COLOR),
        )

        def ride(m):
            fs = source_frequency(clock.get_value())[0]
            hs = merger_strain(fs, SOURCE_MASS, SOURCE_Z)
            m.move_to(plot_point(axes, np.log10(fs), np.log10(hs)))

        source.add_updater(ride)
        ride(source)

        # The time left, pre-typeset: one Tex per step, only the current one lit.
        heading = Tex("Time to merger:", font_size=FONT_AXIS, color=PLOT_FOREGROUND)
        heading.next_to(plot_point(axes, LOG_F_RANGE[0], LOG_H_RANGE[1]), UP, buff=0.35,
                        aligned_edge=LEFT)
        steps = [(tau, Tex(text, font_size=FONT_AXIS, color=GW_SOURCE_COLOR))
                 for tau, text in TIME_LEFT]
        steps.append((0.0, Tex("merger", font_size=FONT_AXIS, color=GW_SOURCE_COLOR)))
        for _, tex in steps:
            tex.next_to(heading, RIGHT, buff=0.2)
        readout = VGroup(*(tex for _, tex in steps))

        def tick(m):
            t = clock.get_value()
            tau = source_frequency(t)[1]
            current = len(steps) - 1 if t >= T_INSPIRAL else max(
                i for i, (limit, _) in enumerate(steps[:-1]) if tau <= limit or i == 0
            )
            for i, tex in enumerate(m):
                tex.set_opacity(1.0 if i == current else 0.0)

        readout.add_updater(tick)
        tick(readout)

        f_data = frequency_before_merger(LIGO_DATA_BEFORE_MERGER, SOURCE_MASS, SOURCE_Z)
        self.data_window = ahead.copy().pointwise_become_partial(
            ahead, (np.log10(f_data) - log_f[0]) / (log_f[-1] - log_f[0]), 1
        ).set_stroke(color=GW_DATA_WINDOW_COLOR, opacity=1.0)
        self.source = source

        self.trace = make_trace(clock, SIDE_TRACE_CENTER, SIDE_TRACE_WIDTH)
        plot = VGroup(region, frame, ligo, ligo_label, ahead, source_label)
        live = VGroup(lit, source, heading, readout, self.trace)
        self.add_fixed_in_frame_mobjects(plot, live)
        self.play(FadeIn(plot), FadeIn(live), run_time=1.0)

    def after_ringdown(self, spacetime):
        pixels = np.asarray(Image.open(LIGO_DATA_IMAGE).convert("RGB"))
        floor = np.array(color_to_int_rgb(PLOT_BACKGROUND), dtype=np.uint8)
        data = ImageMobject(np.maximum(pixels, floor))
        data.height = LIGO_DATA_HEIGHT
        data.move_to(LIGO_DATA_CENTER)
        self.trace.clear_updaters()
        self.add_fixed_in_frame_mobjects(data, self.data_window)
        self.add(self.source)  # the dot stays on top of the recoloured track
        self.play(
            FadeOut(spacetime),
            FadeOut(self.trace),
            FadeIn(data, target_position=self.trace, scale=0.4),
            Create(self.data_window),
            run_time=1.5,
        )
        self.wait(3.0)
