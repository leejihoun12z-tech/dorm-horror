class_name Player
extends CharacterBody3D
## 1인칭 사감. WASD 이동 · 스페이스 점프 · Shift 숙이기 · 마우스 시선 · E/왼쪽 클릭 상호작용 · F 손전등.

signal interacted(target: Node)
signal look_target_changed(target: Node)

@export var walk_speed: float = 3.0
@export var crouch_speed: float = 1.4
@export var jump_velocity: float = 3.6
@export var mouse_sensitivity: float = 0.0025
@export var stand_eye_height: float = 1.6
@export var crouch_eye_height: float = 0.95
@export var crouch_lerp_speed: float = 10.0
@export var interact_distance: float = 2.2

@onready var head: Node3D = $Head
@onready var camera: Camera3D = $Head/Camera3D
@onready var ray: RayCast3D = $Head/Camera3D/InteractRay
@onready var flashlight: SpotLight3D = $Head/Camera3D/Flashlight
@onready var body_shape: CollisionShape3D = $BodyShape

var is_crouching: bool = false
var _look_target: Node = null
var _stand_shape_height: float = 0.0

func _ready() -> void:
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	ray.target_position = Vector3(0.0, 0.0, -interact_distance)
	_stand_shape_height = (body_shape.shape as CapsuleShape3D).height

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		var motion: InputEventMouseMotion = event
		rotate_y(-motion.relative.x * mouse_sensitivity)
		head.rotate_x(-motion.relative.y * mouse_sensitivity)
		head.rotation.x = clampf(head.rotation.x, deg_to_rad(-85.0), deg_to_rad(85.0))
	elif event.is_action_pressed("pause"):
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE if Input.mouse_mode == Input.MOUSE_MODE_CAPTURED else Input.MOUSE_MODE_CAPTURED
	elif event.is_action_pressed("flashlight"):
		flashlight.visible = not flashlight.visible
	elif event.is_action_pressed("interact") and _look_target != null:
		if _look_target.has_method("interact"):
			_look_target.call("interact", self)
		interacted.emit(_look_target)

func _physics_process(delta: float) -> void:
	is_crouching = Input.is_action_pressed("crouch") or (is_crouching and not _can_stand())
	var target_eye: float = crouch_eye_height if is_crouching else stand_eye_height
	head.position.y = lerpf(head.position.y, target_eye, clampf(crouch_lerp_speed * delta, 0.0, 1.0))
	var capsule: CapsuleShape3D = body_shape.shape
	capsule.height = _stand_shape_height * (0.6 if is_crouching else 1.0)
	body_shape.position.y = capsule.height * 0.5

	if not is_on_floor():
		velocity += get_gravity() * delta
	elif Input.is_action_just_pressed("jump") and not is_crouching:
		velocity.y = jump_velocity

	var input_dir: Vector2 = Input.get_vector("move_left", "move_right", "move_forward", "move_back")
	var direction: Vector3 = (transform.basis * Vector3(input_dir.x, 0.0, input_dir.y)).normalized()
	var speed: float = crouch_speed if is_crouching else walk_speed
	velocity.x = direction.x * speed
	velocity.z = direction.z * speed
	move_and_slide()
	_update_look_target()

func _can_stand() -> bool:
	var space: PhysicsDirectSpaceState3D = get_world_3d().direct_space_state
	var query := PhysicsRayQueryParameters3D.create(global_position + Vector3.UP * 0.5, global_position + Vector3.UP * (_stand_shape_height + 0.05))
	query.exclude = [get_rid()]
	return space.intersect_ray(query).is_empty()

func _update_look_target() -> void:
	var hit: Node = ray.get_collider() if ray.is_colliding() else null
	if hit != null and not hit.has_method("interact"):
		hit = null
	if hit != _look_target:
		_look_target = hit
		look_target_changed.emit(hit)
