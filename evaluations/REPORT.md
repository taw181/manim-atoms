# Does manim-atoms make new animations easier? An A/B test

**Question.** Does manim-atoms make a new atom-physics animation easier to build than plain manim?

**Method.**
- Six prompts, each given verbatim to two isolated agents running the same model:
  - **A (manim-atoms):** worked in this repo, following its CLAUDE.md and skill.
  - **B (plain manim):** worked in a separate project with only manim 0.21, numpy and matplotlib, and was barred from reading this repo.
- Both arms followed the same loop: render at `-ql`, extract frames, read them, iterate.
- Afterwards:
  - I checked every B transcript for tool calls that touched the package; none did.
  - I re-checked every A change to an existing module against renders from before the change.
  - I read both final frames and a six-frame contact sheet for each prompt.

Each prompt's directory (`p1_lmt12/` … `p6_fountain/`) has:
- `notes.md`: the metrics, physics checklist and verdict;
- `contact.png`: six frames from each build, A on top and B below;
- `final_A.png` and `final_B.png`: each build's final frame;
- `plain_manim.py`: B's scene.

## Summary

| # | Prompt | What the package already had | A/B tokens | A/B time | A/B code | Physics A / B | Better result | Verdict for the package |
|---|---|---|---|---|---|---|---|---|
| P1 | 12-pulse LMT Mach–Zehnder | LMT engine (`lmz_pulses`, `lmt_history`) | 1.27× | **0.74×** | **0.28×** | ✓ / ✓ | A for the talk, B for detail | **Helped** |
| P2 | Ramsey–Bordé, both loops and four ports | Primitives only | 2.10× | 1.77× | 1.31× | ✓ / ✓ | B | **Cost more** |
| P3 | Gravimeter with curved arms, ending on k g T² | Displaced legs in `core.spacetime` | 1.74× | 1.34× | 0.85× | ✓ / ✓ | slight A | Neutral |
| P4 | Three-cloud gradiometer | Two-cloud `GradiometerBase` | 1.87× | 1.19× | 1.33×, but two scenes | ✓ / ✓ | B standalone, A for the talk | Cost more; integrates better |
| P5 | Rabi oscillations, Bloch vector and P_e together | `BlochView`, level diagram | 1.73× | 1.30× | 1.16× | ✓ / ✓ | tie | Neutral to negative |
| P6 | MOT → fountain → Mach–Zehnder | Trapping and interferometry, plus the spacetime clock | 1.72× | 1.06× | 0.76× | ✓ / ✓ | A for AION, B general | Helped with composition |
| | **Total** | | **973k vs 568k (1.71×)** | **62 vs 54 min (1.15×)** | **1399 vs 1558 lines (0.90×)** | **12 / 12** | | |

All ratios are A ÷ B. Code counts new scene and tool lines, leaving out blanks, comments, docstrings and small style or extension edits (`notes.md` has the details). Every A extension to an existing module left the scenes using it pixel-identical:
- 9 gradiometer-based scenes;
- `LMTMachZehnder` and `LargeMomentumTransfer`;
- `SinglePhotonMachZehnder`;
- every frame of the 4 scenes that use `absorb`/`emit`.

## What the test says

**1. On effort, the package mostly doesn't pay for itself yet.**
- A used about 1.7× the tokens on five of the six prompts, and about 15% more wall time overall.
- Most of the extra goes in before any code is written: CLAUDE.md, the skill, the style modules, primitives, and whichever scenes the build has to understand before it can reuse them. That's roughly 50–70k tokens of fixed cost per task.
- It only paid off when an engine for the exact problem already existed (P1: 3.5× less code, 25% faster).

**2. Its real value is integration and compounding, not speed.**
- Every A scene came out in the deck's house style, with `beat()` stops, ready for `class XSlide(Clicks, …)`, and with AION's Sr conventions.
- B's scenes each invented their own look.
- For "the next slide in this talk", A's output is the one you'd use. That holds most clearly for P4: its third cloud appears in exactly the visual language of the existing gradiometer slide.
- The package also grew as it was used:
  - P1 made `LMTMachZehnder` take any order;
  - P4 made `GradiometerBase` take N clouds;
  - P2 added a general pulse-tree engine and a pulse that can come from above;
  - P3 added curved arms;
  - **P6 reused P3's `curved_loop`, written earlier in this same test.**

**3. On standalone explanation, plain manim did as well or better.**
- The plain builds tended to be more didactic:
  - P2 keeps the open branches and boxes each loop's ports;
  - P4 animates laser noise cancelling in the differences;
  - P6 ends on bars and a fringe scan.
- Their equivalents in the A builds were cleaner, but sparser.
- Physics was right in all 12 builds. Both arms handled the ambiguous "12-pulse" the same way: 12 LMT pulses plus the plain three, so 15 in all.

**4. The package anchors interpretation.**
- In P1, A used the package's own scheme, where every pulse drives both arms (N = 7). B independently chose the sequential, single-arm scheme (n = 4).
- In P3 and P6, A used single-photon Sr conventions; B used the textbook Raman/Rb ones.
- That's right for AION, but it's a bias to know about if the package goes public as general-purpose.

## Package gaps, in priority order

1. **Discoverability is the main cost.**
   - Agents found general tools by grepping:
     - `draw_wavy_legs` is the curved-arm version of `draw_legs`, but is documented only for GW-bowed legs;
     - `BlochView` lives in `squeezing.py`;
     - `recoil` lives in `lmt.py`.
   - Add a toolbox map to SKILL.md ("I need X → use Y in Z") and a one-paragraph summary at the top of each tools module. This is the cheapest way to cut the token overhead.
2. **General tools live in topic modules.**
   - Promote to `core/`, or a shared `interferometry/tools/common.py`:
     - `BlochView` (from squeezing);
     - `recoil` (from lmt);
     - `curved_loop` (from gravimeter);
     - `beamsplitter_tree` and `sweep_pulse` (from ramsey_borde, added in this test).
   - `BlochView` should sit low enough that `species/` can use it.
3. **Scenes hard-wired to one configuration.**
   - P1 and P4 fixed `LMTMachZehnder` (order) and `GradiometerBase` (number of clouds). Still open:
     - `Gradiometer.construct` is one long method, so its effect step and readout get copied rather than reused;
     - `MachZehnder.make_legend` and `pulse_caption` are static methods on a scene class, so a new scene subclasses `MachZehnder` just to get them.
   - The pattern that worked: configuration as class attributes, and steps as hook methods.
4. **One-direction primitives.**
   - `absorb`, `emit` and `make_k_arrow` only work for a beam from below.
   - `draw_ports` only draws straight ports, flat for g and rising for e.
   - `arm_ket` only knows |g,p⟩ and |e,p+ħk⟩.
   - P2's `sweep_pulse` (either side, many atoms) is the general version.
5. **The layering rule blocks generic compositions.** A MOT plus an interferometer has to live in `aion/` because trapping and interferometry can't import each other. Either accept `aion/` as the home for compositions, or add a composition layer above the two topics.
6. **Trapping objects aren't parametric.**
   - `AtomCloud` can't follow a path; P6 mutated `center` from a first-placed updater.
   - `Coils` hard-codes its size.
   - `stage_heading` needs a `Stage` keyed to the timeline's colours.
7. **Silent failures.**
   - `lmz_pulses` accepts an even n and only fails later, at `lmt_history`'s closure assert.
   - Add these manim traps to the skill:
     - `Integer`/`DecimalNumber` don't line up with `Tex` that has descenders;
     - `Tex` wraps long lines silently;
     - fading a `Transform`ed title turns its glyphs into garbled shapes.
8. **A bug in parallel deck renders.**
   - The problem: manim's `delete_nonsvg_files` deletes every non-SVG file in the shared `media/Tex`. Renders running in parallel therefore delete each other's fresh `.dvi` files before `dvisvgm` converts them, and the render fails with "Your installation does not support converting .dvi files to SVG".
   - Where it happens: this hit the test's setup, and it will hit `manim-atoms-deck render -j N` (and qsim_visit's `deck.sh -j N`) whenever two slides compile new TeX at once.
   - The fix: set `no_latex_cleanup = True` in `manim.cfg`, or pass a per-job `--media_dir`.

## Caveats
- **Sample size:** one run per arm per prompt. Agent runs vary a lot, so ratios within about ±30% shouldn't be read as differences.
- **Model:** both arms ran the same model, so these results say how much the package helps *this* model build an animation. A human, or a model that already knows the package, pays the reading cost once, not every task.
- **A's extra obligations:** A's arm carried obligations B's didn't (regression-checking existing scenes, house conventions, slide hooks). That's real usage, but it inflates A's cost relative to a quick one-off.
- **Isolation:** B was isolated by instruction, and the transcript check found no tool call touching the package. What the B agents' harness put in their context wasn't checked.
- **Quality:** the "better result" column is my judgement from the frames, not a blind rating.
