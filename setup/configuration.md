configuration

Live config lives on knave at `/srv/klipper/config/`. Copies of every file are in
[`config/`](../config/), pulled 2026-08-04.

Files: `printer.cfg` (machine), `macros.cfg` (`_CLIENT_VARIABLE`, START_PRINT /
END_PRINT / PARK / preheats / COOLDOWN / TEST_SPEED / E_CAL_START /
E_CAL_RESULT), `plr.cfg` (power-loss recovery only, see
[`power-loss-recovery.md`](power-loss-recovery.md)), `maintenance.cfg` (service
counters only since 2026-08-13), `mainsail.cfg` (vendor UI macros,
`virtual_sdcard`), `moonraker.conf`, `shell_command.cfg` (orphaned — no
`[include]` references it).

`_CLIENT_VARIABLE` in `macros.cfg` is the supported override point for the
read-only vendor `mainsail.cfg`. All three slots — `user_pause_macro`,
`user_resume_macro`, `user_cancel_macro` — are present and empty (`""`). The
first two held `WIPE_NOZZLE` until the wipe bar came off the bed.

preheat presets

`PREHEAT_PLA` 230/60 · `PREHEAT_PETG` 250/80 · `PREHEAT_PETG_HS` 250/80 ·
`PREHEAT_ABS` 250/100 · `PREHEAT_BED_ONLY` 80 · `COOLDOWN`. All live in
`macros.cfg`.

PLA and PETG values are not guesses — they are what 25 completed prints on this
machine actually used. See [`slicer.md`](../slicer/slicer.md).

current values

| Section | Setting | Value | Note |
|---|---|---|---|
| `printer` | `kinematics` | cartesian | |
| | `max_velocity` / `max_accel` | 150 / 500 | at or below the vendor firmware; not a measured limit — run `TEST_SPEED` before a long print |
| | `square_corner_velocity` | 5.0 | |
| | `max_z_velocity` / `max_z_accel` | 5 / 100 | keep low, dual Z shares one driver |
| `stepper_x` | step / dir | `PB9` / `PC2` | 4.2.7 map |
| | `rotation_distance` | 40 | 20T GT2 |
| | `endstop_pin` / `position_endstop` / `position_max` | `^PA5` / 0 / 235 | **offsets unverified since direct drive** |
| `stepper_y` | step / dir | `PB7` / `PB8` | |
| | `endstop_pin` / `position_max` | `^PA6` / 235 | same caveat |
| `stepper_z` | step / dir | `PB5` / `!PB6` | drives **both** Z motors |
| | `rotation_distance` | 8 | T8×2 lead screw |
| | `endstop_pin` / `position_max` | `^PA7` / 200 | |
| `extruder` | step / dir | `PB3` / `PB4` | |
| | `rotation_distance` | 34.406 | **nominal, unmeasured** — vendor 93 steps/mm. Re-measure with `E_CAL_START` |
| | `sensor_type` | EPCOS 100K B57560G104F | stock sensor, kept through the hotend swap |
| | `max_extrude_only_velocity` / `_accel` | 40.0 / 500.0 | set explicitly, never derived from `[printer]` (0.266× each). Extrude-only moves are **clamped** to these, not rejected, so an under-set value shows up as stringing, never an error |
| | `min_temp` / `max_temp` | 0 / 300 | |
| | PID | Kp 21.527 / Ki 1.063 / Kd 108.982 | **stale** — old hotend |
| | `pressure_advance` | 0.0 | retune for direct drive, expect 0.02–0.08 |
| `heater_bed` | PID | Kp 54.027 / Ki 0.770 / Kd 948.182 | **stale** |
| | `min_temp` / `max_temp` | 0 / 130 | |
| `fan` | pin | `PA0` | the only controllable fan output |
| `firmware_retraction` | length / extra | 0.6 / 0.0 | direct-drive values |
| `idle_timeout` | timeout | 600 s | disables steppers, kills heaters |
| `board_pins` | `FIL_RUNOUT` | `PA4` | 4.2.7 pin |

Also enabled: `[exclude_object]`, `[gcode_arcs]`, `[force_move] enable_force_move: True`,
`[bed_screws]`, `[save_variables]`, `[input_shaper]`, `[bed_mesh]`,
`[temperature_sensor mcu_temp]`.

`[safe_z_home]` is **active** — `home_xy_position: 117.5, 117.5`, `z_hop: 10`, so
`G28` parks the nozzle at bed centre rather than a corner. No probe is involved;
it is only about where the nozzle sits when Z comes down.

Staged but commented: `[bltouch]`, `[filament_switch_sensor]`.

change log — 2026-08-04

Backups on knave: `printer.cfg.pi-original`, `.pre-427-pinmap`,
`.pre-directdrive`, `.pre-tier1`; `macros.cfg.pre-tier1`;
`mainsail.cfg.pi-original`.

| Setting | Was | Now | Why |
|---|---|---|---|
| all four `step_pin`/`dir_pin` | 4.2.2 map | 4.2.7 map | the 4.2.7 swaps them pairwise; every pin was wrong |
| `[save_variables] filename` | `~/printer_data/...` | `/opt/printer_data/...` | `~` = `/home/klipper`, absent in container — Klipper would not start |
| `[virtual_sdcard] path` | `~/printer_data/gcodes` | `/opt/printer_data/gcodes` | same |
| extruder `min_temp` | −30 | 0 | `min_temp` **is** the disconnected-thermistor check; −30 widens it past any real ambient |
| `pressure_advance` | 0.85 | 0.0 | bowden value, ~15× too high for direct drive |
| `retract_length` / `unretract_extra_length` | 0.12 / 0.2 | 0.6 / 0.0 | bowden leftovers |
| `max_velocity` / `max_accel` | 300 / 3000 | 200 / 1000 | direct drive adds carriage mass |
| `FIL_RUNOUT` | `PC6` | `PA4` | `PC6` is the 4.2.2 pin |

Added the same day: `[input_shaper]` (values commented pending a ringing tower),
`[bed_mesh]` 4×4 bicubic for manual probing, `[temperature_sensor mcu_temp]`,
commented `[bltouch]`, `[safe_z_home]`, a `TEST_SPEED` macro, and a
direct-drive rework of `START_PRINT`.

Removed: `sonar.conf` — a Pi Wi-Fi keepalive, meaningless on wired knave.

START_PRINT rework

Three changes from the bowden version:

1. Bed heats and the machine **homes before the nozzle is at temperature**, so a
   direct-drive hotend is not oozing across the bed during `G28`.
2. Prime line cut from `E15`/`E30` to `E10`/`E20`. The line geometry
   (0.3 × 0.4 × 180 mm = 21.6 mm³) needs ~9 mm of 1.75 mm filament per line; the
   old value over-purged by roughly 60 %.
3. Ends on a 0.6 mm retract instead of a bowden-sized one.

nozzle wipe — gone

**Removed 2026-08-13.** The Hi Mouth bar was taken off the bed, and the
macros went with it: `WIPE_NOZZLE`, `_WIPE_GUARD`, `WIPE_LEFT_PROBE`,
`WIPE_FRONT_PROBE`, `WIPE_SPOT`, `WIPE_TRACE` are all deleted from
`maintenance.cfg`. It had already been unhooked from every caller on 2026-08-12;
this is the rest of it.

What that leaves:

| | |
|---|---|
| `_CLIENT_VARIABLE` `user_pause_macro` / `user_resume_macro` | present, uncommented, `""` |
| `START_PRINT`, `END_PRINT` | no wipe call, commented or otherwise |
| Orca `bed_exclude_area` | `[]` — the whole 235×235 plate is printable again |
| `variables.cfg` | never held wipe state, nothing to clean |

Nothing in the printer or the slicer now reserves the front-right strip. The old
geometry (X180 → X220 along Y225, `wipe_z` 4.2 above a 2 mm platform) described
one specific stuck-down bar and is dead the moment the bar moves — recover the
macros from git history if one goes back on, then re-measure from scratch with a
fresh siting pass rather than trusting those numbers.

maintenance counters

`MAINT_LOG_PRINT` (called by `END_PRINT`) accumulates hours and print count into
`variables.cfg`. It also nags on the console once three prints have passed since
the last bed adjust — clear with `BED_SCREWS_ADJUST` then
`MAINT_RESET COMPONENT=bed`. `MAINT_STATUS` prints all counters.

extruder calibration

`E_CAL_START TEMP=240` heats, waits, and extrudes 100 mm at 1 mm/s.
`E_CAL_RESULT REMAIN=<mm>` prints the new `rotation_distance`. Two macros rather
than console gcode because Fluidd's console takes one line at a time and `M104`
does not wait. `max_extrude_only_distance` was raised to 200 for headroom.

**Run 2026-08-08: 120 mm mark, `REMAIN=20` → actual 100.0 mm on 100.0 requested,
0.0 % off.** That validated `rotation_distance: 32.000` — for the extruder that
was fitted then.

**Void since 2026-08-12.** The old stock Ender 3 extruder went on, config moved
to the nominal `34.406` (200 × 16 / 93), and no measurement has been taken
against it. Re-run `E_CAL_START` / `E_CAL_RESULT` before trusting a print, and
record the result here.

z reference

`Z_ENDSTOP_CALIBRATE` writes `position_endstop` into the `SAVE_CONFIG` block —
`-0.105` originally, then `-0.080` on 2026-08-08. `[stepper_z] position_min` must
stay **below** whatever is in there; at 0 Klipper refuses to load with
*"position_endstop in section 'stepper_z' must be between position_min and
position_max"*.

**`position_min` widened -2 → -5 on 2026-08-12.** The rebuilt hotend is longer,
so the nozzle sits lower at the moment the endstop triggers and the new
`position_endstop` goes further negative than -2 could hold. It also matters
during the calibration itself: `TESTZ` will not travel past `position_min`, so
too tight a value leaves you unable to walk the nozzle down to the bed at all.
Once the new endstop figure is known, `position_min` can come back to just below
it — `-5` is headroom for the procedure, not a target.

known-stale, needs the machine running to fix

- Both PID sets — old hotend, old thermal mass.
- X/Y `position_endstop` and `position_max` — direct-drive nozzle offset.
- `bed_mesh` `mesh_min`/`mesh_max` — provisional 30,30–200,200, must be inside
  what the nozzle can actually reach.
- `input_shaper` frequencies — unmeasured.

repo sync

The tracked copy under `chip-rpi/printer_data/config/` is the **retired Pi's**
config and is stale in every respect. [`config/`](../config/) here is the current
one. The old tree should be removed or clearly marked once the move settles.
