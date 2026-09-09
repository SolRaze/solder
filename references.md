references

vendor source and upstream projects this machine is built on


ender 3

`../printer-examples/Ender-3/` | vendor upstream release | gpl-3.0 | gitignored | reference only, never edited

| Directory | Contents | Use for |
|---|---|---|
| `Ender-3 Firmware (Marlin)` | stock marlin source | historical only — this machine runs klipper |
| `Ender-3 Mechanical` | `3DXML` `ASM` `DWG` `F360` `IGS` `STP` `XT` `PDF` `Ender-3 Parts` `Ender-3 BOM.XLS` | frame dimensions | part geometry | printed mods that must bolt to the real thing |
| `Ender-3 PCB` | binary pcb files (3.0 / 5.0) `Ender3_pcb_parts.PDF` `Ender-3 PCBA BOM.xlsx` | board questions the silkscreen cannot answer |
| `Ender-3 Wiring` | `DWG` + `PDF` per cable | main board line | power line | hot bed line | x/e | y | z motor lines | display line |
| `Ender-3 SD` | shipped sd contents | |

wiring pdfs are per-cable drawings | not a board pinout

pin-level truth is klipper `config/generic-creality-v4.2.7.cfg`, in the klipper
container at `/opt/klipper/config/` | what the pin map in
[`electronics.md`](hardware/electronics.md) was verified against

trap `printer-creality-ender3-*.cfg` shipped with klipper are all 4.2.2 maps | never use on this board

pinned versions

klipper `v0.13.0-700-gd6ea62542` | moonraker `v0.10.0-30-g6597123`

pin both to the same commits when rebuilding | runtime and firmware must match

upstream

klipper https://github.com/Klipper3d/klipper
moonraker https://github.com/Arksine/moonraker
mainsail https://github.com/mainsail-crew/mainsail
fluidd https://github.com/fluidd-core/fluidd
prind — source of the `mkuf/klipper` and `mkuf/moonraker` images https://github.com/mkuf/prind
prettygcode https://github.com/Kragrathea/pgcode
spoolman https://github.com/Donkie/Spoolman
kiauh — source of the `gcode_shell_command` extra https://github.com/dw-0/kiauh
orcaslicer https://github.com/SoftFever/OrcaSlicer
ntfy https://github.com/binwiederhier/ntfy
docker-socket-proxy https://github.com/Tecnativa/docker-socket-proxy
nginx-proxy-manager https://github.com/NginxProxyManager/nginx-proxy-manager
ender-3 vendor source https://github.com/Creality3DPrinting/Ender-3

suppliers

online vendors | local shops

licensing

ender-3 vendor repo gpl-3.0 | vendor source kept for reference | not redistributed from here | gitignored, on disk only

printed mod models carry their own licences | recorded per part in [`printed-parts.md`](hardware/printed-parts.md)
