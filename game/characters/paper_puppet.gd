class_name PaperPuppet
extends Node3D
## 종이인형극 빌보드 (tech-plan §5-5-5): 그림 카드 한 장 = 앞면 앞모습 · 뒷면 뒷모습.
## - 카드는 늘 나를 향해 돈다(세로축만). 캐릭터가 나를 등지면 카드가 손으로 뒤집듯 휙 돈다(가운데에서 종이 옆면이 보임).
## - 움직이면 손에 들린 인형처럼 콩콩 뛰고 살짝 기운다.
## - 상황 그림은 set_pose("이름")으로 바꾼다(카드를 접었다 펴듯 바뀜).
## 캐릭터 정면 = 이 노드의 +Z. 그림 발끝 = 이 노드 위치.

const EDGE_SHADER: Shader = preload("res://game/characters/paper_edge.gdshader")

## 그림 이름 → 텍스처. "front"(앞), "back"(뒤)는 꼭 있어야 함. 나머지는 상황 그림(앞면에 씀)
@export var poses: Dictionary = {}
## 키 (m) — 그림 세로가 이 높이가 됨
@export var height: float = 1.55
## 종이 두께 (m)
@export var thickness: float = 0.01
@export var edge_color: Color = Color(0.93, 0.9, 0.84)
## 뒤집는 데 걸리는 시간 (초)
@export var flip_time: float = 0.22
## 걸을 때 콩콩 높이 (m) · 1m에 몇 번
@export var hop_height: float = 0.045
@export var hops_per_meter: float = 2.4
## 걸을 때 좌우 기울기 (도)
@export var hop_tilt_deg: float = 4.0

var pose: String = "front"
var _pivot: Node3D
var _front: MeshInstance3D
var _back: MeshInstance3D
var _edges: Array[MeshInstance3D] = []
var _flip: float = 0.0
var _showing_back: bool = false
var _phase: float = 0.0
var _last_pos: Vector3
var _walk_blend: float = 0.0

func _ready() -> void:
	_pivot = Node3D.new()
	add_child(_pivot)
	_front = _quad(false)
	_back = _quad(true)
	for i: int in range(4):
		var e := MeshInstance3D.new()
		e.mesh = QuadMesh.new()
		var m := ShaderMaterial.new()
		m.shader = EDGE_SHADER
		m.set_shader_parameter("edge_color", edge_color)
		e.material_override = m
		e.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		_pivot.add_child(e)
		_edges.append(e)
	set_pose("front")
	_set_back_tex(poses.get("back") as Texture2D)
	_last_pos = global_position

func _quad(is_back: bool) -> MeshInstance3D:
	var q := MeshInstance3D.new()
	q.mesh = QuadMesh.new()
	var m := StandardMaterial3D.new()
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR
	m.alpha_scissor_threshold = 0.5
	m.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	m.roughness = 1.0
	m.cull_mode = BaseMaterial3D.CULL_BACK
	q.material_override = m
	if is_back:
		q.rotation.y = PI
	_pivot.add_child(q)
	return q

func _fit(q: MeshInstance3D, tex: Texture2D, z: float) -> void:
	if tex == null:
		return
	var w: float = height * float(tex.get_width()) / float(tex.get_height())
	(q.mesh as QuadMesh).size = Vector2(w, height)
	q.position = Vector3(0, height * 0.5, z)

## 상황 그림 바꾸기 (앞면). 카드를 옆으로 접었다 펴듯 바뀜
func set_pose(name: String) -> void:
	if not poses.has(name):
		return
	var first: bool = _front.material_override.albedo_texture == null
	pose = name
	if first:
		_set_front_tex(poses[name])
		return
	var tw := create_tween()
	tw.tween_property(_pivot, "scale:x", 0.0, 0.07)
	tw.tween_callback(_set_front_tex.bind(poses[name]))
	tw.tween_property(_pivot, "scale:x", 1.08, 0.08)
	tw.tween_property(_pivot, "scale:x", 1.0, 0.06)

func _set_front_tex(tex: Texture2D) -> void:
	(_front.material_override as StandardMaterial3D).albedo_texture = tex
	_fit(_front, tex, thickness * 0.5)
	for i: int in range(_edges.size()):
		var e: MeshInstance3D = _edges[i]
		(e.material_override as ShaderMaterial).set_shader_parameter("shape_tex", tex)
		_fit(e, tex, lerpf(thickness * 0.4, -thickness * 0.4, float(i) / float(_edges.size() - 1)))

func _set_back_tex(tex: Texture2D) -> void:
	(_back.material_override as StandardMaterial3D).albedo_texture = tex
	_fit(_back, tex, -thickness * 0.5)
	for e: MeshInstance3D in _edges:
		var m: ShaderMaterial = e.material_override
		m.set_shader_parameter("back_tex", tex)
		m.set_shader_parameter("use_back", tex != null)

func _process(delta: float) -> void:
	var cam: Camera3D = get_viewport().get_camera_3d()
	if cam == null:
		return
	var to_cam: Vector3 = cam.global_position - global_position
	to_cam.y = 0.0
	if to_cam.length() < 0.01:
		return
	# 앞/뒤: 캐릭터 정면(+Z)이 나를 향하나. 경계에서 덜컹이지 않게 약간의 여유
	var facing: Vector3 = global_basis.z
	facing.y = 0.0
	var d: float = facing.normalized().dot(to_cam.normalized())
	if _showing_back and d > 0.15:
		_showing_back = false
	elif not _showing_back and d < -0.15:
		_showing_back = true
	_flip = move_toward(_flip, PI if _showing_back else 0.0, PI / maxf(flip_time, 0.01) * delta)
	# 카드는 늘 나를 향함(세로축) + 뒤집기 각도
	var yaw_world: float = atan2(to_cam.x, to_cam.z)
	_pivot.global_rotation = Vector3(0.0, yaw_world + _flip, 0.0)
	# 걸으면 콩콩
	var moved: Vector3 = global_position - _last_pos
	moved.y = 0.0
	_last_pos = global_position
	var speed: float = moved.length() / maxf(delta, 0.0001)
	_walk_blend = move_toward(_walk_blend, 1.0 if speed > 0.2 else 0.0, delta * 6.0)
	_phase += moved.length() * hops_per_meter * PI
	var hop: float = absf(sin(_phase)) * hop_height * _walk_blend
	_pivot.position.y = hop
	_pivot.rotate_object_local(Vector3.FORWARD, deg_to_rad(hop_tilt_deg) * sin(_phase) * _walk_blend)
