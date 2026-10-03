electronics

Controller — V4.2.7

| | |
|---|---|
| MCU | STM32F103 (some batches GD32F303; same Klipper target) |
| Confirmed clock | 72 MHz — read back from Klipper `Stats freq=72002436` |
| Stepper drivers | TMC2225, **soldered down, not socketed** |
| USB bridge | CH340, `1a86:7523`, wired to **USART1 PA10/PA9** |
| Bootloader | 28 KiB — firmware links at `FLASH_START_7000` |

The drivers being soldered is the single most important fact about this board.
There is no single chip to swap. A blown driver scraps the whole board, which is
exactly what happened to the V4.2.2.

Pin map (verified 2026-08-01 against Klipper's `generic-creality-v4.2.7.cfg`)

The 4.2.7 **swaps step and dir pairwise** relative to the 4.2.2. Every pin in
the old Pi-era config was wrong.

| Block | 4.2.2 (old, wrong here) | 4.2.7 (in use) |
|---|---|---|
| `stepper_x` | `step PC2` / `dir PB9` | `step PB9` / `dir PC2` |
| `stepper_y` | `step PB8` / `dir PB7` | `step PB7` / `dir PB8` |
| `stepper_z` | `step PB6` / `dir !PB5` | `step PB5` / `dir !PB6` |
| `extruder` | `step PB4` / `dir PB3` | `step PB3` / `dir PB4` |

Identical on both boards: `enable_pin: !PC3` (shared by all four), endstops
`^PA5` / `^PA6` / `^PA7`, hotend heater `PA1`, hotend sensor `PC5`, bed heater
`PA2`, bed sensor `PC4`, part fan `PA0`.

Moved: `FIL_RUNOUT` from `PC6` (4.2.2) to **`PA4`** (4.2.7).

Probe header aliases: `PROBE_IN=PB0`, `PROBE_OUT=PB1`, silkscreened
**`G V IN G OUT`** left to right — named from the probe's side, so `IN` is the
control line and `OUT` is the sensor line. For a BLTouch/3D Touch
that is `control_pin: PB0`, `sensor_pin: ^PB1`.  Wire colours, the
reason not to hang the signal off the Z endstop port, and the bring-up order are
in [`probe.md`](probe.md).

Direction signs (`!`) vary by batch and by how a cable was crimped. Expect to
flip one or two after the first motion test — normal, not a fault.

connectors — what plugs in where

Read the silkscreen; every connector is labelled on the board.

| Connector | Type | Wires | Polarity |
|---|---|---|---|
| Power in (`24V`, `+ −`) | green screw terminal, 2-pos | PSU **red = V+**, **black = COM** | **Critical.** Reversed kills the board instantly |
| Hot bed (`HB`) | green screw terminal, 2-pos | bed red + black | Resistive, electrically doesn't matter; put red on `+` |
| Hotend heater | JST XH 2-pin | 2 cartridge wires | Resistive, doesn't matter |
| Part cooling fan | JST XH 2-pin, driven by `PA0` | red +, black − | Matters — reversed simply won't spin |
| Hotend heatsink fan | JST XH 2-pin, **always-on 24 V**, position moved on the 4.2.7 | red +, black − | Matters |
| MCU / case fans | always-on 24 V | red +, black − | Matters |
| Thermistors (bed, hotend) | JST XH 2-pin | both same colour | Doesn't matter |
| Endstops X/Y/Z | 3-pin keyed; **Z position moved** on the 4.2.7 | — | keyed |
| Motors X/Y/Z/E | JST XH 2.54 4-pin | see below | **pairing is critical** |

Only two red/black pairs can destroy anything: **PSU input** (reversed = dead
board) and **fan headers** (reversed = no spin). Everything else red/black is a
heater, which is just a resistor.

fans — there is only one controllable output

Klipper's own `generic-creality-v4.2.7.cfg` defines exactly one fan pin:

```
[fan]
pin: PA0
```

That is **part cooling only**. The hotend heatsink fan and the MCU/case fans sit
on hard-wired always-on 24 V headers. There is no second PWM output, so:

- No `[heater_fan]` or `[controller_fan]` can be configured for them — there is
  no pin to give it.
- A fan on those headers spins whenever 24 V is present, or it is a hardware
  fault: no 24 V at the header, reversed polarity, wrong-voltage fan, or a dead
  fan.

**Open issue 2026-08-04:** MCU case fans are not spinning. See
[`bringup-log.md`](../log/bringup-log.md).

motor cables

| | |
|---|---|
| Board end | JST XH 2.54 mm, 4-pin, white |
| Motor end | JST PH 2.0 mm, 6-pin, black/white |
| Cable | 4-wire, unshielded, 26 AWG stranded |
| Lengths | ~1000 mm (X, Y, E), ~1200 mm (Z) |
| Wire colours | Red, Blue, Green, Black — **order varies by batch, do not trust colour** |

Pairing at the board-side connector: `pin1=2B, pin2=2A, pin3=1A, pin4=1B`.
**Pins 1+2 are one coil, pins 3+4 are the other.**

Meter every cable, every time, board unplugged and unpowered:

| Probe | Expect |
|---|---|
| 1 ↔ 2 | 2–4 Ω |
| 3 ↔ 4 | 2–4 Ω |
| 1↔3, 1↔4, 2↔3, 2↔4 | OL |
| any pin ↔ motor body | OL |

A **2–4 Ω where OL belongs means crossed pairs**, and that cable will kill a
driver on the first pulse. Reversing a whole coil is harmless — the motor spins
backwards and you fix it with `!` in config. Crossing the pairs is what
destroys hardware.

An **OL where 2–4 Ω belongs** is an open coil — broken conductor or an unseated
crimp. It presents as a motor that locks hard but will not rotate.

Two different connector types on one cable is exactly how the pinout got
scrambled the first time.

PSU

CMS-350-24, 24 V 350 W, 215 × 145 × 60 mm. Check the 115/230 V selector
matches the wall before first power-on. Output must read **24 V ± 0.5** unloaded;
over 25 V, do not connect the board.

The alternative on hand is a LRS-350-24 ("slim"), unused, part of the
retired Config A.

safety rules

1. **Never plug or unplug a stepper with the printer powered.** The inductive
   spike kills drivers outright. This destroys more boards than miswiring does.
2. Never power the board with a motor cable dangling where its pins can touch
   the frame.
3. Frame ↔ each heater and thermistor lead must read OL.
