extends SceneTree
## 배경 스타일 3종 비교 (env-style-direction): 같은 기숙사 복도를 ① 극사실 ② 데포르메 ③ 단순 형태로, 낮·밤, 종이인형 카드와 함께 찍는다.
##   godot --path . --rendering-driver vulkan --rendering-method forward_plus --resolution 1280x720 \
##         -s res://tools/dev/style3_test.gd -- --dir=절대경로 [--style=real|deform|simple] [--time=day|night]
## 재질: .screenshots/style3/tex/ (Poly Haven CC0, git 제외). 종이인형 카드: .screenshots/paper_fx/ (make_paper_cards.py).
## 조명: 시험이라 실시간 GI(SDFGI). 실제 게임은 라이트맵 굽기 예정. 그래픽카드 없는 곳에서는 lavapipe로 느리게 돈다.

const TEX: String = "res://.screenshots/style3/tex/"
const LEN: float = 16.0

var dir: String = "res://.screenshots"
var only_style: String = ""
var only_time: String = ""
var root3d: Node3D
var cam: Camera3D
var env: Environment
var cam_attr: CameraAttributesPractical
var mats: Dictionary = {}
var S: Dictionary = {}  # 지금 스타일 값
var style_name: String = ""
var night: bool = false
var flashlight: SpotLight3D

const STYLES: Dictionary = {
	"real": {"w": 2.2, "h": 2.5, "wall_t": 0.15, "door_h": 2.05, "door_w": 0.9, "handle": 1.0, "bevel": 0.0, "tex_scale": 1.0, "tilt": 0.0, "textured": true, "lowres": false},
	"deform": {"w": 2.7, "h": 2.9, "wall_t": 0.3, "door_h": 2.35, "door_w": 1.05, "handle": 2.0, "bevel": 0.08, "tex_scale": 0.45, "tilt": 2.0, "textured": true, "lowres": false},
	"simple": {"w": 2.4, "h": 2.6, "wall_t": 0.2, "door_h": 2.15, "door_w": 0.95, "handle": 1.2, "bevel": 0.0, "tex_scale": 1.0, "tilt": 0.0, "textured": false, "lowres": true, "lowres_scale": 0.3},
}

func _init() -> void:
	for a: String in OS.get_cmdline_user_args():
		if a.begins_with("--dir="):
			dir = a.substr(6)
		elif a.begins_with("--style="):
			only_style = a.substr(8)
		elif a.begins_with("--time="):
			only_time = a.substr(7)
	DirAccess.make_dir_recursive_absolute(dir)
	_run()

func _run() -> void:
	for st: String in ["real", "deform", "simple"]:
		if only_style != "" and st != only_style:
			continue
		for t: String in ["day", "night"]:
			if only_time != "" and t != only_time:
				continue
			await _build(st, t == "night")
			for i: int in range(40):  # GI·안개가 자리 잡을 시간
				await process_frame
			await _shot("%s_%s_a" % [st, t])
			_cam_b()
			for i: int in range(25):
				await process_frame
			await _shot("%s_%s_b" % [st, t])
	quit()

func _shot(name: String) -> void:
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(dir + "/" + name + ".png")
	print("saved ", name)

# ---------------------------------------------------------------- 재질
func _tex(n: String) -> Texture2D:
	var p: String = ProjectSettings.globalize_path(TEX + n + ".jpg")
	if not FileAccess.file_exists(p):
		return null
	var img := Image.load_from_file(p)
	img.generate_mipmaps()
	return ImageTexture.create_from_image(img)

func _pbr(name: String, tint: Color, uv: float, rough_mul: float = 1.0) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = tint
	if S.textured:
		m.albedo_texture = _tex(name + "_diff")
		m.normal_enabled = true
		m.normal_texture = _tex(name + "_nor")
		m.roughness_texture = _tex(name + "_rough")
		m.roughness = rough_mul
		m.ao_enabled = true
		m.ao_texture = _tex(name + "_ao")
		m.uv1_triplanar = true
		m.uv1_world_triplanar = true
		m.uv1_scale = Vector3.ONE * uv * S.tex_scale
	else:
		m.roughness = 0.85
	return m

func _flat(c: Color, rough: float = 0.8, emit: float = 0.0) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = c
	m.roughness = rough
	if emit > 0.0:
		m.emission_enabled = true
		m.emission = c
		m.emission_energy_multiplier = emit
	return m

func _make_mats() -> void:
	var simple: bool = not S.textured
	mats.floor = _pbr("terrazzo_tiles", Color(0.85, 0.85, 0.85) if not simple else Color(0.62, 0.6, 0.56), 0.5, 0.8)
	mats.wall = _pbr("painted_plaster_wall", Color(0.96, 0.93, 0.85) if not simple else Color(0.88, 0.84, 0.74), 0.5)
	mats.lower = _pbr("painted_plaster_wall", Color(0.5, 0.68, 0.56) if not simple else Color(0.45, 0.62, 0.52), 0.6)
	mats.ceiling = _pbr("painted_plaster_wall", Color(1, 1, 1) if not simple else Color(0.9, 0.9, 0.88), 0.4)
	mats.door = _pbr("laminate_floor_02", Color(1.0, 0.92, 0.82) if not simple else Color(0.66, 0.48, 0.32), 0.7, 0.9)
	mats.frame = _flat(Color(0.35, 0.3, 0.26), 0.5)
	mats.base = _flat(Color(0.2, 0.18, 0.17), 0.6)
	mats.metal = _flat(Color(0.75, 0.75, 0.76), 0.3)
	mats.metal.metallic = 0.9
	mats.plate = _flat(Color(0.95, 0.95, 0.92), 0.4)
	mats.red = _flat(Color(0.75, 0.08, 0.07), 0.45)
	mats.cork = _flat(Color(0.62, 0.45, 0.28), 0.9)
	mats.paper = _flat(Color(0.95, 0.94, 0.9), 0.95)
	mats.paper2 = _flat(Color(0.98, 0.9, 0.55), 0.95)
	mats.shelf = _flat(Color(0.5, 0.36, 0.24), 0.7)
	mats.bin = _flat(Color(0.2, 0.42, 0.7), 0.5)
	mats.shoe1 = _flat(Color(0.9, 0.9, 0.9), 0.6)
	mats.shoe2 = _flat(Color(0.15, 0.15, 0.18), 0.6)
	mats.shoe3 = _flat(Color(0.85, 0.3, 0.4), 0.6)

# ---------------------------------------------------------------- 도형
## 모서리를 깎은 상자 (데포르메). r = 0이면 그냥 상자
func _chamfer_mesh(size: Vector3, r: float) -> Mesh:
	if r <= 0.0:
		var b := BoxMesh.new()
		b.size = size
		return b
	r = minf(r, minf(size.x, minf(size.y, size.z)) * 0.45)
	var h: Vector3 = size * 0.5
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var pts: Dictionary = {}
	for sx: int in [-1, 1]:
		for sy: int in [-1, 1]:
			for sz: int in [-1, 1]:
				var k: Vector3i = Vector3i(sx, sy, sz)
				pts[k] = [Vector3(sx * h.x, sy * (h.y - r), sz * (h.z - r)), Vector3(sx * (h.x - r), sy * h.y, sz * (h.z - r)), Vector3(sx * (h.x - r), sy * (h.y - r), sz * h.z)]
	var faces: Array = []
	# 큰 면 6개
	for s: int in [-1, 1]:
		faces.append([pts[Vector3i(s, -1, -1)][0], pts[Vector3i(s, 1, -1)][0], pts[Vector3i(s, 1, 1)][0], pts[Vector3i(s, -1, 1)][0]])
		faces.append([pts[Vector3i(-1, s, -1)][1], pts[Vector3i(1, s, -1)][1], pts[Vector3i(1, s, 1)][1], pts[Vector3i(-1, s, 1)][1]])
		faces.append([pts[Vector3i(-1, -1, s)][2], pts[Vector3i(1, -1, s)][2], pts[Vector3i(1, 1, s)][2], pts[Vector3i(-1, 1, s)][2]])
	# 모서리 깎은 면 12개
	for a: int in [-1, 1]:
		for b: int in [-1, 1]:
			faces.append([pts[Vector3i(a, b, -1)][0], pts[Vector3i(a, b, 1)][0], pts[Vector3i(a, b, 1)][1], pts[Vector3i(a, b, -1)][1]])  # z 방향 모서리
			faces.append([pts[Vector3i(a, -1, b)][0], pts[Vector3i(a, 1, b)][0], pts[Vector3i(a, 1, b)][2], pts[Vector3i(a, -1, b)][2]])  # y 방향
			faces.append([pts[Vector3i(-1, a, b)][1], pts[Vector3i(1, a, b)][1], pts[Vector3i(1, a, b)][2], pts[Vector3i(-1, a, b)][2]])  # x 방향
	# 꼭짓점 삼각형 8개
	for k: Vector3i in pts:
		faces.append(pts[k])
	for f: Array in faces:
		var c: Vector3 = Vector3.ZERO
		for p: Vector3 in f:
			c += p
		c /= f.size()
		var n: Vector3 = (f[1] - f[0]).cross(f[2] - f[0]).normalized()
		if n.dot(c) < 0.0:
			f.reverse()
			n = -n
		for i: int in range(1, f.size() - 1):
			for p: Vector3 in [f[0], f[i + 1], f[i]]:  # Godot 앞면 = 시계 방향
				st.set_normal(n)
				st.add_vertex(p)
	return st.commit()

func _box(size: Vector3, at: Vector3, mat: Material, bevel: float = -1.0, rot_deg: Vector3 = Vector3.ZERO) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	mi.mesh = _chamfer_mesh(size, S.bevel if bevel < 0.0 else bevel)
	mi.material_override = mat
	mi.position = at
	mi.rotation_degrees = rot_deg
	root3d.add_child(mi)
	return mi

func _cyl(r: float, hgt: float, at: Vector3, mat: Material, rot_deg: Vector3 = Vector3.ZERO) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	var c := CylinderMesh.new()
	c.top_radius = r
	c.bottom_radius = r
	c.height = hgt
	c.radial_segments = 8 if not S.textured else 24
	mi.mesh = c
	mi.material_override = mat
	mi.position = at
	mi.rotation_degrees = rot_deg
	root3d.add_child(mi)
	return mi

# ---------------------------------------------------------------- 장면
func _build(st: String, is_night: bool) -> void:
	if root3d != null:
		root3d.queue_free()
		await process_frame
	style_name = st
	S = STYLES[st]
	night = is_night
	mats.clear()
	_make_mats()
	root3d = Node3D.new()
	root.add_child(root3d)
	var hw: float = S.w * 0.5
	var t: float = S.wall_t
	var H: float = S.h
	# 바닥·천장·벽
	_box(Vector3(S.w + 2 * t, 0.2, LEN), Vector3(0, -0.1, -LEN * 0.5), mats.floor, 0.0)
	_box(Vector3(S.w + 2 * t, 0.2, LEN), Vector3(0, H + 0.1, -LEN * 0.5), mats.ceiling, 0.0)
	for s: float in [-1.0, 1.0]:
		_box(Vector3(t, H, LEN), Vector3(s * (hw + t * 0.5), H * 0.5, -LEN * 0.5), mats.wall, 0.0)
		var wh: float = 1.0 if S.bevel <= 0.0 else 1.2
		_box(Vector3(0.02, wh, LEN), Vector3(s * (hw - 0.01), wh * 0.5, -LEN * 0.5), mats.lower, 0.0)
		var bh: float = 0.1 if S.bevel <= 0.0 else 0.16
		_box(Vector3(0.04 + t * 0.2, bh, LEN), Vector3(s * (hw - 0.02), bh * 0.5, -LEN * 0.5), mats.base)
	_box(Vector3(S.w, H, t), Vector3(0, H * 0.5, 0.6), mats.wall, 0.0)
	# 끝 벽 + 창
	_box(Vector3(S.w, H, t), Vector3(0, H * 0.5, -LEN - t * 0.5), mats.wall, 0.0)
	var win_mat: StandardMaterial3D = _flat(Color(0.55, 0.72, 0.95) if not night else Color(0.08, 0.12, 0.25), 0.2, 2.5 if not night else 0.8)
	_box(Vector3(1.1, 1.0, 0.04), Vector3(0, 1.5, -LEN + 0.01), win_mat, 0.0)
	_box(Vector3(1.25, 0.08, 0.12), Vector3(0, 0.96, -LEN + 0.04), mats.frame)
	# 비상구 표시
	_box(Vector3(0.45, 0.18, 0.06), Vector3(0, H - 0.25, -LEN + 0.08), _flat(Color(0.1, 0.85, 0.35), 0.4, 3.0))
	# 문 6개
	var z: float = -2.5
	var i: int = 0
	while z > -LEN + 2.0:
		for s: float in [-1.0, 1.0]:
			_door(s, z + (0.0 if s < 0 else -1.2), i)
			i += 1
		z -= 4.2
	# 소품
	_box(Vector3(0.45, 0.65, 0.18), Vector3(-hw + 0.09, 1.1, -5.0), mats.red)  # 소화기함
	_box(Vector3(0.01, 0.42, 0.32), Vector3(-hw + 0.185, 1.15, -5.0), _flat(Color(0.6, 0.65, 0.7), 0.1), 0.0)
	_board(Vector3(hw - 0.03, 1.5, -7.6))
	_shoes(Vector3(hw - 0.25, 0.0, -3.0))
	_cyl(0.2, 0.55, Vector3(-hw + 0.3, 0.275, -10.5), mats.bin)
	# 천장 형광등
	var lz: float = -1.5
	var k: int = 0
	while lz > -LEN + 0.5:
		var on: bool = not night or k == 2
		var dim: float = 1.0 if not night else 0.25
		var lamp_mat: StandardMaterial3D = _flat(Color(1.0, 0.97, 0.9), 0.3, (4.0 * dim) if on else 0.0)
		if not on:
			lamp_mat = _flat(Color(0.35, 0.35, 0.33), 0.4)
		var lamp_h: float = 0.06 if S.bevel <= 0.0 else 0.12
		_box(Vector3(0.6, lamp_h, 1.2), Vector3(0, H - lamp_h * 0.5, lz), lamp_mat, minf(S.bevel, 0.05))
		if on:
			var al := AreaLight3D.new()
			al.area_size = Vector2(0.6, 1.2)
			al.area_range = 8.0
			al.light_energy = 2.2 * dim
			al.light_color = Color(1.0, 0.95, 0.86) if not night else Color(0.8, 1.0, 0.85)
			al.shadow_enabled = true
			al.position = Vector3(0, H - lamp_h - 0.01, lz)
			al.rotation_degrees = Vector3(-90, 0, 0)
			root3d.add_child(al)
			var spill := OmniLight3D.new()
			spill.position = Vector3(0, H - 0.25, lz)
			spill.omni_range = 2.6
			spill.light_energy = 0.5 * dim
			spill.light_color = al.light_color
			root3d.add_child(spill)
		lz -= 3.0
		k += 1
	# 창빛
	var wl := SpotLight3D.new()
	wl.position = Vector3(0, 1.6, -LEN + 0.3)
	wl.rotation_degrees = Vector3(-8, 0, 0)
	wl.spot_angle = 50.0
	wl.spot_range = 12.0
	wl.light_energy = 2.5 if not night else 0.6
	wl.light_color = Color(0.75, 0.85, 1.0) if not night else Color(0.4, 0.5, 0.9)
	wl.rotate_y(PI)
	wl.shadow_enabled = true
	root3d.add_child(wl)
	# 종이인형 카드
	var pp := PaperPuppet.new()
	pp.poses = {"front": _ptex("front"), "back": _ptex("back")}
	pp.height = 1.55
	pp.position = Vector3(0.35, 0.0, -6.2)
	root3d.add_child(pp)
	# 환경
	var we := WorldEnvironment.new()
	env = Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.02, 0.02, 0.03)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.9, 0.88, 0.85) if not night else Color(0.3, 0.35, 0.5)
	env.ambient_light_energy = 0.35 if not night else 0.03
	env.tonemap_mode = Environment.TONE_MAPPER_AGX
	env.sdfgi_enabled = true
	env.sdfgi_use_occlusion = true
	env.ssao_enabled = true
	env.ssao_intensity = 2.0
	env.ssr_enabled = S.textured
	env.glow_enabled = true
	env.glow_intensity = 0.6
	env.volumetric_fog_enabled = night or st == "real"
	env.volumetric_fog_density = 0.035 if night else 0.006
	env.volumetric_fog_albedo = Color(0.8, 0.85, 0.9)
	env.adjustment_enabled = true
	env.adjustment_saturation = 1.05 if not night else 0.6
	env.adjustment_contrast = 1.05 if not night else 1.15
	we.environment = env
	cam_attr = CameraAttributesPractical.new()
	if st == "deform" and not night:
		cam_attr.dof_blur_far_enabled = true
		cam_attr.dof_blur_far_distance = 7.5
		cam_attr.dof_blur_far_transition = 4.0
		cam_attr.dof_blur_amount = 0.2
		cam_attr.dof_blur_near_enabled = true
		cam_attr.dof_blur_near_distance = 1.2
		cam_attr.dof_blur_near_transition = 0.8
	we.camera_attributes = cam_attr
	root3d.add_child(we)
	# 카메라·손전등
	cam = Camera3D.new()
	cam.fov = 70.0
	root3d.add_child(cam)
	cam.current = true
	cam.look_at_from_position(Vector3(-0.25, 1.6, -0.6), Vector3(0.1, 1.25, -9.0), Vector3.UP)
	if night:
		flashlight = SpotLight3D.new()
		flashlight.spot_angle = 22.0
		flashlight.spot_range = 14.0
		flashlight.light_energy = 6.0
		flashlight.light_color = Color(1.0, 0.95, 0.85)
		flashlight.shadow_enabled = true
		flashlight.light_volumetric_fog_energy = 1.5
		flashlight.position = Vector3(0.18, -0.15, 0.0)
		cam.add_child(flashlight)
	root.scaling_3d_mode = Viewport.SCALING_3D_MODE_NEAREST if S.lowres else Viewport.SCALING_3D_MODE_BILINEAR
	root.scaling_3d_scale = 0.3 if S.lowres else 1.0
	await process_frame

func _cam_b() -> void:
	cam.look_at_from_position(Vector3(-0.5, 1.6, -3.6), Vector3(0.55, 1.1, -6.6), Vector3.UP)

func _ptex(n: String) -> Texture2D:
	var img := Image.load_from_file(ProjectSettings.globalize_path("res://.screenshots/paper_fx/%s.png" % n))
	img.generate_mipmaps()
	return ImageTexture.create_from_image(img)

func _door(side: float, z: float, idx: int) -> void:
	var hw: float = S.w * 0.5
	var dh: float = S.door_h
	var dw: float = S.door_w
	var x: float = side * (hw - 0.03)
	var tilt: float = S.tilt * (1.0 if idx % 3 == 1 else 0.0) * side
	var fr: float = 0.07 if S.bevel <= 0.0 else 0.12
	# 문틀
	_box(Vector3(0.1, dh + fr, fr), Vector3(x, (dh + fr) * 0.5, z - dw * 0.5 - fr * 0.5), mats.frame, -1.0, Vector3(tilt, 0, 0))
	_box(Vector3(0.1, dh + fr, fr), Vector3(x, (dh + fr) * 0.5, z + dw * 0.5 + fr * 0.5), mats.frame, -1.0, Vector3(tilt, 0, 0))
	_box(Vector3(0.1, fr, dw + fr * 2.0), Vector3(x, dh + fr * 0.5, z), mats.frame, -1.0, Vector3(0, 0, tilt))
	# 문짝
	_box(Vector3(0.05, dh, dw), Vector3(x - side * 0.01, dh * 0.5, z), mats.door, -1.0, Vector3(tilt * 0.5, 0, 0))
	# 손잡이(레버)
	var hs: float = S.handle
	_cyl(0.025 * hs, 0.06 * hs, Vector3(x - side * 0.06 * hs, 1.0, z + dw * 0.38), mats.metal, Vector3(0, 0, 90))
	_box(Vector3(0.025 * hs, 0.025 * hs, 0.14 * hs), Vector3(x - side * 0.1 * hs, 1.0, z + dw * 0.38 - 0.06 * hs), mats.metal, minf(S.bevel, 0.01))
	# 호실 표지
	_box(Vector3(0.02, 0.1 * hs, 0.22 * hs), Vector3(x - side * 0.035, dh + 0.18, z), mats.plate)

func _board(at: Vector3) -> void:
	_box(Vector3(0.04, 0.8, 1.2), at, mats.cork)
	var papers: Array = [[Vector3(0, 0.15, -0.3), 4.0, mats.paper], [Vector3(0, 0.1, 0.25), -6.0, mats.paper2], [Vector3(0, -0.2, -0.05), 2.0, mats.paper], [Vector3(0, -0.15, 0.38), 9.0, mats.paper]]
	for p: Array in papers:
		_box(Vector3(0.005, 0.3, 0.22), at + Vector3(-0.025, 0, 0) + p[0], p[2], 0.0, Vector3(p[1], 0, 0))

func _shoes(at: Vector3) -> void:
	var hs: float = 1.0 if S.bevel <= 0.0 else 1.15
	_box(Vector3(0.35, 0.45 * hs, 0.9), at + Vector3(0, 0.225 * hs, 0), mats.shelf)
	var cols: Array = [mats.shoe1, mats.shoe2, mats.shoe3, mats.shoe1]
	for j: int in range(4):
		_box(Vector3(0.11, 0.07, 0.26) * hs, at + Vector3(-0.32, 0.035 * hs, -0.3 + j * 0.2), cols[j], minf(S.bevel, 0.025), Vector3(0, 8.0 * (j - 1.5), 0))
