#!/usr/bin/env python3
"""Map a measured part height to a resume point, for a print that lost extrusion.

The PLR byte offset records where Klipper stopped, not where extrusion stopped.
After an extruder failure the machine keeps moving through air, so that offset
describes a part that was never printed. Measure the real part and map the
height to a layer here.

    resume-at.py <gcode> <measured_mm> [physical_z]
    resume-at.py --apply <gcode> <measured_mm> <physical_z>
    resume-at.py --universal ...      force slicer-independent layer detection
    resume-at.py --next ...           resume the layer above instead
    resume-at.py --selftest

measured_mm  nozzle-contact height on solid bonded plastic, bed hot, taken
             against the endstop datum so it is already in gcode Z terms.
physical_z   where the nozzle actually is now. Park it, read the toolhead, pass
             that. It becomes plr_z and is NOT the layer height.

Default resumes the LAST FULL layer, printing it a second time so the nozzle
lands slightly into solid plastic and bonds. --next leaves that layer floating.

--apply writes plr_pos, plr_z and plr_active through Moonraker. It never writes
plr_file: SAVE_VARIABLE runs ast.literal_eval and strips one quote layer, so a
string needs two, and an empty one shuts the printer down mid-print.
It never starts the print either - run RESUME_AFTER_POWER_LOSS yourself.
"""
import re, sys

MOONRAKER = "http://moonraker:7125"
MARK = b";LAYER_CHANGE"
Z_RE = re.compile(rb"[ \t]Z(-?\d*\.?\d+)")
E_RE = re.compile(rb"[ \t]E(-?\d*\.?\d+)")


def by_marker(data):
    """Orca / PrusaSlicer / SuperSlicer: ;LAYER_CHANGE followed by ;Z:<z>."""
    out, off, pending = [], 0, None
    for raw in data.splitlines(keepends=True):
        if pending is not None and raw.startswith(b";Z:"):
            out.append((float(raw[3:].split(b"\n")[0]), pending))
            pending = None
        elif raw.startswith(MARK):
            pending = off
        off += len(raw)
    return out


def by_motion(data):
    """Any slicer: first extruding move at each new, higher Z starts a layer.

    Z hops are rejected because nothing extrudes at hop height. E is read as
    relative or absolute depending on the last M82/M83 seen.
    """
    out, off, pending = [], 0, None
    cur_z = last_z = None
    rel_e, prev_e = True, 0.0
    for raw in data.splitlines(keepends=True):
        head = raw[:3].upper()
        if head.startswith(b"M83"):
            rel_e = True
        elif head.startswith(b"M82"):
            rel_e = False
        elif head in (b"G0 ", b"G1 ") or raw[:2].upper() in (b"G0", b"G1"):
            mz = Z_RE.search(raw)
            if mz:
                z = float(mz.group(1))
                if z != cur_z:
                    cur_z, pending = z, off
            me = E_RE.search(raw)
            if me:
                e = float(me.group(1))
                extruding = e > 0 if rel_e else e > prev_e
                prev_e = e if not rel_e else prev_e
                if extruding and cur_z is not None and (last_z is None or cur_z > last_z):
                    out.append((cur_z, pending if pending is not None else off))
                    last_z = cur_z
        off += len(raw)
    return out


def layers(path, universal=False):
    data = open(path, "rb").read()
    rows = [] if universal else by_marker(data)
    return rows or by_motion(data)


def pick(rows, measured, use_next):
    done = [r for r in rows if r[0] <= measured + 1e-6]
    if not done:
        sys.exit("measured height is below the first layer")
    i = rows.index(done[-1]) + (1 if use_next else 0)
    if i >= len(rows):
        sys.exit("measured height is at or past the last layer")
    return rows[i]


def apply(byte, phys_z, url):
    import urllib.parse, urllib.request
    for cmd in ("SAVE_VARIABLE VARIABLE=plr_pos VALUE=%d" % byte,
                "SAVE_VARIABLE VARIABLE=plr_z VALUE=%s" % float(phys_z),
                "SAVE_VARIABLE VARIABLE=plr_active VALUE=1"):
        u = url + "/printer/gcode/script?script=" + urllib.parse.quote(cmd)
        urllib.request.urlopen(urllib.request.Request(u, method="POST"), timeout=10).read()
    print("written. check PLR_STATUS, wipe the nozzle, then RESUME_AFTER_POWER_LOSS")


def selftest():
    orca = b"".join(b";LAYER_CHANGE\n;Z:%.2f\nG1 X1 E1\n" % (0.2 * n) for n in range(1, 6))
    rows = by_marker(orca)
    assert [r[0] for r in rows] == [0.2, 0.4, 0.6, 0.8, 1.0], rows
    assert rows[0][1] == 0 and orca[rows[2][1]:].startswith(MARK)
    assert pick(rows, 0.65, False)[0] == 0.6, "reprints the last full layer"
    assert pick(rows, 0.65, True)[0] == 0.8, "--next takes the layer above"
    assert pick(rows, 0.60, False)[0] == 0.6, "exact height is a full layer"

    # no markers, and a z-hop between layers that must not register
    plain = b"M83\n"
    for n in range(1, 5):
        plain += b"G1 Z%.2f F600\nG1 X1 Y1 E0.5\n" % (0.2 * n)
        plain += b"G1 Z%.2f F600\nG1 X9 Y9\n" % (0.2 * n + 0.4)   # hop, no extrusion
    rows = by_motion(plain)
    assert [r[0] for r in rows] == [0.2, 0.4, 0.6, 0.8], rows
    assert plain[rows[1][1]:].startswith(b"G1 Z0.40"), "byte is the Z move"

    absolute = b"M82\nG1 Z0.20\nG1 X1 E5\nG1 E4.5\nG1 Z0.40\nG1 X1 E9\n"
    assert [r[0] for r in by_motion(absolute)] == [0.2, 0.4], "retract is not a layer"
    print("selftest ok")


def main():
    if "--selftest" in sys.argv:
        return selftest()
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) < 2:
        sys.exit(__doc__)
    rows = layers(args[0], "--universal" in flags)
    if not rows:
        sys.exit("no layers found - is this a sliced gcode file?")
    z, byte = pick(rows, float(args[1]), "--next" in flags)

    print("layers          : %d, Z %.2f to %.2f" % (len(rows), rows[0][0], rows[-1][0]))
    print("resume at layer : Z %.2f   byte %d" % (z, byte))
    if len(args) < 3:
        return print("\npark the nozzle, read toolhead Z, pass it as arg 3")
    if "--apply" in flags:
        return apply(byte, args[2], MOONRAKER)
    print("\nSAVE_VARIABLE VARIABLE=plr_pos VALUE=%d" % byte)
    print("SAVE_VARIABLE VARIABLE=plr_z VALUE=%s" % float(args[2]))
    print("SAVE_VARIABLE VARIABLE=plr_active VALUE=1")


if __name__ == "__main__":
    main()
