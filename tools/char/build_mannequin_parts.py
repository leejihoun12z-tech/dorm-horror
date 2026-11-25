"""마네킹 실제 부품(로우폴리) 만들기 — Blender 스크립트.

실행: blender -b --python tools/char/build_mannequin_parts.py -- <출력.glb>
기본 출력: assets/characters/mannequin/mannequin_parts.glb

- 디자인 기준 R27_2 (docs/plan/char3d-test-01-mannequin.md): 검정 단발 + 빨간 브릿지·안쪽 빨강,
  빨간 베레모(검정 띠·금/검정 리본), 빨간 안감 검정 트렌치(어깨에 걸침·빈 소매·금 십자),
  흰 셔츠 + 깃 + 줄무늬 리본·빨간 보석, 검정 광택 하이웨이스트 치마 + 금 단추 2×3.
- "Family Time 느낌": 면이 적은 모양 + 색은 면마다 칠함(정점 색, 셰이더 외곽선과 같이 씀).
- 좌표는 모두 Godot 기준(y 위, 캐릭터 정면 = +z)으로 계산하고 Blender로 옮긴다.
- 물체 이름 = "<관절>__<부품>". 물체 원점 = 그 관절 원점 → Godot에서 그 관절 밑에 그대로 붙인다.
- 재질 이름 = 광택 종류(hair·gloss·cloth·metal). 색은 정점 색.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "assets", "characters", "mannequin", "mannequin_parts.glb")
if "--" in sys.argv and len(sys.argv) > sys.argv.index("--") + 1:
	OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1])


def srgb_to_linear(c: float) -> float:
	return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


# 블록아웃 mannequin.gd와 같은 팔레트 (sRGB)
PALETTE = {
	"hair": (0.07, 0.06, 0.08),
	"hair_red": (0.78, 0.07, 0.12),
	"red": (0.74, 0.06, 0.1),
	"red_dark": (0.45, 0.03, 0.06),
	"black": (0.06, 0.05, 0.07),
	"shirt": (0.97, 0.97, 0.99),
	"shirt_shade": (0.86, 0.86, 0.9),
	"gold": (0.78, 0.62, 0.3),
	"white": (0.95, 0.94, 0.93),
}

# 머리 타원체 (head 관절 기준): 블록아웃 _sphere(0.135, 0.29) at (0, 0.12, 0)
HEAD_C = Vector((0.0, 0.12, 0.0))
HEAD_RX = 0.135
HEAD_RY = 0.145


class Part:
	"""정점·면·면 색을 모았다가 Blender 물체 하나로 만든다."""

	def __init__(self, name: str):
		self.name = name
		self.verts: list[Vector] = []
		self.faces: list[tuple[int, ...]] = []
		self.face_col: list[str] = []
		self.face_mat: list[str] = []

	def v(self, p) -> int:
		self.verts.append(Vector(p))
		return len(self.verts) - 1

	def f(self, idx, col: str, mat: str) -> None:
		self.faces.append(tuple(idx))
		self.face_col.append(col)
		self.face_mat.append(mat)


def lathe(part: Part, profile, segs: int, col_fn, mat: str, center=(0.0, 0.0, 0.0),
		scale_z: float = 1.0, inward: bool = False, jag: float = 0.0, front_dir: float = 90.0):
	"""옆모습(profile: [(반지름, y, 앞쪽 틈 각도)])을 y축으로 돌린 껍데기.
	틈 각도가 모두 0이면 닫힌 고리, 아니면 정면(+z) 쪽이 열린 껍데기.
	jag > 0이면 맨 아래 고리를 한 칸씩 내려 끝을 들쭉날쭉하게.
	col_fn(i, j, 면 중심) -> 색 이름. 반환: 고리마다 정점 번호 목록."""
	closed = all(g <= 0.0 for (_, _, g) in profile)
	n = segs if closed else segs + 1
	rings = []
	for i, (r, y, gap) in enumerate(profile):
		ring = []
		for j in range(n):
			if closed:
				a = math.radians(front_dir) + 2.0 * math.pi * j / segs
			else:
				a0 = math.radians(front_dir + gap * 0.5)
				a1 = math.radians(front_dir + 360.0 - gap * 0.5)
				a = a0 + (a1 - a0) * j / segs
			yy = y
			if jag > 0.0 and i == len(profile) - 1 and j % 2 == 1:
				yy -= jag
			ring.append(part.v((center[0] + r * math.cos(a), center[1] + yy, center[2] + r * math.sin(a) * scale_z)))
		rings.append(ring)
	for i in range(len(rings) - 1):
		for j in range(segs):
			j1 = (j + 1) % n if closed else j + 1
			quad = [rings[i][j], rings[i][j1], rings[i + 1][j1], rings[i + 1][j]]
			if inward:
				quad.reverse()
			c = sum((part.verts[k] for k in quad), Vector()) / 4.0
			part.f(quad, col_fn(i, j, c), mat)
	return rings


def cap(part: Part, ring, center, col: str, mat: str, down: bool):
	"""고리를 부채꼴로 막는다. down = 아래를 보는 면."""
	ci = part.v(center)
	n = len(ring)
	for j in range(n):
		a, b = ring[j], ring[(j + 1) % n]
		part.f((ci, a, b) if down else (ci, b, a), col, mat)


def box(part: Part, center, size, col: str, mat: str, rot_z: float = 0.0, rot_x: float = 0.0):
	cx, cy, cz = center
	sx, sy, sz = size[0] * 0.5, size[1] * 0.5, size[2] * 0.5
	idx = []
	for dx, dy, dz in [(-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)]:
		p = Vector((dx * sx, dy * sy, dz * sz))
		p = Vector((p.x, p.y * math.cos(rot_x) - p.z * math.sin(rot_x), p.y * math.sin(rot_x) + p.z * math.cos(rot_x)))
		p = Vector((p.x * math.cos(rot_z) - p.y * math.sin(rot_z), p.x * math.sin(rot_z) + p.y * math.cos(rot_z), p.z))
		idx.append(part.v((cx + p.x, cy + p.y, cz + p.z)))
	for q in [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (2, 3, 7, 6), (1, 2, 6, 5), (0, 4, 7, 3)]:
		part.f([idx[k] for k in q], col, mat)


def octa(part: Part, center, r: float, col: str, mat: str, squash_z: float = 0.6):
	cx, cy, cz = center
	p = [part.v((cx + r, cy, cz)), part.v((cx - r, cy, cz)), part.v((cx, cy + r, cz)),
		part.v((cx, cy - r, cz)), part.v((cx, cy, cz + r * squash_z)), part.v((cx, cy, cz - r * squash_z))]
	for a, b, c in [(0, 2, 4), (2, 1, 4), (1, 3, 4), (3, 0, 4), (2, 0, 5), (1, 2, 5), (3, 1, 5), (0, 3, 5)]:
		part.f((p[a], p[b], p[c]), col, mat)


def head_point(phi_deg: float, off: float):
	"""머리 타원체 위 위도(꼭대기 0°)의 (반지름, y)를 off만큼 띄워서."""
	phi = math.radians(phi_deg)
	return (HEAD_RX + off) * math.sin(phi), HEAD_C.y + (HEAD_RY + off) * math.cos(phi)


# ---------- 가발 (head 관절) ----------
def build_wig() -> Part:
	p = Part("head__wig")
	off = 0.018
	# 빨간 브릿지 = 캐릭터 왼쪽(+x, 보는 사람 오른쪽) 앞, 안쪽 빨강 = 캐릭터 오른쪽(-x) 아래
	def bridge(c: Vector) -> bool:
		a = math.degrees(math.atan2(c.z, c.x))
		return 28.0 <= a <= 52.0 and c.z > 0.0

	def hair_col(i, j, c):
		if bridge(c):
			return "hair_red"
		if c.x < -0.04 and c.y < 0.075:
			return "hair_red"
		return "hair"

	# 정수리: 닫힌 고리
	crown_prof = [(*head_point(phi, off), 0.0) for phi in (8, 26, 44)]
	crown = lathe(p, crown_prof, 14, hair_col, "hair")
	cap(p, crown[0], (0.0, HEAD_C.y + HEAD_RY + off + 0.004, 0.0), "hair", "hair", down=False)
	# 옆·뒤 껍데기: 정면 100° 열림, 귀 높이 아래로는 곧게 떨어지며 살짝 벌어짐, 끝 들쭉날쭉
	shell_prof = [(*head_point(44, off), 100.0), (*head_point(66, off + 0.004), 100.0),
		(*head_point(88, off + 0.008), 100.0), (0.162, 0.07, 100.0), (0.168, 0.025, 104.0), (0.17, -0.012, 108.0)]
	lathe(p, shell_prof, 14, hair_col, "hair", jag=0.026)
	# 껍데기 안쪽(앞에서 보이는 안쪽 면): 같은 모양을 조금 안으로, 뒤집어서
	inner_prof = [(r - 0.006, y, g) for (r, y, g) in shell_prof[2:]]
	lathe(p, inner_prof, 14, lambda i, j, c: "hair_red" if c.x < -0.04 else "hair", "hair", inward=True, jag=0.026)
	# 앞머리: 정면 140° 부채, 이마를 따라 내려와 눈썹 위(y ≈ 0.155)에서 끝, 끝 들쭉날쭉
	bang_off = off + 0.006
	bang_prof = [(*head_point(40, bang_off), 0.0), (*head_point(58, bang_off), 0.0), (*head_point(72, bang_off - 0.006), 0.0)]
	# 부채는 lathe의 열린 껍데기를 뒤집어 쓴다: 틈 220° = 앞쪽 140°만 남음 → 뒤쪽 중심으로 열리게 front_dir=270
	bang_prof = [(r, y, 220.0) for (r, y, _) in bang_prof]
	lathe(p, bang_prof, 10, lambda i, j, c: "hair_red" if bridge(c) else "hair", "hair", jag=0.014, front_dir=270.0)
	return p


# ---------- 베레모 (head 관절) ----------
def build_beret() -> Part:
	p = Part("head__beret")
	prof = [(0.03, 0.052, 0.0), (0.1, 0.046, 0.0), (0.148, 0.028, 0.0), (0.152, 0.012, 0.0),
		(0.132, 0.0, 0.0), (0.124, -0.004, 0.0), (0.124, -0.012, 0.0), (0.118, -0.012, 0.0)]
	rings = lathe(p, prof, 14, lambda i, j, c: "black" if i >= 5 else ("red_dark" if i == 4 else "red"), "cloth")
	cap(p, rings[0], (0.0, 0.056, 0.0), "red", "cloth", down=False)
	cap(p, rings[-1], (0.0, -0.008, 0.0), "black", "cloth", down=True)
	# 리본: 보는 사람 왼쪽(-x) 앞 — 검정 리본 날개 2 + 금 장식
	for s in (-1.0, 1.0):
		box(p, (-0.105 + s * 0.022, -0.012, 0.075), (0.038, 0.026, 0.012), "black", "cloth", rot_z=s * 0.35)
		box(p, (-0.105 + s * 0.016, 0.0, 0.088), (0.022, 0.018, 0.008), "gold", "metal", rot_z=s * 0.5)
	octa(p, (-0.105, -0.006, 0.092), 0.012, "gold", "metal")
	# 베레모 전체를 기울여 머리 위에: 블록아웃과 같은 자리·기울기
	tilt_z, tilt_x = -0.3, 0.05
	for k, v in enumerate(p.verts):
		x, y, z = v
		y, z = y * math.cos(tilt_x) - z * math.sin(tilt_x), y * math.sin(tilt_x) + z * math.cos(tilt_x)
		x, y = x * math.cos(tilt_z) - y * math.sin(tilt_z), x * math.sin(tilt_z) + y * math.cos(tilt_z)
		p.verts[k] = Vector((x + 0.035, y + 0.288, z - 0.03))
	return p


# ---------- 셔츠 상체 (chest 관절) ----------
def build_shirt() -> Part:
	p = Part("chest__shirt")
	prof = [(0.07, 0.245, 0.0), (0.122, 0.225, 0.0), (0.128, 0.19, 0.0), (0.124, 0.14, 0.0),
		(0.12, 0.09, 0.0), (0.1, 0.03, 0.0), (0.092, -0.02, 0.0)]
	rings = lathe(p, prof, 14, lambda i, j, c: "shirt_shade" if c.z < -0.06 else "shirt", "cloth", scale_z=0.82)
	cap(p, rings[0], (0.0, 0.25, 0.0), "shirt", "cloth", down=False)
	# 가슴: 정면 두 곳을 앞으로 부드럽게 밀어냄
	for k, v in enumerate(p.verts):
		if v.z <= 0.0:
			continue
		bump = 0.0
		for sx in (-0.05, 0.05):
			bump = max(bump, math.exp(-((v.x - sx) / 0.045) ** 2) * math.exp(-((v.y - 0.12) / 0.04) ** 2))
		p.verts[k] = Vector((v.x, v.y, v.z + 0.034 * bump))
	# 깃: 목 앞 두 장
	for s in (-1.0, 1.0):
		a = p.v((s * 0.012, 0.25, 0.062))
		b = p.v((s * 0.07, 0.245, 0.04))
		c = p.v((s * 0.03, 0.205, 0.114))
		p.f((a, c, b) if s > 0 else (a, b, c), "shirt", "cloth")
		p.f((a, b, c) if s > 0 else (a, c, b), "shirt_shade", "cloth")
	return p


# ---------- 줄무늬 리본 + 빨간 보석 (neck 관절) ----------
def build_bow() -> Part:
	p = Part("neck__bow")
	y0, z0 = -0.045, 0.114
	for s in (-1.0, 1.0):
		# 날개: 가운데에서 바깥으로 벌어지는 사다리꼴 판, 줄무늬 = 세 칸
		for k, col in enumerate(("black", "red", "black")):
			x0 = s * (0.01 + k * 0.016)
			x1 = s * (0.01 + (k + 1) * 0.016)
			h0 = 0.012 + k * 0.006
			h1 = 0.012 + (k + 1) * 0.006
			a = p.v((x0, y0 + h0, z0))
			b = p.v((x1, y0 + h1, z0 - 0.006))
			c = p.v((x1, y0 - h1, z0 - 0.006))
			d = p.v((x0, y0 - h0, z0))
			p.f((a, d, c, b) if s > 0 else (a, b, c, d), col, "cloth")
			p.f((a, b, c, d) if s > 0 else (a, d, c, b), "black", "cloth")
		# 꼬리: 아래로 늘어진 두 줄
		box(p, (s * 0.018, y0 - 0.05, z0 + 0.008), (0.02, 0.07, 0.006), "black", "cloth", rot_z=s * 0.25, rot_x=-0.25)
		box(p, (s * 0.018, y0 - 0.05, z0 + 0.012), (0.007, 0.07, 0.006), "red", "cloth", rot_z=s * 0.25, rot_x=-0.25)
	octa(p, (0.0, y0, z0 + 0.006), 0.02, "gold", "metal")
	octa(p, (0.0, y0, z0 + 0.012), 0.013, "red", "gloss")
	return p


# ---------- 하이웨이스트 치마 + 금 단추 (hips 관절) ----------
def build_skirt() -> Part:
	p = Part("hips__skirt")
	sz = 0.86
	prof = [(0.09, 0.285, 0.0), (0.096, 0.22, 0.0), (0.118, 0.14, 0.0), (0.15, 0.05, 0.0),
		(0.158, -0.02, 0.0), (0.152, -0.11, 0.0), (0.142, -0.19, 0.0)]
	rings = lathe(p, prof, 14, lambda i, j, c: "black", "gloss", scale_z=sz)
	cap(p, rings[0], (0.0, 0.285, 0.0), "black", "gloss", down=False)
	inner = [(r - 0.006, y, 0.0) for (r, y, _) in prof[-3:]]
	lathe(p, inner, 14, lambda i, j, c: "black", "gloss", scale_z=sz, inward=True)
	# 금 단추 2줄 × 3개: 치마 앞면 위
	for k, y in enumerate((0.235, 0.18, 0.125)):
		r = 0.096 + (0.118 - 0.096) * (0.22 - y) / 0.08 if y < 0.22 else 0.093
		for s in (-1.0, 1.0):
			x = s * 0.034
			z = math.sqrt(max(r * r - x * x, 0.0)) * sz + 0.004
			octa(p, (x, y, z), 0.011, "gold", "metal", squash_z=0.5)
	return p


# ---------- 트렌치코트 (chest 관절): 어깨에 걸침, 앞 열림, 빈 소매 ----------
def build_coat() -> Part:
	p = Part("chest__coat")
	sz = 0.86
	prof = [(0.078, 0.262, 64.0), (0.185, 0.25, 80.0), (0.228, 0.215, 96.0), (0.245, 0.12, 110.0),
		(0.28, -0.1, 116.0), (0.31, -0.33, 118.0), (0.335, -0.56, 120.0)]
	outer = lathe(p, prof, 18, lambda i, j, c: "black", "gloss", scale_z=sz)
	inner_prof = [(r - 0.008, y, g) for (r, y, g) in prof]
	inner = lathe(p, inner_prof, 18, lambda i, j, c: "red" if i >= 1 else "black", "cloth", scale_z=sz, inward=True)
	# 두께: 아랫단과 앞 가장자리 두 줄을 이어 막음
	last = len(prof) - 1
	for j in range(18):
		a, b = outer[last][j], outer[last][j + 1]
		c, d = inner[last][j + 1], inner[last][j]
		p.f((a, b, c, d), "black", "gloss")
	for i in range(last):
		for j, flip in ((0, True), (18, False)):
			q = [outer[i][j], inner[i][j], inner[i + 1][j], outer[i + 1][j]]
			p.f(tuple(reversed(q)) if flip else tuple(q), "black", "gloss")
	# 빈 소매: 어깨에서 바깥 아래로 늘어진 관, 소맷부리 안쪽 빨강
	for s in (-1.0, 1.0):
		top = Vector((s * 0.23, 0.19, -0.03))
		bot = Vector((s * 0.33, -0.3, -0.04))
		segs = 8
		rings = []
		for t, r in ((0.0, 0.048), (0.5, 0.054), (1.0, 0.06)):
			cc = top.lerp(bot, t)
			ring = []
			for j in range(segs):
				a = 2.0 * math.pi * j / segs
				ring.append(p.v((cc.x + r * math.cos(a), cc.y, cc.z + r * math.sin(a))))
			rings.append(ring)
		for i in range(len(rings) - 1):
			for j in range(segs):
				q = [rings[i][j], rings[i][(j + 1) % segs], rings[i + 1][(j + 1) % segs], rings[i + 1][j]]
				p.f(tuple(q), "black", "gloss")
		cap(p, rings[-1], tuple(bot + Vector((0.0, 0.01, 0.0))), "red_dark", "cloth", down=True)
		# 금 십자: 보는 사람 왼쪽(-x) 소매 바깥
		if s < 0.0:
			cx = top.lerp(bot, 0.45)
			box(p, (cx.x - 0.062, cx.y, cx.z), (0.008, 0.05, 0.016), "gold", "metal")
			box(p, (cx.x - 0.062, cx.y + 0.006, cx.z), (0.008, 0.016, 0.04), "gold", "metal")
	# 어깨 견장 금 단추
	for s in (-1.0, 1.0):
		octa(p, (s * 0.2, 0.222, 0.06), 0.012, "gold", "metal")
	return p


# ---------- Blender 물체로 만들기 ----------
def g2b(v: Vector) -> Vector:
	"""Godot(y 위) → Blender(z 위). glTF 내보내기가 다시 y 위로 돌려 준다."""
	return Vector((v.x, -v.z, v.y))


MATS = {}


def material(name: str):
	if name not in MATS:
		m = bpy.data.materials.new(name)
		m.use_nodes = True
		MATS[name] = m
	return MATS[name]


def make_object(part: Part):
	mesh = bpy.data.meshes.new(part.name)
	mesh.from_pydata([g2b(v) for v in part.verts], [], part.faces)
	mesh.update()
	names = sorted(set(part.face_mat))
	obj = bpy.data.objects.new(part.name, mesh)
	bpy.context.collection.objects.link(obj)
	for n in names:
		obj.data.materials.append(material(n))
	for poly, mn in zip(mesh.polygons, part.face_mat):
		poly.material_index = names.index(mn)
	attr = mesh.color_attributes.new("Col", "FLOAT_COLOR", "CORNER")
	mesh.color_attributes.active_color = attr
	for poly, cn in zip(mesh.polygons, part.face_col):
		r, g, b = (srgb_to_linear(c) for c in PALETTE[cn])
		for li in poly.loop_indices:
			attr.data[li].color = (r, g, b, 1.0)
	for poly in mesh.polygons:
		poly.use_smooth = True
	return obj


def main():
	bpy.ops.wm.read_factory_settings(use_empty=True)
	parts = [build_wig(), build_beret(), build_shirt(), build_bow(), build_skirt(), build_coat()]
	for part in parts:
		obj = make_object(part)
		print("part", part.name, "verts", len(part.verts), "faces", len(part.faces))
	os.makedirs(os.path.dirname(OUT), exist_ok=True)
	bpy.ops.export_scene.gltf(filepath=OUT, export_format="GLB", export_vertex_color="ACTIVE",
		export_all_vertex_colors=False, export_normals=True, export_apply=True)
	print("saved", OUT)


main()
