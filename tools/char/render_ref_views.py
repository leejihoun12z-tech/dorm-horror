"""Tripo 멀티 뷰에 넣을 '모양이 정확히 맞는' 기준 그림용 회색 렌더 (Blender).

실행: blender -b --python tools/char/render_ref_views.py -- <입력.glb> <출력폴더> <이름> [--keep 접두어,…]
출력: <이름>_rgba_front/right/back.png (1024, 투명 바탕, 정사영) → tools/char/ref_sheet.py로 흰 바탕·3칸 시트·실루엣
이 렌더 위에 GPT가 디자인 색만 칠하면 그림 윤곽 = 3D 윤곽이 되어 Tripo가 색을 어긋나게 묻히지 않는다.
카메라: 키의 1.12배 화면, 가운데·바닥 맞춤. 오른쪽 = 캐릭터가 화면 오른쪽을 봄(Tripo '오른쪽' 칸).
"""
import os
import sys

import bpy
from mathutils import Vector

a = sys.argv[sys.argv.index("--") + 1:]
SRC, OUTDIR, NAME = a[0], a[1], a[2]
os.makedirs(OUTDIR, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
ms = [o for o in bpy.context.scene.objects if o.type == "MESH"]
# --keep 접두어1,접두어2: 이름이 이걸로 시작하는 물체만 남김 (예: inner_,outer_face)
if "--keep" in a:
	keep = a[a.index("--keep") + 1].split(",")
	for o in ms:
		if not any(o.name.startswith(k) for k in keep):
			bpy.data.objects.remove(o)
	ms = [o for o in bpy.context.scene.objects if o.type == "MESH"]
ws = [o.matrix_world @ v.co for o in ms for v in o.data.vertices]
lo = Vector(map(min, *ws)); hi = Vector(map(max, *ws))
c = (lo + hi) / 2
h = hi.z - lo.z
sc = bpy.context.scene
sc.render.engine = "BLENDER_WORKBENCH"
sc.render.resolution_x = sc.render.resolution_y = 1024
sc.world = bpy.data.worlds.new("w")
cd = bpy.data.cameras.new("c"); cd.type = "ORTHO"; cd.ortho_scale = h * 1.12
cam = bpy.data.objects.new("c", cd); sc.collection.objects.link(cam); sc.camera = cam
# 캐릭터 정면 = -Y. 오른쪽 칸 = 캐릭터가 화면 오른쪽을 봄 → 카메라는 -X 쪽 (렌더로 확인함)
VIEWS = {"front": Vector((0, -1, 0)), "right": Vector((-1, 0, 0)), "back": Vector((0, 1, 0))}
sc.render.film_transparent = True  # 바탕은 아래 PIL 단계에서 흰색으로(Workbench는 월드 색을 바탕으로 안 씀)
sh = sc.display.shading
sh.light = "STUDIO"; sh.color_type = "SINGLE"; sh.single_color = (0.82, 0.82, 0.82)
sh.show_cavity = True
for k, d in VIEWS.items():
	cam.location = c + d * 5
	cam.rotation_euler = (c - cam.location).to_track_quat("-Z", "Y").to_euler()
	sc.render.filepath = os.path.join(OUTDIR, f"{NAME}_rgba_{k}.png")
	bpy.ops.render.render(write_still=True)
# 카메라 값 (그림 픽셀 ↔ 모델 좌표) + 얼굴판이 보이는 자리(앞, 머리카락에 가린 곳 제외)
import json
with open(os.path.join(OUTDIR, f"{NAME}_cam.json"), "w") as f:
	json.dump({"center": list(c), "lo": list(lo), "height": h, "ortho": h * 1.12, "size": 1024}, f)
sh.light = "FLAT"; sh.color_type = "OBJECT"; sh.show_cavity = False
for o in ms:
	o.color = (1, 1, 1, 1) if o.name.split(".")[0] == "outer_face" else (0, 0, 0, 1)
cam.location = c + VIEWS["front"] * 5
cam.rotation_euler = (c - cam.location).to_track_quat("-Z", "Y").to_euler()
sc.render.filepath = os.path.join(OUTDIR, f"{NAME}_facevis_front.png")
bpy.ops.render.render(write_still=True)
print("saved", OUTDIR, NAME)
