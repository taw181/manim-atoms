"""What the hologram scenes share: the mask and focal-plane pictures' sizes,
the spots of an array in the hologram's units, the array's mask at each
step of its iteration, a bar chart of trap brightnesses or mode amplitudes,
and light traced through thin lenses.

The numbers are core.holography's and the pictures core.optics'; this is
the tweezer scenes' layout of them.
"""

import numpy as np
from manim import *

from manim_atoms.tweezers.style import *
from manim_atoms.core.holography import far_field, spot_phase, wgs_step

# --- the hologram's sampling -------------------------------------------------
HG_N = 128  # pixels across the mask: fine enough that a grating's steps do not show
HG_PAD = 4  # focal-plane pixels per diffraction limit
HG_VIEW = 14  # the focal plane is shown out to this many diffraction limits
HG_SPACING = 4  # between neighbouring spots: clear of each other's rings
HG_GAMMA = 0.6  # lifts faint light (ghost spots, an aberrated spot's skirt) into view
HG_SEED = 1  # of the spots' starting phases


def grid_spots(rows, cols, spacing=HG_SPACING):
    """The (rows * cols, 2) spots of a square array about the axis, in
    diffraction limits, row by row from the top left."""
    return np.array([[(c - (cols - 1) / 2) * spacing, ((rows - 1) / 2 - r) * spacing]
                     for r in range(rows) for c in range(cols)], dtype=float)


def spots_from_sites(xy, pitch, spacing=HG_SPACING):
    """Trap positions in scene units as spots in diffraction limits: traps a
    ``pitch`` apart are ``spacing`` diffraction limits apart."""
    return np.asarray(xy, dtype=float) / pitch * spacing


def starting_mask(x, y, spots):
    """The mask an array's hologram starts from: the sum of its spots'
    gratings, each with a random phase."""
    phases = np.random.default_rng(HG_SEED).uniform(0, TAU, len(spots))
    return spot_phase(x, y, spots, phases)


def iterate_hologram(x, y, amplitude, spots, steps):
    """Weighted Gerchberg-Saxton from the starting mask: (the mask before
    each step, the spots' intensities under each of those masks)."""
    mask, weights = starting_mask(x, y, spots), np.ones(len(spots))
    masks, intensities = [], []
    for _ in range(steps + 1):
        masks.append(mask)
        mask, weights, lit = wgs_step(mask, weights, amplitude, x, y, spots)
        intensities.append(lit)
    return masks, intensities


def focal_view(phase, amplitude, view=HG_VIEW, pad=HG_PAD):
    """The middle of the focal plane a mask makes, out to ``view`` diffraction
    limits either side of the axis: what a FocalImage is painted from."""
    image = far_field(phase, amplitude, pad)
    centre, half = image.shape[0] // 2, int(round(view * pad))
    return image[centre - half:centre + half + 1, centre - half:centre + half + 1]


def framed(image):
    """A thin frame round a picture, so it reads as set into the slide."""
    return SurroundingRectangle(image, buff=0, **IMAGE_BORDER_STYLE)


def panel_label(text, panel, direction=UP):
    """A picture's label, in grey beside it."""
    return Tex(text, font_size=FONT_STEP, color=STEP_COLOR).next_to(panel, direction, buff=0.2)


def bar_chart(values, full, width, height, gap=0.25):
    """A bar per value on a baseline, ``width`` across, a value of ``full``
    drawn ``height`` tall, with its lower left corner at the origin.
    Negative values hang below the baseline. Returns VGroup(baseline, bars)."""
    values = np.asarray(values, dtype=float)
    slot = width / len(values)
    bars = VGroup()
    for i, value in enumerate(values):
        tall = height * value / full
        bar = Rectangle(width=slot * (1 - gap), height=max(abs(tall), 1e-3), stroke_width=0,
                        fill_color=BAR_COLOR, fill_opacity=1)
        bar.move_to([slot * (i + 0.5), tall / 2, 0])
        bars.add(bar)
    return VGroup(Line(ORIGIN, RIGHT * width, **BAR_BASELINE_STYLE), bars)


def trace_ray(height, slope, start, lenses, end):
    """A paraxial ray through thin lenses: it leaves x = ``start`` at
    ``height`` above the axis with ``slope``, and each lens (x, focal length)
    it meets before x = ``end`` turns it by -height / f. Returns the (x,
    height) at the start, at each lens and at the end."""
    x, points = start, [(start, height)]
    for at, focal in sorted(lenses):
        if not start < at < end:
            continue
        height += slope * (at - x)
        slope -= height / focal
        x = at
        points.append((x, height))
    points.append((end, height + slope * (end - x)))
    return points


def beamlet(half_width, slope, start, lenses, end, axis, opacity, color=TWEEZER_COLOR):
    """A beam ``half_width`` either side of its chief ray, leaving x =
    ``start`` on the optical axis with ``slope`` and traced through
    ``lenses`` to ``end``: the band between its two edge rays. ``axis`` is
    the scene y of the optical axis."""
    upper = trace_ray(half_width, slope, start, lenses, end)
    lower = trace_ray(-half_width, slope, start, lenses, end)
    corners = [[x, axis + h, 0] for x, h in upper] + [[x, axis + h, 0] for x, h in lower[::-1]]
    return Polygon(*corners, stroke_width=0, fill_color=color, fill_opacity=opacity)
