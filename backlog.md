backlog

Things worth adding, ranked. Done items move out to the doc that owns them.

blocked on you, not on work

filament runout sensor — deferred by choice, 2026-08-04

Parts are on hand: **filament runout kit** plus its cable. The board pin is already correct and
stubbed — `FIL_RUNOUT=PA4` in `[board_pins]`, and the commented
`#switch_pin: !PA4` further down `printer.cfg` is the right 4.2.7 pin.

When you want it, the work is:

1. Mount the sensor on the frame, filament path upstream of the extruder.
2. Uncomment `[filament_switch_sensor Filament_runout_sensor]`.
3. Write `M600` — park, retract, notify via ntfy, wait for the new spool,
   purge, resume. The `[notifier print_paused]` already fires on pause, so the
   phone alert comes free.
4. Verify the switch logic (`!` or not) with `QUERY_FILAMENT_SENSOR`.

Worth more than power-loss recovery on a 12-hour print: running out of filament
is far likelier than losing mains.

3d touch probe — blocked on a printed duct

Covered in [`printed-parts.md`](hardware/printed-parts.md). Needs a Satsana remix with a
probe boss. Unlocks automatic `bed_mesh`, probe-referenced `safe_z_home`, and
`screws_tilt_adjust`.

Wiring, config and the bring-up order are written up in
[`probe.md`](hardware/probe.md) — the mount is the only thing still missing.

small additions, high return

| Item | Unlocks |
|---|---|
| ADXL345 accelerometer | Real `[input_shaper]` measurement instead of a ringing-tower guess. Matters more here because the extruder rides the X carriage |
| Smart plug (local HTTP control) | Moonraker `[power]` — auto power-off after a print, remote power-on, and a controlled shutdown you can rehearse against the PLR macros |
| Camera | Crowsnest for remote watching and timelapse; Obico or OctoEverywhere adds failure detection that aborts instead of extruding into a nest for six hours |

software, no hardware needed

- **Spoolman** — filament/spool tracking, one container plus `[spoolman]` in
  `moonraker.conf`. Fits the existing homelab.
- **klipper-estimator** — real print-time estimates instead of slicer fiction.
- **Mobileraker** — iPhone client with proper push, if ntfy topics feel thin.
- **`[job_queue]`** — queue several prints back to back.

Notifications off the LAN

`ntfy.knave` resolves through knave's dnsmasq, so notifications only arrive
while the phone is on home Wi-Fi. Two fixes, both real work:

- **Tailscale** (or WireGuard) on knave and the phone — the tidy answer, keeps
  everything private.
- **`upstream-base-url: https://ntfy.sh`** in the ntfy server config, which is
  what makes ntfy's iOS app receive background pushes at all. It forwards only a
  poll request through ntfy.sh; the app then fetches the message body from your
  server — so it still needs to reach `ntfy.knave`, meaning it pairs with the
  VPN rather than replacing it. That config lives in the **odysseus** stack, not
  this one.

not worth it on this machine

`[temperature_fan]` and `[controller_fan]` — the 4.2.7 has exactly one
controllable fan pin (`PA0`) and it is spoken for. Chamber thermistor — no spare
ADC header. `z_tilt` — needs two Z drivers; this build shares one.
