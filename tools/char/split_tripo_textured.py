"""Tripo가 색칠(텍스처)까지 한 마네킹을 관절별 부품으로 자르기만 하는 Blender 스크립트. 색·텍스처는 건드리지 않는다.

실행: blender -b --python tools/char/split_tripo_textured.py -- <입력.glb>
출력: assets/characters/mannequin/mannequin_tripo.glb (물체 이름 "<관절>__<부품>", 원점 = 관절)
      assets/characters/mannequin/mannequin_tripo.json (관절 위치·얼굴 자리)

면마다 붙을 관절 정하기: 부위가 따로 나뉜 모델이면 부위 이름(위치로 찾음) → 관절,
소매는 팔꿈치·다리는 무릎 평면으로 위/아래를 나눔. 관절·얼굴 자리는 prep_tripo_mannequin.py와 같은 값을 쓴다.
"""
import json
import os
import sys

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, os.path.dirname(__file__))
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_GLB = os.path.join(ROOT, "assets/characters/mannequin/mannequin_tripo.glb")
OUT_JSON = os.path.join(ROOT, "assets/characters/mannequin/mannequin_tripo.json")
HEIGHT = 1.55
# 부위 이름을 정할 때 쓰는 원래 부분별 생성 모델 (같은 Tripo 작업에서 나옴 → 같은 좌표)
REF = os.path.join(ROOT, "assets/art_src/char3d/mannequin_tripo_20261126/mq_tripo_W2_noface_parts.glb")
REF_NAMES = {
	"tripo_part_0": "hair", "tripo_part_1": "beret", "tripo_part_8": "face", "tripo_part_10": "collar",
	"tripo_part_14": "shirt", "tripo_part_15": "waist", "tripo_part_2": "skirt", "tripo_part_12": "coat",
	"tripo_part_6": "l_sleeve", "tripo_part_3": "r_sleeve", "tripo_part_9": "l_hand", "tripo_part_11": "r_hand",
	"tripo_part_4": "l_leg", "tripo_part_5": "r_leg", "tripo_part_7": "l_shoe", "tripo_part_13": "r_shoe",
}

# prep_tripo_mannequin.py와 같은 관절 (키 1.0 모델 기준, Blender 좌표)
JOINTS = {
	"hips": ((0.0, -0.05, 0.36), None), "spine": ((0.0, -0.05, 0.45), "hips"),
	"chest": ((0.0, -0.05, 0.55), "spine"), "neck": ((0.0, -0.045, 0.625), "chest"),
	"head": ((0.0, -0.045, 0.65), "neck"),
	"l_shoulder": ((-0.075, -0.055, 0.615), "chest"), "l_elbow": ((-0.13, -0.057, 0.535), "l_shoulder"),
	"l_wrist": ((-0.188, -0.06, 0.452), "l_elbow"),
	"r_shoulder": ((0.075, -0.055, 0.615), "chest"), "r_elbow": ((0.13, -0.057, 0.535), "r_shoulder"),
	"r_wrist": ((0.188, -0.06, 0.452), "r_elbow"),
	"l_hip": ((-0.045, -0.07, 0.345), "hips"), "l_knee": ((-0.045, -0.072, 0.205), "l_hip"),
	"l_ankle": ((-0.05, -0.075, 0.075), "l_knee"),
	"r_hip": ((0.045, -0.07, 0.345), "hips"), "r_knee": ((0.045, -0.072, 0.205), "r_hip"),
	"r_ankle": ((0.05, -0.075, 0.075), "r_knee"),
}
FACE_CENTER = (0.0, 0.745)
FACE_SIZE = 0.15
# face_from_paint.py가 칠한 정면 그림에서 얼굴 네모를 재면 그 값을 씀
FACE_FIT = os.path.join(ROOT, "assets/characters/mannequin/face_fit.json")
if os.path.exists(FACE_FIT):
	_ff = json.load(open(FACE_FIT, encoding="utf-8"))
	FACE_CENTER = tuple(_ff["center"])
	FACE_SIZE = _ff["size"]
# 부분별 생성 모델의 부위 중심(키 1.0 기준, 확인함) → 이름. 다시 만든 모델에서는 가장 가까운 중심으로 이름을 정함
PART_CENTERS = {
	"hair": (-0.002, -0.009, 0.763), "beret": (-0.004, 0.022, 0.881), "face": (0.0, -0.070, 0.726),
	"collar": (-0.001, -0.108, 0.626), "shirt": (0.0, -0.113, 0.583), "waist": (-0.001, -0.110, 0.514),
	"skirt": (0.0, -0.074, 0.417), "coat": (0.001, -0.033, 0.431),
	"l_sleeve": (-0.134, -0.055, 0.533), "r_sleeve": (0.133, -0.055, 0.530),
	"l_hand": (-0.195, -0.060, 0.420), "r_hand": (0.195, -0.061, 0.425),
	"l_leg": (-0.045, -0.080, 0.199), "r_leg": (0.045, -0.069, 0.197),
	"l_shoe": (-0.054, -0.097, 0.044), "r_shoe": (0.056, -0.081, 0.047),
}
PART_JOINT = {"hair": "head", "beret": "head", "face": "head", "collar": "chest", "shirt": "chest",
	"waist": "spine", "skirt": "hips", "coat": "chest", "l_hand": "l_wrist", "r_hand": "r_wrist",
	"l_shoe": "l_ankle", "r_shoe": "r_ankle"}
CUTS = {"l_sleeve": ("l_elbow", "l_shoulder", "l_elbow"), "r_sleeve": ("r_elbow", "r_shoulder", "r_elbow"),
	"l_leg": ("l_knee", "l_hip", "l_knee"), "r_leg": ("r_knee", "r_hip", "r_knee")}


def main():
	src = sys.argv[sys.argv.index("--") + 1]
	bpy.ops.wm.read_factory_settings(use_empty=True)
	ref_bvh, ref_part = load_reference()
	before = set(bpy.data.objects)
	bpy.ops.import_scene.gltf(filepath=src)
	meshes = [o for o in bpy.data.objects if o not in before and o.type == "MESH"]
	for o in meshes:
		mw = o.matrix_world.copy()
		o.parent = None
		o.matrix_world = mw
		bpy.context.view_layer.objects.active = o
		o.select_set(True)
		bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
		o.select_set(False)
	ws = [o.matrix_world @ v.co for o in meshes for v in o.data.vertices]
	lo = Vector(map(min, *ws)); hi = Vector(map(max, *ws))
	h = hi.z - lo.z
	print(f"input meshes {len(meshes)} faces {sum(len(o.data.polygons) for o in meshes)} height {h:.3f}")
	# 키 1.0·바닥 0 기준으로 (관절 값이 그 기준)
	norm = 1.0 / h
	for o in meshes:
		for v in o.data.vertices:
			v.co = (v.co - Vector((0, 0, lo.z))) * norm

	# 면마다 부위 이름: 물체가 여러 개면 물체 중심으로, 한 덩어리면 면 중심에서 가장 가까운 부위 중심으로
	pieces = {}
	for o in meshes:
		bm = bmesh.new(); bm.from_mesh(o.data); bm.faces.ensure_lookup_table()
		groups = {}
		for f in bm.faces:
			_, _, idx, _ = ref_bvh.find_nearest(f.calc_center_median())
			groups.setdefault(ref_part[idx] if idx is not None else "coat", []).append(f.index)
		bm.free()
		print(o.name, {k: len(v) for k, v in groups.items()})
		if len(meshes) > 1:
			# 부위가 이미 나뉜 모델: 물체 하나 = 부위 하나 (가장 많이 나온 이름)
			main = max(groups, key=lambda k: len(groups[k]))
			groups = {main: [i for v in groups.values() for i in v]}
		for name, idx in groups.items():
			for key, ob in split_part(o, name, idx).items():
				pieces[key] = ob
	s = HEIGHT
	out = {}
	for key, (joint, ob) in pieces.items():
		jp = Vector(JOINTS[joint][0])
		for v in ob.data.vertices:
			v.co = (v.co - jp) * s
		ob.location = jp * s
		ob.name = f"{joint}__{key}"
		ob.data.name = ob.name
		for p in ob.data.polygons:
			p.use_smooth = True
		out[ob.name] = ob
	for o in list(bpy.context.scene.objects):
		o.select_set(o.name in out)
	bpy.ops.export_scene.gltf(filepath=OUT_GLB, export_format="GLB", use_selection=True,
		export_normals=True, export_apply=True, export_image_format="AUTO")
	data = {
		"height": HEIGHT,
		"joints": {k: {"pos": list(to_godot(Vector(v[0]) * s)), "parent": v[1]} for k, v in JOINTS.items()},
		"face": {"center": [FACE_CENTER[0] * s, (FACE_CENTER[1] - JOINTS["head"][0][2]) * s], "size": FACE_SIZE * s,
			"textures": ["res://assets/characters/mannequin/face_w2_s0.png"]},
		"faces_total": sum(len(o.data.polygons) for o in out.values()),
		"source": os.path.basename(src),
	}
	with open(OUT_JSON, "w", encoding="utf-8") as f:
		json.dump(data, f, ensure_ascii=False, indent=1)
	print("saved", OUT_GLB, "pieces", len(out), "faces", data["faces_total"])


def load_reference():
	"""원래 부위 모델을 키 1.0·바닥 0으로 맞춰 BVH와 면→부위 이름 표를 만든 뒤 지운다."""
	before = set(bpy.data.objects)
	bpy.ops.import_scene.gltf(filepath=REF)
	objs = [o for o in bpy.data.objects if o not in before and o.type == "MESH"]
	verts, polys, part = [], [], []
	for o in objs:
		name = REF_NAMES.get(o.name)
		if name is None:
			continue
		off = len(verts)
		verts += [o.matrix_world @ v.co for v in o.data.vertices]
		for p in o.data.polygons:
			polys.append([off + i for i in p.vertices]); part.append(name)
	lo_z = min(v.z for v in verts); h = max(v.z for v in verts) - lo_z
	verts = [Vector((v.x / h, v.y / h, (v.z - lo_z) / h)) for v in verts]
	for o in list(bpy.data.objects):
		if o not in before:
			bpy.data.objects.remove(o)
	return BVHTree.FromPolygons(verts, polys), part


def split_part(o, name, face_idx):
	"""o에서 face_idx 면만 떼어 새 물체로. 소매·다리는 관절 평면으로 위/아래 둘로."""
	result = {}
	keep = set(face_idx)
	if name in CUTS:
		cut_joint, up_j, lo_j = CUTS[name]
		cp = Vector(JOINTS[cut_joint][0])
		axis = (cp - Vector(JOINTS[JOINTS[cut_joint][1]][0])).normalized()
		up, low = [], []
		for i in keep:
			c = o.data.polygons[i].center
			(low if (c - cp).dot(axis) > 0 else up).append(i)
		result[f"{name}_up"] = (up_j, copy_faces(o, set(up), f"{name}_up"))
		result[f"{name}_low"] = (lo_j, copy_faces(o, set(low), f"{name}_low"))
	else:
		result[name] = (PART_JOINT[name], copy_faces(o, keep, name))
	return result


def copy_faces(o, keep, name):
	ob = o.copy(); ob.data = o.data.copy(); ob.name = name
	bpy.context.collection.objects.link(ob)
	bm = bmesh.new(); bm.from_mesh(ob.data); bm.faces.ensure_lookup_table()
	bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.index not in keep], context="FACES")
	# Tripo 부품 중 일부(얼굴·셔츠·다리)는 면이 안쪽을 봄 → 바깥을 보는 면이 절반 미만이면 통째로 뒤집음
	if bm.faces:
		c = sum((v.co for v in bm.verts), Vector()) / len(bm.verts)
		out = sum(1 for f in bm.faces if (f.calc_center_median() - c).dot(f.normal) > 0)
		if out < len(bm.faces) * 0.5:
			bmesh.ops.reverse_faces(bm, faces=bm.faces[:])
			print(f"flip normals: {name} ({out}/{len(bm.faces)} outward)")
	bm.to_mesh(ob.data); bm.free()
	return ob


def to_godot(v):
	return (round(v.x, 4), round(v.z, 4), round(-v.y, 4))


main()
