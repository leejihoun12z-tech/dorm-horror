extends SceneTree
## 룩 탐색용 구도 그림 (look-exploration-20261127.md): 기숙사 공간 4곳을 회색 상자로 짓고, 고정 카메라에서
## clay(회색 렌더)·depth(깊이, 가까울수록 흰색)·normal(면 방향)을 찍는다. ComfyUI ControlNet 입력으로 쓴다.
##   godot --path . --rendering-driver vulkan --rendering-method forward_plus --resolution 1344x768 \
##         -s res://tools/look/look_spaces.gd -- --dir=절대경로 [--space=corridor|room|office|stairs]
## 크기는 실제 한국 대학 기숙사 비율(대략). 화풍은 이 구도 위에 AI가 입히므로 모양만 맞으면 된다.

const SPACES: Array[String] = ["corridor", "room", "office", "stairs"]
const MODES: Array[String] = ["clay", "depth", "normal"]
const FAR: float = 16.0

var dir: String = "res://.screenshots/look"
var only_space: String = ""
var mode: String = "clay"
var root3d: Node3D
var cam: Camera3D
var shaders: Dictionary = {}

func _init() -> void:
	for a: String in OS.get_cmdline_user_args():
		if a.begins_with("--dir="):
			dir = a.substr(6)
		elif a.begins_with("--space="):
			only_space = a.substr(8)
	DirAccess.make_dir_recursive_absolute(dir)
	_make_shaders()
	_run()

func _run() -> void:
	for sp: String in SPACES:
		if only_space != "" and sp != only_space:
			continue
		for m: String in MODES:
			mode = m
			await _build(sp)
			for i: int in range(30 if m == "clay" else 4):
				await process_frame
			await RenderingServer.frame_post_draw
			root.get_texture().get_image().save_png("%s/%s_%s.png" % [dir, sp, m])
			print("saved ", sp, "_", m)
	quit()

func _make_shaders() -> void:
	var d := Shader.new()
	d.code = """shader_type spatial;
render_mode unshaded, cull_disabled;
uniform float far_d = 16.0;
void fragment() {
	float z = -VERTEX.z;
	float v = 1.0 - clamp(z / far_d, 0.0, 1.0);
	ALBEDO = vec3(pow(v, 1.6));
}"""
	shaders.depth = d
	var n := Shader.new()
	n.code = """shader_type spatial;
render_mode unshaded, cull_disabled;
void fragment() {
	ALBEDO = NORMAL * 0.5 + 0.5;
}"""
	shaders.normal = n

func _mat(c: Color) -> Material:
	if mode == "clay":
		var m := StandardMaterial3D.new()
		m.albedo_color = Color(0.78, 0.78, 0.76).lerp(c, 0.25)
		m.roughness = 0.85
		return m
	var sm := ShaderMaterial.new()
	sm.shader = shaders[mode]
	if mode == "depth":
		sm.set_shader_parameter("far_d", FAR)
	return sm

func _box(size: Vector3, at: Vector3, c: Color = Color(0.8, 0.8, 0.8), rot: Vector3 = Vector3.ZERO) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	var b := BoxMesh.new()
	b.size = size
	mi.mesh = b
	mi.material_override = _mat(c)
	mi.position = at
	mi.rotation_degrees = rot
	root3d.add_child(mi)
	return mi

func _cyl(r: float, h: float, at: Vector3, c: Color, rot: Vector3 = Vector3.ZERO) -> void:
	var mi := MeshInstance3D.new()
	var m := CylinderMesh.new()
	m.top_radius = r
	m.bottom_radius = r
	m.height = h
	mi.mesh = m
	mi.material_override = _mat(c)
	mi.position = at
	mi.rotation_degrees = rot
	root3d.add_child(mi)

func _build(sp: String) -> void:
	if root3d != null:
		root3d.queue_free()
		await process_frame
	root3d = Node3D.new()
	root.add_child(root3d)
	cam = Camera3D.new()
	cam.fov = 68.0
	root3d.add_child(cam)
	cam.current = true
	match sp:
		"corridor":
			_corridor()
		"room":
			_room()
		"office":
			_office()
		"stairs":
			_stairs()
	var we := WorldEnvironment.new()
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.85, 0.85, 0.85) if mode == "clay" else Color(0, 0, 0)
	env.tonemap_mode = Environment.TONE_MAPPER_LINEAR
	if mode == "clay":
		env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
		env.ambient_light_color = Color(1, 1, 1)
		env.ambient_light_energy = 0.45
		env.ssao_enabled = true
		env.ssao_intensity = 2.5
		env.sdfgi_enabled = true
		var sun := DirectionalLight3D.new()
		sun.rotation_degrees = Vector3(-55, 35, 0)
		sun.light_energy = 0.35
		root3d.add_child(sun)
	we.environment = env
	root3d.add_child(we)

func _light(at: Vector3, e: float = 1.2, r: float = 6.0) -> void:
	if mode != "clay":
		return
	var o := OmniLight3D.new()
	o.position = at
	o.light_energy = e
	o.omni_range = r
	o.shadow_enabled = true
	root3d.add_child(o)

# ---------------------------------------------------------------- 복도
func _corridor() -> void:
	var w: float = 2.4
	var h: float = 2.6
	var L: float = 20.0
	var hw: float = w * 0.5
	var wall := Color(0.92, 0.9, 0.85)
	_box(Vector3(w + 0.4, 0.1, L), Vector3(0, -0.05, -L * 0.5 + 1.0), Color(0.7, 0.7, 0.68))
	_box(Vector3(w + 0.4, 0.1, L), Vector3(0, h + 0.05, -L * 0.5 + 1.0), Color(0.95, 0.95, 0.95))
	for s: float in [-1.0, 1.0]:
		_box(Vector3(0.2, h, L), Vector3(s * (hw + 0.1), h * 0.5, -L * 0.5 + 1.0), wall)
		_box(Vector3(0.03, 0.1, L), Vector3(s * (hw - 0.015), 0.05, -L * 0.5 + 1.0), Color(0.3, 0.3, 0.3))  # 걸레받이
	_box(Vector3(w, h, 0.2), Vector3(0, h * 0.5, 1.2), wall)
	# 끝: 방화문(양문) + 위 창
	var ez: float = -L + 1.0
	_box(Vector3(w, h, 0.2), Vector3(0, h * 0.5, ez - 0.1), wall)
	for s: float in [-1.0, 1.0]:
		_box(Vector3(0.88, 2.05, 0.06), Vector3(s * 0.45, 1.025, ez + 0.03), Color(0.6, 0.6, 0.62))
		_box(Vector3(0.25, 0.5, 0.02), Vector3(s * 0.45, 1.45, ez + 0.07), Color(0.4, 0.5, 0.6))  # 문 유리
		_box(Vector3(0.6, 0.04, 0.05), Vector3(s * 0.45, 1.0, ez + 0.09), Color(0.7, 0.7, 0.7))  # 밀대
	_box(Vector3(1.6, 0.4, 0.03), Vector3(0, 2.35, ez + 0.02), Color(0.5, 0.6, 0.7))
	_box(Vector3(0.4, 0.15, 0.05), Vector3(0, 2.15, ez + 0.05), Color(0.2, 0.8, 0.4))  # 비상구 표시
	# 방문 (엇갈려 배치) + 번호판 + 신발장
	var z: float = -1.5
	var i: int = 0
	while z > ez + 2.0:
		for s: float in [-1.0, 1.0]:
			var dz: float = z - (0.0 if s < 0 else 1.8)
			if dz < ez + 1.5:
				continue
			var x: float = s * (hw - 0.02)
			_box(Vector3(0.06, 2.1, 0.95), Vector3(x, 1.05, dz), Color(0.62, 0.45, 0.3))
			_box(Vector3(0.08, 0.06, 1.07), Vector3(x, 2.13, dz), Color(0.35, 0.3, 0.27))
			for e: float in [-1.0, 1.0]:
				_box(Vector3(0.08, 2.16, 0.06), Vector3(x, 1.08, dz + e * 0.5), Color(0.35, 0.3, 0.27))
			_cyl(0.025, 0.08, Vector3(x - s * 0.06, 1.0, dz + 0.35), Color(0.8, 0.8, 0.8), Vector3(0, 0, 90))
			_box(Vector3(0.02, 0.12, 0.22), Vector3(x - s * 0.02, 2.35, dz), Color(0.95, 0.95, 0.9))  # 호실 번호판
			if i % 2 == 0:
				_box(Vector3(0.35, 1.0, 0.8), Vector3(s * (hw - 0.2), 0.5, dz - 1.0), Color(0.75, 0.7, 0.62))  # 신발장
			i += 1
		z -= 3.6
	# 소품
	_box(Vector3(0.18, 0.7, 0.45), Vector3(-hw + 0.1, 1.2, -6.2), Color(0.8, 0.15, 0.1))  # 소화전함
	_box(Vector3(0.03, 0.8, 1.3), Vector3(hw - 0.02, 1.5, -8.2), Color(0.65, 0.5, 0.32))  # 게시판
	for k: int in range(5):
		_box(Vector3(0.005, 0.28, 0.2), Vector3(hw - 0.04, 1.45 + (k % 2) * 0.2, -8.7 + k * 0.24), Color(1, 1, 1), Vector3(k * 3.0 - 6.0, 0, 0))
	_cyl(0.2, 0.6, Vector3(-hw + 0.3, 0.3, -11.0), Color(0.3, 0.5, 0.8))  # 분리수거함
	_cyl(0.2, 0.6, Vector3(-hw + 0.75, 0.3, -11.0), Color(0.3, 0.7, 0.4))
	var lz: float = -0.5
	while lz > ez + 1.0:
		_box(Vector3(0.3, 0.05, 1.2), Vector3(0, h - 0.025, lz), Color(1, 1, 1))
		_light(Vector3(0, h - 0.3, lz), 1.0, 5.0)
		lz -= 3.0
	cam.look_at_from_position(Vector3(-0.35, 1.6, 0.6), Vector3(0.15, 1.3, -10.0), Vector3.UP)

# ---------------------------------------------------------------- 2인실
func _room() -> void:
	var w: float = 3.4
	var d: float = 5.2
	var h: float = 2.5
	var hw: float = w * 0.5
	var wall := Color(0.93, 0.92, 0.88)
	_box(Vector3(w, 0.1, d), Vector3(0, -0.05, -d * 0.5), Color(0.72, 0.6, 0.45))
	_box(Vector3(w, 0.1, d), Vector3(0, h + 0.05, -d * 0.5), Color(0.96, 0.96, 0.96))
	for s: float in [-1.0, 1.0]:
		_box(Vector3(0.2, h, d), Vector3(s * (hw + 0.1), h * 0.5, -d * 0.5), wall)
	# 뒷벽 + 창문
	_box(Vector3(w, 0.85, 0.2), Vector3(0, 0.425, -d - 0.1), wall)
	_box(Vector3(w, 0.35, 0.2), Vector3(0, h - 0.175, -d - 0.1), wall)
	for s: float in [-1.0, 1.0]:
		_box(Vector3(0.8, 1.3, 0.2), Vector3(s * (hw - 0.4), 1.5, -d - 0.1), wall)
	_box(Vector3(1.8, 1.3, 0.02), Vector3(0, 1.5, -d - 0.15), Color(0.7, 0.8, 0.9))
	_box(Vector3(0.05, 1.3, 0.06), Vector3(0, 1.5, -d - 0.05), Color(0.85, 0.85, 0.85))
	_box(Vector3(2.0, 0.06, 0.25), Vector3(0, 0.86, -d + 0.08), Color(0.85, 0.85, 0.85))  # 창턱
	for s: float in [-1.0, 1.0]:
		_box(Vector3(0.5, 1.6, 0.06), Vector3(s * 1.05, 1.45, -d + 0.15), Color(0.85, 0.8, 0.7))  # 커튼
	_box(Vector3(w, h, 0.2), Vector3(0, h * 0.5, 0.6), wall)
	for s: float in [-1.0, 1.0]:
		var x: float = s * (hw - 0.5)
		# 침대 (창 쪽)
		_box(Vector3(0.95, 0.35, 2.0), Vector3(x, 0.175, -d + 1.05), Color(0.6, 0.45, 0.3))
		_box(Vector3(0.9, 0.18, 1.95), Vector3(x, 0.44, -d + 1.05), Color(0.95, 0.95, 0.95))
		_box(Vector3(0.55, 0.12, 0.35), Vector3(x, 0.59, -d + 0.3), Color(0.9, 0.9, 0.95))
		_box(Vector3(0.92, 0.1, 1.2), Vector3(x, 0.56, -d + 1.5), Color(0.6, 0.7, 0.85))  # 이불
		_box(Vector3(0.95, 0.8, 0.05), Vector3(x, 0.4, -d + 2.06), Color(0.6, 0.45, 0.3))  # 침대 발판
		# 책상 + 선반 + 의자
		var dx: float = s * (hw - 0.3)
		_box(Vector3(0.6, 0.04, 1.2), Vector3(dx, 0.75, -2.3), Color(0.7, 0.55, 0.38))
		_box(Vector3(0.6, 0.73, 0.04), Vector3(dx, 0.365, -1.72), Color(0.7, 0.55, 0.38))
		_box(Vector3(0.6, 0.73, 0.04), Vector3(dx, 0.365, -2.88), Color(0.7, 0.55, 0.38))
		_box(Vector3(0.3, 0.6, 1.2), Vector3(s * (hw - 0.15), 1.55, -2.3), Color(0.7, 0.55, 0.38))  # 선반장
		_box(Vector3(0.28, 0.02, 1.15), Vector3(s * (hw - 0.15), 1.55, -2.3), Color(0.6, 0.45, 0.3))
		for b: int in range(6):
			_box(Vector3(0.2, 0.22, 0.05), Vector3(s * (hw - 0.15), 1.68, -2.75 + b * 0.09), Color(0.3 + b * 0.1, 0.4, 0.6 - b * 0.05))
		_box(Vector3(0.35, 0.25, 0.04), Vector3(s * (hw - 0.35), 0.92, -2.3), Color(0.15, 0.15, 0.17), Vector3(0, s * -90, 0))  # 노트북 화면
		_box(Vector3(0.45, 0.45, 0.45), Vector3(s * (hw - 0.75), 0.45, -2.2), Color(0.3, 0.3, 0.35))  # 의자
		_box(Vector3(0.45, 0.5, 0.06), Vector3(s * (hw - 0.98), 0.9, -2.2), Color(0.3, 0.3, 0.35), Vector3(0, 90, 0))
		_box(Vector3(0.45, 0.5, 0.45), Vector3(dx, 0.25, -1.95), Color(0.9, 0.9, 0.9))  # 작은 냉장고
		# 옷장 (문 쪽)
		_box(Vector3(0.6, 2.1, 0.9), Vector3(s * (hw - 0.3), 1.05, -0.6), Color(0.75, 0.65, 0.5))
		_box(Vector3(0.02, 2.0, 0.02), Vector3(s * (hw - 0.61), 1.05, -0.6), Color(0.4, 0.35, 0.3))
	_box(Vector3(1.4, 0.01, 1.0), Vector3(0, 0.005, -2.6), Color(0.8, 0.6, 0.6))  # 러그
	_box(Vector3(0.6, 0.05, 0.6), Vector3(0, h - 0.025, -2.5), Color(1, 1, 1))
	_light(Vector3(0, h - 0.4, -2.5), 1.6, 6.0)
	_light(Vector3(0, 1.6, -d + 0.3), 1.0, 4.0)
	cam.look_at_from_position(Vector3(0.25, 1.55, 0.35), Vector3(-0.1, 1.1, -d), Vector3.UP)

# ---------------------------------------------------------------- 사감실
func _office() -> void:
	var w: float = 4.0
	var d: float = 4.6
	var h: float = 2.5
	var hw: float = w * 0.5
	var wall := Color(0.9, 0.9, 0.86)
	_box(Vector3(w, 0.1, d), Vector3(0, -0.05, -d * 0.5), Color(0.6, 0.62, 0.6))
	_box(Vector3(w, 0.1, d), Vector3(0, h + 0.05, -d * 0.5), Color(0.96, 0.96, 0.96))
	for s: float in [-1.0, 1.0]:
		_box(Vector3(0.2, h, d), Vector3(s * (hw + 0.1), h * 0.5, -d * 0.5), wall)
	_box(Vector3(w, h, 0.2), Vector3(0, h * 0.5, 0.6), wall)
	# 앞벽: 창구(왼쪽) + 출입문(오른쪽)
	var fz: float = -d
	_box(Vector3(2.4, 1.0, 0.2), Vector3(-0.8, 0.5, fz - 0.1), wall)
	_box(Vector3(2.4, 0.5, 0.2), Vector3(-0.8, h - 0.25, fz - 0.1), wall)
	_box(Vector3(2.2, 1.0, 0.02), Vector3(-0.8, 1.5, fz - 0.12), Color(0.75, 0.85, 0.9))  # 창구 유리
	_box(Vector3(0.4, 0.15, 0.03), Vector3(-0.8, 1.07, fz - 0.1), Color(0.2, 0.2, 0.2))  # 창구 구멍
	_box(Vector3(2.4, 0.05, 0.45), Vector3(-0.8, 1.0, fz + 0.1), Color(0.65, 0.5, 0.35))  # 창구 선반
	_box(Vector3(0.3, h, 0.2), Vector3(0.55, h * 0.5, fz - 0.1), wall)
	_box(Vector3(0.9, 2.1, 0.05), Vector3(1.15, 1.05, fz - 0.05), Color(0.6, 0.45, 0.3))
	_box(Vector3(0.9, 0.4, 0.2), Vector3(1.15, h - 0.2, fz - 0.1), wall)
	_box(Vector3(0.25, h, 0.2), Vector3(1.75, h * 0.5, fz - 0.1), wall)
	# 책상 (창구를 향함) + 모니터 + CCTV
	_box(Vector3(2.0, 0.04, 0.75), Vector3(-0.8, 0.75, fz + 0.9), Color(0.7, 0.6, 0.45))
	_box(Vector3(0.04, 0.73, 0.7), Vector3(-1.78, 0.365, fz + 0.9), Color(0.7, 0.6, 0.45))
	_box(Vector3(0.04, 0.73, 0.7), Vector3(0.18, 0.365, fz + 0.9), Color(0.7, 0.6, 0.45))
	_box(Vector3(0.55, 0.35, 0.04), Vector3(-1.1, 1.0, fz + 0.75), Color(0.15, 0.15, 0.18))
	_box(Vector3(0.45, 0.02, 0.15), Vector3(-1.1, 0.78, fz + 1.05), Color(0.3, 0.3, 0.3))
	for k: int in range(4):
		_box(Vector3(0.32, 0.22, 0.04), Vector3(-0.35 + (k % 2) * 0.34, 0.92 + (k / 2) * 0.24, fz + 0.72), Color(0.1, 0.2, 0.15))
	_box(Vector3(0.55, 0.9, 0.55), Vector3(-1.1, 0.45, fz + 1.6), Color(0.25, 0.25, 0.28))  # 의자
	# 왼벽: 열쇠함 + 화이트보드
	_box(Vector3(0.08, 0.8, 0.6), Vector3(-hw + 0.04, 1.5, -2.2), Color(0.7, 0.7, 0.72))
	for r: int in range(5):
		for c: int in range(4):
			_box(Vector3(0.03, 0.06, 0.04), Vector3(-hw + 0.1, 1.25 + r * 0.13, -2.4 + c * 0.13), Color(0.85, 0.75, 0.3))
	_box(Vector3(0.03, 0.9, 1.4), Vector3(-hw + 0.02, 1.55, -0.9), Color(0.97, 0.97, 0.97))
	# 오른벽: 서류장 + 정수기 + 소파
	for k: int in range(2):
		_box(Vector3(0.5, 1.3, 0.45), Vector3(hw - 0.25, 0.65, -2.6 + k * 0.48), Color(0.6, 0.62, 0.65))
	_box(Vector3(0.35, 1.1, 0.35), Vector3(hw - 0.2, 0.55, -1.6), Color(0.9, 0.9, 0.92))
	_box(Vector3(0.7, 0.45, 1.6), Vector3(hw - 0.35, 0.225, -0.3), Color(0.45, 0.35, 0.3))
	_box(Vector3(0.2, 0.5, 1.6), Vector3(hw - 0.1, 0.55, -0.3), Color(0.45, 0.35, 0.3))
	_cyl(0.16, 0.04, Vector3(0.0, 2.1, fz + 0.02), Color(0.95, 0.95, 0.95), Vector3(90, 0, 0))  # 벽시계
	_box(Vector3(0.6, 0.05, 1.2), Vector3(0, h - 0.025, -2.3), Color(1, 1, 1))
	_light(Vector3(0, h - 0.4, -2.3), 1.6, 6.0)
	_light(Vector3(-0.8, 1.6, fz - 0.6), 0.8, 3.0)
	cam.look_at_from_position(Vector3(1.2, 1.6, 0.3), Vector3(-0.7, 1.1, -d), Vector3.UP)

# ---------------------------------------------------------------- 계단참
func _stairs() -> void:
	var fw: float = 1.3  # 한 줄 계단 폭
	var rise: float = 0.17
	var run: float = 0.28
	var n: int = 10
	var wall := Color(0.88, 0.88, 0.85)
	var step_c := Color(0.7, 0.7, 0.68)
	var flight_len: float = n * run
	var land_y: float = n * rise
	var land_z: float = -flight_len - 0.3
	_box(Vector3(fw * 2 + 0.2, 0.1, 2.5), Vector3(0, -0.05, 1.0), step_c)  # 아래층 바닥
	# 오른쪽: 올라가는 계단 (카메라에서 멀어짐)
	for i: int in range(n):
		_box(Vector3(fw, rise * (i + 1), run), Vector3(fw * 0.5 + 0.05, rise * (i + 1) * 0.5, -i * run - run * 0.5), step_c)
	# 계단참
	_box(Vector3(fw * 2 + 0.1, land_y, 1.6), Vector3(0, land_y * 0.5, land_z - 0.8 + 0.3), step_c)
	# 왼쪽: 계단참에서 다시 카메라 쪽으로 올라가는 계단 (위층)
	for i: int in range(n):
		var y: float = land_y + rise * (i + 1)
		_box(Vector3(fw, 0.22, run), Vector3(-fw * 0.5 - 0.05, y - 0.11, land_z + 0.3 + i * run + run * 0.5), step_c)
		_box(Vector3(fw, 0.06, run * 1.02), Vector3(-fw * 0.5 - 0.05, y - 0.25, land_z + 0.3 + i * run + run * 0.5), step_c)
	# 난간: 오른쪽 계단 안쪽 가장자리를 따라 기운 손잡이 + 세로 살 (계단 사이는 뚫림)
	var ang: float = rad_to_deg(atan(rise / run))
	var rail_len: float = sqrt(flight_len * flight_len + land_y * land_y)
	_box(Vector3(0.06, 0.05, rail_len), Vector3(0.08, land_y * 0.5 + 0.9, -flight_len * 0.5), Color(0.4, 0.4, 0.42), Vector3(ang, 0, 0))
	for i: int in range(0, n, 2):
		var sy: float = rise * (i + 1)
		_box(Vector3(0.03, 0.9, 0.03), Vector3(0.08, sy + 0.45, -i * run - run * 0.5), Color(0.4, 0.4, 0.42))
	_box(Vector3(0.06, 0.05, rail_len), Vector3(-0.08, land_y * 1.5 + 0.9, -flight_len * 0.5), Color(0.4, 0.4, 0.42), Vector3(-ang, 0, 0))
	_box(Vector3(fw * 2 + 0.3, 0.1, 6.5), Vector3(0, -0.05, -1.6), step_c)  # 아래층 바닥 전체
	# 벽
	var H: float = land_y * 2 + 2.8
	_box(Vector3(0.2, H, 6.0), Vector3(fw + 0.15, H * 0.5 - 0.5, -1.4), wall)
	_box(Vector3(0.2, H, 6.0), Vector3(-fw - 0.15, H * 0.5 - 0.5, -1.4), wall)
	var bz: float = land_z - 0.8 - 0.4
	_box(Vector3(fw * 2 + 0.5, H, 0.2), Vector3(0, H * 0.5 - 0.5, bz), wall)
	_box(Vector3(1.2, 1.3, 0.02), Vector3(0, land_y + 1.6, bz + 0.11), Color(0.75, 0.85, 0.95))  # 계단참 창
	_box(Vector3(1.3, 0.06, 0.2), Vector3(0, land_y + 0.92, bz + 0.15), Color(0.85, 0.85, 0.85))
	_box(Vector3(0.5, 0.35, 0.02), Vector3(fw + 0.04, land_y + 1.6, land_z + 0.2), Color(0.2, 0.3, 0.6), Vector3(0, -90, 0))  # 층 표시 3F
	# 아래층 방화문 (오른벽)
	_box(Vector3(0.06, 2.1, 0.95), Vector3(fw + 0.03, 1.05, 1.3), Color(0.55, 0.55, 0.58))
	_box(Vector3(fw * 2 + 0.5, 0.1, 6.0), Vector3(0, H - 0.5, -1.4), Color(0.95, 0.95, 0.95))
	_light(Vector3(0, land_y + 2.2, land_z - 0.6), 1.6, 6.0)
	_light(Vector3(0.6, 2.4, 0.5), 0.8, 4.0)
	cam.look_at_from_position(Vector3(0.7, 1.6, 1.7), Vector3(0.0, 2.0, -3.6), Vector3.UP)
