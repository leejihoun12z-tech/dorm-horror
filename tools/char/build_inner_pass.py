"""2차 칠하기용 '속 부위' 모델 만들기 (Blender).

실행: blender -b --python tools/char/build_inner_pass.py
입력: 1차 텍스처 모델(리토폴로지) + 얼굴 있게 뽑은 모델(머리만)
출력: assets/art_src/char3d/mannequin_tripo_20261126/inner_pass_in.glb
  = 셔츠·깃·허리·다리·손 (1차 리토폴로지 모양 그대로) + 얼굴 있는 모델의 머리(면 줄임)
  코트·소매·베레모·치마·신발·얼굴판은 넣지 않음 → Tripo가 코트 없는 그림으로 이 부위만 칠함.
좌표는 1차 텍스처 모델과 같음(나중에 합칠 때 그대로 겹침).
"""
import math
import os
import sys

import bpy
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
D = os.path.join(ROOT, "assets/art_src/char3d/mannequin_tripo_20261126")
PASS1 = os.path.join(D, "mq_tripo_W2_retopo_tex.glb")
FACEFUL = os.path.join(D, "mq_tripo_W2_parts.glb")
OUT = os.path.join(D, "inner_pass_in.glb")
HAIR_TRIS = 16000
# 키 1.0 기준 부위 중심 (split_tripo_textured.py와 같은 값)
CENTERS = {
	"hair": (-0.002, -0.009, 0.763), "beret": (-0.004, 0.022, 0.881), "face": (0.0, -0.070, 0.726),
	"collar": (-0.001, -0.108, 0.626), "shirt": (0.0, -0.113, 0.583), "waist": (-0.001, -0.110, 0.514),
	"skirt": (0.0, -0.074, 0.417), "coat": (0.001, -0.033, 0.431),
	"l_sleeve": (-0.134, -0.055, 0.533), "r_sleeve": (0.133, -0.055, 0.530),
	"l_hand": (-0.195, -0.060, 0.420), "r_hand": (0.195, -0.061, 0.425),
	"l_leg": (-0.045, -0.080, 0.199), "r_leg": (0.045, -0.069, 0.197),
	"l_shoe": (-0.054, -0.097, 0.044), "r_shoe": (0.056, -0.081, 0.047),
}
KEEP = {"collar", "shirt", "waist", "l_hand", "r_hand", "l_leg", "r_leg"}
# 1차 리토폴로지 모델은 원래 부위 모델과 같은 번호 (split_tripo_textured.py REF_NAMES, 확인함)
PASS1_NAMES = {
	"tripo_part_0": "hair", "tripo_part_1": "beret", "tripo_part_8": "face", "tripo_part_10": "collar",
	"tripo_part_14": "shirt", "tripo_part_15": "waist", "tripo_part_2": "skirt", "tripo_part_12": "coat",
	"tripo_part_6": "l_sleeve", "tripo_part_3": "r_sleeve", "tripo_part_9": "l_hand", "tripo_part_11": "r_hand",
	"tripo_part_4": "l_leg", "tripo_part_5": "r_leg", "tripo_part_7": "l_shoe", "tripo_part_13": "r_shoe",
}


def load(path):
	before = set(bpy.data.objects)
	bpy.ops.import_scene.gltf(filepath=path)
	ms = [o for o in bpy.data.objects if o not in before and o.type == "MESH"]
	for o in ms:
		mw = o.matrix_world.copy()
		o.parent = None
		o.data = o.data.copy()
		o.data.transform(mw)
		o.matrix_world.identity()
	for o in list(bpy.data.objects):
		if o not in before and o.type != "MESH":
			bpy.data.objects.remove(o)
	ws = [v.co for o in ms for v in o.data.vertices]
	lo = Vector(map(min, *ws)); hi = Vector(map(max, *ws))
	return ms, lo, hi.z - lo.z


def name_of(o, lo, h):
	c = sum((v.co for v in o.data.vertices), Vector()) / len(o.data.vertices)
	c = Vector((c.x / h, c.y / h, (c.z - lo.z) / h))
	return min(CENTERS, key=lambda k: (Vector(CENTERS[k]) - c).length)


bpy.ops.wm.read_factory_settings(use_empty=True)
p1, lo1, h1 = load(PASS1)
names = {}
for o in p1:
	n = PASS1_NAMES[o.name]
	names[o.name] = n
	if n not in KEEP:
		bpy.data.objects.remove(o)
	else:
		o.name = "inner_" + n
print("pass1 parts", names)
fc, lo2, h2 = load(FACEFUL)
hair = None
for o in fc:
	if name_of(o, lo2, h2) == "hair" and (hair is None or len(o.data.polygons) > len(hair.data.polygons)):
		hair = o
for o in fc:
	if o is not hair:
		bpy.data.objects.remove(o)
# 얼굴 있는 모델 좌표 → 1차 모델 좌표 (둘 다 바닥·키로 맞춤)
s = h1 / h2
for v in hair.data.vertices:
	v.co = Vector((v.co.x * s, v.co.y * s, (v.co.z - lo2.z) * s + lo1.z))
hair.name = "inner_hair"
n0 = sum(len(p.vertices) - 2 for p in hair.data.polygons)
mod = hair.modifiers.new("dec", "DECIMATE")
mod.ratio = HAIR_TRIS / n0
bpy.context.view_layer.objects.active = hair
bpy.ops.object.modifier_apply(modifier="dec")
print("hair tris", n0, "->", sum(len(p.vertices) - 2 for p in hair.data.polygons))
# 얼굴 있는 모델 머리는 UV가 없음 → 없으면 Tripo가 칠해도 텍스처가 안 붙음 (1차 시도에서 확인)
for uvl in list(hair.data.uv_layers):
	hair.data.uv_layers.remove(uvl)
hair.data.uv_layers.new(name="UVMap")
for o in bpy.data.objects:
	o.select_set(o is hair)
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.003)
bpy.ops.object.mode_set(mode="OBJECT")
for o in bpy.data.objects:
	o.select_set(o.type == "MESH")
	if o.type == "MESH":
		o.data.materials.clear()
bpy.ops.export_scene.gltf(filepath=OUT, export_format="GLB", use_selection=True, export_normals=True)
print("saved", OUT, [o.name for o in bpy.data.objects if o.type == "MESH"])
