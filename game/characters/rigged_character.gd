class_name RiggedCharacter
extends Node3D
## Tripo에서 색·뼈대·동작까지 만든 캐릭터(glb)를 그대로 쓰는 공용 노드.
## 만드는 순서는 docs/plan/char3d-pipeline.md. 모양·색은 여기서 고치지 않는다(빛만 평평하게).

const FLAT_SHADER: Shader = preload("res://game/characters/char_flat.gdshader")

## 모델 파일 (키 1.0 기준으로 나옴)
@export_file("*.glb") var model_path: String = ""
## 키 (m)
@export var height: float = 1.55
## 면 방향에 따른 명암 세기 (0 = 완전히 평평, 1 = 보통 툰)
@export_range(0.0, 1.0) var shade_amount: float = 0.0
## 시작할 때 틀 동작 이름 (비우면 안 틂)
@export var start_animation: String = ""

var model: Node3D
var anim: AnimationPlayer
var _materials: Array[ShaderMaterial] = []

func _ready() -> void:
	if model_path != "":
		load_model(model_path)

func load_model(path: String) -> void:
	if model != null:
		model.queue_free()
		_materials.clear()
	model = (load(path) as PackedScene).instantiate()
	add_child(model)
	model.scale = Vector3.ONE * height
	_restyle(model)
	anim = _find_anim(model)
	if anim != null:
		for name: StringName in anim.get_animation_list():
			_make_in_place(anim.get_animation(name))
		if start_animation != "" and anim.has_animation(start_animation):
			anim.play(start_animation)

## 동작 틀기 (없으면 false)
func play(animation_name: String) -> bool:
	if anim == null or not anim.has_animation(animation_name):
		return false
	anim.play(animation_name)
	return true

## 텍스처 통째로 바꾸기 (표정 단계: 얼굴 자리만 다른 텍스처를 넣을 때)
func set_texture(tex: Texture2D) -> void:
	for m: ShaderMaterial in _materials:
		m.set_shader_parameter("albedo_tex", tex)

func _restyle(n: Node) -> void:
	if n is MeshInstance3D:
		var mi: MeshInstance3D = n
		for s: int in range(mi.mesh.get_surface_count()):
			var src: Material = mi.mesh.surface_get_material(s)
			var tex: Texture2D = (src as BaseMaterial3D).albedo_texture if src is BaseMaterial3D else null
			var m := ShaderMaterial.new()
			m.shader = FLAT_SHADER
			m.set_shader_parameter("base_color", Color.WHITE)
			m.set_shader_parameter("roughness_value", 1.0)
			m.set_shader_parameter("specular_value", 0.0)
			m.set_shader_parameter("use_tex", tex != null)
			m.set_shader_parameter("albedo_tex", tex)
			m.set_shader_parameter("nl_amount", shade_amount)
			mi.set_surface_override_material(s, m)
			_materials.append(m)
	for c: Node in n.get_children():
		_restyle(c)

func _find_anim(n: Node) -> AnimationPlayer:
	if n is AnimationPlayer:
		return n
	for c: Node in n.get_children():
		var r: AnimationPlayer = _find_anim(c)
		if r != null:
			return r
	return null

## 걷기 등은 제자리 동작으로: 엉덩이 뼈의 이동 트랙을 뺀다 (이동은 게임 코드가 한다)
func _make_in_place(a: Animation) -> void:
	a.loop_mode = Animation.LOOP_LINEAR
	for t: int in range(a.get_track_count() - 1, -1, -1):
		if a.track_get_type(t) == Animation.TYPE_POSITION_3D and String(a.track_get_path(t)).to_lower().contains("hips"):
			a.remove_track(t)
