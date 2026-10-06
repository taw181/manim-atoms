"""Three-cloud single-photon gradiometer sharing one laser.

Left: the vertical baseline (vacuum tube) with one laser at the bottom and
three atom clouds A, B, C along it.  Centre: the space-time picture (height z
up, lab time t across) in the clouds' free-fall frame.  Each laser pulse is a
light-like line whose tilt (finite light travel time, exaggerated) shows that
the *same* pulse reaches A, then B, then C.  Each cloud runs a clock-transition
Mach-Zehnder (pi/2 - pi - pi/2): absorbing a photon of the upward beam is a
+hbar k kick into |e>, stimulated emission back into it a -hbar k kick to |g>.
Right: the three interferometer phases, their two gradients and the second
difference.  Laser phase noise is common to all three clouds and drops out of
every difference.

Render from /home/user/lmt-plain:
    uv run manim -ql --media_dir p4/media p4/three_cloud_gradiometer.py ThreeCloudGradiometer
"""

import numpy as np
from manim import *

# ---------------------------------------------------------------- style ----
GROUND = "#4cc9f0"      # |g>
EXCITED = "#ffa630"     # |e>
LASER = "#ff4d6d"       # 698 nm clock light
DIM = "#7a7a7a"
TEXT = "#e8e8e8"
ARM_W = 4
PULSE_W = 3

# ------------------------------------------------------------- geometry ----
X0, Y0 = -5.0, -2.95    # scene point of (t = 0, z = 0); z = 0 is the laser
TOWER_X = -6.35
Z_TOP = 5.6             # top of the baseline
C = 8.0                 # light speed (diagram units): tilt hugely exaggerated
V = 0.45                # recoil velocity (exaggerated)
T = 1.8                 # pulse separation
T_PULSES = (0.35, 0.35 + T, 0.35 + 2 * T)
PULSE_NAMES = (r"\pi/2", r"\pi", r"\pi/2")
Z0 = {"A": 0.7, "B": 2.5, "C": 4.3}   # launch heights of the three clouds
NAMES = ("A", "B", "C")
OUT = 0.6               # length of the output-port stubs
SIGNAL = {"A": 0.0, "B": 0.9, "C": 2.4}  # phase signal along the baseline (rad)


def P(t, z):
    """Scene point of space-time event (t, z)."""
    return np.array([X0 + t, Y0 + z, 0.0])


def kinks(name):
    """Times at which the three pulses reach cloud `name` (at its mid-height)."""
    zm = Z0[name] + V * T / 2
    return [tp + zm / C for tp in T_PULSES]


def segments(name):
    """Arm segments (t_a, z_a, t_b, z_b, colour) of cloud `name`'s interferometer."""
    z0 = Z0[name]
    t1, t2, t3 = kinks(name)
    zt = z0 + V * T
    return [
        (0.0, z0, t1, z0, GROUND),                     # cloud at rest in |g>
        (t1, z0, t2, z0, GROUND),                      # lower arm: stays |g>
        (t1, z0, t2, zt, EXCITED),                     # upper arm: absorbs, +hbar k
        (t2, zt, t3, zt, GROUND),                      # upper arm: emits, -hbar k
        (t2, z0, t3, zt, EXCITED),                     # lower arm: absorbs, +hbar k
        (t3, zt, t3 + OUT, zt, GROUND),                # port g
        (t3, zt, t3 + OUT, zt + V * OUT, EXCITED),     # port e
    ]


def t_end():
    return kinks("C")[2] + OUT


def arm_positions(name, tau):
    """(z, colour) of every wavepacket of cloud `name` at lab time tau."""
    segs = segments(name)
    out = []
    for i, (ta, za, tb, zb, col) in enumerate(segs):
        is_port = i >= len(segs) - 2
        if ta <= tau and (tau < tb or (is_port and tau >= tb)):
            s = min((tau - ta) / (tb - ta), 1.0)
            out.append((za + s * (zb - za), col))
    return out


class ThreeCloudGradiometer(Scene):
    def construct(self):
        tau = ValueTracker(0.0)

        # ---------------------------------------------------- title, legend
        title = Text("Three-cloud gradiometer, one shared laser",
                     font_size=30, color=TEXT).to_corner(UL, buff=0.3)
        legend = VGroup()
        for col, lab in ((GROUND, r"|g\rangle"), (EXCITED, r"|e\rangle"), (LASER, r"\text{pulse}")):
            legend.add(VGroup(Line(ORIGIN, 0.4 * RIGHT, color=col, stroke_width=ARM_W),
                              MathTex(lab, font_size=28, color=TEXT)).arrange(RIGHT, buff=0.12))
        legend.arrange(RIGHT, buff=0.35).to_corner(UR, buff=0.3)
        legend.match_y(title)

        # ---------------------------------------------------- tower + laser
        laser_box = RoundedRectangle(width=0.9, height=0.42, corner_radius=0.06,
                                     fill_color="#3a0f18", fill_opacity=1,
                                     stroke_color=LASER, stroke_width=2)
        laser_box.move_to([TOWER_X, Y0 - 0.25, 0])
        laser_lab = Text("laser", font_size=18, color=LASER).move_to(laser_box)
        beam = Rectangle(width=0.16, height=Z_TOP, stroke_width=0,
                         fill_color=LASER, fill_opacity=0.18)
        beam.move_to([TOWER_X, Y0 + Z_TOP / 2 - 0.04, 0])
        tube = VGroup(*[Line([TOWER_X + s * 0.32, Y0 - 0.04, 0], [TOWER_X + s * 0.32, Y0 + Z_TOP, 0],
                             color=DIM, stroke_width=2) for s in (-1, 1)])
        tower = VGroup(beam, tube, laser_box, laser_lab)

        # ---------------------------------------------------- axes
        t_axis = Arrow(P(-0.05, 0), P(5.75, 0), buff=0, stroke_width=2, color=DIM,
                       max_tip_length_to_length_ratio=0.03)
        z_axis = Arrow(P(0, -0.05), P(0, Z_TOP + 0.1), buff=0, stroke_width=2, color=DIM,
                       max_tip_length_to_length_ratio=0.04)
        t_lab = MathTex("t", font_size=30, color=DIM).next_to(t_axis.get_end(), DOWN, buff=0.12)
        z_lab = MathTex("z", font_size=30, color=DIM).next_to(z_axis.get_end(), RIGHT, buff=0.12)
        ticks = VGroup()
        for name in NAMES:
            y = Y0 + Z0[name]
            ticks.add(DashedLine([TOWER_X + 0.35, y, 0], [X0, y, 0], dash_length=0.06,
                                 stroke_width=1.5, color=DIM, stroke_opacity=0.6))
        cloud_labs = VGroup(*[
            Text(n, font_size=26, color=TEXT, weight=BOLD)
            .move_to([X0 - 0.42, Y0 + Z0[n] + 0.24, 0]) for n in NAMES])
        axes = VGroup(t_axis, z_axis, t_lab, z_lab)

        # ---------------------------------------------------- dynamic: arms
        def draw_arms():
            g = VGroup()
            now = tau.get_value()
            for name in NAMES:
                for ta, za, tb, zb, col in segments(name):
                    if now <= ta:
                        continue
                    s = min((now - ta) / (tb - ta), 1.0)
                    end = (ta + s * (tb - ta), za + s * (zb - za))
                    g.add(Line(P(ta, za), P(*end), color=col, stroke_width=ARM_W))
            return g

        arms = always_redraw(draw_arms)

        # ---------------------------------------------------- dynamic: pulses
        def draw_pulses():
            g = VGroup()
            now = tau.get_value()
            for tp in T_PULSES:
                if now <= tp:
                    continue
                z = min(C * (now - tp), Z_TOP)
                done = z >= Z_TOP
                g.add(Line(P(tp, 0), P(tp + z / C, z), color=LASER,
                           stroke_width=PULSE_W, stroke_opacity=0.55 if done else 1.0))
                if not done:   # the pulse in the tube
                    g.add(Rectangle(width=0.3, height=0.32, stroke_width=0, fill_color=LASER,
                                    fill_opacity=0.95).move_to([TOWER_X, Y0 + z, 0]))
                    g.add(Dot(P(tp + z / C, z), radius=0.06, color=WHITE))
            return g

        pulses = always_redraw(draw_pulses)
        pulse_labs = VGroup(*[
            MathTex(lab, font_size=28, color=LASER).move_to(P(tp + Z_TOP / C, Z_TOP + 0.3))
            for tp, lab in zip(T_PULSES, PULSE_NAMES)])

        # ---------------------------------------------------- dynamic: atoms in the tube
        def draw_atoms():
            g = VGroup()
            now = tau.get_value()
            for name in NAMES:
                for z, col in arm_positions(name, now):
                    g.add(Dot([TOWER_X, Y0 + z, 0], radius=0.09, color=col))
            return g

        atoms = always_redraw(draw_atoms)

        # ================================================== beat 1: layout
        self.play(FadeIn(title), FadeIn(tower), Create(axes), run_time=1.5)
        self.add(arms, atoms)
        self.play(FadeIn(cloud_labs), Create(ticks), FadeIn(legend), run_time=1.0)
        cap = self.caption("One laser beam addresses three clouds along a vertical baseline")
        self.wait(1.2)

        # ================================================== beats 2-4: pulses
        self.add(pulses)
        travel = Text("light travel time exaggerated", font_size=18, color=LASER, slant=ITALIC)
        travel.move_to([X0, Y0 - 0.32, 0], aligned_edge=LEFT)
        stops = [T_PULSES[1] - 0.05, T_PULSES[2] - 0.05, t_end()]
        texts = [
            r"$\pi/2$: the same pulse splits A, then B, then C",
            r"$\pi$: every arm swaps $|g\rangle \leftrightarrow |e\rangle$ and its momentum",
            r"$\pi/2$: recombine; each cloud's output ports read out its phase",
        ]
        start = 0.0
        for k, (stop, msg) in enumerate(zip(stops, texts)):
            new_cap = self.caption_tex(msg)
            anims = [FadeIn(pulse_labs[k], shift=0.1 * DOWN), ReplacementTransform(cap, new_cap)]
            if k == 0:
                anims.append(FadeIn(travel))
            self.play(*anims, run_time=0.6)
            cap = new_cap
            self.play(tau.animate.set_value(stop), run_time=1.6 * (stop - start),
                      rate_func=linear)
            start = stop
            self.wait(0.5)
        self.play(FadeOut(travel), run_time=0.4)

        # ================================================== readout
        noise = ValueTracker(0.0)
        sig = ValueTracker(0.0)

        def phase(name):
            return noise.get_value() + sig.get_value() * SIGNAL[name]

        y_mid = {n: Y0 + Z0[n] + V * T / 2 for n in NAMES}

        # port populations in the space-time picture
        def draw_ports():
            g = VGroup()
            for name in NAMES:
                t3 = kinks(name)[2]
                zt = Z0[name] + V * T
                pe = np.sin(phase(name) / 2) ** 2
                g.add(Dot(P(t3 + OUT, zt), radius=0.11, color=GROUND,
                          fill_opacity=0.12 + 0.88 * (1 - pe)))
                g.add(Dot(P(t3 + OUT, zt + V * OUT), radius=0.11, color=EXCITED,
                          fill_opacity=0.12 + 0.88 * pe))
            return g

        ports = always_redraw(draw_ports)

        def dial(center, get_phi, label, color=TEXT, r=0.42):
            ring = Circle(radius=r, color=DIM, stroke_width=2).move_to(center)
            zero = Line(center + r * UP, center + (r - 0.1) * UP, color=DIM, stroke_width=2)
            needle = always_redraw(lambda: Line(
                center, center + 0.88 * r * np.array([np.sin(get_phi()), np.cos(get_phi()), 0]),
                color=color, stroke_width=4))
            hub = Dot(center, radius=0.04, color=color)
            lab = MathTex(label, font_size=28, color=color).next_to(ring, DOWN, buff=0.1)
            return VGroup(ring, zero, needle, hub, lab)

        DX1, DX2, DX3 = 1.75, 3.7, 5.7
        c_dial = {n: np.array([DX1, y_mid[n], 0]) for n in NAMES}
        cloud_dials = VGroup(*[dial(c_dial[n], (lambda n=n: phase(n)), rf"\phi_{n}") for n in NAMES])
        pab = np.array([DX2, (y_mid["A"] + y_mid["B"]) / 2, 0])
        pbc = np.array([DX2, (y_mid["B"] + y_mid["C"]) / 2, 0])
        pcurv = np.array([DX3, y_mid["B"], 0])
        GRAD = "#9be564"
        CURV = "#c77dff"
        grad_dials = VGroup(
            dial(pab, lambda: phase("B") - phase("A"), r"\phi_B-\phi_A", GRAD),
            dial(pbc, lambda: phase("C") - phase("B"), r"\phi_C-\phi_B", GRAD),
        )
        curv_dial = dial(pcurv, lambda: phase("A") - 2 * phase("B") + phase("C"),
                         r"\phi_A-2\phi_B+\phi_C", CURV)

        def link(a, b, col):
            d = b - a
            u = d / np.linalg.norm(d)
            return Line(a + 0.5 * u, b - 0.5 * u, color=col, stroke_width=1.5, stroke_opacity=0.6)

        links_g = VGroup(link(c_dial["A"], pab, GRAD), link(c_dial["B"], pab, GRAD),
                         link(c_dial["B"], pbc, GRAD), link(c_dial["C"], pbc, GRAD))
        links_c = VGroup(link(pab, pcurv, CURV), link(pbc, pcurv, CURV))
        heads = VGroup(*[Text(s, font_size=20, color=c).move_to([x, y_mid["C"] + 0.95, 0])
                         for s, c, x in (("each cloud", TEXT, DX1), ("gradients", GRAD, DX2),
                                         ("curvature", CURV, DX3))])
        port_feed = VGroup(*[
            DashedLine(P(kinks(n)[2] + OUT, Z0[n] + V * T / 2) + 0.2 * RIGHT,
                       c_dial[n] + 0.5 * LEFT, dash_length=0.06, stroke_width=1.5,
                       color=DIM) for n in NAMES])

        self.add(ports)
        self.play(FadeIn(cloud_dials), Create(port_feed), FadeIn(heads[0]), run_time=1.0)
        self.wait(0.5)

        rng = np.random.default_rng(3)

        def jitter(n_steps, step=0.18):
            for _ in range(n_steps):
                self.play(noise.animate.set_value(noise.get_value() + rng.normal(0, 0.55)),
                          run_time=step, rate_func=smooth)

        # ---- laser phase noise alone: all needles move together
        new_cap = self.caption("Laser phase noise enters every cloud identically")
        self.play(ReplacementTransform(cap, new_cap), run_time=0.5)
        cap = new_cap
        jitter(8)
        self.wait(0.3)

        # ---- add a signal that varies along the baseline
        new_cap = self.caption("A signal that varies along the baseline spreads the phases")
        self.play(ReplacementTransform(cap, new_cap), run_time=0.5)
        cap = new_cap
        self.play(sig.animate.set_value(1.0), noise.animate.set_value(noise.get_value() - 0.4),
                  run_time=1.5)
        jitter(5)
        self.wait(0.3)

        # ---- gradients: noise-free
        new_cap = self.caption("Adjacent pairs: two gradiometers, laser noise cancels")
        self.play(ReplacementTransform(cap, new_cap), Create(links_g), FadeIn(grad_dials),
                  FadeIn(heads[1]), run_time=1.0)
        cap = new_cap
        jitter(8)
        self.wait(0.3)

        # ---- second difference
        new_cap = self.caption("The third cloud adds a second difference: curvature of the signal")
        self.play(ReplacementTransform(cap, new_cap), Create(links_c), FadeIn(curv_dial),
                  FadeIn(heads[2]), run_time=1.0)
        cap = new_cap
        jitter(10)
        self.wait(1.5)

    # ------------------------------------------------------------ helpers
    @staticmethod
    def caption(s):
        return Text(s, font_size=22, color=TEXT).move_to([1.6, -3.62, 0])

    @staticmethod
    def caption_tex(s):
        return Tex(s, font_size=30, color=TEXT).move_to([1.6, -3.62, 0])
