"""Tripo 마네킹(부분별 생성 glb)을 게임용으로 정리 — Blender 스크립트.

실행: blender -b --python tools/char/prep_tripo_mannequin.py
입력: assets/art_src/char3d/mannequin_tripo_20261126/mq_tripo_W2_noface_parts.glb
      assets/art_src/char3d/mannequin_deform_20261126/noface/W2_{front_noface,right_noface,back}.png (색 비추기용)
출력: assets/characters/mannequin/mannequin_tripo.glb  (물체 이름 "<관절>__<부품>", 원점 = 관절)
      assets/characters/mannequin/mannequin_tripo.json (관절 위치·얼굴 자리)

순서: ① 부위 이름 붙이기 ② 면 줄이기·삼각형으로 ③ UV 펼치기 → 그림을 비춰 **텍스처 한 장에 픽셀 단위로 굽기**
      → 부위별 허용 디자인 색으로 맞추고 얼룩 정리(Family Time식 평면 색, 경계는 그림 선을 따라감)
      ④ 얼굴 그림: W2 원본(얼굴 있음)과 얼굴 지운 판의 차이 = 눈·눈썹·입 → 투명 배경 그림 (face_w2_s0.png)
      ⑤ 소매는 팔꿈치, 다리는 무릎에서 잘라 관절별 부품으로 + 관절 구슬 ⑥ 키 1.55m로 키워 내보내기
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
OUT_TEX = os.path.join(ROOT, "assets/characters/mannequin/mannequin_tripo_atlas.png")
OUT_FACE = os.path.join(ROOT, "assets/characters/mannequin/face_w2_s0.png")
TEX = 2048
FACE_TEX = 512
FILTER_PASSES = 2  # 5x5 다수결 횟수 (텍스처 얼룩 정리)
MIN_TEX_ISLAND = 1500  # 이보다 작은 색 조각(텍셀 수)은 부위의 주된 색으로
MIN_TEX_ISLAND_GOLD = 60
HEIGHT = 1.55
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
# 얼굴 그림 자리 (Blender 좌표, 정면에서 본 중심과 크기). 이 네모 안의 눈·눈썹·입을 오려 씀
FACE_CENTER = (0.0, 0.745)  # (x, z)
FACE_SIZE = 0.15


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
		bm = bmesh.new(); bm.from_mesh(o.data)
		bmesh.ops.triangulate(bm, faces=bm.faces[:])
		bm.to_mesh(o.data); bm.free()
		print(f"decimate {name}: {n} -> {len(o.data.polygons)} tris")

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

	def to_img(view, P):
		"""모델 점들(N,3) → 그 방향 그림의 (x, y) 픽셀 (실수)."""
		v, d, ufn, (umin, umax) = views[view]
		k, dx, dy, _ = v["fit"]
		scale = (v["y1"] - v["y0"]) / (hi.z - lo.z) * k
		u = {"front": P[:, 0], "back": -P[:, 0], "right": -P[:, 1], "left": -P[:, 1]}[view]
		x = (v["x0"] + v["x1"]) / 2 + dx + (u - (umin + umax) / 2) * scale
		y = v["y1"] + dy - (P[:, 2] - lo.z) * scale
		return x, y

	def sample_many(view, P):
		v = views[view][0]
		x, y = to_img(view, P)
		xi = np.clip(np.round(x).astype(int), 0, v["w"] - 1)
		yi = np.clip(np.round(y).astype(int), 0, v["h"] - 1)
		c = v["px"][yi, xi]
		ok = c.min(axis=1) < 0.97  # 흰 배경은 버림
		return c, ok

	# 면마다 쓸 방향(가림 검사): 법선과 가장 맞는 방향부터, 가려지면 다음 방향
	face_view = {}
	for name, o in objs.items():
		fv = []
		for poly in o.data.polygons:
			c = o.matrix_world @ poly.center
			n = (o.matrix_world.to_3x3() @ poly.normal).normalized()
			chosen = None
			for k in sorted(views, key=lambda k: -n.dot(views[k][1])):
				d = views[k][1]
				if n.dot(d) < -0.05:
					break
				if bvh.ray_cast(c + n * 0.0015 + d * 0.0005, d)[0] is None:
					chosen = k
					break
			fv.append(chosen)
		face_view[name] = fv
		print(f"view {name}: seen {sum(1 for x in fv if x)}/{len(fv)}")

	# ③ UV: 모든 부품을 한 번에 펼쳐 한 장(아틀라스)에. 구석 한 칸은 관절 구슬 색 자리로 비움
	bpy.ops.object.select_all(action="DESELECT")
	for o in objs.values():
		o.select_set(True)
	bpy.context.view_layer.objects.active = next(iter(objs.values()))
	bpy.ops.object.mode_set(mode="EDIT")
	bpy.ops.mesh.select_all(action="SELECT")
	bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.004)
	bpy.ops.object.mode_set(mode="OBJECT")
	for o in objs.values():
		for l in o.data.uv_layers.active.data:
			l.uv = (l.uv[0] * 0.97, l.uv[1] * 0.97)

	# 굽기: 삼각형마다 텍스처 픽셀을 채우고, 그 점을 그 면의 방향 그림에서 읽음
	names = list(PALETTE)
	cent = np.array([PALETTE[k] for k in names], dtype=np.float32) / 255.0
	tex = np.zeros((TEX, TEX, 3), dtype=np.float32)
	seen = np.zeros((TEX, TEX), dtype=bool)
	part = np.full((TEX, TEX), -1, dtype=np.int16)
	for pi, (name, o) in enumerate(objs.items()):
		mw = o.matrix_world
		vw = np.array([tuple(mw @ v.co) for v in o.data.vertices], dtype=np.float64)
		uvd = o.data.uv_layers.active.data
		loops = o.data.loops
		for poly in o.data.polygons:
			li = list(poly.loop_indices)
			uv = np.array([tuple(uvd[i].uv) for i in li]) * TEX
			P = vw[[loops[i].vertex_index for i in li]]
			xs, ys = uv[:, 0], TEX - uv[:, 1]
			x0, x1 = int(max(0, np.floor(xs.min()))), int(min(TEX - 1, np.ceil(xs.max())))
			y0, y1 = int(max(0, np.floor(ys.min()))), int(min(TEX - 1, np.ceil(ys.max())))
			if x1 < x0 or y1 < y0:
				continue
			gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
			(ax, bx, cx), (ay, by, cy) = xs, ys
			den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
			if abs(den) < 1e-12:
				continue
			w0 = ((by - cy) * (gx - cx) + (cx - bx) * (gy - cy)) / den
			w1 = ((cy - ay) * (gx - cx) + (ax - cx) * (gy - cy)) / den
			w2 = 1 - w0 - w1
			e = -0.08  # 모서리 조금 넘겨 채움 (틈 방지)
			m = (w0 >= e) & (w1 >= e) & (w2 >= e)
			if not m.any():
				continue
			W = np.stack([w0[m], w1[m], w2[m]], axis=1)
			pts = W @ P
			yy, xx = (gy[m] - 0.5).astype(int), (gx[m] - 0.5).astype(int)
			part[yy, xx] = pi
			view = face_view[name][poly.index]
			if view is None:
				continue
			c, ok = sample_many(view, pts)
			tex[yy[ok], xx[ok]] = c[ok]
			seen[yy[ok], xx[ok]] = True
		print(f"bake {name}: texels {(part == pi).sum()} seen {(seen & (part == pi)).sum()}")

	# 디자인 색으로 맞추기 (부위별 허용 색) → 5x5 다수결로 얼룩 정리
	lab = np.full((TEX, TEX), -1, dtype=np.int16)
	for pi, name in enumerate(objs):
		allowed = [names.index(k) for k in ALLOWED[name]]
		pm = part == pi
		ps = pm & seen
		if ps.any():
			sub = cent[allowed]
			d = ((tex[ps][:, None, :] - sub[None]) ** 2).sum(2)
			lab[ps] = np.array(allowed)[np.argmin(d, axis=1)]
			vals, cnt = np.unique(lab[ps], return_counts=True)
			fallback = vals[np.argmax(cnt)]
		else:
			fallback = allowed[0]
		lab[pm & ~seen] = fallback
		if name == "face":
			lab[pm] = names.index("skin")
		for _ in range(FILTER_PASSES):
			counts = np.stack([box_sum((lab == k) & pm, 2) for k in allowed])
			best = np.array(allowed)[np.argmax(counts, axis=0)]
			lab[pm] = best[pm]
		# 텍스처 안의 작은 색 조각 지우기: 부위의 주된 색이 아닌 조각이 작으면 주된 색으로 (금색은 작아도 남김)
		vals, cnt = np.unique(lab[pm], return_counts=True)
		main_col = vals[np.argmax(cnt)]
		for k in allowed:
			if k == main_col:
				continue
			mk = (lab == k) & pm
			if not mk.any():
				continue
			big = keep_big_parts(mk, MIN_TEX_ISLAND_GOLD if names[k] == "gold" else MIN_TEX_ISLAND)
			lab[mk & ~big] = main_col
		vals, cnt = np.unique(lab[pm], return_counts=True)
		print(f"paint {name}: " + ", ".join(f"{names[v]} {c}" for v, c in zip(vals, cnt)))
	img_px = np.zeros((TEX, TEX, 3), dtype=np.float32)
	filled = lab >= 0
	img_px[filled] = cent[lab[filled]]
	for _ in range(10):  # 섬 밖으로 번지게 (경계 틈 방지)
		for dy_, dx_ in ((1, 0), (-1, 0), (0, 1), (0, -1)):
			src = np.roll(np.roll(img_px, dy_, 0), dx_, 1)
			sf = np.roll(np.roll(filled, dy_, 0), dx_, 1)
			put = ~filled & sf
			img_px[put] = src[put]
			filled = filled | put
	sw = int(TEX * 0.025)
	img_px[:sw, TEX - sw:] = cent[names.index("joint")]  # 관절 구슬 색 자리 (UV 0.988 근처)
	img = bpy.data.images.new("mannequin_tripo_atlas", TEX, TEX)
	# 8비트 이미지 버퍼는 sRGB 값 그대로 저장됨 (그림에서 읽은 값도 sRGB)
	rgba = np.concatenate([img_px[::-1], np.ones((TEX, TEX, 1), np.float32)], axis=2)
	img.pixels = rgba.ravel()
	img.filepath_raw = OUT_TEX
	img.file_format = "PNG"
	img.save()
	mats = {}
	for kind in ("hair", "cloth", "skin"):
		m = bpy.data.materials.new(kind)
		m.use_nodes = True
		bsdf = m.node_tree.nodes.get("Principled BSDF")
		node = m.node_tree.nodes.new("ShaderNodeTexImage")
		node.image = img
		m.node_tree.links.new(node.outputs["Color"], bsdf.inputs["Base Color"])
		mats[kind] = m

	# ④ 얼굴 그림: 원본(얼굴 있음) - 얼굴 지운 판 = 눈·눈썹·입. 얼굴 지운 판에서 피부인 자리만 (3D 앞머리 밑으로 보이는 곳)
	make_face_texture(views, to_img)

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
		mesh.materials.clear()
		mesh.materials.append(mats["hair" if pname == "hair" else ("skin" if pname == "face" else "cloth")])

	os.makedirs(os.path.dirname(OUT_GLB), exist_ok=True)
	for o in list(bpy.context.scene.objects):
		o.select_set(o.type == "MESH")
	bpy.ops.export_scene.gltf(filepath=OUT_GLB, export_format="GLB", use_selection=True,
		export_vertex_color="NONE", export_normals=True, export_apply=True, export_image_format="AUTO")
	total = sum(len(o.data.polygons) for _, o in pieces.values())
	data = {
		"height": HEIGHT,
		"joints": {k: {"pos": list(to_godot((Vector(v[0]) - Vector((0, 0, lo.z))) * s)), "parent": v[1]} for k, v in JOINTS.items()},
		"face": {"center": [FACE_CENTER[0] * s, (FACE_CENTER[1] - JOINTS["head"][0][2]) * s], "size": FACE_SIZE * s,
			"textures": ["res://assets/characters/mannequin/face_w2_s0.png"]},
		"faces_total": total,
	}
	with open(OUT_JSON, "w", encoding="utf-8") as f:
		json.dump(data, f, ensure_ascii=False, indent=1)
	print("saved", OUT_GLB, "faces", total)


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
	uvl = me.uv_layers.new(name="UVMap")
	for l in uvl.data:
		l.uv = (0.988, 0.988)  # 아틀라스 구석의 관절 색 자리
	return ob


def box_sum(mask, r):
	"""(2r+1)x(2r+1) 창 안 True 개수."""
	a = np.pad(mask.astype(np.int32), ((r + 1, r), (r + 1, r)))
	c = a.cumsum(0).cumsum(1)
	k = 2 * r + 1
	return c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]


def keep_big_parts(mask, min_px):
	"""4방향으로 이어진 덩어리 중 min_px 이상만 남김."""
	h, w = mask.shape
	out = np.zeros_like(mask)
	seen = np.zeros_like(mask)
	ys, xs = np.nonzero(mask)
	for y0, x0 in zip(ys, xs):
		if seen[y0, x0]:
			continue
		comp, stack = [], [(y0, x0)]
		seen[y0, x0] = True
		while stack:
			y, x = stack.pop(); comp.append((y, x))
			for yy, xx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
				if 0 <= yy < h and 0 <= xx < w and mask[yy, xx] and not seen[yy, xx]:
					seen[yy, xx] = True; stack.append((yy, xx))
		if len(comp) >= min_px:
			cy, cx = zip(*comp); out[list(cy), list(cx)] = True
	return out


def make_face_texture(views, to_img):
	"""정면 그림에서 얼굴 네모를 오려 투명 배경 얼굴 그림으로. 위치·크기는 색 굽기와 같은 맞춤값."""
	full = load_view("W2_front_face.png")["px"]
	noface = views["front"][0]["px"]
	n = FACE_TEX
	gx, gz = np.meshgrid(np.linspace(-0.5, 0.5, n), np.linspace(0.5, -0.5, n))
	P = np.stack([FACE_CENTER[0] + gx * FACE_SIZE, np.zeros_like(gx), FACE_CENTER[1] + gz * FACE_SIZE], axis=-1).reshape(-1, 3)
	x, y = to_img("front", P)
	h, w = full.shape[:2]
	xi = np.clip(np.round(x).astype(int), 0, w - 1)
	yi = np.clip(np.round(y).astype(int), 0, h - 1)
	a = full[yi, xi]
	b = noface[yi, xi]
	diff = np.abs(a - b).sum(1)
	lum_b = b.mean(1)
	sat_b = b.max(1) - b.min(1)
	skin_b = (lum_b > 0.78) & (sat_b < 0.16)
	feat = ((diff > 0.18) & skin_b).reshape(n, n)
	# 가는 선 잡티(두 그림의 미세한 차이) 지우기: 한 칸 깎았다 다시 키움. 입(빨강)은 작아도 남김
	er = feat.copy()
	for dy_, dx_ in ((1, 0), (-1, 0), (0, 1), (0, -1)):
		er &= np.roll(np.roll(feat, dy_, 0), dx_, 1)
	op = er.copy()
	for dy_, dx_ in ((1, 0), (-1, 0), (0, 1), (0, -1)):
		op |= np.roll(np.roll(er, dy_, 0), dx_, 1)
	ar = a.reshape(n, n, 3)
	red = (ar[..., 0] > 0.55) & (ar[..., 1] < 0.45) & (ar[..., 0] - ar[..., 1] > 0.3) & skin_b.reshape(n, n)
	keep = keep_big_parts(feat, 150) | (keep_big_parts(red & feat, 10))
	keep[int(n * 0.85):] = False  # 턱 가장자리 자국
	alpha = keep.astype(np.float32)
	grow = alpha.copy()
	for dy_, dx_ in ((1, 0), (-1, 0), (0, 1), (0, -1)):
		grow = np.maximum(grow, np.roll(np.roll(alpha, dy_, 0), dx_, 1) * 0.6)
	rgb = a.reshape(n, n, 3)
	rgba = np.concatenate([rgb, grow[..., None]], axis=2)
	img = bpy.data.images.new("face_w2_s0", n, n, alpha=True)
	img.pixels = rgba[::-1].ravel()
	img.filepath_raw = OUT_FACE
	img.file_format = "PNG"
	img.save()
	print("face texture", OUT_FACE, "alpha px", int((alpha > 0).sum()))


main()
