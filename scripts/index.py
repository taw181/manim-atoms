"""Write docs/reference.md from the source, and check docs/index.md against it.

    python scripts/index.py            # check; exits 1 and lists what is wrong
    python scripts/index.py --write    # regenerate docs/reference.md

Everything is read with ``ast``: nothing is imported, so the check needs no
manim, no LaTeX and no virtualenv, and runs in a fraction of a second.

The check fails when:

- docs/reference.md is not what --write would make of the source;
- a public module-level function or class is missing from docs/index.md
  (scene modules: only their Scene classes are required);
- docs/index.md cites a ``manim_atoms`` name that no longer exists;
- a module, or a public module-level function or class, has no docstring.

How docs/index.md cites things: every backticked token that looks like a
dotted Python name is a citation, after anything from ``(`` on is dropped.

- ``core.spacetime`` names a module (``manim_atoms.`` is optional);
- ``core.spacetime.draw_wavy_legs`` names something in it, as does
  ``interferometry.tools.squeezing.BlochView.ring`` a method;
- a bare ``draw_wavy_legs`` or ``BlochView.ring`` is looked up in the
  modules cited on the same line, and must be in one of them -- or, on a
  line that cites no module, anywhere in the package;
- tokens starting ``manim.`` (manim's own names) are left alone, as is
  anything that is not a dotted name (``|g>``, ``uv run ...``, ``-ql``).
"""

import argparse
import ast
import difflib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKAGE = ROOT / "src" / "manim_atoms"
REFERENCE = ROOT / "docs" / "reference.md"
INDEX = ROOT / "docs" / "index.md"

# Layer order, as CLAUDE.md lays the package out, and within a topic the
# order a reader meets its parts in.
LAYERS = ["style", "core", "species", "interferometry", "trapping", "aion",
          "slides", "bibliography", "resources"]
PARTS = ["style", "physics", "tools", "plots", "scenes"]

# Public, but nothing a scene author reaches for: exempt from index coverage.
SKIP = {
    "slides.cli.main",
    "slides.cli.render",
    "slides.cli.manim_slides",
}

SCENE_BASES = {"Scene", "ThreeDScene", "MovingCameraScene", "Slide"}
NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*$")
SECTION = re.compile(r"^# --- (.*?) -*$")


# --- reading the package ----------------------------------------------------

def paragraph(doc):
    """The first paragraph of a docstring, on one line."""
    if not doc:
        return ""
    return " ".join(doc.strip().split("\n\n")[0].split())


class Module:
    def __init__(self, path):
        self.path = path
        rel = path.relative_to(PACKAGE).with_suffix("")
        self.name = ".".join(rel.parts)  # e.g. core.spacetime
        self.source = path.read_text()
        self.tree = ast.parse(self.source)
        self.doc = ast.get_docstring(self.tree)
        self.is_scenes = "scenes" in rel.parts
        self.is_style = rel.name == "style"
        self.functions, self.classes, self.constants = {}, {}, {}
        for node in self.tree.body:
            if isinstance(node, ast.FunctionDef):
                self.functions[node.name] = node
            elif isinstance(node, ast.ClassDef):
                self.classes[node.name] = node
            elif isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for t in targets:
                    if isinstance(t, ast.Name):
                        self.constants[t.id] = node

    def sort_key(self):
        parts = self.name.split(".")
        layer = LAYERS.index(parts[0]) if parts[0] in LAYERS else len(LAYERS)
        part = parts[1] if len(parts) > 1 else ""
        return (layer, PARTS.index(part) if part in PARTS else -1, self.name)

    def public(self):
        """Public top-level functions and classes, in source order."""
        return [n for n in self.tree.body
                if isinstance(n, (ast.FunctionDef, ast.ClassDef))
                and not n.name.startswith("_")]

    def resolves(self, dotted):
        """Whether ``name`` or ``Class.method`` exists in this module."""
        head, _, rest = dotted.partition(".")
        if not rest:
            return head in self.functions or head in self.classes or head in self.constants
        cls = self.classes.get(head)
        if cls is None or "." in rest:
            return False
        return any(isinstance(n, ast.FunctionDef) and n.name == rest for n in cls.body) or any(
            isinstance(n, (ast.Assign, ast.AnnAssign)) and rest in [
                t.id for t in (n.targets if isinstance(n, ast.Assign) else [n.target])
                if isinstance(t, ast.Name)]
            for n in cls.body)


def load_modules():
    mods = [Module(p) for p in PACKAGE.rglob("*.py") if p.name != "__init__.py"]
    return {m.name: m for m in sorted(mods, key=Module.sort_key)}


def scene_classes(modules):
    """Every class that is a Scene, by class name: one whose base is a manim
    scene or another Scene in the package, mixins and all."""
    bases = {name: [ast.unparse(b).split(".")[-1] for b in node.bases]
             for m in modules.values() for name, node in m.classes.items()}
    scenes = set()
    changed = True
    while changed:
        changed = False
        for name, bs in bases.items():
            if name not in scenes and any(b in SCENE_BASES or b in scenes for b in bs):
                scenes.add(name)
                changed = True
    return scenes, bases


def has_construct(name, modules, bases, seen=()):
    for m in modules.values():
        node = m.classes.get(name)
        if node is not None:
            if any(isinstance(n, ast.FunctionDef) and n.name == "construct" for n in node.body):
                return True
            return any(has_construct(b, modules, bases, seen + (name,))
                       for b in bases[name] if b not in seen)
    return False


# --- docs/reference.md ------------------------------------------------------

def signature(node, method=False):
    args = node.args
    if method and args.args and args.args[0].arg in ("self", "cls"):
        args = ast.arguments(posonlyargs=args.posonlyargs, args=args.args[1:],
                             vararg=args.vararg, kwonlyargs=args.kwonlyargs,
                             kw_defaults=args.kw_defaults, kwarg=args.kwarg,
                             defaults=args.defaults)
    return f"{node.name}({ast.unparse(args)})"


def class_settings(node):
    """A class's UPPER_CASE attributes: a scene's configuration knobs."""
    names = []
    for n in node.body:
        targets = n.targets if isinstance(n, ast.Assign) else [n.target] if isinstance(
            n, ast.AnnAssign) else []
        names += [t.id for t in targets if isinstance(t, ast.Name) and t.id.isupper()]
    return names


def methods(node):
    return [n for n in node.body if isinstance(n, ast.FunctionDef)
            and not n.name.startswith("_") and n.name != "construct"]


def style_lines(m):
    """A style module's constants, grouped under its ``# --- section ---`` lines."""
    lines = m.source.splitlines()
    groups, current = [], None
    for i, line in enumerate(lines, start=1):
        sec = SECTION.match(line)
        if sec:
            current = [sec.group(1), []]
            groups.append(current)
            continue
        for name, node in m.constants.items():
            if node.lineno == i and name.isupper():
                if current is None:
                    current = ["", []]
                    groups.append(current)
                current[1].append(name)
    out = []
    for title, names in groups:
        if names:
            label = f"*{title}*: " if title else ""
            out.append(f"- {label}" + ", ".join(f"`{n}`" for n in names))
    return out


def reference(modules):
    scenes, bases = scene_classes(modules)
    out = [
        "# manim_atoms reference",
        "",
        "<!-- Generated by `python scripts/index.py --write` from the source's",
        "docstrings and signatures. Do not edit by hand: edit the docstring and",
        "regenerate. -->",
        "",
        "Every module, and every public name in it, with the first paragraph of",
        "its docstring. To find what to reach for, start at [index.md](index.md);",
        "this page is for looking a name up. Paths are under `manim_atoms`.",
        "",
    ]
    layer = None
    for m in modules.values():
        top = m.name.split(".")[0]
        if top != layer:
            layer = top
            out += [f"## {top}", ""]
        out += [f"### `{m.name}`", "", f"`src/manim_atoms/{m.path.relative_to(PACKAGE)}`"
                + (f" — {paragraph(m.doc)}" if m.doc else ""), ""]
        if m.is_style:
            out += style_lines(m)
        for node in m.public():
            doc = paragraph(ast.get_docstring(node))
            if isinstance(node, ast.FunctionDef):
                out.append(f"- `{signature(node)}`" + (f": {doc}" if doc else ""))
                continue
            kind = "Scene" if node.name in scenes else "class"
            bs = ", ".join(ast.unparse(b) for b in node.bases)
            out.append(f"- {kind} `{node.name}({bs})`" + (f": {doc}" if doc else ""))
            settings = class_settings(node)
            if settings:
                out.append("  - settings: " + ", ".join(f"`{n}`" for n in settings))
            for meth in methods(node):
                mdoc = paragraph(ast.get_docstring(meth))
                out.append(f"  - `.{signature(meth, method=True)}`" + (f": {mdoc}" if mdoc else ""))
            if node.name in scenes and has_construct(node.name, modules, bases):
                out.append(f"  - `uv run manim -ql src/manim_atoms/"
                           f"{m.path.relative_to(PACKAGE)} {node.name}`")
        out.append("")
    return "\n".join(out).rstrip() + "\n"


# --- checks -----------------------------------------------------------------

def module_of(token, modules):
    """(module, rest) for the longest module path ``token`` starts with."""
    token = token.removeprefix("manim_atoms.")
    parts = token.split(".")
    for i in range(len(parts), 0, -1):
        name = ".".join(parts[:i])
        if name in modules:
            return modules[name], ".".join(parts[i:])
    return None, token


def check_index(modules, problems):
    """Resolve every citation in docs/index.md; return what was cited."""
    if not INDEX.exists():
        problems.append(f"{INDEX.relative_to(ROOT)} is missing")
        return set()
    cited = set()
    for lineno, line in enumerate(INDEX.read_text().splitlines(), start=1):
        tokens = [t.split("(")[0].strip() for t in re.findall(r"`([^`]+)`", line)]
        tokens = [t for t in tokens if NAME.match(t) and not t.startswith("manim.")]
        line_mods, bare = [], []
        for t in tokens:
            mod, rest = module_of(t, modules)
            if mod is None:
                bare.append(t)
            elif not rest:
                line_mods.append(mod)
            elif mod.resolves(rest):
                line_mods.append(mod)
                cited.add(f"{mod.name}.{rest.split('.')[0]}")
            else:
                problems.append(f"index.md:{lineno}: `{t}` -- no `{rest}` in {mod.name}")
        for t in bare:
            pool = line_mods or modules.values()
            hits = [m for m in pool if m.resolves(t)]
            if not hits:
                where = ", ".join(m.name for m in line_mods) if line_mods else "the package"
                problems.append(f"index.md:{lineno}: `{t}` -- not in {where}")
            for m in hits:
                cited.add(f"{m.name}.{t.split('.')[0]}")
    return cited


def check(modules):
    problems = []
    if not REFERENCE.exists() or REFERENCE.read_text() != reference(modules):
        old = REFERENCE.read_text().splitlines() if REFERENCE.exists() else []
        diff = list(difflib.unified_diff(old, reference(modules).splitlines(),
                                         "docs/reference.md", "generated", lineterm="", n=0))
        problems.append("docs/reference.md is stale: run `python scripts/index.py --write`"
                        + "".join(f"\n    {d}" for d in diff[2:12]))

    cited = check_index(modules, problems)
    scenes, _ = scene_classes(modules)
    for m in modules.values():
        if not m.doc:
            problems.append(f"{m.name}: no module docstring")
        for node in m.public():
            full = f"{m.name}.{node.name}"
            if not ast.get_docstring(node):
                problems.append(f"{full}: no docstring")
            if m.is_style or full in SKIP:
                continue
            needed = node.name in scenes if m.is_scenes else True
            if needed and full not in cited:
                problems.append(f"{full}: not in docs/index.md")
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--write", action="store_true", help="regenerate docs/reference.md")
    args = parser.parse_args()
    modules = load_modules()
    if args.write:
        REFERENCE.parent.mkdir(exist_ok=True)
        REFERENCE.write_text(reference(modules))
        print(f"wrote {REFERENCE.relative_to(ROOT)}")
    problems = check(modules)
    for p in problems:
        print(p)
    if problems:
        print(f"\n{len(problems)} problem(s).", file=sys.stderr)
        return 1
    print("docs/index.md and docs/reference.md are up to date.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
