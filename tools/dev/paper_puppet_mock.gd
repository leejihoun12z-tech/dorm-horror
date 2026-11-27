extends SceneTree
## 종이인형극 빌보드 시안 (tech-plan §5-5-5):
##   godot --path . --fixed-fps 30 -s res://tools/dev/paper_puppet_mock.gd -- --dir=절대경로 [--video]
## 먼저 python tools/dev/make_turnaround_cutouts.py → python tools/dev/make_paper_cards.py (.screenshots/paper_fx/)
## 정지: 정면 · 비스듬히(종이 두께) · 뒤집히는 중 · 뒷모습 · 상황 그림으로 바뀜 · 밤 손전등(카드 그림자)
## 영상: 다가옴(콩콩) → 멈춤 → 상황 그림 → 돌아서 멀어짐(뒤집힘) → 다시 돌아봄

var dir: String = "res://.screenshots"
var video: bool = false
var scene: Node3D
var cam: Camera3D
var puppet: PaperPuppet

func _init() -> void:
	for a: String in OS.get_cmdline_user_args():
		if a.begins_with("--dir="):
			dir = a.substr(6)
		elif a == "--video":
			video = true
	DirAccess.make_dir_recursive_absolute(dir)
	_run()

func _tex(name: String) -> Texture2D:
	var img := Image.load_from_file(ProjectSettings.globalize_path("res://.screenshots/paper_fx/%s.png" % name))
	img.generate_mipmaps()
	return ImageTexture.create_from_image(img)

func _frames(n: int) -> void:
	for i: int in range(n):
		await process_frame

func _shot(name: String) -> void:
	await _frames(3)
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(dir + "/" + name + ".png")
	print("saved ", name)

func _run() -> void:
	scene = (load("res://game/world/test_corridor.tscn") as PackedScene).instantiate()
	scene.set("spawn_mannequin", false)
	root.add_child(scene)
	await process_frame
	(scene.get_node("HUD") as CanvasLayer).visible = false
	cam = Camera3D.new()
	scene.add_child(cam)
	cam.current = true
	cam.fov = 55.0
	puppet = PaperPuppet.new()
	puppet.poses = {"front": _tex("front"), "back": _tex("back"), "side": _tex("pose_side")}
	puppet.position = Vector3(0, 0, -6.5)
	scene.add_child(puppet)
	_blob(puppet)
	if video:
		await _video()
	else:
		await _stills()
	quit()

func _blob(parent: Node3D) -> void:
	var sh := MeshInstance3D.new()
	var disc := CylinderMesh.new()
	disc.top_radius = 0.24
	disc.bottom_radius = 0.24
	disc.height = 0.004
	sh.mesh = disc
	var sm := StandardMaterial3D.new()
	sm.albedo_color = Color(0, 0, 0, 0.28)
	sm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	sm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	sh.material_override = sm
	sh.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	sh.position = Vector3(0, 0.003, 0)
	parent.add_child(sh)

func _aim(from: Vector3, look: Vector3) -> void:
	cam.global_position = from
	cam.look_at(look, Vector3.UP)

func _stills() -> void:
	var t := Vector3(0, 0.85, -6.5)
	_aim(Vector3(0, 1.5, -3.6), t)
	await _shot("pp_1_front")
	# 비스듬히: 판은 나를 향하지만 아주 옆에서 보면 두께가 보이도록, 이 한 장만 카드 회전을 잠깐 멈춤
	_aim(Vector3(1.05, 1.45, -5.3), t)
	await _frames(2)
	puppet.set_process(false)
	puppet._pivot.global_rotation = Vector3(0, deg_to_rad(-62), 0)
	await _shot("pp_2_paper_edge")
	puppet.set_process(true)
	# 뒤집히는 중: 캐릭터가 돌아섬 → 몇 프레임 뒤 찍기
	_aim(Vector3(0, 1.5, -3.6), t)
	await _frames(4)
	puppet.rotation.y = PI
	await _frames(2)
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(dir + "/pp_3_flipping.png")
	print("saved pp_3_flipping")
	await _frames(10)
	await _shot("pp_4_back")
	puppet.rotation.y = 0.0
	await _frames(12)
	puppet.set_pose("side")
	await _frames(10)
	await _shot("pp_5_pose")
	puppet.set_pose("front")
	# 밤: 손전등 → 카드 모양 그림자가 벽·바닥에
	scene.call("set_night", true)
	(scene.get("player") as Player).flashlight.visible = false
	var spot := SpotLight3D.new()
	spot.light_energy = 4.0
	spot.spot_range = 14.0
	spot.spot_angle = 28.0
	spot.shadow_enabled = true
	cam.add_child(spot)
	_aim(Vector3(0.75, 1.3, -3.4), Vector3(-0.2, 0.9, -6.8))
	await _frames(12)
	await _shot("pp_6_night")

func _video() -> void:
	var fdir: String = dir + "/frames"
	DirAccess.make_dir_recursive_absolute(fdir)
	_aim(Vector3(0.0, 1.5, -2.6), Vector3(0, 0.9, -8.0))
	var f: int = 0
	# 1) 멀리서 다가옴 (2.5초)
	puppet.rotation.y = 0.0
	for i: int in range(75):
		puppet.position = Vector3(0.2, 0, lerpf(-12.0, -6.0, float(i) / 74.0))
		f = await _cap(fdir, f)
	# 2) 멈춤 → 상황 그림 → 되돌림 (2초)
	for i: int in range(60):
		if i == 12:
			puppet.set_pose("side")
		if i == 45:
			puppet.set_pose("front")
		f = await _cap(fdir, f)
	# 3) 돌아서 멀어짐 (2.5초)
	puppet.rotation.y = PI
	for i: int in range(75):
		var k: float = clampf((float(i) - 6.0) / 68.0, 0.0, 1.0)
		puppet.position = Vector3(lerpf(0.2, -0.3, k), 0, lerpf(-6.0, -10.5, k))
		f = await _cap(fdir, f)
	# 4) 멈춰서 돌아봄 (1.5초)
	for i: int in range(45):
		if i == 15:
			puppet.rotation.y = 0.0
		f = await _cap(fdir, f)
	print("frames ", f)

func _cap(fdir: String, f: int) -> int:
	await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png("%s/f_%04d.png" % [fdir, f])
	return f + 1
