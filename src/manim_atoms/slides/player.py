"""A phone-friendly web player for a rendered deck.

Reads each slide's manim-slides config in slides/, copies every segment's
video (remuxed with ffmpeg, faststart so it streams) into OUT/v/, and writes
OUT/index.html with the deck inlined as a manifest. Render the deck first,
from the same directory:

    manim-atoms-deck --deck deck.txt render m
    manim-atoms-deck --deck deck.txt player [OUT]      # default: player/
"""

import json
import re
import subprocess
from importlib.resources import files
from pathlib import Path


def pretty(name, names=None):
    """A slide's menu name: ``names[name]`` if given, else its class name in
    words, less the ``Slide``."""
    if names and name in names:
        return names[name]
    words = re.sub(r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", " ",
                   name.removesuffix("Slide"))
    return words[0] + words[1:].lower()


def build_player(deck, out, sections=None, names=None, title="Slides",
                 slides_dir=Path("slides"), first_section="Intro"):
    """Write the player for ``deck`` (a manim_atoms.slides.deck.Deck) to ``out``.

    ``sections`` maps a slide to the section it opens, as the menu groups
    them (a slide belongs to the last section slide before it; the ones
    before any are ``first_section``); ``names`` overrides menu names where a
    class name reads badly once split into words.
    """
    out = Path(out)
    (out / "v").mkdir(parents=True, exist_ok=True)
    sections = sections or {}
    slides, segments = [], []
    section = first_section
    resolution = None
    for number, name in enumerate(deck.slides, start=1):
        config = json.loads((Path(slides_dir) / f"{name}.json").read_text())
        resolution = resolution or config["resolution"]
        section = sections.get(name, section)
        first = len(segments)
        for k, seg in enumerate(config["slides"]):
            dest = f"v/{number:02d}-{k:02d}.mp4"
            subprocess.run(
                ["ffmpeg", "-loglevel", "error", "-y", "-i", seg["file"],
                 "-c", "copy", "-movflags", "+faststart", str(out / dest)],
                check=True,
            )
            segments.append({"src": dest, "slide": number - 1,
                             "loop": seg["loop"], "auto": seg["auto_next"]})
        slides.append({"name": pretty(name, names), "section": section, "first": first,
                       "count": len(segments) - first})
    manifest = {"slides": slides, "segments": segments, "resolution": resolution}
    template = files("manim_atoms.slides").joinpath("player_template.html").read_text(
        encoding="utf-8")
    html = (template
            .replace("/*TITLE*/Slides", title)
            .replace("/*MANIFEST*/null", json.dumps(manifest, separators=(",", ":"))))
    (out / "index.html").write_text(html, encoding="utf-8")
    size = sum(p.stat().st_size for p in (out / "v").glob("*.mp4"))
    print(f"{len(slides)} slides, {len(segments)} segments, {size / 1e6:.1f} MB of video -> {out}")
