extends SceneTree
## 밤 추격 연출 시안(5-5-2): godot --path . -s res://tools/dev/signature_mock.gd -- --dir=절대경로 [--video]
## 먼저 python tools/dev/make_signature_mock_tex.py 로 .screenshots/mock_fx/ 텍스처를 만든다(그림 대역).
## 정지 화면: A 그림자만 괴물 · B 어둠 속에서만 진짜 모습 · C 종이 레이어가 벌어짐 · D1~D3 깜빡일 때마다 작화 붕괴하며 다가옴
## --video: 깜빡임 접근 6초 프레임(dir/frames/)을 찍는다. ffmpeg로 묶는다.

const TEX_DIR: String = "res://.screenshots/mock_fx/"
const CARD_H: float = 1.55
const SRC_H: float = 920.0

var dir: String = "res://.screenshots"
var video: bool = false
var scene: Node3D
var cam: Camera3D
var spot: SpotLight3D
var tex: Dictionary = {}

func _init() -> void:
	for a: String in OS.get_cmdline_user_args():
		if a.begins_with("--dir="):
			dir = a.substr(6)
		elif a == "--video":
			video = true
	DirAccess.make_dir_recursive_absolute(dir)
	_run()

func _load(name: String) -> Texture2D:
	var img := Image.load_from_file(ProjectSettings.globalize_path(TEX_DIR + name + ".png"))
	img.generate_mipmaps()
	return ImageTexture.create_from_image(img)

func _shot(name: String, settle: int = 6) -> void:
	for i: int in range(settle):
		await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(dir + "/" + name + ".png")
	print("saved ", name)

## 그림 한 장을 세운다. 발이 바닥(y=0)에 닿게. 픽셀 크기는 모든 그림이 같다(원본 920px = 1.55m).
func _card(t: Texture2D, at: Vector3, billboard: bool) -> Sprite3D:
	var s := Sprite3D.new()
	s.texture = t
	s.pixel_size = CARD_H / SRC_H
	s.offset = Vector2(0, t.get_height() * 0.5)
	s.shaded = true
	s.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
	s.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	s.billboard = BaseMaterial3D.BILLBOARD_FIXED_Y if billboard else BaseMaterial3D.BILLBOARD_DISABLED
	s.position = at
	scene.add_child(s)
	return s

func _base(at: Vector3) -> MeshInstance3D:
	var m := MeshInstance3D.new()
	var b := BoxMesh.new()
	b.size = Vector3(0.62, 0.025, 0.32)
	m.mesh = b
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.85, 0.92, 1.0, 0.35)
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.roughness = 0.05
	mat.metallic_specular = 1.0
	m.material_override = mat
	m.position = at + Vector3(0, 0.0125, 0)
	scene.add_child(m)
	return m

func _clear() -> void:
	for c: Node in scene.get_children():
		if c.has_meta("mock"):
			c.queue_free()
	await process_frame

func _mark(n: Node) -> Node:
	n.set_meta("mock", true)
	return n

func _aim(from: Vector3, look: Vector3) -> void:
	cam.global_position = from
	cam.look_at(look, Vector3.UP)

func _run() -> void:
	for n: String in ["day", "shadow", "true", "s1", "s2", "s3"]:
		tex[n] = _load(n)
	scene = (load("res://game/world/test_corridor.tscn") as PackedScene).instantiate()
	scene.set("spawn_mannequin", false)
	root.add_child(scene)
	await process_frame
	(scene.get_node("HUD") as CanvasLayer).visible = false
	cam = Camera3D.new()
	scene.add_child(cam)
	cam.current = true
	cam.fov = 60.0
	spot = SpotLight3D.new()
	spot.light_energy = 4.0
	spot.spot_range = 16.0
	spot.spot_angle = 24.0
	spot.shadow_enabled = true
	cam.add_child(spot)
	spot.visible = false
	if video:
		await _video()
	else:
		await _stills()
	quit()

func _stills() -> void:
	# A 해 질 녘: 등신대는 귀여운데 벽에 비친 그림자만 괴물
	var at := Vector3(0.0, 0, -21.6)
	var day: Sprite3D = _mark(_card(tex["day"], at, false))
	day.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	var sh: Sprite3D = _mark(_card(tex["shadow"], at + Vector3(0, 0, -0.02), false))
	sh.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_SHADOWS_ONLY
	_mark(_base(at))
	var sun := SpotLight3D.new()
	sun.light_energy = 6.0
	sun.spot_range = 12.0
	sun.spot_angle = 55.0
	sun.light_color = Color(1.0, 0.72, 0.45)
	sun.shadow_enabled = true
	_mark(sun)
	scene.add_child(sun)
	sun.global_position = Vector3(0.15, 0.35, -19.4)
	sun.look_at(Vector3(0.0, 1.6, -24.0), Vector3.UP)
	var env: Environment = (scene.get("world_env") as WorldEnvironment).environment
	env.ambient_light_energy = 0.22
	for lamp: OmniLight3D in scene.get("lamps"):
		lamp.visible = false
	_aim(Vector3(0.55, 1.5, -16.8), Vector3(-0.05, 1.25, -23.0))
	await _shot("sig_A_shadow")
	for lamp: OmniLight3D in scene.get("lamps"):
		lamp.visible = true
	await _clear()

	# B 밤: 손전등 안은 귀여운 그림, 어둠 속 부분만 진짜 모습
	scene.call("set_night", true)
	(scene.get("player") as Player).flashlight.visible = false
	spot.visible = true
	var quad := MeshInstance3D.new()
	var qm := QuadMesh.new()
	var t_day: Texture2D = tex["day"]
	qm.size = Vector2(t_day.get_width(), t_day.get_height()) * CARD_H / SRC_H
	quad.mesh = qm
	var sm := ShaderMaterial.new()
	sm.shader = load("res://tools/dev/signature_reveal.gdshader")
	sm.set_shader_parameter("tex_day", tex["day"])
	sm.set_shader_parameter("tex_true", tex["true"])
	quad.material_override = sm
	quad.position = Vector3(0, qm.size.y * 0.5, -6.0)
	_mark(quad)
	scene.add_child(quad)
	_aim(Vector3(0, 1.55, -3.6), Vector3(0, 0.95, -6.0))
	spot.spot_angle = 11.0
	sm.set_shader_parameter("cos_out", cos(deg_to_rad(11.0)))
	sm.set_shader_parameter("cos_in", cos(deg_to_rad(9.0)))
	spot.look_at(Vector3(-0.02, 1.33, -6.0), Vector3.UP)
	sm.set_shader_parameter("true_glow", 0.9)
	sm.set_shader_parameter("flash_pos", spot.global_position)
	sm.set_shader_parameter("flash_dir", -spot.global_transform.basis.z)
	await _shot("sig_B_dark_true")
	spot.rotation = Vector3.ZERO
	spot.spot_angle = 24.0
	await _clear()

	# C 밤: 종이 레이어가 벌어짐(머리·몸·다리가 앞뒤로 떨어져 섬)
	var bands: Array = [[0, 330, 1.0, 0.1], [330, 620, 0.5, -0.05], [620, 920, 0.0, 0.0]]
	var base_at := Vector3(0, 0, -6.0)
	for b: Array in bands:
		var s := Sprite3D.new()
		s.texture = tex["day"]
		s.region_enabled = true
		s.region_rect = Rect2(0, b[0], t_day.get_width(), b[1] - b[0])
		s.pixel_size = CARD_H / SRC_H
		s.shaded = true
		s.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
		s.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
		var mid_y: float = (SRC_H - (float(b[0]) + float(b[1])) * 0.5) * CARD_H / SRC_H
		s.position = base_at + Vector3(b[3], mid_y, b[2])
		s.rotation.z = b[3] * 1.5
		_mark(s)
		scene.add_child(s)
	_aim(Vector3(1.05, 1.4, -4.6), Vector3(-0.2, 0.95, -5.6))
	await _shot("sig_C_layers")
	await _clear()

	# D 깜빡일 때마다 작화가 무너지며 다가옴 (빌보드: 늘 나를 봄)
	var steps: Array = [["s1", 12.0], ["s2", 7.5], ["s3", 4.6]]
	var k: int = 1
	for st: Array in steps:
		_mark(_card(tex[st[0]], Vector3(0, 0, -st[1] - 2.0), true))
		_aim(Vector3(0, 1.55, -4.0), Vector3(0, 1.0, -st[1] - 2.0))
		await _shot("sig_D%d_%s" % [k, st[0]])
		await _clear()
		k += 1

## 6초: 낮 등신대 → 밤, 받침만 남음 → 깜빡일 때마다 가까이(작화 붕괴) → 전체 화면 그림
func _video() -> void:
	var fdir: String = dir + "/frames"
	DirAccess.make_dir_recursive_absolute(fdir)
	var frame: int = 0
	var base_pos := Vector3(0.0, 0, -9.0)
	# 1) 낮: 받침 위 등신대 (1초)
	var day: Sprite3D = _mark(_card(tex["day"], base_pos, true))
	_mark(_base(base_pos))
	for i: int in range(30):
		_aim(Vector3(sin(i * 0.05) * 0.03, 1.55, -4.0 - i * 0.01), Vector3(0, 1.0, -9.0))
		frame = await _vframe(fdir, frame)
	# 2) 밤: 받침만 남음 (1초)
	day.queue_free()
	scene.call("set_night", true)
	(scene.get("player") as Player).flashlight.visible = false
	spot.visible = true
	for i: int in range(30):
		_aim(Vector3(sin(i * 0.07) * 0.04, 1.55 + sin(i * 0.2) * 0.01, -4.3), Vector3(0, 0.3, -9.0))
		frame = await _vframe(fdir, frame)
	# 3) 고개를 들면 복도 끝에 서 있음 → 깜빡임마다 가까이
	var steps: Array = [["day", 14.0, 24], ["s1", 10.5, 18], ["s2", 7.0, 16], ["s3", 4.6, 14], ["s3", 3.0, 8]]
	for st: Array in steps:
		var s: Sprite3D = _mark(_card(tex[st[0]], Vector3(0, 0, -st[1] - 2.0), true))
		for i: int in range(st[2]):
			var shake: float = 0.02 if st[0] == "day" else 0.035
			_aim(Vector3(sin(frame * 0.9) * shake, 1.55 + cos(frame * 1.3) * shake * 0.5, -4.3), Vector3(0, 1.1, -st[1] - 2.0))
			frame = await _vframe(fdir, frame)
		# 깜빡임: 손전등 꺼짐 3프레임
		s.queue_free()
		spot.visible = false
		for i: int in range(3):
			frame = await _vframe(fdir, frame)
		spot.visible = true
	# 4) 잡힘: 전체 화면 그림 (화면 앞 0.5m에 "진짜 모습")
	var t: Texture2D = tex["true"]
	var catch_card: Sprite3D = _mark(_card(t, Vector3(0, 0, 0), true))
	catch_card.pixel_size = 2.2 / t.get_height()
	catch_card.offset = Vector2(0, t.get_height() * 0.5)
	catch_card.position = Vector3(0, -0.2, -5.05)
	for i: int in range(20):
		_aim(Vector3(sin(i * 2.1) * 0.05, 1.55 + cos(i * 2.7) * 0.04, -4.3), Vector3(0, 1.55, -5.0))
		frame = await _vframe(fdir, frame)
	spot.visible = false
	catch_card.visible = false
	for i: int in range(15):
		frame = await _vframe(fdir, frame)
	print("frames ", frame)

func _vframe(fdir: String, frame: int) -> int:
	await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png("%s/f_%04d.png" % [fdir, frame])
	return frame + 1
