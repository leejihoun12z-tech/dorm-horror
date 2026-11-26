class_name Mannequin
extends Node3D
## 시험 캐릭터: 마네킹(뷰티디자인학과 1학년). 디자인 기준 = 아트 채팅 R27_2(사용자 2026-11-25):
## 검정 단발 + 빨간 브릿지 · 빨간 베레모 · 빨간 안감 검정 트렌치 · 흰 셔츠 + 줄무늬 리본 · 검정 하이웨이스트 치마 · 흰 구체관절.
## 부품(구체관절)으로 조립한 로우폴리 + 그린 얼굴 텍스처. 부품마다 관절 하나에 고정 → 리깅 깨짐 없음.
## 변이 0~3단계(상한 3): 얼굴 그림 바꾸기 + 부품 옮기기. 1단계부터 "안 볼 때 자세가 바뀜".

signal pose_changed(count: int)

const FACE_TEXTURES: Array[String] = [
	"res://assets/characters/mannequin/face_s0.png",
	"res://assets/characters/mannequin/face_s1.png",
	"res://assets/characters/mannequin/face_s2.png",
	"res://assets/characters/mannequin/face_s3.png",
]
## Tripo 3D 모델(W2, 얼굴 없는 판)을 관절별 부품으로 자른 것. 만드는 도구 tools/char/prep_tripo_mannequin.py
## 물체 이름 "<관절>__<부품>", 관절 위치는 json. 색 = 정점 색, 얼굴 = 셰이더가 얼굴 그림을 덮음
const TRIPO_SCENE: String = "res://assets/characters/mannequin/mannequin_tripo.glb"
const TRIPO_JSON: String = "res://assets/characters/mannequin/mannequin_tripo.json"
## [폐기·대체] Blender 스크립트 도형 부품 (비교용으로만 남김). 만드는 도구 tools/char/build_mannequin_parts.py
const PARTS_SCENE: String = "res://assets/characters/mannequin/mannequin_parts.glb"
## 부품 광택 종류(glb 재질 이름) → (거칠기, 반사)
const PART_FINISH: Dictionary = {"hair": Vector2(0.3, 0.8), "gloss": Vector2(0.2, 0.9), "cloth": Vector2(0.7, 0.3), "metal": Vector2(0.3, 0.9)}
const SEGMENTS: int = 12
const RINGS: int = 6

@export var stage: int = 0
@export var unseen_seconds: float = 1.2
@export var step_toward_watcher: float = 0.0
## Tripo 모델 사용 (끄면 아래 블록아웃)
@export var use_tripo_model: bool = true
## 블록아웃일 때: 끄면 예전 도형 옷·머리 (비교용)
@export var use_model_parts: bool = true
var watcher: Camera3D = null

var joints: Dictionary = {}
var _base_rot: Dictionary = {}
var _base_pos: Dictionary = {}
## 3단계에서 머리를 뒤집을 때 올려 주는 높이 (머리 관절 위로 머리 끝까지)
var _head_height: float = 0.36
var _face_mat: ShaderMaterial
## 단계별 얼굴 그림 (Tripo 모델이면 json의 얼굴 그림으로 바꿈)
var _face_textures: Array[String] = FACE_TEXTURES.duplicate()
var _unseen_time: float = 0.0
var _was_seen: bool = true
var pose_change_count: int = 0
var _rng := RandomNumberGenerator.new()

var _shader: Shader = preload("res://game/characters/char_toon.gdshader")

func _ready() -> void:
	_rng.seed = 7
	if use_tripo_model and ResourceLoader.exists(TRIPO_SCENE) and FileAccess.file_exists(TRIPO_JSON):
		_build_tripo()
	else:
		_build()
	set_stage(stage)

func _mat(color: Color, rough: float, spec: float) -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.shader = _shader
	m.set_shader_parameter("base_color", color)
	m.set_shader_parameter("roughness_value", rough)
	m.set_shader_parameter("specular_value", spec)
	var outline := StandardMaterial3D.new()
	outline.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	outline.cull_mode = BaseMaterial3D.CULL_FRONT
	outline.albedo_color = Color(0.08, 0.05, 0.07)
	outline.grow = true
	outline.grow_amount = 0.0035
	m.next_pass = outline
	return m

func _joint(parent: Node3D, key: String, pos: Vector3) -> Node3D:
	var j := Node3D.new()
	j.name = key
	j.position = pos
	parent.add_child(j)
	joints[key] = j
	return j

func _part(parent: Node3D, mesh: Mesh, mat: Material, pos: Vector3, scl: Vector3 = Vector3.ONE, rot: Vector3 = Vector3.ZERO) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	mi.mesh = mesh
	mi.material_override = mat
	mi.position = pos
	mi.scale = scl
	mi.rotation = rot
	parent.add_child(mi)
	return mi

func _sphere(r: float, h: float = -1.0) -> SphereMesh:
	var s := SphereMesh.new()
	s.radius = r
	s.height = r * 2.0 if h < 0.0 else h
	s.radial_segments = SEGMENTS
	s.rings = RINGS
	return s

func _capsule(r: float, h: float) -> CapsuleMesh:
	var c := CapsuleMesh.new()
	c.radius = r
	c.height = h
	c.radial_segments = SEGMENTS
	c.rings = 2
	return c

func _cyl(top: float, bottom: float, h: float) -> CylinderMesh:
	var c := CylinderMesh.new()
	c.top_radius = top
	c.bottom_radius = bottom
	c.height = h
	c.radial_segments = SEGMENTS
	c.rings = 1
	return c

## 앞이 열린 원뿔 껍데기(코트). 바깥(법선 밖)과 안(법선 안)을 따로 만든다.
func _open_cone(top_r: float, bottom_r: float, h: float, gap_deg: float, inner: bool) -> ArrayMesh:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var segs: int = SEGMENTS
	var a0: float = deg_to_rad(90.0 + gap_deg * 0.5)
	var a1: float = deg_to_rad(90.0 + 360.0 - gap_deg * 0.5)
	var k: float = 0.96 if inner else 1.0
	for i: int in range(segs):
		var t0: float = lerpf(a0, a1, float(i) / segs)
		var t1: float = lerpf(a0, a1, float(i + 1) / segs)
		var p0 := Vector3(cos(t0) * top_r * k, h * 0.5, sin(t0) * top_r * k)
		var p1 := Vector3(cos(t1) * top_r * k, h * 0.5, sin(t1) * top_r * k)
		var p2 := Vector3(cos(t0) * bottom_r * k, -h * 0.5, sin(t0) * bottom_r * k)
		var p3 := Vector3(cos(t1) * bottom_r * k, -h * 0.5, sin(t1) * bottom_r * k)
		if inner:
			for v: Vector3 in [p0, p1, p2, p1, p3, p2]:
				st.add_vertex(v)
		else:
			for v: Vector3 in [p0, p2, p1, p1, p2, p3]:
				st.add_vertex(v)
	st.generate_normals()
	return st.commit()

func _box(size: Vector3) -> BoxMesh:
	var b := BoxMesh.new()
	b.size = size
	return b

func _build() -> void:
	var plastic := _mat(Color(0.95, 0.94, 0.93), 0.25, 0.8)
	var metal := _mat(Color(0.3, 0.3, 0.34), 0.3, 0.9)
	var black := _mat(Color(0.06, 0.05, 0.07), 0.22, 0.9)
	var red := _mat(Color(0.74, 0.06, 0.1), 0.35, 0.6)
	var shirt := _mat(Color(0.97, 0.97, 0.99), 0.7, 0.3)
	var gold := _mat(Color(0.78, 0.62, 0.3), 0.3, 0.9)
	var hair := _mat(Color(0.07, 0.06, 0.08), 0.3, 0.8)
	hair.set_shader_parameter("use_tip", true)
	hair.set_shader_parameter("tip_color", Color(0.78, 0.07, 0.12))
	var brush_wood := _mat(Color(0.1, 0.08, 0.09), 0.3, 0.6)
	var brush_tip := _mat(Color(0.95, 0.85, 0.82), 0.8, 0.2)

	var model: bool = use_model_parts and ResourceLoader.exists(PARTS_SCENE)
	var hips := _joint(self, "hips", Vector3(0, 0.66, 0))
	_part(hips, _sphere(0.12, 0.17), plastic, Vector3(0, 0.03, 0), Vector3(1.05, 1.0, 0.85))
	var spine := _joint(hips, "spine", Vector3(0, 0.12, 0))
	var chest := _joint(spine, "chest", Vector3(0, 0.17, 0))
	# 흰 셔츠 상체 + 검정 하이웨이스트 치마(금 단추) — 실제 부품이 있으면 그쪽을 씀
	if not model:
		_part(chest, _cyl(0.122, 0.092, 0.24), shirt, Vector3(0, 0.1, 0), Vector3(1.0, 1.0, 0.82))
		for side: float in [-1.0, 1.0]:
			_part(chest, _sphere(0.046), shirt, Vector3(side * 0.048, 0.115, 0.05))
		_part(spine, _cyl(0.094, 0.11, 0.2), black, Vector3(0, 0.06, 0), Vector3(1.0, 1.0, 0.86))
		_part(hips, _cyl(0.112, 0.17, 0.26), black, Vector3(0, -0.04, 0))
		for k: int in range(3):
			for side: float in [-1.0, 1.0]:
				_part(spine, _sphere(0.011), gold, Vector3(side * 0.035, 0.0 + k * 0.05, 0.088))
	# 깃·줄무늬 리본·빨간 보석
	var neck := _joint(chest, "neck", Vector3(0, 0.24, 0))
	_part(neck, _cyl(0.05, 0.06, 0.05), shirt, Vector3(0, -0.02, 0))
	if not model:
		_part(neck, _box(Vector3(0.09, 0.035, 0.02)), black, Vector3(0, -0.04, 0.055))
		_part(neck, _box(Vector3(0.03, 0.09, 0.018)), black, Vector3(0.008, -0.09, 0.06), Vector3.ONE, Vector3(0, 0, 0.15))
		_part(neck, _box(Vector3(0.012, 0.09, 0.02)), red, Vector3(0.008, -0.09, 0.062), Vector3.ONE, Vector3(0, 0, 0.15))
		_part(neck, _sphere(0.016), red, Vector3(0, -0.04, 0.068))
	_part(neck, _sphere(0.04), metal, Vector3(0, 0.0, 0))
	_part(neck, _cyl(0.034, 0.036, 0.09), plastic, Vector3(0, 0.05, 0))
	# 머리: 그린 얼굴
	var head := _joint(neck, "head", Vector3(0, 0.1, 0))
	_face_mat = _mat(Color(0.95, 0.94, 0.93), 0.25, 0.7)
	_face_mat.set_shader_parameter("use_face", true)
	_face_mat.set_shader_parameter("face_center", Vector2(0.0, 0.0))
	_face_mat.set_shader_parameter("face_size", Vector2(0.2, 0.2))
	_part(head, _sphere(0.135, 0.29), _face_mat, Vector3(0, 0.12, 0))
	if not model:
		# 검정 단발 + 빨간 끝·브릿지
		var back_hair := _part(head, _sphere(0.152, 0.3), hair, Vector3(0, 0.15, -0.03))
		(back_hair.material_override as ShaderMaterial).set_shader_parameter("tip_y", -0.1)
		_part(head, _sphere(0.138, 0.09), _mat(Color(0.07, 0.06, 0.08), 0.3, 0.8), Vector3(0, 0.215, 0.06), Vector3(1.0, 1.0, 0.62))
		_part(head, _capsule(0.011, 0.15), red, Vector3(0.085, 0.13, 0.1), Vector3.ONE, Vector3(0.25, 0, 0.18))
		for side: float in [-1.0, 1.0]:
			var sm := _mat(Color(0.07, 0.06, 0.08), 0.3, 0.8)
			sm.set_shader_parameter("use_tip", true)
			sm.set_shader_parameter("tip_color", Color(0.78, 0.07, 0.12))
			sm.set_shader_parameter("tip_y", -0.085)
			_part(head, _capsule(0.05, 0.25), sm, Vector3(side * 0.125, 0.09, 0.0), Vector3(0.8, 1.0, 1.0), Vector3(0, 0, side * 0.14))
		# 빨간 베레모(오른쪽으로 기울임) + 금 장식
		_part(head, _sphere(0.125, 0.06), red, Vector3(0.035, 0.3, -0.03), Vector3(1.0, 1.0, 1.0), Vector3(0.05, 0, -0.3))
		_part(head, _box(Vector3(0.03, 0.03, 0.01)), gold, Vector3(-0.08, 0.26, 0.09), Vector3.ONE, Vector3(0, 0, 0.7))
		# 트렌치코트: 어깨에 걸침, 앞이 열림, 바깥 검정·안 빨강 + 금 십자 장식
		var coat_out := _part(chest, _open_cone(0.17, 0.3, 0.78, 80.0, false), black, Vector3(0, -0.17, -0.01))
		coat_out.material_override = black
		_part(chest, _open_cone(0.17, 0.3, 0.78, 80.0, true), red, Vector3(0, -0.17, -0.01))
		for side: float in [-1.0, 1.0]:
			_part(chest, _box(Vector3(0.035, 0.012, 0.012)), gold, Vector3(side * 0.19, -0.05, 0.08))
			_part(chest, _box(Vector3(0.012, 0.035, 0.012)), gold, Vector3(side * 0.19, -0.05, 0.08))
	# 팔
	for side: float in [-1.0, 1.0]:
		var key: String = "l" if side < 0.0 else "r"
		var sh := _joint(chest, key + "_shoulder", Vector3(side * 0.155, 0.19, 0))
		sh.rotation.z = side * 0.22
		_part(sh, _sphere(0.045), metal, Vector3.ZERO)
		_part(sh, _capsule(0.034, 0.26), plastic, Vector3(0, -0.13, 0))
		var el := _joint(sh, key + "_elbow", Vector3(0, -0.26, 0))
		_part(el, _sphere(0.036), metal, Vector3.ZERO)
		_part(el, _capsule(0.03, 0.23), plastic, Vector3(0, -0.115, 0))
		var wr := _joint(el, key + "_wrist", Vector3(0, -0.23, 0))
		_part(wr, _sphere(0.026), metal, Vector3.ZERO)
		_part(wr, _sphere(0.045), plastic, Vector3(0, -0.05, 0), Vector3(0.7, 1.15, 0.45))
		if side > 0.0:
			_part(wr, _cyl(0.007, 0.009, 0.2), brush_wood, Vector3(0, -0.06, 0.03), Vector3.ONE, Vector3(1.2, 0, 0))
			_part(wr, _sphere(0.02, 0.06), brush_tip, Vector3(0, -0.0, 0.12), Vector3.ONE, Vector3(1.2, 0, 0))
	# 다리: 흰 플라스틱 + 금속 무릎 + 검정 구두
	for side: float in [-1.0, 1.0]:
		var key: String = "l" if side < 0.0 else "r"
		var hp := _joint(hips, key + "_hip", Vector3(side * 0.075, -0.02, 0))
		_part(hp, _sphere(0.055), metal, Vector3.ZERO)
		_part(hp, _capsule(0.052, 0.31), plastic, Vector3(0, -0.15, 0))
		var kn := _joint(hp, key + "_knee", Vector3(0, -0.3, 0))
		_part(kn, _sphere(0.045), metal, Vector3.ZERO)
		_part(kn, _capsule(0.04, 0.3), plastic, Vector3(0, -0.145, 0))
		var an := _joint(kn, key + "_ankle", Vector3(0, -0.29, 0))
		_part(an, _sphere(0.032), metal, Vector3.ZERO)
		_part(an, _sphere(0.05, 0.07), black, Vector3(0, -0.035, 0.04), Vector3(0.85, 1.0, 1.7))
	if model:
		_attach_model_parts()
	_store_rest()

## glb 안 물체 "<관절>__<부품>"을 그 관절 밑에 붙인다. 색 = 정점 색, 광택 = 재질 이름.
func _attach_model_parts() -> void:
	var inst: Node = (load(PARTS_SCENE) as PackedScene).instantiate()
	var finish_mats: Dictionary = {}
	for node: Node in inst.find_children("*", "MeshInstance3D", true, false):
		var src: MeshInstance3D = node
		var key: String = String(src.name).get_slice("__", 0)
		if not joints.has(key):
			push_warning("마네킹 부품 관절 없음: %s" % src.name)
			continue
		var part := MeshInstance3D.new()
		part.name = src.name
		part.mesh = src.mesh
		part.transform = src.transform
		for s: int in range(src.mesh.get_surface_count()):
			var m: Material = src.mesh.surface_get_material(s)
			var kind: String = m.resource_name if m != null and PART_FINISH.has(m.resource_name) else "cloth"
			if not finish_mats.has(kind):
				var f: Vector2 = PART_FINISH[kind]
				var mat := _mat(Color.WHITE, f.x, f.y)
				mat.set_shader_parameter("use_vcol", true)
				finish_mats[kind] = mat
			part.set_surface_override_material(s, finish_mats[kind])
		(joints[key] as Node3D).add_child(part)
	inst.free()

func _store_rest() -> void:
	for k: String in joints.keys():
		_base_rot[k] = (joints[k] as Node3D).rotation
		_base_pos[k] = (joints[k] as Node3D).position

## Tripo 모델: json의 관절 위치로 관절을 세우고, glb의 부품을 이름대로 붙인다
func _build_tripo() -> void:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(TRIPO_JSON))
	var jd: Dictionary = data["joints"]
	var world_pos: Dictionary = {}
	for key: String in jd.keys():
		var p: Array = jd[key]["pos"]
		world_pos[key] = Vector3(p[0], p[1], p[2])
	# 부모가 먼저 만들어지도록 json 순서(부모 → 자식)대로
	for key: String in jd.keys():
		var parent_key = jd[key]["parent"]
		var parent: Node3D = self if parent_key == null else joints[parent_key]
		var parent_pos: Vector3 = Vector3.ZERO if parent_key == null else world_pos[parent_key]
		_joint(parent, key, world_pos[key] - parent_pos)
	var face: Dictionary = data["face"]
	# 무광 (Family Time식 평면 색): 반사 0
	_face_mat = _mat(Color.WHITE, 1.0, 0.0)
	_face_mat.set_shader_parameter("use_face", true)
	_face_mat.set_shader_parameter("face_center", Vector2(face["center"][0], face["center"][1]))
	_face_mat.set_shader_parameter("face_size", Vector2(face["size"], face["size"]))
	# 0단계 = W2 원본에서 오린 얼굴. 1단계도 우선 같은 그림, 2·3단계는 아직 예전 임시 그림 [작업값]
	if face.has("textures"):
		var w2: String = face["textures"][0]
		_face_textures = [w2, w2, FACE_TEXTURES[2], FACE_TEXTURES[3]]
	var finish_mats: Dictionary = {}
	var inst: Node = (load(TRIPO_SCENE) as PackedScene).instantiate()
	var head_top: float = 0.0
	for node: Node in inst.find_children("*", "MeshInstance3D", true, false):
		var src: MeshInstance3D = node
		var key: String = String(src.name).get_slice("__", 0)
		var part_name: String = String(src.name).get_slice("__", 1)
		if not joints.has(key):
			push_warning("마네킹 부품 관절 없음: %s" % src.name)
			continue
		var part := MeshInstance3D.new()
		part.name = src.name
		part.mesh = src.mesh
		for s: int in range(src.mesh.get_surface_count()):
			# 색 = glb에 든 텍스처 (Tripo가 칠한 것). 텍스처마다 무광 툰 재질 하나
			var m: Material = src.mesh.surface_get_material(s)
			var tex: Texture2D = (m as BaseMaterial3D).albedo_texture if m is BaseMaterial3D else null
			if part_name == "face":
				_face_mat.set_shader_parameter("use_tex", tex != null)
				_face_mat.set_shader_parameter("albedo_tex", tex)
				part.set_surface_override_material(s, _face_mat)
				continue
			var key_tex: String = str(tex.get_instance_id()) if tex != null else "none"
			if not finish_mats.has(key_tex):
				var mat := _mat(Color.WHITE, 1.0, 0.0)
				mat.set_shader_parameter("use_tex", tex != null)
				mat.set_shader_parameter("albedo_tex", tex)
				finish_mats[key_tex] = mat
			part.set_surface_override_material(s, finish_mats[key_tex])
		(joints[key] as Node3D).add_child(part)
		if key == "head":
			head_top = maxf(head_top, src.mesh.get_aabb().end.y)
	inst.free()
	if head_top > 0.0:
		_head_height = head_top
	_store_rest()

func set_stage(s: int) -> void:
	stage = clampi(s, 0, 3)
	_face_mat.set_shader_parameter("face_tex", load(_face_textures[stage]))
	_reset_pose()
	if stage >= 2:
		(joints["head"] as Node3D).rotation.z = deg_to_rad(24.0)
		(joints["neck"] as Node3D).rotation.x = deg_to_rad(-8.0)
	if stage >= 3:
		var head: Node3D = joints["head"]
		head.rotation = Vector3(0, 0, PI)
		head.position = _base_pos["head"] + Vector3(0, _head_height, 0)
		var el: Node3D = joints["l_elbow"]
		el.rotation = Vector3(deg_to_rad(-70), 0, deg_to_rad(40))
		(joints["r_knee"] as Node3D).rotation.x = deg_to_rad(-45)
		(joints["r_shoulder"] as Node3D).rotation = Vector3(deg_to_rad(-160), 0, deg_to_rad(10))

func _reset_pose() -> void:
	for k: String in joints.keys():
		(joints[k] as Node3D).rotation = _base_rot[k]
		(joints[k] as Node3D).position = _base_pos[k]

func is_seen_by(cam: Camera3D) -> bool:
	var head: Node3D = joints["head"]
	var p: Vector3 = head.global_position
	if not cam.is_position_in_frustum(p):
		return false
	var space: PhysicsDirectSpaceState3D = get_world_3d().direct_space_state
	var q := PhysicsRayQueryParameters3D.create(cam.global_position, p)
	return space.intersect_ray(q).is_empty()

func _process(delta: float) -> void:
	if watcher == null or stage < 1:
		return
	var seen: bool = is_seen_by(watcher)
	if seen:
		_unseen_time = 0.0
		_was_seen = true
		return
	_unseen_time += delta
	if _was_seen and _unseen_time >= unseen_seconds:
		_was_seen = false
		_shift_pose()

## 안 볼 때 자세가 조금 바뀜 (1단계부터). 다가오기는 step_toward_watcher > 0일 때만.
func _shift_pose() -> void:
	var head: Node3D = joints["head"]
	head.rotation.y = _rng.randf_range(-0.35, 0.35)
	head.rotation.z += _rng.randf_range(-0.15, 0.15)
	for key: String in ["l_shoulder", "r_shoulder"]:
		var j: Node3D = joints[key]
		j.rotation.x = _rng.randf_range(-0.5, 0.1)
	if step_toward_watcher > 0.0 and watcher != null:
		var to: Vector3 = watcher.global_position - global_position
		to.y = 0.0
		if to.length() > 1.2:
			global_position += to.normalized() * step_toward_watcher
			look_at(Vector3(watcher.global_position.x, global_position.y, watcher.global_position.z), Vector3.UP, true)
	pose_change_count += 1
	pose_changed.emit(pose_change_count)
