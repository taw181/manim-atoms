"""Phase drawn as a clock hand: hands, dials, output ports and the phase budget.

The pieces the clock-phase scenes and the gradiometer share: a hand on each
arm that turns while that arm is excited, a dial that reads the angle between
two hands, the two output ports the last pulse splits the atoms between, and
the phase budget that names which terms the measurement keeps.
"""

import numpy as np
from manim import *

from aionanim.style import *
from aionanim.tools.primitives import draw_legs, make_atom, make_guide
from aionanim.tools.spacetime import run_to


# --- phase, drawn as a clock hand -----------------------------------------
# The clock is the whole interferometer, not either arm on its own. The
# oscillator is the Sr clock transition at omega_A, and the pulses start and
# stop a Ramsey comparison against it -- that is what makes this an atom
# *clock* interferometer.
#
# A single arm is not a clock. Between pulses each arm is in a definite
# internal state, one in |e> and the other in |g>, swapped at the mirror, and
# an energy eigenstate does not tick: its phase e^{-iEt/hbar} only means
# something relative to another state. A hand that turns "only in |e>" is
# bookkeeping with E_g set to zero, showing the phase of |e> relative to |g>.
# What is measured is omega_A times the *difference* in the two arms' time
# spent excited, and that quantity belongs to both arms together.
#
# The hands are still exactly the lab-frame phase, which is why the drawing
# works. Each pulse writes omega_L * t_emission, fixed by when the laser
# fired rather than when the pulse arrived, so with equally spaced pulses the
# laser terms cancel between the arms; on resonance what is left is
# omega_A * [(t2'-t1') - (t3'-t2')] in arrival times. Two arms that have
# spent equal time up there land their hands on top of each other -- the null
# a gradiometer sits on, and what a gravitational wave breaks by moving those
# arrival times.
CLOCK_TURNS = 1.5  # turns of a hand per interrogation time T

# the explainer's own geometry: one interferometer, low and left, leaving the
# upper right for a dial big enough to read
CP_T0 = -6.2  # far enough left that the output ports clear the dial
CP_T = 2.8  # the same T as the gradiometer, so the hands turn at the same rate
CP_Z = -2.4
CP_ARM = 1.7
CP_SLOPE = CP_ARM / CP_T  # the kicked legs' climb, which the excited port keeps
# How far the output ports run past the last pulse: far enough that the two
# port atoms, which part only at CP_SLOPE, end up more than an atom apart
# (CP_OUT * CP_SLOPE against 2 * CLOCK_ATOM_RADIUS) instead of on top of
# each other.
CP_OUT = 1.5
CP_DIAL = np.array([4.6, 0.9, 0.0])
# where the readout goes: the strip under the interferometer's lower leg,
# which is the one part of the frame no pulse column ends in and nothing on
# the crowded right-hand side -- dial, result, port labels -- reaches into.
CP_READOUT = np.array([-4.6, -3.3, 0.0])


def clock_rate(interrogation_time):
    """How fast a hand turns, fixed by how far it should get in one leg."""
    return CLOCK_TURNS * TAU / interrogation_time


def make_clock_hand(atom, phase):
    """A hand riding an atom, pointing at the phase that arm has accumulated.

    Deliberately not part of the atom's own VGroup: every scene here moves an
    atom by its group centre, and folding a turning hand into that group would
    drag the centre around and pull the atom off the trajectory it is drawing.
    """
    length = CLOCK_HAND_RATIO * CLOCK_ATOM_RADIUS

    def follow(hand):
        pivot = atom[0].get_center()
        hand.put_start_and_end_on(
            pivot, pivot + rotate_vector(UP * length, -phase.get_value())
        )

    hand = Line(
        ORIGIN, UP * length, color=CLOCK_HAND_COLOR, stroke_width=CLOCK_HAND_WIDTH
    )
    # placed now rather than when the next animation starts: a slide stop
    # holds on the frame in between, which would show the hand at the origin
    hand.add_updater(follow, call_updater=True)
    return hand


def make_dial(center, caption=None, radius=CLOCK_DIAL_RADIUS):
    """A clock face, for a phase that is too small to read off a moving atom.

    The caption is optional because in a crowded figure the only room left
    under the face is where a phase label from the diagram already sits.
    """
    face = Circle(
        radius=radius, stroke_width=2,
        stroke_color=lighten(GUIDE_COLOR), fill_opacity=0,
    )
    ticks = VGroup(*[
        Line(
            (radius - 0.14 * radius) * rotate_vector(UP, -k * TAU / 12),
            radius * rotate_vector(UP, -k * TAU / 12),
            stroke_width=2, color=lighten(GUIDE_COLOR),
        )
        for k in range(12)
    ])
    dial = VGroup(face, ticks).move_to(center)
    if caption is None:
        return VGroup(dial)
    label = Tex(
        caption, font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR)
    ).next_to(dial, DOWN, buff=0.2)
    return VGroup(dial, label)


def dial_hand(center, phase, color, radius=CLOCK_DIAL_RADIUS):
    """The same phase a clock hand shows, at a size you can actually read."""
    length = radius - 0.16 * radius

    def follow(hand):
        hand.put_start_and_end_on(
            center, center + rotate_vector(UP * length, -phase.get_value())
        )

    hand = Line(
        ORIGIN, UP * length, color=color, stroke_width=CLOCK_HAND_WIDTH + 1
    )
    # placed now rather than when the next animation starts: a slide stop
    # holds on the frame in between, which would show the hand at the origin
    hand.add_updater(follow, call_updater=True)
    return hand


def phase_sweep(center, phase_a, phase_b, radius=CLOCK_DIAL_RADIUS):
    """The angle between two arms' hands: what the interferometer reads out.

    Wrapped into one turn, because a hand that has been round three times and
    a hand that has been round twice and a bit are only distinguishable by
    where they end up.
    """
    gap = (phase_b.get_value() - phase_a.get_value()) % TAU
    sector = AnnularSector(
        inner_radius=0.0,
        outer_radius=radius - 0.3 * radius,
        start_angle=PI / 2 - phase_b.get_value(),
        angle=gap,
        color=AREA_COLOR,
        fill_opacity=CLOCK_SWEEP_OPACITY,
        stroke_width=0,
    )
    return sector.move_arc_center_to(center), gap


def ground_share(phase_a, phase_b):
    """The share of the atoms the last pulse leaves in |g, p>.

    The same angle phase_sweep draws, read as a population instead of as a
    sector: P = (1 + cos Phi) / 2. Wrapped into one turn for the same reason
    the sector is -- a hand that has been round an extra time is in the same
    place, and the ports cannot tell the two apart either.
    """
    gap = (phase_b.get_value() - phase_a.get_value()) % TAU
    return 0.5 * (1 + np.cos(gap))


def fire_vertical_pulse(scene, x, hits):
    """One pulse climbing the diagram at time `x`, flashing what it crosses.

    A bare worldline, as in the gradiometer, but vertical: nothing in this
    scene turns on the light travel time, and both arms share a column, so one
    pulse reaches them at the same instant -- which is what makes the two legs
    equal and the null exact. It stops at the topmost atom it acts on rather
    than running off the top, because there is nothing above to draw it for.
    """
    hits = sorted(hits, key=lambda m: m.get_center()[1])
    y = -config.frame_y_radius - 0.3
    drawn = []
    for atom in hits:
        y_next = atom.get_center()[1]
        segment = Line(
            [x, y, 0], [x, y_next, 0],
            color=LASER_COLOR, stroke_width=PULSE_STROKE_WIDTH,
        )
        scene.play(
            Create(segment), rate_func=linear, run_time=(y_next - y) / PULSE_SPEED
        )
        scene.play(Flash(atom, **FLASH_STYLE), run_time=0.3)
        drawn.append(segment)
        y = y_next
    scene.play(*[FadeOut(m) for m in drawn], run_time=0.3)


def strobe_pulse(scene, clock, x, top, flash_at, on_arrival=None, hold=PULSE_HOLD):
    """fire_vertical_pulse with lab time running.

    The clock geometry has no light travel time -- one pulse reaches both arms
    at the same instant, which is what makes the two legs equal -- so the
    column is not something that climbs. It is an instant: it appears whole at
    the crossing and fades over `hold` of lab time while the atoms carry on
    through it. `top` is where the column stops, the topmost vertex it acts
    on, for the same reason fire_vertical_pulse stops at the topmost atom.

    `on_arrival` is called once lab time is on the pulse and before anything
    is played, which is where whatever the pulse does to the atoms belongs --
    swapping which arm is excited, say. It happens on the instant because the
    pulse does: there is no window here to animate it over.
    """
    column = Line(
        [x, -config.frame_y_radius - 0.3, 0], [x, top, 0],
        color=LASER_COLOR, stroke_width=PULSE_STROKE_WIDTH,
    )
    run_to(scene, clock, x)
    if on_arrival is not None:
        on_arrival()
    scene.add(column)
    run_to(
        scene, clock, x + hold,
        *[Flash(p, run_time=STROBE_FLASH, **FLASH_STYLE) for p in flash_at],
        FadeOut(column),
    )


def ring_around(term, color):
    """An ellipse drawn round one term of an equation."""
    return Ellipse(
        width=term.width + 2 * RING_BUFF,
        height=term.height + 2 * RING_BUFF,
        color=color,
        stroke_width=RING_STROKE_WIDTH,
    ).move_to(term)


def budget_equation(lhs, term_prefix="", font_size=FONT_STATE):
    """The budget with `lhs` on the left, as one expression.

    `term_prefix` goes in front of every term on the right. It is there for
    the difference form: a gradiometer subtracts one interferometer's phase
    from another's, and subtraction distributes over the sum, so every term on
    the right becomes a Delta too. Writing the difference on the left over
    undifferenced terms on the right would just be false.

    One MathTex with the terms as separate substrings: LaTeX still sets it as
    one expression, so the relation lines up, but each term is a submobject
    that can be circled or struck through on its own. The spaces round each
    term are wider than a ring stands off it (RING_BUFF), so a ring clears the
    = and + on either side. Whatever the left-hand side is,
    it stays a single substring, so the terms keep the same indices.
    """
    def term(name, trailing=r"\;\;"):
        return r"\;\;" + term_prefix + r"\Phi_{\text{" + name + r"}}" + trailing

    return MathTex(
        lhs, "=", term("propagation"), "+", term("laser", trailing=""),
        font_size=font_size,
    )


def leg_slope(start, end):
    """How steeply a leg climbs: the rise per unit time from `start` to `end`."""
    return (end[1] - start[1]) / (end[0] - start[0])


def draw_ports(scene, origin, length, p_ground, slope=CP_SLOPE, labels=True,
               extra=()):
    """The two output states the last pulse leaves the atoms in.

    Until that pulse fires the two arms are distinguishable -- one in
    |e, p + hbar k>, the other in |g, p> -- so the phase between them cannot
    show up anywhere. The pulse couples exactly those two states, so each port
    takes an amplitude from both arms and the angle between the hands becomes
    a population: P = (1 +- cos Phi) / 2. `p_ground` is the share that leaves
    in |g, p>; the excited port takes the rest.

    A port that got nothing is drawn as a dashed guide rather than left out,
    because a null only reads as "they all came out here" if the side they did
    not come out of is on the page.

    The excited port carries p + hbar k, the momentum of the kicked leg that
    arrives at `origin`, so it leaves at that leg's `slope` and carries it on
    in a straight line; only the ground port runs flat. Ports are straight
    even where the arms bow with a wave: they only stand for the atoms flying
    out to be imaged, and are not part of the interferometer.

    `labels` names the two ports. A gradiometer turns that off: it closes four
    ports rather than two, the colours already say which state each one is,
    and what its figure is about is the two splits being unequal -- eight
    labels would bury the one thing the frame has to show.

    `extra` is draw_legs' hook, passed straight through. The continuous scenes
    go through fly_ports instead, which is this with the clock kept running.

    Returns what it put on the scene bar the labels -- the atoms, their
    trails, any empty guide -- for live_ports to take over.
    """
    before = set(scene.mobjects)
    empty, legs, tags = port_parts(scene, origin, length, p_ground, slope)
    if len(empty):
        scene.play(FadeIn(empty), run_time=0.5)
    if legs:
        draw_legs(scene, legs, extra=extra)
    drawn = [m for m in scene.mobjects if m not in before]
    if labels:
        scene.play(FadeIn(tags), run_time=0.6)
    return drawn


def port_parts(scene, origin, length, p_ground, slope=CP_SLOPE):
    """The pieces draw_ports is made of: empty guides, legs to fly, labels.

    The atoms that will fly are put on the scene at `origin`; nothing else is.
    """
    empty, legs, tags = VGroup(), [], VGroup()
    for direction, color, p, tex, label_dir in (
        (RIGHT, ATOM_COLOR, p_ground, r"P_g", DOWN),
        (RIGHT + UP * slope, KICKED_COLOR, 1.0 - p_ground, r"P_e", UP),
    ):
        end = origin + direction * length
        # `end` is a bare point, so the buff has to clear the atom that will
        # be sitting on it, not just the point itself.
        label = MathTex(
            tex, font_size=FONT_ANNOTATION, color=lighten(color)
        ).next_to(end, label_dir, buff=CLOCK_ATOM_RADIUS + 0.22)
        if p < PORT_EMPTY:
            empty.add(make_guide(origin, end))
            label.set_opacity(PORT_EMPTY_OPACITY)
        else:
            atom = make_atom(color, radius=CLOCK_ATOM_RADIUS, opacity=p)
            scene.add(atom.move_to(origin))
            legs.append((atom, origin, end, color))
        tags.add(label)
    return empty, legs, tags


def live_ports(scene, drawn, origin, length, share, slope=CP_SLOPE):
    """Keep ports draw_ports has already flown in step with the phase.

    For a phase picked up after the ports are out -- a scene that shows an
    effect once the readout is on the page, without replaying the sequence.
    `drawn` is what draw_ports returned (the atoms, their trails and any
    empty guide); they are swapped for the same finished picture,
    redrawn every frame from `share`, a function returning the ground share,
    so the split follows the hands as they sweep. Labels, if any, stay put.
    """
    def ports():
        p_ground = share()
        group = VGroup()
        for direction, color, p in (
            (RIGHT, ATOM_COLOR, p_ground),
            (RIGHT + UP * slope, KICKED_COLOR, 1.0 - p_ground),
        ):
            end = origin + direction * length
            if p < PORT_EMPTY:
                group.add(make_guide(origin, end))
            else:
                group.add(
                    Line(origin, end, color=color, **TRAJECTORY_STYLE),
                    make_atom(color, radius=CLOCK_ATOM_RADIUS, opacity=p).move_to(end),
                )
        return group

    scene.remove(*drawn)
    live = always_redraw(ports)
    scene.add(live)
    return live


def fly_ports(scene, ports, length, labels=True, extra=()):
    """draw_ports for a continuous scene: every port in one beat, clock running.

    `ports` is a list of (origin, p_ground, slope), one per interferometer.
    The stop-start version gives an empty port's guide a beat of its own
    before the flight and a gradiometer one beat per cloud; either would be a
    play with lab time stood still, which is the freeze these scenes exist to
    remove. So the guides fade in while the atoms fly, and all of a
    gradiometer's ports leave together -- the two clouds are one instrument
    read out in one frame, and `extra` (the clock, the sectors) runs once.
    """
    empty, legs, tags = VGroup(), [], VGroup()
    for origin, p_ground, slope in ports:
        e, l, t = port_parts(scene, origin, length, p_ground, slope)
        empty.add(*e)
        legs.extend(l)
        tags.add(*t)
    draw_legs(scene, legs, extra=[*extra, *([FadeIn(empty)] if len(empty) else [])])
    if labels:
        scene.play(FadeIn(tags), run_time=0.6)


def readout_equation(center=CP_READOUT):
    """What the angle on the dial becomes once the last pulse has fired.

    The ports are the measurement, and this is the only thing that ties them
    to the phase: a hand that has come round to a different place than its
    partner is not itself an observable, and what a shot of atoms yields is
    the two populations. Deliberately the same relation, wording and size as
    the Mach-Zehnder scene ends on, because it is the same measurement drawn
    twice -- there in momentum states, here in the clock states.
    """
    return MathTex(
        r"P_{g,e} = \tfrac{1}{2}\left(1 \pm \cos\Phi\right)",
        font_size=FONT_ANNOTATION,
    ).move_to(center)


def show_phase_budget(scene, center, laser_struck, laser_label,
                      difference_lhs=None, max_width=None, eq=None):
    """Phi split into its two terms, each marked with what it is worth.

    The separation phase is the third term of the usual decomposition and is
    neglected throughout this talk, so it is not drawn: what is left is the
    phase the atoms accumulate between the pulses, which is the signal --
    omega_A times the difference in time the two arms spend excited -- and the
    phase the light writes in. The laser term is the one that depends on the
    instrument, which is the whole reason for drawing the budget twice:
    circled and noisy in a single interferometer, struck out and cancelled
    once two of them share a laser.

    `difference_lhs` rewrites the whole relation before anything is marked: a
    gradiometer does not read Phi but the difference between two of them, and
    striking a term out as cancelled only means anything once that difference
    is what is being written down. The Delta lands on every term on the right
    as well, because that is where subtracting the two budgets puts it.
    `max_width` is the clear span the result has to fit into. `eq` is a
    budget already on screen, to be marked where it stands rather than written
    again.
    """
    if eq is None:
        eq = budget_equation(r"\Phi").move_to(center)
        scene.play(Write(eq), run_time=1.4)

    if difference_lhs is not None:
        wide = budget_equation(difference_lhs, r"\Delta").move_to(center)
        if max_width is not None and wide.width > max_width:
            wide.scale(max_width / wide.width)
        scene.play(ReplacementTransform(eq, wide), run_time=1.1)
        eq = wide

    # Each label hangs off the equation's own bounding box rather than off its
    # mark, so the two share a baseline however tall each mark is.
    def label(text, color, term):
        return Tex(
            text, font_size=FONT_LEGEND, color=color
        ).next_to(eq, DOWN, buff=0.5).set_x(term.get_x())

    def strike(term):
        # Corner to corner of the term itself: any larger and the tips reach
        # the + signs on either side and read as part of the equation.
        scene.play(
            Create(Cross(
                term, stroke_color=CROSS_COLOR, stroke_width=CROSS_STROKE_WIDTH
            )),
            term.animate.set_opacity(STRUCK_OPACITY),
            run_time=0.9,
        )

    # --- the term the measurement is after -------------------------------
    scene.play(Create(ring_around(eq[2], SIGNAL_COLOR)), run_time=0.6)
    scene.play(FadeIn(label(r"signal", SIGNAL_COLOR, eq[2])), run_time=0.5)

    # --- the one the instrument decides the fate of -----------------------
    if laser_struck:
        strike(eq[4])
        color = STRUCK_COLOR
    else:
        scene.play(Create(ring_around(eq[4], NOISE_COLOR)), run_time=0.6)
        color = NOISE_COLOR
    scene.play(FadeIn(label(laser_label, color, eq[4])), run_time=0.5)
