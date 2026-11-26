"""빛 경계가 울퉁불퉁한 면을 따라 지그재그로 꺾이지 않게, 모양(실루엣)은 두고 '빛 받는 방향(법선)'만 매끈하게.

실행: blender -b --python tools/char/smooth_normals.py -- <입력.glb> <출력.glb> [반복=20]
부위마다: 복사본을 여러 번 매끈하게(Smooth 수정자) → 그 법선을 원본에 옮김(Data Transfer, custom normal).
참고: 다른 Tripo 툰 프로젝트(jgyy/trixian PR #8)도 같은 원인(면이 각져 그림자 경계가 삼각형을 따라 지그재그)을 법선 매끈하게로 고침.
"""
import sys

import bpy

a = sys.argv[sys.argv.index("--") + 1:]
SRC, OUT = a[0], a[1]
IT = int(a[2]) if len(a) > 2 else 20
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
objs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
for o in objs:
	# UV 경계에서 갈라진 점을 합쳐야 이웃 면과 법선이 이어짐 (복사본에서만)
	src = o.copy(); src.data = o.data.copy(); bpy.context.collection.objects.link(src)
	bpy.context.view_layer.objects.active = src
	for x in bpy.context.selected_objects:
		x.select_set(False)
	src.select_set(True)
	bpy.ops.object.mode_set(mode="EDIT")
	bpy.ops.mesh.select_all(action="SELECT")
	bpy.ops.mesh.remove_doubles(threshold=1e-5)
	bpy.ops.object.mode_set(mode="OBJECT")
	sm = src.modifiers.new("sm", "SMOOTH"); sm.factor = 0.8; sm.iterations = IT
	bpy.ops.object.modifier_apply(modifier="sm")
	for p in src.data.polygons:
		p.use_smooth = True
	for p in o.data.polygons:
		p.use_smooth = True
	dt = o.modifiers.new("dt", "DATA_TRANSFER")
	dt.object = src
	dt.use_loop_data = True
	dt.data_types_loops = {"CUSTOM_NORMAL"}
	dt.loop_mapping = "POLYINTERP_NEAREST"
	bpy.context.view_layer.objects.active = o
	bpy.ops.object.modifier_apply(modifier="dt")
	bpy.data.objects.remove(src)
for o in bpy.data.objects:
	o.select_set(o.type == "MESH")
bpy.ops.export_scene.gltf(filepath=OUT, export_format="GLB", use_selection=True, export_normals=True, export_image_format="AUTO")
print("saved", OUT, len(objs))
