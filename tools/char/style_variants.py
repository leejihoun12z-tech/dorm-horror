"""칠 방식 비교용 변형 만들기 (Blender). 같은 모양으로 '색 칠하는 법'만 바꿔 본다.

실행: blender -b --python tools/char/style_variants.py -- <입력.glb> <출력.glb> <pal|flat>
  pal : 부위마다 텍스처 색을 몇 개(k)로 묶어 그 색으로만 칠함(경계는 AI가 칠한 선을 따라감, 번짐·붓질 없앰)
  flat: 부위마다 한 색(코트는 바깥 검정·안쪽 빨강을 면 방향으로) — 무늬 없음, 가장 깔끔
입력은 merge_inner_pass.py 결과(outer_*/inner_* 물체).
"""
import sys

import bpy
import numpy as np
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
SRC, OUT, MODE = argv[0], argv[1], argv[2]
# 부위마다 색 개수 (pal)
K = {"hair": 3, "beret": 3, "coat": 3, "l_sleeve": 3, "r_sleeve": 3, "collar": 4, "shirt": 2, "waist": 2,
	"skirt": 2, "l_leg": 2, "r_leg": 2, "l_hand": 2, "r_hand": 2, "l_shoe": 2, "r_shoe": 2}


def part_of(name):
	return name.split(".")[0].replace("inner_", "").replace("outer_", "")


def base_nodes(o):
	for mat in o.data.materials:
		if mat and mat.node_tree:
			for n in mat.node_tree.nodes:
				if n.type == "TEX_IMAGE" and n.image and any(l.to_socket.name == "Base Color" for l in mat.node_tree.links if l.from_node == n):
					yield mat, n


def uv_mask(o, w, h):
	mask = np.zeros((h, w), dtype=bool)
	uvl = o.data.uv_layers.active
	uv = np.zeros(len(o.data.loops) * 2, dtype=np.float32)
	uvl.data.foreach_get("uv", uv)
	uv = uv.reshape(-1, 2)
	for p in o.data.polygons:
		li = list(p.loop_indices)
		for k in range(1, len(li) - 1):
			t = uv[[li[0], li[k], li[k + 1]]]
			xs, ys = t[:, 0] * w, t[:, 1] * h
			x0, x1 = max(0, int(xs.min()) - 1), min(w - 1, int(xs.max()) + 1)
			y0, y1 = max(0, int(ys.min()) - 1), min(h - 1, int(ys.max()) + 1)
			if x1 < x0 or y1 < y0:
				continue
			gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
			(ax, bx, cx), (ay, by, cy) = xs, ys
			den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
			if abs(den) < 1e-12:
				continue
			a = ((by - cy) * (gx - cx) + (cx - bx) * (gy - cy)) / den
			b = ((cy - ay) * (gx - cx) + (ax - cx) * (gy - cy)) / den
			mask[y0:y1 + 1, x0:x1 + 1] |= (a >= -0.02) & (b >= -0.02) & (1 - a - b >= -0.02)
	return mask


def kmeans(X, k, iters=20):
	rng = np.random.default_rng(0)
	C = X[rng.choice(len(X), k, replace=False)]
	for _ in range(iters):
		d = ((X[:, None, :] - C[None]) ** 2).sum(2)
		lab = d.argmin(1)
		for j in range(k):
			if (lab == j).any():
				C[j] = X[lab == j].mean(0)
	return C


def box_sum(m, r):
	a = np.pad(m.astype(np.int32), ((r + 1, r), (r + 1, r)))
	c = a.cumsum(0).cumsum(1)
	k = 2 * r + 1
	return c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]


def palette_image(img, mask, k):
	w, h = img.size
	px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)[..., :3]
	X = px[mask]
	samp = X[np.random.default_rng(1).choice(len(X), min(len(X), 40000), replace=False)]
	C = kmeans(samp, k + 1)
	# 너무 비슷한 색(그림자 단계 등)은 합침
	keep = []
	for c in C:
		if all(np.abs(c - q).sum() > 0.16 for q in keep):
			keep.append(c)
	C = np.array(keep)
	lab = np.full((h, w), -1, dtype=np.int16)
	d = ((px[mask][:, None, :] - C[None]) ** 2).sum(2)
	lab[mask] = d.argmin(1)
	for _ in range(2):  # 5x5 다수결로 얼룩·붓질 정리
		counts = np.stack([box_sum((lab == j) & mask, 2) for j in range(len(C))])
		best = counts.argmax(0)
		lab[mask] = best[mask]
	out = np.zeros((h, w, 3), np.float32)
	out[mask] = C[lab[mask]]
	return out, mask, C


def push_pull(col, mask):
	levels = [(col * mask[..., None], mask.astype(np.float32))]
	while min(levels[-1][1].shape) > 1:
		c, wg = levels[-1]
		hh, ww = (wg.shape[0] // 2) * 2, (wg.shape[1] // 2) * 2
		c = c[:hh, :ww]; wg = wg[:hh, :ww]
		levels.append((c[0::2, 0::2] + c[1::2, 0::2] + c[0::2, 1::2] + c[1::2, 1::2],
			wg[0::2, 0::2] + wg[1::2, 0::2] + wg[0::2, 1::2] + wg[1::2, 1::2]))
	c, wg = levels[-1]
	cur = c / np.maximum(wg, 1e-6)[..., None]
	for c, wg in reversed(levels[:-1]):
		up = np.repeat(np.repeat(cur, 2, 0), 2, 1)
		up = np.pad(up, ((0, max(0, wg.shape[0] - up.shape[0])), (0, max(0, wg.shape[1] - up.shape[1])), (0, 0)), mode="edge")[:wg.shape[0], :wg.shape[1]]
		cur = np.where((wg > 0)[..., None], c / np.maximum(wg, 1e-6)[..., None], up)
	out = col.copy(); out[~mask] = cur[~mask]
	return out


def set_image(node, rgb, name):
	h, w = rgb.shape[:2]
	img = bpy.data.images.new(name, w, h)
	img.pixels.foreach_set(np.dstack([rgb, np.ones((h, w, 1), np.float32)]).ravel())
	img.pack()
	node.image = img


def flat_parts(objs):
	"""부위마다 한 색. 색 = 그 부위 텍스처에서 가장 넓은 색(pal과 같은 묶기). 코트는 안쪽 면만 두 번째 색."""
	centers = {}
	for o in objs:
		ws = [v.co for v in o.data.vertices]
		centers[o.name] = sum(ws, Vector()) / len(ws)
	axis_x = 0.0
	ys = [v.co.y for o in objs for v in o.data.vertices]
	axis_y = (min(ys) + max(ys)) / 2
	for o in objs:
		p = part_of(o.name)
		for mat, node in list(base_nodes(o)):
			img = node.image
			w, h = img.size
			if w < 16:
				continue
			mask = uv_mask(o, w, h)
			_, _, C = palette_image(img, mask, K.get(p, 2))
			px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)[..., :3][mask]
			lab = ((px[:, None, :] - C[None]) ** 2).sum(2).argmin(1)
			order = np.argsort(-np.bincount(lab, minlength=len(C)))
			main = C[order[0]]
			second = C[order[1]] if len(order) > 1 else main
			# 2칸 텍스처: 왼쪽 = 주색, 오른쪽 = 두 번째 색(코트 안감)
			set_image(node, np.array([[main, second]], np.float32), f"flat_{o.name}")
			uvl = o.data.uv_layers.active
			for poly in o.data.polygons:
				u = 0.25
				if p == "coat":
					c = poly.center
					out_dir = Vector((c.x - axis_x, c.y - axis_y, 0))
					if out_dir.length > 1e-6 and poly.normal.dot(out_dir.normalized()) < -0.2:
						u = 0.75
				for li in poly.loop_indices:
					uvl.data[li].uv = (u, 0.5)
			print("flat", o.name, np.round(main * 255).astype(int), np.round(second * 255).astype(int))


def main():
	bpy.ops.wm.read_factory_settings(use_empty=True)
	bpy.ops.import_scene.gltf(filepath=SRC)
	objs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
	if MODE == "pal":
		for o in objs:
			p = part_of(o.name)
			if p == "face":
				continue
			for mat, node in list(base_nodes(o)):
				w, h = node.image.size
				if w < 16:
					continue
				mask = uv_mask(o, w, h)
				out, mask, C = palette_image(node.image, mask, K.get(p, 2))
				set_image(node, push_pull(out, mask), f"pal_{o.name}")
				print("pal", o.name, len(C), "colors", np.round(C * 255).astype(int).tolist())
	elif MODE == "flat":
		flat_parts([o for o in objs if part_of(o.name) != "face"])
	for o in bpy.data.objects:
		o.select_set(o.type == "MESH")
	bpy.ops.export_scene.gltf(filepath=OUT, export_format="GLB", use_selection=True, export_normals=True, export_image_format="AUTO")
	print("saved", OUT)


main()
