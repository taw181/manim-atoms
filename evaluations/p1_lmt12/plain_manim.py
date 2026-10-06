"""12-pulse LMT Mach-Zehnder atom interferometer (single-photon clock transition).

Sequential large-momentum-transfer (LMT) Mach-Zehnder of order n = 4:
the standard pi/2 - pi - pi/2 sequence plus 4(n-1) = 12 LMT pi pulses
(n-1 after each beam splitter, n-1 on each side of the mirror, n-1 before
the final beam splitter). Pulses come alternately from a laser below
(+hbar k) and a laser above (-hbar k); every pi pulse swaps the internal
state g <-> e and adds one photon recoil, so the internal state is fixed
by the momentum: g at even, e at odd multiples of hbar k.

Space-time diagram in the freely falling frame of the initial atom
(gravity removed): horizontal = time, vertical = height.

Render (from /home/user/lmt-plain):
    uv run manim -ql --media_dir p1/media p1/lmt_mz.py LMTMachZehnder
"""

from manim import *
import numpy as np

# ---------------------------------------------------------------- style
G_COL = "#4FA3FF"      # ground state |g>
E_COL = "#FF9F43"      # excited clock state |e>
UP_COL = "#7CDB6A"     # laser pulse from below (+hbar k)
DN_COL = "#D27BFF"     # laser pulse from above (-hbar k)
DIM = "#8A8A8A"
TXT = "#E8E8E8"
ARM_W = 5

STATE_COL = {"g": G_COL, "e": E_COL}
DIR_COL = {+1: UP_COL, -1: DN_COL}

# ------------------------------------------------------------- geometry
N = 4               # LMT order: arms separate by N hbar k
T = 4.2             # pulse separation of the bare MZ (screen x units)
D = 0.45            # spacing between pulses inside one LMT stage
T_PRE = 0.6         # atom drawn before the first pulse
X0 = -5.9           # screen x of t = 0
Y0 = -2.2           # screen y of z = 0 (lower arm)
Y_BOT, Y_TOP = -2.55, 2.42   # extent of the drawn laser pulses
PORT_T = 0.9        # length of the output ports after the last pulse


def build_sequence():
    """Pulse schedule and the two arms' piecewise-linear trajectories.

    Each pulse is (t, {arm: dp}); dp = +-1 recoil for the arm it addresses.
    The laser direction follows from the arm's internal state:
    g + photon from below -> e, +hbar k; g + photon from above -> e, -hbar k;
    e stimulated into the beam from above -> g, +hbar k; from below -> g, -hbar k.
    """
    sched = []
    sched.append((0.0, {"U": +1}, "bs"))                      # pi/2 splits
    for j in range(1, N):
        sched.append((j * D, {"U": +1}, "lmt"))                # accelerate U
    for j in range(N - 1, 0, -1):
        sched.append((T - j * D, {"U": -1}, "lmt"))            # decelerate U
    sched.append((T, {"U": -1, "L": +1}, "mirror"))           # pi swaps arms
    for j in range(1, N):
        sched.append((T + j * D, {"L": +1}, "lmt"))            # accelerate L
    for j in range(N - 1, 0, -1):
        sched.append((2 * T - j * D, {"L": -1}, "lmt"))        # decelerate L
    sched.append((2 * T, {"U": +1, "L": -1}, "bs"))           # pi/2 recombines

    arm = {a: dict(state="g", p=0) for a in "UL"}
    segs = {a: [[-T_PRE, None, 0, "g"]] for a in "UL"}  # [t0, t1, p, state]
    pulses = []
    lmt_count = 0
    for i, (t, targets, kind) in enumerate(sched):
        dirs = set()
        for a, dp in targets.items():
            s = arm[a]["state"]
            # photon direction that gives this recoil from this state
            d = dp if s == "g" else -dp
            dirs.add(d)
        assert len(dirs) == 1, "a pulse comes from one laser"
        d = dirs.pop()
        last = i == len(sched) - 1
        if not last:
            for a, dp in targets.items():
                arm[a]["p"] += dp
                arm[a]["state"] = "e" if arm[a]["state"] == "g" else "g"
                segs[a][-1][1] = t
                segs[a].append([t, None, arm[a]["p"], arm[a]["state"]])
        if kind == "lmt":
            lmt_count += 1
            label = str(lmt_count)
        else:
            label = r"\pi" if kind == "mirror" else r"\pi/2"
        pulses.append(dict(t=t, dir=d, kind=kind, label=label,
                           targets=list(targets)))
    for a in "UL":
        segs[a][-1][1] = 2 * T
    # heights: integrate p (velocity in units of hbar k / m)
    for a in "UL":
        z = 0.0
        for s in segs[a]:
            s.append(z)                      # z at t0
            z += s[2] * (s[1] - s[0])
    zU = segs["U"][-1][4] + segs["U"][-1][2] * (2 * T - segs["U"][-1][0])
    zL = segs["L"][-1][4] + segs["L"][-1][2] * (2 * T - segs["L"][-1][0])
    assert abs(zU - zL) < 1e-9, (zU, zL)
    return pulses, segs, zU


PULSES, SEGS, Z_END = build_sequence()
S = (2.0 - Y0) / Z_END          # vertical scale: closure point at y = 2.0


def to_xy(t, z):
    return np.array([X0 + t, Y0 + S * z, 0.0])


def arm_at(a, t):
    """(point, state, p) of arm a at time t (clamped to its drawn range)."""
    segs = SEGS[a]
    t = min(max(t, segs[0][0]), segs[-1][1])
    for s in segs:
        if s[0] <= t < s[1] or s is segs[-1]:
            return to_xy(t, s[4] + s[2] * (t - s[0])), s[3], s[2]


def arm_path(a, t_now):
    g = VGroup()
    for t0, t1, p, st, z0 in SEGS[a]:
        if t_now <= t0:
            break
        te = min(t1, t_now)
        g.add(Line(to_xy(t0, z0), to_xy(te, z0 + p * (te - t0)),
                   color=STATE_COL[st], stroke_width=ARM_W))
    return g


def ket(state, p):
    mom = "0" if p == 0 else (r"\hbar k" if p == 1 else rf"{p}\hbar k")
    return MathTex(rf"|{state},\,{mom}\rangle", color=STATE_COL[state])


class LMTMachZehnder(Scene):
    def construct(self):
        # ------------------------------------------------ title
        title = Text("12-pulse LMT Mach–Zehnder atom interferometer",
                     font_size=32, color=TXT).to_edge(UP, buff=0.22)
        sub = Tex(r"$\pi/2$ -- $\pi$ -- $\pi/2$ Mach--Zehnder $+$ 12 LMT "
                  r"$\pi$ pulses $\Rightarrow$ $4\hbar k$ arm separation",
                  font_size=26, color=DIM).next_to(title, DOWN, buff=0.12)
        self.play(FadeIn(title), FadeIn(sub))

        # ------------------------------------------------ right panel
        xl = 4.15  # left edge of the panel
        head = Text("momentum ladder", font_size=20, color=TXT)
        head.move_to([0, 1.5, 0], aligned_edge=LEFT).set_x(xl, LEFT)
        rung_y = {p: 1.0 - 0.45 * (N - p) for p in range(N + 1)}
        rungs, kets = VGroup(), VGroup()
        for p in range(N + 1):
            st = "g" if p % 2 == 0 else "e"
            y = rung_y[p]
            rungs.add(Line([xl, y, 0], [xl + 0.85, y, 0],
                           color=STATE_COL[st], stroke_width=4))
            kets.add(ket(st, p).scale(0.62).set_y(y).set_x(xl + 1.0, LEFT))
        lad_note = Tex(r"$g$ ground, $e$ clock state", font_size=22,
                       color=DIM).set_y(rung_y[0] - 0.45).set_x(xl, LEFT)

        def legend_row(d, text, y):
            a = Arrow([0, -0.22 * d, 0], [0, 0.22 * d, 0], buff=0,
                      color=DIR_COL[d], stroke_width=5,
                      max_tip_length_to_length_ratio=0.45)
            a.move_to([xl + 0.1, y, 0])
            t = Tex(text, font_size=22, color=TXT)
            t.next_to(a, RIGHT, buff=0.15)
            return VGroup(a, t)

        leg = VGroup(
            legend_row(+1, r"from below: $+\hbar k$", -1.6),
            legend_row(-1, r"from above: $-\hbar k$", -2.1),
        )

        def mk_marker(letter, dx):
            def f():
                pt, st, p = arm_at(letter, tt.get_value())
                c = Circle(radius=0.13, color=WHITE, stroke_width=2,
                           fill_color=STATE_COL[st], fill_opacity=1)
                lab = Text(letter, font_size=14, color="#101010",
                           weight=BOLD)
                return VGroup(c, lab).move_to([xl + 0.42 + dx, rung_y[p], 0])
            return f

        tt = ValueTracker(-T_PRE)
        mark_L = always_redraw(mk_marker("L", -0.22))
        mark_U = always_redraw(mk_marker("U", +0.22))

        counter = VGroup(
            Text("pulse 0 / 15", font_size=20, color=TXT),
            Text("LMT pulse 0 / 12", font_size=20, color=TXT),
        ).arrange(DOWN, buff=0.12, aligned_edge=LEFT).set_y(-2.95).set_x(xl, LEFT)

        self.play(FadeIn(head), Create(rungs), FadeIn(kets),
                  FadeIn(lad_note), FadeIn(leg), FadeIn(counter))

        # ------------------------------------------------ axes hint
        ax = VGroup(
            Arrow([X0 - T_PRE - 0.35, Y0 - 0.15, 0],
                  [X0 - T_PRE - 0.35, Y0 + 0.75, 0], buff=0,
                  stroke_width=3, color=DIM,
                  max_tip_length_to_length_ratio=0.2),
        )
        ax.add(MathTex("z", color=DIM, font_size=28).next_to(ax[0], UP, 0.08))
        self.play(FadeIn(ax))

        # ------------------------------------------------ arms and atoms
        path_U = always_redraw(lambda: arm_path("U", tt.get_value()))
        path_L = always_redraw(lambda: arm_path("L", tt.get_value()))

        def mk_dot(a):
            def f():
                pt, st, p = arm_at(a, tt.get_value())
                return VGroup(
                    Dot(pt, radius=0.24, color=STATE_COL[st],
                        fill_opacity=0.25),
                    Circle(radius=0.14, color=WHITE, stroke_width=2,
                           fill_color=STATE_COL[st],
                           fill_opacity=1).move_to(pt),
                    Text(a, font_size=15, color="#101010",
                         weight=BOLD).move_to(pt),
                )
            return f

        dot_L = always_redraw(mk_dot("L"))
        dot_U = always_redraw(mk_dot("U"))
        self.add(path_L, path_U)
        self.play(FadeIn(dot_L), FadeIn(dot_U), FadeIn(mark_L),
                  FadeIn(mark_U))

        # ------------------------------------------------ stages (braces)
        stage_spans = [
            (0.0, (N - 1) * D, "beam splitter"),
            (T - (N - 1) * D, T + (N - 1) * D, "mirror"),
            (2 * T - (N - 1) * D, 2 * T, "beam splitter"),
        ]
        braces = []
        for t0, t1, name in stage_spans:
            b = BraceBetweenPoints([X0 + t1, Y_BOT - 0.08, 0],
                                   [X0 + t0, Y_BOT - 0.08, 0],
                                   direction=DOWN, color=DIM)
            lab = Text(name, font_size=20, color=DIM).next_to(b, DOWN, 0.08)
            braces.append((t0, VGroup(b, lab)))
        time_lab = Tex(r"time $\rightarrow$", font_size=24, color=DIM)
        time_lab.move_to([X0 + 0.5 * (stage_spans[0][1] + stage_spans[1][0]),
                          Y_BOT - 0.42, 0])

        # ------------------------------------------------ run the sequence
        n_lmt = 0
        for i, pu in enumerate(PULSES):
            t = pu["t"]
            dt = t - tt.get_value()
            if dt > 1e-9:
                self.play(tt.animate.set_value(t - 1e-6),
                          run_time=max(0.35, 0.55 * dt), rate_func=linear)
            stage = [g for t0, g in braces if abs(t0 - t) < 1e-9]
            if i == 0:
                self.play(FadeIn(time_lab), run_time=0.3)
            d = pu["dir"]
            col = DIR_COL[d]
            x = X0 + t
            y0, y1 = (Y_BOT, Y_TOP) if d > 0 else (Y_TOP, Y_BOT)
            beam = Arrow([x, y0, 0], [x, y1, 0], buff=0, color=col,
                         stroke_width=6, max_tip_length_to_length_ratio=0.05)
            if pu["kind"] == "lmt":
                lab = Text(pu["label"], font_size=18, color=col)
            else:
                lab = MathTex(pu["label"], font_size=26, color=WHITE)
            lab.move_to([x, Y_TOP + 0.2, 0])

            if pu["kind"] == "lmt":
                n_lmt += 1
            new_counter = VGroup(
                Text(f"pulse {i + 1} / 15", font_size=20, color=TXT),
                Text(f"LMT pulse {n_lmt} / 12", font_size=20, color=TXT),
            ).arrange(DOWN, buff=0.12, aligned_edge=LEFT).set_y(-2.95).set_x(xl, LEFT)

            flashes = [Flash(arm_at(a, t)[0], color=col, line_length=0.15,
                             flash_radius=0.22, num_lines=10)
                       for a in pu["targets"]]
            counter.become(new_counter)
            anims = [GrowArrow(beam), FadeIn(lab, shift=0.1 * DOWN)]
            anims += [FadeIn(g) for g in stage]
            self.play(*anims, run_time=0.45)
            tt.set_value(t)        # state flips now
            ghost = Line([x, Y_BOT, 0], [x, Y_TOP, 0], color=col,
                         stroke_width=2, stroke_opacity=0.35)
            ghost.set_z_index(-1)
            self.play(*flashes, FadeOut(beam), FadeIn(ghost),
                      run_time=0.4)
            self.add_foreground_mobjects(dot_L, dot_U)

        # ------------------------------------------------ output ports
        pt_end, _, _ = arm_at("U", 2 * T)
        port_g = Line(pt_end, to_xy(2 * T + PORT_T, Z_END),
                      color=G_COL, stroke_width=ARM_W)
        port_e = Line(pt_end, to_xy(2 * T + PORT_T, Z_END + PORT_T),
                      color=E_COL, stroke_width=ARM_W)
        dg = Dot(pt_end, radius=0.1, color=G_COL)
        de = Dot(pt_end, radius=0.1, color=E_COL)
        self.remove(dot_L, dot_U)
        self.add(dg, de)
        self.play(Create(port_g), Create(port_e),
                  MoveAlongPath(dg, port_g), MoveAlongPath(de, port_e),
                  FadeOut(mark_L), FadeOut(mark_U), run_time=1.0,
                  rate_func=linear)
        kg = ket("g", 0).scale(0.6).next_to(port_g.get_end(), RIGHT, 0.22)
        ke = ket("e", 1).scale(0.6).next_to(port_e.get_end(), RIGHT, 0.22)
        kg.shift(0.08 * DOWN)
        ke.shift(0.08 * UP)
        self.play(FadeIn(kg), FadeIn(ke))
        self.wait(0.4)

        # ------------------------------------------------ annotations
        def seg_mid(a, p):
            s = max((s for s in SEGS[a] if s[2] == p),
                    key=lambda s: s[1] - s[0])
            tm = 0.5 * (s[0] + s[1])
            return to_xy(tm, s[4] + s[2] * (tm - s[0]))

        ang = np.arctan(S * N)
        lab_u = MathTex(r"4\hbar k", font_size=30, color=TXT)
        lab_u.rotate(ang).move_to(seg_mid("U", N) + 0.32 * np.array(
            [-np.sin(ang), np.cos(ang), 0]))
        lab_l = MathTex(r"4\hbar k", font_size=30, color=TXT)
        lab_l.rotate(ang).move_to(seg_mid("L", N) + 0.32 * np.array(
            [np.sin(ang), -np.cos(ang), 0]))
        lab_u0 = MathTex(r"0", font_size=30, color=TXT).move_to(
            seg_mid("U", 0) + 0.25 * DOWN)
        lab_l0 = MathTex(r"0", font_size=30, color=TXT).move_to(
            seg_mid("L", 0) + 0.25 * UP)
        self.play(FadeIn(lab_u), FadeIn(lab_l), FadeIn(lab_u0),
                  FadeIn(lab_l0))

        # separation arrow at the mirror
        top = arm_at("U", T)[0]
        bot = arm_at("L", T)[0]
        sep = DoubleArrow(bot + 0.12 * UP, top + 0.12 * DOWN, buff=0,
                          color=TXT, stroke_width=3,
                          max_tip_length_to_length_ratio=0.06)
        sep.shift(0.0 * RIGHT)
        sep_lab = Tex(r"$\Delta z = \frac{\hbar k}{m}\,(4T - 12\delta)$",
                      font_size=24, color=TXT)
        sep_lab.next_to(sep, RIGHT, 0.1).set_y(1.3)
        self.play(GrowFromCenter(sep), FadeIn(sep_lab))
        note = Text("each LMT pulse addresses one arm (Doppler-selected)"
                    "  \u00b7  \u03b4: LMT pulse spacing  \u00b7  "
                    "freely falling frame",
                    font_size=14, color=DIM).move_to([-0.6, -3.72, 0])
        self.play(FadeIn(note))
        self.wait(2.5)
