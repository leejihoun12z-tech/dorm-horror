extends SceneTree
## 캐릭터 시험 화면 여러 장: godot --path . -s res://tools/dev/char_shots.gd -- --dir=절대경로
## 찍는 것: 낮 전신 · 낮 얼굴 0~3단계 · 밤 손전등 전신(1단계) · 밤 3단계 · "안 볼 때 자세 바뀜" 확인(콘솔)

var dir: String = "res://.screenshots"
var scene: Node3D
var cam: Camera3D
var spot: SpotLight3D

func _init() -> void:
	for a: String in OS.get_cmdline_user_args():
		if a.begins_with("--dir="):
			dir = a.substr(6)
	DirAccess.make_dir_recursive_absolute(dir)
	_run()

func _shot(name: String) -> void:
	for i: int in range(6):
		await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(dir + "/" + name + ".png")
	print("saved ", name)

func _aim(from: Vector3, at: Vector3, fov: float = 50.0) -> void:
	cam.global_position = from
	cam.look_at(at, Vector3.UP)
	cam.fov = fov

func _run() -> void:
	scene = (load("res://game/world/test_corridor.tscn") as PackedScene).instantiate()
	root.add_child(scene)
	await process_frame
	(scene.get_node("HUD") as CanvasLayer).visible = false
	cam = Camera3D.new()
	scene.add_child(cam)
	cam.current = true
	spot = SpotLight3D.new()
	spot.light_energy = 3.5
	spot.spot_range = 14.0
	spot.spot_angle = 24.0
	spot.shadow_enabled = true
	cam.add_child(spot)
	spot.visible = false
	var m: Mannequin = scene.get("mannequin")
	m.watcher = cam
	var mp: Vector3 = m.global_position
	# 낮 전신
	m.set_stage(0)
	_aim(mp + Vector3(0.0, 1.0, 2.0), mp + Vector3(0, 0.8, 0))
	await _shot("day_full_s0")
	_aim(mp + Vector3(1.0, 1.1, 1.6), mp + Vector3(0, 0.85, 0))
	await _shot("day_34_s0")
	# 얼굴 0~3단계
	for st: int in range(4):
		m.set_stage(st)
		var hp: Vector3 = (m.joints["head"] as Node3D).global_position + Vector3(0, 0.12, 0)
		if st >= 3:
			hp = (m.joints["head"] as Node3D).global_position + Vector3(0, -0.12, 0)
		_aim(hp + Vector3(0, 0.0, 0.62), hp, 40.0)
		await _shot("face_s%d" % st)
	# 밤
	scene.call("set_night", true)
	(scene.get("player") as Player).flashlight.visible = false
	spot.visible = true
	m.set_stage(1)
	_aim(mp + Vector3(0.0, 1.5, 3.2), mp + Vector3(0, 0.9, 0))
	await _shot("night_full_s1")
	m.set_stage(3)
	await _shot("night_full_s3")
	# 안 볼 때 자세 바뀜 확인
	m.set_stage(1)
	var before: Vector3 = (m.joints["head"] as Node3D).rotation
	_aim(mp + Vector3(0.0, 1.5, 3.2), mp + Vector3(0, 0.9, 8.0))
	for i: int in range(120):
		await process_frame
	_aim(mp + Vector3(0.0, 1.5, 3.2), mp + Vector3(0, 0.9, 0))
	await process_frame
	var after: Vector3 = (m.joints["head"] as Node3D).rotation
	print("unseen pose changes: ", m.pose_change_count, " head before ", before, " after ", after)
	await _shot("night_after_lookaway_s1")
	quit()
