what has actually been tested, as opposed to assumed

proven vs unproven

| Item | State |
|---|---|
| MCU core, flash, 72 MHz clock, USART1, CH340 | **verified** 2026-08-04 |
| Both thermistor ADC channels | **verified** — sane room-temp readings |
| A stepper driver sourcing real current | **verified** — Y holds against hand torque |
| All three endstops | **verified** — read `open`, read `TRIGGERED` when unplugged |
| Config parses, Klipper reaches `ready` | **verified** |
| Axis movement, all axes | **verified** 2026-08-04 |
| Motor direction signs | **verified** — homing works |
| Motor cable coil pairing | **verified by behaviour** — motors run correctly under load |
| Dual Z splitter pairing | **verified by behaviour** — Z drives both screws |
| Heaters | **verified** — hotend and bed reach temperature |
| Extrusion and melt | **verified** — filament feeds and melts |
| Extruder motor wiring | **verified** 2026-09-05 — rewired after a dead-motor fault; the driver was never involved |
| MCU case fans | **FAULT** — one of two not spinning, broken splice, see below |
| Nozzle offset, X/Y limits | **UNMEASURED** since direct drive |
| Thermistor curve | **confirmed** 2026-08-08 — stock sensor, stock EPCOS curve |
| Extruder `rotation_distance` | **UNMEASURED** — the 2026-08-08 100 mm test proved 32.000 for the extruder that came off; stock Ender 3 extruder fitted 2026-08-12, config now nominal 34.406 |

what bites

Facts that survived a session of finding out, kept because breaking them costs
a print or a board.

board and wiring

- The 4.2.7 swaps step/dir pairwise against the 4.2.2. Klipper's own
  `generic-creality-v4.2.7.cfg` is authoritative; every shipped
  `printer-creality-ender3-*.cfg` is a 4.2.2 map and must not be used here.
- The dead 4.2.2 died from motor wires in the wrong order, which fused a
  capacitor. Not a driver. Meter every motor cable's coil pairing and its
  end-to-end continuity before it touches this board.
- `emergency_stop` halts the MCU and disables the drivers, but **VMOT stays
  live on the motor connectors**. A swap after only an E-stop is a hot-plug.
  Power off at the PSU.
- One controllable fan output, `PA0`. Everything else is hard-wired 24 V
  always-on, so a fan that will not spin is never a config problem.
- Unconnected thermistor inputs float; a disconnected sensor reads as a
  plausible temperature rather than an obvious fault.
- The TMC2225s are standalone with no UART, soldered down. There is no
  `[tmc2225]` section and no `run_current` to lower — a driver fault scraps the
  board, and driver heat is managed by airflow alone.
- Five steppers on four drivers, dual Z sharing one through a parallel
  splitter, so each Z motor gets half the driver's current. Drivers are
  independent silicon: the Z pair cannot starve the extruder driver. The only
  mechanism that stops one motor at random is TMC2225 overtemperature
  shutdown, which clears on cooling and so explains nothing permanent.

motion and extrusion

- `rotation_distance: 34.406` is 200 × 16 / 93, the nominal figure for this
  extruder. **Not a measurement.** The 100 mm test that proved 32.000 was run
  against the extruder that has since been swapped out.
- `max_extrude_only_velocity` / `_accel` are set explicitly at 40 / 500, not
  derived from `[printer]`. Derived they would be 0.266 × the XY limits, and
  Klipper clamps extrude-only moves to them — a floored value strings PETG
  badly by throttling retraction.
- Skipping on every extrude was **the throat tube**, which had clogged and
  snapped on removal. Not the extruder, not the drivers, not the motion limits
  that were floored while chasing it.
- A dead extruder motor that vibrates without turning is one missing phase:
  split coil pairing, an open conductor, or a dead half-bridge. Two motors
  behaving identically on one port exonerates the motor. In the 2026-09-04 case
  it was the cable, fixed by rewiring.

z and the bed

- The longer hotend put the nozzle on the glass before the Z switch could
  trigger, so the endstop bracket was raised. `position_max: 200` still refers
  to the old Z0, a few mm below the current one.
- `G28` parks at bed centre — `[safe_z_home]`, `home_xy_position: 117.5, 117.5`,
  `z_hop: 10`. The hop fires even when Z is unhomed, which is what makes an
  X/Y homing sweep survivable with a part on the bed.
- The wipe bar is gone from the bed and its macros are deleted.
  `bed_exclude_area` is cleared to the full plate.

slicing

- **A 3MF carries its own process settings and they win.** Every support value
  in the first finished print came from the model file, not the Solder preset.
- `independent_support_layer_height = 1` makes a file non-uniform: 0.2 mm object
  layers alternating with 0.05 mm support slivers. A sliver carrying both
  support and object geometry cannot print, and that is what forced the pauses.
- The vendor's system profile sets support spacing to 0.2 mm against a generic
  default of 2.5. At a 0.38 mm line width that is effectively solid. Both
  process presets now pin the geometry explicitly.
- `pressure_advance` is a **slicer** setting here: the filament preset's
  `filament_start_gcode` runs `SET_PRESSURE_ADVANCE` at every print start, so
  the value in `printer.cfg` never applies.
- Retraction lives in two places and the **filament** preset wins over the
  machine preset.
- `SET_RETRACTION` does nothing with this output — `use_firmware_retraction = 0`
  and no `G10`/`G11` in the gcode, so `[firmware_retraction]` is never called.
  Retraction changes need a reslice.
- Travel speed is a `printer.cfg` lever, not a slicer one. Orca slices travel at
  120 mm/s and `max_velocity` clamps it.

filament

A tangle stalls the feed, the extruder grinds a flat onto the filament, and that
flat then jams the drive gear even after the tangle is freed. The spool is the
cause and the nozzle is the symptom — clear both, and cut the flat back before
reloading. The runout kit on hand is a break detector and will not catch this:
the filament never ran out, it stopped moving.

From the host side a tangle, a clog and a dead extruder motor are
indistinguishable. Klipper accepts every E move and reports success whether or
not plastic reaches the nozzle.

Remaining filament is tracked in Spoolman, bound to Klipper, reported per print.

resuming a print that lost extrusion

`PLR_SAVE` records where Klipper stopped, not where extrusion stopped. After an
extruder failure the machine keeps moving through air, so the saved offset
describes a part that was never printed. On 2026-09-05 that gap was 6.94 mm,
about 35 layers.

The resume point has to be measured off the part. Homing Z gives the print's own
`position_endstop` datum, so the reading needs no offset arithmetic — but
`[safe_z_home]` puts the nozzle at bed centre, and the object's own
`EXCLUDE_OBJECT_DEFINE` gave `CENTER=117.5,117.142`, so `G28 Z` would have
descended into the middle of the print. Retarget `home_xy_position` clear of the
first-layer footprint, home, measure, then put it back.

Resume the **last full layer**, not the one above: the nozzle lands slightly into
solid plastic and bonds, where the layer above floats in the gap. The cost is one
doubled layer, which is the only visible defect on the finished part.

`plr_z` is the nozzle's **physical** height, never the layer height — it feeds
`SET_KINEMATIC_POSITION`, and the gcode's own absolute `G1 Z` drops to the layer
by itself. Park at a known height and read it off the toolhead.

`PLR_SAVE` writes the **layer** height into `plr_z`. After a real power cut the
nozzle is at the layer, so the two meanings coincide and nothing catches it.
After an E-stop followed by homing they do not: `G28` leaves the nozzle at
`z_hop` 10, and declaring a saved 1.44 puts every later move 8.56 mm high.

So `RESUME_AFTER_POWER_LOSS` declares Z **only when Z is unhomed**. A homed Z is
Klipper's own endstop datum and beats any saved number. `PLR_RESUME_AT_Z`
refuses when Z is unhomed and no `PLR_Z` is given, because an unhomed toolhead
reports 0.0 and that would be written down and believed.

Purge by hand before resuming. Filament frozen in the melt zone comes back as
silent under-extrusion across the one layer that has to bond, and Klipper
reports success either way.

Outcome: completed, 11.94 h. Not push-button — finding contact is a manual jog
down onto the part at a decreasing step size, because there is no probe.
Tooling is [`resume-at.py`](../resume-at.py); the macro is `PLR_RESUME_AT_Z`.

next actions

1. **`E_CAL_START` / `E_CAL_RESULT`** — 34.406 is nominal, nothing has measured
   it on the fitted extruder.
2. `PID_CALIBRATE` both heaters — the values in config are the old hotend's.
3. Measure the direct-drive nozzle offset; fix X/Y `position_endstop` /
   `position_max`, then set real `bed_mesh` bounds.
4. `TEST_SPEED` to walk the limits up, then a manual `BED_MESH_CALIBRATE`.
5. Pressure advance from 0, then a ringing tower for `[input_shaper]`.
6. Fix the dead case fan — a broken splice, not a board fault.
7. Dry the PETG properly before a long print.
