"""Charakuru 키트: 웨이트 전송이 끝난 weighted.blend에 머리카락·모자를 다시 붙이고 흔들림 뼈·웨이트를 만든다.

실행: blender -b <weighted.blend> --python tools/char/charakuru_springs.py -- <assembly.blend> <출력 blend> <출력 spring-config.json>
그 뒤 키트의 scripts/spring-setup.py setup 으로 VRM 스프링 등록·검사.
- 머리카락: 앞머리는 머리에 고정, 옆·뒤 5갈래를 2마디씩 흔들림.
- 모자·리본: 머리에 고정.
- 코트: 윗부분은 몸 웨이트를 옮겨 받고, 허리 아래를 6갈래 x 3마디로 흔들림.
"""
import json
import math
import sys

import addon_utils
import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
ASSEMBLY, OUT_BLEND, OUT_CFG = args[0], args[1], args[2]

for m in addon_utils.modules():
	if m.bl_info.get("name") == "VRM format":
		bpy.ops.preferences.addon_enable(module=m.__name__)

rig = next(o for o in bpy.data.objects if o.type == "ARMATURE" and o.name.startswith("CharaKit_Weights") and o.name.endswith("_Rig"))
keep = {rig.name, "Body", "Head", "Spring_02_coat"}
for o in list(bpy.data.objects):
	if o.name not in keep:
		bpy.data.objects.remove(o, do_unlink=True)
rig.name = "Rig"
body, head, coat = bpy.data.objects["Body"], bpy.data.objects["Head"], bpy.data.objects["Spring_02_coat"]
scene = bpy.context.scene
for o in (rig, body, head, coat):
	if o.name not in scene.collection.all_objects:
		scene.collection.objects.link(o)
	o.hide_set(False)
	o.hide_render = False


def bbox(o):
	ws = [o.matrix_world @ v.co for v in o.data.vertices]
	return Vector(map(min, *ws)), Vector(map(max, *ws))


# --- 1. 머리카락·모자 다시 붙이기 (조립본의 머리와 같은 변환)
with bpy.data.libraries.load(ASSEMBLY) as (src, dst):
	dst.objects = [n for n in src.objects if n in ("Head", "Spring_01_hair", "Hair")]
a_head = next(o for o in dst.objects if o.name.startswith("Head"))
a_hair = next(o for o in dst.objects if o.name.startswith("Spring_01_hair"))
a_hat = next(o for o in dst.objects if o.name.startswith("Hair"))
for o in (a_head, a_hair, a_hat):
	scene.collection.objects.link(o)
bpy.context.view_layer.update()
alo, ahi = bbox(a_head)
hlo, hhi = bbox(head)
s = (hhi.x - hlo.x) / (ahi.x - alo.x)
sz = (hhi.z - hlo.z) / (ahi.z - alo.z)
assert abs(s - sz) / s < 0.02, (s, sz)
off = (hlo + hhi) / 2 - (alo + ahi) / 2 * s
for o in (a_hair, a_hat):
	mw = o.matrix_world.copy()
	for v in o.data.vertices:
		v.co = (mw @ v.co) * s + off
	o.parent = None
	o.matrix_world.identity()
	o.parent = rig
	o.matrix_parent_inverse = rig.matrix_world.inverted()
	o.modifiers.clear()
	mod = o.modifiers.new("Armature", "ARMATURE")
	mod.object = rig
bpy.data.objects.remove(a_head, do_unlink=True)


def plain_material(o):
	"""덧붙인 MToon 재질은 켜짐 표시가 풀려 있어 키트 변환이 거부한다 → 같은 텍스처의 기본 재질로 바꿔 키트가 다시 MToon으로 만들게 한다."""
	old = o.material_slots[0].material
	img = next(n.image for n in old.node_tree.nodes if n.type == "TEX_IMAGE" and n.image and "basecolor" in n.image.name.lower())
	mat = bpy.data.materials.new(old.name + "_src")
	mat.use_nodes = True
	bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
	tex = mat.node_tree.nodes.new("ShaderNodeTexImage")
	tex.image = img
	mat.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
	mat.use_backface_culling = False
	o.data.materials.clear()
	o.data.materials.append(mat)


plain_material(a_hair)
plain_material(a_hat)
a_hair.name = "HairMesh"
a_hat.name = "Hat"
a_hair["charakitRole"] = "hair"
a_hat["charakitRole"] = "hair"
hair, hat = a_hair, a_hat
hat.vertex_groups.clear()
hat.vertex_groups.new(name="head").add(range(len(hat.data.vertices)), 1.0, "REPLACE")
bpy.context.view_layer.update()

# --- 2. 코트 윗부분: 몸 웨이트를 옮겨 받기
coat.vertex_groups.clear()
dt = coat.modifiers.new("dt", "DATA_TRANSFER")
dt.object = body
dt.use_vert_data = True
dt.data_types_verts = {"VGROUP_WEIGHTS"}
dt.vert_mapping = "POLYINTERP_NEAREST"
dt.layers_vgroup_select_src = "ALL"
dt.layers_vgroup_select_dst = "NAME"
for o in bpy.data.objects:
	o.select_set(False)
coat.select_set(True)
bpy.context.view_layer.objects.active = coat
bpy.ops.object.datalayout_transfer(modifier="dt")
while coat.modifiers[0].name != "dt":
	bpy.ops.object.modifier_move_up(modifier="dt")
bpy.ops.object.modifier_apply(modifier="dt")
TORSO = {"hips", "spine", "chest", "upperChest", "neck", "shoulder.L", "shoulder.R", "upper_arm.L", "upper_arm.R"}
for g in list(coat.vertex_groups):
	if g.name not in TORSO:
		coat.vertex_groups.remove(g)

# --- 3. 흔들림 뼈 만들기
bones = rig.data.bones
hl, hh = bbox(hair)
hc = Vector(((hlo.x + hhi.x) / 2, (hlo.y + hhi.y) / 2, 0))
h_zr = hl.z + 0.50 * (hh.z - hl.z)
HAIR = [("hair_side_L", 80), ("hair_back_L", 135), ("hair_back", 180), ("hair_back_R", -135), ("hair_side_R", -80)]
HAIR_FIXED = [0, 40, -40]  # 앞머리는 고정
cl, ch = bbox(coat)
c_zw = (rig.matrix_world @ bones["hips"].head_local).z + 0.02
cc = Vector((0, (cl.y + ch.y) / 2, 0))
COAT = [("coat_front_L", 40), ("coat_side_L", 100), ("coat_back_L", 155), ("coat_back_R", -155), ("coat_side_R", -100), ("coat_front_R", -40)]


def ang(p, c):
	return math.degrees(math.atan2(p.x - c.x, -(p.y - c.y)))  # 정면 0 · 본인 왼쪽 +


def adiff(a, b):
	return abs((a - b + 180) % 360 - 180)


def sector_pts(o, c, deg, width, zlo, zhi):
	out = []
	for v in o.data.vertices:
		p = o.matrix_world @ v.co
		if zlo <= p.z <= zhi and adiff(ang(p, c), deg) <= width:
			out.append(p)
	return out


def radial(pts, c):
	rs = sorted(math.hypot(p.x - c.x, p.y - c.y) for p in pts)
	return rs[len(rs) // 2]


def chain_points(o, c, deg, z_top, z_bot, n):
	d = Vector((math.sin(math.radians(deg)), -math.cos(math.radians(deg)), 0))
	pts = []
	for i in range(n + 1):
		z = z_top + (z_bot - z_top) * i / n
		band = sector_pts(o, c, deg, 35, z - 0.03, z + 0.03) or sector_pts(o, c, deg, 60, z - 0.06, z + 0.06)
		if band:
			r = radial(band, c)
		elif pts:
			r = math.hypot(pts[-1].x - c.x, pts[-1].y - c.y)
		else:
			r = 0.05
		pts.append(Vector((c.x + d.x * r, c.y + d.y * r, z)))
	return pts


plans = []
for name, deg in HAIR:
	low = sector_pts(hair, hc, deg, 35, hl.z, h_zr)
	zb = min(p.z for p in low) if low else hl.z
	plans.append((name, "head", chain_points(hair, hc, deg, h_zr, zb, 2)))
for name, deg in COAT:
	plans.append((name, "hips", chain_points(coat, cc, deg, c_zw, cl.z, 3)))

for o in bpy.data.objects:
	o.select_set(False)
rig.select_set(True)
bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode="EDIT")
inv = rig.matrix_world.inverted()
chain_bones = {}
for name, parent, pts in plans:
	prev = rig.data.edit_bones[parent]
	names = []
	for i in range(len(pts) - 1):
		b = rig.data.edit_bones.new(f"{name}_{i + 1}")
		b.head = inv @ pts[i]
		b.tail = inv @ pts[i + 1]
		b.parent = prev
		b.use_connect = i > 0
		b.use_deform = True
		prev = b
		names.append(b.name)
	chain_bones[name] = names
bpy.ops.object.mode_set(mode="OBJECT")


def smooth(t):
	t = max(0.0, min(1.0, t))
	return t * t * (3 - 2 * t)


def set_weights(o, row_fn):
	rows = {}
	for v in o.data.vertices:
		rows[v.index] = row_fn(v, o.matrix_world @ v.co)
	o.vertex_groups.clear()
	groups = {}
	for i, row in rows.items():
		tot = sum(row.values())
		for n, w in row.items():
			if w / tot > 1e-4:
				if n not in groups:
					groups[n] = o.vertex_groups.new(name=n)
				groups[n].add([i], w / tot, "REPLACE")


def hair_row(v, p):
	a = ang(p, hc)
	shares = {n: max(0.0, 1 - adiff(a, d) / 50) for n, d in HAIR}
	fixed = sum(max(0.0, 1 - adiff(a, d) / 50) for d in HAIR_FIXED)
	tot = sum(shares.values()) + fixed
	if tot <= 0:
		return {"head": 1.0}
	t = (h_zr - p.z) / max(1e-6, h_zr - hl.z)
	sp = smooth(t * 1.6)
	u = max(0.0, min(1.0, (t - 0.35) / 0.5))
	row = {"head": (1 - sp) + sp * fixed / tot + 1e-6}
	for n, w in shares.items():
		if w > 0:
			b1, b2 = chain_bones[n]
			row[b1] = row.get(b1, 0) + sp * w / tot * (1 - u)
			row[b2] = row.get(b2, 0) + sp * w / tot * u
	return row


set_weights(hair, hair_row)

existing = {v.index: {coat.vertex_groups[g.group].name: g.weight for g in v.groups} for v in coat.data.vertices}


def coat_row(v, p):
	base = {n: w for n, w in existing[v.index].items() if w > 0} or {"hips": 1.0}
	bt = sum(base.values())
	base = {n: w / bt for n, w in base.items()}
	t = (c_zw - p.z) / max(1e-6, c_zw - cl.z)
	if t <= 0:
		return base
	a = ang(p, cc)
	shares = {n: max(0.0, 1 - adiff(a, d) / 65) for n, d in COAT}
	tot = sum(shares.values())
	if tot <= 0:
		return base
	sp = smooth(t * 2.0)
	row = {n: w * (1 - sp) + 1e-6 for n, w in base.items()}
	k = [max(0.0, 1 - abs(t - c) / 0.4) for c in (0.15, 0.5, 0.9)]
	ks = sum(k) or 1.0
	for n, w in shares.items():
		if w > 0:
			for bn, kw in zip(chain_bones[n], k):
				row[bn] = row.get(bn, 0) + sp * w / tot * kw / ks
	return row


set_weights(coat, coat_row)

# --- 4. VRM 1.0 휴머노이드
ext = rig.data.vrm_addon_extension
ext.spec_version = "1.0"
bpy.ops.vrm.assign_vrm1_humanoid_human_bones_automatically(armature_object_name=rig.name)
hb = ext.vrm1.humanoid.human_bones.human_bone_name_to_human_bone()
print("HUMANOID", len([1 for v in hb.values() if v.node.bone_name]))

cfg = {"armature": "Rig", "chains": [], "targets": []}
for name, deg in HAIR:
	cfg["chains"].append({"name": name, "bones": chain_bones[name], "stiffness": 1.2, "gravityPower": 0.1, "dragForce": 0.5, "hitRadius": 0.01, "colliderGroups": []})
for name, deg in COAT:
	cfg["chains"].append({"name": name, "bones": chain_bones[name], "stiffness": 2.2, "gravityPower": 0.03, "dragForce": 0.5, "hitRadius": 0.015, "colliderGroups": []})
cfg["targets"] = [
	{"mesh": "HairMesh", "source": "hair", "mode": "spring", "chains": [n for n, _ in HAIR]},
	{"mesh": "Hat", "source": "hair", "mode": "fixed", "reason": "베레모·띠·리본은 단단한 장식이라 머리에 고정 (눈으로 확인)"},
	{"mesh": "Spring_02_coat", "source": "Spring_02_coat", "mode": "spring", "chains": [n for n, _ in COAT]},
]
with open(OUT_CFG, "w", encoding="utf-8") as f:
	f.write(json.dumps(cfg, ensure_ascii=False, indent=1))
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
print("SAVED", OUT_BLEND, {n: len(b) for n, b in chain_bones.items()})
