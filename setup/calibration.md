calibration

Order matters — each step depends on the ones above it.

Done so far: the thermistor curve (step 0, settled — stock sensor, no change).
Both PID sets still belong to the old hotend, and the geometry steps are
untouched.

**Step 5 reopened 2026-08-12** — the old stock Ender 3 extruder went on, so the
2026-08-08 `rotation_distance` measurement no longer describes the hardware.

0. thermistor curve — settled 2026-08-08, no change needed

**The fitted thermistor is the stock one.** The V3 all-metal hotend was
built around the original sensor rather than the one it shipped with, so
`sensor_type: EPCOS 100K B57560G104F` is correct and stays.

Three things agree on this:

- the vendor's shipped Marlin sets `TEMP_SENSOR_0 1` and `TEMP_SENSOR_BED 1`
  (`printer-examples/Ender-3/.../Marlin/Configuration.h:286,291`). Marlin sensor
  table **1 is the EPCOS 100K curve** — the same one Klipper names
  `EPCOS 100K B57560G104F`. The config matches what the vendor assumes.
- 25 prints completed on this exact sensor and this exact curve (Cura era, PETG
  250 / PLA 230). A curve wrong by 5–10 °C at those temperatures would have shown
  up as stringing or poor adhesion across all of them.
- Only the **hot end** changed, not the sensor. A new block changes thermal mass
  and heat path, which invalidates the PID tune — it does not touch the
  resistance-vs-temperature curve.

The Beta 3950 parts on hand are **spare** hotend thermistors and a loose B3950
with an XH2.54 connector. Neither is fitted. If one is ever
swapped in, change to `sensor_type: Generic 3950` at the same time.

Residual uncertainty is component tolerance — a cheap bead may read a couple of
°C off the ideal EPCOS curve — not curve selection. Chasing that needs a
reference thermocouple and is not worth doing before a print exists to judge.

1. direction, before any homing

Park each axis mid-travel by hand, power on, then one at a time:

```
FORCE_MOVE STEPPER=stepper_x DISTANCE=10 VELOCITY=10
FORCE_MOVE STEPPER=stepper_y DISTANCE=10 VELOCITY=10
FORCE_MOVE STEPPER=stepper_z DISTANCE=5 VELOCITY=3
```

Positive must move each axis **away from its endstop** — X away from the left
switch, the Y bed away from its switch, Z gantry **up**. Wrong direction gets a
`!` on that `dir_pin`.

At `homing_speed: 50`, a backwards axis slams into the end of travel. This check
is not optional.

On Z, also confirm **both lead screws turn together and the same way**.

`FORCE_MOVE` ignores endstops and travel limits entirely.

Visibility note: `DISTANCE=20` with `rotation_distance: 40` is only **half a
turn**. Mark the shaft or you will not see it.

2. homing

One axis at a time, hand on the power switch: `G28 X`, `G28 Y`, `G28 Z`.

Endstops read `open` when connected and untriggered. All three reading
`TRIGGERED` means they are **unplugged** — with `^PAx` pullups, a floating pin
looks exactly like a pressed switch.

3. nozzle offset and travel limits

Direct drive moved the nozzle relative to the carriage. After homing works:

- Measure where the nozzle actually sits at X0 Y0 and correct
  `position_endstop`.
- Push X and Y through full travel **by hand, power off** first, confirming the
  printed mount clears the frame at both ends and does not foul the bed at the
  front. Reduce `position_max` if it does not.
- Only then set real `bed_mesh` `mesh_min`/`mesh_max`.

3b. z endstop after a hotend rebuild — 2026-08-12, resolved mechanically

**What actually happened:** step 2's escape hatch is what was needed. The nozzle
reached the bed before the switch triggered, so the **Z endstop bracket was slid
up a few mm** and the bed screws re-levelled up to meet the new Z0.
`Z_ENDSTOP_CALIBRATE` was never run — `position_endstop` is still `-0.080` and
`save_config_pending` is `False`. That is correct, not an omission: raising the
bracket lifts the nozzle at trigger, raising the bed brings the bed back to it,
and the paper level at Z0 is the calibration. Config never needed to know.

Consequence to remember: `position_max: 200` was measured from the old Z0, which
is now a few mm lower than the current one. The top of Z travel is that much
closer to the frame — check before printing anything near full height.

The procedure below is kept for the next rebuild.

procedure

The rebuilt hotend is **longer**, so the nozzle now sits lower relative to the X
gantry. The endstop bracket has not moved, so it still triggers at the same
gantry height — which means the nozzle reaches the bed *earlier* than it used to.
The saved `position_endstop = -0.080` describes the old assembly and is wrong.

**Do not `G28` first.** If the nozzle now needs to be below the bed surface for
the switch to trigger, the gantry cannot descend far enough, the nozzle jams into
the glass and the Z motor grinds. Drop the bed before homing.

1. **Tighten all four bed levelling knobs**, pulling the bed down to its lowest.
   That is maximum nozzle clearance and it is what makes the first `G28` safe.
2. `G28`, hand on the power switch. It should trigger the Z switch with visible
   air under the nozzle.
   - Still bottoms out on the bed with the knobs fully tightened? Then the
     springs cannot absorb the extra length: **power off and slide the Z endstop
     bracket up the extrusion**, then start again. No config value fixes this.
3. `Z_ENDSTOP_CALIBRATE`. It homes, lifts, and hands over to the manual probe
   helper.
4. Walk down with `TESTZ Z=-1`, then `-0.1`, then `-0.05`, paper under the
   nozzle, until the paper just drags. `TESTZ Z=+0.05` backs off if overshot.
   `ABORT` leaves everything untouched.
5. `ACCEPT`, then `SAVE_CONFIG` — Klipper restarts and rewrites
   `position_endstop` in the `SAVE_CONFIG` block.
6. The bed is now sitting low and unlevel: `BED_SCREWS_ADJUST` to re-level
   against the new reference, then `MAINT_RESET COMPONENT=bed`.

Two notes. `position_min` was widened to **-5** for this — `TESTZ` cannot travel
past it, so the old -2 could have stopped the probe short of the bed. And the old
`-0.080` had a **+0.4 mm babystep folded into it** from the first finished print;
this recalibration discards that, so expect to re-find any live-Z tweak from
zero rather than assuming the old feel carries over.

Nothing else keys off Z0 any more. The wipe macros did — their heights were
measured against the bed — and they are gone as of 2026-08-13 along with the bar
itself.

4. heaters, one at a time

`M104 S100` — watch for a smooth climb, no runaway. Then `M140 S60`.

Then, each followed by `SAVE_CONFIG` (which restarts Klipper):

```
PID_CALIBRATE HEATER=extruder TARGET=200
PID_CALIBRATE HEATER=heater_bed TARGET=60
```

5. extruder

Heat to 200 first — Klipper refuses to extrude below 170 °C, and forcing a cold
extrude strips filament in a direct drive.

Direction: `G91` then `G1 E10 F60`. Wrong way is a `!` on `dir_pin: PB4`.

`rotation_distance`: mark 120 mm of filament at the extruder inlet, command
`G1 E100 F60`, measure what remains. New value =
`old × (100 / actually_extruded)`. `E_CAL_START` / `E_CAL_RESULT` wrap this.

**Measured 2026-08-08.** `REMAIN=20` → 100.0 mm actual on 100.0 requested,
0.0 % off, so 32.000 was right for the extruder fitted then. That extruder is
off the machine.

**Outstanding since 2026-08-12.** The old stock Ender 3 extruder replaced it and
config now carries the nominal `34.406` — 200 × 16 / 93, the vendor's steps/mm,
with nothing measured behind it. Run `E_CAL_START TEMP=240` / `E_CAL_RESULT` and
write the number here. Expect it to land near 34.4 rather than 32; if it comes
back at 32 again, the extruder on the machine is not the one assumed here.

6. bed

`BED_SCREWS_ADJUST` with the four `[bed_screws]` positions already in config
(30.5/204.5 × 37/207).

Then `BED_MESH_CALIBRATE METHOD=manual` — no probe fitted, so the nozzle visits
each of the 4×4 points and you paper-gauge it.

Dual Z with a single driver cannot self-level. If the gantry is racked, **power
off** and turn one lead screw by hand.

7. speed and shaping

`TEST_SPEED SPEED=200 ACCEL=1000 ITERATIONS=5` — homes, hammers diagonals and a
box, re-homes. If the axes end up somewhere else, steps were lost and the limits
in config are fiction. Walk the numbers up from there, not down from optimism.

Config is at the floor as of 2026-08-12 (40 / 200 / SCV 2.0, Z 3 / 40), so
`TEST_SPEED` above those figures is testing `SET_VELOCITY_LIMIT`, not the config
— and per the `SET_VELOCITY_LIMIT` trap it leaves the raised limits in place
until `FIRMWARE_RESTART`. Restart after any speed session.

`[input_shaper]`: no accelerometer on hand, so print a ringing tower, measure
band spacing, compute frequency, then uncomment and set `shaper_freq_x/y`.
Matters more here than stock because the extruder now rides the X carriage.

8. pressure advance

Currently `0.0`. Direct drive typically lands **0.02–0.08** — nowhere near the
old bowden 0.85. Tune with `TUNING_TOWER` or Orca's built-in PA test.

order of worth

1. Thermistor curve — everything thermal is measured against it.
2. Direction checks — prevents a crash.
3. Nozzle offset — prevents printing off the bed.
4. PID — prevents heater faults mid-print.
5. `rotation_distance` — **reopened** by the 2026-08-12 extruder swap; the
   34.406 in config is nominal, not measured.
6. Pressure advance and input shaper — quality, not safety.
