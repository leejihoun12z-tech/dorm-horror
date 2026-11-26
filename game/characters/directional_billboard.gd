class_name DirectionalBillboard
extends AnimatedSprite3D
## 방향 입간판 [후보] (tech-plan §5-5-3): 판은 늘 나를 향하고(Y 빌보드), 그림은 내가 캐릭터를 보는 각도에 따라 정면 → 옆 → 뒤로 바뀐다.
## 한 장짜리가 아니라 방향마다 동작(걷기·대기 …)이 돈다. 방향이 바뀌어도 동작 칸은 이어진다.
##
## SpriteFrames 이름 규칙: "<동작>_<방향번호>". 방향번호 0 = 정면, 반시계(위에서 볼 때)로 360/directions 도씩.
##   4방향: 0 정면 · 1 캐릭터 왼쪽에서 봄 · 2 뒤 · 3 캐릭터 오른쪽에서 봄
## mirror_missing = true면, 없는 방향은 반대쪽 방향 그림을 좌우 뒤집어 쓴다(옆 1장으로 양옆).
## 캐릭터 정면 = 부모 Node3D의 +Z (glb 기본).

## 방향 수 (4 또는 8)
@export_enum("4:4", "8:8") var directions: int = 4
## 지금 동작 이름 (예: "walk", "idle")
@export var action: String = "idle":
	set(v):
		action = v
		_apply(true)
## 없는 방향은 반대쪽을 뒤집어 씀
@export var mirror_missing: bool = true
## 경계에서 깜빡이지 않게 여유 각도 (도)
@export_range(0.0, 20.0) var hysteresis_deg: float = 8.0

## 지금 보이는 방향 번호
var sector: int = 0

func _ready() -> void:
	billboard = BaseMaterial3D.BILLBOARD_FIXED_Y
	_apply(true)

func _process(_delta: float) -> void:
	_apply(false)

## 카메라가 캐릭터 둘레 어느 각도에 있나 (0 = 정면, 반시계 +, 도 단위 -180~180)
func view_angle_deg(cam: Camera3D) -> float:
	var body: Node3D = get_parent() as Node3D
	if body == null or cam == null:
		return 0.0
	var local: Vector3 = body.global_basis.inverse() * (cam.global_position - body.global_position)
	return rad_to_deg(atan2(local.x, local.z))

func _apply(force: bool) -> void:
	if sprite_frames == null or not is_inside_tree():
		return
	var cam: Camera3D = get_viewport().get_camera_3d()
	var step: float = 360.0 / float(directions)
	var a: float = view_angle_deg(cam)
	var target: int = posmod(roundi(a / step), directions)
	if target != sector and not force:
		# 지금 방향의 가운데에서 반 칸 + 여유각을 넘었을 때만 바꾼다
		var center: float = float(sector) * step
		var diff: float = absf(wrapf(a - center, -180.0, 180.0))
		if diff < step * 0.5 + hysteresis_deg:
			target = sector
	if target == sector and not force:
		return
	sector = target
	var name_now: String = "%s_%d" % [action, sector]
	var flip: bool = false
	if not sprite_frames.has_animation(name_now) and mirror_missing:
		name_now = "%s_%d" % [action, posmod(directions - sector, directions)]
		flip = true
	if not sprite_frames.has_animation(name_now):
		return
	var keep_frame: int = frame
	var keep_progress: float = frame_progress
	flip_h = flip
	play(name_now)
	if sprite_frames.get_frame_count(name_now) > keep_frame:
		set_frame_and_progress(keep_frame, keep_progress)
