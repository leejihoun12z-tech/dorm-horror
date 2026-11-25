extends Node3D
## 회색 상자 시험 복도: 1인칭 조작 확인용. 길이 24m 복도 + 양쪽 방문 6개 + 끝 창문.

const CORRIDOR_LENGTH: float = 24.0
const CORRIDOR_WIDTH: float = 2.6
const WALL_HEIGHT: float = 2.7
const DOOR_SPACING: float = 6.0

@export var spawn_mannequin: bool = true
@export var mannequin_stage: int = 1

@onready var prompt_label: Label = $HUD/Prompt
@onready var player: Player = $Player
@onready var world_env: WorldEnvironment = $WorldEnvironment

var lamps: Array[OmniLight3D] = []
var mannequin: Mannequin = null
var is_night: bool = false

func _ready() -> void:
	_build_corridor()
	player.look_target_changed.connect(_on_look_target_changed)
	prompt_label.text = ""
	if spawn_mannequin:
		mannequin = Mannequin.new()
		mannequin.stage = mannequin_stage
		mannequin.position = Vector3(0.0, 0.0, -8.0)
		add_child(mannequin)
		mannequin.watcher = player.camera

## 밤: 복도 불 끔 · 푸른 어둠 · 손전등 켬. 낮: 반대.
func set_night(on: bool) -> void:
	is_night = on
	for lamp: OmniLight3D in lamps:
		lamp.visible = not on
	var env: Environment = world_env.environment
	env.background_color = Color(0.02, 0.025, 0.05) if on else Color(0.85, 0.82, 0.75)
	env.ambient_light_color = Color(0.35, 0.42, 0.65) if on else Color(1.0, 0.96, 0.88)
	env.ambient_light_energy = 0.08 if on else 0.55
	player.flashlight.visible = on

func _build_corridor() -> void:
	var floor_mat := _mat(Color(0.82, 0.74, 0.6))
	var wall_mat := _mat(Color(0.93, 0.89, 0.78))
	var trim_mat := _mat(Color(0.55, 0.72, 0.58))
	var door_mat := _mat(Color(0.6, 0.38, 0.2))
	var half_w: float = CORRIDOR_WIDTH * 0.5
	_box(Vector3(CORRIDOR_WIDTH, 0.2, CORRIDOR_LENGTH), Vector3(0, -0.1, -CORRIDOR_LENGTH * 0.5), floor_mat, true)
	_box(Vector3(CORRIDOR_WIDTH, 0.2, CORRIDOR_LENGTH), Vector3(0, WALL_HEIGHT + 0.1, -CORRIDOR_LENGTH * 0.5), wall_mat, true)
	for side: float in [-1.0, 1.0]:
		_box(Vector3(0.2, WALL_HEIGHT, CORRIDOR_LENGTH), Vector3(side * (half_w + 0.1), WALL_HEIGHT * 0.5, -CORRIDOR_LENGTH * 0.5), wall_mat, true)
		_box(Vector3(0.05, 0.9, CORRIDOR_LENGTH), Vector3(side * (half_w - 0.02), 0.45, -CORRIDOR_LENGTH * 0.5), trim_mat, false)
	_box(Vector3(CORRIDOR_WIDTH, WALL_HEIGHT, 0.2), Vector3(0, WALL_HEIGHT * 0.5, -CORRIDOR_LENGTH - 0.1), wall_mat, true)
	_box(Vector3(CORRIDOR_WIDTH, WALL_HEIGHT, 0.2), Vector3(0, WALL_HEIGHT * 0.5, 0.6), wall_mat, true)
	var i: int = 0
	var z: float = -3.0
	while z > -CORRIDOR_LENGTH + 1.0:
		for side: float in [-1.0, 1.0]:
			_door(Vector3(side * (half_w - 0.06), 0.0, z), side, door_mat, "%d호 문 열기" % (201 + i))
			i += 1
		z -= DOOR_SPACING
	for k: int in range(4):
		var lamp := OmniLight3D.new()
		lamp.position = Vector3(0, WALL_HEIGHT - 0.3, -3.0 - k * DOOR_SPACING)
		lamp.omni_range = 7.0
		lamp.light_energy = 1.4
		lamp.light_color = Color(1.0, 0.95, 0.85)
		add_child(lamp)
		lamps.append(lamp)

func _door(at: Vector3, side: float, mat: StandardMaterial3D, prompt_text: String) -> void:
	var door := Interactable.new()
	door.is_door = true
	door.prompt = prompt_text
	door.position = at + Vector3(0, 0, 0.45)
	door.open_angle_deg = 95.0 * side
	var mesh := MeshInstance3D.new()
	var box := BoxMesh.new()
	box.size = Vector3(0.06, 2.05, 0.9)
	mesh.mesh = box
	mesh.material_override = mat
	mesh.position = Vector3(0, 1.025, -0.45)
	door.add_child(mesh)
	var shape := CollisionShape3D.new()
	var bs := BoxShape3D.new()
	bs.size = box.size
	shape.shape = bs
	shape.position = mesh.position
	door.add_child(shape)
	add_child(door)

func _box(size: Vector3, at: Vector3, mat: StandardMaterial3D, solid: bool) -> void:
	var mesh := MeshInstance3D.new()
	var box := BoxMesh.new()
	box.size = size
	mesh.mesh = box
	mesh.material_override = mat
	if solid:
		var body := StaticBody3D.new()
		body.position = at
		var shape := CollisionShape3D.new()
		var bs := BoxShape3D.new()
		bs.size = size
		shape.shape = bs
		body.add_child(shape)
		body.add_child(mesh)
		add_child(body)
	else:
		mesh.position = at
		add_child(mesh)

func _mat(color: Color) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = color
	m.roughness = 0.9
	return m

func _on_look_target_changed(target: Node) -> void:
	prompt_label.text = ("[E] " + (target as Interactable).prompt) if target is Interactable else ""
