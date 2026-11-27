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
## 짧은 음성 음높이 (캐릭터마다 다르게. 1.0 = 원래 소리)
@export var voice_pitch: float = 1.0

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
var _bubble: Sprite3D
var _bubble_label: Label
var _bubble_view: SubViewport
var _bubble_tween: Tween
var _voice: AudioStreamPlayer3D

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
	_build_bubble()
	_voice = AudioStreamPlayer3D.new()
	_voice.position = Vector3(0, height * 0.85, 0)
	add_child(_voice)

## 말풍선 한 줄 + 짧은 음성(있으면). 평소 대화용 — 긴 대화는 대화 화면에서
func say(text: String, voice: AudioStream = null, seconds: float = 2.5) -> void:
	_bubble_label.text = text
	_bubble_view.size = Vector2i(maxi(160, int(_bubble_label.get_minimum_size().x) + 48), 112)
	_bubble_view.render_target_update_mode = SubViewport.UPDATE_ONCE
	_bubble.visible = true
	_bubble.scale = Vector3.ONE * 0.2
	if _bubble_tween != null:
		_bubble_tween.kill()
	_bubble_tween = create_tween()
	_bubble_tween.tween_property(_bubble, "scale", Vector3.ONE * 1.08, 0.09)
	_bubble_tween.tween_property(_bubble, "scale", Vector3.ONE, 0.06)
	_bubble_tween.tween_interval(seconds)
	_bubble_tween.tween_property(_bubble, "scale", Vector3.ZERO, 0.08)
	_bubble_tween.tween_callback(func() -> void: _bubble.visible = false)
	if voice != null:
		_voice.stream = voice
		_voice.pitch_scale = voice_pitch * randf_range(0.97, 1.03)
		_voice.play()

func _build_bubble() -> void:
	_bubble_view = SubViewport.new()
	_bubble_view.transparent_bg = true
	_bubble_view.size = Vector2i(320, 112)
	_bubble_view.render_target_update_mode = SubViewport.UPDATE_ONCE
	add_child(_bubble_view)
	var root_c := Control.new()
	root_c.set_anchors_preset(Control.PRESET_FULL_RECT)
	_bubble_view.add_child(root_c)
	var box := PanelContainer.new()
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.99, 0.98, 0.95)
	sb.border_color = Color(0.08, 0.07, 0.08)
	sb.set_border_width_all(4)
	sb.set_corner_radius_all(26)
	sb.content_margin_left = 20
	sb.content_margin_right = 20
	sb.content_margin_top = 10
	sb.content_margin_bottom = 10
	box.add_theme_stylebox_override("panel", sb)
	box.set_anchors_preset(Control.PRESET_TOP_WIDE)
	box.offset_bottom = 82
	root_c.add_child(box)
	_bubble_label = Label.new()
	_bubble_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_bubble_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	var font := SystemFont.new()
	font.font_names = PackedStringArray(["Malgun Gothic", "Noto Sans CJK KR", "Noto Sans KR", "Apple SD Gothic Neo", "Unifont"])
	_bubble_label.add_theme_font_override("font", font)
	_bubble_label.add_theme_font_size_override("font_size", 34)
	_bubble_label.add_theme_color_override("font_color", Color(0.08, 0.07, 0.08))
	box.add_child(_bubble_label)
	# 꼬리: 테두리 삼각형 위에 흰 삼각형
	var tail_b := Polygon2D.new()
	tail_b.polygon = PackedVector2Array([Vector2(-18, 76), Vector2(18, 76), Vector2(0, 108)])
	tail_b.color = Color(0.08, 0.07, 0.08)
	var tail_w := Polygon2D.new()
	tail_w.polygon = PackedVector2Array([Vector2(-12, 72), Vector2(12, 72), Vector2(0, 99)])
	tail_w.color = Color(0.99, 0.98, 0.95)
	var tail := Node2D.new()
	tail.add_child(tail_b)
	tail.add_child(tail_w)
	root_c.add_child(tail)
	root_c.resized.connect(func() -> void: tail.position.x = root_c.size.x * 0.5)
	_bubble = Sprite3D.new()
	_bubble.texture = _bubble_view.get_texture()
	_bubble.pixel_size = 0.003
	_bubble.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	_bubble.shaded = false
	_bubble.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
	_bubble.centered = true
	_bubble.offset = Vector2(0, 56)
	_bubble.position = Vector3(0, height + 0.12, 0)
	_bubble.visible = false
	add_child(_bubble)

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
