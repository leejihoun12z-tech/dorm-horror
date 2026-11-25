class_name Interactable
extends StaticBody3D
## 바라보고 E(또는 왼쪽 클릭)로 쓰는 물건. 지금은 시험용: 문은 열고 닫힘, 나머지는 알림만.

signal used(by: Node)

@export var prompt: String = "조사하기"
@export var is_door: bool = false
@export var open_angle_deg: float = 95.0

var is_open: bool = false
var _closed_rotation_y: float = 0.0

func _ready() -> void:
	_closed_rotation_y = rotation.y

func interact(by: Node) -> void:
	if is_door:
		is_open = not is_open
		var tween := create_tween()
		tween.tween_property(self, "rotation:y", _closed_rotation_y + (deg_to_rad(open_angle_deg) if is_open else 0.0), 0.35)
	used.emit(by)
