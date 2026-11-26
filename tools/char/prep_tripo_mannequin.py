"""Tripo 마네킹(부분별 생성 glb)을 게임용으로 정리 — Blender 스크립트.

실행: blender -b --python tools/char/prep_tripo_mannequin.py
입력: assets/art_src/char3d/mannequin_tripo_20261126/mq_tripo_W2_noface_parts.glb
      assets/art_src/char3d/mannequin_deform_20261126/noface/W2_{front_noface,right_noface,back}.png (색 비추기용)
출력: assets/characters/mannequin/mannequin_tripo.glb  (물체 이름 "<관절>__<부품>", 원점 = 관절)
      assets/characters/mannequin/mannequin_tripo.json (관절 위치·얼굴 자리)

순서: ① 부위 이름 붙이기 ② 면 줄이기 ③ 그림을 비춰 면마다 색 → 팔레트 색으로 맞춤(Family Time식 평면 색)
      ④ 소매는 팔꿈치, 다리는 무릎에서 잘라 관절별 부품으로 + 관절 구슬 ⑤ 키 1.55m로 키워 내보내기
좌표: Blender(z 위, 캐릭터 정면 = -Y). glTF로 내보내면 Godot에서 y 위·정면 +Z.
"""
import json
import math
import os

import bmesh
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = os.path.join(ROOT, "assets/art_src/char3d/mannequin_tripo_20261126/mq_tripo_W2_noface_parts.glb")
IMG_DIR = os.path.join(ROOT, "assets/art_src/char3d/mannequin_deform_20261126/noface")
OUT_GLB = os.path.join(ROOT, "assets/characters/mannequin/mannequin_tripo.glb")
OUT_JSON = os.path.join(ROOT, "assets/characters/mannequin/mannequin_tripo.json")
HEIGHT = 1.55
SMOOTH_PASSES = 5
# 이보다 작은 색 섬(이어진 면 수)은 주변 색으로
MIN_ISLAND = 30
# 디자인 색 (sRGB). W2 그림에서 뽑아 손으로 고정
PALETTE = {
	"black": (34, 29, 31), "hair": (50, 43, 47), "red": (196, 30, 40), "white": (238, 234, 236),
	"skin": (247, 233, 233), "gold": (214, 168, 86), "joint": (78, 68, 72),
}
# 부위마다 쓸 수 있는 색
ALLOWED = {
	"hair": ["hair", "red"], "beret": ["red", "black", "gold"], "face": ["skin"],
	"collar": ["white", "red", "black", "gold"], "shirt": ["white", "gold", "black"], "waist": ["black", "gold"],
	"skirt": ["black"], "coat": ["black", "red"], "l_sleeve": ["black", "gold"], "r_sleeve": ["black", "gold"],
	"l_hand": ["white"], "r_hand": ["white"], "l_leg": ["white"], "r_leg": ["white"],
	"l_shoe": ["black"], "r_shoe": ["black"],
}

# 부위 이름 (mq_tripo_W2_noface_parts.glb 기준, 위치로 확인함). x<0 = l (mannequin.gd와 같은 쪽)
PART_NAMES = {
	"tripo_part_0": "hair", "tripo_part_1": "beret", "tripo_part_8": "face", "tripo_part_10": "collar",
	"tripo_part_14": "shirt", "tripo_part_15": "waist", "tripo_part_2": "skirt", "tripo_part_12": "coat",
	"tripo_part_6": "l_sleeve", "tripo_part_3": "r_sleeve", "tripo_part_9": "l_hand", "tripo_part_11": "r_hand",
	"tripo_part_4": "l_leg", "tripo_part_5": "r_leg", "tripo_part_7": "l_shoe", "tripo_part_13": "r_shoe",
}
# 부위별 남길 면 수 (모두 합쳐 약 2만)
TARGET_FACES = {"hair": 4200, "coat": 3600, "beret": 1200, "face": 900, "skirt": 700, "shirt": 500,
	"waist": 300, "collar": 400, "l_sleeve": 700, "r_sleeve": 700, "l_hand": 350, "r_hand": 350,
	"l_leg": 600, "r_leg": 600, "l_shoe": 350, "r_shoe": 350}

# 관절 (Blender 좌표, 키 1.0 모델 기준). 부모 → 자식 순서
JOINTS = {
	"hips": ((0.0, -0.05, 0.36), None),
	"spine": ((0.0, -0.05, 0.45), "hips"),
	"chest": ((0.0, -0.05, 0.55), "spine"),
	"neck": ((0.0, -0.045, 0.625), "chest"),
	"head": ((0.0, -0.045, 0.65), "neck"),
	"l_shoulder": ((-0.075, -0.055, 0.615), "chest"),
	"l_elbow": ((-0.13, -0.057, 0.535), "l_shoulder"),
	"l_wrist": ((-0.188, -0.06, 0.452), "l_elbow"),
	"r_shoulder": ((0.075, -0.055, 0.615), "chest"),
	"r_elbow": ((0.13, -0.057, 0.535), "r_shoulder"),
	"r_wrist": ((0.188, -0.06, 0.452), "r_elbow"),
	"l_hip": ((-0.045, -0.07, 0.345), "hips"),
	"l_knee": ((-0.045, -0.072, 0.205), "l_hip"),
	"l_ankle": ((-0.05, -0.075, 0.075), "l_knee"),
	"r_hip": ((0.045, -0.07, 0.345), "hips"),
	"r_knee": ((0.045, -0.072, 0.205), "r_hip"),
	"r_ankle": ((0.05, -0.075, 0.075), "r_knee"),
}
# 부품 → 관절. 소매·다리는 자른 뒤 위/아래가 각각 다른 관절로
PART_JOINT = {"hair": "head", "beret": "head", "face": "head", "collar": "chest", "shirt": "chest",
	"waist": "spine", "skirt": "hips", "coat": "chest", "l_hand": "l_wrist", "r_hand": "r_wrist",
	"l_shoe": "l_ankle", "r_shoe": "r_ankle"}
CUTS = {  # 부품: (자를 관절, 위쪽 관절, 아래쪽 관절)
	"l_sleeve": ("l_elbow", "l_shoulder", "l_elbow"), "r_sleeve": ("r_elbow", "r_shoulder", "r_elbow"),
	"l_leg": ("l_knee", "l_hip", "l_knee"), "r_leg": ("r_knee", "r_hip", "r_knee"),
}
# 얼굴 그림 자리 (Blender 좌표, 정면에서 본 중심과 크기)
FACE_CENTER = (0.0, 0.712)  # (x, z)
FACE_SIZE = 0.115


def load_view(name):
	img = bpy.data.images.load(os.path.join(IMG_DIR, name))
	w, h = img.size
	px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)[::-1, :, :3]  # 위가 0행
	fg = px.min(axis=2) < 0.92
	rows = np.where(fg.any(axis=1))[0]
	cols = np.where(fg.any(axis=0))[0]
	return {"px": px, "w": w, "h": h, "y0": rows.min(), "y1": rows.max(), "x0": cols.min(), "x1": cols.max()}


def srgb_to_linear(c):
	return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def main():
	bpy.ops.wm.read_factory_settings(use_empty=True)
	bpy.ops.import_scene.gltf(filepath=SRC)
	objs = {}
	for o in list(bpy.context.scene.objects):
		if o.type == "MESH" and o.name in PART_NAMES:
			o.name = PART_NAMES[o.name]
			objs[o.name] = o
	missing = set(PART_NAMES.values()) - set(objs)
	assert not missing, missing
	# 부모(ROOT) 변환을 메시에 굽고 떼어 냄
	for o in objs.values():
		mw = o.matrix_world.copy()
		o.parent = None
		o.matrix_world = mw
		bpy.context.view_layer.objects.active = o
		o.select_set(True)
		bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
		o.select_set(False)

	# ② 면 줄이기
	for name, o in objs.items():
		n = len(o.data.polygons)
		ratio = min(1.0, TARGET_FACES[name] / max(n, 1))
		mod = o.modifiers.new("dec", "DECIMATE")
		mod.ratio = ratio
		bpy.context.view_layer.objects.active = o
		bpy.ops.object.modifier_apply(modifier="dec")
		print(f"decimate {name}: {n} -> {len(o.data.polygons)}")

	# ③ 색 비추기: 모든 부품을 합친 BVH로 가림 검사
	verts_all, polys_all = [], []
	for o in objs.values():
		off = len(verts_all)
		verts_all += [o.matrix_world @ v.co for v in o.data.vertices]
		polys_all += [[off + i for i in p.vertices] for p in o.data.polygons]
	bvh = BVHTree.FromPolygons(verts_all, polys_all)
	lo = Vector(map(min, *verts_all))
	hi = Vector(map(max, *verts_all))
	views = {
		"front": (load_view("W2_front_noface.png"), Vector((0, -1, 0)), lambda p: p.x, (lo.x, hi.x)),
		"back": (load_view("W2_back.png"), Vector((0, 1, 0)), lambda p: -p.x, (-hi.x, -lo.x)),
		"right": (load_view("W2_right_noface.png"), Vector((-1, 0, 0)), lambda p: -p.y, (-hi.y, -lo.y)),
		"left": (load_view("W2_right_noface.png"), Vector((1, 0, 0)), lambda p: -p.y, (-hi.y, -lo.y)),
	}

	# 방향마다 그림과 모델 윤곽이 가장 잘 겹치는 크기·위치를 찾음 (겹침 비율 IoU 최대)
	pts = np.array([tuple(v) for v in verts_all], dtype=np.float32)
	for key, (v, d, ufn, (umin, umax)) in views.items():
		v["fit"] = fit_view(v, pts, ufn, (umin + umax) / 2, lo.z, hi.z)
		print(f"fit {key}: scale x{v['fit'][0]:.3f} dx {v['fit'][1]:+.1f} dy {v['fit'][2]:+.1f} IoU {v['fit'][3]:.3f}")

	def sample(view, p):
		v, d, ufn, (umin, umax) = views[view]
		k, dx, dy, _ = v["fit"]
		scale = (v["y1"] - v["y0"]) / (hi.z - lo.z) * k
		ucenter_img = (v["x0"] + v["x1"]) / 2 + dx
		ucenter_mod = (umin + umax) / 2
		x = int(round(ucenter_img + (ufn(p) - ucenter_mod) * scale))
		y = int(round(v["y1"] + dy - (p.z - lo.z) * scale))
		if 0 <= x < v["w"] and 0 <= y < v["h"]:
			return v["px"][y, x]
		return None

	face_cols = {}
	for name, o in objs.items():
		cols = []
		for poly in o.data.polygons:
			c = o.matrix_world @ poly.center
			n = (o.matrix_world.to_3x3() @ poly.normal).normalized()
			order = sorted(views, key=lambda k: -n.dot(views[k][1]))
			col = None
			for k in order:
				d = views[k][1]
				if n.dot(d) < -0.05:
					break
				hit = bvh.ray_cast(c + n * 0.0015 + d * 0.0005, d)
				if hit[0] is not None:
					continue
				s = sample(k, c)
				if s is not None and s.min() < 0.97:  # 흰 배경은 버림
					col = s
					break
			cols.append(col)
		known = [c for c in cols if c is not None]
		fallback = np.median(np.array(known), axis=0) if known else np.array([0.5, 0.5, 0.5])
		face_cols[name] = np.array([c if c is not None else fallback for c in cols])
		print(f"color {name}: seen {len(known)}/{len(cols)}")

	# 팔레트: 디자인 색(R27_2·W2) 고정 + 부위마다 쓸 수 있는 색만 → 가장 가까운 색 → 이웃 다수결로 외톨이 얼룩 지우기
	names = list(PALETTE)
	cent = np.array([PALETTE[k] for k in names], dtype=np.float32) / 255.0
	for name, o in objs.items():
		allowed = [names.index(k) for k in ALLOWED[name]]
		fc = face_cols[name]
		sub = cent[allowed]
		lab = np.array(allowed)[np.argmin(((fc[:, None, :] - sub[None]) ** 2).sum(2), axis=1)]
		lab = smooth_labels(o.data, lab, SMOOTH_PASSES)
		lab = remove_islands(o.data, lab, MIN_ISLAND, keep_small={names.index("gold"): 4})
		mesh = o.data
		attr = mesh.color_attributes.new("Col", "FLOAT_COLOR", "CORNER")
		mesh.color_attributes.active_color = attr
		lin = srgb_to_linear(cent)
		for poly, k in zip(mesh.polygons, lab):
			r, g, b = lin[k]
			for li in poly.loop_indices:
				attr.data[li].color = (r, g, b, 1.0)
		counts = {names[k]: int((lab == k).sum()) for k in set(lab.tolist())}
		print(f"paint {name}: {counts}")

	# ④ 자르기 + 관절 구슬
	pieces = {}  # 이름 → (관절, 물체)
	for name, o in objs.items():
		if name in CUTS:
			cut_joint, up_j, lo_j = CUTS[name]
			cp = Vector(JOINTS[cut_joint][0])
			par = Vector(JOINTS[JOINTS[cut_joint][1]][0])
			axis = (cp - par).normalized()  # 위 관절에서 자르는 관절 쪽
			up, low = split_by_plane(o, cp, axis)
			pieces[f"{name}_up"] = (up_j, up)
			pieces[f"{name}_low"] = (lo_j, low)
			r = 0.013 if "leg" in name else 0.011
			pieces[f"{name}_ball"] = (lo_j, make_ball(f"{name}_ball", cp, r))
		else:
			pieces[name] = (PART_JOINT[name], o)

	# ⑤ 키 맞추고 관절 원점으로 옮겨 이름 붙이기
	s = HEIGHT / (hi.z - lo.z)
	for pname, (j, o) in pieces.items():
		jp = Vector(JOINTS[j][0])
		mesh = o.data
		for v in mesh.vertices:
			v.co = ((o.matrix_world @ v.co) - jp) * s
		o.matrix_world = o.matrix_world.Identity(4)
		o.location = (jp - Vector((0, 0, lo.z))) * s
		o.name = f"{j}__{pname}"
		mesh.name = o.name
		for poly in mesh.polygons:
			poly.use_smooth = True
		mat = bpy.data.materials.get("hair" if pname in ("hair",) else ("skin" if pname == "face" else "cloth")) or bpy.data.materials.new("hair" if pname == "hair" else ("skin" if pname == "face" else "cloth"))
		mesh.materials.clear()
		mesh.materials.append(mat)

	os.makedirs(os.path.dirname(OUT_GLB), exist_ok=True)
	for o in list(bpy.context.scene.objects):
		o.select_set(o.type == "MESH")
	bpy.ops.export_scene.gltf(filepath=OUT_GLB, export_format="GLB", use_selection=True,
		export_vertex_color="ACTIVE", export_normals=True, export_apply=True)
	total = sum(len(o.data.polygons) for _, o in pieces.values())
	data = {
		"height": HEIGHT,
		"joints": {k: {"pos": list(to_godot((Vector(v[0]) - Vector((0, 0, lo.z))) * s)), "parent": v[1]} for k, v in JOINTS.items()},
		"face": {"center": [FACE_CENTER[0] * s, (FACE_CENTER[1] - JOINTS["head"][0][2]) * s], "size": FACE_SIZE * s},
		"faces_total": total,
	}
	with open(OUT_JSON, "w", encoding="utf-8") as f:
		json.dump(data, f, ensure_ascii=False, indent=1)
	print("saved", OUT_GLB, "faces", total)


def face_neighbors(mesh):
	edge_faces = {}
	for p in mesh.polygons:
		for ek in p.edge_keys:
			edge_faces.setdefault(ek, []).append(p.index)
	nbr = [set() for _ in mesh.polygons]
	for fs in edge_faces.values():
		for a in fs:
			for b in fs:
				if a != b:
					nbr[a].add(b)
	return nbr


def remove_islands(mesh, lab, min_size, keep_small=None):
	"""같은 색으로 이어진 면 묶음이 min_size(색마다 keep_small로 따로)보다 작으면 둘레에서 가장 많은 색으로 바꾼다 (부품 전체가 한 섬이면 그대로)."""
	nbr = face_neighbors(mesh)
	lab = lab.copy()
	for _ in range(3):
		seen = np.zeros(len(lab), dtype=bool)
		changed = False
		for start in range(len(lab)):
			if seen[start]:
				continue
			comp, stack = [], [start]
			seen[start] = True
			while stack:
				f = stack.pop(); comp.append(f)
				for n in nbr[f]:
					if not seen[n] and lab[n] == lab[start]:
						seen[n] = True; stack.append(n)
			need = (keep_small or {}).get(int(lab[start]), min_size)
			if len(comp) >= need or len(comp) == len(lab):
				continue
			border = [lab[n] for f in comp for n in nbr[f] if lab[n] != lab[start]]
			if border:
				vals, cnt = np.unique(border, return_counts=True)
				lab[comp] = vals[np.argmax(cnt)]
				changed = True
		if not changed:
			break
	return lab


def smooth_labels(mesh, lab, passes):
	"""면마다 이웃(모서리 공유) 면 색의 다수결. 자기 색이 이웃 중 2개 미만이면 다수 색으로 바꿈."""
	edge_faces = {}
	for p in mesh.polygons:
		for ek in p.edge_keys:
			edge_faces.setdefault(ek, []).append(p.index)
	nbr = [[] for _ in mesh.polygons]
	for fs in edge_faces.values():
		for a in fs:
			for b in fs:
				if a != b:
					nbr[a].append(b)
	lab = lab.copy()
	for _ in range(passes):
		new = lab.copy()
		for i, ns in enumerate(nbr):
			if not ns:
				continue
			vals, cnt = np.unique(lab[ns], return_counts=True)
			same = cnt[vals == lab[i]].sum() if (vals == lab[i]).any() else 0
			if same < 2:
				new[i] = vals[np.argmax(cnt)]
		lab = new
	return lab


def fit_view(v, pts, ufn, ucenter_mod, zlo, zhi):
	"""모델 정점을 그림 위에 찍은 윤곽과 그림의 전경이 가장 많이 겹치는 (배율, dx, dy)를 찾는다 (1/4 해상도)."""
	q = 4
	H, W = v["h"] // q, v["w"] // q
	fg = v["px"].min(axis=2)[::q, ::q][:H, :W] < 0.92
	u = np.array([ufn(type("P", (), {"x": float(a), "y": float(b), "z": float(c)})) for a, b, c in pts])
	z = pts[:, 2]
	base = (v["y1"] - v["y0"]) / (zhi - zlo)
	uc = (v["x0"] + v["x1"]) / 2
	best = (1.0, 0.0, 0.0, -1.0)
	offs = [(i, j) for i in range(-2, 3) for j in range(-2, 3)]
	for k in np.arange(0.94, 1.061, 0.02):
		for dx in range(-24, 25, 3):
			for dy in range(-60, 25, 3):
				x = ((uc + dx + (u - ucenter_mod) * base * k) / q).astype(int)
				y = ((v["y1"] + dy - (z - zlo) * base * k) / q).astype(int)
				m = np.zeros((H, W), dtype=bool)
				for ox, oy in offs:
					xx = np.clip(x + ox, 0, W - 1); yy = np.clip(y + oy, 0, H - 1)
					m[yy, xx] = True
				inter = (m & fg).sum(); union = (m | fg).sum()
				iou = inter / max(union, 1)
				if iou > best[3]:
					best = (float(k), float(dx), float(dy), float(iou))
	return best


def to_godot(v):
	return (round(v.x, 4), round(v.z, 4), round(-v.y, 4))


def split_by_plane(o, point, normal):
	"""면 중심이 평면 위쪽(normal 반대편)이면 up, 아니면 low 로 두 물체로 나눔."""
	mesh = o.data
	up_idx, low_idx = [], []
	for p in mesh.polygons:
		c = o.matrix_world @ p.center
		(low_idx if (c - point).dot(normal) > 0 else up_idx).append(p.index)
	up = o.copy(); up.data = mesh.copy(); bpy.context.collection.objects.link(up)
	low = o.copy(); low.data = mesh.copy(); bpy.context.collection.objects.link(low)
	for obj, keep in ((up, set(up_idx)), (low, set(low_idx))):
		bm = bmesh.new(); bm.from_mesh(obj.data)
		bm.faces.ensure_lookup_table()
		bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.index not in keep], context="FACES")
		bm.to_mesh(obj.data); bm.free()
	bpy.data.objects.remove(o)
	return up, low


def make_ball(name, center, r):
	bm = bmesh.new()
	bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=r)
	me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
	ob = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(ob)
	ob.location = center
	bpy.context.view_layer.update()
	col = srgb_to_linear(np.array(PALETTE["joint"], dtype=np.float32) / 255.0)
	attr = me.color_attributes.new("Col", "FLOAT_COLOR", "CORNER")
	me.color_attributes.active_color = attr
	for li in range(len(me.loops)):
		attr.data[li].color = (col[0], col[1], col[2], 1.0)
	return ob


main()
