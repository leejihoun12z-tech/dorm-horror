"""회색 상자 판 짓기: 입력 자산(IA_*·IMC_Dorm) · 데이터 표(data/*.csv → DT_*) · 시험 복도 레벨.
실행(편집기가 끝나면 닫힘):
  UnrealEditor.exe DormHorror.uproject -ExecutePythonScript="<이 파일>"
몇 번 돌려도 같은 결과(있으면 다시 씀).
"""
import os

import unreal

PROJ = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
DATA = os.path.normpath(os.path.join(PROJ, "..", "data"))
MAP = "/Game/Maps/TestCorridor"
CUBE = "/Engine/BasicShapes/Cube.Cube"

tools = unreal.AssetToolsHelpers.get_asset_tools()
eal = unreal.EditorAssetLibrary
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)


def log(msg):
	unreal.log(f"[DormBuild] {msg}")


def fresh(path, cls, factory):
	"""있으면 그 자산을 다시 쓰고(다른 자산이 참조하고 있어 지우면 안 됨), 없으면 만든다."""
	if eal.does_asset_exist(path):
		return unreal.load_asset(path)
	folder, name = path.rsplit("/", 1)
	return tools.create_asset(name, folder, cls, factory)


# ---------- 입력 ----------
def make_action(name, value_type):
	ia = fresh(f"/Game/Input/{name}", unreal.InputAction, unreal.InputAction_Factory())
	ia.set_editor_property("value_type", value_type)
	eal.save_loaded_asset(ia)
	return ia


def add_map(imc, ia, key_name, mods=()):
	key = unreal.Key()
	key.import_text(key_name)
	imc.map_key(ia, key)
	if not mods:
		return
	# map_key가 돌려주는 것은 복사본이라, 목록을 꺼내 고친 뒤 다시 넣는다
	data = imc.get_editor_property("default_key_mappings")
	maps = list(data.get_editor_property("mappings"))
	m = maps[-1]
	objs = []
	for cls, props in mods:
		o = unreal.new_object(cls, outer=imc)
		for k, v in props.items():
			o.set_editor_property(k, v)
		objs.append(o)
	m.set_editor_property("modifiers", objs)
	maps[-1] = m
	data.set_editor_property("mappings", maps)
	imc.set_editor_property("default_key_mappings", data)


def build_input():
	A2 = unreal.InputActionValueType.AXIS2D
	B = unreal.InputActionValueType.BOOLEAN
	move = make_action("IA_Move", A2)
	look = make_action("IA_Look", A2)
	jump = make_action("IA_Jump", B)
	crouch = make_action("IA_Crouch", B)
	interact = make_action("IA_Interact", B)
	flash = make_action("IA_Flashlight", B)

	imc = fresh("/Game/Input/IMC_Dorm", unreal.InputMappingContext, unreal.InputMappingContext_Factory())
	imc.unmap_all()
	swz = (unreal.InputModifierSwizzleAxis, {})
	neg = (unreal.InputModifierNegate, {})
	# 조작 [확정] tech-plan D3: WASD · 마우스 · Space · Shift(누르는 동안) · E/왼쪽 클릭 · F
	add_map(imc, move, "W", [swz])
	add_map(imc, move, "S", [swz, neg])
	add_map(imc, move, "A", [neg])
	add_map(imc, move, "D")
	add_map(imc, look, "Mouse2D", [(unreal.InputModifierNegate, {"x": False, "y": True, "z": False})])
	add_map(imc, jump, "SpaceBar")
	add_map(imc, crouch, "LeftShift")
	add_map(imc, interact, "E")
	add_map(imc, interact, "LeftMouseButton")
	add_map(imc, flash, "F")
	eal.save_loaded_asset(imc)

	maps = imc.get_editor_property("default_key_mappings").get_editor_property("mappings")
	desc = [f"{m.get_editor_property('key').export_text()}:{len(m.get_editor_property('modifiers'))}" for m in maps]
	log(f"IMC_Dorm {len(maps)}개 {desc}")


# ---------- 데이터 표 ----------
def build_table(name, struct, csv):
	f = unreal.DataTableFactory()
	f.set_editor_property("struct", struct)
	dt = fresh(f"/Game/Data/{name}", unreal.DataTable, f)
	ok = unreal.DataTableFunctionLibrary.fill_data_table_from_csv_file(dt, os.path.join(DATA, csv))
	eal.save_loaded_asset(dt)
	rows = unreal.DataTableFunctionLibrary.get_data_table_row_names(dt)
	log(f"{name} ← {csv}: {ok}, 행 {len(rows)} {[str(r) for r in rows]}")


# ---------- 레벨 ----------
GRAY = None


def box(name, x, y, z, sx, sy, sz, cls=unreal.StaticMeshActor):
	"""(x,y,z)=가운데, (sx,sy,sz)=크기 cm"""
	a = eas.spawn_actor_from_class(cls, unreal.Vector(x, y, z))
	a.set_actor_label(name)
	a.set_actor_scale3d(unreal.Vector(sx / 100.0, sy / 100.0, sz / 100.0))
	if cls is unreal.StaticMeshActor:
		smc = a.static_mesh_component
		smc.set_static_mesh(unreal.load_asset(CUBE))
		smc.set_material(0, GRAY)
	return a


def thing(id_, x, y, z, sx, sy, sz):
	a = box(f"I_{id_}", x, y, z, sx, sy, sz, cls=unreal.DormInteractable)
	a.set_editor_property("id", id_)
	return a


def light(name, x, y, z, intensity, color, tag, radius=900.0):
	a = eas.spawn_actor_from_class(unreal.PointLight, unreal.Vector(x, y, z))
	a.set_actor_label(name)
	c = a.point_light_component
	c.set_mobility(unreal.ComponentMobility.MOVABLE)
	c.set_editor_property("intensity_units", unreal.LightUnits.CANDELAS)
	c.set_intensity(intensity)
	c.set_light_color(unreal.LinearColor(*color, 1.0))
	c.set_attenuation_radius(radius)
	a.tags = [tag]
	return a


def build_level():
	global GRAY
	GRAY = unreal.load_asset("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial")
	if eal.does_asset_exist(MAP):
		les.load_level(MAP)
		eas.destroy_actors(eas.get_all_level_actors())
	else:
		les.new_level(MAP)

	H = 280.0  # 천장 높이
	T = 20.0  # 벽 두께
	# 사감실: x -600..0, y -300..300 / 복도: x 0..2000, y -130..130
	box("Floor", 700, 0, -T / 2, 2600 + 2 * T, 600 + 2 * T, T)
	box("Ceiling", 700, 0, H + T / 2, 2600 + 2 * T, 600 + 2 * T, T)
	# 사감실 벽
	box("Office_Back", -600 - T / 2, 0, H / 2, T, 600, H)
	box("Office_L", -300, -300 - T / 2, H / 2, 600, T, H)
	box("Office_R", -300, 300 + T / 2, H / 2, 600, T, H)
	box("Office_FrontL", T / 2, -215, H / 2, T, 170, H)
	box("Office_FrontR", T / 2, 215, H / 2, T, 170, H)
	box("Office_Lintel", T / 2, 0, 250, T, 260, 60)
	# 복도 벽
	box("Corr_L", 1000, -130 - T / 2, H / 2, 2000, T, H)
	box("Corr_R", 1000, 130 + T / 2, H / 2, 2000, T, H)
	box("Corr_End", 2000 + T / 2, 0, H / 2, T, 260, H)

	# 쓰는 물건 (Id = data/interactables.csv 행)
	thing("desk", -450, -200, 37.5, 70, 140, 75)
	thing("bed", -470, 200, 25, 200, 100, 50)
	thing("roll_book", 250, -127, 150, 80, 6, 60)
	thing("broken_lamp", 800, -125, 210, 30, 10, 30)
	thing("patrol_check", 1995, 0, 140, 6, 40, 40)
	for i, x in enumerate((500, 1000, 1500)):
		thing("room_door", x, 127, 105, 100, 6, 210).set_actor_label(f"I_room_door_{i + 1}")

	# 불: 천장(낮) · 비상등(밤)
	for i, x in enumerate((-450, -150)):
		light(f"L_Office_{i}", x, 0, H - 30, 14.0, (1.0, 0.93, 0.82), "Dorm_Ceiling")
	for i, x in enumerate(range(200, 2000, 400)):
		light(f"L_Corr_{i}", x, 0, H - 30, 7.0, (0.92, 1.0, 0.95), "Dorm_Ceiling")
	light("L_Exit", 1960, 0, 240, 1.5, (0.3, 1.0, 0.45), "Dorm_Night", radius=500.0)

	# 노출 고정 (밤이 자동으로 밝아지지 않게)
	ppv = eas.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0, 0, 0))
	ppv.set_actor_label("PPV")
	ppv.set_editor_property("unbound", True)
	s = ppv.settings
	s.set_editor_property("override_auto_exposure_bias", True)
	s.set_editor_property("auto_exposure_bias", -1.5)
	ppv.set_editor_property("settings", s)

	ps = eas.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(-250, 0, 100))
	ps.set_actor_label("PlayerStart")

	les.save_current_level()
	log(f"레벨 저장 {MAP}: 물체 {len(eas.get_all_level_actors())}개")


def main():
	build_input()
	build_table("DT_DayPhases", unreal.DormPhaseRow.static_struct(), "day_phases.csv")
	build_table("DT_Interactables", unreal.DormInteractableRow.static_struct(), "interactables.csv")
	build_level()
	log("끝")


main()
