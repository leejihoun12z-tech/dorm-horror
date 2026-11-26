extends SceneTree
## 마네킹 맞닿는 곳 확대 (낮): godot --path . -s res://tools/dev/char_closeups.gd -- --dir=절대경로
## 머리 끝 뒤 · 머리 끝 옆 · 얼굴 · 목·깃 · 겨드랑이·소매 · 손목 · 치마·다리 · 코트 안

var dir: String = "res://.screenshots"
var cam: Camera3D
var view: int = 0  # --view=1 색만(조명 없음) · 2 회색 모양 + 조명

func _init() -> void:
	for a: String in OS.get_cmdline_user_args():
		if a.begins_with("--dir="):
			dir = a.substr(6)
		elif a.begins_with("--view="):
			view = int(a.substr(7))
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
	root.add_child(scene)
	await process_frame
	(scene.get_node("HUD") as CanvasLayer).visible = false
	cam = Camera3D.new()
	scene.add_child(cam)
	cam.current = true
	var m: Mannequin = scene.get("mannequin")
	m.watcher = cam
	m.set_stage(0)
	if view != 0:
		_set_view(m, view)
	var mp: Vector3 = m.global_position
	# 키 1.55 기준 높이(키 1.0 값 × 1.55). 앞 = +Z
	var shots: Array = [
		["c0_hair_back", Vector3(0, 0.70, 0), 180.0, 0.46],
		["c1_hair_side", Vector3(0, 0.72, 0), 90.0, 0.46],
		["c2_face", Vector3(0, 0.73, 0.05), 0.0, 0.31],
		["c3_neck", Vector3(0, 0.62, 0.08), 25.0, 0.28],
		["c4_armpit", Vector3(0.10, 0.57, 0.05), 35.0, 0.31],
		["c5_wrist", Vector3(0.17, 0.45, 0.06), 20.0, 0.22],
		["c6_legs", Vector3(0, 0.33, 0.06), 20.0, 0.34],
		["c7_coat_in", Vector3(0, 0.40, 0.03), 200.0, 0.46],
	]
	for s: Array in shots:
		var p: Vector3 = s[1]
		var target: Vector3 = mp + Vector3(p.x, p.y * 1.55, p.z * 1.55)
		var a: float = deg_to_rad(s[2])
		cam.projection = Camera3D.PROJECTION_ORTHOGONAL
		cam.size = s[3]
		cam.global_position = target + Vector3(sin(a), 0.15, cos(a)) * 0.9
		cam.look_at(target, Vector3.UP)
		await _shot(s[0])
	quit()

func _set_view(n: Node, v: int) -> void:
	if n is MeshInstance3D:
		var mi: MeshInstance3D = n
		for i: int in range(mi.get_surface_override_material_count()):
			var mat: Material = mi.get_surface_override_material(i)
			if mat is ShaderMaterial:
				(mat as ShaderMaterial).set_shader_parameter("debug_view", v)
		if mi.material_override is ShaderMaterial:
			(mi.material_override as ShaderMaterial).set_shader_parameter("debug_view", v)
	for c: Node in n.get_children():
		_set_view(c, v)
