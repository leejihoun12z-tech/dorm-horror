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
			hair = [x for x in inner if base(x.name) == "inner_hair"]
			if hair:
				full_head(o, hair[0])
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


def full_head(face, hair):
	"""얼굴판(앞머리 밑으로 보이던 조각뿐)을 온전한 머리통으로 바꾼다.
	공 모양에서 시작해 중심에서 바깥으로 광선을 쏴서: 얼굴판에 맞으면 그 자리(코·턱 모양 유지),
	아니면 머리카락 안쪽 93% 지점(머리카락 밖으로 안 나옴), 아무것도 없으면 타원 그대로.
	→ 얼굴판과 머리카락 사이 구멍이 없어지고, 얼굴 그림이 얹힐 면이 이마·관자놀이까지 이어짐."""
	fv = np.array([tuple(v.co) for v in face.data.vertices])
	hv = np.array([tuple(v.co) for v in hair.data.vertices])
	chin = fv[:, 2].min(); top = hv[:, 2].max()
	c = Vector((0.0, float((hv[:, 1].min() + hv[:, 1].max()) / 2), float(chin + (top - chin) * 0.5)))
	rx = float((hv[:, 0].max() - hv[:, 0].min()) / 2 * 0.86)
	ry = float((hv[:, 1].max() - hv[:, 1].min()) / 2 * 0.86)
	rz = float((top - chin) * 0.5)

	def tree(o):
		return BVHTree.FromPolygons([v.co.copy() for v in o.data.vertices], [list(p.vertices) for p in o.data.polygons])
	ft, ht = tree(face), tree(hair)
	bm = bmesh.new()
	bmesh.ops.create_uvsphere(bm, u_segments=64, v_segments=40, radius=1.0)
	hit_face = {}
	for v in bm.verts:
		d = v.co.normalized()
		ell = 1.0 / math.sqrt((d.x / rx) ** 2 + (d.y / ry) ** 2 + (d.z / rz) ** 2)
		r = ell
		hf = ft.ray_cast(c, d)
		if hf[0] is not None:
			r = hf[3]; hit_face[v.index] = True
		else:
			hh = ht.ray_cast(c, d)
			if hh[0] is not None:
				r = min(ell, hh[3] * 0.93)
		v.co = c + d * r
	# 얼굴판에 안 맞은 점만 이웃 평균으로 몇 번 다듬음 (얼굴판 경계 턱 줄이기)
	for _ in range(6):
		new = {}
		for v in bm.verts:
			if v.index in hit_face:
				continue
			nb = [e.other_vert(v).co for e in v.link_edges]
			new[v.index] = (v.co + sum(nb, Vector()) / len(nb)) / 2
		bm.verts.ensure_lookup_table()
		for i, co in new.items():
			d = (co - c).normalized()
			hh = ht.ray_cast(c, d)
			r = (co - c).length
			if hh[0] is not None:
				r = min(r, hh[3] * 0.93)
			bm.verts[i].co = c + d * r
	# 목: 원래 얼굴판을 머리 중심 쪽으로 5% 줄여 머리통 안에 그대로 둠 → 목 부분만 밖으로 보임
	# (찢어진 윗가장자리는 머리통 안에 숨고, 외곽선 껍데기 3.5mm도 안 튀어나옴)
	old = bmesh.new(); old.from_mesh(face.data)
	vmap = {}
	for v in old.verts:
		vmap[v.index] = bm.verts.new(c + (v.co - c) * 0.95)
	old.normal_update()
	oc = sum((v.co for v in old.verts), Vector()) / len(old.verts)
	inward = sum(1 for f in old.faces if (f.calc_center_median() - oc).dot(f.normal) < 0) > len(old.faces) / 2
	for f in old.faces:
		try:
			vs = [vmap[v.index] for v in f.verts]
			bm.faces.new(vs[::-1] if inward else vs)
		except ValueError:
			pass
	old.free()
	bm.normal_update()
	me = face.data
	mats = list(me.materials)
	bm.to_mesh(me); bm.free()
	uvl = me.uv_layers.new(name="UVMap") if not me.uv_layers else me.uv_layers.active
	for l in uvl.data:
		l.uv = (0.5, 0.5)
	for p in me.polygons:
		p.use_smooth = True
	if not me.materials:
		for m in mats:
			me.materials.append(m)
	print("full head: verts", len(me.vertices), "from face plate hits", len(hit_face))


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
