"""Preview tiles for hardware/model.md, rendered headless with the workbench engine.

    B=/Applications/Blender-cad.app/Contents/MacOS/Blender
    $B -b --factory-startup ~/Projects/Assets/blend/solder/Solder.blend -P model-preview.py -- scene /tmp/tiles
    $B -b --factory-startup -P model-preview.py -- parts /tmp/tiles ~/Reference/hardware/printer/blend/solder

Parts are drawn in the blend's object colour, black throughout. `scene` writes printer--, toolhead--, feet--, rear-- and wiring-- tiles from the open blend.
`parts` writes one row of six views per STL in the folder, named <stem>--<view>.png, in the same black.
Nothing is saved back to the blend. The montage commands are in hardware/model.md.
"""
import sys
from pathlib import Path

import bpy
from mathutils import Vector

mode, out, *rest = sys.argv[sys.argv.index("--") + 1:]
# the object colour every part of the printer carries in the blend
BLACK = (0.06, 0.06, 0.07, 1)
SIDES = [("front", (0, 1, 0)), ("back", (0, -1, 0)), ("left", (1, 0, 0)), ("right", (-1, 0, 0)), ("top", (0, 0.001, 1)), ("iso", (0.8, 1.3, 0.7))]


def camera(scene, px):
    cam = bpy.data.objects.new("preview", bpy.data.cameras.new("preview"))
    scene.collection.objects.link(cam)
    scene.camera = cam
    cam.data.type = "ORTHO"
    cam.data.clip_start, cam.data.clip_end = 1, 20000
    scene.render.engine = "BLENDER_WORKBENCH"
    shading = scene.display.shading
    shading.color_type, shading.light = "OBJECT", "STUDIO"
    shading.show_cavity = shading.show_object_outline = True
    # black parts on a black ground read by their lit edges and pale outline alone
    shading.cavity_type, shading.cavity_ridge_factor, shading.curvature_ridge_factor = "BOTH", 2.5, 2.0
    shading.show_specular_highlight, shading.object_outline_color = True, (0.7, 0.7, 0.72)
    shading.background_type, shading.background_color = "VIEWPORT", (0, 0, 0)
    scene.view_settings.view_transform, scene.view_settings.look = "Standard", "Medium High Contrast"
    scene.render.resolution_x = scene.render.resolution_y = px
    return cam


def shoot(scene, cam, mid, span, views, tag):
    for name, d in views:
        d = Vector(d).normalized()
        cam.data.ortho_scale = span
        cam.location = Vector(mid) + d * 5000
        cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = f"{out}/{tag}--{name}.png"
        bpy.ops.render.render(write_still=True)


if mode == "scene":
    scene = bpy.context.scene
    for o in scene.objects:
        # the ground plane and the skulls on the bed are not the machine
        o.hide_render = o.name == "Floor" or "skull" in o.name
    cam = camera(scene, 900)
    shoot(scene, cam, (-5, 25, 287), 790, SIDES, "printer")
    shoot(scene, cam, (5, 60, 165), 190, SIDES[:4] + [("under", (0.3, 0.6, -1)), SIDES[5]], "toolhead")
    shoot(scene, cam, (0, 0, 30), 520, [("low", (0.9, 1.3, 0.25)), ("under", (0.5, 0.8, -1))], "feet")
    shoot(scene, cam, (145, 130, -10), 150, [("corner", (1, 1.2, 0.3))], "feet")
    shoot(scene, cam, (0, -20, 430), 420, [("ztop", (-0.6, -1.3, 0.7))], "rear")
    shoot(scene, cam, (0, -85, 40), 420, [("closed", (-0.5, -1.3, 0.8))], "rear")
    shoot(scene, cam, (0, -150, 20), 420, [("fans", (0, -1, 0.35))], "rear")
    for o in bpy.data.collections["Rear Enclosure"].objects:
        o.hide_render = "Cover" in o.name
    shoot(scene, cam, (0, -85, 40), 420, [("open", (-0.5, -1.3, 0.8))], "rear")
    for o in bpy.data.collections["Rear Enclosure"].objects:
        o.hide_render = False
    shoot(scene, cam, (0, -20, 200), 640, [("machine", (0.7, -1.3, 0.7))], "wiring")
    shoot(scene, cam, (110, 10, 200), 300, [("gantry", (0.3, -1, 1.1))], "wiring")
    shoot(scene, cam, (150, 0, 110), 330, [("upright", (1.3, 0.8, 0.4))], "wiring")
    shoot(scene, cam, (130, 5, 5), 150, [("under", (0.6, 0.5, -1))], "wiring")
    shoot(scene, cam, (40, -150, 30), 260, [("rear", (-0.2, -1, 0.5))], "wiring")
    shoot(scene, cam, (0, 0, 140), 520, [("front", (0, 1, 0.04))], "wiring")
    shoot(scene, cam, (0, -5, 0), 420, [("bottom", (0, 0.001, -1))], "wiring")
    for name in ("Heated Bed", "Y Carriage"):
        for o in bpy.data.collections[name].all_objects:
            o.hide_render = True
    # plan views: covers off, and nothing above the base may hide the runs
    for o in scene.objects:
        if o.type == "MESH" and ("Enclosure Cover" in o.name or sum((o.matrix_world @ Vector(c)).z for c in o.bound_box) / 8 > 60):
            o.hide_render = True
    shoot(scene, cam, (0, -65, 40), 400, [("top", (0, -0.001, 1))], "wiring")
    shoot(scene, cam, (60, -85, 30), 150, [("board", (0, -0.001, 1))], "wiring")
else:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    cam = camera(scene, 300)
    files = sorted(Path(rest[0]).expanduser().glob("*.stl"))
    for f in files:
        bpy.ops.wm.stl_import(filepath=str(f))
        o = bpy.context.selected_objects[0]
        o.color = BLACK
        ps = [o.matrix_world @ Vector(c) for c in o.bound_box]
        lo = Vector([min(p[k] for p in ps) for k in range(3)])
        hi = Vector([max(p[k] for p in ps) for k in range(3)])
        shoot(scene, cam, (lo + hi) / 2, (hi - lo).length * 1.05, SIDES, f.stem)
        bpy.data.objects.remove(o)
