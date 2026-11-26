"""glb의 정해진 부위를 가까이 렌더해 한 장으로 (Blender, 확인용).

실행: blender -b --python tools/char/render_closeups.py -- <입력.glb> <출력.png> [--tex] [--gray]
모델은 바닥 0·키 1.0으로 맞춰서 본다 (게임용 1.55m 모델도 같은 자리).
"""
import math
import sys

import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
SRC, OUT = argv[0], argv[1]
TEX = "--tex" in argv
SIZE = 512
# 이름: (보는 점 x, y, z (키 1.0 기준), 방향 각도(정면 0·오른쪽 90·뒤 180), 화면 폭)
SHOTS = [
	("머리 끝 뒤", (0.0, 0.0, 0.70), 180, 0.30),
	("머리 끝 옆", (0.0, 0.0, 0.72), 90, 0.30),
	("얼굴", (0.0, -0.05, 0.73), 0, 0.20),
	("목·깃", (0.0, -0.08, 0.62), 25, 0.18),
	("겨드랑이·소매", (0.10, -0.05, 0.57), 35, 0.20),
	("손목", (0.17, -0.06, 0.45), 20, 0.14),
	("치마·다리", (0.0, -0.06, 0.33), 20, 0.22),
	("코트 안", (0.0, -0.03, 0.40), 200, 0.30),
]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
ws = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
lo = Vector(map(min, *ws)); hi = Vector(map(max, *ws))
k = hi.z - lo.z

scene = bpy.context.scene
scene.render.engine = "BLENDER_WORKBENCH"
scene.display.shading.light = "FLAT" if TEX else "STUDIO"
scene.display.shading.color_type = "TEXTURE" if TEX else "SINGLE"
scene.display.shading.single_color = (0.8, 0.8, 0.8)
scene.display.shading.show_cavity = not TEX
scene.render.resolution_x = SIZE
scene.render.resolution_y = SIZE
scene.world = bpy.data.worlds.new("w")
scene.world.color = (0.55, 0.6, 0.55)
cam_data = bpy.data.cameras.new("cam"); cam_data.type = "ORTHO"
cam = bpy.data.objects.new("cam", cam_data); scene.collection.objects.link(cam); scene.camera = cam

paths = []
for i, (name, p, deg, width) in enumerate(SHOTS):
	target = Vector((p[0] * k, p[1] * k, lo.z + p[2] * k))
	a = math.radians(deg)
	cam.location = target + Vector((-math.sin(a), -math.cos(a), 0.15)) * k * 2
	cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
	cam_data.ortho_scale = width * k
	path = OUT.replace(".png", f"_{i}.png")
	scene.render.filepath = path
	bpy.ops.render.render(write_still=True)
	paths.append(path)

cols = 4
rows = math.ceil(len(paths) / cols)
sheet = bpy.data.images.new("sheet", SIZE * cols, SIZE * rows)
pix = [0.0] * (SIZE * cols * SIZE * rows * 4)
for i, pth in enumerate(paths):
	img = bpy.data.images.load(pth)
	src = list(img.pixels)
	cx, cy = i % cols, rows - 1 - i // cols
	for y in range(SIZE):
		start = ((cy * SIZE + y) * SIZE * cols + cx * SIZE) * 4
		pix[start:start + SIZE * 4] = src[y * SIZE * 4:(y + 1) * SIZE * 4]
sheet.pixels = pix
sheet.filepath_raw = OUT
sheet.file_format = "PNG"
sheet.save()
print("saved", OUT, [s[0] for s in SHOTS])
