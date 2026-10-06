"""Ramsey–Bordé atom interferometer (four travelling-wave pi/2 pulses).

Space-time diagram: time to the right, position z along the laser k-vector up.
Pulses 1, 2 come from one direction (+k), pulses 3, 4 from the opposite one
(-k).  Internal state labels the arms (ground blue, excited orange) and the
slope of an arm is its momentum (0, +hk, +2hk, -hk).  Two interferometers
close at pulse 4:
  loop I  -- both arms excited during the dark time T'; ports |e,hk>, |g,2hk>
  loop II -- both arms in the ground state during T'; ports |g,0>, |e,-hk>
Their fringes are shifted by the recoil +-delta (delta = hbar k^2 / 2m):
the recoil doublet.  Branches that do not close (four of them after pulse 3)
are drawn faint and dashed.

Render from /home/user/lmt-plain:
    uv run manim -ql --media_dir p2/media p2/ramsey_borde.py RamseyBorde
"""

import numpy as np
from manim import *

# ---------------------------------------------------------------- style
G_COL = "#4FC3F7"        # ground state |g>
E_COL = "#FFB74D"        # excited state |e>
LASER = "#B39DDB"        # pulse bands
LOOP1 = "#F06292"        # loop I fill
LOOP2 = "#81C784"        # loop II fill
DIM = "#8A8A8A"
TXT = "#E6E6E6"
ARM_W = 4.0
LOST_W = 2.0

# ---------------------------------------------------------------- geometry
T, TP, TX = 1.0, 1.4, 0.8              # T, dark time T', port run-out
T1, T2, T3, T4 = 0.0, T, T + TP, 2 * T + TP
TEND = T4 + TX
X0, SX = -6.2, 2.0                     # screen x of t=0, units per T
Z_MIN, Z_MAX = -1.0, 5.0               # positions in units of (hbar k/m) T
Y0, SY = -2.85, 0.92                   # screen y of z=Z_MIN, units per vT


def P(t, z):
    return np.array([X0 + SX * t, Y0 + SY * (z - Z_MIN), 0.0])


# (t0, z0, momentum in hk, t1, state, kind)
#   kind: "pre" (shared by both loops), "I", "II", "lost", "port"
SEGS = [
    (T1, 0.0, 0, T2, "g", "pre"),
    (T1, 0.0, 1, T2, "e", "pre"),
    # dark zone (pulse 2 -> 3)
    (T2, 0.0, 0, T3, "g", "II"),     # A stays g
    (T2, 0.0, 1, T3, "e", "I"),      # A excited
    (T2, 1.0, 1, T3, "e", "I"),      # B stays e
    (T2, 1.0, 0, T3, "g", "II"),     # B de-excited
    # pulse 3 (-k) -> pulse 4, closing arms
    (T3, T3, 1, T4, "e", "I"),       # B stays e
    (T3, TP, 2, T4, "g", "I"),       # A: e,hk -> g,2hk
    (T3, 0.0, 0, T4, "g", "II"),     # A stays g
    (T3, 1.0, -1, T4, "e", "II"),    # B: g,0 -> e,-hk
    # pulse 3 branches that never close
    (T3, T3, 2, T4, "g", "lost"),
    (T3, TP, 1, T4, "e", "lost"),
    (T3, 1.0, 0, T4, "g", "lost"),
    (T3, 0.0, -1, T4, "e", "lost"),
    # output ports
    (T4, T4, 1, TEND, "e", "port"),
    (T4, T4, 2, TEND, "g", "port"),
    (T4, 0.0, 0, TEND, "g", "port"),
    (T4, 0.0, -1, TEND, "e", "port"),
]


def col(state):
    return G_COL if state == "g" else E_COL


def lines(texts, **kw):
    return VGroup(*[Tex(t, **kw) for t in texts]).arrange(DOWN, aligned_edge=LEFT, buff=0.1)


class RamseyBorde(Scene):
    def construct(self):
        clock = ValueTracker(0.0)
        lost_op = ValueTracker(0.45)

        # ------------------------------------------------ axes
        t_axis = Arrow(P(-0.1, Z_MIN) + DOWN * 0.3, P(TEND + 0.25, Z_MIN) + DOWN * 0.3,
                       buff=0, stroke_width=2, color=DIM, max_tip_length_to_length_ratio=0.03)
        t_lab = MathTex("t", font_size=30, color=DIM).next_to(t_axis.get_end(), RIGHT, buff=0.08)
        z_axis = Arrow(P(-0.12, Z_MIN) + DOWN * 0.3, P(-0.12, Z_MAX + 0.35),
                       buff=0, stroke_width=2, color=DIM, max_tip_length_to_length_ratio=0.04)
        z_lab = MathTex(r"z \parallel \vec k", font_size=28, color=DIM).rotate(PI / 2)
        z_lab.next_to(z_axis, LEFT, buff=0.08).shift(UP * 1.2)
        ticks = VGroup()
        for t, s in [(T1, "0"), (T2, "T"), (T3, "T+T'"), (T4, "2T+T'")]:
            base = P(t, Z_MIN) + DOWN * 0.3
            tk = Line(base + UP * 0.07, base + DOWN * 0.07, stroke_width=2, color=DIM)
            lb = MathTex(s, font_size=26, color=DIM).next_to(tk, DOWN, buff=0.08)
            ticks.add(tk, lb)

        # ------------------------------------------------ right panel
        PX = 3.55
        title = lines([r"Ramsey--Bord\'e", r"interferometer"], font_size=40, color=TXT)
        title.to_corner(UR, buff=0.35).align_to(np.array([PX, 0, 0]), LEFT)
        sub = lines([r"four $\pi/2$ pulses:", r"two along $+\vec k$, two along $-\vec k$"],
                    font_size=24, color=DIM)
        sub.next_to(title, DOWN, buff=0.18, aligned_edge=LEFT)

        def key(color, text, dashed=False):
            ln = (DashedLine if dashed else Line)(ORIGIN, RIGHT * 0.45, stroke_width=4 if not dashed else 2,
                                                   color=color)
            if dashed:
                ln.set_stroke(opacity=0.6)
            tx = Tex(text, font_size=24, color=TXT).next_to(ln, RIGHT, buff=0.15)
            return VGroup(ln, tx)

        legend = VGroup(
            key(G_COL, r"ground state $|g\rangle$"),
            key(E_COL, r"excited state $|e\rangle$"),
            key(DIM, r"branch that never closes", dashed=True),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        slope = lines([r"slope = momentum", r"($0,\ \pm\hbar k,\ 2\hbar k$)"], font_size=22, color=DIM)
        legend.add(slope)
        slope.next_to(legend[2], DOWN, buff=0.14, aligned_edge=LEFT)
        legend.next_to(sub, DOWN, buff=0.35, aligned_edge=LEFT)

        # ------------------------------------------------ arms (grow with the clock)
        def seg_mob(seg):
            t0, z0, p, t1, st, kind = seg

            def build():
                t = clock.get_value()
                tc = min(t, t1)
                if tc <= t0 + 1e-4:
                    return VMobject()
                a, b = P(t0, z0), P(tc, z0 + p * (tc - t0))
                if kind == "lost":
                    if np.linalg.norm(b - a) < 0.12:
                        return Line(a, b, stroke_width=LOST_W, color=col(st)).set_stroke(
                            opacity=lost_op.get_value())
                    return DashedLine(a, b, dash_length=0.09, stroke_width=LOST_W,
                                      color=col(st)).set_stroke(opacity=lost_op.get_value())
                return Line(a, b, stroke_width=ARM_W, color=col(st))

            return always_redraw(build)

        def seg_dot(seg):
            t0, z0, p, t1, st, kind = seg

            def build():
                t = clock.get_value()
                if not (t0 < t <= t1 + 1e-6) and not (kind == "port" and t >= t1 - 1e-6):
                    return VMobject()
                tc = min(t, t1)
                d = Dot(P(tc, z0 + p * (tc - t0)), radius=0.085 if kind != "lost" else 0.06,
                        color=col(st))
                if kind == "lost":
                    d.set_opacity(0.45)
                return d

            return always_redraw(build)

        arms = {k: VGroup() for k in ("pre", "I", "II", "lost", "port")}
        dots = VGroup()
        for s in SEGS:
            arms[s[5]].add(seg_mob(s))
            dots.add(seg_dot(s))
        start_dot = always_redraw(
            lambda: Dot(P(0, 0), radius=0.085, color=G_COL) if clock.get_value() <= 1e-4 else VMobject())

        # ------------------------------------------------ pulses
        def pulse(t, sign):
            band = Rectangle(width=0.2, height=P(0, Z_MAX + 0.2)[1] - P(0, Z_MIN - 0.15)[1],
                             stroke_width=0, fill_color=LASER, fill_opacity=0.0).set_z_index(-1)
            band.move_to((P(t, Z_MAX + 0.2) + P(t, Z_MIN - 0.15)) / 2)
            top = P(t, Z_MAX + 0.2)
            ar = Arrow(top + UP * (0.12 if sign > 0 else 0.62), top + UP * (0.62 if sign > 0 else 0.12),
                       buff=0, stroke_width=4, color=LASER, max_tip_length_to_length_ratio=0.45)
            kl = MathTex(r"+\vec k" if sign > 0 else r"-\vec k", font_size=26, color=LASER)
            kl.next_to(ar, RIGHT, buff=0.06)
            pl = MathTex(r"\tfrac{\pi}{2}", font_size=26, color=LASER).next_to(ar, LEFT, buff=0.06)
            return band, VGroup(ar, kl, pl)

        def fire(band, lab, run_time=0.9):
            return Succession(
                AnimationGroup(band.animate(run_time=0.35).set_fill(opacity=0.75), FadeIn(lab, run_time=0.35)),
                band.animate(run_time=run_time - 0.35).set_fill(opacity=0.2),
            )

        pulses = [pulse(T1, +1), pulse(T2, +1), pulse(T3, -1), pulse(T4, -1)]

        def advance(to, rt):
            return clock.animate(run_time=rt, rate_func=linear).set_value(to)

        # ------------------------------------------------ build up
        self.add(*[b for b, _ in pulses])
        self.add(arms["lost"], arms["pre"], arms["I"], arms["II"], arms["port"], dots, start_dot)
        init = MathTex(r"|g,0\rangle", font_size=28, color=G_COL).next_to(P(0, 0), DOWN, buff=0.15)
        init.shift(RIGHT * 0.25)
        self.play(FadeIn(t_axis, t_lab, z_axis, z_lab, ticks), Write(title), run_time=1.2)
        self.play(FadeIn(sub), FadeIn(init), run_time=0.8)
        self.play(FadeIn(legend), run_time=0.8)
        self.wait(0.4)

        # pulse 1: beam splitter, g,0 -> g,0 + e,hk
        self.play(fire(*pulses[0]))
        self.play(advance(0.5, 1.0))
        lab_g = MathTex(r"|g,0\rangle", font_size=26, color=G_COL).next_to(P(0.5, 0), DOWN, buff=0.15)
        lab_e = MathTex(r"|e,\hbar k\rangle", font_size=26, color=E_COL)
        lab_e.next_to(P(0.5, 0.5), UL, buff=0.08)
        self.play(FadeIn(lab_g), FadeIn(lab_e), FadeOut(init), run_time=0.5)
        self.play(advance(T2, 1.0))

        # pulse 2: each arm splits again -> two parallel pairs
        self.play(fire(*pulses[1]))
        self.play(advance(T3, 2.6))
        self.wait(0.3)

        # pulse 3 (-k): closes each pair; other halves leave
        self.play(fire(*pulses[2]))
        self.play(advance(T4, 2.0))
        self.wait(0.3)

        # pulse 4 (-k): recombination, four ports
        self.play(fire(*pulses[3]))
        self.play(advance(TEND, 1.4))
        port_labels = VGroup()
        for (z, tex, st) in [(T4 + 2 * TX, r"|g,2\hbar k\rangle", "g"),
                             (T4 + TX, r"|e,\hbar k\rangle", "e"),
                             (0.0, r"|g,0\rangle", "g"),
                             (-TX, r"|e,-\hbar k\rangle", "e")]:
            port_labels.add(MathTex(tex, font_size=28, color=col(st)).next_to(P(TEND, z), RIGHT, buff=0.15))
        self.play(LaggedStart(*[FadeIn(l, shift=RIGHT * 0.1) for l in port_labels], lag_ratio=0.2),
                  run_time=1.2)
        self.wait(0.5)

        # ------------------------------------------------ the two closed loops
        loop1_pts = [P(0, 0), P(T4, T4), P(T3, TP), P(T2, 0)]
        loop2_pts = [P(0, 0), P(T2, 1.0), P(T3, 1.0), P(T4, 0)]
        fill1 = Polygon(*loop1_pts, stroke_width=0, fill_color=LOOP1, fill_opacity=0.22)
        fill2 = Polygon(*loop2_pts, stroke_width=0, fill_color=LOOP2, fill_opacity=0.22)
        edge1 = Polygon(*loop1_pts, stroke_width=7, color=LOOP1, fill_opacity=0)
        edge2 = Polygon(*loop2_pts, stroke_width=7, color=LOOP2, fill_opacity=0)
        tag1 = Tex("I", font_size=34, color=LOOP1).move_to(P(2.05, 1.62))
        tag2 = Tex("II", font_size=30, color=LOOP2).move_to(P(2.95, 0.24))

        box1 = SurroundingRectangle(port_labels[0:2], buff=0.07, corner_radius=0.08,
                                    color=LOOP1, stroke_width=2)
        box2 = SurroundingRectangle(port_labels[2:4], buff=0.07, corner_radius=0.08,
                                    color=LOOP2, stroke_width=2)
        card1 = VGroup(
            Tex(r"\textbf{Loop I}: $|e\rangle$ during $T'$", font_size=26, color=LOOP1),
            Tex(r"ports $|e,\hbar k\rangle,\ |g,2\hbar k\rangle$", font_size=24, color=TXT),
            MathTex(r"\Delta\phi_{\rm I} = 2T\,(\omega-\omega_0+\delta)", font_size=28, color=TXT),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        card2 = VGroup(
            Tex(r"\textbf{Loop II}: $|g\rangle$ during $T'$", font_size=26, color=LOOP2),
            Tex(r"ports $|g,0\rangle,\ |e,-\hbar k\rangle$", font_size=24, color=TXT),
            MathTex(r"\Delta\phi_{\rm II} = 2T\,(\omega-\omega_0-\delta)", font_size=28, color=TXT),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        card1.next_to(legend, DOWN, buff=0.35, aligned_edge=LEFT)
        card2.next_to(card1, DOWN, buff=0.3, aligned_edge=LEFT)
        doublet = lines([r"$\delta=\hbar k^2/2m$: fringes at $\omega_0\mp\delta$",
                         r"(the recoil doublet)"], font_size=24, color=DIM)
        doublet.next_to(card2, DOWN, buff=0.3, aligned_edge=LEFT)

        self.play(FadeOut(lab_g), FadeOut(lab_e), lost_op.animate.set_value(0.18), run_time=0.6)
        self.play(Create(edge1), run_time=1.4)
        self.play(FadeIn(fill1), FadeOut(edge1), FadeIn(tag1), FadeIn(card1, shift=LEFT * 0.1),
                  Create(box1), run_time=1.0)
        self.wait(0.5)
        self.play(Create(edge2), run_time=1.4)
        self.play(FadeIn(fill2), FadeOut(edge2), FadeIn(tag2), FadeIn(card2, shift=LEFT * 0.1),
                  Create(box2), run_time=1.0)
        self.wait(0.4)
        self.play(FadeIn(doublet), run_time=0.8)
        self.wait(2.0)
