---
name: verify-refactor
description: Prove a change to manim-atoms leaves every scene and figure as it was — moving or renaming functions, modules or style constants, splitting a module, tidying imports, any refactor meant to change nothing on screen. Use it before starting such a change (to take the baseline) and after each step, whenever the user says refactor, move, rename, reorganise, clean up or tidy in this repo, or asks you to check nothing broke.
---

# Verifying a refactor

A refactor of a manim package fails in three ways, each caught at a
different cost. Use all three, cheapest first, and never declare a refactor
done on "it imports".

| What breaks | Caught by | Cost |
|---|---|---|
| a name used but no longer defined or imported where it is used | `undefined_names.py` | seconds |
| code that only fails when it runs (a helper called wrongly, a hook a subclass still overrides) | `dry_run.sh` | ~6 min for all 41 scenes, seconds for a few |
| a picture that changed without an error: a default argument now bound to a different constant, a draw order, a colour | `last_frames.sh` + `compare_frames.py` | ~10 min, in the background |

Every script finds the repo root itself; run them from anywhere. `S` below is
this skill's `scripts/` directory.

## Before touching anything: the baseline

The renders read the source when each one starts, so the baseline must
finish before you edit a single `.py` file — or work in a git worktree.

```bash
$S/last_frames.sh /tmp/before            # every scene's last frame; background it
uv run python $S/save_figures.py /tmp/before_figs   # the matplotlib figures
```

## After each step

```bash
python -m compileall -q src
uv run --with pyflakes python $S/undefined_names.py   # must report undefined: 0
python scripts/index.py                              # the index and reference
$S/dry_run.sh 'squeezing|dipole'                     # the scenes this step touched
```

`undefined_names.py` is the one that matters most. Every module star-imports
manim and a style module, so plain pyflakes can only say a name "may be
undefined". This script checks each such name against the module's real
namespace. It catches what moving code typically leaves behind:
- a function moved without its import following it;
- a style constant moved to a style the module doesn't see;
- a removed `import numpy` that a star import was passing on to a module
  further down the chain.

It also lists imports left unused.

Pick the scenes for `dry_run.sh` by grepping for the modules you changed.
`scenes.sh FILTER` shows what a filter selects. After a style change, run
every scene: they all star-import the styles.

## At the end

```bash
$S/last_frames.sh /tmp/after                          # background it
uv run python $S/compare_frames.py /tmp/before /tmp/after   # 0 differ or missing
uv run python $S/save_figures.py /tmp/after_figs
uv run python $S/compare_frames.py /tmp/before_figs /tmp/after_figs
```

For a step that touched only a few scenes, `last_frames.sh /tmp/after FILTER`
followed by `compare_frames.py ... --subset` compares just those.

A pure refactor must come out pixel-identical. If a frame differs, it is a
real change: find out why before going on, don't re-baseline over it.

## Habits that keep it cheap

- **Move with code, not by hand.** Cut top-level definitions by `ast` span,
  with the comment block above each. Then rewrite every
  `from old import ...` across the package. Hand-moving a dozen functions
  loses a comment or an import every time.
- **One concern per commit**, each checked as above before it is pushed.
- **Change only Markdown while a render runs.** Editing a `.py` file under a
  running render can corrupt the run.
- **Docstring-only edits can't change frames**, but CLAUDE.md asks for a
  last-frame comparison after any change to a scene. A few `--subset`
  renders are cheap.
