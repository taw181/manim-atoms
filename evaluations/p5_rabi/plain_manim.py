"""Rabi oscillations on the 87Sr clock transition 1S0 -> 3P0 (698 nm).

Left: Bloch sphere (|e> = 3P0 at the north pole, |g> = 1S0 at the south pole)
with the Bloch vector precessing about the drive vector (Omega, 0, Delta).
Right: excited-state population P_e(t) = (1 + w)/2 traced in step with it.

First on resonance (Delta = 0): full-contrast oscillation, P_e = sin^2(Omega t / 2),
with the pi/2 and pi pulses marked.  Then detuned (Delta = Omega): the drive axis
tilts, the vector circles a cone that never reaches |e>, and the population
oscillates faster (Omega' = sqrt(2) Omega) with amplitude Omega^2/Omega'^2 = 1/2.

Render from /home/user/lmt-plain:
    uv run manim -ql --media_dir p5/media p5/rabi_bloch.py RabiBloch
"""
from manim import *
import numpy as np

# ---------------------------------------------------------------- style
C_SPHERE = "#6f86a8"
C_VEC = "#ffd166"
C_RES = "#4cc9f0"      # resonant trace
C_DET = "#f4a261"      # detuned trace
C_DRIVE = "#ef476f"    # 698 nm clock laser / drive vector
C_TEXT = "#e8e8e8"
C_DIM = "#8a8a8a"

# ---------------------------------------------------------------- Bloch-sphere projection
AZ, EL = np.radians(28), np.radians(17)
CEN = np.array([-4.15, -0.45, 0.0])
RAD = 2.0
SCR_R = np.array([-np.sin(AZ), np.cos(AZ), 0.0])
SCR_U = np.array([-np.sin(EL) * np.cos(AZ), -np.sin(EL) * np.sin(AZ), np.cos(EL)])
VIEW = np.array([np.cos(EL) * np.cos(AZ), np.cos(EL) * np.sin(AZ), np.sin(EL)])


def P(v):
    """Orthographic projection of a Bloch-space point onto the screen."""
    v = np.asarray(v, dtype=float)
    return CEN + RAD * (np.dot(v, SCR_R) * RIGHT + np.dot(v, SCR_U) * UP)


def depth(v):
    return float(np.dot(np.asarray(v, dtype=float), VIEW))


def split_by_depth(pts3, front_kw, back_kw):
    """Polyline through 3D points, solid in front of the sphere and faint behind."""
    group = VGroup()
    if len(pts3) < 2:
        return group
    front = [depth(p) >= 0 for p in pts3]
    run = [pts3[0]]
    for i in range(1, len(pts3)):
        run.append(pts3[i])
        if front[i] != front[i - 1] or i == len(pts3) - 1:
            if len(run) >= 2:
                m = VMobject().set_points_as_corners([P(p) for p in run])
                m.set_stroke(**(front_kw if front[i - 1] else back_kw))
                group.add(m)
            run = [pts3[i]]
    return group


def drive_axis(d):
    """Unit rotation axis for drive (Omega, 0, Delta), Delta = d * Omega."""
    n = np.array([1.0, 0.0, d])
    return n / np.linalg.norm(n)


def bloch(theta, d):
    """Bloch vector after Omega*t = theta, starting in |g> = (0, 0, -1).

    Rodrigues rotation about n by the generalised Rabi angle sqrt(1 + d^2) * theta.
    dr/dt = Omega_vec x r.
    """
    n = drive_axis(d)
    r0 = np.array([0.0, 0.0, -1.0])
    a = np.sqrt(1 + d * d) * theta
    return r0 * np.cos(a) + np.cross(n, r0) * np.sin(a) + n * np.dot(n, r0) * (1 - np.cos(a))


def p_exc(theta, d):
    """P_e = Omega^2/Omega'^2 sin^2(Omega' t / 2)."""
    return np.sin(np.sqrt(1 + d * d) * theta / 2) ** 2 / (1 + d * d)


class RabiBloch(Scene):
    def construct(self):
        th = ValueTracker(0.0)   # Omega * t
        dt = ValueTracker(0.0)   # Delta / Omega
        state = {"color": C_RES}

        # ------------------------------------------------------------ title
        title = Text("Rabi oscillations on the strontium clock transition",
                     font_size=34, color=C_TEXT)
        sub = MathTex(r"^{87}\mathrm{Sr}:\ {}^1S_0 \;\leftrightarrow\; {}^3P_0"
                      r"\quad \lambda = 698\,\mathrm{nm}", font_size=32, color=C_DIM)
        head = VGroup(title, sub).arrange(DOWN, buff=0.15).to_edge(UP, buff=0.25)

        # ------------------------------------------------------------ Bloch sphere
        ring = np.linspace(0, TAU, 241)
        outline = Circle(radius=RAD, color=C_SPHERE, stroke_width=2.5).move_to(CEN)
        outline.set_fill(C_SPHERE, opacity=0.07)
        front_kw = dict(color=C_SPHERE, width=1.6, opacity=0.9)
        back_kw = dict(color=C_SPHERE, width=1.2, opacity=0.3)
        equator = split_by_depth([(np.cos(a), np.sin(a), 0) for a in ring], front_kw, back_kw)
        meridian = split_by_depth([(np.cos(a), 0, np.sin(a)) for a in ring], front_kw, back_kw)
        axes3 = VGroup(
            DashedLine(P((-1, 0, 0)), P((1, 0, 0)), stroke_width=1.5, color=C_DIM, dash_length=0.06),
            DashedLine(P((0, -1, 0)), P((0, 1.25, 0)), stroke_width=1.5, color=C_DIM, dash_length=0.06),
            DashedLine(P((0, 0, -1)), P((0, 0, 1)), stroke_width=1.5, color=C_DIM, dash_length=0.06),
        )
        ax_lab = VGroup(
            MathTex("x", font_size=28, color=C_DIM).move_to(P((1.0, 0, 0)) + 0.32 * DOWN + 0.12 * RIGHT),
            MathTex("y", font_size=28, color=C_DIM).next_to(P((0, 1.25, 0)), RIGHT, buff=0.08),
        )
        e_lab = MathTex(r"|e\rangle = {}^3P_0", font_size=32, color=C_TEXT).next_to(P((0, 0, 1)), UP, buff=0.12)
        g_lab = MathTex(r"|g\rangle = {}^1S_0", font_size=32, color=C_TEXT).next_to(P((0, 0, -1)), DOWN, buff=0.12)
        poles = VGroup(Dot(P((0, 0, 1)), radius=0.045, color=C_TEXT), Dot(P((0, 0, -1)), radius=0.045, color=C_TEXT))
        sphere = VGroup(outline, equator, meridian, axes3, ax_lab, poles, e_lab, g_lab)

        # drive vector (Omega, 0, Delta): rotation axis of the Bloch vector
        def drive_arrow():
            n = drive_axis(dt.get_value())
            return Arrow(P((0, 0, 0)), P(1.3 * n), buff=0, color=C_DRIVE, stroke_width=5,
                         max_tip_length_to_length_ratio=0.18)
        drive = always_redraw(drive_arrow)
        drive_lab = always_redraw(
            lambda: MathTex(r"\vec\Omega", font_size=34, color=C_DRIVE)
            .next_to(P(1.3 * drive_axis(dt.get_value())), LEFT, buff=0.08))

        # Bloch-vector trail on the sphere
        def trail():
            t = th.get_value()
            if t < 1e-3:
                return VGroup()
            n = max(2, int(120 * t / PI))
            pts = [bloch(s, dt.get_value()) for s in np.linspace(0, t, n)]
            c = state["color"]
            return split_by_depth(pts, dict(color=c, width=3.5, opacity=1.0),
                                  dict(color=c, width=2.5, opacity=0.55))
        trail_m = always_redraw(trail)

        # Bloch vector itself and its projection onto the z axis (w = 2 P_e - 1)
        def vec():
            r = bloch(th.get_value(), dt.get_value())
            return Arrow(P((0, 0, 0)), P(r), buff=0, color=C_VEC, stroke_width=6,
                         max_tip_length_to_length_ratio=0.2, max_stroke_width_to_length_ratio=12)
        vec_m = always_redraw(vec)

        def zproj():
            r = bloch(th.get_value(), dt.get_value())
            a, b = P(r), P((0, 0, r[2]))
            g = VGroup(Dot(b, radius=0.06, color=C_VEC))
            if np.linalg.norm(a - b) > 0.12:
                g.add(DashedLine(a, b, stroke_width=1.8, color=C_VEC, dash_length=0.06))
            return g
        zproj_m = always_redraw(zproj)

        # ------------------------------------------------------------ population plot
        ax = Axes(x_range=[0, 4 * PI, PI], y_range=[0, 1, 0.5], x_length=6.4, y_length=3.0,
                  tips=False, axis_config={"color": GREY_B, "stroke_width": 2})
        ax.move_to([2.95, 0.55, 0])
        xt = VGroup(*[MathTex(s, font_size=28, color=C_TEXT).next_to(ax.c2p(k * PI, 0), DOWN, buff=0.15)
                      for k, s in [(1, r"\pi"), (2, r"2\pi"), (3, r"3\pi"), (4, r"4\pi")]])
        yt = VGroup(*[MathTex(s, font_size=28, color=C_TEXT).next_to(ax.c2p(0, v), LEFT, buff=0.15)
                      for v, s in [(0, "0"), (0.5, "0.5"), (1, "1")]])
        grid = VGroup(*[DashedLine(ax.c2p(0, v), ax.c2p(4 * PI, v), stroke_width=1, color=GREY_D,
                                   dash_length=0.05) for v in (0.5, 1.0)])
        xl = MathTex(r"\Omega t", font_size=32, color=C_TEXT).next_to(ax.c2p(4 * PI, 0), RIGHT, buff=0.3)
        yl = MathTex(r"P_e", font_size=34, color=C_TEXT).next_to(ax.c2p(0, 1), UP, buff=0.15)
        plot = VGroup(grid, ax, xt, yt, xl, yl)

        def curve_pts(t, d):
            n = max(2, int(150 * t / PI))
            xs = np.linspace(0, t, n)
            return [ax.c2p(x, p_exc(x, d)) for x in xs]

        def curve():
            t = th.get_value()
            if t < 1e-3:
                return VMobject()
            return VMobject().set_points_as_corners(curve_pts(t, dt.get_value())).set_stroke(
                state["color"], width=4)
        curve_m = always_redraw(curve)
        cdot = always_redraw(lambda: Dot(ax.c2p(th.get_value(), p_exc(th.get_value(), dt.get_value())),
                                         radius=0.08, color=C_VEC))

        clock = VGroup(MathTex(r"\Omega t =", font_size=32, color=C_TEXT),
                       DecimalNumber(0, num_decimal_places=2, font_size=32, color=C_TEXT),
                       MathTex(r"\pi", font_size=32, color=C_TEXT)).arrange(RIGHT, buff=0.1)
        clock.next_to(ax, UP, buff=0.25).align_to(ax, RIGHT)
        clock[1].add_updater(lambda m: m.set_value(th.get_value() / PI))
        clock[2].add_updater(lambda m: m.next_to(clock[1], RIGHT, buff=0.08))

        # ------------------------------------------------------------ formulas / level scheme
        f_res = MathTex(r"\Delta = 0:\quad P_e(t) = \sin^2\!\left(\tfrac{\Omega t}{2}\right)",
                        font_size=34, color=C_RES)
        f_det = MathTex(r"\Delta \neq 0:\quad P_e(t) = \frac{\Omega^2}{\Omega'^2}"
                        r"\sin^2\!\left(\tfrac{\Omega' t}{2}\right),\quad \Omega' = \sqrt{\Omega^2+\Delta^2}",
                        font_size=34, color=C_DET)
        f_det.scale(30 / 34)
        f_res.scale(30 / 34)
        f_res.move_to([0, -1.75, 0]).align_to(ax, LEFT).shift(0.35 * LEFT)
        f_det.next_to(f_res, DOWN, buff=0.3).align_to(f_res, LEFT)
        note = MathTex(r"\Gamma_e/2\pi \approx 1\,\mathrm{mHz} \ll \Omega/2\pi:\ \text{no visible damping}",
                       font_size=28, color=C_DIM)
        note.to_edge(DOWN, buff=0.3).align_to(f_res, LEFT)

        # ------------------------------------------------------------ build-up
        self.play(FadeIn(head, shift=0.2 * DOWN))
        self.play(Create(outline), Create(equator), Create(meridian), FadeIn(axes3), run_time=1.5)
        self.play(FadeIn(ax_lab), FadeIn(poles), Write(e_lab), Write(g_lab),
                  Create(ax), FadeIn(grid), FadeIn(xt), FadeIn(yt), Write(xl), Write(yl))
        self.add(trail_m, curve_m)
        self.play(GrowArrow(vec_m.copy()), run_time=0.8)
        self.add(vec_m, zproj_m, cdot)
        self.remove(*[m for m in self.mobjects if isinstance(m, Arrow) and m is not vec_m])
        self.wait(0.5)

        # resonant drive switched on
        self.play(FadeIn(drive), FadeIn(drive_lab), Write(f_res), FadeIn(clock), FadeIn(note))
        self.wait(0.5)

        def mark(theta, text, direction):
            d = Dot(ax.c2p(theta, p_exc(theta, 0)), radius=0.07, color=C_RES)
            lab = Tex(text, font_size=28, color=C_RES).next_to(d, direction, buff=0.12)
            return VGroup(d, lab)

        self.play(th.animate.set_value(PI / 2), run_time=2.5, rate_func=linear)
        m1 = mark(PI / 2, r"$\pi/2$ pulse", DR)
        self.play(FadeIn(m1))
        self.wait(1)
        self.play(th.animate.set_value(PI), run_time=2.5, rate_func=linear)
        m2 = mark(PI, r"$\pi$ pulse", UP)
        self.play(FadeIn(m2))
        self.wait(1)
        self.play(th.animate.set_value(4 * PI), run_time=9, rate_func=linear)
        self.wait(1)

        # ------------------------------------------------------------ detuned drive
        res_curve = VMobject().set_points_as_corners(curve_pts(4 * PI, 0)).set_stroke(C_RES, width=3, opacity=0.4)
        res_trail = split_by_depth([bloch(s, 0) for s in np.linspace(0, 4 * PI, 241)],
                                   dict(color=C_RES, width=2.5, opacity=0.4),
                                   dict(color=C_RES, width=2, opacity=0.15))
        self.add(res_curve, res_trail)
        self.bring_to_front(trail_m, curve_m, vec_m, zproj_m, cdot, drive, drive_lab)
        state["color"] = C_DET
        th.set_value(0)
        self.play(FadeOut(m1), FadeOut(m2), f_res.animate.set_opacity(0.5), run_time=0.8)
        self.play(dt.animate.set_value(1.0), Write(f_det), run_time=2)
        dlab = MathTex(r"\Delta = \Omega", font_size=32, color=C_DET).next_to(clock, LEFT, buff=0.6)
        self.play(FadeIn(dlab))
        self.wait(0.5)
        self.play(th.animate.set_value(4 * PI), run_time=10, rate_func=linear)
        self.wait(2)
