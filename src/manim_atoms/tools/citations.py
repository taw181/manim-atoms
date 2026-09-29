"""A citation as a line on a slide.

citation() turns references (aionanim.bibliography entries, or LaTeX
strings already formatted) into small grey lines, one per reference;
place_citation() puts them in the footer, bottom left. A slide that wants its
citation elsewhere, under a figure say, calls citation() and places it itself.
labelled_citation() is the compact form for a slide drawing on many papers:
"LIGO: Aasi et al. (2015) . LISA: ...", run on over as few lines as fit.
"""

from manim import *

from aionanim.bibliography import AUTHOR_YEAR, SHORT, Reference, format_reference
from aionanim.style import *


def citation(*refs, fmt=SHORT, numbered=False, font_size=FONT_CITATION,
             color=CITATION_COLOR, max_width=CITATION_MAX_WIDTH):
    """One line per reference, left aligned, shrunk to fit ``max_width``.

    Each of ``refs`` is a Reference, formatted under ``fmt``, or a LaTeX
    string used as it is. ``numbered`` puts [1], [2], ... in front.
    """
    lines = VGroup()
    for n, ref in enumerate(refs):
        text = format_reference(ref, fmt) if isinstance(ref, Reference) else ref
        if numbered:
            text = f"[{n + 1}] {text}"
        # \mbox: Tex's default environment would wrap a line this long
        lines.add(Tex(rf"\mbox{{{text}}}", font_size=font_size, color=color))
    lines.arrange(DOWN, aligned_edge=LEFT, buff=CITATION_LINE_BUFF)
    if lines.width > max_width:
        lines.scale_to_fit_width(max_width)
    lines.set_stroke(**CITATION_OUTLINE, background=True)
    return lines


def labelled_citation(items, fmt=AUTHOR_YEAR, font_size=FONT_CITATION,
                      color=CITATION_COLOR, max_width=CITATION_MAX_WIDTH):
    """``items`` are (label, refs) pairs, refs one reference or a list of
    them (Reference or LaTeX string, as for citation()): each becomes
    "label: refs", and they run on, separated, onto as few lines as keep
    within ``max_width``."""
    pieces = []
    for label, refs in items:
        if isinstance(refs, (Reference, str)):
            refs = [refs]
        body = ", ".join(
            format_reference(r, fmt) if isinstance(r, Reference) else r for r in refs
        )
        pieces.append(f"{label}: {body}")

    def width(line):
        return Tex(rf"\mbox{{{line}}}", font_size=font_size).width

    lines, current = [], []
    for piece in pieces:
        if current and width(CITATION_SEPARATOR.join(current + [piece])) > max_width:
            lines.append(current)
            current = []
        current.append(piece)
    lines.append(current)
    return citation(*[CITATION_SEPARATOR.join(line) for line in lines],
                    font_size=font_size, color=color, max_width=max_width)


def place_citation(mob, corner=DL):
    """``mob`` in a corner of the slide: by default the footer, bottom left,
    its last line just above the progress bar. The bottom right keeps clear
    of the slide number; on the right the lines are right aligned."""
    x = config.frame_x_radius - CITATION_EDGE_BUFF
    if corner[0] > 0:
        for line in mob:
            line.align_to(mob, RIGHT)
        if corner[1] < 0:
            x = config.frame_x_radius - CITATION_NUMBER_CLEARANCE
    y = (config.frame_y_radius - CITATION_EDGE_BUFF if corner[1] > 0
         else -config.frame_y_radius + CITATION_BOTTOM)
    return mob.move_to([x if corner[0] > 0 else -x, y, 0], aligned_edge=corner)
