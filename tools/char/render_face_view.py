"""얼굴만 확대한 정면 렌더 (GPT가 얼굴을 칠할 바탕) + 얼굴판이 보이는 자리 + 카메라 값.

실행: blender -b --python tools/char/render_face_view.py -- <입력.glb> <출력폴더> <이름> <face_fit.json>
face_fit.json의 얼굴 네모(키 1.0·바닥 0 기준)를 가운데에 두고, 네모의 1.5배를 1024px로 찍는다.
출력: <이름>_face_rgba.png(투명 바탕 회색) · <이름>_face_vis.png · <이름>_face_cam.json
"""
import json
import os
import sys

import bpy
from mathutils import Vector

a = sys.argv[sys.argv.index("--") + 1:]
SRC, OUTDIR, NAME, FIT = a[0], a[1], a[2], a[3]
fit = json.load(open(FIT))
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
ms = [o for o in bpy.context.scene.objects if o.type == "MESH"]
ws = [o.matrix_world @ v.co for o in ms for v in o.data.vertices]
lo = Vector(map(min, *ws)); hi = Vector(map(max, *ws)); h = hi.z - lo.z
fx, fz = fit["center"][0] * h, lo.z + fit["center"][1] * h
ortho = fit["size"] * h * 1.5
target = Vector((fx, (lo.y + hi.y) / 2, fz))
sc = bpy.context.scene
sc.render.engine = "BLENDER_WORKBENCH"
sc.render.resolution_x = sc.render.resolution_y = 1024
sc.render.film_transparent = True
cd = bpy.data.cameras.new("c"); cd.type = "ORTHO"; cd.ortho_scale = ortho
cam = bpy.data.objects.new("c", cd); sc.collection.objects.link(cam); sc.camera = cam
cam.location = target + Vector((0, -5, 0))
cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
sh = sc.display.shading
sh.light = "STUDIO"; sh.color_type = "SINGLE"; sh.single_color = (0.82, 0.82, 0.82); sh.show_cavity = True
sc.render.filepath = os.path.join(OUTDIR, f"{NAME}_face_rgba.png"); bpy.ops.render.render(write_still=True)
sh.light = "FLAT"; sh.color_type = "OBJECT"; sh.show_cavity = False
for o in ms:
	o.color = (1, 1, 1, 1) if o.name.split(".")[0] == "outer_face" else (0, 0, 0, 1)
sc.render.filepath = os.path.join(OUTDIR, f"{NAME}_face_vis.png"); bpy.ops.render.render(write_still=True)
json.dump({"center_px_model": [fx, fz], "ortho": ortho, "lo_z": lo.z, "height": h, "size": 1024},
	open(os.path.join(OUTDIR, f"{NAME}_face_cam.json"), "w"))
print("saved face view")
