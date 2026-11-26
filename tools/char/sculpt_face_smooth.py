"""보완된 머리통(눈·코가 조각된 얼굴)을 Blender에서 직접 다듬는 시험: 눈·눈썹 자리의 굴곡만 매끈하게.

실행: blender -b --python tools/char/sculpt_face_smooth.py -- <출력 폴더> [반복=40] [눈 띠 아래=0.705] [위=0.80]
입력: mq_tripo_W2_parts_filled.glb (부위 보완 결과) — 머리통 = tripo_part_5, 머리카락 = tripo_part_0
방법: 얼굴 앞면 중 눈 띠(높이 범위) 안의 점만 골라 이웃 평균으로 여러 번 고르게(스컬프트의 Smooth 붓과 같은 일).
      코·입·턱·윤곽은 띠 밖이라 그대로. 전·후를 앞·3/4·옆에서 찍어 확인한다.
출력: head_smooth.glb(머리통 + 머리카락) + 확인 그림
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector

a = sys.argv[sys.argv.index("--") + 1:]
OUT = a[0]
IT = int(a[1]) if len(a) > 1 else 40
Z0 = float(a[2]) if len(a) > 2 else 0.705
Z1 = float(a[3]) if len(a) > 3 else 0.80
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = os.path.join(ROOT, "assets/art_src/char3d/mannequin_tripo_20261126/mq_tripo_W2_parts_filled.glb")
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
ms = [o for o in bpy.context.scene.objects if o.type == "MESH"]
for o in ms:
	mw = o.matrix_world.copy(); o.parent = None; o.data.transform(mw); o.matrix_world.identity()
ws = [v.co for o in ms for v in o.data.vertices]
lo = min(v.z for v in ws); h = max(v.z for v in ws) - lo
for o in ms:
	for v in o.data.vertices:
		v.co = Vector((v.co.x / h, v.co.y / h, (v.co.z - lo) / h))
head = [o for o in ms if o.name == "tripo_part_5"][0]
hair = [o for o in ms if o.name == "tripo_part_0"][0]
for o in ms:
	if o not in (head, hair):
		bpy.data.objects.remove(o)

sc = bpy.context.scene
sc.render.engine = "BLENDER_WORKBENCH"
sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "SINGLE"; sc.display.shading.show_cavity = True
sc.render.resolution_x = sc.render.resolution_y = 600
cd = bpy.data.cameras.new("c"); cd.type = "ORTHO"; cd.ortho_scale = 0.24
cam = bpy.data.objects.new("c", cd); sc.collection.objects.link(cam); sc.camera = cam


def shots(tag):
	for name, ang, vis in [("front", (0, -1, 0), [head]), ("q", (-0.6, -0.8, 0), [head]), ("side", (-1, 0, 0), [head]), ("hair", (0, -1, 0), [head, hair])]:
		head.hide_render = head not in vis; hair.hide_render = hair not in vis
		t = Vector((0, 0, 0.74)); cam.location = t + Vector(ang) * 5
		cam.rotation_euler = (t - cam.location).to_track_quat("-Z", "Y").to_euler()
		sc.render.filepath = os.path.join(OUT, f"{tag}_{name}.png"); bpy.ops.render.render(write_still=True)


shots("before")
bm = bmesh.new(); bm.from_mesh(head.data)
ys = [v.co.y for v in bm.verts]
front = min(ys); depth = max(ys) - front
# 눈 띠: 앞면(얼굴 앞에서 깊이 45%까지) · 높이 Z0~Z1. 가장자리는 서서히(가중치)
sel = {}
for v in bm.verts:
	if (v.co.y - front) / depth < 0.62 and Z0 < v.co.z < Z1:
		edge = min(v.co.z - Z0, Z1 - v.co.z) / 0.012
		sel[v] = max(0.0, min(1.0, edge))
print("masked verts", len(sel), "of", len(bm.verts))
for _ in range(IT):
	new = {}
	for v, w in sel.items():
		nb = [e.other_vert(v).co for e in v.link_edges]
		avg = sum(nb, Vector()) / len(nb)
		new[v] = v.co.lerp(avg, 0.6 * w)
	for v, co in new.items():
		v.co = co
bm.normal_update(); bm.to_mesh(head.data); bm.free()
for p in head.data.polygons:
	p.use_smooth = True
shots("after")
head.hide_render = hair.hide_render = False
for o in bpy.data.objects:
	o.select_set(o.type == "MESH")
bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "head_smooth.glb"), export_format="GLB", use_selection=True)
print("ok")
