extends SceneTree
## 데포르메 배경 스타일 후보 비교 (env-style-direction §10): 같은 기숙사 복도를 극사실 1 + 데포르메 6가지로, 낮, 종이인형 카드와 함께 찍는다.
##   godot --path . --rendering-driver vulkan --rendering-method forward_plus --resolution 1280x720 \
##         -s res://tools/dev/deform_styles.gd -- --dir=절대경로 [--style=real|mini|clay|paper|toy|anime|paint]
## 조명 분위기 비교(vibe-board §8): --moods [--mood=이름] → 같은 모양(기본 real)에 조명만 바꿔 light_<이름>_a/b.png
## 극사실은 얇고 반듯한 모양 + 사진 재질. 데포르메 6가지는 같은 "과장된 모양"(두꺼운 벽·둥근 모서리·큰 문과 손잡이·기운 벽)에
## 겉만 다르게 입힌다. 재질 사진은 .screenshots/style3/tex/ (Poly Haven CC0, git 제외), 나머지 무늬는 코드로 만든다.

const TEX: String = "res://.screenshots/style3/tex/"
const LEN: float = 16.0
const ORDER: Array[String] = ["real", "mini", "clay", "paper", "toy", "anime", "paint"]

## 모양 값: 극사실(real)과 데포르메(나머지 전부)
const SHAPE_REAL: Dictionary = {"w": 2.2, "h": 2.5, "wall_t": 0.15, "door_h": 2.05, "door_w": 0.9, "frame": 0.06, "handle": 1.0, "bevel": 0.0, "lean": 0.0, "prop": 1.0}
const SHAPE_DEFORM: Dictionary = {"w": 2.8, "h": 2.9, "wall_t": 0.35, "door_h": 2.45, "door_w": 1.15, "frame": 0.17, "handle": 2.8, "bevel": 0.12, "lean": 1.6, "prop": 1.35}

## 기본 색 (모든 스타일이 같은 색 정체성: 크림 벽·초록 징두리·나무 문·테라초 바닥)
const PAL: Dictionary = {
	"floor": Color(0.78, 0.74, 0.68), "wall": Color(0.95, 0.91, 0.82), "lower": Color(0.45, 0.66, 0.54),
	"ceiling": Color(0.97, 0.96, 0.93), "door": Color(0.72, 0.52, 0.34), "frame": Color(0.36, 0.3, 0.26),
	"base": Color(0.24, 0.2, 0.18), "metal": Color(0.78, 0.78, 0.8), "plate": Color(0.96, 0.95, 0.9),
	"red": Color(0.8, 0.12, 0.1), "cork": Color(0.66, 0.48, 0.3), "paper": Color(0.96, 0.95, 0.9),
	"paper2": Color(0.98, 0.86, 0.45), "shelf": Color(0.55, 0.38, 0.24), "bin": Color(0.22, 0.45, 0.75),
	"shoe1": Color(0.92, 0.92, 0.92), "shoe2": Color(0.18, 0.18, 0.22), "shoe3": Color(0.88, 0.32, 0.42),
	"clock": Color(0.95, 0.95, 0.93),
}
## 스타일별 색 조정: [채도 배수, 밝기 배수]
const TONE: Dictionary = {
	"real": [0.8, 1.0], "mini": [0.65, 0.8], "clay": [0.85, 1.02], "paper": [1.05, 1.0],
	"toy": [1.7, 1.05], "anime": [1.15, 1.06], "paint": [1.1, 0.95],
}

var dir: String = "res://.screenshots"
var only_style: String = ""
var root3d: Node3D
var cam: Camera3D
var S: Dictionary = {}
var st: String = ""
var rng := RandomNumberGenerator.new()
var tex_cache: Dictionary = {}
var gen: Dictionary = {}  # 코드로 만든 무늬
var moods_mode: bool = false
var only_mood: String = ""
var mood: String = ""
var lamp_slots: Array = []  # [재질, 위치]
var win_mat: StandardMaterial3D
const MOODS: Array[String] = ["base", "dusk", "mono_red", "duo", "liminal", "stage", "moon_blinds", "alarm", "uv", "pools"]

func _init() -> void:
	for a: String in OS.get_cmdline_user_args():
		if a.begins_with("--dir="):
			dir = a.substr(6)
		elif a.begins_with("--style="):
			only_style = a.substr(8)
		elif a == "--moods":
			moods_mode = true
		elif a.begins_with("--mood="):
			only_mood = a.substr(7)
	DirAccess.make_dir_recursive_absolute(dir)
	_make_gen_textures()
	_run()

func _run() -> void:
	if moods_mode:
		await _run_moods()
		return
	for s: String in ORDER:
		if only_style != "" and s != only_style:
			continue
		await _build(s)
		for i: int in range(40):
			await process_frame
		await _shot("%s_a" % s)
		cam.look_at_from_position(Vector3(-0.55, 1.6, -3.4), Vector3(0.6, 1.15, -6.6), Vector3.UP)
		for i: int in range(25):
			await process_frame
		await _shot("%s_b" % s)
	quit()

func _run_moods() -> void:
	for m: String in MOODS:
		if only_mood != "" and m != only_mood:
			continue
		mood = m
		await _build(only_style if only_style != "" else "real")
		if m != "base":
			_apply_mood()
		for i: int in range(45):
			await process_frame
		await _shot("light_%s_a" % m)
		cam.look_at_from_position(Vector3(-0.55, 1.6, -3.4), Vector3(0.6, 1.15, -6.6), Vector3.UP)
		for i: int in range(25):
			await process_frame
		await _shot("light_%s_b" % m)
	quit()

func _shot(n: String) -> void:
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(dir + "/" + n + ".png")
	print("saved ", n)

# ---------------------------------------------------------------- 코드로 만드는 무늬
func _img_tex(img: Image) -> ImageTexture:
	img.generate_mipmaps()
	return ImageTexture.create_from_image(img)

func _noise_img(freq: float, seed_v: int, size: int = 512, type: int = FastNoiseLite.TYPE_SIMPLEX_SMOOTH, octaves: int = 4) -> Image:
	var n := FastNoiseLite.new()
	n.noise_type = type
	n.frequency = freq
	n.seed = seed_v
	n.fractal_octaves = octaves
	return n.get_seamless_image(size, size)

func _make_gen_textures() -> void:
	# 점토: 울퉁불퉁 + 손가락 자국 같은 큰 움푹
	var clay: Image = _noise_img(0.02, 3)
	var dents: Image = _noise_img(0.006, 7, 512, FastNoiseLite.TYPE_CELLULAR, 1)
	for y: int in range(512):
		for x: int in range(512):
			var v: float = clay.get_pixel(x, y).r * 0.6 + dents.get_pixel(x, y).r * 0.4
			clay.set_pixel(x, y, Color(v, v, v))
	clay.convert(Image.FORMAT_RGBA8)
	clay.bump_map_to_normal_map(6.0)
	gen.clay_n = _img_tex(clay)
	# 종이: 섬유 결(밝기) + 골판지 줄무늬(법선)
	var fib: Image = _noise_img(0.18, 11, 512, FastNoiseLite.TYPE_VALUE, 3)
	fib.convert(Image.FORMAT_RGBA8)
	for y: int in range(512):
		for x: int in range(512):
			var v: float = 0.9 + fib.get_pixel(x, y).r * 0.1
			fib.set_pixel(x, y, Color(v, v, v * 0.98))
	gen.paper_a = _img_tex(fib)
	var corr := Image.create(512, 512, false, Image.FORMAT_RGBA8)
	for y: int in range(512):
		for x: int in range(512):
			var v: float = 0.5 + 0.5 * sin(x / 512.0 * TAU * 24.0)
			corr.set_pixel(x, y, Color(v, v, v))
	corr.bump_map_to_normal_map(2.5)
	gen.corr_n = _img_tex(corr)
	# 바닥 타일 (큰 칸 + 줄눈) — 데포르메용
	var tile := Image.create(512, 512, false, Image.FORMAT_RGBA8)
	for y: int in range(512):
		for x: int in range(512):
			var cx: int = x / 128
			var cy: int = y / 128
			var grout: bool = (x % 128) < 5 or (y % 128) < 5
			var v: float = 0.62 if grout else (1.0 if (cx + cy) % 2 == 0 else 0.86)
			tile.set_pixel(x, y, Color(v, v, v))
	gen.tile_a = _img_tex(tile)
	# 붓 자국 (가로로 늘린 낮은 주파수 + 작은 결)
	var br: Image = _noise_img(0.012, 21, 256)
	br.resize(256, 48, Image.INTERPOLATE_BILINEAR)
	br.resize(512, 512, Image.INTERPOLATE_CUBIC)
	var grain: Image = _noise_img(0.08, 22)
	br.convert(Image.FORMAT_RGBA8)
	for y: int in range(512):
		for x: int in range(512):
			var v: float = 0.78 + br.get_pixel(x, y).r * 0.32 + (grain.get_pixel(x, y).r - 0.5) * 0.06
			br.set_pixel(x, y, Color(v, v * 0.99, v * 0.96))
	gen.brush_a = _img_tex(br)
	# 줄무늬 벽지 (장난감)
	var stripe := Image.create(256, 256, false, Image.FORMAT_RGBA8)
	for y: int in range(256):
		for x: int in range(256):
			var v: float = 1.0 if (x / 32) % 2 == 0 else 0.9
			stripe.set_pixel(x, y, Color(v, v, v))
	gen.stripe_a = _img_tex(stripe)

func _tex(n: String) -> Texture2D:
	if tex_cache.has(n):
		return tex_cache[n]
	var p: String = ProjectSettings.globalize_path(TEX + n + ".jpg")
	var t: Texture2D = null
	if FileAccess.file_exists(p):
		t = _img_tex(Image.load_from_file(p))
	tex_cache[n] = t
	return t

# ---------------------------------------------------------------- 재질
func _col(kind: String) -> Color:
	var c: Color = PAL[kind]
	var tone: Array = TONE[st]
	return Color.from_hsv(c.h, clampf(c.s * tone[0], 0.0, 1.0), clampf(c.v * tone[1], 0.0, 1.0))

func _photo(m: StandardMaterial3D, name: String, uv: float) -> void:
	m.albedo_texture = _tex(name + "_diff")
	m.normal_enabled = true
	m.normal_texture = _tex(name + "_nor")
	m.roughness_texture = _tex(name + "_rough")
	m.ao_enabled = true
	m.ao_texture = _tex(name + "_ao")
	m.uv1_triplanar = true
	m.uv1_world_triplanar = true
	m.uv1_scale = Vector3.ONE * uv

func _tri(m: StandardMaterial3D, uv: float) -> void:
	m.uv1_triplanar = true
	m.uv1_world_triplanar = true
	m.uv1_scale = Vector3.ONE * uv

const PHOTO: Dictionary = {"floor": ["terrazzo_tiles", 0.5], "wall": ["painted_plaster_wall", 0.5], "lower": ["painted_plaster_wall", 0.6], "ceiling": ["ceiling_interior", 0.5], "door": ["laminate_floor_02", 0.7]}

func _mat(kind: String) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	var c: Color = _col(kind)
	m.albedo_color = c
	m.roughness = 0.7
	var big: bool = PHOTO.has(kind)
	match st:
		"real":
			if big:
				m.albedo_color = Color(1, 1, 1).lerp(c, 0.55)
				_photo(m, PHOTO[kind][0], PHOTO[kind][1])
		"mini":  # 사실 재질, 무늬를 크게(미니어처), 거칠고 어둡게
			if big:
				m.albedo_color = Color(1, 1, 1).lerp(c, 0.6)
				_photo(m, PHOTO[kind][0], PHOTO[kind][1] * 0.35)
			m.roughness = 0.9
		"clay":  # 점토: 평평한 색 + 울퉁불퉁 법선, 무광
			m.normal_enabled = true
			m.normal_texture = gen.clay_n
			m.normal_scale = 1.4
			_tri(m, 0.9)
			m.roughness = 0.88
			m.rim_enabled = true
			m.rim = 0.25
			m.rim_tint = 0.6
		"paper":  # 종이·골판지: 섬유 결 + 벽은 골판지 줄
			m.albedo_texture = gen.paper_a
			_tri(m, 0.8)
			m.roughness = 1.0
			if kind in ["wall", "lower", "door", "shelf", "ceiling"]:
				m.normal_enabled = true
				m.normal_texture = gen.corr_n
				m.normal_scale = 0.8
			if kind == "floor":
				m.albedo_texture = gen.tile_a
				_tri(m, 0.45)
		"toy":  # 장난감 플라스틱: 진한 색 + 광택
			m.roughness = 0.22
			m.clearcoat_enabled = true
			m.clearcoat = 0.6
			m.clearcoat_roughness = 0.15
			if kind == "floor":
				m.albedo_texture = gen.tile_a
				_tri(m, 0.45)
			if kind == "wall":
				m.albedo_texture = gen.stripe_a
				_tri(m, 0.5)
		"anime":  # 애니 툰: 두 단계 명암 + 외곽선
			m.diffuse_mode = BaseMaterial3D.DIFFUSE_TOON
			m.specular_mode = BaseMaterial3D.SPECULAR_TOON
			m.roughness = 0.75
			if kind == "floor":
				m.albedo_texture = gen.tile_a
				_tri(m, 0.45)
			if kind not in ["floor", "wall", "ceiling", "lower"]:
				m.stencil_mode = BaseMaterial3D.STENCIL_MODE_OUTLINE
				m.stencil_color = Color(0.18, 0.12, 0.14)
				m.stencil_outline_thickness = 0.012
		"paint":  # 손그림 질감(Dishonored 결): 붓 자국 + 과장된 모양
			m.albedo_texture = gen.brush_a
			_tri(m, 0.35)
			m.roughness = 0.8
			if kind == "floor":
				m.albedo_texture = gen.tile_a
				_tri(m, 0.4)
				m.albedo_color = c.darkened(0.1)
	if kind == "metal":
		m.metallic = 0.9 if st != "anime" else 0.0
		m.roughness = 0.3
	return m

var mats: Dictionary = {}

# ---------------------------------------------------------------- 도형
func _chamfer_mesh(size: Vector3, r: float) -> Mesh:
	if r <= 0.0:
		var b := BoxMesh.new()
		b.size = size
		return b
	r = minf(r, minf(size.x, minf(size.y, size.z)) * 0.45)
	var h: Vector3 = size * 0.5
	var stt := SurfaceTool.new()
	stt.begin(Mesh.PRIMITIVE_TRIANGLES)
	var pts: Dictionary = {}
	for sx: int in [-1, 1]:
		for sy: int in [-1, 1]:
			for sz: int in [-1, 1]:
				pts[Vector3i(sx, sy, sz)] = [Vector3(sx * h.x, sy * (h.y - r), sz * (h.z - r)), Vector3(sx * (h.x - r), sy * h.y, sz * (h.z - r)), Vector3(sx * (h.x - r), sy * (h.y - r), sz * h.z)]
	var faces: Array = []
	for s: int in [-1, 1]:
		faces.append([pts[Vector3i(s, -1, -1)][0], pts[Vector3i(s, 1, -1)][0], pts[Vector3i(s, 1, 1)][0], pts[Vector3i(s, -1, 1)][0]])
		faces.append([pts[Vector3i(-1, s, -1)][1], pts[Vector3i(1, s, -1)][1], pts[Vector3i(1, s, 1)][1], pts[Vector3i(-1, s, 1)][1]])
		faces.append([pts[Vector3i(-1, -1, s)][2], pts[Vector3i(1, -1, s)][2], pts[Vector3i(1, 1, s)][2], pts[Vector3i(-1, 1, s)][2]])
	for a: int in [-1, 1]:
		for b: int in [-1, 1]:
			faces.append([pts[Vector3i(a, b, -1)][0], pts[Vector3i(a, b, 1)][0], pts[Vector3i(a, b, 1)][1], pts[Vector3i(a, b, -1)][1]])
			faces.append([pts[Vector3i(a, -1, b)][0], pts[Vector3i(a, 1, b)][0], pts[Vector3i(a, 1, b)][2], pts[Vector3i(a, -1, b)][2]])
			faces.append([pts[Vector3i(-1, a, b)][1], pts[Vector3i(1, a, b)][1], pts[Vector3i(1, a, b)][2], pts[Vector3i(-1, a, b)][2]])
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
			for p: Vector3 in [f[0], f[i + 1], f[i]]:
				stt.set_normal(n)
				stt.add_vertex(p)
	return stt.commit()

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
	c.radial_segments = 32
	mi.mesh = c
	mi.material_override = mat
	mi.position = at
	mi.rotation_degrees = rot_deg
	root3d.add_child(mi)
	return mi

func _attach(child: Node3D, parent: Node3D, local: Vector3) -> void:
	child.get_parent().remove_child(child)
	parent.add_child(child)
	child.position = local
	child.rotation = Vector3.ZERO

func _inset() -> float:
	return 0.03 + S.wall_t * 0.15

func _lean() -> float:
	return rng.randf_range(-1.0, 1.0) * S.lean

# ---------------------------------------------------------------- 장면
func _build(s: String) -> void:
	if root3d != null:
		root3d.queue_free()
		await process_frame
	st = s
	S = SHAPE_REAL if s == "real" else SHAPE_DEFORM
	rng.seed = 5
	mats.clear()
	for k: String in PAL:
		mats[k] = _mat(k)
	root3d = Node3D.new()
	root.add_child(root3d)
	var hw: float = S.w * 0.5
	var t: float = S.wall_t
	var H: float = S.h
	_box(Vector3(S.w + 2 * t, 0.2, LEN + 2.0), Vector3(0, -0.1, -LEN * 0.5), mats.floor, 0.0)
	_box(Vector3(S.w + 2 * t, 0.2, LEN + 2.0), Vector3(0, H + 0.1, -LEN * 0.5), mats.ceiling, 0.0)
	# 벽: 극사실은 한 장, 데포르메는 2m 조각마다 살짝 기울여 손으로 만든 모형처럼
	var seg: float = LEN + 2.0 if s == "real" else 2.1
	for side: float in [-1.0, 1.0]:
		var z: float = 1.0
		while z > -LEN - 1.0:
			var l: float = minf(seg, z + LEN + 1.0)
			var zc: float = z - l * 0.5
			var r := Vector3(_lean() * 0.4, 0, side * absf(_lean()))
			var wall: MeshInstance3D = _box(Vector3(t, H, l + 0.04), Vector3(side * (hw + t * 0.5), H * 0.5, zc), mats.wall, minf(S.bevel, 0.04), r)
			# 징두리·걸레받이는 벽 조각에 붙여 같이 기울게 (따로 돌리면 이음매가 어긋남)
			var wh: float = 1.0 if s == "real" else 1.25
			var lw: float = 0.03 + t * 0.15
			_attach(_box(Vector3(lw, wh, l + 0.02), Vector3.ZERO, mats.lower, minf(S.bevel, 0.03)), wall, Vector3(-side * (t * 0.5 + lw * 0.5 - 0.005), wh * 0.5 - H * 0.5, 0))
			var bh: float = 0.1 if s == "real" else 0.2
			var bw: float = 0.04 + t * 0.25
			_attach(_box(Vector3(bw, bh, l + 0.04), Vector3.ZERO, mats.base), wall, Vector3(-side * (t * 0.5 + bw * 0.5 - 0.01), bh * 0.5 - H * 0.5, 0))
			z -= l
	_box(Vector3(S.w, H, t), Vector3(0, H * 0.5, 0.8), mats.wall, 0.0)
	_box(Vector3(S.w, H, t), Vector3(0, H * 0.5, -LEN - t * 0.5), mats.wall, 0.0)
	var win := StandardMaterial3D.new()
	win_mat = win
	win.albedo_color = Color(0.6, 0.78, 0.98)
	win.emission_enabled = true
	win.emission = win.albedo_color
	win.emission_energy_multiplier = 2.5
	_box(Vector3(1.1, 1.0, 0.04) * (1.0 if s == "real" else 1.2), Vector3(0, 1.55, -LEN + 0.01), win, 0.0)
	_box(Vector3(1.3, 0.08, 0.12) * (1.0 if s == "real" else 1.3), Vector3(0, 0.95, -LEN + 0.05), mats.frame)
	var ex := StandardMaterial3D.new()
	ex.albedo_color = Color(0.1, 0.85, 0.35)
	ex.emission_enabled = true
	ex.emission = ex.albedo_color
	ex.emission_energy_multiplier = 3.0
	_box(Vector3(0.45, 0.18, 0.06) * S.prop, Vector3(0, H - 0.3, -LEN + 0.1), ex)
	# 문
	var dz: float = -2.5
	var i: int = 0
	while dz > -LEN + 2.0:
		for side: float in [-1.0, 1.0]:
			_door(side, dz + (0.0 if side < 0 else -1.2), i)
			i += 1
		dz -= 4.2
	# 소품
	var p: float = S.prop
	_box(Vector3(0.45, 0.65, 0.18) * p, Vector3(-hw + _inset() + 0.09 * p, 1.1, -5.0), mats.red)
	_board(Vector3(hw - _inset() - 0.03, 1.55, -7.6))
	_shoes(Vector3(hw - _inset() - 0.18 * p, 0.0, -3.0))
	_cyl(0.2 * p, 0.55 * p, Vector3(-hw + 0.3 * p, 0.275 * p, -10.5), mats.bin)
	# 벽시계
	_cyl(0.16 * p, 0.05, Vector3(hw - 0.03, 2.15 if s == "real" else 2.4, -7.6), mats.clock, Vector3(0, 0, 90))
	_box(Vector3(0.01, 0.1 * p, 0.012 * p), Vector3(hw - 0.06, (2.15 if s == "real" else 2.4) + 0.04 * p, -7.6), mats.base, 0.0)
	_box(Vector3(0.01, 0.012 * p, 0.13 * p), Vector3(hw - 0.06, 2.15 if s == "real" else 2.4, -7.6 + 0.05 * p), mats.base, 0.0)
	_lamps()
	_window_light()
	_puppet()
	_environment()
	cam = Camera3D.new()
	cam.fov = 70.0
	root3d.add_child(cam)
	cam.current = true
	cam.look_at_from_position(Vector3(-0.3, 1.6, -0.4), Vector3(0.1, 1.25, -9.0), Vector3.UP)
	await process_frame

func _lamps() -> void:
	var H: float = S.h
	var lz: float = -1.5
	var k: int = 0
	var mood: bool = st == "mini"
	lamp_slots.clear()
	while lz > -LEN + 0.5:
		var on: bool = not mood or k == 1 or k == 3
		var lamp := StandardMaterial3D.new()
		lamp.albedo_color = Color(1.0, 0.97, 0.9) if on else Color(0.3, 0.3, 0.28)
		if on:
			lamp.emission_enabled = true
			lamp.emission = Color(1.0, 0.93, 0.8) if st != "real" else Color(0.95, 0.98, 1.0)
			lamp.emission_energy_multiplier = 4.0
		var lh: float = 0.06 if st == "real" else 0.16
		_box(Vector3(0.6, lh, 1.2) * Vector3(1, 1, 1) * (1.0 if st == "real" else 1.15), Vector3(0, H - lh * 0.5, lz), lamp, 0.0 if st == "real" else 0.07)
		lamp_slots.append([lamp, Vector3(0, H - lh - 0.01, lz)])
		if on:
			var al := AreaLight3D.new()
			al.area_size = Vector2(0.6, 1.2)
			al.area_range = 8.0
			al.light_energy = 2.2 if not mood else 3.2
			al.light_color = Color(0.95, 0.98, 1.0) if st == "real" else Color(1.0, 0.92, 0.8)
			al.shadow_enabled = true
			al.position = Vector3(0, H - lh - 0.01, lz)
			al.rotation_degrees = Vector3(-90, 0, 0)
			root3d.add_child(al)
			var spill := OmniLight3D.new()
			spill.position = Vector3(0, H - 0.3, lz)
			spill.omni_range = 2.6
			spill.light_energy = 0.5
			spill.light_color = al.light_color
			root3d.add_child(spill)
		lz -= 3.0
		k += 1

func _window_light() -> void:
	var wl := SpotLight3D.new()
	wl.position = Vector3(0, 1.7, -LEN + 0.3)
	wl.rotation_degrees = Vector3(-8, 0, 0)
	wl.rotate_y(PI)
	wl.spot_angle = 50.0
	wl.spot_range = 12.0
	wl.light_energy = 2.5
	wl.light_color = Color(0.75, 0.85, 1.0)
	wl.shadow_enabled = true
	root3d.add_child(wl)

func _puppet() -> void:
	var pp := PaperPuppet.new()
	pp.poses = {"front": _ptex("front"), "back": _ptex("back")}
	pp.height = 1.55
	pp.position = Vector3(0.35, 0.0, -6.2)
	root3d.add_child(pp)

func _environment() -> void:
	var we := WorldEnvironment.new()
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.02, 0.02, 0.03)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.9, 0.88, 0.85)
	env.tonemap_mode = Environment.TONE_MAPPER_AGX
	env.sdfgi_enabled = true
	env.sdfgi_use_occlusion = true
	env.ssao_enabled = true
	env.glow_enabled = true
	env.adjustment_enabled = true
	# [주변광, SSAO, 안개, 채도, 대비, 반사, 빛 번짐]
	var v: Array = {
		"real": [0.35, 2.0, 0.006, 0.95, 1.05, true, 0.5],
		"mini": [0.08, 3.0, 0.03, 0.75, 1.2, false, 0.8],
		"clay": [0.4, 1.5, 0.0, 1.05, 1.0, false, 0.5],
		"paper": [0.45, 1.2, 0.0, 1.05, 1.0, false, 0.5],
		"toy": [0.5, 1.0, 0.0, 1.2, 1.05, true, 0.9],
		"anime": [0.65, 0.5, 0.0, 1.1, 0.95, false, 0.6],
		"paint": [0.3, 2.0, 0.012, 1.1, 1.12, false, 0.7],
	}[st]
	env.ambient_light_energy = v[0]
	env.ssao_intensity = v[1]
	env.volumetric_fog_enabled = v[2] > 0.0
	env.volumetric_fog_density = v[2]
	env.volumetric_fog_albedo = Color(0.85, 0.8, 0.7) if st != "real" else Color(0.8, 0.85, 0.9)
	env.adjustment_saturation = v[3]
	env.adjustment_contrast = v[4]
	env.ssr_enabled = v[5]
	env.glow_intensity = v[6]
	if st == "paint":
		env.ambient_light_color = Color(0.6, 0.7, 0.9)  # 그늘은 푸르게, 빛은 따뜻하게
	we.environment = env
	var ca := CameraAttributesPractical.new()
	if st in ["mini", "toy", "clay", "paper"]:  # 미니어처 사진처럼 앞·뒤 흐림
		ca.dof_blur_far_enabled = true
		ca.dof_blur_far_distance = 7.0 if st != "mini" else 8.0
		ca.dof_blur_far_transition = 3.5
		ca.dof_blur_near_enabled = true
		ca.dof_blur_near_distance = 1.6
		ca.dof_blur_near_transition = 1.0
		ca.dof_blur_amount = 0.25 if st != "mini" else 0.18
	we.camera_attributes = ca
	root3d.add_child(we)

func _ptex(n: String) -> Texture2D:
	return _img_tex(Image.load_from_file(ProjectSettings.globalize_path("res://.screenshots/paper_fx/%s.png" % n)))

func _door(side: float, z: float, idx: int) -> void:
	var hw: float = S.w * 0.5
	var dh: float = S.door_h
	var dw: float = S.door_w
	var fr: float = S.frame
	var x: float = side * (hw - _inset() - 0.04)  # 징두리 앞에
	var tilt: float = _lean() * 1.3 if idx % 2 == 1 else 0.0
	_box(Vector3(0.12, dh + fr, fr), Vector3(x, (dh + fr) * 0.5, z - dw * 0.5 - fr * 0.5), mats.frame, -1.0, Vector3(tilt, 0, 0))
	_box(Vector3(0.12, dh + fr, fr), Vector3(x, (dh + fr) * 0.5, z + dw * 0.5 + fr * 0.5), mats.frame, -1.0, Vector3(tilt, 0, 0))
	_box(Vector3(0.12, fr, dw + fr * 2.0), Vector3(x, dh + fr * 0.5, z), mats.frame, -1.0, Vector3(0, 0, tilt))
	_box(Vector3(0.06, dh, dw), Vector3(x - side * 0.01, dh * 0.5, z), mats.door, -1.0, Vector3(tilt * 0.5, 0, 0))
	if st != "real":  # 문 가운데 큰 판 (모형 문)
		_box(Vector3(0.03, dh * 0.55, dw * 0.62), Vector3(x - side * 0.045, dh * 0.58, z), mats.door, 0.04, Vector3(tilt * 0.5, 0, 0))
	var hs: float = S.handle
	_cyl(0.025 * hs, 0.06 * hs, Vector3(x - side * 0.06 * hs, 1.0, z + dw * 0.36), mats.metal, Vector3(0, 0, 90))
	_box(Vector3(0.025 * hs, 0.025 * hs, 0.14 * hs), Vector3(x - side * 0.1 * hs, 1.0, z + dw * 0.36 - 0.06 * hs), mats.metal, minf(S.bevel, 0.012))
	if st == "real":
		_box(Vector3(0.02, 0.1, 0.22), Vector3(x - side * 0.035, dh + 0.18, z), mats.plate)
	else:
		_cyl(0.15, 0.04, Vector3(x - side * 0.04, dh + 0.3, z), mats.plate, Vector3(0, 0, 90))
	# 스위치
	_box(Vector3(0.02, 0.1, 0.07) * (1.0 if st == "real" else 1.8), Vector3(x - side * 0.015, 1.25, z - dw * 0.5 - fr - 0.18), mats.plate)

func _board(at: Vector3) -> void:
	var p: float = S.prop
	_box(Vector3(0.05, 0.8 * p, 1.2 * p), at, mats.cork)
	var papers: Array = [[Vector3(0, 0.15, -0.3), 4.0, mats.paper], [Vector3(0, 0.1, 0.25), -6.0, mats.paper2], [Vector3(0, -0.2, -0.05), 2.0, mats.paper], [Vector3(0, -0.15, 0.38), 9.0, mats.paper]]
	for q: Array in papers:
		_box(Vector3(0.006, 0.3 * p, 0.22 * p), at + Vector3(-0.03, 0, 0) + q[0] * p, q[2], 0.0, Vector3(q[1] * (1.0 if st == "real" else 1.8), 0, 0))

func _shoes(at: Vector3) -> void:
	var p: float = S.prop
	_box(Vector3(0.35, 0.45, 0.9) * p, at + Vector3(0, 0.225 * p, 0), mats.shelf, minf(S.bevel, 0.05))
	var cols: Array = [mats.shoe1, mats.shoe1, mats.shoe3, mats.shoe3]
	for j: int in range(4):  # 신발 두 켤레, 앞코가 복도 쪽
		var zz: float = (-0.25 + j * 0.13 + (0.12 if j >= 2 else 0.0)) * p
		_box(Vector3(0.26, 0.08, 0.1) * p, at + Vector3(-0.36 * p, 0.04 * p, zz), cols[j], minf(S.bevel, 0.035), Vector3(0, 6.0 * (j % 2) - 3.0, 0))

# ---------------------------------------------------------------- 조명 분위기 (vibe-board §8)
func _apply_mood() -> void:
	for n: Node in root3d.get_children():
		if n is Light3D or n is WorldEnvironment:
			root3d.remove_child(n)
			n.free()
	for sl: Array in lamp_slots:
		_lamp(sl, Color.BLACK, 0.0, 0.0)
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0, 0, 0)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.tonemap_mode = Environment.TONE_MAPPER_AGX
	env.sdfgi_enabled = true
	env.sdfgi_use_occlusion = true
	env.ssao_enabled = true
	env.ssao_intensity = 2.0
	env.glow_enabled = true
	env.glow_intensity = 0.8
	env.adjustment_enabled = true
	env.volumetric_fog_enabled = true
	env.volumetric_fog_density = 0.02
	var H: float = S.h
	var hw: float = S.w * 0.5
	var puppet := Vector3(0.35, 1.0, -6.2)
	match mood:
		"dusk":  # 노을 역광: 끝 창에서 낮은 해가 복도를 가로지름
			win_mat.emission = Color(1.0, 0.55, 0.25)
			win_mat.emission_energy_multiplier = 7.0
			_spot(Vector3(0, 1.55, -LEN + 0.3), Vector3(0, 0.5, -1.0), Color(1.0, 0.55, 0.25), 14.0, 32.0, 22.0, null, 2.5)
			_amb(env, Color(0.4, 0.32, 0.6), 0.12, 0.03, Color(1.0, 0.8, 0.6))
			env.glow_intensity = 1.1
		"mono_red":  # 한 색: 전부 빨강
			for sl: Array in lamp_slots:
				_lamp(sl, Color(1.0, 0.08, 0.06), 3.0, 2.2)
			_amb(env, Color(0.6, 0.05, 0.05), 0.05, 0.015, Color(1.0, 0.3, 0.3))
			env.adjustment_saturation = 1.3
			env.adjustment_contrast = 1.2
		"duo":  # 보색 두 색: 청록·자홍 번갈아
			for i: int in lamp_slots.size():
				_lamp(lamp_slots[i], Color(0.1, 0.95, 0.9) if i % 2 == 0 else Color(1.0, 0.15, 0.65), 3.0, 2.4)
			_amb(env, Color(0.2, 0.12, 0.3), 0.08, 0.018, Color(0.9, 0.9, 1.0))
			env.adjustment_saturation = 1.2
		"liminal":  # 리미널 형광: 과하게 밝고 연두빛, 흐릿
			for i: int in lamp_slots.size():
				if i != 2:  # 하나는 꺼짐
					_lamp(lamp_slots[i], Color(0.82, 1.0, 0.68), 4.5, 3.6)
			_amb(env, Color(0.8, 0.95, 0.7), 0.7, 0.025, Color(0.95, 1.0, 0.9))
			env.tonemap_exposure = 1.45
			env.glow_intensity = 1.6
			env.glow_bloom = 0.3
			env.adjustment_saturation = 0.6
			env.adjustment_contrast = 0.8
		"stage":  # 무대 조명: 위에서 핀 조명 + 바닥 쪽 빛이 인형 그림자를 크게
			_spot(Vector3(0.35, H - 0.05, -4.9), puppet, Color(1.0, 0.9, 0.75), 6.0, 16.0, 8.0, null, 1.5)
			_spot(Vector3(0.28, 0.25, -4.3), Vector3(0.35, 1.5, -10.0), Color(1.0, 0.72, 0.45), 4.5, 38.0, 16.0, null, 0.6)
			_amb(env, Color(0.2, 0.2, 0.35), 0.015, 0.02, Color(1, 0.9, 0.8))
		"moon_blinds":  # 달빛 + 블라인드 줄무늬
			win_mat.emission = Color(0.4, 0.55, 1.0)
			win_mat.emission_energy_multiplier = 1.5
			_spot(Vector3(-hw + 0.2, H - 0.15, -5.0), Vector3(hw, 0.4, -7.2), Color(0.55, 0.7, 1.0), 16.0, 42.0, 10.0, _blinds_tex(), 1.8)
			_amb(env, Color(0.2, 0.3, 0.6), 0.05, 0.025, Color(0.6, 0.7, 1.0))
		"alarm":  # 비상등: 빨간 경광등 + 초록 비상구
			_spot(Vector3(0, H - 0.25, -4.3), Vector3(-hw, 1.0, -6.5), Color(1.0, 0.05, 0.03), 18.0, 26.0, 9.0, null, 2.0)
			_omni(Vector3(0, H - 0.25, -4.3), Color(1.0, 0.1, 0.05), 1.5, 4.0)
			_omni(Vector3(0, H - 0.35, -LEN + 0.5), Color(0.1, 1.0, 0.35), 2.5, 6.0)
			_amb(env, Color(0.3, 0.05, 0.05), 0.04, 0.02, Color(1, 0.8, 0.8))
		"uv":  # 블랙라이트: 보라빛에서만 보이는 낙서
			_spot(Vector3(0.2, 1.45, -0.7), puppet, Color(0.45, 0.15, 1.0), 9.0, 30.0, 14.0, null, 1.5)
			_amb(env, Color(0.18, 0.06, 0.35), 0.08, 0.015, Color(0.6, 0.4, 1.0))
			_uv_text("돌아가", Vector3(-hw + 0.02, 1.7, -4.2), 90.0, 0.006)
			_uv_text("7번 수칙은 거짓", Vector3(hw - 0.02, 1.9, -9.0), -90.0, 0.004)
			_uv_text("→ → →", Vector3(-hw + 0.02, 0.9, -8.0), 90.0, 0.005)
			_uv_text("여기 있어", Vector3(0.0, 0.02, -3.2), 0.0, 0.006, true)
		"pools":  # 빛 웅덩이: 형광등 몇 개만 켜져 안개 속 빛기둥
			for i: int in lamp_slots.size():
				if i % 2 == 0:
					_lamp(lamp_slots[i], Color(1.0, 0.82, 0.6), 3.0, 0.0)
					var pos: Vector3 = lamp_slots[i][1]
					_spot(pos, pos + Vector3(0, -3.0, 0.01), Color(1.0, 0.8, 0.55), 12.0, 34.0, 6.0, null, 2.5)
			_amb(env, Color(0.3, 0.3, 0.4), 0.01, 0.045, Color(0.9, 0.85, 0.8))
	var we := WorldEnvironment.new()
	we.environment = env
	root3d.add_child(we)

func _amb(env: Environment, c: Color, e: float, fog: float, fog_col: Color) -> void:
	env.ambient_light_color = c
	env.ambient_light_energy = e
	env.volumetric_fog_density = fog
	env.volumetric_fog_albedo = fog_col

func _lamp(sl: Array, c: Color, emit: float, light: float) -> void:
	var m: StandardMaterial3D = sl[0]
	m.emission_enabled = emit > 0.0
	m.emission = c
	m.emission_energy_multiplier = emit
	m.albedo_color = Color(0.25, 0.25, 0.24) if emit <= 0.0 else Color(1, 1, 1)
	if light > 0.0:
		var al := AreaLight3D.new()
		al.area_size = Vector2(0.6, 1.2)
		al.area_range = 8.0
		al.light_energy = light
		al.light_color = c
		al.shadow_enabled = true
		al.position = sl[1]
		al.rotation_degrees = Vector3(-90, 0, 0)
		root3d.add_child(al)

func _spot(pos: Vector3, target: Vector3, c: Color, energy: float, angle: float, rng_m: float, proj: Texture2D, fog_e: float) -> SpotLight3D:
	var sp := SpotLight3D.new()
	sp.light_color = c
	sp.light_energy = energy
	sp.spot_angle = angle
	sp.spot_range = rng_m
	sp.shadow_enabled = true
	sp.light_volumetric_fog_energy = fog_e
	if proj != null:
		sp.light_projector = proj
	root3d.add_child(sp)
	sp.look_at_from_position(pos, target, Vector3.UP if absf((target - pos).normalized().y) < 0.95 else Vector3.FORWARD)
	return sp

func _omni(pos: Vector3, c: Color, energy: float, r: float) -> void:
	var o := OmniLight3D.new()
	o.position = pos
	o.light_color = c
	o.light_energy = energy
	o.omni_range = r
	root3d.add_child(o)

func _blinds_tex() -> Texture2D:
	var img := Image.create(256, 256, false, Image.FORMAT_RGBA8)
	for y: int in range(256):
		for x: int in range(256):
			var on: bool = (y % 32) < 20 and not (x > 122 and x < 134)
			var edge: float = clampf(1.0 - Vector2(x - 128, y - 128).length() / 128.0, 0.0, 1.0)
			var v: float = (1.0 if on else 0.0) * minf(1.0, edge * 2.5)
			img.set_pixel(x, y, Color(v, v, v))
	return _img_tex(img)

func _uv_text(t: String, pos: Vector3, yaw: float, px: float, floor_text: bool = false) -> void:
	var l := Label3D.new()
	l.text = t
	var f := SystemFont.new()
	f.font_names = PackedStringArray(["Noto Sans CJK KR", "Noto Sans KR", "Malgun Gothic", "Unifont"])
	l.font = f
	l.font_size = 64
	l.pixel_size = px
	l.shaded = false
	l.double_sided = true
	l.modulate = Color(0.55, 2.2, 0.5)
	l.outline_size = 0
	l.position = pos
	l.rotation_degrees = Vector3(-90 if floor_text else 0, yaw, 0)
	root3d.add_child(l)
