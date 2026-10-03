3d touch probe — wiring and bring-up

Pins: [`electronics.md`](electronics.md) ·
Procedures: [`calibration.md`](../setup/calibration.md) ·
Mount: [`printed-parts.md`](printed-parts.md)

The probe is a **3D Touch** (BLTouch clone, unused).
It was blocked on a duct with no probe boss; a Satsana remix that carries one is
being printed now, so this is the wiring and the bring-up that follows it.

Nothing here is deployed. `[bltouch]` is still commented out in `printer.cfg`.

what comes out of the probe

Five wires in two connectors. Colours are the same on genuine BLTouch and on
every clone worth buying:

| Connector | Wire | Meaning |
|---|---|---|
| 3-pin (servo) | **brown** | GND |
| | **red** | +5 V |
| | **yellow** (orange on some) | control — the servo-style pulse that deploys and stows the pin |
| 2-pin | **black** | GND |
| | **white** | signal — pulled by the probe when the pin triggers |

Both GNDs are the same net inside the probe. Some clones ship the two connectors
merged into one 5-pin plug that fits the board directly; that is the easy case.

Where it goes on the 4.2.7

**The dedicated 5-pin probe header, and nowhere else.** Klipper's
`generic-creality-v4.2.7.cfg` names its two signal pins:

```
aliases: ... PROBE_IN=PB0, PROBE_OUT=PB1, FIL_RUNOUT=PA4
```

which for a BLTouch is `control_pin: PB0`, `sensor_pin: ^PB1`. The header also
carries +5 V and GND, so all five probe wires land on that one connector.

**Do not improvise the signal wire onto the Z endstop port.** It looks tempting —
`^PA7` is right there and the switch becomes redundant anyway — but on the
STM32F103 `PA7`, `PB0` and `PB1` are all ADC-capable pins and **none of them are
5 V tolerant**. The endstop port is designed for a dry switch that only ever
shorts to GND, so nothing there conditions a 5 V push-pull output. The probe
header is where the vendor expects a 5 V probe signal and where whatever
conditioning the board has actually sits. Use it.

header pinout

The header is silkscreened **`G V IN G OUT`, left to right**, and the names are
from the *probe's* point of view — `IN` is the signal going into the probe, `OUT`
is the one coming back. The grouping is the giveaway: `G V IN` is the 3-pin servo
plug and `G OUT` is the 2-pin, in that order.

```
  G      V      IN       G       OUT
  │      │      │        │        │
brown   red   yellow   black    white
 GND   +5 V  control     GND    signal
       <-- 3-pin -->    <-- 2-pin -->

 IN  = PB0 -> control_pin
 OUT = PB1 -> sensor_pin (^PB1)
```

**Wire by colour, not by plug position.** The 3-pin housing does not necessarily
come crimped in `brown, red, yellow` order — check it against the silkscreen
before it goes on, and re-pin the housing (lift the tabs with a needle) or use
three separate leads if it disagrees. Plugging a 3-pin housing in blind because
it fits is how +5 V ends up on a signal pin.

One check with the meter, board unpowered and probe unplugged: **brown ↔ black
must read ~0 Ω**, because both are the same GND net inside the probe. If they do
not, the cable is not a standard one and none of the colours above can be
trusted. The board-side sanity check is continuity from either `G` pin to the
PSU `COM` terminal.

Only +5 V and GND can damage anything. Get those two right and the worst a
mistake does is a probe that sits there ignoring you.

routing

The cable runs up the X gantry with the hotend loom. Keep it clear of the heater
cartridge leads — the probe's signal line is a slow logic level and the heater
is 24 V switching at 100 W. Leave enough slack for full X travel **and** full Z,
and check it does not foul the Satsana duct's blower.

config

Uncomment the block in `printer.cfg` and fill in the offsets:

```
[bltouch]
sensor_pin: ^PB1     # header pin OUT, white
control_pin: PB0     # header pin IN, yellow
x_offset: 0          # measure — see below
y_offset: 0          # measure — see below
z_offset: 0          # PROBE_CALIBRATE writes this, do not guess it
speed: 3
samples: 2
```

Three other things change with it, and all three are easy to miss:

**1. `[stepper_z]` loses its endstop.** Delete `endstop_pin` and
`position_endstop` from the section, and delete the
`#*# [stepper_z] position_endstop = -0.080` pair from the `SAVE_CONFIG` block at
the bottom of the file — a leftover there conflicts with the virtual endstop and
Klipper refuses to start. Replace with:

```
endstop_pin: probe:z_virtual_endstop
```

`position_min: -5` already gives `PROBE_CALIBRATE` room to go below zero. Keep
it. The physical Z endstop switch can stay bolted to the frame; it is simply
unused, and its pin is free.

**2. `[safe_z_home]` homes the *nozzle*, so it has to be shifted** or the probe
hangs off the bed at `G28`. The probe lands at bed centre when:

```
home_xy_position: 117.5 - x_offset, 117.5 - y_offset
```

With a typical left-mounted Satsana probe (`x_offset` around −40) that is
`157.5, 117.5`.

**3. `[bed_mesh]` bounds are in probe coordinates, not nozzle coordinates.**
`mesh_min`/`mesh_max` say where the *probe* touches, and Klipper drives the
nozzle to `point − offset` to get it there. `[stepper_x] position_min` is `0`, so
there is no travel left of the bed at all — with `x_offset: -40`, the current
`mesh_min: 30, 30` becomes unreachable and Klipper errors out. The rule is:

```
mesh_min_x >= |x_offset|        (when x_offset is negative)
mesh_max_x <= 235 - x_offset    (when x_offset is positive)
```

Same for Y. Recompute both corners once the offsets are measured, and drop the
`METHOD=manual` note in the `[bed_mesh]` comment while you are there.

measuring the offsets

`x_offset`/`y_offset` are pure geometry — the probe pin's position relative to
the nozzle tip, `+X` right and `+Y` toward the back of the machine. Two ways,
in order of preference:

1. **From the mount's model.** Whatever Satsana remix gets printed states the
   offsets, because they are fixed by the boss position. Trust it, then check it.
2. **Mark and measure.** Home, drop a sheet of paper on the bed, jog the nozzle
   down to just touch and mark the spot; jog until the *probe pin* is over the
   same paper, deploy it with `BLTOUCH_DEBUG COMMAND=pin_down` and mark again.
   The vector between the marks is the offset. Calipers on the printed mount is
   the sanity check, not the measurement.

`z_offset` is **not** measured by hand. `PROBE_CALIBRATE` does it and writes the
result to `SAVE_CONFIG`.

bring-up order

Power on with the probe wired and the config still commented out — the probe
does its own self-test with no firmware involved:

1. **At power-on the pin drops and raises twice, then the red LED sits steady.**
   That alone proves +5 V, GND and the probe itself. A blinking red LED means
   the pin is stuck or the probe has faulted.
2. Uncomment `[bltouch]`, keep the physical Z endstop for now, `FIRMWARE_RESTART`.
3. `BLTOUCH_DEBUG COMMAND=pin_down` then `COMMAND=pin_up`. The pin must move.
   This tests `control_pin` only.
4. With the pin down, `QUERY_PROBE` reports `open`. Push the pin up by hand and
   `QUERY_PROBE` again — it must report `TRIGGERED`. This tests `sensor_pin`.
   **Do not move to step 5 until this works**; a probe that deploys but never
   reports is a nozzle driven into the bed.
5. Switch `[stepper_z]` to `probe:z_virtual_endstop`, shift `[safe_z_home]`,
   `FIRMWARE_RESTART`, then `G28` with a hand on the power switch.
6. `PROBE_ACCURACY`. Range under 0.01 mm is a good genuine BLTouch; a clone at
   0.02–0.03 mm is normal and still usable. Worse than that is a loose mount,
   not a bad probe.
7. `PROBE_CALIBRATE`, paper-gauge, `ACCEPT`, `SAVE_CONFIG`.
8. `BED_MESH_CALIBRATE` — automatic now, no `METHOD=manual`.
9. `[screws_tilt_adjust]` becomes worth adding: it turns bed levelling into
   "turn the front-left knob 40 minutes clockwise" instead of paper under four
   corners.

if it misbehaves

| Symptom | Cause |
|---|---|
| Pin never moves, LED steady | Yellow is not on `IN`. Check the crimp order in the 3-pin housing before touching the config — the silkscreen is not ambiguous |
| `BLTouch failed to verify sensor state` | Clone in touch mode. Add `pin_up_touch_mode_reports_triggered: False` |
| Deploys, probes, never triggers | Signal wire, or the clone is push-pull where the board wants open drain. Try `probe_with_touch_mode: True` |
| Pin down at power-on, blinking red | Pin jammed or bent. Straighten it; they bend on the first crash |
| Triggers early and inconsistently | Mount flex. The printed boss is the usual culprit, not the probe |
| Homes into the bed | Stop. `QUERY_PROBE` never worked — go back to step 4 |

`set_output_mode: 5V` is a **genuine BLTouch v3.x** setting. Clones ignore it,
and setting it on a clone that does not implement the command can leave the
probe in a bad state. Leave it out.

---

Prev: [`electronics.md`](electronics.md) ·
Next: [`calibration.md`](../setup/calibration.md)
