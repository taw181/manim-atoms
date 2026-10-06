"""The Ramsey-Borde interferometer: four pi/2 pulses, two closed loops,
four output ports.

Borde's optical Ramsey geometry (Phys. Lett. A 140, 10 (1989)): two pi/2
pulses from one side, T apart, then after a dark time T' two more from the
other side, T apart again. Every pulse splits every arm it crosses, so after
three of them eight paths are in flight. Only four of them close, in two
loops, and each loop leaves by two ports of its own: four ports carrying a
fringe, in four different momentum states.

Counter-propagating pairs are the point of the geometry: the first-order
Doppler shift k v the first pair writes in, the second writes back out, so
an atomic beam with a spread of velocities still gives one fringe. What is
left is the photon recoil, and it has opposite signs in the two loops: the
upper one, whose arms spend T' in |e>, rings at Delta = -omega_r, the lower,
whose arms spend it in |g>, at Delta = +omega_r -- the recoil doublet. Since
both arms of a loop share one state through T', T' drops out of both phases.
"""

import numpy as np
from manim import *

from manim_atoms.interferometry.style import *
from manim_atoms.core.primitives import (
    draw_legs,
    make_atom,
    make_guide,
    momentum_arrow,
    state_label,
)
from manim_atoms.interferometry.tools.ramsey_borde import (
    beamsplitter_tree,
    sweep_pulse,
)

# --- Ramsey-Borde geometry ------------------------------------------------
# Space-time again: x is time (or, for Borde's atomic beam crossing four
# laser beams, distance along the beam -- the same picture), y is position
# along the laser axis. A recoil climbs RB_SLOPE per unit x rather than at 45
# degrees, because the top port carries 2 hbar k and has to stay on the page.
# T' is longer than T so that, at the third pulse, the two loops' arms sit at
# four distinct heights (0, T, T', T + T' recoils) rather than two on top of
# each other.
RB_T = 2.2  # between the two pulses of a pair
RB_TP = 3.4  # T', the dark time between the pairs
RB_X1 = -5.0  # the first pulse
RB_PULSE_X = (RB_X1, RB_X1 + RB_T, RB_X1 + RB_T + RB_TP, RB_X1 + 2 * RB_T + RB_TP)
RB_FROM_BELOW = (True, True, False, False)  # +k, +k, -k, -k
RB_Z = -2.3  # where the atom comes in
RB_SLOPE = 0.5  # rise per unit x per photon recoil
RB_OUT = 1.6  # how far the output ports run past the last pulse
RB_START = np.array([RB_X1, RB_Z, 0.0])
RB_ENTRY = np.array([-config.frame_x_radius + 0.2, RB_Z, 0.0])

RB_RECOIL_LENGTH = 0.5  # short: at the third pulse four arms share a column
RB_AXIS_Y = -config.frame_y_radius + 0.25  # the timing axis along the bottom
RB_TICK = 0.09
RB_CAPTION_BELOW_Y = -config.frame_y_radius + 0.95  # pulses from below
RB_CAPTION_ABOVE_Y = config.frame_y_radius - 0.4  # pulses from above
# The phase labels sit where only their own loop is: the lower loop's just
# before the third pulse, after the upper loop's lower arm has climbed out of
# it; the upper loop's just after it, between that arm and the diagonal.
RB_PHI_LOWER = np.array([RB_PULSE_X[2] - 0.6, RB_Z + 0.5 * RB_SLOPE * RB_T, 0.0])
RB_PHI_UPPER = np.array([
    RB_PULSE_X[2] + 0.45,
    RB_Z + RB_SLOPE * (RB_TP + 0.5 * RB_T + 0.45 * 1.5),
    0.0,
])

STATE_COLORS = {"g": ATOM_COLOR, "e": KICKED_COLOR}


def rb_ket(state, n):
    """|g, p + 2 hbar k>, |e, p - hbar k> and so on, in the state's colour."""
    if n == 0:
        mom = r"p"
    else:
        size = "" if abs(n) == 1 else str(abs(n))
        mom = rf"p {'+' if n > 0 else '-'} {size}\hbar k"
    return state_label(rf"|{state},\, {mom}\rangle", STATE_COLORS[state], FONT_LEGEND)


class RamseyBorde(Scene):
    """pi/2 - pi/2 from below, T', pi/2 - pi/2 from above: two closed loops,
    four output ports.

    Stops (beat) once the timing and the atom's way in are laid out; after
    each pulse and the legs it launches; once the last pulse has sent the four
    ports out and they are labelled; after each loop is shaded with its
    phase; and on the readout.
    """

    def beat(self):
        """The pause after each step: nothing here, a click on the slide version."""

    def construct(self):
        tree = beamsplitter_tree(
            list(zip(RB_PULSE_X, RB_FROM_BELOW)), RB_START, RB_SLOPE
        )
        open_paths = set(tree["open"])
        closed_paths = [m for m in tree["paths"] if m not in open_paths]
        arm_state = {"": "g"}

        # --- 1. setup ----------------------------------------------------
        title = Tex(r"Ramsey--Bord\'e interferometer", font_size=FONT_TITLE)
        title.to_corner(UL)
        note = Tex(
            r"colour is the internal state; slope is momentum",
            font_size=FONT_LEGEND,
            color=lighten(GUIDE_COLOR),
        ).next_to(title, DOWN, buff=0.2).align_to(title, LEFT)
        # the key beside the title, leaving the triangle above the diagonal free
        # for the readout
        legend = self.make_legend().next_to(title, RIGHT, buff=0.7)
        axis = self.make_time_axis()
        guide = make_guide(RB_ENTRY, RB_START)
        self.play(*[FadeIn(m) for m in (title, note, legend, axis, guide)], run_time=1.0)
        self.beat()

        # --- 2. the atom comes in ---------------------------------------
        atom = make_atom().move_to(RB_ENTRY)
        self.play(FadeIn(atom, scale=0.5), run_time=0.4)
        draw_legs(self, [(atom, RB_ENTRY, RB_START, ATOM_COLOR)])
        atoms = {"": atom}
        open_trails = VGroup()

        # --- 3. three beamsplitters, every arm split by each ------------
        for k, step in enumerate(tree["steps"]):
            arrows = []

            def stop(split):
                parent, point, stay, kicked, kstate, dv = split

                def on_hit():
                    self.remove(atoms.pop(parent))
                    arm_state[stay], arm_state[kicked] = arm_state[parent], kstate
                    for name in (stay, kicked):
                        # faint if no closed path runs on from here
                        faint = not any(m.startswith(name) for m in closed_paths)
                        opacity = OPEN_ATOM_OPACITY if faint else SUPERPOSITION_OPACITY
                        atoms[name] = make_atom(STATE_COLORS[arm_state[name]], opacity=opacity)
                        self.add(atoms[name].move_to(point))
                    arrow = self.recoil_arrow(point, dv, labelled=k == 0)
                    arrows.append(arrow)
                    return [Flash(point, **FLASH_STYLE), *self.grow(arrow)]

                return (point[1], on_hit)

            caption = self.pulse_caption(step["x"], step["from_below"])
            sweep_pulse(
                self, step["x"], [stop(s) for s in step["splits"]],
                from_below=step["from_below"], extras=[caption],
            )

            closed_legs, extra = [], []
            for name, start, end, state, closed in step["legs"]:
                if closed:
                    closed_legs.append((atoms[name], start, end, STATE_COLORS[state]))
                else:
                    trail = DashedLine(start, end, color=STATE_COLORS[state],
                                       **OPEN_PATH_STYLE)
                    extra += [atoms[name].animate.move_to(end), Create(trail)]
                    open_trails.add(trail)
            draw_legs(self, closed_legs, fade=arrows, extra=extra)
            self.beat()

        # --- 4. the last pulse: two loops close, four ports leave --------
        x4 = RB_PULSE_X[-1]
        open_mobs = VGroup(*open_trails, *[atoms[m] for m in open_paths])
        port_legs, port_tags = [], VGroup()

        def merge(a, b):
            point = tree["paths"][a][-1]

            def on_hit():
                self.remove(atoms.pop(a), atoms.pop(b))
                for name in (a, b):
                    state, n = tree["states"][name]
                    port = make_atom(STATE_COLORS[state], opacity=SUPERPOSITION_OPACITY)
                    self.add(port.move_to(point))
                    end = point + np.array([RB_OUT, RB_OUT * n * RB_SLOPE, 0.0])
                    port_legs.append((port, point, end, STATE_COLORS[state]))
                    port_tags.add(rb_ket(state, n).next_to(end, RIGHT, buff=0.32))
                # the open paths never meet anyone: no fringe, so they go
                # out of the picture with the first flash
                fade = [FadeOut(open_mobs)] if open_mobs in self.mobjects else []
                return [Flash(point, **FLASH_STYLE), *fade]

            return (point[1], on_hit)

        caption = self.pulse_caption(x4, RB_FROM_BELOW[-1])
        loops = tree["loops"]
        # the same mobjects, regrouped to fade as one (and drawn once, not twice)
        self.remove(*open_mobs)
        self.add(open_mobs)
        sweep_pulse(
            self, x4, [merge(a, b) for a, b in loops],
            from_below=RB_FROM_BELOW[-1], extras=[caption],
        )
        draw_legs(self, port_legs)
        self.play(FadeIn(port_tags), run_time=0.7)
        self.beat()

        # --- 5. the two loops, and the phase each one reads --------------
        for (a, b), sign, at in zip(loops, ("-", "+"), (RB_PHI_LOWER, RB_PHI_UPPER)):
            shared = self.state_of(tree, a, 1)  # through T'
            style = RB_UPPER_LOOP_STYLE if shared == "e" else RB_LOWER_LOOP_STYLE
            loop = Polygon(*tree["paths"][a], *reversed(tree["paths"][b]), **style)
            phi = MathTex(rf"\Phi_{sign}", font_size=FONT_PHASE,
                          color=lighten(STATE_COLORS[shared])).move_to(at)
            self.add(loop)
            self.bring_to_back(loop)
            self.play(FadeIn(loop), FadeIn(phi), run_time=0.8)
            self.beat()

        # --- 6. the readout ----------------------------------------------
        readout = VGroup(
            MathTex(r"\Phi_\pm = 2T\,(\Delta \pm \omega_r)", font_size=FONT_ANNOTATION),
            MathTex(r"\omega_r = \frac{\hbar k^2}{2m},\quad \Delta = \omega_L - \omega_0",
                    font_size=FONT_LEGEND),
            MathTex(r"\text{each loop: } P = \tfrac{1}{2}\left(1 \pm \cos\Phi\right)",
                    font_size=FONT_LEGEND),
            Tex(r"recoil doublet at $\Delta = \mp\omega_r$",
                font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR)),
            Tex(r"$\Phi_\pm$ free of $T'$ and of Doppler $kv$",
                font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR)),
        ).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        # under the note, in the empty triangle above the diagonal
        readout.next_to(note, DOWN, buff=0.4).align_to(note, LEFT)
        self.play(Write(readout), run_time=1.6)
        self.wait(2.0)

    # --- helpers ---------------------------------------------------------
    @staticmethod
    def state_of(tree, name, k):
        """The state the path `name` flies in after pulse k (0-based)."""
        return next(leg[3] for leg in tree["steps"][k]["legs"] if leg[0] == name[: k + 1])

    @staticmethod
    def make_legend():
        """|g> and |e>, beside an atom of each colour, on one row."""
        row = VGroup()
        for color, tex in ((ATOM_COLOR, r"|g\rangle"), (KICKED_COLOR, r"|e\rangle")):
            row.add(VGroup(make_atom(color, radius=LEGEND_ATOM_RADIUS),
                           state_label(tex, color, FONT_LEGEND)).arrange(RIGHT, buff=0.18))
        return row.arrange(RIGHT, buff=0.5)

    @staticmethod
    def make_time_axis():
        """The pulse timing along the bottom: a tick per pulse, T, T', T."""
        y = RB_AXIS_Y
        axis = VGroup(Line([RB_PULSE_X[0], y, 0], [RB_PULSE_X[-1], y, 0], **TIME_AXIS_STYLE))
        for x in RB_PULSE_X:
            axis.add(Line([x, y - RB_TICK, 0], [x, y + RB_TICK, 0], **TIME_AXIS_STYLE))
        for (a, b), tex in zip(zip(RB_PULSE_X, RB_PULSE_X[1:]), ("T", "T'", "T")):
            axis.add(MathTex(tex, font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR))
                     .move_to([(a + b) / 2, y + 0.3, 0]))
        return axis

    @staticmethod
    def pulse_caption(x, from_below):
        """pi/2 beside the column, on the side the light comes from, with an
        arrow for which way it travels: +k from below, -k from above."""
        text = MathTex(r"\pi/2", font_size=FONT_ANNOTATION, color=LASER_COLOR)
        k = Arrow(ORIGIN, (UP if from_below else DOWN) * 0.55, **K_ARROW_STYLE)
        group = VGroup(text, k).arrange(RIGHT, buff=0.12)
        y = RB_CAPTION_BELOW_Y if from_below else RB_CAPTION_ABOVE_Y
        return group.move_to([x + 0.2 + group.width / 2, y, 0])

    @staticmethod
    def recoil_arrow(point, dv, labelled=False):
        """The recoil on the arm that made the transition: up for +hbar k,
        down for -hbar k, standing on the atom. Labelled on the first pulse
        only; after that the direction says it."""
        direction = UP if dv > 0 else DOWN
        if labelled:
            return momentum_arrow(point, direction, rf"{'+' if dv > 0 else '-'}\hbar k",
                                  length=RB_RECOIL_LENGTH + 0.2)
        return VGroup(Arrow(point, point + direction * RB_RECOIL_LENGTH,
                            **RECOIL_ARROW_STYLE))

    @staticmethod
    def grow(arrow):
        return [GrowArrow(arrow[0]), *[FadeIn(m) for m in arrow[1:]]]
