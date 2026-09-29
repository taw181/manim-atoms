"""References from a BibTeX file, formatted as LaTeX for a slide.

bibtexparser does the parsing and splits each author into BibTeX's first /
von / last / jr parts; this module turns an entry into one line of LaTeX,
under a CiteFormat that says which authors to name, how, and which fields
follow them. Values stay as LaTeX throughout (Zotero's ``{\\"u}`` and
``{{AION-10}}``), since they go straight into a Tex.

    bib = load_bibliography("AION.bib")
    format_reference(bib["baynhamPrototypeDifferentialAtom2026"], SHORT)
    # 'Baynham \\emph{et al.}, Nature \\textbf{654}, 622 (2026)'

A format is a frozen dataclass: vary one with dataclasses.replace, e.g.
``replace(SHORT, keep=("Walker, T",))`` to keep an author through the
et al., or ``replace(SHORT, collaboration="AION Collaboration")``.
"""

import os
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import bibtexparser
from bibtexparser.middlewares import SeparateCoAuthors, SplitNameParts


# --- names ----------------------------------------------------------------
def _strip_braces(text):
    return text.replace("{", "").replace("}", "")


def _first_letter(word):
    """The first letter of a name, as LaTeX: an accented one keeps its
    accent, so S{\\'e}lyan gives S and {\\'E}mile gives {\\'E}."""
    if word.startswith("{\\"):  # a special character, kept whole
        depth = 0
        for i, c in enumerate(word):
            depth += {"{": 1, "}": -1}.get(c, 0)
            if depth == 0:
                return word[: i + 1]
    if word.startswith("{"):
        return _first_letter(word[1:])
    if word.startswith("\\"):  # \"Olaf: the command and its letter
        m = re.match(r"\\[^a-zA-Z]\s*(\{[^}]*\}|.)|\\[a-zA-Z]+\s*(\{[^}]*\}|.)", word)
        return "{" + m.group(0) + "}"
    return word[:1]


def _initials(word):
    """Charles gives C., F. stays F., and Jean-Baptiste gives J.-B."""
    return "-".join(_first_letter(part) + "." for part in word.split("-") if part)


@dataclass(frozen=True)
class Name:
    """One author, in BibTeX's four parts, each a tuple of words."""

    first: tuple[str, ...] = ()
    von: tuple[str, ...] = ()
    last: tuple[str, ...] = ()
    jr: tuple[str, ...] = ()

    @property
    def surname(self):
        return " ".join(self.von + self.last)

    def render(self, form="initials"):
        """``initials`` (C.~F.~A.~Baynham), ``last`` (Baynham) or ``full``
        (Charles F.~A.~Baynham, as the bib spells the first names)."""
        surname = self.surname + (", " + " ".join(self.jr) if self.jr else "")
        if form == "last" or not self.first:
            return surname
        if form == "initials":
            given = "~".join(_initials(w) for w in self.first)
        elif form == "full":
            given = " ".join(self.first)
        else:
            raise ValueError(f"unknown name form {form!r}")
        return f"{given}~{surname}"

    def matches(self, spec):
        """Whether this is the author ``spec`` names: a surname, optionally
        with a first initial after a comma ("Walker" or "Walker, T")."""
        surname, _, initial = (s.strip() for s in spec.partition(","))
        if _strip_braces(self.surname).lower() != surname.lower():
            return False
        first = _strip_braces(" ".join(self.first))
        return not initial or first.lower().startswith(initial.lower())


# --- entries --------------------------------------------------------------
@dataclass(frozen=True)
class Reference:
    """One entry: its authors, and every other field as a LaTeX string."""

    key: str
    kind: str  # article, misc, ...
    authors: tuple[Name, ...]
    fields: dict = field(hash=False)
    more_authors: bool = False  # the list ends "and others", as INSPIRE's do

    def __getitem__(self, name):
        return self.fields[name]

    def get(self, name, default=None):
        return self.fields.get(name, default)


def _reference(entry):
    fields = {f.key.lower(): str(f.value) for f in entry.fields if f.key != "author"}
    authors = [
        Name(tuple(n.first), tuple(n.von), tuple(n.last), tuple(n.jr))
        for n in (entry["author"] if "author" in entry else [])
    ]
    more = bool(authors) and authors[-1] == Name(last=("others",))
    if more:
        authors.pop()
    return Reference(entry.key, entry.entry_type.lower(), tuple(authors), fields, more)


@lru_cache
def _load(path, mtime):  # mtime only keys the cache
    library = bibtexparser.parse_file(
        path, append_middleware=[SeparateCoAuthors(), SplitNameParts()]
    )
    if library.failed_blocks:
        raise ValueError(f"{path}: could not parse {library.failed_blocks}")
    return {e.key: _reference(e) for e in library.entries}


def load_bibliography(path):
    """Every entry in a .bib file, by citation key. Cached until the file
    changes, so a re-export from Zotero is picked up."""
    path = str(Path(path))
    return _load(path, os.path.getmtime(path))


# --- formatting -----------------------------------------------------------
# Each field is (joiner, template): the joiner goes between it and whatever
# comes before, and the template is filled from the entry. A field the entry
# lacks is left out, joiner and all.
TEMPLATES = {
    "authors": (", ", "{authors}"),
    "title": (", ", r"\emph{{{title}}}"),
    "venue": (", ", "{venue}"),
    "journal": (", ", "{journal}"),
    "volume": (" ", r"\textbf{{{volume}}}"),
    "pages": (", ", "{pages}"),
    "arxiv": (", ", "arXiv:{eprint}"),
    "year": (" ", "({year})"),
    "doi": (", ", "doi:{doi}"),
}
# What "venue" is made of: the journal reference for a published paper, the
# arXiv number for a preprint.
JOURNAL_REF = ("journal", "volume", "pages")
PREPRINT_REF = ("arxiv",)


@dataclass(frozen=True)
class CiteFormat:
    """How a reference reads: which authors, in what form, then which fields."""

    fields: tuple[str, ...] = ("authors", "venue", "year")
    name_form: str = "initials"  # initials, last or full; see Name.render
    max_authors: int = 1  # name them all up to this many, else truncate...
    shown_authors: int = 1  # ...to this many, then et al.
    et_al: str = r"\emph{et al.}"
    keep: tuple[str, ...] = ()  # authors named even when truncating (Name.matches)
    highlight: tuple[str, ...] = ()  # authors set in highlight_tex
    highlight_tex: str = r"\textbf{{{}}}"
    collaboration: str | None = None  # stands in for the whole author list
    pages: str = "range"  # range (622--628) or first (622)
    templates: dict = field(default_factory=lambda: dict(TEMPLATES), hash=False)


FULL = CiteFormat(fields=("authors", "venue", "year", "doi"))
SHORT = CiteFormat(name_form="last", pages="first")
AUTHOR_YEAR = CiteFormat(fields=("authors", "year"), name_form="last")


def _join(names, values, templates):
    text = ""
    for name in names:
        joiner, template = templates[name]
        try:
            piece = template.format(**values)
        except KeyError:  # the entry doesn't have it
            continue
        if not text:
            text = piece
            continue
        # an abbreviation's full stop doesn't end a sentence: Sci.\ \textbf{6}
        if text.endswith(".") and joiner.startswith(" "):
            joiner = "\\" + joiner
        text += joiner + piece
    return text


def _list_authors(ref, fmt):
    if fmt.collaboration:
        return fmt.collaboration
    names = ref.authors
    if not names:
        return None

    def render(name):
        text = name.render(fmt.name_form)
        if any(name.matches(s) for s in fmt.highlight):
            text = fmt.highlight_tex.format(text)
        return text

    if len(names) <= fmt.max_authors and not ref.more_authors:
        rendered = [render(n) for n in names]
        if len(rendered) <= 2:
            return " and ".join(rendered)
        return ", ".join(rendered[:-1]) + ", and " + rendered[-1]

    shown = sorted(
        set(range(min(fmt.shown_authors, len(names))))
        | {i for i, n in enumerate(names) if any(n.matches(s) for s in fmt.keep)}
    )
    pieces, previous = [], -1
    for i in shown:
        if i > previous + 1:
            pieces.append(r"\ldots")
        pieces.append(render(names[i]))
        previous = i
    text = ", ".join(pieces)
    if previous < len(names) - 1 or ref.more_authors:
        text += " " + fmt.et_al
    return text


def format_reference(ref, fmt=SHORT):
    """One reference as a line of LaTeX, under ``fmt``."""
    values = dict(ref.fields)
    if "pages" in values and fmt.pages == "first":
        values["pages"] = re.split(r"-+", values["pages"])[0]
    if "journal" in values:
        values["journal"] = re.sub(r"\. ", r".\\ ", values["journal"])
    authors = _list_authors(ref, fmt)
    if authors:
        values["authors"] = authors
    venue = _join(JOURNAL_REF if "journal" in values else PREPRINT_REF,
                  values, fmt.templates)
    if venue:
        values["venue"] = venue
    return _join(fmt.fields, values, fmt.templates)
