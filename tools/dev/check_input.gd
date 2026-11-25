extends SceneTree
## 입력 설정 확인: godot --headless --path . -s res://tools/dev/check_input.gd
func _init() -> void:
	for action: StringName in ["move_forward", "move_back", "move_left", "move_right", "jump", "crouch", "interact", "flashlight", "pause"]:
		var names: PackedStringArray = []
		for ev: InputEvent in InputMap.action_get_events(action):
			names.append(ev.as_text())
		print(action, " = ", ", ".join(names))
	quit()
