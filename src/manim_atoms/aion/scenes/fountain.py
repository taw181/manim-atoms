"""An atomic fountain: cool in a MOT, launch, and interrogate in free flight.

The apparatus is on the left -- a MOT at the foot of a vertical tube -- and
the fountain's space-time diagram on the right, sharing its height axis, so a
cloud in the tube and the same cloud on the diagram are always level, joined
by a faint dashed tie line.

Strontium, as in AION: a blue MOT on the broad 461 nm line catches the atoms
and a red MOT on the narrow 689 nm line cools them to microkelvin. A vertical
optical lattice then lifts the cloud and lets it go, and from there it flies
a parabola up the tube and back. On the way it is interrogated by a
Mach-Zehnder sequence on the 698 nm clock line, the laser coming up the tube
from below: pi/2 on the way up, pi at the top, pi/2 on the way down,
symmetric about the apex. Each pulse rises up the tube and up its column of
the diagram at once. The arms are two clouds in the tube, drifting apart and
back together, and on the diagram the bowed Mach-Zehnder of the gravimeter.
The two output ports are imaged by fluorescence as they fall back, and their
populations read out the phase gravity has written in, Phi = k g T^2.
"""

import numpy as np
from manim import *

from manim_atoms.aion.style import *
from manim_atoms.core.primitives import (
    absorb,
    emit,
    fluoresce,
    grow,
    make_atom,
    make_k_arrow,
    momentum_arrow,
    state_colors,
    state_label,
)
from manim_atoms.core.spacetime import carry, growing_trail, run_to, worldline
from manim_atoms.interferometry.scenes.mach_zehnder import MachZehnder
from manim_atoms.interferometry.tools.gravimeter import curved_loop
from manim_atoms.trapping.scenes.cooling import COOL_TEMPERATURE_TEX
from manim_atoms.trapping.tools.cooling import AtomCloud, Coils, MotBeams
from manim_atoms.trapping.tools.sequence import Stage, stage_heading
from manim_atoms.aion.tools.fountain import (
    FT_MOT_REACH,
    FT_COIL_SCALE,
    FT_PULSE_T,
    FT_T_LAUNCH,
    FT_T_READOUT,
    FT_T_REL,
    FT_T_START,
    FT_TUBE_X,
    FT_Z_MOT,
    before_split,
    fall,
    follow,
    mach_zehnder_corners,
    make_lattice,
    make_tube,
    tie,
)

# --- layout ---------------------------------------------------------------
FT_A, FT_B, FT_B_UP, FT_C, FT_PORT_G, FT_PORT_E = mach_zehnder_corners()
FT_MOT = np.array([FT_TUBE_X, FT_Z_MOT, 0.0])
FT_HEADING_CORNER = np.array([-3.35, 3.8, 0.0])  # right of the tube, left of the pi column
FT_TEMPERATURE_AT = FT_MOT + np.array([2.55, 0.95, 0.0])
FT_AXIS_Y = -3.1  # the time axis, under everything the atoms do
FT_AXIS_X = FT_T_START - 0.3  # the height axis, between tube and diagram
FT_AXIS_TOP = 3.0
FT_TICK = 0.09
FT_READOUT_AT = np.array([5.15, 1.3, 0.0])
# The pi pulse's two recoil arrows share a column between the arms, so they
# are shortened to meet without overlapping.
FT_MIRROR_ARROW = 0.8

# --- the stages, as headings ----------------------------------------------
FT_STAGES = {
    "blue": Stage("blue_mot", r"Blue MOT", "461"),
    "red": Stage("narrowband_red_mot", r"Red MOT", "689"),
    "launch": Stage("upper_dipole_trap", r"Lattice launch"),
    "mz": Stage("differential_interferometry", r"Mach--Zehnder", "698"),
    "readout": Stage("state_readout", r"State readout", "461"),
}
# The cloud at the end of each MOT stage: (radius, temperature), as in the
# cooling scene but scaled down to this MOT's beams.
FT_CLOUD = {"blue": (0.55, 1.0), "red": (0.15, 0.008)}
FT_N_ATOMS = 120
FT_N_ARM = 60  # each arm's cloud, once split

# --- pacing ---------------------------------------------------------------
FT_SWITCH_TIME = 1.2
FT_LOAD_TIME = 3.0
FT_COOL_TIME = 2.5
FT_LIFT_TIME = 1.2  # the lattice's acceleration, slowed down to be seen


class Fountain(MachZehnder):
    """MOT, lattice launch, and a pi/2 - pi - pi/2 fountain interferometer.

    Built from MachZehnder's pieces (legend, pulse captions, beats) and the
    cooling scene's MOT, with the flight on one lab clock (core.spacetime)
    that stops while each pulse is drawn, as the explainers do.
    """

    def construct(self):
        # --- 1. the apparatus --------------------------------------------
        tube = make_tube()
        coils = Coils(FT_MOT).scale(FT_COIL_SCALE, about_point=FT_MOT)
        blue = MotBeams(TRANSITION_461_COLOR, FT_MOT, reach=FT_MOT_REACH)
        red = MotBeams(TRANSITION_689_COLOR, FT_MOT, reach=FT_MOT_REACH)
        heading = self.heading("blue")
        self.play(Create(tube), Create(coils), FadeIn(blue), FadeIn(heading),
                  run_time=FT_SWITCH_TIME)
        self.beat()

        # --- 2. blue MOT: load, hot --------------------------------------
        radius, temperature = FT_CLOUD["blue"]
        cloud = AtomCloud(FT_N_ATOMS, FT_MOT, n_leak=0,
                          palette=(TRANSITION_461_COLOR, TRANSITION_689_COLOR),
                          radius=radius, temperature=temperature)
        cloud.arrived.set_value(0)
        self.add(cloud)
        self.play(cloud.arrived.animate.set_value(1), rate_func=linear,
                  run_time=FT_LOAD_TIME)
        tag = self.temperature("blue_mot")
        self.play(FadeIn(tag))
        self.beat()

        # --- 3. red MOT: small and cold ----------------------------------
        radius, temperature = FT_CLOUD["red"]
        new_tag = self.temperature("narrowband_red_mot")
        heading = self.switch_heading(heading, "red", [
            FadeOut(blue), FadeIn(red), coils.animate.set_gradient(COIL_WEAK_WIDTH),
            cloud.glow.animate.set_value(1),
        ])
        self.play(cloud.radius.animate.set_value(radius),
                  cloud.temperature.animate.set_value(temperature),
                  Succession(FadeOut(tag), FadeIn(new_tag)), run_time=FT_COOL_TIME)
        tag = new_tag
        self.beat()

        # --- 4. the diagram, and the lattice launch ----------------------
        clock = ValueTracker(FT_T_START)
        offset = ValueTracker(0.0)
        offset.add_updater(lambda m: m.set_value(before_split(clock.get_value()) - FT_Z_MOT))
        lattice = make_lattice(offset)
        axes = self.make_axes()
        trapped = Tex(r"trapped", font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR))
        trapped.next_to([(FT_T_START + FT_T_LAUNCH) / 2, FT_Z_MOT, 0], DOWN, buff=0.25)

        atom = make_atom().move_to([FT_T_START, FT_Z_MOT, 0])
        atom.add_updater(lambda m: m.move_to([clock.get_value(),
                                              before_split(clock.get_value()), 0]))
        trail = always_redraw(lambda: ParametricFunction(
            lambda t: np.array([t, before_split(t), 0.0]),
            t_range=[FT_T_START, max(clock.get_value(), FT_T_START + 1e-3), 0.01],
            color=ATOM_COLOR, **TRAJECTORY_STYLE,
        ))
        # in the tube, the atoms are now in |g>: ATOM_COLOR rather than the
        # red light they were scattering
        cloud.palette = [ManimColor(TRANSITION_689_COLOR), ManimColor(ATOM_COLOR)]
        cloud.glow.set_value(0)
        follow(cloud, before_split, clock)
        tie0 = tie(atom)

        heading = self.switch_heading(heading, "launch", [
            FadeOut(red), FadeOut(tag), coils.animate.set_stroke(opacity=0.35),
            cloud.glow.animate.set_value(1),
            FadeIn(lattice), FadeIn(axes), FadeIn(trapped),
        ])
        self.add(offset, trail, tie0, atom)
        self.play(FadeIn(atom, scale=0.5), run_time=0.5)
        run_to(self, clock, FT_T_LAUNCH)
        # the lattice's acceleration is a few ms of the flight: slowed to be seen
        self.play(clock.animate.set_value(FT_T_REL), rate_func=linear,
                  run_time=FT_LIFT_TIME)
        legend = self.make_legend().to_corner(UR)
        run_to(self, clock, FT_PULSE_T[0], FadeOut(lattice), FadeOut(trapped),
               FadeIn(legend))
        self.remove(offset)
        self.beat()

        # --- 5. first pi/2: split, on the way up -------------------------
        t1, t2, t3 = FT_PULSE_T
        k_arrow = make_k_arrow(t1 - 0.9, -config.frame_y_radius + 0.45)
        heading = self.switch_heading(heading, "mz", [])
        absorb(self, t1, atom,
               extras=[self.pulse_caption(r"\pi/2", t1), k_arrow],
               fade=[k_arrow], also=[(FT_TUBE_X, cloud)])

        lower_path = worldline([FT_A, FT_B, FT_C], fall)
        upper_path = worldline([FT_A, FT_B_UP, FT_C], fall)
        lower = carry(make_atom(opacity=SUPERPOSITION_OPACITY), lower_path, clock)
        upper = carry(make_atom(KICKED_COLOR, opacity=SUPERPOSITION_OPACITY),
                      upper_path, clock)
        lower_cloud = self.arm_cloud(cloud, lower_path, clock, excited=False, seed=5)
        upper_cloud = self.arm_cloud(cloud, upper_path, clock, excited=True, seed=6)
        legs = VGroup(
            growing_trail([FT_A, FT_B], ATOM_COLOR, clock, fall),
            growing_trail([FT_B, FT_C], KICKED_COLOR, clock, fall),
            growing_trail([FT_A, FT_B_UP], KICKED_COLOR, clock, fall),
            growing_trail([FT_B_UP, FT_C], ATOM_COLOR, clock, fall),
        )
        atom.clear_updaters()
        trail.clear_updaters()
        self.remove(atom, cloud, tie0)
        arm_ties = VGroup(tie(lower), tie(upper))
        self.add(legs, lower_cloud, upper_cloud, arm_ties, lower, upper)
        recoil = momentum_arrow(FT_A, UP, r"\hbar k")
        self.play(*grow(recoil), run_time=0.6)
        run_to(self, clock, t2, FadeOut(recoil))
        self.beat()

        # --- 6. pi pulse at the top: the mirror --------------------------
        # The ground-state arm absorbs (+hbar k); the excited arm is driven
        # down by stimulated emission (-hbar k), and the two converge.
        gain = momentum_arrow(FT_B, UP, r"+\hbar k", length=FT_MIRROR_ARROW)
        lose = momentum_arrow(FT_B_UP, DOWN, r"-\hbar k", label_dir=RIGHT,
                              length=FT_MIRROR_ARROW)
        absorb(self, t2, lower, extras=[self.pulse_caption(r"\pi", t2)],
               also=[(FT_TUBE_X, lower_cloud)])
        self.play(state_colors(lower, KICKED_COLOR),
                  lower_cloud.glow.animate.set_value(1), *grow(gain), run_time=0.6)
        emit(self, t2, upper, also=[(FT_TUBE_X, upper_cloud)])
        self.play(state_colors(upper, ATOM_COLOR),
                  upper_cloud.glow.animate.set_value(0), *grow(lose), run_time=0.6)
        run_to(self, clock, t3, FadeOut(gain), FadeOut(lose))
        self.beat()

        # --- 7. last pi/2 on the way down: recombine, ports, readout ----
        absorb(self, t3, lower, extras=[self.pulse_caption(r"\pi/2", t3)],
               also=[(FT_TUBE_X, lower_cloud)])
        g_path = worldline([FT_C, FT_PORT_G], fall)
        e_path = worldline([FT_C, FT_PORT_E], fall)
        port_g = carry(make_atom(opacity=SUPERPOSITION_OPACITY), g_path, clock)
        port_e = carry(make_atom(KICKED_COLOR, opacity=SUPERPOSITION_OPACITY), e_path, clock)
        cloud_g = self.arm_cloud(lower_cloud, g_path, clock, excited=False, seed=7)
        cloud_e = self.arm_cloud(lower_cloud, e_path, clock, excited=True, seed=8)
        ports = VGroup(growing_trail([FT_C, FT_PORT_G], ATOM_COLOR, clock, fall),
                       growing_trail([FT_C, FT_PORT_E], KICKED_COLOR, clock, fall))
        for m in (lower, upper):
            m.clear_updaters()
        self.remove(lower, upper, lower_cloud, upper_cloud, arm_ties)
        self.add(ports, cloud_g, cloud_e, tie(port_g), tie(port_e), port_g, port_e)
        run_to(self, clock, FT_T_READOUT)

        heading = self.switch_heading(heading, "readout", [])
        fluoresce(self, [cloud_g, cloud_e])
        p_g = state_label(r"P_g", ATOM_COLOR).next_to(port_g, RIGHT, buff=0.3)
        p_e = state_label(r"P_e", KICKED_COLOR).next_to(port_e, RIGHT, buff=0.3)
        self.play(Write(p_g), Write(p_e), run_time=1.0)
        self.beat()

        # --- 8. the phase gravity wrote in -------------------------------
        loop = curved_loop([FT_A, FT_B, FT_C, FT_B_UP], fall)
        phi = MathTex(r"\Phi", font_size=FONT_PHASE, color=lighten(AREA_COLOR))
        phi.move_to((FT_B + FT_B_UP) / 2)  # the loop's widest point
        readout = VGroup(
            MathTex(r"P_{g,e} = \tfrac{1}{2}\left(1 \pm \cos\Phi\right)",
                    font_size=FONT_ANNOTATION),
            MathTex(r"\Phi = k\,g\,T^2", font_size=FONT_PHASE, color=SIGNAL_COLOR),
        ).arrange(DOWN, buff=0.35).move_to(FT_READOUT_AT)
        self.add(loop)
        self.bring_to_back(loop)
        self.play(FadeIn(loop), FadeIn(phi), Write(readout), run_time=1.5)
        self.wait(2.0)

    # --- helpers ---------------------------------------------------------
    def heading(self, key):
        return stage_heading(FT_STAGES[key]).move_to(FT_HEADING_CORNER, aligned_edge=UL)

    def switch_heading(self, heading, key, anims):
        """Move on to stage ``key``'s heading alongside ``anims``."""
        new = self.heading(key)
        self.play(*anims,
                  # out, then in: two headings crossing each other can't be read
                  Succession(FadeOut(heading, shift=UP * 0.2), FadeIn(new, shift=UP * 0.2)),
                  run_time=FT_SWITCH_TIME)
        return new

    @staticmethod
    def temperature(key):
        return MathTex(COOL_TEMPERATURE_TEX[key], font_size=FONT_TEMPERATURE,
                       color=lighten(GUIDE_COLOR)).move_to(FT_TEMPERATURE_AT)

    @staticmethod
    def arm_cloud(parent, path, clock, excited, seed):
        """Half of ``parent``'s atoms, in the tube on ``path``: one arm's
        share of the cloud, in that arm's state colour."""
        cloud = AtomCloud(FT_N_ARM, parent.center, n_leak=0, seed=seed,
                          palette=(ATOM_COLOR, KICKED_COLOR),
                          radius=FT_CLOUD["red"][0],
                          temperature=parent.temperature.get_value())
        cloud.glow.set_value(1 if excited else 0)
        return follow(cloud, lambda t: path(t)[1], clock, radius0=FT_CLOUD["red"][0])

    @staticmethod
    def make_axes():
        """Height up the side, shared with the tube; lab time along the
        bottom, with a tick at each pulse: 0, T, 2T."""
        y = FT_AXIS_Y
        height = Arrow([FT_AXIS_X, y, 0], [FT_AXIS_X, FT_AXIS_TOP, 0], buff=0,
                       max_tip_length_to_length_ratio=0.04, **TIME_AXIS_STYLE)
        z = MathTex("z", font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR))
        z.next_to(height, UP, buff=0.1)
        time = Arrow([FT_AXIS_X, y, 0], [FT_T_READOUT + 0.9, y, 0], buff=0,
                     max_tip_length_to_length_ratio=0.04, **TIME_AXIS_STYLE)
        axes = VGroup(height, z, time)
        for x, tex in zip(FT_PULSE_T, ("0", "T", "2T")):
            axes.add(Line([x, y - FT_TICK, 0], [x, y + FT_TICK, 0], **TIME_AXIS_STYLE))
            axes.add(MathTex(tex, font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR))
                     .move_to([x - 0.35, y - 0.3, 0]))  # clear of the column
        axes.add(MathTex("t", font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR))
                 .next_to(time, RIGHT, buff=0.12))
        return axes
