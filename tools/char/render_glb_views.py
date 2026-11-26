"""glb 모델을 앞·오른쪽·뒤·3/4 네 방향으로 렌더해 한 장으로 붙인다 (Blender, 확인용).

실행: blender -b --python tools/char/render_glb_views.py -- <입력.glb> <출력.png> [--parts]
  --parts: 부위(물체)마다 다른 색 (부위 나누기 확인용). --vcol: 정점 색. 둘 다 없으면 회색 단색.
부위 목록(이름·면 수·크기)을 콘솔에 찍는다.
"""
import math
import sys

import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
SRC, OUT = argv[0], argv[1]
PARTS = "--parts" in argv
VCOL = "--vcol" in argv
SIZE = 720

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]

lo = Vector((1e9, 1e9, 1e9))
hi = Vector((-1e9, -1e9, -1e9))
total = 0
for o in meshes:
	ws = [o.matrix_world @ Vector(c) for c in o.bound_box]
	for w in ws:
		lo = Vector(map(min, lo, w))
		hi = Vector(map(max, hi, w))
	n = len(o.data.polygons)
	total += n
	size = Vector(map(max, *[o.matrix_world @ Vector(c) for c in o.bound_box])) - Vector(map(min, *[o.matrix_world @ Vector(c) for c in o.bound_box]))
	print(f"part {o.name}: faces {n} size {size.x:.3f} x {size.y:.3f} x {size.z:.3f}")
print(f"total parts {len(meshes)} faces {total} bbox {tuple(round(v, 3) for v in lo)} -> {tuple(round(v, 3) for v in hi)}")

center = (lo + hi) / 2
height = hi.z - lo.z

scene = bpy.context.scene
scene.render.engine = "BLENDER_WORKBENCH"
scene.display.shading.light = "STUDIO"
scene.display.shading.color_type = "RANDOM" if PARTS else ("VERTEX" if VCOL else "SINGLE")
scene.display.shading.single_color = (0.8, 0.8, 0.8)
scene.display.shading.show_cavity = True
scene.render.resolution_x = SIZE
scene.render.resolution_y = SIZE
scene.render.film_transparent = False
scene.world = bpy.data.worlds.new("w")
scene.world.color = (1, 1, 1)

cam_data = bpy.data.cameras.new("cam")
cam_data.type = "ORTHO"
cam_data.ortho_scale = height * 1.15
cam = bpy.data.objects.new("cam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam

# glTF는 -Y가 앞(Blender로 들어오면 캐릭터 정면 = -Y 방향)
views = [("front", 0), ("right", 90), ("back", 180), ("34", 35)]
images = []
for name, deg in views:
	a = math.radians(deg)
	d = height * 3
	cam.location = center + Vector((-math.sin(a) * d, -math.cos(a) * d, 0))
	direction = center - cam.location
	cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
	path = OUT.replace(".png", f"_{name}.png")
	scene.render.filepath = path
	bpy.ops.render.render(write_still=True)
	images.append(path)

sheet = bpy.data.images.new("sheet", SIZE * len(images), SIZE)
pix = [0.0] * (SIZE * len(images) * SIZE * 4)
for i, p in enumerate(images):
	img = bpy.data.images.load(p)
	src = list(img.pixels)
	for y in range(SIZE):
		row = src[y * SIZE * 4:(y + 1) * SIZE * 4]
		start = (y * SIZE * len(images) + i * SIZE) * 4
		pix[start:start + SIZE * 4] = row
sheet.pixels = pix
sheet.filepath_raw = OUT
sheet.file_format = "PNG"
sheet.save()
print("saved", OUT)
