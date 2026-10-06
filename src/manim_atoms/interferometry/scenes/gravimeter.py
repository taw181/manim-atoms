"""The atom gravimeter: a Mach-Zehnder interferometer in free fall.

A space-time diagram, time across and height up, with the laser pointing up
against gravity. The atoms are released from a trap at the first pulse, and
from then on every arm falls: each leg is the straight one MachZehnder draws,
bent down by the same parabola, g t^2 / 2. The loop still closes -- gravity
moves both arms alike -- but the pulses now find the atoms lower and lower,
and each pulse writes the laser's phase k z at the height it finds them. In
the falling frame the parallelogram's own phases cancel, so what is left is
the second difference of the fall:

    Phi = k [ d(0) - 2 d(T) + d(2T) ] = k g T^2,   d(t) = g t^2 / 2,

taking Phi as the lower arm's phase less the upper's; the other order gives
-k g T^2, which is k.g T^2 with k up and g down. The readout, cos Phi, does
not care.
"""

import numpy as np
from manim import *

from manim_atoms.interferometry.style import *
from manim_atoms.core.primitives import (
    absorb,
    emit,
    grow,
    make_atom,
    make_guide,
    make_k_arrow,
    momentum_arrow,
    state_colors,
    state_label,
)
from manim_atoms.core.spacetime import draw_wavy_legs
from manim_atoms.interferometry.scenes.mach_zehnder import MachZehnder
from manim_atoms.interferometry.tools.gravimeter import (
    GV_A,
    GV_OUT,
    GV_T,
    curved_loop,
    drop_arrow,
    fall,
    free_fall_corners,
    in_lab,
)

# --- layout ---------------------------------------------------------------
# The free-fall corners, and where the pulses really find the atoms.
FF_A, FF_B, FF_B_UP, FF_C = free_fall_corners()
GV_B, GV_B_UP, GV_C = in_lab(FF_B), in_lab(FF_B_UP), in_lab(FF_C)
# The ports: |g, p> carries on with the lower arm's free-fall velocity (none),
# |e, p + hbar k> with one recoil; both keep falling.
GV_PORT_G = in_lab(FF_C + RIGHT * GV_OUT)
GV_PORT_E = in_lab(FF_C + (RIGHT + UP) * GV_OUT)
GV_PULSE_X = (GV_A[0], GV_B[0], GV_C[0])

GV_AXIS_Y = -2.9  # the time axis, below everything the atoms do
GV_TICK = 0.09
GV_G_ARROW = (np.array([-6.55, 1.1, 0.0]), np.array([-6.55, -0.1, 0.0]))
GV_TRAP_LABEL = np.array([-6.35, GV_A[1] + 0.35, 0.0])  # clear of the first column
# The phase is worked out in the clear space right of the ports, under the
# title and above the port labels.
GV_PANEL_TOP = 2.95
GV_PANEL_EDGE = 0.25  # from the right edge of the frame
GV_PHI = np.array([GV_B[0], 0.05, 0.0])  # inside the loop, between the drop arrows


class Gravimeter(MachZehnder):
    """pi/2 - pi - pi/2 on atoms falling under gravity, ending on Phi = k g T^2.

    Built from MachZehnder's pieces (legend, pulse captions, beats), with the
    straight legs swapped for core.spacetime's displaced ones.
    """

    def construct(self):
        # --- 1. setup ----------------------------------------------------
        title = Tex(
            r"Atom gravimeter: a Mach--Zehnder in free fall", font_size=FONT_TITLE
        ).to_corner(UR)
        legend = self.make_legend().to_corner(UL)
        g_arrow = Arrow(*GV_G_ARROW, **GRAVITY_ARROW_STYLE)
        g_label = MathTex(r"\vec g", font_size=FONT_ANNOTATION,
                          color=lighten(GRAVITY_COLOR)).next_to(g_arrow, RIGHT, buff=0.15)
        guide = make_guide([-config.frame_x_radius, GV_A[1], 0], GV_A)
        trap = Tex(r"trapped", font_size=FONT_LEGEND,
                   color=lighten(GUIDE_COLOR)).move_to(GV_TRAP_LABEL)
        axis = self.make_time_axis()
        self.play(*[FadeIn(m) for m in (title, legend, g_arrow, g_label, guide, trap, axis)],
                  run_time=1.0)
        self.beat()

        # --- 2. the atom, held, then released at the first pulse --------
        atom = make_atom().move_to([-config.frame_x_radius + 0.2, GV_A[1], 0])
        self.play(FadeIn(atom, scale=0.5), run_time=0.5)
        self.play(atom.animate.move_to(GV_A), rate_func=linear,
                  run_time=(GV_A[0] - atom.get_center()[0]) / V)

        # --- 3. first pi/2: split, and both halves start to fall ---------
        k_arrow = make_k_arrow(GV_A[0] - 0.9, -config.frame_y_radius + 0.45)
        absorb(self, GV_A[0], atom,
               extras=[self.pulse_caption(r"\pi/2", GV_A[0]), k_arrow],
               fade=[k_arrow, trap])
        lower = make_atom(opacity=SUPERPOSITION_OPACITY).move_to(GV_A)
        upper = make_atom(KICKED_COLOR, opacity=SUPERPOSITION_OPACITY).move_to(GV_A)
        recoil = momentum_arrow(GV_A, UP, r"\hbar k")
        self.remove(atom)
        self.add(lower, upper)
        self.play(*grow(recoil), run_time=0.6)
        draw_wavy_legs(self, [
            (lower, GV_A, GV_B, ATOM_COLOR, fall),
            (upper, GV_A, GV_B_UP, KICKED_COLOR, fall),
        ], fade=[recoil])
        self.beat()

        # --- 4. pi pulse: the mirror, on two arms that have both fallen --
        gain = momentum_arrow(GV_B, UP, r"+\hbar k")
        lose = momentum_arrow(GV_B_UP, DOWN, r"-\hbar k", label_dir=RIGHT)
        absorb(self, GV_B[0], lower, extras=[self.pulse_caption(r"\pi", GV_B[0])])
        self.play(state_colors(lower, KICKED_COLOR), *grow(gain), run_time=0.6)
        emit(self, GV_B_UP[0], upper)
        self.play(state_colors(upper, ATOM_COLOR), *grow(lose), run_time=0.6)
        draw_wavy_legs(self, [
            (lower, GV_B, GV_C, KICKED_COLOR, fall),
            (upper, GV_B_UP, GV_C, ATOM_COLOR, fall),
        ], fade=[gain, lose])
        self.beat()

        # --- 5. second pi/2: recombine, ports, readout -------------------
        absorb(self, GV_C[0], lower, extras=[self.pulse_caption(r"\pi/2", GV_C[0])])
        port_g = make_atom(opacity=SUPERPOSITION_OPACITY).move_to(GV_C)
        port_e = make_atom(KICKED_COLOR, opacity=SUPERPOSITION_OPACITY).move_to(GV_C)
        self.remove(lower, upper)
        self.add(port_g, port_e)
        draw_wavy_legs(self, [
            (port_g, GV_C, GV_PORT_G, ATOM_COLOR, fall),
            (port_e, GV_C, GV_PORT_E, KICKED_COLOR, fall),
        ])

        loop = curved_loop([GV_A, GV_B, GV_C, GV_B_UP], fall)
        phi = MathTex(r"\Phi", font_size=FONT_PHASE, color=lighten(AREA_COLOR)).move_to(GV_PHI)
        p_g = state_label(r"P_g", ATOM_COLOR).next_to(port_g, RIGHT, buff=0.3)
        p_e = state_label(r"P_e", KICKED_COLOR).next_to(port_e, RIGHT, buff=0.3)
        readout = MathTex(r"P_{g,e} = \tfrac{1}{2}\left(1 \pm \cos\Phi\right)",
                          font_size=FONT_ANNOTATION).to_corner(DR)
        self.add(loop)
        self.bring_to_back(loop)
        self.play(FadeIn(loop), FadeIn(phi), Write(p_g), Write(p_e), Write(readout),
                  run_time=1.3)
        self.beat()

        # --- 6. the falling frame: same loop, unbent, and how far it fell
        ghost = VGroup(*[
            DashedLine(a, b, **FREE_FALL_STYLE)
            for a, b in ((FF_A, FF_B), (FF_B, FF_C), (FF_A, FF_B_UP), (FF_B_UP, FF_C))
        ])
        ghost_label = Tex(r"no gravity", font_size=FONT_LEGEND,
                          color=lighten(GUIDE_COLOR)).next_to(
            (FF_B_UP + FF_C) / 2, UP, buff=0.15)
        drops = VGroup(
            drop_arrow(FF_B[0], FF_B_UP[1], r"\tfrac12 gT^2"),
            drop_arrow(FF_B[0], FF_B[1], r"\tfrac12 gT^2", label_dir=DOWN),
            drop_arrow(FF_C[0], FF_C[1], r"2gT^2"),
        )
        self.play(Create(ghost), FadeIn(ghost_label), run_time=1.2)
        self.play(*[GrowArrow(d[0]) for d in drops], *[FadeIn(d[1]) for d in drops],
                  run_time=1.0)
        self.beat()

        # --- 7. the phase: the laser's k z at each vertex ----------------
        lines = VGroup(
            Tex(r"each pulse writes the\\laser phase $kz$ at the atom",
                font_size=FONT_LEGEND, color=lighten(LASER_COLOR)),
            MathTex(r"d(t) = \tfrac12\,g\,t^2", font_size=FONT_LEGEND,
                    color=lighten(GRAVITY_COLOR)),
            MathTex(r"\Phi = k\,\big[\,d(0) - 2\,d(T) + d(2T)\,\big]",
                    font_size=FONT_ANNOTATION),
            MathTex(r"= k\,\big[\,0 - gT^2 + 2\,gT^2\,\big]", font_size=FONT_ANNOTATION),
        ).arrange(DOWN, buff=0.35)
        lines[3].align_to(lines[2][0][1], LEFT)  # the = under the =
        result = MathTex(r"\Phi = k\,g\,T^2", font_size=FONT_PHASE, color=SIGNAL_COLOR)
        box = SurroundingRectangle(result, buff=0.2, color=lighten(AREA_COLOR),
                                   stroke_width=RING_STROKE_WIDTH)
        boxed = VGroup(result, box).next_to(lines, DOWN, buff=0.45)
        panel = VGroup(lines, boxed).to_edge(RIGHT, buff=GV_PANEL_EDGE)
        panel.shift(UP * (GV_PANEL_TOP - panel.get_top()[1]))
        self.play(FadeIn(lines[0]), run_time=0.8)
        self.play(FadeIn(lines[1]), Write(lines[2]), run_time=1.2)
        self.play(Write(lines[3]), run_time=1.0)
        self.play(Write(result), Create(box), run_time=1.0)
        self.wait(2.0)

    # --- helpers ---------------------------------------------------------
    @staticmethod
    def make_time_axis():
        """Lab time along the bottom: a tick at each pulse, 0, T, 2T."""
        y = GV_AXIS_Y
        axis = VGroup(Arrow([GV_PULSE_X[0] - 0.4, y, 0], [GV_PULSE_X[-1] + 0.9, y, 0],
                            buff=0, max_tip_length_to_length_ratio=0.04, **TIME_AXIS_STYLE))
        for x, tex in zip(GV_PULSE_X, ("0", "T", "2T")):
            axis.add(Line([x, y - GV_TICK, 0], [x, y + GV_TICK, 0], **TIME_AXIS_STYLE))
            axis.add(MathTex(tex, font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR))
                     .move_to([x - 0.35, y - 0.3, 0]))  # clear of the column
        axis.add(MathTex("t", font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR))
                 .next_to(axis[0], RIGHT, buff=0.12))
        return axis
