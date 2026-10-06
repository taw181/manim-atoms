"""MOT -> moving-molasses launch -> atomic fountain -> Mach-Zehnder (pi/2-pi-pi/2) -> readout.

Render from /home/user/lmt-plain:
    uv run manim -ql --media_dir p6/media p6/fountain_mz.py FountainMachZehnder
"""
from manim import *
import numpy as np

# ---------------------------------------------------------------- style
C1 = "#58C4DD"          # |F=1, p>
C2 = "#FF9F43"          # |F=2, p + hbar k_eff>
HOT = "#FFE6A0"         # untrapped vapour
MOT_RED = "#E8505B"     # cooling light (red-detuned)
RAMAN = "#C77DFF"       # interferometry (Raman) light
DET = "#7EE08A"         # detection light
WALL = GREY_B
FS_TXT = 26

# ---------------------------------------------------------------- geometry (screen units)
R_CH = 0.55                       # chamber radius at the small (final) scale
SMALL_C = np.array([-5.2, -2.6, 0.0])
BIG_C = np.array([-3.1, -0.35, 0.0])
BIG_S = 2.55
TUBE_HW = 0.35
TUBE_TOP = 2.85

# ---------------------------------------------------------------- fountain kinematics (display units)
# z(t) = H (2t - t^2): launched at t=0, apex at t=1, back at t=2.
H = 4.6
T = 0.6
T1, T2, T3 = 1 - T, 1.0, 1 + T     # pulses symmetric about the apex
VR = 1.0                           # recoil velocity hbar k_eff / m (exaggerated)
Z_DET = 1.2                        # detection height above the MOT
T_END = 2.0
P2 = 0.75                          # P(F=2) for this shot: dphi = 2pi/3


def z0(t):
    return H * (2 * t - t * t)


def z_arm(arm, t):
    if arm == "a":   # stays in F=1 at the first pulse, kicked by the pi pulse
        return z0(t) + VR * max(0.0, t - T2)
    return z0(t) + VR * min(t - T1, T)   # kicked at the first pulse, de-kicked by pi


def z_port(port, t):
    return z0(t) + VR * T + (VR * (t - T3) if port == 2 else 0.0)


def tex(s, fs=FS_TXT, color=WHITE):
    return Tex(s, font_size=fs, color=color)


def lines(strs, fs=FS_TXT, buff=0.14):
    return VGroup(*[tex(s, fs) for s in strs]).arrange(DOWN, aligned_edge=LEFT, buff=buff)


def beam_pair(direction, half_len=1.1, half_w=0.11, color=MOT_RED):
    """A counter-propagating beam pair through the origin (two arrowheads, one per beam)."""
    d = np.array([*direction, 0.0]) / np.linalg.norm(direction)
    n = np.array([-d[1], d[0], 0.0])
    a, b = -half_len * d, half_len * d
    body = Polygon(a + half_w * n, b + half_w * n, b - half_w * n, a - half_w * n,
                   stroke_width=0, fill_color=color, fill_opacity=0.28)
    heads = VGroup()
    for end, sgn in ((a, 1), (b, -1)):   # arrow at each entry, pointing inward
        tip = end + sgn * 0.42 * d
        base = end + sgn * 0.18 * d
        heads.add(Polygon(tip, base + 0.1 * n, base - 0.1 * n, stroke_width=0,
                          fill_color=color, fill_opacity=0.9))
    return VGroup(body, heads)


def coil_xsec(out_of_page):
    c = Circle(radius=0.11, color=GREY_A, stroke_width=2).set_fill(BLACK, 1)
    if out_of_page:
        mark = Dot(radius=0.03, color=GREY_A)
    else:
        mark = VGroup(Line(UL * 0.06, DR * 0.06), Line(UR * 0.06, DL * 0.06)).set_stroke(GREY_A, 2)
    return VGroup(c, mark)


class FountainMachZehnder(Scene):
    def construct(self):
        rng = np.random.default_rng(7)

        # ============================================================ MOT (built small, shown big)
        chamber = Circle(radius=R_CH, color=WALL, stroke_width=3).set_fill("#1b1b1b", 1)
        pair_up_right = beam_pair((1, 1))     # entries: lower-left (up-going), upper-right (down-going)
        pair_up_left = beam_pair((-1, 1))     # entries: lower-right (up-going), upper-left (down-going)
        beams = VGroup(pair_up_right, pair_up_left)
        coils = VGroup(
            coil_xsec(True).move_to([-0.9, 0.45, 0]), coil_xsec(False).move_to([0.9, 0.45, 0]),
            coil_xsec(False).move_to([-0.9, -0.45, 0]), coil_xsec(True).move_to([0.9, -0.45, 0]),
        )
        mot = VGroup(chamber, beams, coils).shift(SMALL_C)
        mot.scale(BIG_S, about_point=SMALL_C).shift(BIG_C - SMALL_C)

        # big-view labels (not scaled with the group; faded before the shrink)
        def bigpt(x, y):
            return BIG_C + BIG_S * np.array([x, y, 0])

        sig_lbls = VGroup(
            MathTex(r"\sigma^+", font_size=34, color=MOT_RED).move_to(bigpt(-1.0, -0.72)),
            MathTex(r"\sigma^-", font_size=34, color=MOT_RED).move_to(bigpt(1.0, 0.72)),
            MathTex(r"\sigma^+", font_size=34, color=MOT_RED).move_to(bigpt(1.0, -0.72)),
            MathTex(r"\sigma^-", font_size=34, color=MOT_RED).move_to(bigpt(-1.0, 0.72)),
        )
        coil_lbl = tex(r"anti-Helmholtz coils", 24, GREY_A).move_to(bigpt(0, -0.82))

        # ============================================================ atoms
        N = 72
        amp = np.clip(np.abs(rng.normal(0, 0.55, (N, 2))) + 0.12, 0, 1.0)
        om = rng.uniform(0.7, 1.5, (N, 2)) * np.where(rng.random((N, 2)) < 0.5, -1, 1)
        ph = rng.uniform(0, TAU, (N, 2))
        arm = np.where(rng.random(N) < 0.5, "a", "b")
        port = np.ones(N, dtype=int)
        port[rng.permutation(N)[: int(round(P2 * N))]] = 2
        n2 = int((port == 2).sum())

        tt = ValueTracker(0.0)        # lab time since launch (display units)
        sig = ValueTracker(0.48)      # cloud size, local units
        speed = ValueTracker(5.0)     # thermal jitter rate
        cool = ValueTracker(0.0)      # colour: hot vapour -> cold
        det_on = [False]
        R_DOT = 0.034

        def z_atom(i, t):
            if t <= 0:
                return 0.0
            if t < T1:
                return z0(t)
            if t < T3:
                return z_arm(arm[i], t)
            return z_port(port[i], t)

        def col_atom(i, t):
            if t <= 0:
                return interpolate_color(ManimColor(HOT), ManimColor(C1), cool.get_value())
            if t < T1:
                return C1
            if t < T3:
                kicked = (arm[i] == "b") == (t < T2)
                return C2 if kicked else C1
            return C2 if port[i] == 2 else C1

        atoms = VGroup(*[Dot(radius=R_DOT, color=HOT) for _ in range(N)])

        def upd_atoms(m, dt):
            ph[:] += dt * speed.get_value() * om
            s = chamber.width / (2 * R_CH)
            c = chamber.get_center()
            t = tt.get_value()
            sg = sig.get_value() * (np.sqrt(1 + (0.55 * t) ** 2) if t > 0 else 1.0)
            ydet = SMALL_C[1] + Z_DET
            for i, d in enumerate(m):
                x = c[0] + s * sg * amp[i, 0] * np.sin(ph[i, 0])
                y = c[1] + s * (z_atom(i, t) + sg * amp[i, 1] * np.sin(ph[i, 1]))
                d.move_to([x, y, 0])
                d.set_color(col_atom(i, t))
                glow = det_on[0] and abs(y - ydet) < 0.09
                d.set(width=2 * R_DOT * (1.9 if glow else 1.0))

        upd_atoms(atoms, 0)
        atoms.add_updater(upd_atoms)

        # ============================================================ stage 1: MOT
        title = tex(r"1.\ Laser cooling: magneto-optical trap", 34).to_corner(UL, buff=0.3)
        info1 = lines([
            r"Red-detuned beams ($\Delta<0$) in",
            r"counter-propagating $\sigma^+/\sigma^-$ pairs",
            r"(third pair $\perp$ page)",
        ])
        info2 = lines([
            r"Doppler: an atom scatters more from",
            r"the beam it moves into $\Rightarrow$ friction",
        ])
        info3 = lines([
            r"Quadrupole field $B\propto r$: Zeeman shift",
            r"$+\ \sigma^\pm$ $\Rightarrow$ restoring force to $B=0$",
        ])
        info4 = lines([
            r"Optical molasses: $B$ off, larger $|\Delta|$",
            r"$\Rightarrow$ sub-Doppler (polarisation-gradient)",
            r"cooling",
        ])
        info = VGroup(info1, info2, info3, info4).arrange(DOWN, aligned_edge=LEFT, buff=0.38)
        info.move_to([3.75, 0.9, 0])
        temp_lbls = [
            tex(r"$T\approx 300$ K \ (vapour)", 32, HOT),
            tex(r"$T\approx 150\,\mu$K \ (MOT)", 32, C1),
            tex(r"$T\approx 3\,\mu$K \ (molasses)", 32, C1),
        ]
        for tl in temp_lbls:
            tl.next_to(info, DOWN, buff=0.55).align_to(info, LEFT)
        temp = temp_lbls[0]

        self.add(mot, atoms)
        self.play(FadeIn(title), FadeIn(mot), FadeIn(sig_lbls), FadeIn(coil_lbl),
                  FadeIn(info1), FadeIn(temp), run_time=1.5)
        self.wait(1.0)
        self.play(FadeIn(info2), run_time=0.8)
        self.play(FadeIn(info3), run_time=0.8)
        # capture and Doppler cooling
        self.play(sig.animate.set_value(0.11), speed.animate.set_value(1.8),
                  cool.animate.set_value(1.0), Transform(temp, temp_lbls[1]),
                  run_time=4.0, rate_func=smooth)
        self.wait(0.8)
        # molasses: field off
        self.play(FadeIn(info4), coils.animate.set_opacity(0.25), coil_lbl.animate.set_opacity(0.3),
                  run_time=1.0)
        self.play(sig.animate.set_value(0.075), speed.animate.set_value(0.6),
                  Transform(temp, temp_lbls[2]), run_time=2.5)
        self.wait(1.0)

        # ============================================================ apparatus + space-time axes
        def sp(z):  # screen y of height z above the MOT
            return SMALL_C[1] + z

        x0 = SMALL_C[0]
        tube = VGroup(
            Line([x0 - TUBE_HW, sp(R_CH - 0.03), 0], [x0 - TUBE_HW, TUBE_TOP, 0]),
            Line([x0 + TUBE_HW, sp(R_CH - 0.03), 0], [x0 + TUBE_HW, TUBE_TOP, 0]),
        ).set_stroke(WALL, 3)
        mirror = VGroup(
            Line([x0 - 0.45, TUBE_TOP + 0.08, 0], [x0 + 0.45, TUBE_TOP + 0.08, 0]).set_stroke(GREY_A, 5),
            *[Line([x0 - 0.42 + 0.12 * k, TUBE_TOP + 0.1, 0], [x0 - 0.34 + 0.12 * k, TUBE_TOP + 0.2, 0])
              .set_stroke(GREY_A, 1.5) for k in range(8)],
        )
        raman_col = Rectangle(width=2 * TUBE_HW - 0.12, height=TUBE_TOP - sp(-R_CH - 0.6),
                              stroke_width=0, fill_color=RAMAN, fill_opacity=0.0)
        raman_col.move_to([x0, (TUBE_TOP + sp(-R_CH - 0.6)) / 2, 0])
        raman_ghost = DashedLine([x0, sp(-R_CH - 0.6), 0], [x0, TUBE_TOP, 0],
                                 dash_length=0.08).set_stroke(RAMAN, 1.5, opacity=0.5)
        raman_lbl = tex(r"Raman\\beams", 22, RAMAN).move_to([-6.45, 2.25, 0])
        raman_arrows = VGroup(
            Arrow([-6.45, 1.55, 0], [-6.45, 2.0 - 0.05 + 0.0, 0], buff=0, stroke_width=3,
                  max_tip_length_to_length_ratio=0.35).set_color(RAMAN),
        )
        raman_arrows = VGroup(  # k1 up, k2 down (retro-reflected)
            Arrow([-6.6, 1.2, 0], [-6.6, 1.75, 0], buff=0, stroke_width=3,
                  max_tip_length_to_length_ratio=0.3).set_color(RAMAN),
            Arrow([-6.3, 1.75, 0], [-6.3, 1.2, 0], buff=0, stroke_width=3,
                  max_tip_length_to_length_ratio=0.3).set_color(RAMAN),
        )
        ydet = sp(Z_DET)
        det_beam = Rectangle(width=1.7, height=0.1, stroke_width=0, fill_color=DET, fill_opacity=0.3)
        det_beam.move_to([x0 - 0.1, ydet, 0])
        pmt = Rectangle(width=0.22, height=0.34, color=GREY_A, stroke_width=2).set_fill("#2a2a2a", 1)
        pmt.next_to(det_beam, RIGHT, buff=0.08)
        det_lbl = tex(r"detection", 22, DET).next_to(pmt, RIGHT, buff=0.1)
        mot_lbl = tex(r"MOT", 24, MOT_RED).move_to([-6.55, SMALL_C[1], 0])
        g_arrow = Arrow([-6.45, 0.6, 0], [-6.45, -0.3, 0], buff=0, stroke_width=4, color=GREY_A,
                        max_tip_length_to_length_ratio=0.3)
        g_lbl = MathTex(r"g", font_size=32, color=GREY_A).next_to(g_arrow, RIGHT, buff=0.1)
        apparatus = VGroup(raman_ghost, raman_col, tube, mirror, det_beam, pmt, det_lbl,
                           raman_lbl, raman_arrows, mot_lbl, g_arrow, g_lbl)

        ax = Axes(x_range=[0, 2.12, 1], y_range=[0, 5.45, 1], x_length=5.0, y_length=5.45,
                  tips=True, axis_config={"include_ticks": False, "stroke_width": 2.5,
                                          "color": GREY_B, "tip_width": 0.18, "tip_height": 0.18})
        ax.shift(np.array([-2.75, SMALL_C[1], 0]) - ax.c2p(0, 0))
        ax_lbls = VGroup(
            MathTex("t", font_size=32, color=GREY_B).next_to(ax.x_axis.get_end(), DOWN, buff=0.15),
            MathTex("z", font_size=32, color=GREY_B).next_to(ax.y_axis.get_end(), LEFT, buff=0.15),
            tex(r"launch", 20, GREY_B).next_to(ax.c2p(0, 0), DOWN, buff=0.12),
        )

        def seg(f, ta, tb, color, tc, n=48):
            tb = min(tb, tc)
            if tb <= ta + 1e-4:
                return VMobject()
            ts = np.linspace(ta, tb, n)
            m = VMobject().set_points_as_corners([ax.c2p(t, f(t)) for t in ts])
            return m.set_stroke(color, 4)

        def worldlines():
            t = tt.get_value()
            if t <= 0:
                return VGroup()
            return VGroup(
                seg(z0, 0, T1, C1, t),
                seg(lambda s: z_arm("a", s), T1, T2, C1, t),
                seg(lambda s: z_arm("a", s), T2, T3, C2, t),
                seg(lambda s: z_arm("b", s), T1, T2, C2, t),
                seg(lambda s: z_arm("b", s), T2, T3, C1, t),
                seg(lambda s: z_port(1, s), T3, T_END, C1, t),
                seg(lambda s: z_port(2, s), T3, T_END, C2, t),
            )

        def tracers():
            t = tt.get_value()
            if t <= 0.02 or t >= T_END:
                return VGroup()
            if t < T1:
                zs = [z0(t)]
            elif t < T3:
                zs = [z_arm("a", t), z_arm("b", t)]
            else:
                zs = [z_port(1, t), z_port(2, t)]
            g = VGroup()
            for z in zs:
                p = ax.c2p(t, z)
                g.add(DashedLine([x0 + TUBE_HW + 0.08, p[1], 0], p, dash_length=0.06)
                      .set_stroke(GREY_A, 1.2, opacity=0.45))
            return g

        wl = always_redraw(worldlines)
        tr = always_redraw(tracers)

        # ============================================================ stage 2: shrink + launch
        title2 = tex(r"2.\ Launch: moving molasses $\to$ atomic fountain", 34).to_corner(UL, buff=0.3)
        mot.generate_target()
        mot.target.scale(1 / BIG_S, about_point=BIG_C).shift(SMALL_C - BIG_C)
        self.play(FadeOut(VGroup(info, temp, sig_lbls, coil_lbl)), run_time=0.8)
        self.play(MoveToTarget(mot), run_time=2.0)
        self.play(FadeIn(apparatus), Create(ax), FadeIn(ax_lbls), FadeOut(title, shift=UP*0.2), FadeIn(title2, shift=UP*0.2), run_time=1.5)
        title = title2
        self.add(wl, tr)

        INFO_X = 3.0
        delta_lbls = VGroup(
            MathTex(r"\omega{+}\delta", font_size=24, color=MOT_RED).move_to(SMALL_C + [-1.2, -0.95, 0]),
            MathTex(r"\omega{+}\delta", font_size=24, color=MOT_RED).move_to(SMALL_C + [1.2, -0.95, 0]),
            MathTex(r"\omega{-}\delta", font_size=24, color=MOT_RED).move_to(SMALL_C + [-1.2, 0.95, 0]),
            MathTex(r"\omega{-}\delta", font_size=24, color=MOT_RED).move_to(SMALL_C + [1.2, 0.95, 0]),
        )
        mot_lbl.generate_target()
        info_l = VGroup(
            tex(r"\textbf{Moving molasses}", 28),
            lines([
                r"up-going beams at $\omega+\delta$,",
                r"down-going beams at $\omega-\delta$:",
                r"atoms cool in a frame moving up",
                r"at $v_0=\sqrt{2}\,\delta/k$ (beams at $45^\circ$)",
            ], 24),
            lines([
                r"Light off $\Rightarrow$ free fall:",
                r"$z(t)=v_0t-\tfrac12 g t^2$",
                r"state prep: $|F{=}1,m_F{=}0\rangle$",
            ], 24),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        info_l.next_to([INFO_X, 2.95, 0], DOWN, buff=0, aligned_edge=UL)
        info_l.align_to([INFO_X, 0, 0], LEFT)

        self.play(FadeIn(delta_lbls), FadeOut(mot_lbl), FadeIn(info_l[0]), FadeIn(info_l[1]), run_time=1.0)
        self.wait(1.0)
        # acceleration in the moving molasses, beams switched off as the cloud leaves
        self.play(tt.animate.set_value(0.1), beams.animate.set_opacity(0.0),
                  FadeOut(delta_lbls), rate_func=rate_functions.ease_in_quad, run_time=1.2)
        self.play(FadeIn(info_l[2]), tt.animate.set_value(T1 - 0.02), rate_func=linear, run_time=1.6)
        self.play(tt.animate.set_value(T1), rate_func=linear, run_time=0.1)

        # ============================================================ stage 3: Mach-Zehnder
        title3 = tex(r"3.\ Mach--Zehnder: $\pi/2$ -- $\pi$ -- $\pi/2$ Raman pulses", 34).to_corner(UL, buff=0.3)
        legend = VGroup(
            VGroup(Dot(radius=0.07, color=C1), MathTex(r"|F{=}1,\,p\rangle", font_size=28, color=C1)
                   ).arrange(RIGHT, buff=0.15),
            VGroup(Dot(radius=0.07, color=C2),
                   MathTex(r"|F{=}2,\,p+\hbar k_\mathrm{eff}\rangle", font_size=28, color=C2)
                   ).arrange(RIGHT, buff=0.15),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        mz_head = tex(r"\textbf{Raman pulses}, $k_\mathrm{eff}=k_1+k_2$", 26)
        mz_lines = [
            tex(r"$\pi/2$: beamsplitter", 26),
            tex(r"$\pi$: mirror (swap states)", 26),
            tex(r"$\pi/2$: recombine", 26),
        ]
        mz_note = lines([
            r"pulses $T$ apart, symmetric",
            r"about the apex",
            r"(arm separation not to scale)",
        ], 22)
        info_m = VGroup(mz_head, legend, *mz_lines, mz_note).arrange(DOWN, aligned_edge=LEFT, buff=0.24)
        info_m.next_to([INFO_X, 2.95, 0], DOWN, buff=0, aligned_edge=UL)
        info_m.align_to([INFO_X, 0, 0], LEFT)
        mz_note.shift(DOWN * 0.15)

        band_h = ax.c2p(0, 5.45)[1] - ax.c2p(0, 0)[1]
        pulse_names = [r"\pi/2", r"\pi", r"\pi/2"]
        bands, plabels = VGroup(), VGroup()
        for ti, nm in zip((T1, T2, T3), pulse_names):
            b = Rectangle(width=0.07, height=band_h, stroke_width=0, fill_color=RAMAN, fill_opacity=0.35)
            b.move_to(ax.c2p(ti, 0), aligned_edge=DOWN)
            bands.add(b)
            plabels.add(MathTex(nm, font_size=32, color=RAMAN).next_to(b, UP, buff=0.08))

        self.play(FadeOut(info_l), FadeOut(title, shift=UP*0.2), FadeIn(title3, shift=UP*0.2), run_time=0.8)
        title = title3
        self.play(FadeIn(mz_head), FadeIn(legend), run_time=0.8)

        def pulse(k):
            self.play(raman_col.animate.set_fill(opacity=0.55), FadeIn(bands[k]), FadeIn(plabels[k]),
                      FadeIn(mz_lines[k]), run_time=0.35)
            self.play(raman_col.animate.set_fill(opacity=0.0), run_time=0.45)

        pulse(0)
        self.play(tt.animate.set_value(T2), rate_func=linear, run_time=3.0)
        pulse(1)
        self.play(tt.animate.set_value(T3), rate_func=linear, run_time=3.0)
        pulse(2)
        self.play(FadeIn(mz_note), run_time=0.6)
        braces = VGroup(
            BraceBetweenPoints(ax.c2p(T1, 0), ax.c2p(T2, 0), DOWN, buff=0.08),
            BraceBetweenPoints(ax.c2p(T2, 0), ax.c2p(T3, 0), DOWN, buff=0.08),
        ).set_color(GREY_A)
        blbls = VGroup(*[MathTex("T", font_size=30, color=GREY_A).next_to(b, DOWN, buff=0.06)
                         for b in braces])
        loop_pts = ([ax.c2p(t, z_arm("b", t)) for t in np.linspace(T1, T3, 60)]
                    + [ax.c2p(t, z_arm("a", t)) for t in np.linspace(T3, T1, 60)])
        loop = Polygon(*loop_pts, stroke_width=0, fill_color=WHITE, fill_opacity=0.16)
        phase_lbl = MathTex(r"\Delta\phi = k_\mathrm{eff}\, g\, T^2", font_size=34)
        phase_lbl.move_to(ax.c2p(1.0, 2.45))
        loop_mid = ax.c2p(1.15, z0(1.15) + VR * (0.5 * T + 0.5 * (1.15 - T2)))
        phase_arrow = Arrow(phase_lbl.get_corner(UR) + LEFT * 0.35, loop_mid, buff=0.08,
                            stroke_width=2.5, color=GREY_A, max_tip_length_to_length_ratio=0.12)
        self.play(FadeIn(loop), GrowFromCenter(braces), FadeIn(blbls), run_time=1.0)
        self.play(Write(phase_lbl), GrowArrow(phase_arrow), run_time=1.2)
        self.wait(0.8)

        # ============================================================ stage 4: detection + fringe
        title4 = tex(r"4.\ Readout: state-selective fluorescence", 34).to_corner(UL, buff=0.3)
        self.play(FadeOut(info_m), FadeOut(title, shift=UP*0.2), FadeIn(title4, shift=UP*0.2), run_time=0.8)
        title = title4

        bar_base = 0.95
        bar_hmax = 1.5
        bx1, bx2 = INFO_X + 0.55, INFO_X + 1.55
        baseline = Line([INFO_X + 0.1, bar_base, 0], [INFO_X + 2.1, bar_base, 0]).set_stroke(GREY_B, 2)
        p1 = (N - n2) / N
        p2 = n2 / N

        def bar(x, frac, color):
            return Rectangle(width=0.55, height=max(bar_hmax * frac, 1e-3), stroke_width=0,
                             fill_color=color, fill_opacity=0.85).move_to([x, bar_base, 0], aligned_edge=DOWN)

        bar1, bar2 = bar(bx1, p1, C1), bar(bx2, p2, C2)
        bar1_0, bar2_0 = bar(bx1, 0, C1), bar(bx2, 0, C2)
        bar_lbls = VGroup(
            MathTex(r"F{=}1", font_size=26, color=C1).next_to([bx1, bar_base, 0], DOWN, buff=0.12),
            MathTex(r"F{=}2", font_size=26, color=C2).next_to([bx2, bar_base, 0], DOWN, buff=0.12),
        )
        val1 = tex(f"{round(100 * p1)}\\%", 24, C1).next_to(bar1, UP, buff=0.08)
        val2 = tex(f"{round(100 * p2)}\\%", 24, C2).next_to(bar2, UP, buff=0.08)
        head4 = tex(r"\textbf{One shot}", 26).move_to([INFO_X, 2.75, 0], aligned_edge=LEFT)
        pmt_glow = pmt.copy().set_fill(DET, 0.0).set_stroke(width=0)

        self.play(FadeIn(head4), Create(baseline), FadeIn(bar_lbls), FadeIn(bar1_0), FadeIn(bar2_0),
                  run_time=0.8)
        self.add(pmt_glow)
        # fall back through the detection beam
        t_d0 = 1.86
        self.play(tt.animate.set_value(t_d0), rate_func=linear, run_time=1.7)
        det_on[0] = True
        self.play(det_beam.animate.set_fill(opacity=0.75), pmt_glow.animate.set_fill(opacity=0.8),
                  tt.animate.set_value(1.905), rate_func=linear, run_time=0.6)
        self.play(tt.animate.set_value(1.99), Transform(bar1_0, bar1), Transform(bar2_0, bar2),
                  rate_func=linear, run_time=1.6)
        det_on[0] = False
        self.play(det_beam.animate.set_fill(opacity=0.3), pmt_glow.animate.set_fill(opacity=0.0),
                  FadeIn(val1), FadeIn(val2), FadeOut(atoms), tt.animate.set_value(T_END),
                  run_time=0.7)
        atoms.clear_updaters()
        self.remove(tr)

        # fringe from repeated shots, scanning the laser phase of the last pulse
        phi0 = np.arccos(1 - 2 * P2)    # k_eff g T^2 (mod 2 pi) for this shot
        fx = Axes(x_range=[0, 4 * PI, PI], y_range=[0, 1.05, 0.5], x_length=3.4, y_length=1.55,
                  tips=False, axis_config={"include_ticks": True, "stroke_width": 2, "color": GREY_B,
                                           "tick_size": 0.05})
        fx.move_to([INFO_X + 2.15, -2.55, 0])
        fx_lbls = VGroup(
            MathTex(r"\phi_L", font_size=28, color=GREY_B).next_to(fx.x_axis.get_end(), DOWN, buff=0.12),
            MathTex(r"P_2", font_size=28, color=GREY_B).next_to(fx.c2p(0, 0.5), LEFT, buff=0.15),
            MathTex("1", font_size=22, color=GREY_B).next_to(fx.c2p(0, 1), LEFT, buff=0.1).shift(RIGHT * 0.02),
            MathTex("0", font_size=22, color=GREY_B).next_to(fx.c2p(0, 0), LEFT, buff=0.1),
        )
        formula = MathTex(r"P_2=\tfrac12\left[1-\cos\!\left(k_\mathrm{eff}gT^2+\phi_L\right)\right]",
                          font_size=26)
        formula.move_to([INFO_X, -0.75, 0], aligned_edge=LEFT)
        scan_head = VGroup(tex(r"\textbf{Many shots}, scanning the laser", 24),
                           tex(r"phase $\phi_L$ of the last pulse", 24)).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        scan_head.move_to([INFO_X, 0.0 + 0.1, 0], aligned_edge=LEFT)
        scan_head.next_to(formula, UP, buff=0.18).align_to([INFO_X, 0, 0], LEFT)
        fringe = fx.plot(lambda p: 0.5 * (1 - np.cos(phi0 + p)), x_range=[0, 4 * PI], color=C2,
                         stroke_width=2.5)
        nshot = 28
        phis = np.linspace(0, 4 * PI, nshot)
        pts = VGroup()
        for k, p in enumerate(phis):
            y = 0.5 * (1 - np.cos(phi0 + p)) + (0 if k == 0 else rng.normal(0, 0.035))
            pts.add(Dot(fx.c2p(p, np.clip(y, 0.0, 1.0)), radius=0.04, color=WHITE))
        first = pts[0]
        ring = Circle(radius=0.1, color=C2, stroke_width=3).move_to(first)

        self.play(FadeIn(scan_head), FadeIn(formula), Create(fx), FadeIn(fx_lbls), run_time=1.2)
        self.play(TransformFromCopy(val2, first), Create(ring), run_time=1.0)
        self.play(LaggedStart(*[FadeIn(p, scale=0.5) for p in pts[1:]], lag_ratio=0.15), run_time=3.0)
        self.play(Create(fringe), run_time=1.5)
        self.wait(2.5)
