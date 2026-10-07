"""Render, present or convert a deck of manim-slides slides.

    manim-atoms-deck --deck talk/deck.txt --slides talk/slides.py render [-j N] [-f FPS] [l|m|h] [Slide ...]
    manim-atoms-deck --deck talk/deck.txt present
    manim-atoms-deck --deck talk/deck.txt --html talk.html html
    manim-atoms-deck --deck talk/deck.txt player [OUT]

render: every slide in the deck, or just those named, at quality l, m or h
(default h); -j N renders N slides at once, one process each (Cairo renders on
one core), logging to media/deck_logs/<Slide>.log; -f sets the frame rate,
default 30 (l keeps its 15). present and html take the whole deck in order;
player builds a phone-friendly web player from the rendered slides.

Run it from the project root, so the project's manim.cfg applies. The deck
file is described in manim_atoms.slides.deck; --slides names the file its
unqualified slides come from.
"""

import argparse
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from manim_atoms.slides.deck import load_deck

QUALITIES = {"l", "m", "h", "p", "k"}
# manim's rich output is UTF-8; without this a Windows child writing to a log hits cp1252.
ENV = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}


def manim_slides(*args, **kwargs):
    """Run manim-slides with this interpreter, so it sees the same packages."""
    return subprocess.run(
        [sys.executable, "-m", "manim_slides", *map(str, args)], env=ENV, **kwargs
    ).returncode


def render(deck, main, jobs, fps, args):
    """Render ``deck``'s slides (``args``: [l|m|h] [Slide ...]), ``jobs`` at a time."""
    quality = args.pop(0) if args and args[0] in QUALITIES else "h"
    # 30 fps unless asked otherwise: slide animations don't need 60, and
    # it halves the frames at h. l keeps its own 15.
    fps = fps or (15 if quality == "l" else 30)
    slides = args or list(deck.slides)

    def file_of(slide):
        if main is None and slide not in deck.files:
            sys.exit(f"--slides is needed to render {slide}")
        return deck.file_of(slide, main).as_posix()

    # -q h, not -qh: manim-slides reads the h of -qh as --help.
    quality_args = ["-q", quality, "--fps", fps]
    if jobs == 1:
        # one manim-slides run per file, in the order the files first come up
        rc = 0
        for path in dict.fromkeys(map(file_of, slides)):
            named = [s for s in slides if file_of(s) == path]
            rc = manim_slides("render", *quality_args, path, *named) or rc
        return rc

    # one process per slide, each logging to its own file rather than interleaving
    logs = Path("media") / "deck_logs"
    logs.mkdir(parents=True, exist_ok=True)

    def render_one(slide):
        log = logs / f"{slide}.log"
        with open(log, "wb") as out:
            rc = manim_slides("render", *quality_args, file_of(slide), slide,
                              stdin=subprocess.DEVNULL, stdout=out, stderr=subprocess.STDOUT)
        print(f"done    {slide}" if rc == 0 else f"FAILED  {slide}  (see {log.as_posix()})",
              flush=True)
        return rc == 0

    with ThreadPoolExecutor(jobs) as pool:
        ok = all(list(pool.map(render_one, slides)))
    return 0 if ok else 1


def main(argv=None):
    """The manim-atoms-deck command: render, present, html or player."""
    parser = argparse.ArgumentParser(
        prog="manim-atoms-deck", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("command", choices=["render", "present", "html", "player"])
    parser.add_argument("--deck", type=Path, default=Path("deck.txt"),
                        help="the deck file (default deck.txt)")
    parser.add_argument("--slides", type=Path,
                        help="the file the deck's unqualified slides come from")
    parser.add_argument("--html", type=Path, help="html: the file to write (default <deck>.html)")
    parser.add_argument("-j", type=int, default=1, metavar="N", help="render: N slides at once")
    parser.add_argument("-f", type=float, metavar="FPS",
                        help="render: frame rate (default 30; l keeps its 15)")
    parser.add_argument("args", nargs="*", help="render: [l|m|h] [Slide ...]; player: [OUT]")
    opts = parser.parse_args(argv)
    deck = load_deck(opts.deck)

    if opts.command == "render":
        return render(deck, opts.slides, opts.j, opts.f, opts.args)
    if opts.command == "present":
        return manim_slides("present", *deck.slides)
    if opts.command == "html":
        out = opts.html or Path(opts.deck.stem + ".html")
        return manim_slides("convert", *deck.slides, out, "--to", "html", "--one-file")
    from manim_atoms.slides.player import build_player

    build_player(deck, Path(opts.args[0]) if opts.args else Path("player"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
