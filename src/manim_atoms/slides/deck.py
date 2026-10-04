"""Any manim_atoms scene as a manim-slides slide, and a deck made of them.

A scene marks where a presenter would stop by calling a no-op hook, and the
mixins below turn the hook into a slide break, so a scene needs no changes to
become a slide:

- ``beat()``: Clicks makes it a plain stop. Nothing in those scenes moves
  while they are paused, so there is nothing to loop.
- ``stage_break()``: the sequence scenes' timed hold; LoopingStages loops two
  seconds of it instead, so the cloud keeps moving while a stage is talked
  through.
- ``hold()``: one period of a scene that runs on its own (a field
  oscillating); a slide loops it with ``self.loop(self.hold)``.

A looping stop is still one click: RunsOnIntoLoops plays each stretch
straight on into its loop, and the click moves on from the loop.

A slide is the package scene with a mixin in front, ``class XSlide(Clicks,
SomeScene)``. A talk configures the deck once, by subclassing DeckSlide and
the mixins with its deck file, bibliography and citation look::

    from manim_atoms.slides import deck

    class DeckSlide(deck.DeckSlide):
        DECK = deck.load_deck(Path(__file__).parent / "deck.txt")
        BIB = load_bibliography(Path("refs.bib"))

    class Clicks(deck.Clicks, DeckSlide): ...
    class RunsOnIntoLoops(deck.RunsOnIntoLoops, DeckSlide): ...
    class LoopingStages(deck.LoopingStages, RunsOnIntoLoops): ...

The deck file lists the slides in order, one class name per line, from the
talk's main slides file; ``#`` starts a comment. A line naming a slide with
its file, ``extra_slides/x.py: XSlide`` (relative to the deck file), is
played and rendered in its place but numbered as none of the deck: no footer
number, not counted. ``manim-atoms-deck`` renders, presents and converts it.
"""

from dataclasses import dataclass
from pathlib import Path

from manim import *
from manim_slides import Slide

from manim_atoms.bibliography import AUTHOR_YEAR, SHORT
from manim_atoms.core.citations import citation, labelled_citation, place_citation
from manim_atoms.style import *


# --- the deck file ---------------------------------------------------------
@dataclass(frozen=True)
class Deck:
    """The slides of a deck file, in order. ``files`` maps each slide named
    with its file to that file (relative to the deck file); every other slide
    comes from the talk's main slides file."""

    path: Path
    slides: tuple[str, ...]
    files: dict

    @property
    def numbered(self):
        """The slides that carry a footer number: those from the main file."""
        return [s for s in self.slides if s not in self.files]

    def file_of(self, slide, main):
        """The file ``slide`` renders from, ``main`` unless the deck names one."""
        if slide in self.files:
            return self.path.parent / self.files[slide]
        return Path(main)


def load_deck(path):
    """Read a deck file (see the module docstring)."""
    path = Path(path)
    slides, files = [], {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not (entry := line.split("#")[0].strip()):
            continue
        file, _, slide = entry.rpartition(":")
        slide = slide.strip()
        slides.append(slide)
        if file:
            files[slide] = file.strip()
    return Deck(path, tuple(slides), files)


def cite(bib, *keys):
    """The entries of ``bib`` under these keys, failing on one not in it."""
    missing = [k for k in keys if k not in bib]
    if missing:
        raise KeyError(f"not in the bibliography: {', '.join(missing)}")
    return [bib[k] for k in keys]


# --- the footer ------------------------------------------------------------
def make_footer(number, total):
    """The progress bar along the bottom edge, filled to this slide's place in
    the deck, and the slide's number in the corner above the end of it."""
    width = config.frame_width
    bottom = -config.frame_y_radius + PROGRESS_BAR_HEIGHT / 2
    track = Rectangle(
        width=width,
        height=PROGRESS_BAR_HEIGHT,
        stroke_width=0,
        fill_color=PROGRESS_TRACK_COLOR,
        fill_opacity=1,
    ).move_to([0, bottom, 0])
    fill = (
        Rectangle(
            width=width * number / total,
            height=PROGRESS_BAR_HEIGHT,
            stroke_width=0,
            fill_color=PROGRESS_FILL_COLOR,
            fill_opacity=1,
        )
        .align_to(track, LEFT)
        .set_y(bottom)
    )
    label = Tex(str(number), font_size=FONT_SLIDE_NUMBER, color=SLIDE_NUMBER_COLOR)
    label.next_to(track, UP, buff=0.1).to_edge(RIGHT, buff=0.15)
    label.set_stroke(PLOT_BACKGROUND, width=4, background=True)  # legible over photos
    return VGroup(track, fill, label)


# --- slides ----------------------------------------------------------------
class DeckSlide(Slide):
    """Every slide in a deck: a Slide that stops on its finished frame, with
    the footer (progress bar and slide number) over everything it draws, and
    the references it names in CITE (keys into BIB) bottom left above it:
    one line each, or, if CITE holds (label, key, ...) tuples, run on together
    as "label: Author et al. (year)". CITE_CORNER moves it off something the
    footer would cover.

    A talk sets DECK (from load_deck) and BIB (from
    manim_atoms.bibliography.load_bibliography) on a subclass; without a DECK
    a slide has no footer, and without a CITE no citation.

    Slides are rendered without reversed copies (skip_reversing), so stepping
    back replays a slide forwards.

    SETTLE is how long each slide holds its last frame before it stops.
    Manim only draws an animation's final frame when the next one starts, so
    without it a slide freezes a frame short -- atoms a hair before their
    vertex -- and jumps the rest of the way on the click. Anything over one
    frame at 15 fps will do. Looping slides are left without it: their last
    frame is their first, so the one manim leaves out is the one a loop
    would repeat.

    The footer and citation are foreground mobjects, so they stay on top of
    whatever the scene adds; they are pinned to the frame in a 3D scene, ride
    along with a moving camera, and are kept out of any remove(), since a
    scene may clear the page with remove(*self.mobjects).
    """

    DECK = None
    BIB = {}
    CITE = ()
    CITE_FORMAT = SHORT
    # ...and a slide citing many papers, as (label, key) pairs, run on together
    CITE_LABELLED_FORMAT = AUTHOR_YEAR
    CITE_CORNER = DL
    SETTLE = 0.1
    # no reversed copy of each slide: it costs a re-encode, and stepping back
    # through the deck then replays a slide forwards instead
    skip_reversing = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wait_time_between_slides = self.SETTLE
        self.wait_between_looping_slides = False
        self.furniture = []

    def setup(self):
        super().setup()
        if self.CITE:
            self._pin(place_citation(self.citation(), self.CITE_CORNER))
        name = type(self).__name__
        numbered = self.DECK.numbered if self.DECK else []
        if name in numbered:
            self._pin(make_footer(numbered.index(name) + 1, len(numbered)))

    def cite(self, *keys):
        """This deck's references under these keys."""
        return cite(self.BIB, *keys)

    def citation(self):
        if all(isinstance(c, tuple) for c in self.CITE):
            return labelled_citation(
                [(label, self.cite(*keys)) for label, *keys in self.CITE],
                fmt=self.CITE_LABELLED_FORMAT,
            )
        return citation(*self.cite(*self.CITE), fmt=self.CITE_FORMAT)

    def _pin(self, mob):
        """``mob`` on top, fixed on the screen, and out of reach of remove()."""
        if isinstance(self, ThreeDScene):
            self.add_fixed_in_frame_mobjects(mob)
        elif isinstance(self, MovingCameraScene):
            frame = self.camera.frame  # moves, but never zooms
            offset = mob.get_center() - frame.get_center()
            mob.add_updater(lambda m: m.move_to(frame.get_center() + offset))
        self.add_foreground_mobject(mob)
        self.furniture.append(mob)

    def remove(self, *mobjects):
        return super().remove(*[m for m in mobjects if m not in self.furniture])


class Clicks(DeckSlide):
    """A DeckSlide whose beat() stops and waits for the presenter."""

    def beat(self):
        self.next_slide()


class RunsOnIntoLoops(DeckSlide):
    """A DeckSlide on which each stretch plays straight on into the loop after
    it, so a stage is one click however it is cut: the click starts the stage,
    and its loop holds the screen until the next. (Without auto_next the
    stretch would stop on its last frame and need a click of its own to start
    its loop.)

    auto_next belongs to the segment a next_slide() opens; one with nothing
    before it sets the options of the slide's first segment instead.
    """

    def setup(self):
        super().setup()
        self.next_slide(auto_next=True)

    def loop(self, hold):
        """Loop what hold() plays until the click, then run on into the next."""
        self.next_slide(loop=True)
        hold()
        self.next_slide(auto_next=True)


class LoopingStages(RunsOnIntoLoops):
    """stage_break() loops two seconds of the running stage until the click."""

    def stage_break(self):
        self.loop(lambda: self.wait(2))
