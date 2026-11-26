extends SceneTree
## 2D 일러스트 입간판 시안: godot --path . -s res://tools/dev/billboard_mock.gd -- --dir=절대경로
## 시험 복도에 마네킹 전신 일러스트(배경 지운 판)를 세워 낮 정면 · 낮 비스듬히(카메라 향함) · 낮 비스듬히(향하지 않음 = 종이) · 밤 손전등을 찍는다.

var dir: String = "res://.screenshots"

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

func _run() -> void:
	var scene: Node3D = (load("res://game/world/test_corridor.tscn") as PackedScene).instantiate()
	scene.set("spawn_mannequin", false)
	root.add_child(scene)
	await process_frame
	(scene.get_node("HUD") as CanvasLayer).visible = false
	var tex: Texture2D = load("res://assets/characters/mannequin/illust_cutout_test.png")
	var spr := Sprite3D.new()
	spr.texture = tex
	spr.pixel_size = 1.55 / float(tex.get_height())
	spr.centered = true
	spr.offset = Vector2(0, tex.get_height() * 0.5)
	spr.shaded = true
	spr.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
	spr.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	spr.position = Vector3(0, 0, -6.0)
	scene.add_child(spr)
	var shadow := MeshInstance3D.new()
	var disc := CylinderMesh.new()
	disc.top_radius = 0.28
	disc.bottom_radius = 0.28
	disc.height = 0.005
	shadow.mesh = disc
	var sm := StandardMaterial3D.new()
	sm.albedo_color = Color(0, 0, 0, 0.35)
	sm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	sm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	shadow.material_override = sm
	shadow.position = Vector3(0, 0.003, -6.0)
	scene.add_child(shadow)
	var cam := Camera3D.new()
	scene.add_child(cam)
	cam.current = true
	cam.fov = 60.0
	var spot := SpotLight3D.new()
	spot.light_energy = 3.5
	spot.spot_range = 14.0
	spot.spot_angle = 24.0
	spot.shadow_enabled = true
	cam.add_child(spot)
	spot.visible = false
	var target := Vector3(0, 0.9, -6.0)
	# 1 낮 정면
	spr.billboard = BaseMaterial3D.BILLBOARD_FIXED_Y
	cam.global_position = Vector3(0, 1.6, -3.0)
	cam.look_at(target, Vector3.UP)
	await _shot("bb_day_front")
	# 2 낮 비스듬히, 카메라를 향함
	cam.global_position = Vector3(1.0, 1.6, -4.4)
	cam.look_at(target, Vector3.UP)
	await _shot("bb_day_side_facing")
	# 3 낮 비스듬히, 향하지 않음 (종이처럼 얇음)
	spr.billboard = BaseMaterial3D.BILLBOARD_DISABLED
	cam.global_position = Vector3(1.15, 1.6, -5.4)
	cam.look_at(target, Vector3.UP)
	await _shot("bb_day_side_paper")
	# 4 밤 손전등 정면
	spr.billboard = BaseMaterial3D.BILLBOARD_FIXED_Y
	scene.call("set_night", true)
	(scene.get("player") as Player).flashlight.visible = false
	spot.visible = true
	cam.global_position = Vector3(0, 1.6, -2.4)
	cam.look_at(target, Vector3.UP)
	await _shot("bb_night_front")
	quit()
