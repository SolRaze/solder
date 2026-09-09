slicers

proven settings — 25 completed prints

Pulled from Moonraker's history database on knave (jobs with status
`completed`, Feb 2026, all sliced in **Cura 5.10.2**). This is the only hard
evidence of what worked on this machine, and it is the basis for the Orca
profiles below.

| Material | Nozzle | Bed | Layer | First layer | Fan |
|---|---|---|---|---|---|
| PETG | 250 °C | 80 °C | 0.2 mm | 0.24 mm | 40 %, first layer 30 % |
| PLA | 230 °C | 60 °C | 0.2 mm | 0.24 mm | as Cura default |

Longest completed print: 12.1 h, 32 m of filament (`PLA-14h07m_rear_enclosure`).
Largest PETG: 5.1 h / 14 m. So the machine has a track record of long,
unattended prints — which is exactly why
[`power-loss-recovery.md`](../setup/power-loss-recovery.md) is worth having.

Other settings recovered from the embedded Cura profile of a completed PETG
print (`Beyblade/PETG-1h10m_atomic.gcode`, profile `petg_100_normal`):

| Setting | Value |
|---|---|
| `material_print_temperature` | 250 |
| `layer_height_0` | 0.24 |
| `cool_fan_speed` / `cool_fan_speed_0` | 40 / 30 |
| `retraction_amount` | **0.2 mm** |
| `top_bottom_pattern` | concentric |
| `z_seam_type` | sharpest corner |
| `adhesion_type` | skirt |
| post-processing | `KlipperPreprocessor`, `CreateThumbnail` |

**Do not carry `retraction_amount: 0.2` forward.** That value only made sense
with a bowden tube plus `pressure_advance: 0.85`. Now that the machine is direct
drive with PA at 0, retraction is `0.6 mm` in both `printer.cfg` and the Orca
profiles.

process presets

| Preset | Layer | First layer | Outer wall | For |
|---|---|---|---|---|
| `0.20mm Standard @Solder` | 0.20 | 0.24 | 30 mm/s | everything, default |
| `0.12mm Fine @Solder` | 0.12 | 0.20 | 25 mm/s | precision, added 2026-08-13 |
| `0.12mm Clear @Solder` | 0.12 | 0.20 | 15 mm/s | transparent PETG only, added 2026-09-08 |

All three inherit a `Creality Ender3 0.4` system parent and carry explicit
support geometry (see below). `0.20mm Standard` and `0.12mm Fine` both have
`enable_support 0`, `raft_layers 0`, `fuzzy_skin none`, `reduce_crossing_wall 1`.

`0.12mm Fine @Solder` keeps a **0.2 mm first layer** rather than 0.12 — a 0.12
first layer leaves no margin for the paper level being slightly off, and this
machine has no probe. `adaptive_layer_height` is forced **0** (the system parent
sets it to 1), so the profile describes what actually prints.

**It will expose flow error that 0.2 mm hides.** `rotation_distance: 34.406` is
nominal and unmeasured since the extruder swap, and `pressure_advance: 0.04` is a
starting point. Run `E_CAL_START` / `E_CAL_RESULT` and a PA tower before trusting
a fine print — at 0.12 mm a few percent of over-extrusion is a visible ridge.

orcaslicer — installed and configured

OrcaSlicer 2.4.2, `/Applications/OrcaSlicer.app`. The Creality vendor profiles
were never downloaded, so these presets inherit from Orca's built-in **Klipper**
bases rather than an Ender-3 system preset. That is the right base anyway — this
machine runs Klipper, not Marlin.

Written to `~/Library/Application Support/OrcaSlicer/user/default/`, with copies
in this folder. Each `.json` needs a matching **`.info`**
sidecar (`sync_info = create`, `base_id = <parent's setting_id>`) or Orca ignores
the preset silently — that is what kept them from appearing on the first try:

| Preset | Inherits | Notes |
|---|---|---|
| `Solder` (machine) | `MyKlipper 0.4 nozzle` | 235 × 235 × 200, Klipper flavour, limits mirroring `printer.cfg` |
| `Numakers PETG-HS @Solder` (filament) | `Generic PETG @System` | 250 first layer / 245 after, bed 80 |
| `Numakers PLA+ @Solder` (filament) | **`Numakers PLA+ @System`** — Orca ships a real vendor profile | 230 first layer / 225 after, bed 60 |
| `Numakers ABS @Solder` (filament) | `Generic ABS @System` | 255/250, bed 100, fan nearly off — **untested, open frame** |
| `0.20mm Standard @Solder` (process) | `0.20mm Standard @MyKlipper` | 0.2 mm layers, 0.24 first, conservative speeds |
| `0.12mm Clear @Solder` (process) | `0.12mm Fine @Creality Ender3 0.4` | one wall, zero shells, 100% aligned rectilinear |
| `Numakers PETG-HS Clear @Solder` (filament) | `Generic PETG @System` | 250/250, bed 80, **fan 0%**, flow 1.00 |

what the machine preset carries

- **Start gcode:** `START_PRINT BED_TEMP=[first_layer_bed_temperature] EXTRUDER_TEMP=[first_layer_temperature]`
  — hands off to the macro, which heats the bed, homes cool, then heats the
  nozzle.
- **End gcode:** `END_PRINT`.
- **Layer change gcode:** `PLR_SAVE` — this is what makes power-loss recovery
  layer-accurate rather than 30-second-accurate.
- **Limits:** velocity 200, accel 1000, Z velocity 5 — matching `printer.cfg`,
  so Orca cannot plan a move the firmware will refuse.
- **Retraction:** 0.9 mm at 35 mm/s, 0.4 mm Z hop (raised from 0.6 / 0.2 on
  2026-08-13, see "Stringing" below). The PETG filament preset carries its own
  `filament_retraction_length` of **0.9**, which overrides the machine preset —
  change both or the filament one silently wins.
- **Bed exclusion:** none. `bed_exclude_area` is `[]` since the wipe bar came
  off the bed 2026-08-13; the full 235 × 235 is printable.
- **Thumbnails:** 400 × 400 PNG, so Mainsail shows previews like the old Cura
  files did.
- **Upload:** `print_host: https://solder.knave`, `host_type: moonraker`,
  `printer_agent: moonraker`. Verified reachable from the Mac; the mkcert
  certificate validates, so no TLS workaround is needed.
- **Relative E** (`use_relative_e_distances: 1`) — pinned so that
  `RESUME_AFTER_POWER_LOSS` can default to relative E and be right.

Supports — a downloaded 3MF overrides your preset

`0.20mm Standard @Solder` carries `enable_support`, `support_type`,
`support_style`, `support_critical_regions_only` and `support_on_build_plate_only`
— but **no geometry keys** (spacing, threshold angle, Z distance). Those are all
inherited. So when a downloaded `.3mf` carries the designer's process settings,
they win, and the preset you think you selected is not what gets sliced.

That is what happened on 2026-08-08 (see [`bringup-log.md`](../log/bringup-log.md)):

| Setting | Orca default (Ender 3) | What the 3MF used | Effect |
|---|---|---|---|
| `support_base_pattern_spacing` | 2.5 | **0.2** | near-solid raft against a 0.38 line width |
| `support_interface_spacing` | 0.5 | **0.2** | solid interface slab |
| `support_threshold_angle` | 30 | **60** | supports far more geometry |
| `support_top_z_distance` | 0.2 | **0.15** | object first layer ploughs the interface |
| `independent_support_layer_height` | — | **1** | 0.05 mm sliver layers, see below |

Support came to ~500 mm of the ~1825 mm printed — **27 % of the filament** — for a
card that did not need any, because the object was sitting 1.84 mm above the plate.

**Drop objects to the bed and check the support preview before slicing.** Import
the mesh rather than the project, or re-select the Solder process preset after
opening a 3MF.

The 0.2 mm support spacing comes from the vendor, not just the 3MF

**Corrected 2026-08-13.** The 0000A0 post-mortem blamed the downloaded 3MF for
`support_base_pattern_spacing 0.2`. That was only half of it —
`/Applications/OrcaSlicer.app/Contents/Resources/profiles/Creality/process/`
ships that value in the system profiles themselves:

```
0.12mm Fine @Creality Ender3 0.4.json
  "support_base_pattern_spacing": "0.2",
  "support_interface_spacing": "0.2",
```

Orca's generic default is **2.5**. The vendor overrides it to **0.2** against a
0.38 mm support line width, which is a solid block rather than infill. Any
Solder process preset that inherits from a vendor parent and leaves those keys
inherited gets a near-solid support — no 3MF needed.

Both Solder process presets now set the support geometry **explicitly** so they
cannot inherit it:

| Key | Value | Was inherited as |
|---|---|---|
| `support_base_pattern_spacing` | **2.5** | 0.2 |
| `support_interface_spacing` | **0.5** | 0.2 |
| `support_interface_top_layers` | **2** | 3 |
| `support_top_z_distance` | **0.2** | 0.15 |
| `support_bottom_z_distance` | **0.2** | 0.2 |
| `support_threshold_angle` | **30** | 30 |
| `support_base_pattern` | `rectilinear` | rectilinear |
| `tree_support_branch_distance` | **6** | 5 |
| `independent_support_layer_height` | **0** | — |

Spacing is the lever that matters. With `support_type: tree(auto)` /
`support_style: organic` — what both Solder presets use —
`tree_support_branch_distance` controls how many branches get generated;
`support_base_pattern_spacing` governs the base infill under them. Raise either
to use less material.

support settings that are known good here

Cura printed this machine's 25 successful prints. Its `petg_20_fast` profile
used `support_pattern = grid` and `support_top_distance = 0.24`. Orca equivalents:

| Orca | Set to | Why |
|---|---|---|
| `support_base_pattern_spacing` | **2.5** | Orca default. Cura's grid at its default density is ~2 mm. This one setting is the 12× filament difference |
| `support_interface_spacing` | **0.5** | Orca default; 0.2 is a solid slab |
| `support_threshold_angle` | **30** | Orca default |
| `support_top_z_distance` | **0.2** | Orca default. Cura's 0.24 also worked — do not go below 0.2 |
| `support_base_pattern` | `grid` or `rectilinear` | Cura used grid. `rectilinear` is lighter at the same spacing |
| `independent_support_layer_height` | **0** | see below |
| `support_style` | `grid` | already correct |

Spacing dominates. Pattern choice is worth a few percent; going from 0.2 to
2.5 mm spacing is worth roughly an order of magnitude.

supports: the geometry that prints

Supports are **wanted on this machine** and `enable_support: 1` is deliberate.
Supports are not the problem; near-solid support *geometry* firing on every
model is.

Do not chase snap-off removal by cutting interface layers to 0, widening gaps,
thinning support lines and switching Standard to `tree_slim`. **That set
collapses within the first few layers.** The geometry that holds is the one from
`holder.3mf` (holder + bucket,
2026-08-21), which is the last set of prints with clean supports, reduced
stringing and good bed adhesion. Those two were sliced with `0.12mm Fine
@Solder` at PETG 250 first layer / 245 after.

| Orca | Snap-off attempt | **Now (proven)** | Why |
|---|---|---|---|
| `support_interface_top_layers` | 0 | **0** | The one snap-off knob that was kept — see below |
| `support_interface_bottom_layers` | 0 | **2** | Explicit, not `-1`: `-1` mirrors the top value, which is now 0 |
| `support_top_z_distance` | 0.25 / 0.16 | **0.2** | Exactly one 0.2 layer of air |
| `support_bottom_z_distance` | 0.25 / 0.16 | **0.2** | Same |
| `support_object_xy_distance` | 0.5 | **0.35** | 0.5 leaves tall branches leaning on nothing |
| `support_line_width` | 0.36 | **0.38** | Deliberately-weak extrusions were weak at the base too |
| `support_style` | `tree_slim` (Standard) | **organic** | Organic branches merge and brace each other; slim ones are isolated sticks |

Both process presets now carry the same seven values — Fine no longer uses
0.16 mm Z distances.

**Removability is a top-only change.** `support_interface_top_layers: 0` stays
off — that is the dense slab pressed against the part's underside, and it is
what makes PETG supports fight back. Everything below the contact is back on the
proven numbers, so the branches still stand up.

`support_interface_bottom_layers` must be written as **2**, not `-1`. `-1` means
"same as top", which now resolves to 0 and silently strips the interface where
support lands *on* the model — that is structure, not removability.

The price is a rougher first supported layer. A part that needs that surface
gets `support_interface_top_layers` back to 2 for that print only, not in the
preset.

uploads land in a per-model subfolder

`filename_format` is now:

```
{input_filename_base}/{input_filename_base}_{filament_type[initial_tool]}_{print_time}.gcode
```

The leading path segment makes Orca's upload dialog prefill a subfolder, and
Moonraker creates it on upload. Six slices of the same model land in one folder
instead of six near-identical names in the gcodes root. The model name is
repeated in the filename on purpose — Fluidd's recent-jobs list and the printer
status show the basename alone, and `PETG_1h53m.gcode` on its own says nothing.

`independent_support_layer_height` — turn it OFF

With it on, Orca puts the support on its own layer grid. When that grid does not
line up with the object's, it emits a **sliver layer for every support layer** —
in that file, 0.05 mm layers alternating with 0.15 mm object layers instead of a
uniform 0.2 mm:

```
L9  Z2.04  H0.15   walls, solid infill        <- object
L10 Z2.09  H0.05   Support, Support interface <- support only
```

Why a 0.05 mm sliver cannot print here: layers 16 and 18 of that file deposit
**1.03 mm and 0.93 mm of filament in total**, while the retract that straddles
each one is 0.6 mm out and 0.6 mm back. Most of the layer is spent re-pressurising
the melt — worse with `pressure_advance: 0.0` — so the support blade comes out
thin or missing and the bridge above it has nothing to land on.

`min_layer_height = 0.08` does **not** protect you; this setting bypasses it.

It also silently rewrites the object's layer height (0.2 → 0.15 there), so the
process preset stops describing what actually gets printed.

Leave it off unless there is a specific reason, and check the layer preview for
alternating thin/thick bands before sending anything with supports.

stringing and unwanted extrusion — 2026-08-13

Diagnosed against a live PETG job (`Ender_3_toolholder_upgraded_PETG_1h56m`) by
querying Moonraker and reading the sliced gcode. Two separate problems wearing
the same complaint:

**Material where the model isn't.** The process preset was forcing
`enable_support: 1` (`tree(auto)`, organic), `raft_layers: 3` and
`fuzzy_skin: external` on **every** print, model regardless. That job alone had
147 `;TYPE:Support` sections plus a three-layer raft. All three are now off —
enable support per-model when a part actually has overhangs.

**Actual stringing.** Ranked by size on this machine:

| Cause | Evidence | Fix | Where |
|---|---|---|---|
| Travels run at 40 mm/s, sliced for 120 — 3× longer over open air, 3× the ooze | `max_velocity 40.0` live vs `; travel_speed = 120` | **done 2026-08-23: `max_velocity` → 150** | `printer.cfg`, not the slicer |
| `pressure_advance` forced to **0.0 on every print** by the filament preset's own start gcode | `SET_PRESSURE_ADVANCE ADVANCE=0.0` in `filament_start_gcode` | now `0.04` | filament preset |
| Retraction 0.6 mm, and only 0.42 of it happens before the toolhead moves (`retract_before_wipe 70%`) | `G1 E-.42` then `G1 X.. Y.. E-.18` | 0.6 → **0.9** | machine **and** filament preset |
| Travels cross straight over the part | `reduce_crossing_wall = 0` | → **1** | process preset |
| Z hop too small to clear a bulge | `z_hop = 0.2` | → **0.4** | machine preset |
| PETG never dried | open item since 2026-08-12 | dry it | — |

The `0.04` pressure advance is a **starting point, not a measurement** — a PA
tower is still owed. Note the mechanism: PA lives in `filament_start_gcode`, so
whatever `printer.cfg` says is overwritten at the start of every print.

Retraction is real `G1 E` moves, not `G10`/`G11` — the running file has **zero**
firmware-retraction commands, so `SET_RETRACTION` changes nothing and only a
reslice moves the number.

Clean PETG pass — 2026-08-23

The direct-drive mount was rebuilt, the extruder cable extended by soldering,
and the goal became one clean PETG print. Five changes, ranked by how much they
move the needle:

| # | Change | From → To | Where |
|---|---|---|---|
| 1 | **Motion limits off the floor** | `40 / 200 / 2.0` → **`150 / 500 / 5.0`**, Z `3/40` → `5/100` | `printer.cfg` |
| 2 | `enable_support` | stays **1** — supports are wanted (see above) | process preset |
| 3 | Nozzle temperature | holds at **`250 / 245`** — do not drop it | filament preset |
| 4 | `seam_position` | `nearest` → **`aligned`** | process preset |
| 5 | `wipe_distance` | 1 → **2** | machine preset |

**1 is the whole ballgame.** Orca slices travel at 120 mm/s, so a low
`max_velocity` clamps every travel and each one spends proportionally longer
dribbling over open air. Never floor the motion limits to slow a skipping
extruder — a skip is a mechanical fault, and the floor treats the symptom. The
numbers here are still **below stock**: the vendor firmware ships accel 500 and
Z accel 100. Nothing is measured — run `TEST_SPEED` before trusting a long
print.

**2: supports stay on.** `enable_support` is 1 because supports are *wanted*,
switched on deliberately print by print, not drifting. What needs tuning is the
support **geometry** — see above.

**3: the temperature holds at 250/245.** The argument for dropping it is sound
in general — the all-metal hotend has no PTFE in the melt zone to protect, so
250 is habit rather than a requirement, and hot PETG strings. But
[`bringup-log.md`](../log/bringup-log.md) records that **PETG under ~245 °C in this
hotend skips**. That was a hypothesis in a skip diagnosis rather than a
measurement, and the real cause turned out to be a snapped throat tube — but 240
sits below the line, this machine has a clog history, and change 1 moves the
dominant stringing variable by 3.75× on its own. Temperature is the wrong
variable to move in the same pass. Back at **250 / 245**; revisit only after a
clean print at those numbers.

**Retraction was left alone at 0.9 mm, deliberately.** That is already a
direct-drive number — bowden wants 4–6 mm, direct drive wants 0.4–1.0. Raising
it buys filament grinding and heat creep into the PTFE above the heatbreak, not
fewer strings. `retraction_speed` stays at 35 because
`max_extrude_only_velocity: 40` silently clamps anything above 40 — an
over-set value produces slow retracts and stringing, never an error message.

**`pressure_advance` really is 0.04, not 0.02.** The sliced gcode header reports
`; pressure_advance = 0.02`, which is Orca's own unused field inherited from
`Generic PETG @System`. The only `SET_PRESSURE_ADVANCE` in the file comes from
`filament_start_gcode` and says `0.04`. A PA tower is still owed.

schema traps when hand-writing orca presets

Orca silently ignores a preset that is malformed - no error, no log line, it
simply never appears in the dropdown. All four of these bit during setup:

| Requirement | Wrong | Right |
|---|---|---|
| `.info` sidecar per `.json` | absent | `sync_info = create`, `base_id = <parent setting_id>` |
| `version` field | absent | `2.3.2.75` (must match the vendor bundle) |
| Host type for Moonraker | `klipper` | `moonraker` |
| Thumbnails | `["400x400"]` | `["32x32/PNG", "400x400/PNG"]` |

Plus `printer_extruder_id` / `printer_extruder_variant`, which Orca writes for
any preset it creates itself. The fastest way to get the schema right is to
duplicate a system preset in the GUI once and read what Orca wrote.

Numakers PETG-HS

Three spools on hand: two Pitch Black, one Transparent.

Temperatures come from **this machine's own successful PETG prints**, not from a
vendor datasheet — Numakers' published spec for the HS range wasn't available
when the profile was written. Two things to check against the spool label before
a long print:

1. The HS ("high speed") formulation may want a different range than generic
   PETG. If the label says otherwise, believe the label.
2. Those 250 °C prints were made with the **stock hotend**. The V3 hotend
   Pro is all-metal with a different melt zone, and may run a few degrees
   cooler for the same result.

`filament_max_volumetric_speed` is set to a deliberately safe **10 mm³/s**.
The V3 is a high-flow hotend and can likely do more, but that is a
measurement, not a guess — run a flow test before raising it.

filaments owned

| Spool | Source | Preset |
|---|---|---|
| PETG-HS Pitch Black ×2, Transparent ×1 | Numakers | `Numakers PETG-HS @Solder` |
| PLA+ Black 1 kg, ±0.03 mm | Numakers | `Numakers PLA+ @Solder` |
| ABS Natural 1 kg | Numakers, unopened | `Numakers ABS @Solder` |

The PLA+ preset inherits **Orca's own bundled Numakers profile** (225 °C, flow
0.99, 12 mm³/s) rather than an invented one; only the bed temperature and a
230 °C first layer come from this machine's print history.

The ABS preset is a **generic-ABS starting point, not a measured profile**. This
is an open-frame Ender 3 with no enclosure: expect warping, layer splitting on
tall parts, and styrene fumes. Ventilate, print small, keep part cooling off.

All three set `filament_start_gcode: SET_PRESSURE_ADVANCE ADVANCE=0.0`, so once
PA is tuned per material the value lives with the filament rather than the
printer.

migration notes

What changed between the Cura era and now, and why the old profiles cannot be
used as-is:

| Then | Now | Consequence |
|---|---|---|
| Bowden | Direct drive | Retraction 0.2 → 0.6 mm; PA 0.85 → 0 pending tune |
| Stock MK8 hotend | V3 all-metal | PID invalid; melt behaviour differs |
| 4015 duct | Satsana 5015 | Cooling is stronger — fan percentages may want lowering |
| Marlin-flavour Cura output | Klipper-flavour Orca | `START_PRINT` / `END_PRINT` macros do the work now |
| max_accel 3000 | 500 | Slower, until `TEST_SPEED` proves otherwise |

transparent petg and gloss

`0.12mm Clear @Solder` + `Numakers PETG-HS Clear @Solder`, added 2026-09-08 for
the Transparent PETG-HS spool. **Both presets or neither** — fan and flow are
filament-level settings in Orca, and they are half the recipe.

Clarity is a density problem, not a material one. Light refracts at every air gap
between extrusions and at every interface that did not fuse, and enough of those
reads as milky. So the profile removes gaps rather than adding anything:

| Setting | Value | Why |
|---|---|---|
| `wall_loops` | 1 | every wall-to-infill boundary is an interface |
| `top_shell_layers` / `bottom_shell_layers` | 0 | a shell runs at a second angle — crossings scatter |
| `ensure_vertical_shell_thickness` | `none` | otherwise Orca puts solid infill back |
| `sparse_infill_density` | 100% | anything less is engineered air |
| `sparse_infill_pattern` | `alignedrectilinear` | one direction, no crossings |
| `infill_direction` | 0 | locked, so every layer lines up |
| all line widths | 0.5 mm | overextrude into what is left |
| outer/inner wall speed | 15 mm/s | time to fuse |
| `fan_min_speed` / `fan_max_speed` | 0 | cooling freezes the interface before it fuses |
| `slow_down_layer_time` | 12 | holds layer time by slowing, since the fan cannot |
| `filament_flow_ratio` | 1.00 | +5% against the opaque preset's 0.95 |

**Flow is the largest single lever**, and `rotation_distance: 34.406` is still
nominal, so `E_CAL_START` / `E_CAL_RESULT` comes before reading anything into a
flow number. Push toward 1.05 if the part is still milky.

Temperature stays **250 both layers**. Published clear recipes range 220 to 270;
this hotend is all-metal with PTFE cold-side only and PETG under about 245 skips
in it, so the low end is not available here. Above 250 gives microbubbles, which
is its own milkiness. **A damp spool cannot print clear at any setting.**

What the profile costs, all of it deliberate:

- no solid skin — optical parts only, never functional ones
- overhangs and bridges are poor, a direct consequence of 0% fan
- supports are off; a support contact face is a matte scar on a clear part
- slow. CNC Kitchen measured 50 min for a tensile coupon

Ceiling is semi-optical. FDM does not reach glass.

gloss is a different problem

Gloss is surface, clarity is bulk, and the two only partly overlap:

- **Bottom face is free** — a smooth PEI or glass plate prints a mirror, textured prints matte. Nothing in the slicer changes this.
- **Ironing** smooths flat top faces: 10–20 mm/s, flow ≤15%, spacing 0.15–0.25 mm. Useless on walls, slopes and domes, and useless here — `0.12mm Clear @Solder` has no top shell to iron. For a glossy top on an opaque part, use `0.12mm Fine @Solder` with `ironing_type: top surfaces`.
- **Walls** gloss up with the same levers clarity wants: slow, hot, no fan.
- **Post-process**: a heat-gun pass, or an epoxy/UV resin coat. PETG has no acetone equivalent — the solvents that touch it are hazardous and marginal.

sources, clear petg

cnc kitchen — measured settings and tensile data https://www.cnckitchen.com/blog/transparent-fdm-3d-prints-are-clearly-stronger
hackaday https://hackaday.com/2025/11/29/how-to-print-petg-as-transparently-as-possible/
prusa clear petg glass profile https://www.printables.com/model/240108-clear-prusament-petg-glass-profile
petg smoothing methods https://coex3d.com/blogs/blog/the-best-methods-for-petg-filament-smoothing
ironing guide https://www.snapmaker.com/blog/ironing-in-3d-printing/

first print checklist

Everything in [`calibration.md`](../setup/calibration.md) comes first. Then: slice
something small in `0.20mm Standard @Solder` with `Numakers PETG-HS @Solder`,
send it to `https://solder.knave`, and watch the first layer.
