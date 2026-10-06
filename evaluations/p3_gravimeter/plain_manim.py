"""Atom gravimeter: a light-pulse Mach-Zehnder interferometer in free fall.

Left: the vertical apparatus (vacuum tube, Raman beam with k_eff pointing
down along g, the atom clouds falling).  Middle: the same motion as a
height-time diagram, where free fall bends every arm into a parabola.
Right: the phase.  Each pulse prints the laser phase k_eff . r at the
atoms; the interferometer phase is the second difference
phi1 - 2 phi2 + phi3 of the arm-midpoint trajectory, which kills every
term linear in t (launch velocity, photon recoil) and leaves only the
curvature: Delta phi = k_eff g T^2.

Units are illustrative (T = 1, g = 2, v_rec = 1): the recoil is hugely
exaggerated relative to g T so the two arms are visibly separated.

Render:
    cd /home/user/lmt-plain && uv run manim -ql --media_dir p3/media \
        p3/gravimeter.py AtomGravimeter
"""

import numpy as np
from manim import *

# ---------------------------------------------------------------- physics
T = 1.0      # pulse separation
G = 2.0      # gravity (downward)
VR = 1.0     # two-photon recoil velocity hbar k_eff / m (downward: k_eff along g)
TAU = 0.25   # how far the output ports are drawn past 2T


def z_a(t):
    """Arm A: unkicked by the first pulse, kicked by the mirror pulse."""
    return -0.5 * G * t**2 - VR * max(t - T, 0.0)


def z_b(t):
    """Arm B: kicked by the first pulse, kick removed by the mirror pulse.
    Also the unkicked output port after 2T."""
    return -VR * min(t, T) - 0.5 * G * t**2


def z_port2(t):
    """Kicked output port after the final beam splitter."""
    return z_b(t) - VR * max(t - 2 * T, 0.0)


def z_mid(t):
    return 0.5 * (z_a(t) + z_b(t))


# ---------------------------------------------------------------- style
C1 = BLUE_C          # |1, p>
C2 = ORANGE          # |2, p + hbar k_eff>
LASER = RED_D
DIM = GREY_B
AXIS = GREY_A

# ---------------------------------------------------------------- layout
X0 = -4.7            # screen x of t = 0
SX = 5.2 / 2.4       # screen units per unit time
SZ = 5.6 / 7.2       # screen units per unit height
Z_TOP, Z_BOT = 0.6, -6.6
Y0 = 2.75 - Z_TOP * SZ   # screen y of z = 0
TUBE_X = -6.15
BRACE_X = 0.75


def c2p(t, z):
    return np.array([X0 + t * SX, Y0 + z * SZ, 0.0])


def zy(z):
    return Y0 + z * SZ


def arm(f, t0, t1, color, tmax):
    """The piece of arm f on [t0, min(t1, tmax)] (empty before t0)."""
    hi = min(t1, tmax)
    if hi <= t0 + 1e-4:
        return VMobject()
    ts = np.linspace(t0, hi, 60)
    m = VMobject(stroke_color=color, stroke_width=5)
    m.set_points_smoothly([c2p(t, f(t)) for t in ts])
    return m


def cloud(point, color):
    g = VGroup(
        Dot(point, radius=0.20, color=color, fill_opacity=0.18),
        Dot(point, radius=0.13, color=color, fill_opacity=0.35),
        Dot(point, radius=0.075, color=color, fill_opacity=1.0),
    )
    return g


class AtomGravimeter(Scene):
    def construct(self):
        t = ValueTracker(-0.0001)

        title = Tex(r"Atom gravimeter: a Mach--Zehnder in free fall", font_size=38)
        title.to_edge(UP, buff=0.25)

        # ---------- apparatus: vacuum tube + downward Raman beam
        tube_top, tube_bot = zy(Z_TOP) + 0.1, zy(Z_BOT) - 0.1
        tube = Rectangle(width=0.62, height=tube_top - tube_bot,
                         stroke_color=GREY_B, stroke_width=2)
        tube.move_to([TUBE_X, 0.5 * (tube_top + tube_bot), 0])
        beam = Rectangle(width=0.34, height=tube_top - tube_bot,
                         stroke_width=0, fill_color=LASER, fill_opacity=0.12)
        beam.move_to(tube)
        k_arrow = Arrow([TUBE_X, 3.75, 0], [TUBE_X, tube_top + 0.02, 0], buff=0,
                        color=LASER, stroke_width=5,
                        max_tip_length_to_length_ratio=0.35)
        k_lab = MathTex(r"\vec k_{\rm eff}", color=LASER, font_size=34)
        k_lab.next_to(k_arrow, RIGHT, buff=0.12).shift(0.05 * UP)
        g_arrow = Arrow([-5.42, -1.55, 0], [-5.42, -2.6, 0], buff=0,
                        color=WHITE, stroke_width=5,
                        max_tip_length_to_length_ratio=0.3)
        g_lab = MathTex(r"\vec g", font_size=36).next_to(g_arrow, RIGHT, buff=0.08)
        apparatus = VGroup(beam, tube, k_arrow, k_lab, g_arrow, g_lab)

        # ---------- height-time axes
        z_axis = Arrow(c2p(0, Z_BOT) + 0.2 * DOWN + 0.25 * LEFT,
                       c2p(0, Z_TOP) + 0.25 * UP + 0.25 * LEFT,
                       buff=0, color=AXIS, stroke_width=3,
                       max_tip_length_to_length_ratio=0.04)
        t_axis = Arrow(c2p(0, Z_BOT) + 0.2 * DOWN + 0.25 * LEFT, c2p(2.42, Z_BOT) + 0.2 * DOWN,
                       buff=0, color=AXIS, stroke_width=3,
                       max_tip_length_to_length_ratio=0.05)
        z_lab = MathTex("z", font_size=34, color=AXIS).next_to(z_axis.get_end(), LEFT, buff=0.12)
        t_lab = MathTex("t", font_size=34, color=AXIS).next_to(t_axis.get_end(), RIGHT, buff=0.1)
        ticks = VGroup()
        for tt, s in [(0, "0"), (T, "T"), (2 * T, "2T")]:
            p = c2p(tt, Z_BOT) + 0.2 * DOWN
            ticks.add(Line(p + 0.08 * UP, p + 0.08 * DOWN, color=AXIS, stroke_width=3))
            ticks.add(MathTex(s, font_size=30, color=AXIS).next_to(p, DOWN, buff=0.14))
        axes = VGroup(z_axis, t_axis, z_lab, t_lab, ticks)

        # ---------- legend (top of right panel)
        leg1 = VGroup(Dot(color=C1, radius=0.09),
                      MathTex(r"|1,\,\vec p\,\rangle", font_size=32))
        leg2 = VGroup(Dot(color=C2, radius=0.09),
                      MathTex(r"|2,\,\vec p+\hbar\vec k_{\rm eff}\rangle", font_size=32))
        for lg in (leg1, leg2):
            lg.arrange(RIGHT, buff=0.15)
        legend = VGroup(leg1, leg2).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        legend.move_to([4.4, 2.75, 0]).align_to([2.1, 0, 0], LEFT)

        self.play(Write(title), run_time=1.2)
        self.play(FadeIn(apparatus), Create(axes), FadeIn(legend), run_time=1.5)

        # ---------- live trajectories and clouds
        def arms():
            tm = t.get_value()
            return VGroup(
                arm(z_a, 0, T, C1, tm), arm(z_b, 0, T, C2, tm),
                arm(z_a, T, 2 * T, C2, tm), arm(z_b, T, 2 * T, C1, tm),
                arm(z_b, 2 * T, 2 * T + TAU, C1, tm),
                arm(z_port2, 2 * T, 2 * T + TAU, C2, tm),
            )

        def clouds():
            tm = t.get_value()
            if tm <= 0:
                return VGroup(cloud([TUBE_X, zy(0), 0], C1))
            if tm < 2 * T:
                ca = C1 if tm < T else C2
                cb = C2 if tm < T else C1
                return VGroup(cloud([TUBE_X, zy(z_a(tm)), 0], ca),
                              cloud([TUBE_X, zy(z_b(tm)), 0], cb))
            return VGroup(cloud([TUBE_X, zy(z_b(tm)), 0], C1),
                          cloud([TUBE_X, zy(z_port2(tm)), 0], C2))

        def heads():
            tm = t.get_value()
            if tm <= 0:
                return VGroup(Dot(c2p(0, 0), radius=0.08, color=C1))
            if tm < 2 * T:
                ca = C1 if tm < T else C2
                cb = C2 if tm < T else C1
                return VGroup(Dot(c2p(tm, z_a(tm)), radius=0.08, color=ca),
                              Dot(c2p(tm, z_b(tm)), radius=0.08, color=cb))
            return VGroup(Dot(c2p(tm, z_b(tm)), radius=0.08, color=C1),
                          Dot(c2p(tm, z_port2(tm)), radius=0.08, color=C2))

        arm_mob = always_redraw(arms)
        cloud_mob = always_redraw(clouds)
        head_mob = always_redraw(heads)
        release = Tex("cold cloud, released", font_size=26, color=DIM)
        release.next_to(c2p(0, 0), RIGHT, buff=0.3).shift(0.05 * UP)
        self.add(arm_mob)
        self.play(FadeIn(cloud_mob), FadeIn(head_mob), FadeIn(release))
        self.wait(0.5)

        # ---------- pulses
        def pulse_band(tt):
            top, bot = c2p(tt, Z_TOP), c2p(tt, Z_BOT)
            return Rectangle(width=0.1, height=top[1] - bot[1], stroke_width=0,
                             fill_color=LASER, fill_opacity=0.45,
                             z_index=-2).move_to(0.5 * (top + bot))

        def fire(tt, name):
            band = pulse_band(tt)
            lab = MathTex(name, font_size=32, color=LASER)
            lab.next_to(band, UP, buff=0.08)
            flash = beam.copy().set_fill(LASER, opacity=0.6).set_z_index(-1)
            self.play(FadeIn(band, scale=1.0), FadeIn(lab, shift=0.1 * DOWN),
                      FadeIn(flash), run_time=0.45)
            self.play(FadeOut(flash), band.animate.set_fill(opacity=0.28), run_time=0.35)
            return band, lab

        fire(0, r"\tfrac{\pi}{2}")
        self.play(FadeOut(release), run_time=0.3)
        self.play(t.animate.set_value(0.38 * T), run_time=1.3, rate_func=linear)
        kick = MathTex(r"+\hbar\vec k_{\rm eff}", font_size=28, color=C2)
        kick.next_to(c2p(0.3, z_b(0.3)), DOWN, buff=0.12).shift(0.15 * LEFT)
        self.play(t.animate.set_value(T), FadeIn(kick, run_time=0.6),
                  run_time=2.2, rate_func=linear)

        fire(T, r"\pi")
        self.play(t.animate.set_value(2 * T), run_time=3.2, rate_func=linear)

        fire(2 * T, r"\tfrac{\pi}{2}")
        self.play(t.animate.set_value(2 * T + TAU), run_time=1.0, rate_func=linear)
        p1 = MathTex(r"|1\rangle", font_size=28, color=C1)
        p2 = MathTex(r"|2\rangle", font_size=28, color=C2)
        p1.next_to(c2p(2 * T + TAU, z_b(2 * T + TAU)), RIGHT, buff=0.12).shift(0.12 * UP)
        p2.next_to(c2p(2 * T + TAU, z_port2(2 * T + TAU)), RIGHT, buff=0.12).shift(0.08 * DOWN)
        self.play(FadeIn(p1), FadeIn(p2), run_time=0.6)
        self.wait(0.8)

        # ---------- freeze the drawing
        frozen = VGroup(arms(), heads())
        self.remove(arm_mob, head_mob)
        self.add(frozen)
        cloud_mob.clear_updaters()

        # ---------- midpoints, phase fronts, fall distances
        mids = VGroup(*[Dot(c2p(tt, z_mid(tt)), radius=0.07, color=WHITE)
                        for tt in (0, T, 2 * T)])
        mid_tick = Line(c2p(T, z_a(T)), c2p(T, z_b(T)), color=WHITE, stroke_width=2)
        rails = VGroup(*[DashedLine(c2p(tt, z_mid(tt)), [BRACE_X, zy(z_mid(tt)), 0],
                                    color=GREY_C, stroke_width=1.8, dash_length=0.08)
                         for tt in (0, T, 2 * T)])
        b1 = BraceBetweenPoints([BRACE_X, zy(z_mid(0)), 0], [BRACE_X, zy(z_mid(T)), 0],
                                direction=RIGHT, buff=0.02, color=WHITE)
        b2 = BraceBetweenPoints([BRACE_X, zy(z_mid(T)), 0], [BRACE_X, zy(z_mid(2 * T)), 0],
                                direction=RIGHT, buff=0.02, color=WHITE)
        l1 = MathTex(r"\Delta z_1", font_size=32).next_to(b1, RIGHT, buff=0.08)
        l2 = MathTex(r"\Delta z_2", font_size=32).next_to(b2, RIGHT, buff=0.08)
        self.play(FadeOut(kick),
                  Create(mid_tick), FadeIn(mids, scale=1.5), run_time=0.8)
        self.play(Create(rails), run_time=0.9)
        self.play(GrowFromCenter(b1), FadeIn(l1), run_time=0.7)
        self.play(GrowFromCenter(b2), FadeIn(l2), run_time=0.7)
        self.wait(0.4)

        # ---------- the phase
        fs = 34
        e1 = MathTex(r"\phi_i = \vec k_{\rm eff}\cdot\bar{\vec r}(t_i)", font_size=fs)
        n1 = Tex(r"laser phase printed at pulse $i$,\\at the arms' midpoint $\bar{\vec r}$", font_size=24, color=DIM)
        e2 = MathTex(r"\Delta\phi", r"=\phi_1-2\phi_2+\phi_3", font_size=fs)
        e3 = MathTex(r"=k_{\rm eff}\,(\Delta z_2-\Delta z_1)", font_size=fs)
        e4 = MathTex(r"\Delta z_1=\tfrac12 v_{\rm r}T+\tfrac12 gT^2", font_size=30)
        e5 = MathTex(r"\Delta z_2=\tfrac12 v_{\rm r}T+\tfrac32 gT^2", font_size=30)
        e6 = MathTex(r"\Delta\phi = k_{\rm eff}\, g\, T^2", font_size=46)
        box = SurroundingRectangle(e6, color=YELLOW, buff=0.18, corner_radius=0.08)
        n2 = Tex(r"recoil and launch velocity cancel:\\only the curvature $g$ survives",
                 font_size=24, color=DIM)

        col = VGroup(e1, n1, e2, e3, e4, e5, VGroup(e6, box), n2)
        col.arrange(DOWN, aligned_edge=LEFT, buff=0.24)
        n1.shift(0.12 * UP)
        e3.align_to(e2[1], LEFT)
        VGroup(e6, box).shift(0.15 * DOWN)
        n2.shift(0.1 * DOWN)
        col.next_to(legend, DOWN, buff=0.45).align_to(legend, LEFT)

        self.play(Write(e1), FadeIn(n1), run_time=1.2)
        self.wait(0.5)
        self.play(Write(e2), run_time=1.0)
        self.play(Write(e3), Indicate(VGroup(l1, l2), color=YELLOW), run_time=1.2)
        self.wait(0.4)
        self.play(FadeIn(e4, shift=0.1 * DOWN), Indicate(l1, color=YELLOW), run_time=0.9)
        self.play(FadeIn(e5, shift=0.1 * DOWN), Indicate(l2, color=YELLOW), run_time=0.9)
        self.wait(0.6)
        self.play(Write(e6), run_time=1.2)
        self.play(Create(box), FadeIn(n2), run_time=0.9)
        self.wait(2.5)
