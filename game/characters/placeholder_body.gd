class_name PlaceholderBody
extends CharacterView
## 대역 몸: 실제 로우폴리 모델이 오기 전, 시험 장면을 먼저 돌려 보기 위한 회색 상자 사람.
## 키 1.58m · 데포르메 5.5등신 [작업값] · 구미호 색(흰 머리·크림 스웨터·청바지) 2~3색.
## 얼굴 그림 3장도 코드로 그린 대역이다 (실제 얼굴은 우리 일러스트에서 가져옴).

const HEIGHT: float = 1.58
const HEADS: float = 5.5
const FACE_TEX_SIZE: int = 128

@export var hair_color: Color = Color(0.95, 0.94, 0.92)
@export var hair_tip_color: Color = Color(0.8, 0.16, 0.18)
@export var top_color: Color = Color(0.93, 0.88, 0.8)
@export var bottom_color: Color = Color(0.32, 0.42, 0.6)
@export var skin_color: Color = Color(1.0, 0.89, 0.82)

func _ready() -> void:
	_build()
	super._ready()

func _build() -> void:
	var head_r: float = HEIGHT / HEADS * 0.55
	var head_y: float = HEIGHT - head_r
	_part(SphereMesh.new(), Vector3(head_r * 2.0, head_r * 2.0, head_r * 2.0), Vector3(0, head_y, 0), Vector3.ZERO, hair_color)
	_part(_capsule(0.13, 0.5), Vector3.ONE, Vector3(0, 1.04, 0), Vector3.ZERO, top_color)
	for side: float in [-1.0, 1.0]:
		_part(_capsule(0.065, 0.8), Vector3.ONE, Vector3(side * 0.07, 0.4, 0), Vector3.ZERO, bottom_color)
		_part(_capsule(0.045, 0.48), Vector3.ONE, Vector3(side * 0.18, 1.02, 0), Vector3(0, 0, side * 0.12), top_color)
		_part(_cone(0.05, 0.14), Vector3.ONE, Vector3(side * 0.085, head_y + head_r * 0.95, -0.01), Vector3(0, 0, -side * 0.35), hair_color)
	_part(_capsule(0.09, 0.62), Vector3.ONE, Vector3(0, 0.8, -0.3), Vector3(-0.9, 0, 0), hair_color)
	_part(_capsule(0.06, 0.16), Vector3.ONE, Vector3(0, 0.99, -0.54), Vector3(-0.9, 0, 0), hair_tip_color)

	var face := MeshInstance3D.new()
	face.name = "Face"
	var quad := QuadMesh.new()
	quad.size = Vector2(head_r * 1.5, head_r * 1.5)
	face.mesh = quad
	face.position = Vector3(0, head_y - head_r * 0.15, head_r * 1.01)
	add_child(face)
	face_mesh = face
	face_surface = 0
	if expressions.is_empty():
		expressions = {
			&"neutral": _draw_face(&"neutral"),
			&"smile": _draw_face(&"smile"),
			&"hollow": _draw_face(&"hollow"),
		}

func _part(mesh: PrimitiveMesh, scale_v: Vector3, at: Vector3, rot: Vector3, color: Color) -> void:
	var mi := MeshInstance3D.new()
	mi.mesh = mesh
	mi.scale = scale_v
	mi.position = at
	mi.rotation = rot
	var mat := ShaderMaterial.new()
	mat.shader = TOON_SHADER
	mat.set_shader_parameter("tint", color)
	mi.material_override = mat
	add_child(mi)

func _capsule(radius: float, height: float) -> CapsuleMesh:
	var m := CapsuleMesh.new()
	m.radius = radius
	m.height = height
	m.radial_segments = 8
	m.rings = 2
	return m

func _cone(radius: float, height: float) -> CylinderMesh:
	var m := CylinderMesh.new()
	m.top_radius = 0.0
	m.bottom_radius = radius
	m.height = height
	m.radial_segments = 4
	return m

## 대역 얼굴: 피부 타원 + 눈 2개 + 입. hollow = 눈 하이라이트 꺼짐·미소 넓어짐 (변이 1단계 예)
func _draw_face(kind: StringName) -> ImageTexture:
	var s: int = FACE_TEX_SIZE
	var img := Image.create(s, s, false, Image.FORMAT_RGBA8)
	img.fill(Color(0, 0, 0, 0))
	var c := Vector2(s * 0.5, s * 0.5)
	var line := Color(0.15, 0.08, 0.1)
	var eye_col := Color(0.75, 0.12, 0.15)
	for y: int in range(s):
		for x: int in range(s):
			var p := Vector2(x, y)
			if ((p - c) / Vector2(s * 0.48, s * 0.5)).length() <= 1.0:
				img.set_pixel(x, y, skin_color)
	for side: float in [-1.0, 1.0]:
		var e := c + Vector2(side * s * 0.2, -s * 0.02)
		for y: int in range(s):
			for x: int in range(s):
				var d := (Vector2(x, y) - e) / Vector2(s * 0.085, s * 0.12)
				if kind == &"smile":
					# 웃는 눈: 위로 볼록한 호
					var t: float = d.x
					if absf(t) <= 1.0 and absf(d.y + (1.0 - t * t) * 0.6) < 0.18:
						img.set_pixel(x, y, line)
				elif d.length() <= 1.0:
					img.set_pixel(x, y, line if d.length() > 0.8 else eye_col)
					if kind != &"hollow" and (Vector2(x, y) - (e + Vector2(-s * 0.025, -s * 0.04))).length() < s * 0.025:
						img.set_pixel(x, y, Color.WHITE)
	var mouth_w: float = s * (0.16 if kind == &"hollow" else 0.07)
	var mouth_c := c + Vector2(0, s * 0.24)
	for x: int in range(int(mouth_c.x - mouth_w), int(mouth_c.x + mouth_w) + 1):
		var t: float = (x - mouth_c.x) / mouth_w
		var curve: float = (1.0 - t * t) * (s * 0.04 if kind != &"neutral" else s * 0.015)
		var y: int = int(mouth_c.y + curve)
		img.set_pixel(x, y, line)
		img.set_pixel(x, y + 1, line)
	if kind == &"hollow":
		# 송곳니 하나
		for k: int in range(int(s * 0.04)):
			img.set_pixel(int(mouth_c.x + s * 0.05), int(mouth_c.y + s * 0.03) + k, Color.WHITE)
	return ImageTexture.create_from_image(img)
