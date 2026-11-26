extends SceneTree
## 방향 입간판 시안 (tech-plan §5-5-3):
##   godot --path . --fixed-fps 30 -s res://tools/dev/directional_mock.gd -- --dir=절대경로 [--video]
## 먼저 python tools/dev/make_turnaround_cutouts.py 로 .screenshots/dir_fx/idle_0·2·3.png 를 만든다.
## 왼쪽 = 그림 3장(정면·옆·뒤, 옆은 뒤집어 양옆) 4방향 · 오른쪽 = Tripo 3D 마네킹 걷기를 8방향 × 12칸으로 구워 만든 입간판.
## 두 캐릭터를 제자리에서 돌린다(= 내가 둘레를 도는 것과 같은 각도). 판은 늘 나를 향하고 그림만 바뀐다.

const BAKE_DIRS: int = 8
const BAKE_FRAMES: int = 12
const BAKE_W: int = 360
const BAKE_H: int = 540
const BAKE_SPAN: float = 1.75  # 구운 그림 세로 = 1.75m
const CHAR_H: float = 1.55

var dir: String = "res://.screenshots"
var video: bool = false
var scene: Node3D
var cam: Camera3D
var body_a: Node3D
var body_b: Node3D

func _init() -> void:
	for a: String in OS.get_cmdline_user_args():
		if a.begins_with("--dir="):
			dir = a.substr(6)
		elif a == "--video":
			video = true
	DirAccess.make_dir_recursive_absolute(dir)
	_run()

func _shot(name: String) -> void:
	for i: int in range(4):
		await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(dir + "/" + name + ".png")
	print("saved ", name)

func _tex(path: String) -> Texture2D:
	var img := Image.load_from_file(ProjectSettings.globalize_path(path))
	img.generate_mipmaps()
	return ImageTexture.create_from_image(img)

## Tripo 3D 마네킹 걷기를 8방향 × 12칸으로 굽는다 (화면 밖 뷰포트, 투명 바탕, 평평한 빛)
func _bake() -> SpriteFrames:
	var sv := SubViewport.new()
	sv.size = Vector2i(BAKE_W, BAKE_H)
	sv.transparent_bg = true
	sv.own_world_3d = true
	sv.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(sv)
	var rc := RiggedCharacter.new()
	rc.model_path = "res://assets/characters/mannequin_rigged/mannequin_rigged.glb"
	rc.height = CHAR_H
	sv.add_child(rc)
	var bcam := Camera3D.new()
	bcam.projection = Camera3D.PROJECTION_ORTHOGONAL
	bcam.size = BAKE_SPAN
	var env := Environment.new()
	env.background_mode = Environment.BG_CLEAR_COLOR
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color.WHITE
	env.ambient_light_energy = 0.6
	bcam.environment = env
	sv.add_child(bcam)
	var key := DirectionalLight3D.new()
	key.light_energy = 0.6
	bcam.add_child(key)
	await process_frame
	var sf := SpriteFrames.new()
	var length: float = rc.anim.get_animation("walk").length
	rc.anim.play("walk")
	rc.anim.pause()
	for d: int in range(BAKE_DIRS):
		var anim_name: String = "walk_%d" % d
		sf.add_animation(anim_name)
		sf.set_animation_loop(anim_name, true)
		sf.set_animation_speed(anim_name, float(BAKE_FRAMES) / length)
		var th: float = deg_to_rad(360.0 / BAKE_DIRS * d)
		bcam.position = Vector3(sin(th) * 4.0, BAKE_SPAN * 0.5, cos(th) * 4.0)
		bcam.look_at(Vector3(0, BAKE_SPAN * 0.5, 0), Vector3.UP)
		for f: int in range(BAKE_FRAMES):
			rc.anim.seek(length * float(f) / BAKE_FRAMES, true)
			await process_frame
			await RenderingServer.frame_post_draw
			var img: Image = sv.get_texture().get_image()
			img.generate_mipmaps()
			sf.add_frame(anim_name, ImageTexture.create_from_image(img))
	# 굽기 확인용 한 장 (8방향 × 첫 칸)
	var sheet := Image.create(BAKE_W * BAKE_DIRS, BAKE_H, false, Image.FORMAT_RGBA8)
	for d: int in range(BAKE_DIRS):
		var im: Image = sf.get_frame_texture("walk_%d" % d, 0).get_image()
		im.clear_mipmaps()
		sheet.blit_rect(im, Rect2i(0, 0, BAKE_W, BAKE_H), Vector2i(d * BAKE_W, 0))
	sheet.save_png(dir + "/bake_sheet.png")
	sv.queue_free()
	return sf

func _illust_frames() -> SpriteFrames:
	var sf := SpriteFrames.new()
	sf.remove_animation("default")
	for k: int in [0, 2, 3]:
		var n: String = "idle_%d" % k
		sf.add_animation(n)
		sf.add_frame(n, _tex("res://.screenshots/dir_fx/%s.png" % n))
	return sf

func _make_body(at: Vector3, sf: SpriteFrames, dirs: int, action: String, pixel: float, tex_h: float) -> Node3D:
	var body := Node3D.new()
	body.position = at
	scene.add_child(body)
	var db := DirectionalBillboard.new()
	db.sprite_frames = sf
	db.directions = dirs
	db.pixel_size = pixel
	db.offset = Vector2(0, tex_h * 0.5)
	db.shaded = true
	db.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
	db.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	body.add_child(db)
	db.action = action
	# 발밑 그림자
	var sh := MeshInstance3D.new()
	var disc := CylinderMesh.new()
	disc.top_radius = 0.26
	disc.bottom_radius = 0.26
	disc.height = 0.004
	sh.mesh = disc
	var sm := StandardMaterial3D.new()
	sm.albedo_color = Color(0, 0, 0, 0.3)
	sm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	sm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	sh.mesh.surface_set_material(0, sm)
	sh.position = Vector3(0, 0.003, 0)
	body.add_child(sh)
	return body

func _run() -> void:
	var baked: SpriteFrames = await _bake()
	scene = (load("res://game/world/test_corridor.tscn") as PackedScene).instantiate()
	scene.set("spawn_mannequin", false)
	root.add_child(scene)
	await process_frame
	(scene.get_node("HUD") as CanvasLayer).visible = false
	cam = Camera3D.new()
	scene.add_child(cam)
	cam.current = true
	cam.fov = 55.0
	cam.position = Vector3(0, 1.45, -3.2)
	cam.look_at(Vector3(0, 0.85, -6.5), Vector3.UP)
	var ill: SpriteFrames = _illust_frames()
	var ill_h: float = float(ill.get_frame_texture("idle_0", 0).get_height())
	body_a = _make_body(Vector3(-0.55, 0, -6.5), ill, 4, "idle", CHAR_H / ill_h, ill_h)
	body_b = _make_body(Vector3(0.55, 0, -6.5), baked, 8, "walk", BAKE_SPAN / BAKE_H, BAKE_H)
	if video:
		var fdir: String = dir + "/frames"
		DirAccess.make_dir_recursive_absolute(fdir)
		for i: int in range(240):
			var yaw: float = -TAU * float(i) / 240.0
			body_a.rotation.y = yaw
			body_b.rotation.y = yaw
			await process_frame
			await RenderingServer.frame_post_draw
			root.get_texture().get_image().save_png("%s/f_%04d.png" % [fdir, i])
		print("frames 240")
	else:
		# 내가 캐릭터 둘레를 도는 각도 = 캐릭터를 반대로 돌린 것
		for deg: int in [0, 45, 90, 135, 180, 270]:
			body_a.rotation.y = deg_to_rad(-deg)
			body_b.rotation.y = deg_to_rad(-deg)
			await _shot("dir_%03d" % deg)
	quit()
