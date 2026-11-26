"""1차 텍스처 모델(겉 부위) + 2차 텍스처 모델(속 부위·새 머리)을 한 모델로 합치는 Blender 스크립트.

실행: blender -b --python tools/char/merge_inner_pass.py -- <2차 결과.glb>
출력: assets/art_src/char3d/mannequin_tripo_20261126/mq_tripo_W2_merged.glb
  → 그다음 split_tripo_textured.py에 그대로 넣는다.

- 1차(mq_tripo_W2_retopo_tex.glb)에서 코트·소매·베레모·치마·신발·얼굴판만 남기고
  셔츠·깃·허리·다리·손·머리는 지운다 (2차 것으로 바꿈).
- 2차 결과는 Tripo가 위치·크기·방향을 바꿔 놓을 수 있어서, 올린 모델(inner_pass_in.glb)에
  4방향(0·90·180·270도) × 상자 맞춤으로 겹쳐 보고 점 거리가 가장 작은 것을 고른다.
- 2차 결과가 한 덩어리면 면마다 올린 모델의 가장 가까운 부위로 나눠 부위별 물체로 만든다.
- 얼굴판은 앞머리 그림자 얼룩이 있으므로 텍스처의 피부색(중앙값) 한 색으로 바꾼다
  (눈·입은 게임에서 얼굴 그림으로 덮음).
"""
import math
import os
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
D = os.path.join(ROOT, "assets/art_src/char3d/mannequin_tripo_20261126")
PASS1 = os.path.join(D, "mq_tripo_W2_retopo_tex.glb")
INNER_IN = os.path.join(D, "inner_pass_in.glb")
OUT = os.path.join(D, "mq_tripo_W2_merged.glb")
PASS1_NAMES = {
	"tripo_part_0": "hair", "tripo_part_1": "beret", "tripo_part_8": "face", "tripo_part_10": "collar",
	"tripo_part_14": "shirt", "tripo_part_15": "waist", "tripo_part_2": "skirt", "tripo_part_12": "coat",
	"tripo_part_6": "l_sleeve", "tripo_part_3": "r_sleeve", "tripo_part_9": "l_hand", "tripo_part_11": "r_hand",
	"tripo_part_4": "l_leg", "tripo_part_5": "r_leg", "tripo_part_7": "l_shoe", "tripo_part_13": "r_shoe",
}
OUTER = {"beret", "coat", "l_sleeve", "r_sleeve", "skirt", "l_shoe", "r_shoe", "face"}


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
	return ms


def verts_np(objs):
	return np.array([tuple(v.co) for o in objs for v in o.data.vertices], dtype=np.float64)


def bbox(P):
	return P.min(0), P.max(0)


def main():
	src = sys.argv[sys.argv.index("--") + 1]
	bpy.ops.wm.read_factory_settings(use_empty=True)
	# 기준: 올린 모델 (1차 좌표)
	ref = load(INNER_IN)
	ref_P = verts_np(ref)
	rlo, rhi = bbox(ref_P)
	ref_verts, ref_polys, ref_part = [], [], []
	for o in ref:
		off = len(ref_verts)
		ref_verts += [v.co.copy() for v in o.data.vertices]
		for p in o.data.polygons:
			ref_polys.append([off + i for i in p.vertices]); ref_part.append(o.name.split(".")[0].replace("inner_", ""))
	ref_bvh = BVHTree.FromPolygons(ref_verts, ref_polys)
	for o in ref:
		bpy.data.objects.remove(o)

	# 2차 결과 → 기준 좌표로 (세로축 둘레 4방향 중 가장 잘 맞는 것)
	p2 = load(src)
	P = verts_np(p2)
	best = None
	sample = P[:: max(1, len(P) // 3000)]
	for deg in (0, 90, 180, 270):
		R = Matrix.Rotation(math.radians(deg), 3, "Z")
		Rn = np.array(R)
		Q = P @ Rn.T
		qlo, qhi = bbox(Q)
		s = (rhi[2] - rlo[2]) / (qhi[2] - qlo[2])
		t = (rlo + rhi) / 2 - (qlo + qhi) / 2 * s
		S = (sample @ Rn.T) * s + t
		err = np.mean([ref_bvh.find_nearest(Vector(p))[3] for p in S])
		print(f"rot {deg}: scale {s:.4f} err {err:.5f}")
		if best is None or err < best[0]:
			best = (err, Rn, s, t, deg)
	err, Rn, s, t, deg = best
	print(f"use rot {deg} err {err:.5f}")
	M = Matrix(((*(Rn[0] * s), t[0]), (*(Rn[1] * s), t[1]), (*(Rn[2] * s), t[2]), (0, 0, 0, 1)))
	for o in p2:
		o.data.transform(M)
		if M.determinant() < 0:
			o.data.flip_normals()

	# 2차 결과를 부위별 물체로 (면마다 가장 가까운 올린 모델 부위)
	inner = []
	for o in p2:
		bm = bmesh.new(); bm.from_mesh(o.data); bm.faces.ensure_lookup_table()
		groups = {}
		for f in bm.faces:
			_, _, idx, _ = ref_bvh.find_nearest(f.calc_center_median())
			groups.setdefault(ref_part[idx], []).append(f.index)
		bm.free()
		print("pass2", o.name, {k: len(v) for k, v in groups.items()})
		for name, idx in groups.items():
			keep = set(idx)
			ob = o.copy(); ob.data = o.data.copy(); ob.name = "inner_" + name
			bpy.context.collection.objects.link(ob)
			bm = bmesh.new(); bm.from_mesh(ob.data); bm.faces.ensure_lookup_table()
			bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.index not in keep], context="FACES")
			bm.to_mesh(ob.data); bm.free()
			inner.append(ob)
		bpy.data.objects.remove(o)

	# 1차: 겉 부위만
	p1 = load(PASS1)
	for o in p1:
		n = PASS1_NAMES[o.name]
		if n not in OUTER:
			bpy.data.objects.remove(o)
			continue
		o.name = "outer_" + n
		if n == "face":
			flatten_face(o)
	for o in bpy.data.objects:
		o.select_set(o.type == "MESH")
	bpy.ops.export_scene.gltf(filepath=OUT, export_format="GLB", use_selection=True,
		export_normals=True, export_image_format="AUTO")
	print("saved", OUT, sorted(o.name for o in bpy.data.objects if o.type == "MESH"))


def flatten_face(o):
	"""얼굴판 텍스처를 그 텍스처 밝은 부분(피부)의 중앙값 한 색으로."""
	for mat in o.data.materials:
		for node in mat.node_tree.nodes:
			if node.type == "TEX_IMAGE" and node.image and "basecolor" in node.image.name.lower() + node.image.filepath.lower():
				img = node.image
				w, h = img.size
				px = np.array(img.pixels[:], dtype=np.float32).reshape(-1, 4)
				lum = px[:, :3].mean(1)
				skin = np.median(px[lum > np.percentile(lum, 50), :3], axis=0)
				new = bpy.data.images.new(img.name + "_flat", 8, 8)
				new.pixels = np.tile(np.append(skin, 1.0), 64).tolist()
				new.pack()
				node.image = new
				print("face flat color", np.round(skin * 255).astype(int))


main()
