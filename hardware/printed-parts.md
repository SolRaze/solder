printed parts and source models

Every printed mod this machine depends on, and where the model came from. Fields
marked **TODO** are things only the person who printed them knows — fill them in
rather than guessing, because reprinting a mystery part after a crash is how a
rebuild stalls.

in use

direct drive bracket

| | |
|---|---|
| Function | Carries the stock extruder + stock NEMA17 on the X gantry |
| Source model | **TODO** — confirm which model was printed |
| Licence | TODO |
| Material / settings | TODO |
| Status | Fitted, load-bearing |

Candidate present in the local mod library: `BMG DirectDrive Adapter Ender 3 Pro
- remix from scaryPug's design - 4932302.zip` in
`../printer-examples/e3solder/`. That adapter is designed around a **BMG**
extruder, and this machine uses the **stock** extruder, so it is probably *not*
the part in use. Confirm before relying on it.

Anything this bracket changes — nozzle X/Y offset, carriage mass, Z clearance —
is currently unmeasured. See [`calibration.md`](../setup/calibration.md).

satsana fan duct (5015)

| | |
|---|---|
| Function | Part cooling, 5015 blower, replaces the stock 4015 duct |
| Source model | Satsana Ender 3 cooling duct — **TODO** confirm exact variant / remix / thing ID |
| Licence | TODO |
| Blower | 5015, 24 V |
| Status | Fitted |

**This part is the blocker for auto bed levelling.** The variant in use has no
BLTouch mount, and a 3D Touch sensor is sitting unused in the parts box. Fixing
it needs a Satsana remix that carries a probe boss, printed on this machine —
so the first prints happen on a manual mesh, and the probe goes on after.

Satsana variants exist for: stock hotend vs all-metal, 4010 vs 5015 blower, with
and without BLTouch, and with and without a dual-blower option. Pick the one
matching **V3 hotend + 5015 + BLTouch** and record the choice here.

dual z

| | |
|---|---|
| Kit | dual screw rod upgrade kit, ×2 |
| Printed parts needed | TODO — record any brackets/spacers printed for it |
| Status | Fitted, both motors on one driver |

local mod library

`../printer-examples/e3solder/` — model zips kept on disk, **gitignored**, not
in history. Nothing here is fitted unless listed above.

| Zip | Relevance |
|---|---|
| BMG DirectDrive Adapter Ender 3 Pro (4932302) | Direct drive, but BMG-specific — probably not the fitted part |
| Boreas — Mosquito/E3D V6 Hotend Mount (4096159) | Alternative hotend mount, not in use |
| the vendor Sprite Extruder — Vulture V1 Toolhead (7080838) | Alternative toolhead, not in use |
| E3NS — Ender 3 V2 Neo Hotend using Ender 5 S1 Parts (7306857) | Not in use |
| Ender 3 Z Stent, Gantry Alignment Improvement (5241659) | **Relevant** — dual Z has no `z_tilt`, so gantry alignment is manual |
| Gantry Rod Support Bracket (7067770) | Frame stiffening, not fitted |
| Bearing Spool Holder for 2020/2040/3030 (2537713) | Not fitted |
| Ender 3 V2 Minimalist Bed Handle (4723754) | Not fitted |
| Ender 3 V3 KE/SE Filament Sensor Mount (6509336) | Wrong printer generation |
| Extruder Knob one-piece (3458220) | Cosmetic |

to print, in order

1. **Satsana remix with BLTouch mount** — unblocks the 3D Touch sensor, which
   unblocks `bed_mesh` automation, `safe_z_home` and `screws_tilt_adjust`.
2. **Filament runout sensor mount** — the runout kit is on hand and `PA4` is
   already stubbed in config.
3. Gantry alignment aid — dual Z with a single driver cannot self-level.

recording rule

When a printed part goes on this machine, add it above with: what it does, the
source model and where it came from, the licence, material and print settings,
and whether anything in `printer.cfg` depends on it. A printed part that changes
the nozzle position is a **config dependency**, not just a piece of plastic.
