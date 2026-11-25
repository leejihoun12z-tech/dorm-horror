extends SceneTree
## 화면 한 장: godot --path . -s res://tools/dev/screenshot.gd -- --out=절대경로.png [--door] [--crouch]
func _init() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	var out: String = "res://.screenshots/shot.png"
	for a: String in args:
		if a.begins_with("--out="):
			out = a.substr(6)
	var scene: Node = (load("res://game/world/test_corridor.tscn") as PackedScene).instantiate()
	root.add_child(scene)
	for i: int in range(20):
		await process_frame
	var player: Node3D = scene.get_node("Player")
	if "--crouch" in args:
		Input.action_press("crouch")
	if "--door" in args:
		player.rotate_y(deg_to_rad(-60.0))
		player.position = Vector3(0.2, 0.05, -2.2)
	for i: int in range(40):
		await physics_frame
	if "--door" in args:
		var look: Node = player.get("_look_target")
		print("look target: ", look, " prompt: ", scene.get_node("HUD/Prompt").text)
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(out)
	print("saved ", out)
	quit()
