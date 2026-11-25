class_name CharacterView
extends Node3D
## 기숙생 한 명을 3D로 보여 주는 층 (tech-plan §3 "캐릭터 보여 주기 층").
## 표정 = 얼굴 그림 바꾸기 (tech-plan §5-4). 대역 몸이든 실제 로우폴리 모델이든 같은 방식.

signal expression_changed(expression: StringName)

const TOON_SHADER: Shader = preload("res://game/characters/toon_lit.gdshader")

## 얼굴 그림이 붙은 메시 (실제 모델에서는 얼굴 판 또는 머리 메시)
@export var face_mesh: MeshInstance3D
## 그 메시에서 얼굴 그림이 들어간 재질 칸 번호
@export var face_surface: int = 0
## 표정 이름 → 얼굴 그림
@export var expressions: Dictionary[StringName, Texture2D] = {}
@export var default_expression: StringName = &"neutral"

var current_expression: StringName = &""
var _face_material: ShaderMaterial

func _ready() -> void:
	if face_mesh != null:
		_face_material = _ensure_toon_material(face_mesh, face_surface)
	if expressions.has(default_expression):
		set_expression(default_expression)

func set_expression(expression: StringName) -> void:
	if not expressions.has(expression) or _face_material == null:
		push_warning("표정 없음: %s" % expression)
		return
	_face_material.set_shader_parameter("albedo_tex", expressions[expression])
	current_expression = expression
	expression_changed.emit(expression)

## 표정 목록을 차례로 넘긴다 (시험용)
func next_expression() -> void:
	var names: Array = expressions.keys()
	if names.is_empty():
		return
	var i: int = names.find(current_expression)
	set_expression(names[(i + 1) % names.size()])

## 메시의 재질 칸을 툰 재질로 바꿔 끼운다. 원래 텍스처는 그대로 옮긴다.
static func _ensure_toon_material(mesh_inst: MeshInstance3D, surface: int) -> ShaderMaterial:
	var current: Material = mesh_inst.get_active_material(surface)
	if current is ShaderMaterial and (current as ShaderMaterial).shader == TOON_SHADER:
		return current
	var mat := ShaderMaterial.new()
	mat.shader = TOON_SHADER
	if current is BaseMaterial3D:
		var base: BaseMaterial3D = current
		if base.albedo_texture != null:
			mat.set_shader_parameter("albedo_tex", base.albedo_texture)
		mat.set_shader_parameter("tint", base.albedo_color)
	mesh_inst.set_surface_override_material(surface, mat)
	return mat

## 불러온 모델(glb) 안의 모든 메시를 툰 재질로 바꾼다
static func apply_toon_to_all(root: Node) -> void:
	for node: Node in root.find_children("*", "MeshInstance3D", true, false):
		var mi: MeshInstance3D = node
		if mi.mesh == null:
			continue
		for s: int in range(mi.mesh.get_surface_count()):
			_ensure_toon_material(mi, s)
