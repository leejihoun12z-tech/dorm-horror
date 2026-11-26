extends SceneTree
## RiggedCharacter 동작 확인: godot --path . --headless -s res://tools/dev/rigged_character_check.gd
func _init() -> void:
	var c := RiggedCharacter.new()
	c.model_path = "res://assets/characters/mannequin_smart/mannequin_smart.glb"
	c.start_animation = "walk"
	root.add_child(c)
	await process_frame
	print("model ", c.model != null, " anim ", c.anim != null, " playing ", c.anim.current_animation if c.anim else "", " materials ", c._materials.size(), " play(none) ", c.play("none"))
	quit()
