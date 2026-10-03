power-loss recovery

Implemented in [`config/plr.cfg`](../config/plr.cfg), included from `printer.cfg`.
**Proven on a real interrupted print** — 2026-09-05, a PETG job that lost its
extruder at 3 h 37 m picked up from a measured height and ran to completion,
11.94 h. The seek, the restored temperatures and the X/Y-only homing all work.
What it cannot do is work out *where* to resume, which is the failure mode
below, and the result carries one doubled layer.

Not push-button. Finding the contact height is a manual jog down onto the part
at a decreasing step size — coarse, then 0.1 mm — because there is no probe to
do it. Budget for standing at the machine.

what this is, honestly

Klipper has **no native power-loss recovery**. There is no hardware for it
either: the Ender 3 has no power-loss detection circuit and no supercapacitor to
buy time for a graceful save. What stock Marlin called "power loss recovery" was
the same trick used here — periodically write the print position to storage, and
on restart seek the gcode file back to that offset.

So this is best-effort. It recovers *most* of a long print *most* of the time.
It is not a guarantee, and there are failure modes below that no macro can fix.

how it works

**Saving.** `PLR_SAVE` snapshots into `variables.cfg`: the filename, the
`virtual_sdcard` byte offset, X/Y/Z, both heater targets, and the fan speed. It
is called two ways, deliberately overlapping:

- `[delayed_gcode PLR_TIMER]` every **30 s** while a print is active. Started by
  `START_PRINT`, and slicer-independent.
- Orca's **layer change gcode** calls `PLR_SAVE` on every layer, which is more
  precise than the timer.

`END_PRINT` calls `PLR_CLEAR` so a clean finish leaves no stale state.

**Resuming.** `RESUME_AFTER_POWER_LOSS` does, in order:

1. Refuses to run if no state was saved.
2. `SET_KINEMATIC_POSITION Z=<saved>` — tells Klipper where Z already is.
3. Lifts 5 mm.
4. `G28 X Y` — **X and Y only**.
5. Restores bed and nozzle temperatures, waits for both, restores fan.
6. Travels back over the part at the safe height, then drops to the saved Z.
7. Sets the extruder mode, `G92 E0`.
8. `M23` the file, `M26` seek to the saved byte, `M24` to run.

`PLR_STATUS` prints what would be resumed without doing anything.

the rule that matters

**It never homes Z.** `G28 Z` sends the nozzle down until the Z endstop
triggers — straight through whatever is on the bed. The whole procedure rests on
one assumption: **the lead screws held the gantry where it was during the
outage.** They normally do. If someone has cranked a Z screw by hand since the
power cut, the saved Z is a lie and the resume will crash into the print.

Dual Z makes this slightly better (two screws holding) and slightly worse (they
can rack independently while unpowered).

the quoting bug — 2026-08-05, fixed

The first real print died on this, twice:

```
!! Unable to parse 'FilamentSample_PETG_20m46s.gcode' as a literal
!! Internal error on command:"SAVE_VARIABLE"      -> Printer is shutdown
```

`SAVE_VARIABLE` runs `ast.literal_eval` on VALUE, and Klipper strips **one**
layer of surrounding quotes before that. A string therefore needs **two** layers:

```
SAVE_VARIABLE VARIABLE=plr_file VALUE="'{fn}'"
```

The deployed macro had only one layer — the inner `'` pair was eaten by shell
quoting when `plr.cfg` was written over ssh. So:

- a normal filename arrived bare -> `ValueError` -> the "as a literal" message;
- an **empty** filename arrived as nothing -> `ast.literal_eval("")` raises
  `SyntaxError`, which `save_variables.py` does not catch -> uncaught exception
  -> "Internal error" -> **printer shutdown mid-print**.

Fixed by restoring the two-layer quoting and guarding on a non-empty filename,
so PLR_SAVE is a silent no-op unless a print is genuinely active. `RESUME_AFTER_POWER_LOSS`
now also refuses to run when no filename was stored.

Lesson worth keeping: a macro that writes state on **every layer** sits in the
path of every print. Anything that can raise there takes the print with it.
Verify a new PLR_SAVE by watching one full layer change before trusting a long
print to it.

failure modes it cannot fix

- **The saved byte is not where extrusion stopped.** `PLR_SAVE` records where
  Klipper stopped. If the extruder failed first and the machine carried on
  moving through air, the saved offset describes a part that was never printed —
  in the 2026-09-05 case it was 6.94 mm, about 35 layers, too high. Nothing here
  can detect that. The resume point has to come from measuring the physical
  part; see the entry in [`bringup-log.md`](../log/bringup-log.md) for the method and
  the tooling.
- **The part came unstuck.** The bed cools during the outage, PETG and PLA
  release, and the resume happily prints in mid-air. Check adhesion before
  resuming — this is the most common one.
- **Mid-layer loss.** The seek lands on a byte boundary from up to 30 s ago (or
  the last layer change). Expect a visible seam or a small gap.
- **Extruder state.** Melted filament oozes and the nozzle may have leaked out
  during the outage. The first restored moves can under-extrude until pressure
  builds.
- **Absolute vs relative E.** Orca defaults to relative, Cura uses absolute.
  Wrong guess after a seek means a wild extrusion. Default is relative; for a
  Cura file run `RESUME_AFTER_POWER_LOSS EMODE=ABSOLUTE`.
- **A cancelled print leaves stale state** — `PLR_CLEAR` only runs on a clean
  `END_PRINT`. Run `PLR_STATUS` first and check the filename is the one you
  think it is.
- **Thermal drift.** A part that cooled fully and got re-heated will have moved.
  Layer registration is approximate.

finding the resume point

`resume-at.py` maps a measured height to a layer and byte. It reads the gcode
directly, so there is no index file to regenerate per job. Layers come from
`;LAYER_CHANGE` where the slicer emits it, otherwise from the first extruding
move at each new Z — Z hops are rejected because nothing extrudes at hop height,
so it works for any slicer. Both paths agree on the skull file: 734 layers,
same layer Z.

```
resume-at.py <gcode> <measured_mm> [physical_z]   # last full layer, reprinted
resume-at.py --next <gcode> <measured_mm>         # layer above instead
resume-at.py --selftest
```

From the console, `PLR_RESUME_AT_Z HEIGHT=35.3` does the same thing against the
file already in `plr_file` and writes the variables itself:

```
PLR_RESUME_AT_Z HEIGHT=<measured mm> [PLR_Z=<physical nozzle mm>]
```

It refuses while a print is active, because it would overwrite that print's own
resume point. `PLR_Z` defaults to the current toolhead Z, which is only right if
Z is homed — park the nozzle and pass it explicitly otherwise. It writes
`plr_pos`, `plr_z` and `plr_active` and stops there; `RESUME_AFTER_POWER_LOSS`
stays a separate, deliberate command.

The macro needs `[gcode_shell_command]`, because scanning a 50 MB file is not
something a Jinja template can do. `resume-at.py` is deployed by hand — the
config pull only carries `.cfg` files:

```
scp devices/printer/resume-at.py knave:/srv/klipper/config/
```

`measured_mm` is nozzle contact on solid bonded plastic with the bed hot, taken
after homing Z so it is already in gcode Z terms. `physical_z` is where the
nozzle actually sits — park it, read the toolhead, pass that. It becomes
`plr_z`, and it is not the layer height.

Default resumes the **last full layer**, printing it twice: the nozzle lands
slightly into solid plastic and squishes, which bonds. `--next` starts the layer
above and leaves that bond layer floating in the gap. The doubled layer is the
price of a joint that holds; on the 2026-09-05 job it was the only visible
defect.

usage

```
PLR_STATUS                              # what is saved?
RESUME_AFTER_POWER_LOSS                 # Orca files (relative E)
RESUME_AFTER_POWER_LOSS EMODE=ABSOLUTE  # Cura files (absolute E)
PLR_CLEAR                               # forget it
```

Before the first real resume, rehearse it: start a tall print, cut mains at
mid-height, restore power, and run `RESUME_AFTER_POWER_LOSS` while watching the
first travel move with a hand on the switch.

write frequency

Every 30 s plus every layer change means `variables.cfg` gets rewritten a lot.
On knave's storage this is nothing. If it ever shows up as a print stutter,
raise the timer duration in `plr.cfg` or drop the layer-change hook and keep the
timer.
