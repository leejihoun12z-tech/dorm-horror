extends SceneTree
## 화면 한 장: godot --path . -s res://tools/dev/screenshot.gd -- --out=절대경로.png [--door] [--crouch]
##   [--scene=res://찍을씬.tscn] (기본 = 시험 복도)
##   캐릭터 시험 장면(res://game/characters/char_test.tscn)은 [--night] [--expr=이름] [--walk=초] [--far]도 받는다
func _init() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	var out: String = "res://.screenshots/shot.png"
	var scene_path: String = "res://game/world/test_corridor.tscn"
	for a: String in args:
		if a.begins_with("--out="):
			out = a.substr(6)
		elif a.begins_with("--scene="):
			scene_path = a.substr(8)
	var scene: Node = (load(scene_path) as PackedScene).instantiate()
	root.add_child(scene)
	for i: int in range(20):
		await process_frame
	var player: Node3D = scene.find_child("Player", true, false)
	if scene.has_method("apply_shot_args"):
		scene.call("apply_shot_args", args)
	if "--crouch" in args:
		Input.action_press("crouch")
	if "--door" in args:
		player.rotate_y(deg_to_rad(-60.0))
		player.position = Vector3(0.2, 0.05, -2.2)
	for i: int in range(40):
		await physics_frame
	# 진짜 마우스가 움직이면 시선이 돌아가므로, 찍기 직전에 시선을 되돌린다
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	if not "--door" in args:
		player.rotation = Vector3.ZERO
	(player.get_node("Head") as Node3D).rotation = Vector3.ZERO
	await process_frame
	if "--door" in args:
		var look: Node = player.get("_look_target")
		print("look target: ", look, " prompt: ", (scene.find_child("Prompt", true, false) as Label).text)
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(out)
	print("saved ", out)
	quit()
