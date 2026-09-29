"""The furniture of a static slide: a heading, a list, a picture, a slot.

For the slides between the animations -- the title, the contents, the
photographs and the figures -- so that they share the animations' heading
position, type sizes and background rather than each laying itself out.
"""

import numpy as np
from manim import *
from PIL import Image

from aionanim.style import *


def slide_title(text):
    """A slide's heading, top left, where every animation puts its own."""
    return Tex(text, font_size=FONT_TITLE).to_corner(UL)


def load_image(path, height=None, width=None, lift=False):
    """An image file as an ImageMobject, sized by height or width.

    Transparency is kept, so a logo drawn for a dark page sits straight on
    the background. `lift` raises every pixel to at least the background
    colour, the way MergerOnSensitivityPlot shows LIGO's figure: an image
    with a black surround then has no visible edge against the page.
    """
    pixels = np.asarray(Image.open(path).convert("RGBA")).copy()
    if lift:
        floor = np.array(color_to_int_rgb(PLOT_BACKGROUND), dtype=np.uint8)
        pixels[..., :3] = np.maximum(pixels[..., :3], floor)
    image = ImageMobject(pixels)
    if height is not None:
        image.height = height
    if width is not None:
        image.width = width
    return image


def image_point(image, px, py):
    """Pixel (px, py) of an ImageMobject, counted from its upper left, on screen."""
    rows, cols = image.pixel_array.shape[:2]
    return image.get_corner(UL) + [px / cols * image.width, -py / rows * image.height, 0]


def numbered_list(items, font_size=FONT_CONTENTS, buff=0.45):
    """1. first, 2. second, ... with the numbers in a column of their own."""
    rows = VGroup()
    for i, item in enumerate(items, start=1):
        number = Tex(f"{i}.", font_size=font_size, color=lighten(GUIDE_COLOR))
        rows.add(VGroup(number, Tex(item, font_size=font_size)))
    number_width = max(row[0].width for row in rows)
    for row in rows:
        row[1].next_to(row[0], RIGHT, buff=0.3 + number_width - row[0].width)
    rows.arrange(DOWN, buff=buff, aligned_edge=LEFT)
    return rows


def placeholder_frame(width, height, label):
    """A dashed slot, labelled, for a figure that has yet to be dropped in."""
    frame = DashedVMobject(
        RoundedRectangle(width=width, height=height, corner_radius=0.15),
        num_dashes=int(2 * (width + height) / (2 * PLACEHOLDER_STYLE["dash_length"])),
    ).set_stroke(
        color=PLACEHOLDER_STYLE["color"],
        width=PLACEHOLDER_STYLE["stroke_width"],
        opacity=PLACEHOLDER_STYLE["stroke_opacity"],
    )
    text = Tex(label, font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR))
    return VGroup(frame, text.move_to(frame))
