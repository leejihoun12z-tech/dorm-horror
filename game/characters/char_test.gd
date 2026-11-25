extends Node3D
## 기숙생 1명 3D 시험 장면 (STATUS 다음 할 일 2): 시험 복도에 캐릭터를 세우고
## 낮/밤(손전등) · 표정 바꾸기 · 걷기를 본다. 대역 몸으로 먼저 돌리고, 실제 모델이 오면 character_scene만 바꾼다.
## N = 낮/밤 · X = 다음 표정 · B = 걷기 켜고 끄기 (시험용 키, project.godot [input])

const CORRIDOR_SCENE: PackedScene = preload("res://game/world/test_corridor.tscn")
const WALK_NEAR_Z: float = -4.0
const WALK_FAR_Z: float = -13.0

@export var character_scene: PackedScene
@export var stand_position: Vector3 = Vector3(0.0, 0.0, -4.5)
@export var walk_speed: float = 1.1
@export var night: bool = false

var corridor: Node3D
var character: CharacterView
var walking: bool = false
var _walk_dir: float = -1.0
var _night_env: Environment
var _day_env: Environment

func _ready() -> void:
	corridor = CORRIDOR_SCENE.instantiate()
	add_child(corridor)
	if character_scene != null:
		character = character_scene.instantiate()
	else:
		character = PlaceholderBody.new()
	character.position = stand_position
	add_child(character)
	var world_env: WorldEnvironment = corridor.get_node("WorldEnvironment")
	_day_env = world_env.environment
	_night_env = _make_night_env()
	var help: Label = corridor.get_node("HUD/Help")
	help.text += "\n[시험] N 낮/밤 · X 표정 · B 걷기"
	set_night(night)

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("debug_toggle_night"):
		set_night(not night)
	elif event.is_action_pressed("debug_next_expression"):
		character.next_expression()
	elif event.is_action_pressed("debug_toggle_walk"):
		walking = not walking

func _process(delta: float) -> void:
	if walking:
		step_walk(delta)

func step_walk(delta: float) -> void:
	character.position.z += _walk_dir * walk_speed * delta
	if character.position.z < WALK_FAR_Z or character.position.z > WALK_NEAR_Z:
		character.position.z = clampf(character.position.z, WALK_FAR_Z, WALK_NEAR_Z)
		_walk_dir = -_walk_dir
	# 몸은 +Z를 앞으로 만든다 → 가는 쪽을 보게 돌림
	character.rotation.y = 0.0 if _walk_dir > 0.0 else PI

func set_night(value: bool) -> void:
	night = value
	(corridor.get_node("WorldEnvironment") as WorldEnvironment).environment = _night_env if night else _day_env
	for lamp: Node in get_tree().get_nodes_in_group(&"corridor_lamps"):
		(lamp as Light3D).visible = not night
	var player: Player = corridor.get_node("Player")
	player.flashlight.visible = night

func _make_night_env() -> Environment:
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.01, 0.012, 0.02)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.25, 0.3, 0.45)
	env.ambient_light_energy = 0.06
	env.fog_enabled = true
	env.fog_light_color = Color(0.02, 0.025, 0.035)
	env.fog_density = 0.08
	return env

## screenshot.gd가 부른다: --night · --expr=이름 · --walk=초 · --far · --near
func apply_shot_args(args: PackedStringArray) -> void:
	if "--night" in args:
		set_night(true)
	for a: String in args:
		if a.begins_with("--expr="):
			character.set_expression(StringName(a.substr(7)))
		elif a.begins_with("--walk="):
			var t: float = float(a.substr(7))
			var dt: float = 1.0 / 30.0
			for i: int in range(int(t / dt)):
				step_walk(dt)
	if "--far" in args:
		character.position.z = -8.0
	elif "--near" in args:
		character.position.z = -2.0
