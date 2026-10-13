hotend

![toolhead, six sides](model/toolhead.png)

ender-3 v3 se hotend | fitted | recorded 2026-10-12 | 0.4 nozzle

pins [`electronics.md`](electronics.md) | procedures [`calibration.md`](../setup/calibration.md) | sources [`references.md`](../references.md)

what it is
v3 se heater block, heatsink, heater and nozzle | stock ender 3 heatbreak | stock ender 3 thermistor
heatbreak is the MK8 type | PTFE-lined through to the nozzle | PTFE sits in the melt zone
PETG at 250 °C | never above 260 | the always-on heatsink fan is load-bearing
v3 se vendor rating nozzle temperature ≤ 260 °C
the v3 se heatbreak and thermistor came off before fitting | kept as spares
heater on `PA1` | sensor on `PC5` | same board pins as before
heatsink fan stays on the always-on 24 V header | the v3 se switches its own on `PC1`, this board has no spare fan output

vendor firmware values
source `Marlin/Configuration.h` | `CrealityOfficial/Ender-3V3-SE` at `e7b2bad8ff23`

| Setting | Value | Line | Means |
|---|---|---|---|
| `TEMP_SENSOR_0` | 1 | 462 | marlin table 1 is the EPCOS 100K curve, klipper `EPCOS 100K B57560G104F` |
| `HEATER_0_MAXTEMP` | 275 | 518 | shutdown threshold |
| `HOTEND_OVERSHOOT` | 15 | 535 | settable ceiling is 275 − 15 = 260 °C |
| `DEFAULT_Kp` / `Ki` / `Kd` | 17.10 / 1.39 / 52.79 | 563–565 | marlin-scaled, not klipper values |
| `EXTRUDE_MINTEMP` | 180 | 677 | |
| `DEFAULT_AXIS_STEPS_PER_UNIT` E | 424.9 | 868 | the v3 se geared extruder, not fitted here |

klipper reference block
no v3 se file ships in klipper `config/` | community file, same block in both repos listed in `references.md`
source `printer-creality-ender3-v3-se-2023.cfg` | `0xD34D/ender3-v3-se-klipper-config` at `deb2cfd73b31`

```
[extruder]
heater_pin: PA1
sensor_type: EPCOS 100K B57560G104F
sensor_pin: PC5
control: pid
# tuned for stock hardware with 200 degree Celsius target
pid_Kp: 27.142
pid_Ki: 1.371
pid_Kd: 134.351
min_temp: 0
max_temp: 260
```

what carries over to this machine
`sensor_type: EPCOS 100K B57560G104F` | the fitted sensor is the stock one | the saved v3 se sensor reads on the same curve
`heater_pin: PA1` | `sensor_pin: PC5` | identical
`max_temp: 260` | the reference ceiling for this hotend
pid 27.142 / 1.371 / 134.351 | starting point only | tuned with the v3 se fan and shroud, not the satsana duct

what does not carry over
`rotation_distance: 7.44` | `step_pin: PB4` | `dir_pin: PB3` | all belong to the v3 se geared extruder and its board
this machine keeps the stock extruder at `rotation_distance: 32.111` on `PB3` / `PB4`
`[heater_fan hotend_fan] pin: PC1` | never add | the heatsink fan here is hard-wired

live config against the reference

| Key | Live `printer.cfg` | Reference | State |
|---|---|---|---|
| `max_temp` | 300 | 260 | **owed** — 40 °C above the vendor ceiling |
| pid | 21.527 / 1.063 / 108.982 | 27.142 / 1.371 / 134.351 | **owed** — live set predates two hotends, run `PID_CALIBRATE HEATER=extruder TARGET=200` |
| `sensor_type` | EPCOS 100K B57560G104F | same | holds |
| `[verify_heater extruder]` | `max_error: 90`, comment says all-metal | | **owed** — the heatbreak is PTFE-lined |

open — duct sits on the heater block
satsana duct is modified to clear the v3 se hotend | it mounts | its outlet rests on the heater block, not at the nozzle tip
printed duct touching a block at print temperature softens and deforms | check the outlet for sag after every print
blower air lands on the block, not the extrudate | part cooling is weak | bridges and overhangs suffer first
air on the block is a heat load that scales with fan speed | `PID_CALIBRATE` with the fan at print speed, not off
a `verify_heater` trip when the fan ramps is this, not the limit | never widen `max_error`
fix | lower or re-angle the outlet to the nozzle tip with clearance to the block | remix for this hotend, see [`printed-parts.md`](printed-parts.md)

unverified — check on the machine
- heater wattage | a review reports 40 W | meter the cartridge, 24 V 40 W reads about 14.4 Ω
- nozzle | retailer listing gives M6 thread, 16.8 mm long, shared with ender-5 s1 and ender-7 | longer than MK8, do not assume the MK8 spares fit
- nozzle height against the old hotend | re-run the z endstop step in `calibration.md` before the first print

sources
vendor firmware https://github.com/CrealityOfficial/Ender-3V3-SE | gpl-3.0
vendor specification https://www.creality.com/ae/support/creality-ender-3-v3-se
klipper config https://github.com/0xD34D/ender3-v3-se-klipper-config | https://github.com/bootuz-dinamon/ender3-v3-se-full-klipper
wattage report https://printer-hub.ru/en/posts/creality-ender-3-v3-se-vs-ke-vs-plus
nozzle listing https://www.hta3d.com/en/nozzle-compatible-with-ender-5-s1,-ender-7-and-ender-3-v3-se-0.4mm
resource index https://github.com/pwlgrzs/awesome-resources-for-ender-3-v3-se

verify
`curl -sL https://raw.githubusercontent.com/CrealityOfficial/Ender-3V3-SE/main/Marlin/Configuration.h | rg -n 'TEMP_SENSOR_0 |HEATER_0_MAXTEMP|HOTEND_OVERSHOOT|DEFAULT_K[pid] '`
