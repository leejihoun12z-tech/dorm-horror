"""겉 부위 텍스처 모델 + 속 부위 텍스처 모델을 한 모델로 합치는 Blender 스크립트.

실행: blender -b --python tools/char/merge_inner_pass.py -- <겉 결과.glb> <속 결과.glb> [<출력.glb>]
  겉 결과: 이름이 outer_* 인 물체만 쓴다 (없으면 1차 리토폴로지 모델 번호표 PASS1_NAMES로 겉 부위를 고름)
  속 결과: inner_* 물체 (셔츠·깃·허리·다리·손·머리)
출력(기본): assets/art_src/char3d/mannequin_tripo_20261126/mq_tripo_W2_final.glb → split_tripo_textured.py

- Tripo 결과는 위치·크기·방향이 바뀔 수 있어서, 기준 모양(REF_GEOM, 우리가 올린 모델)에
  4방향 × 상자 맞춤으로 겹쳐 보고 점 거리가 가장 작은 것을 고른다.
- 결과가 한 덩어리면 면마다 기준 모양의 가장 가까운 부위로 나눈다.
- 얼굴판은 피부색 한 색 (눈·입은 게임에서 얼굴 그림으로 덮음).
- 텍스처 가장자리 채우기: Tripo 텍스처는 UV 조각 밖이 검정이라 멀리서(밉맵)·조각 경계에서 검은 줄이 생김
  → 조각 밖을 주변 조각 색으로 채움(push-pull). 그림 안쪽(칠한 색)은 건드리지 않음.
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
REF_GEOM = os.path.join(D, "mq_tripo_W2_merged.glb")  # 겉·속 모두 이 모양을 올려서 칠함
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


def base(name):
	return name.split(".")[0]


def ref_tree():
	"""기준 모양: BVH + 면 → 부위 이름 (inner_x / outer_x 에서 x)."""
	objs = load(REF_GEOM)
	verts, polys, part, vpart = [], [], [], []
	for o in objs:
		off = len(verts)
		verts += [v.co.copy() for v in o.data.vertices]
		vpart += [base(o.name)] * len(o.data.vertices)
		for p in o.data.polygons:
			polys.append([off + i for i in p.vertices]); part.append(base(o.name))
	P = np.array([tuple(v) for v in verts])
	vpart = np.array(vpart)
	for o in objs:
		bpy.data.objects.remove(o)

	def box(prefixes):
		m = np.array([any(n.startswith(k) for k in prefixes) for n in vpart])
		return P[m].min(0), P[m].max(0)
	return BVHTree.FromPolygons(verts, polys), part, box


def align(objs, bvh, rlo, rhi):
	P = np.array([tuple(v.co) for o in objs for v in o.data.vertices])
	sample = P[:: max(1, len(P) // 3000)]
	best = None
	for deg in (0, 90, 180, 270):
		Rn = np.array(Matrix.Rotation(math.radians(deg), 3, "Z"))
		Q = P @ Rn.T
		qlo, qhi = Q.min(0), Q.max(0)
		s = (rhi[2] - rlo[2]) / (qhi[2] - qlo[2])
		t = (rlo + rhi) / 2 - (qlo + qhi) / 2 * s
		err = np.mean([bvh.find_nearest(Vector(p))[3] for p in (sample @ Rn.T) * s + t])
		if best is None or err < best[0]:
			best = (err, Rn, s, t, deg)
	err, Rn, s, t, deg = best
	print(f"align rot {deg} scale {s:.4f} err {err:.5f}")
	M = Matrix(((*(Rn[0] * s), t[0]), (*(Rn[1] * s), t[1]), (*(Rn[2] * s), t[2]), (0, 0, 0, 1)))
	for o in objs:
		o.data.transform(M)


def split_by_ref(objs, bvh, part, want):
	"""물체마다 면을 기준 부위로 나눠 want(접두어 목록)에 드는 부위만 남김."""
	out = []
	for o in objs:
		bm = bmesh.new(); bm.from_mesh(o.data); bm.faces.ensure_lookup_table()
		groups = {}
		for f in bm.faces:
			_, _, idx, _ = bvh.find_nearest(f.calc_center_median())
			groups.setdefault(part[idx], []).append(f.index)
		bm.free()
		main = max(groups, key=lambda k: len(groups[k]))
		# 물체 하나 = 부위 하나면(Tripo가 부위를 지킴) 통째로, 아니면 면마다
		if len(groups[main]) > 0.9 * len(o.data.polygons):
			groups = {main: [i for v in groups.values() for i in v]}
		print("split", o.name, {k: len(v) for k, v in groups.items()})
		for name, idx in groups.items():
			if not any(name.startswith(w) for w in want):
				continue
			keep = set(idx)
			ob = o.copy(); ob.data = o.data.copy(); ob.name = name
			bpy.context.collection.objects.link(ob)
			bm = bmesh.new(); bm.from_mesh(ob.data); bm.faces.ensure_lookup_table()
			bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.index not in keep], context="FACES")
			bm.to_mesh(ob.data); bm.free()
			out.append(ob)
		bpy.data.objects.remove(o)
	return out


def main():
	argv = sys.argv[sys.argv.index("--") + 1:]
	outer_src, inner_src = argv[0], argv[1]
	out_path = argv[2] if len(argv) > 2 else os.path.join(D, "mq_tripo_W2_final.glb")
	bpy.ops.wm.read_factory_settings(use_empty=True)
	bvh, part, box = ref_tree()

	inner = load(inner_src)
	# 속 결과 = 속 부위만 올린 모델(얼굴판 없음) → 속 부위 상자로 맞춤
	align(inner, bvh, *box(["inner_"]))
	inner = split_by_ref(inner, bvh, part, ["inner_"])

	outer = load(outer_src)
	if any(base(o.name).startswith("outer_") for o in outer):
		align(outer, bvh, *box(["inner_", "outer_"]))
		outer = split_by_ref(outer, bvh, part, ["outer_"])
	else:  # 1차 리토폴로지 모델(번호 이름) = 이미 기준 좌표
		keep = []
		for o in outer:
			n = PASS1_NAMES.get(base(o.name))
			if n in OUTER:
				o.name = "outer_" + n; keep.append(o)
			else:
				bpy.data.objects.remove(o)
		outer = keep
	for o in outer:
		if base(o.name) == "outer_face":
			flatten_face(o)
	pad_all(inner + outer)
	for o in bpy.data.objects:
		o.select_set(o.type == "MESH")
	bpy.ops.export_scene.gltf(filepath=out_path, export_format="GLB", use_selection=True,
		export_normals=True, export_image_format="AUTO")
	print("saved", out_path, sorted(o.name for o in bpy.data.objects if o.type == "MESH"))


def base_images(o):
	for mat in o.data.materials:
		if not mat or not mat.node_tree:
			continue
		for node in mat.node_tree.nodes:
			if node.type == "TEX_IMAGE" and node.image:
				links = [l for l in mat.node_tree.links if l.from_node == node]
				if any(l.to_socket.name == "Base Color" for l in links):
					yield node


def flatten_face(o):
	"""얼굴판 텍스처를 밝은 부분(피부)의 중앙값 한 색으로."""
	for node in base_images(o):
		px = np.array(node.image.pixels[:], dtype=np.float32).reshape(-1, 4)
		lum = px[:, :3].mean(1)
		skin = np.median(px[lum > np.percentile(lum, 50), :3], axis=0)
		new = bpy.data.images.new(node.image.name + "_flat", 8, 8)
		new.pixels = np.tile(np.append(skin, 1.0), 64).tolist()
		new.pack()
		node.image = new
		print("face flat color", np.round(skin * 255).astype(int))


def pad_all(objs):
	"""텍스처마다 그 텍스처를 쓰는 물체의 UV 조각 자리를 그려(mask) 조각 밖을 주변 색으로 채운다."""
	users = {}
	for o in objs:
		for node in base_images(o):
			users.setdefault(node.image.name, (node.image, []))[1].append(o)
	for name, (img, os_) in users.items():
		w, h = img.size
		if w < 16:
			continue
		mask = np.zeros((h, w), dtype=bool)
		for o in os_:
			uvl = o.data.uv_layers.active
			if uvl is None:
				continue
			uv = np.zeros(len(o.data.loops) * 2, dtype=np.float32)
			uvl.data.foreach_get("uv", uv)
			uv = uv.reshape(-1, 2)
			for p in o.data.polygons:
				li = list(p.loop_indices)
				for k in range(1, len(li) - 1):
					raster_tri(mask, uv[[li[0], li[k], li[k + 1]]], w, h)
		px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)
		filled = push_pull(px[..., :3], mask)
		px[..., :3] = filled
		img.pixels.foreach_set(px.ravel())
		img.pack()
		print(f"pad {name} {w}x{h} island {mask.mean():.2f}")


def raster_tri(mask, t, w, h):
	xs = t[:, 0] * w; ys = t[:, 1] * h  # 이미지 픽셀 행 = 아래에서부터 (Blender pixels 순서와 같음)
	x0, x1 = max(0, int(np.floor(xs.min())) - 1), min(w - 1, int(np.ceil(xs.max())) + 1)
	y0, y1 = max(0, int(np.floor(ys.min())) - 1), min(h - 1, int(np.ceil(ys.max())) + 1)
	if x1 < x0 or y1 < y0:
		return
	gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
	(ax, bx, cx), (ay, by, cy) = xs, ys
	den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
	if abs(den) < 1e-12:
		return
	w0 = ((by - cy) * (gx - cx) + (cx - bx) * (gy - cy)) / den
	w1 = ((cy - ay) * (gx - cx) + (ax - cx) * (gy - cy)) / den
	e = -0.02
	m = (w0 >= e) & (w1 >= e) & (1 - w0 - w1 >= e)
	mask[y0:y1 + 1, x0:x1 + 1] |= m


def push_pull(col, mask):
	"""mask 밖 픽셀을 가까운 mask 안 색으로 (반씩 줄인 단계의 평균을 거꾸로 채워 내려옴)."""
	levels = [(col * mask[..., None], mask.astype(np.float32))]
	while min(levels[-1][1].shape) > 1:
		c, wgt = levels[-1]
		hh, ww = (wgt.shape[0] // 2) * 2, (wgt.shape[1] // 2) * 2
		c = c[:hh, :ww]; wgt = wgt[:hh, :ww]
		c2 = c[0::2, 0::2] + c[1::2, 0::2] + c[0::2, 1::2] + c[1::2, 1::2]
		w2 = wgt[0::2, 0::2] + wgt[1::2, 0::2] + wgt[0::2, 1::2] + wgt[1::2, 1::2]
		levels.append((c2, w2))
	c, wgt = levels[-1]
	cur = c / np.maximum(wgt, 1e-6)[..., None]
	for c, wgt in reversed(levels[:-1]):
		up = np.repeat(np.repeat(cur, 2, 0), 2, 1)
		pad_h, pad_w = wgt.shape[0] - up.shape[0], wgt.shape[1] - up.shape[1]
		if pad_h > 0 or pad_w > 0:
			up = np.pad(up, ((0, max(0, pad_h)), (0, max(0, pad_w)), (0, 0)), mode="edge")
		up = up[:wgt.shape[0], :wgt.shape[1]]
		own = c / np.maximum(wgt, 1e-6)[..., None]
		cur = np.where((wgt > 0)[..., None], own, up)
	out = col.copy()
	out[~mask] = cur[~mask]
	return out


main()
