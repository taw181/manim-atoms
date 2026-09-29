"""A recorded video shown inside a scene, one frame at a time.

Manim has no video mobject, so the frames are decoded up front (with PyAV,
which manim already depends on) and swapped into one ImageMobject as the
scene runs. Which frame shows is up to the caller -- usually an updater
reading a ValueTracker -- so the video can be paused, held, or driven off
the same clock as the rest of the scene.
"""

import av
import numpy as np
from manim import *


def load_video_frames(path, every=1, crop=None):
    """Every ``every``-th frame of the video at ``path``, as RGBA arrays.

    ``crop`` is ``(top, bottom, left, right)`` in pixels, for trimming a
    border or a burnt-in caption too small to read once the video is shrunk
    into a corner.
    """
    with av.open(str(path)) as container:
        frames = [
            frame.to_ndarray(format="rgba")
            for i, frame in enumerate(container.decode(video=0))
            if i % every == 0
        ]
    if crop is not None:
        top, bottom, left, right = crop
        frames = [f[top:bottom, left:right].copy() for f in frames]
    return frames


class VideoFrame(ImageMobject):
    """An image whose pixels can be swapped for another frame of a video.

    Don't animate its opacity: an animation interpolates the pixel array it
    started with and would paint over the frame swaps. Fade it with a
    background-coloured rectangle drawn on top instead.
    """

    def __init__(self, frames, **kwargs):
        super().__init__(frames[0], **kwargs)
        self.frames = frames
        self.index = 0

    def show(self, index):
        """Show frame ``index``, clamped to the frames there are."""
        index = int(np.clip(index, 0, len(self.frames) - 1))
        if index != self.index:
            self.pixel_array = self.frames[index].copy()
            self.orig_alpha_pixel_array = self.pixel_array[:, :, 3].copy()
            self.index = index
        return self
