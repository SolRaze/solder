bill of materials — as built

What is **on this machine right now**. Spares and the wider parts pile are tracked
outside this repo.

Source column: `Stock` = shipped with the printer | `ordered` = bought in | `local` = local shop.

electronics

| Part | Source | Notes |
|---|---|---|
| Mainboard V4.2.7 | Stock | STM32F103/GD32F303, TMC2225, **fitted** |
| PSU Fat 350 W | Stock | CMS-350-24, 24 V, 215×145×60 |
| Endstop switches X/Y/Z | Stock | mechanical, 3-pin |
| Wiring loom | Stock | motors, endstops, fans, thermistors |
| Micro USB-A to Micro-B cable, 100 cm | a vendor #21491 | board ↔ knave |

Not fitted, on hand: Mainboard V4.2.2 (**dead, burnt**), PSU Slim 350 W (LRS-350-24), DWIN 480×320 LCD ×2, Arduino Mega 2560 + RAMPS 1.4 + DRV8825
(a whole alternative controller stack), Raspberry Pi Zero 2 W (**retired**),
3D Touch sensor (blocked on a duct mount), Filament Break Detection
Kit + cable, XL6009 step-up converter.

toolhead

| Part | Source | Notes |
|---|---|---|
| Hotend V3 | ordered | all-metal high flow, **fitted**. Sold under a "High Temp High Flow Pro" name; the unit on the machine is the **V3** |
| Hotend accessory kit | ordered | |
| Throat tube 2.0 | ordered | |
| Throat tube, replacement | see above | **fitted 2026-08-12**, all-metal heatbreak with a cold-side PTFE feeder above it. The previous throat clogged and **snapped during removal** — that broken throat, not the extruder, is what made the machine skip filament on every extrude. Record which of the three spare throat parts actually went on (Throat Tube 2.0 / titanium alloy throat / throat tube kit) and strike the other two |
| Nozzle 0.4 mm | Stock / ordered | MK8 compatible, M6 |
| Heater cartridge 24 V 40 W | Stock | ~14.4 Ω |
| Hotend thermistor | Stock / ordered | Stock sensor kept through the hotend swap — EPCOS curve confirmed 2026-08-08 |
| 5015 blower (part cooling) | ordered / ordered | in the Satsana duct |
| 4010 axial (heatsink) | ordered / ordered | always-on 24 V |
| Extruder (stock MK8 style) | Stock | relocated to the gantry — **direct drive** |
| Extrusion mechanism kit | ordered | |

Out of the filament path now that it is direct drive: bowden tube, PC4-M6 and
PC4-M10 fittings.

motion

| Part | Source | Notes |
|---|---|---|
| Stepper motor 42-34 ×4 | Stock | NEMA17 1.8°, X, Y, Z, E |
| Dual screw rod upgrade kit | ordered | **second Z**, both motors on one driver |
| GT2 belts X 765 mm / Y 720 mm | Stock | 6 mm closed loop |
| GT2 pulley 20T ×4 | Stock | 5 mm bore — sets `rotation_distance: 40` |
| Z leadscrew T8×2 | Stock | sets Z `rotation_distance: 8` |
| Z anti-backlash nut, coupler | Stock | |
| V-slot POM wheels ×13 | Stock | with 625ZZ |

The dual Z kit is the reason `z_tilt` is impossible and gantry rack is a manual,
power-off job.

frame and bed

| Part | Source | Notes |
|---|---|---|
| 4040 / 2040 / 2020 extrusions | Stock | standard Ender 3 frame |
| Heated bed 235×235 | Stock | alu + PCB heater |
| Bed thermistor | Stock | NTC 100 kΩ, Beta 3950 |
| Build surface | ordered | PEI sheet + magnetic base, 220×220 — **note: smaller than the 235×235 bed** |
| Carborundum glass plate | Stock | 235×235×4, alternative surface |
| Bed springs / levelling knobs | Stock | |

The 220 × 220 PEI sheet on a 235 × 235 bed means usable area is smaller than
`position_max` claims. Worth confirming against the bed mesh bounds.

printed parts

Direct drive bracket, Satsana 5015 duct, dual-Z hardware — all in
[`printed-parts.md`](printed-parts.md), which is also where the source models get
recorded.

