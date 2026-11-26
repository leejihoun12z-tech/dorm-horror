extends SceneTree
## Tripo가 색·뼈대·걷기까지 만든 모델을 그대로 복도에 세워 찍는다.
## godot --path . -s res://tools/dev/rigged_shots.gd -- --dir=절대경로 [--count=10] [--raw=1] [--model=res://...glb]
## --raw=1: 재질을 안 바꾸고 glb 그대로. 기본: 텍스처는 그대로, 빛만 평평한 툰 셰이더(외곽선 없음)

var MODEL: String = "res://assets/characters/mannequin_rigged/mannequin_rigged.glb"
var dir: String = "res://.screenshots"
var count: int = 1
var raw: bool = false
var tex_override: String = ""  # --tex=res://... 텍스처만 바꿔 봄
var cam: Camera3D

func _init() -> void:
	for a: String in OS.get_cmdline_user_args():
		if a.begins_with("--dir="):
			dir = a.substr(6)
		elif a.begins_with("--count="):
			count = int(a.substr(8))
		elif a.begins_with("--tex="):
			tex_override = a.substr(6)
		elif a.begins_with("--model="):
			MODEL = a.substr(8)
		elif a.begins_with("--raw="):
			raw = a.substr(6) == "1"
	DirAccess.make_dir_recursive_absolute(dir)
	_run()

func _shot(name: String) -> void:
	for i: int in range(4):
		await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(dir + "/" + name + ".png")
	print("saved ", name)

func _restyle(n: Node) -> void:
	if n is MeshInstance3D:
		var mi: MeshInstance3D = n
		for s: int in range(mi.mesh.get_surface_count()):
			var m: Material = mi.mesh.surface_get_material(s)
			var tex: Texture2D = (m as BaseMaterial3D).albedo_texture if m is BaseMaterial3D else null
			if tex_override != "":
				tex = ImageTexture.create_from_image(Image.load_from_file(ProjectSettings.globalize_path(tex_override)))
				(tex as ImageTexture).get_image().generate_mipmaps()
			var sm := ShaderMaterial.new()
			sm.shader = load("res://tools/dev/char_toon_flat_test.gdshader")
			sm.set_shader_parameter("base_color", Color.WHITE)
			sm.set_shader_parameter("roughness_value", 1.0)
			sm.set_shader_parameter("specular_value", 0.0)
			sm.set_shader_parameter("use_tex", tex != null)
			sm.set_shader_parameter("albedo_tex", tex)
			mi.set_surface_override_material(s, sm)
	for c: Node in n.get_children():
		_restyle(c)

func _find_anim(n: Node) -> AnimationPlayer:
	if n is AnimationPlayer:
		return n
	for c: Node in n.get_children():
		var r: AnimationPlayer = _find_anim(c)
		if r != null:
			return r
	return null

func _run() -> void:
	var scene: Node3D = (load("res://game/world/test_corridor.tscn") as PackedScene).instantiate()
	root.add_child(scene)
	await process_frame
	(scene.get_node("HUD") as CanvasLayer).visible = false
	var old: Node3D = scene.get("mannequin")
	var mp: Vector3 = old.global_position
	old.visible = false
	cam = Camera3D.new()
	scene.add_child(cam)
	cam.current = true
	var players: Array[AnimationPlayer] = []
	var first: Node3D
	for i: int in range(count):
		var inst: Node3D = (load(MODEL) as PackedScene).instantiate()
		scene.add_child(inst)
		inst.global_position = mp + Vector3(((i % 2) * 2 - 1) * 0.45 * float(mini(i, 1)), 0.0, -float((i + 1) / 2) * 0.9)
		inst.scale = Vector3.ONE * 1.55
		if not raw:
			_restyle(inst)
		var ap: AnimationPlayer = _find_anim(inst)
		if ap != null:
			players.append(ap)
		if i == 0:
			first = inst
	if players.size() > 0:
		print("animations: ", players[0].get_animation_list())
	for ap: AnimationPlayer in players:
		var names: PackedStringArray = ap.get_animation_list()
		if names.size() > 0:
			var an: Animation = ap.get_animation(names[names.size() - 1])
			an.loop_mode = Animation.LOOP_LINEAR
			# 제자리 걷기: 엉덩이 뼈의 이동 트랙을 뺌(이동은 게임 코드가 함)
			for t: int in range(an.get_track_count() - 1, -1, -1):
				if an.track_get_type(t) == Animation.TYPE_POSITION_3D and String(an.track_get_path(t)).to_lower().contains("hips"):
					an.remove_track(t)
			ap.play(names[names.size() - 1])
	if count > 1:
		cam.fov = 75.0
		cam.global_position = mp + Vector3(0.0, 1.5, 2.2)
		cam.look_at(mp + Vector3(0.0, 0.9, -2.0), Vector3.UP)
		for i: int in range(60):
			await process_frame
		var t0: int = Time.get_ticks_usec()
		for i: int in range(240):
			await process_frame
		var dt: float = float(Time.get_ticks_usec() - t0) / 1e6
		print("FPS count=%d : %.1f" % [count, 240.0 / dt])
		await _shot("crowd_%d" % count)
		quit()
		return
	# 실제 거리
	for dist: float in [1.2, 2.5]:
		cam.projection = Camera3D.PROJECTION_PERSPECTIVE
		cam.fov = 75.0
		cam.global_position = mp + Vector3(0.0, 1.5, dist)
		cam.look_at(mp + Vector3(0.0, 1.05, 0.0), Vector3.UP)
		await _shot("d%02d" % int(dist * 10.0))
	# 걷기 6장 (옆 3/4)
	cam.global_position = mp + Vector3(1.3, 1.1, 1.8)
	cam.look_at(mp + Vector3(0.0, 0.8, 0.0), Vector3.UP)
	cam.fov = 45.0
	for k: int in range(6):
		for i: int in range(8):
			await process_frame
		await _shot("walk_%d" % k)
	# 확대 (정사영): 얼굴, 가슴, 무릎, 머리 뒤
	for ap: AnimationPlayer in players:
		ap.play("RESET") if ap.has_animation("RESET") else ap.seek(0.0, true)
		ap.pause()
	cam.projection = Camera3D.PROJECTION_ORTHOGONAL
	var shots: Array = [["c_face", Vector3(0, 0.73, 0.05), 0.0, 0.31], ["c_chest", Vector3(0, 0.62, 0.08), 25.0, 0.28], ["c_knee", Vector3(0, 0.30, 0.06), 20.0, 0.30], ["c_hairback", Vector3(0, 0.70, 0), 180.0, 0.46], ["c_sleeve", Vector3(0.14, 0.50, 0.05), 30.0, 0.26]]
	for s: Array in shots:
		var p: Vector3 = s[1]
		var target: Vector3 = mp + Vector3(p.x, p.y, p.z) * 1.55
		var a: float = deg_to_rad(s[2])
		cam.size = s[3]
		cam.global_position = target + Vector3(sin(a), 0.15, cos(a)) * 0.9
		cam.look_at(target, Vector3.UP)
		await _shot(s[0])
	quit()
