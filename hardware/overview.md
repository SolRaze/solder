overview — what solder is now

**Solder** is the whole unit: a Ender 3 frame, heavily deviated from
stock, driven by Klipper running in Docker on **knave**.


identity

| | |
|---|---|
| Kinematics | Cartesian (**not** CoreXY) |
| Nominal volume | 235 × 235 × 200 mm |
| Nozzle | 0.4 mm |
| Controller | V4.2.7 |
| Host | knave, x86_64 — Klipper in Docker |
| Firmware | Klipper `v0.13.0-700-gd6ea62542` (not Marlin) |
| PSU | CMS-350-24, 24 V 350 W ("fat" PSU) |

The host is x86_64, not a single-board computer. Any note describing an SBC
host is stale.

`chip` is the older name for the same box and is deliberately kept where it
already exists — the `chip` branch of the dotfiles repo, and `chip-rpi/` here.

deviations from stock

Every one of these invalidates some piece of stock Ender 3 documentation.

direct drive

Stock motor and stock extruder relocated onto the X gantry on a printed
bracket. Consequences that are still unresolved:

- The nozzle sits at a **different offset** relative to the X carriage, so
  `position_endstop` and `position_max` for X and Y do not describe the machine
  as built. Unmeasured.
- The carriage is heavier, so acceleration was dropped from 3000 to 1000.
- `pressure_advance` went from a bowden 0.85 to 0.0 pending a retune. Direct
  drive lands somewhere around 0.02–0.08.
- Retraction dropped from bowden lengths to 0.6 mm.
- The bowden tube and its PC4-M6/M10 fittings are out of the filament path
  between extruder and hotend.

dual z

the vendor Dual Screw Rod Upgrade Kit. Two Z motors, **one driver** — the 4.2.7
has a single Z output, so both motors run off it through a splitter.

- Wired in parallel, each motor receives **half** the driver's current. Keep
  `max_z_velocity: 5`.
- Both motors' coil pairing must match. Mismatched, they fight each other and
  stress the one driver that runs them.
- **`z_tilt` is impossible** — it needs independent drivers. Gantry rack is
  corrected by hand, power off, by turning one lead screw.
- One Z endstop only.

toolhead

- **V3 hotend**, all-metal high flow. Replaces the stock PTFE-lined MK8.
  All-metal means it will tolerate higher temperatures, and it means the old
  PID values describe a completely different thermal mass.
- **Throat tube replaced 2026-08-12.** The original clogged, then **snapped while
  being removed**. A broken throat was the real cause of the "extruder skips on
  every extrude" fault — the extruder was never at fault. The replacement is an
  all-metal heatbreak with a **PTFE feeder tube above it on the cold side**, so
  it is thermally all-metal and PETG stays at 250 °C. The PTFE must seat hard
  against the top of the heatbreak — the gap is where the last one clogged — and
  the always-on heatsink fan is what keeps that PTFE cool.
- **Satsana duct** with a **5015 blower** for part cooling, replacing the stock
  4015 arrangement.
- Hotend heatsink fan and MCU case fans on always-on 24 V headers.
- The hotend thermistor is **the stock sensor**, kept through the hotend
  swap — so `sensor_type: EPCOS 100K B57560G104F` is correct. The Beta 3950
  thermistors in inventory are spares, not fitted. See
  [`calibration.md`](../setup/calibration.md).

not fitted, on hand

- **3D Touch sensor** (BLTouch clone) — bought, unused, blocked on the lack of a
  duct that carries a probe mount. See [`printed-parts.md`](printed-parts.md).
- **Filament Break Detection Kit** — wiring pin is `PA4` on this board, stubbed
  and commented in the config.

history that matters

The **V4.2.2 board is dead** — visibly burnt. Cause is known: motor wire pins
were in the wrong order, which destroyed a stepper driver. the vendor solders its
drivers down, so a dead driver scraps the board. The V4.2.2 was not lost that
way though — wrong motor wire order fused a capacitor.

That is why metering every motor cable against its header, before power, is not
optional paperwork. The same cables are now plugged into the last good board.
