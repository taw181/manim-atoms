"""The challenges between the tabletop prototype and a kilometre-scale detector.

A table, one challenge per row: what it is and why it bites, what the
prototype does, and what AION-km asks for. The numbers come from
aionanim.physics.km_scale -- the prototype's own (Baynham et al. 2026),
AION-km's Table 1 (Badurina et al. 2020), and what follows from them.

    uv run manim -ql src/aionanim/scenes/km_challenges.py KmScaleChallenges

The headings come up with the title; each row is then one beat().
"""

import numpy as np
from manim import *

from aionanim.style import *
from aionanim.physics.km_scale import (
    BEST_SR_LMT,
    KM_ATOMS,
    KM_BASELINE,
    KM_CLOUD_SPREAD,
    KM_FIDELITY,
    KM_LMT,
    KM_PULSES,
    KM_T,
    KM_WAIST,
    PROTO_ATOMS,
    PROTO_BASELINE,
    PROTO_POWER,
    PROTO_T,
    PROTO_TEMPERATURE,
    PROTO_WAIST,
)
from aionanim.tools.layout import slide_title

# --- layout ---------------------------------------------------------------
# The left edge of each column, and the heading row's height; rows stack down
# from under the headings, a rule between each.
KC_COLUMNS = (-6.75, -2.0, 2.15)
KC_HEADING_Y = 2.8
KC_ROW_BUFF = 0.16  # between a row and the rule on either side of it
KC_LINE_BUFF = 0.1  # between the lines within a cell


def _sci(x, digits=0):
    """x as TeX a \\times 10^{b}, or 10^{b} when a rounds to 1."""
    b = int(np.floor(np.log10(x)))
    a = round(x / 10**b, digits)
    if a >= 10:
        a, b = a / 10, b + 1
    mantissa = f"{a:.{digits}f}"
    return rf"10^{{{b}}}" if mantissa in ("1", "1.0") else rf"{mantissa}\times10^{{{b}}}"


def _km(x):
    return rf"{x / 1e3:.0f}\,\mathrm{{km}}"


# (challenge, why, prototype, AION-km): each a list of lines of TeX
KC_ROWS = (
    (
        [r"Uniform laser over km"],
        [r"same pulse area and phase", r"for every atom"],
        [rf"$w_0 = {PROTO_WAIST * 1e3:.1f}\,$mm, ${PROTO_POWER * 1e3:.0f}\,$mW"],
        [
            rf"$w_0 \gtrsim {KM_WAIST * 1e2:.0f}\,$cm to stay collimated over ${_km(KM_BASELINE)}$",
            r"$\sim$kW laser power",
        ],
    ),
    (
        [r"Large momentum transfer"],
        [r"signal $\propto n$; every pulse", r"must be near-lossless"],
        [r"$n = 1$", rf"(best in Sr: ${BEST_SR_LMT}\,\hbar k$)"],
        [
            rf"$n = {_sci(KM_LMT)}$: $\sim10^{{{np.log10(KM_PULSES):.0f}}}$ pulses,",
            # rounded down: what each pulse must at least reach
            rf"each $\gtrsim{np.floor(KM_FIDELITY * 1e5) / 1e3:.3f}\%$ fidelity",
        ],
    ),
    (
        [r"Atom number"],
        [r"shot noise $1/\sqrt{N}$ per shot"],
        [rf"$\sim{_sci(PROTO_ATOMS)}$ atoms per shot"],
        [rf"${_sci(KM_ATOMS)}$ atoms per shot", r"or squeezed atoms"],
    ),
    (
        [r"Long free fall"],
        [r"the whole baseline in", r"vacuum and shielded"],
        [
            rf"$T = {PROTO_T * 1e6:.0f}\,\mu$s over ${PROTO_BASELINE * 1e3:.0f}\,$mm",
        ],
        [
            rf"$T = {KM_T:.0f}\,$s over ${_km(KM_BASELINE)}$ of UHV",
            r"and magnetic shield",
        ],
    ),
    (
        [r"Colder atoms"],
        [r"the cloud must stay small", r"against the beam for $2T$"],
        [
            rf"${PROTO_TEMPERATURE * 1e6:.0f}\,\mu$K before velocity slicing",
            rf"(grows ${KM_CLOUD_SPREAD * 1e2:.0f}\,$cm in ${2 * KM_T:.0f}\,$s)",
        ],
        [
            r"$<1\,$nK, so the cloud barely spreads",
        ],
    ),
)


def _cell(lines, font_size, color):
    return VGroup(*(Tex(line, font_size=font_size, color=color) for line in lines)).arrange(
        DOWN, aligned_edge=LEFT, buff=KC_LINE_BUFF
    )


def challenge_row(challenge, why, prototype, target):
    """One row of the table, its cells left-aligned on the columns, tops level."""
    name = VGroup(
        _cell(challenge, FONT_TABLE_NAME, WHITE),
        _cell(why, FONT_TABLE_NOTE, lighten(GUIDE_COLOR)),
    ).arrange(DOWN, aligned_edge=LEFT, buff=KC_LINE_BUFF)
    proto = _cell(prototype, FONT_TABLE_CELL, lighten(GUIDE_COLOR))
    km = _cell(target, FONT_TABLE_CELL, WHITE)
    row = VGroup(name, proto, km)
    for cell, x in zip(row, KC_COLUMNS):
        cell.align_to([x, 0, 0], LEFT).align_to(ORIGIN, UP)
    return row


def rule():
    return Line([KC_COLUMNS[0], 0, 0], [-KC_COLUMNS[0], 0, 0], **TABLE_RULE_STYLE)


class KmScaleChallenges(Scene):
    def beat(self):
        """Hook: a pause between rows. A no-op here."""

    def construct(self):
        title = slide_title(r"Challenges at the km scale")
        headings = VGroup(
            Tex(r"Our prototype", font_size=FONT_TABLE_HEADING, color=lighten(GUIDE_COLOR)),
            Tex(r"AION-km", font_size=FONT_TABLE_HEADING),
        )
        for heading, x in zip(headings, KC_COLUMNS[1:]):
            heading.align_to([x, KC_HEADING_Y, 0], LEFT + UP)  # tops level: cap height

        # each row under the rule below the last
        rows, rules = [], [rule().next_to(headings, DOWN, buff=KC_ROW_BUFF / 2)]
        rules[0].set_x(0)
        for spec in KC_ROWS:
            row = challenge_row(*spec)
            row.shift(rules[-1].get_y() * UP - row.get_top()[1] * UP + DOWN * KC_ROW_BUFF)
            rows.append(row)
            rules.append(rule().set_y(row.get_bottom()[1] - KC_ROW_BUFF))

        # a row comes up with the rule above it: none under the last, which
        # would sit on the citations
        self.play(FadeIn(title), FadeIn(headings), Create(rules[0]), run_time=0.8)
        for i, row in enumerate(rows):
            self.beat()
            above = [Create(rules[i])] if i else []
            self.play(FadeIn(row, shift=UP * 0.15), *above, run_time=0.7)
        self.wait(0.5)
