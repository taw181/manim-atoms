# What's where in manim_atoms

Read this first, before opening any source. The sections are organised by
what you want to draw. Each line gives the module to import from, then the
names in it. Every path is under `manim_atoms`, so
`` `core.spacetime`: `draw_wavy_legs` `` means
`from manim_atoms.core.spacetime import draw_wavy_legs`.

[reference.md](reference.md) has every module and name with its signature and
docstring. It is generated from the source, so look a name up there before
reading the file it lives in.

<!-- Keeping this page current: `python scripts/index.py` (CI runs it) fails
when a public function or class is missing from this page, or when the page
cites a name that is gone. A backticked dotted name is a citation; a bare
name is looked up in the modules cited on its line. Write manim's own names
as `manim.ValueTracker`, or leave them unticked. -->

## How the pieces fit

- **Layers.** Imports run one way only: `core` → `species` → {`interferometry`, `trapping`} → `aion`. `slides` depends on `core` alone. Each topic has these parts:
  - `tools/`: helpers, plus the geometry constants they use;
  - `scenes/`: Scene classes;
  - where it has them, `physics/` (numbers, no manim) and `plots/` (matplotlib).
  - Generic concepts live in `core`, even when one topic uses them: the Bloch sphere (`core.bloch`), beams and cavities (`core.optics`), log-log axes and scatters (`core.plots`).
- **Space-time diagrams.** x is lab time and y is height along the baseline, which is also the direction of the beam and of the recoil. Some consequences:
  - an atom at rest is a horizontal line;
  - a kicked arm climbs, and its slope is its momentum;
  - a photon is a steep line in the gradiometer, or a vertical one where light travel time is ignored.
- **One lab clock.** The continuous scenes (`*Continuous`) drive everything from a single `manim.ValueTracker` whose value *is* the x coordinate:
  - `core.spacetime`: `run_to` advances it;
  - `carry` pins an atom to its `worldline`;
  - `wound` turns a phase hand.
  - Between the first pulse and the last, every `manim.Scene.play` must advance the clock.
- **Defaults bind at definition time.** Tools take their geometry from module constants as default arguments, e.g. `interferometry.tools.clock`: `draw_ports` defaults to `CP_SLOPE`. A new scene passes its own values; it does not rebind the constants.
- **Colours** come from the style modules, never from inline values:
  - `style`: `ATOM_COLOR` is |g, p>, `KICKED_COLOR` is |e, p + ħk>, `LASER_COLOR` is the beams and their annotations.
  - `style` holds only what is generic; a topic's own palette is in its style module (`interferometry.style`, `trapping.style`, `aion.style`), and a species' line colours are with the species (`species.strontium`: `TRANSITION_461_COLOR`, ...).
  - Every constant is listed under its section in [reference.md](reference.md).
- **Slide stops** are no-op hooks a scene calls where a presenter would stop: `beat()`, `stage_break()`, `hold()`. See [Making a scene a slide](#making-a-scene-a-slide).

## Atoms and clouds

- **An atom** (a disc you recolour through `atom[0]`), recoloured on a state change. `core.primitives`: `make_atom`, `state_colors`.
- **A state's ket** in its colour. `core.primitives`: `state_label`, and `arm_ket` for |g, p> or |e, p + ħk> with an optional phase factor.
- **The key to the two states**: an atom of each colour beside |g, p> and |e, p + ħk>. `core.primitives`: `state_legend`.
- **A still cartoon cloud** (dots in a Gaussian heap). `core.primitives`: `make_cloud`.
- **A trapped cloud that loads, cools, shrinks and glows.** `trapping.tools.cooling`: `AtomCloud`. Its knobs (radius, temperature, arrived, dark, glow) are all trackers. It can load from a source point and be stretched into a cigar.
- **A stream of atoms** from an oven or a 2D MOT. `trapping.tools.cooling`: `AtomBeam`.
- **Atoms shared between two dipole traps.** `trapping.tools.dipole`: `LoadingAtoms`.
- **A cloud whose atoms drift at their own velocities** (velocity slicing). `trapping.tools.slicing`: `SlicingCloud`.
- **Atoms lighting up under an imaging pulse.** `core.primitives`: `fluoresce`, or `fluorescence` to play the light alongside something else.

## Laser pulses and photons

- **A wavepacket** travelling along +y. `core.primitives`: `make_laser_pulse`.
- **A photon absorbed (|g> → |e>) or stimulating emission (|e> → |g>)**, played on one atom, with light from below (absorbing gives +ħk, emitting −ħk) or from above (the reverse). `core.primitives`: `absorb(from_below=...)`, `emit(from_below=...)`.
- **A pulse from below or from above**, as a worldline arriving at a point. `interferometry.tools.pulses`: `kick_worldline(from_below=...)`.
- **A vertical pulse column** where light travel time is ignored. `interferometry.tools.pulses`:
  - `fire_vertical_pulse` climbs to each atom with lab time stopped;
  - `strobe_pulse` flashes whole with lab time running.
- **A pulse with light travel time**, reaching the far end of the baseline later. `interferometry.tools.pulses`:
  - `photon_worldline` is the line;
  - `fire_pulse` plays it with lab time stopped;
  - `sweep_pulse` plays it with lab time running, calling back at each crossing;
  - `climbing_pulse` draws it as far as the clock has got;
  - `launch_time` is when it left the laser, and `laser_caption` names the phase it carries there.
- **The k-vector marker** beside a beam. `core.primitives`: `make_k_arrow`.
- **A beam with its wavefronts**, which can be tilted. `interferometry.tools.phase_shear`: `make_beam`.
- **A pulse's caption on the caption row.** `interferometry.tools.pulses`: `pulse_caption`.

## Recoil and momentum

- **A recoil arrow** with its label (draw ħk vertical for a beam from below), and the animation that brings it on. `core.primitives`: `momentum_arrow`, `grow`.
- **What one pulse does to one arm**: the velocity change in recoils and the new internal state, for a pulse from below or from above. `core.primitives`: `recoil`.

## Arms and worldlines

- **Straight legs**: fly atoms from corner to corner at `V`, drawing the trajectory in step. `core.primitives`: `draw_legs`.
- **Curved arms**, bowed by a displacement. `core.spacetime`:
  - `draw_wavy_legs` is `core.primitives.draw_legs` for bowed legs;
  - `wavy_path` is the curve;
  - `leg_point` is a point a fraction of the way along it.
- **A dashed construction line** (the trajectory an atom arrives along, an empty port). `core.primitives`: `make_guide`.
- **An arm as a function of lab time**, given its corners. `core.spacetime`:
  - `worldline`;
  - `leg_share` is how far along a leg the clock has got;
  - `carry` pins an atom to it;
  - `growing_trail` draws the trail behind it.
- **A leg's slope**, which is its momentum. `interferometry.tools.clock`: `leg_slope`.
- **A band filling in over a stretch of the diagram** (a beam's on-window, a field's half-cycle). `core.spacetime`: `growing_band`.

## Pulse sequences and arm bookkeeping

- **The engine.** It steps one atom through any list of pulses. Each `Pulse` has an area (½ splits, 1 swaps), a direction, optionally the arms it drives and the arms it drops, and a stage. Merging is automatic: outputs that coincide after a π/2 become one, which is how an interferometer closes. It returns a `Sequence` of `Step`s, each with where the pulse lands, its splits, hits, merges and legs, plus every arm's corners and the output ports. It covers Mach–Zehnder, LMT, Ramsey–Bordé, and with a displacement (disp) a gravimeter or a fountain. `interferometry.tools.pulse_sequence`: `run_sequence`, `Pulse`, `Sequence`, `Step`, `Arm`.
- **Animating a sequence**: one ray per pulse, a flash on every arm it kicks, the recolouring and splits, then the legs (bowed, if displaced). Hooks add captions and stops. `interferometry.tools.pulse_sequence`: `play_sequence`.
- **Sequences already written**: the LMT Mach–Zehnder of any odd order, and the LMT ladder. `interferometry.tools.lmt`: `lmz_pulses`, `lmt_ladder_pulses`.

## Displacements: gravity, a passing wave

- **A displacement function** disp(t) bows a leg through `leg_point` and `draw_wavy_legs`. `no_displacement` is the quiet baseline. Module: `core.spacetime`.
- **A gravitational wave's displacement** of a cloud. `aion.tools.gradiometer_gw`: `gw_displacement`.
- **One interferometer's corners when the pulses arrive late.** `aion.tools.gradiometer_gw`: `gw_vertices`.
- **Per-cloud displacement in a gradiometer scene**, as a hook. `interferometry.scenes.gradiometer`: `GradiometerBase.displacement`, `GradiometerBase.nominal`.

## Phase as a clock hand

- **A hand riding an atom**, and how fast it turns. `interferometry.tools.clock`: `make_clock_hand`, `clock_rate`.
- **A dial**, its hand, and the angle swept between two hands. `interferometry.tools.clock`: `make_dial`, `dial_hand`, `phase_sweep`.
- **Driving a hand off the lab clock.** `core.spacetime`:
  - `wound` turns it only while the arm is excited;
  - `wound_with_shift` adds a light shift across a window;
  - `wound_with_jumps` adds the laser's phase steps at each pulse.
- **The laser phase steps on a gradiometer's hands.** `interferometry.tools.gradiometer`: `laser_jumps`.
- **The phase budget**: an equation, its terms marked and struck out, and a term ringed. `interferometry.tools.clock`: `budget_equation`, `show_phase_budget`, `readout_equation`, `ring_around`.

## Output ports and readout

- **The two output ports** the last pulse sends the atoms into, at any slope. `interferometry.tools.clock`:
  - `draw_ports` with lab time stopped;
  - `fly_ports` on the lab clock;
  - `port_parts` is the pieces;
  - `live_ports` keeps drawn ports following the phase;
  - `ground_share` is the share left in |g>.
- **A point a fraction of the way along a straight leg.** `core.spacetime`: `along`.
- **A point on a port of any slope.** `interferometry.tools.clock`: `along_port`.
- **The excited fraction at a phase**, and a phase sheared across a cloud. `interferometry.tools.phase_shear`: `excited_fraction`, `shear_phase`, `phase_reading`.
- **A camera image of a port**, striped by the phase. `interferometry.tools.phase_shear`: `PortImage`.
- **Imaging the ports** with a 461 nm pulse. `aion.scenes.light_shift`: `LightShiftSignal.imaging_pulse`, `LightShiftSignal.imaging_line`.

## The gradiometer: two interferometers, one laser

- **The scene machinery.** `interferometry.scenes.gradiometer`:
  - `GradiometerBase` has two clouds, their arms, hands, dials and ports, with hooks `GradiometerBase.open_arms`, `GradiometerBase.port_slope`, `GradiometerBase.port_extra` and `GradiometerBase.close`;
  - `RunsContinuously` is the mixin that runs it on one lab clock;
  - `Gradiometer` is the quiet case, and `GradiometerContinuous` is the same on one clock.
- **Its geometry.** `interferometry.tools.gradiometer`:
  - `vertices` is one cloud's four corners;
  - `gradiometer_frame` is the title, laser line, time axis and baseline.
- **The AION versions.** See [AION scenes](#aion-scenes). Each subclasses `GradiometerBase` and overrides `fly`, `shoot` and `pulse_note`.
- **A long-baseline detector in cartoon** (a static slide): the shaft, the sources and the fountain loops. `aion.tools.baseline`: `make_baseline`, `source`, `launch_loop`.

## Level diagrams

- **A two-level clock transition** beside a figure (it doubles as the key), lit up while a pulse drives it. `species.two_level`: `make_level_diagram`, `transition_glow`.
- **Strontium's levels and lines**: 461, 689 and 698 nm, the repumps, 488 nm. `species.strontium`: `SrLevels`, and `SrLevels.drive` to light the running lines.
- **A clock transition dragged by an oscillating field.** `aion.tools.uldm`: `make_modulated_levels`, `dm_upper`.
- **The 689 nm line swept in a sawtooth.** `trapping.tools.cooling`: `SweepFan`, `make_sawtooth`.

## Bloch sphere

- **A Bloch sphere in perspective** on a flat scene. `core.bloch`: `BlochView`, with `BlochView.point`, `BlochView.ring`, `BlochView.curve`, `BlochView.patch` and `BlochView.outline`.
- **Quantum noise as a patch on the sphere** (a coherent or squeezed spin state). `core.bloch`: `noise_patch`.

## Optics: beams, cavities, interferometer parts

- **A beam seen side on**, or a spot seen end on, as a Gaussian profile. `core.optics`: `gaussian_band`, `gaussian_spot`.
- **An optical cavity**: mirrors, mode, probe and detector, plus its vacuum-Rabi-split transmission with atoms in it. `core.optics`: `make_cavity`, `rabi_transmission`.
- **The parts of an optical interferometer**, seen from above and placed by the caller: a flat mirror or test mass, a beam splitter, a laser, a photodetector. `core.optics`: `make_mirror`, `make_beam_splitter`, `make_laser`, `make_photodetector`.
- **Light drawn as a wave riding a beam**, its phase chained from beam to beam, and the faint band under it. `core.optics`: `light_wave`, `beam_glow`.
- **Atoms in the cavity mode** in the superposition's colour (spin squeezing's own). `interferometry.tools.squeezing`: `cavity_atoms`.

## Trapping apparatus

- **MOT beams**, counter-propagating pairs at any in-page angles or in 3D. `trapping.tools.cooling`: `MotBeams`.
- **The red MOT's up beam**, a push beam, and a baffle. `trapping.tools.cooling`: `make_up_beam`, `make_push_beam`, `make_baffle`.
- **Anti-Helmholtz coils**, drawn as heavy as their gradient. `trapping.tools.cooling`: `Coils`.
- **An oven.** `trapping.tools.cooling`: `Oven`.
- **3D on the page**: an oblique projection, a ring across the push axis, an open arrowhead. `trapping.tools.cooling`: `project`, `oblique_ring`, `chevron`.
- **A MOT as a glow**, and the quadrupole field's zero. `trapping.tools.dipole`: `make_mot_glow`, `make_field_zero`.
- **The spread over m_F**, optically pumped. `trapping.tools.dipole`: `SpinHistogram`.
- **A velocity distribution with a pulse's slice through it.** `trapping.tools.slicing`: `VelocityPlot`, `excitation`, `thermal`.
- **A CAD render, labelled, with dimensions.** `trapping.tools.hifais`:
  - `chamber_view` loads it;
  - `chamber_label` adds a label with a leader line;
  - `dimension` adds a dimension arrow;
  - `at` is a pixel of the render on screen.

## Timelines and staged sequences

- **The experiment's stages**, as data. `trapping.tools.sequence`: `Stage`.
- **A timeline of coloured blocks** lighting up stage by stage, and braced references under it. `trapping.tools.sequence`: `Timeline`, `References`.
- **The running stage's heading**, and a grey caption under it. `trapping.tools.sequence`: `stage_heading`, `caption`.
- **Which video frame shows a given time.** `trapping.tools.sequence`: `snapshot_index`, `snapshot_ms`.

## Fields and waves over a diagram

- **A gravitational wave's strain**, its trace above the diagram on the diagram's own time axis, and a marker riding it. `aion.tools.gradiometer_gw`: `strain`, `make_strain_trace`, `trace_point`, `strain_marker`, `arrival_dots`.
- **Light travel time under a wave**, and the early or late arrivals it causes. `aion.tools.gradiometer_gw`: `gw_lag`, `gw_arrival_lags`, `quiet_arrival`, `arrival_note`.
- **An ultralight dark-matter field**, its trace, its marker, and the phase an arm winds up in it. `aion.tools.uldm`: `dm_field`, `make_field_trace`, `field_marker`, `dm_phase`.

## Surfaces in 3D

- **A wireframe sheet whose height is any field z(x, y)**, redrawn each frame and coloured by height (a merger's spacetime; a trap's potential). `core.surfaces`: `make_sheet`, `refresh_sheet`, `height_ramp`.
- **Keeping the sheet behind what sits on it** in ThreeDCamera's depth sort. `core.surfaces`: `SheetLine`, `BEHIND_EVERYTHING`.
- **An off-centre 3D camera whose frame-fixed overlay stays put.** `core.surfaces`: `SideCamera`.
- **A smooth 0-to-1 taper or blend** across a field. `core.surfaces`: `smooth_step`.

## LIGO's Michelson interferometer

- **The apparatus and its light**, on one lab clock: laser, splitter, arms, test masses, detector, and waves whose phase runs on from beam to beam. `aion.tools.ligo`: `make_apparatus`, `make_light`, `run`.
- **The light pooling on its detector.** `aion.tools.ligo`: `detector_glow`. Its parts are `core.optics`' (above), placed at LIGO's own positions.
- **The physics.** `aion.tools.ligo`: `strain`, `mirror_positions`, `phase_difference`.
- **The readout**: h(t), the returning waves overlaid, and the equation. `aion.tools.ligo`: `make_strain_trace`, `returning_waves`, `make_equation`.

## Plots drawn in manim

- **Log-log axes in decades**, and points and curves on them. `core.plots`: `log_axes`, `plot_point`, `curve_points`.
- **Linear axes with tick and axis labels**, the x ticks as MathTex (so they can read π). `core.plots`: `ticked_axes`.
- **A row of keys**, each a dot and its label. `core.plots`: `legend_row`.
- **The GW sensitivity plot's axes**, and a detector's curve with its region shaded. `aion.tools.gw_plot`: `sensitivity_axes`, `detector_region`.
- **The ULDM reach inset.** `aion.tools.uldm_plot`:
  - the whole inset: `uldm_inset`;
  - its pieces: `uldm_axes`, `uldm_curves`, `uldm_labels`, `excluded_region`, `excluded_label`;
  - a mass marked across it: `mass_mark`, `mass_label`;
  - lookups: `reach`, `deepest_reach`, `clipped`, `log_x_range`.
- **MOT loading curves.** `trapping.tools.hifais`: `loading_axes`, `loading_points`, `loading_fit`, `loading_rate_line`, `loading_cutoff`, `temperature_key`.
- **A scatter of thousands of dots as one fast VMobject**, arriving one at a time or all at once. `core.plots`: `dot_points`, `dot_cloud`, `static_cloud`.

## Matplotlib figures (static)

- **AION DAI data**: fringes, the Lissajous ellipse, Allan deviation, injected signals. `aion.plots.dai_fringes`:
  - figures: `fringes_figure`, `lissajous_figure`, `adev_figure`, `adev_inset`, `signals_figure`;
  - loaders: `load`, `load_adev`, `load_sigma`, `load_signals`;
  - styling and units: `deck_fonts`, `dark_axes`, `legend`, `hexed`, `frequency_unit`.
- **GW sensitivity with merger tracks.** `aion.plots.gw_sensitivity`: `sensitivity_figure`, `draw_merger`, `merger_legends`, `dark_axes`.

## Physics numbers (no manim)

- **GW signals.** `aion.physics.gw_signals`:
  - sensitivity curves: `load_sensitivity`, `smooth_log_log`;
  - mergers: `merger_track`, `merger_strain`, `phenom_a_frequencies`, `symmetric_mass_ratio`;
  - chirp timing: `frequency_before_merger`, `time_before_merger`;
  - distance and labels: `luminosity_distance`, `mass_tex`.
- **ULDM reach.** `aion.physics.uldm_sensitivity`: `load_uldm_sensitivity`, `model_reach`, `coupling_at`, `mass_from_frequency`, `frequency_from_mass`.
- **Scaling the prototype to a km.** `aion.physics.km_scale`: `waist_for_rayleigh_range`, `power_for_same_rabi`, `pulse_count`, `fidelity_for_contrast`.
- **MOT loading.** `trapping.physics.mot_loading`: `load_loading_curves`, `load_loading_fits`, `loading_model`.

## Slide furniture, citations, data

- **A static slide**: the heading, an image (and a pixel of it on screen), a numbered list, a placeholder slot. `core.layout`: `slide_title`, `load_image`, `image_point`, `numbered_list`, `placeholder_frame`.
- **References.** `bibliography`:
  - `load_bibliography` reads a .bib file;
  - `format_reference` formats an entry under a `CiteFormat`;
  - `Reference` and `Name` are the entry and its authors.
- **A citation line**, placed in the footer. `core.citations`: `citation`, `labelled_citation`, `place_citation`.
- **A drawing set into part of another scene's frame**, scaled and shifted, so one builder can fill a scene or sit in a corner of another. `core.layout`: `Panel` (LIGO's builders all take one).
- **A video playing inside a scene**, frame by frame, off any tracker. `core.video`: `load_video_frames`, `VideoFrame`.
- **Shipped data files.** `resources`: `data_path`. Sources and licences are in `src/manim_atoms/data/README.md`.

## Making a scene a slide

- **In the scene.** Call `beat()`, `stage_break()` or `hold()` where a presenter would stop. They are no-ops on the scene itself.
- **In the deck.** `slides.deck`:
  - `DeckSlide` is the base slide; it gets a footer from `make_footer` and citations through `cite`;
  - `Clicks` turns `beat()` into a stop;
  - `RunsOnIntoLoops` and `LoopingStages` loop a running stretch until the click.
  - A slide is `class XSlide(Clicks, SomeScene)`.
- **The deck file.** `slides.deck`: `load_deck` reads it into a `Deck`.
- **Rendering and presenting.** `manim-atoms-deck` (`slides.cli`) renders and presents.
- **A web player.** `slides.player`: `build_player`, with `pretty` for menu names.

## Worked examples by pattern

Copy from these when building something similar.

- **A geometry block and stop-start legs.** `interferometry.scenes.mach_zehnder`: `MachZehnder`, `SingleLaserKick`.
- **Photons resolved, with a level diagram as the key.** `interferometry.scenes.single_photon`: `SinglePhotonMachZehnder`.
- **The pulse-sequence engine, animated** (with stage captions and pulse labels through the hooks). `interferometry.scenes.lmt`: `LMTMachZehnder`; the bare ladder is `LargeMomentumTransfer`.
- **Phase as hands, a dial and a budget.** `interferometry.scenes.clock`: `ClockPhase`, `ClockPhaseTerms`.
- **Displaced, bowed legs.** `aion.scenes.gradiometer_gw`: `GradiometerGWStretch`, `GradiometerGWStretchContinuous`.
- **Pulses arriving early or late under a wave.** `aion.scenes.gradiometer_gw`: `GradiometerGW`, `GradiometerGWContinuous`, and the `WaveRunsContinuously` mixin.
- **One lab clock driving several views** (field trace, level diagram, interferometer). `aion.scenes.uldm`: `DarkMatterPhaseContinuous`; also `DarkMatterPhase`, `DarkMatterGradiometer`, `DarkMatterField`.
- **A beam on one arm for a window.** `aion.scenes.light_shift`: `LightShiftSignal`, `LightShiftSignalContinuous`.
- **A Bloch sphere and a cavity.** `interferometry.scenes.squeezing`: `SpinSqueezing`.
- **A tilted beam and camera images.** `interferometry.scenes.phase_shear`: `PhaseShearReadout`.
- **A staged sequence with a moving camera.** `trapping.scenes.cooling`: `CoolingSequence`. Also `trapping.scenes.dipole`: `DipoleTrapLoading`; and `trapping.scenes.slicing`: `VelocitySlicing`.
- **Video on the scene's clock.** `trapping.scenes.sequence`: `ExperimentSequence`, `ExperimentSequenceSimple`.
- **A CAD render labelled, then data.** `trapping.scenes.hifais`: `HighFluxLoading`.
- **3D: a sheet, a camera, a merger.** `aion.scenes.gravitational_waves`: `BlackHoleMerger`, `MergerOnSensitivityPlot`.
- **An optical interferometer with beams that carry phase.** `aion.scenes.ligo`: `LIGOMichelson`.
- **Data arriving shot by shot.** `aion.scenes.dai_data`: `FringesToEllipse`, `FringesToEllipseNoisy`, `FringesFirst`, `FringesFirstNoisy`, `LaserNoiseLissajous`.
- **A plot built up one beat at a time.** `aion.scenes.gw_landscape`: `SensitivityBuildUp`; and `aion.scenes.aedge`: `AEDGESensitivity`.
- **A camera flying across scales.** `aion.scenes.uldm_scale`: `DarkMatterScale`, `DarkMatterScalePlot`.
- **A table revealed row by row.** `aion.scenes.km_challenges`: `KmScaleChallenges`.
- **A lab picture with traps and a beam through them.** `aion.scenes.signal_injection`: `SignalInjection`.

## Still to generalise

These are general in what they draw but not yet in how they are called:
they are fixed to one scene's layout, or live on a scene as methods. They
are the candidates for the next round of generalisation.

- `interferometry.tools.pulse_sequence`: `run_sequence` draws pulses as vertical (no light travel time); the gradiometer's sloped pulses (`interferometry.tools.pulses`: `sweep_pulse`) are not yet a pulse option.
- `interferometry.tools.pulses`: the sloped pulses take their defaults from the gradiometer's `GR_*` geometry.
