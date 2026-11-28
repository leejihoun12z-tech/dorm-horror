"""확인용: 시험 복도를 플레이하며 스스로 몇 장 찍고 편집기를 닫는다 (사람 조작 없음).
실행: UnrealEditor.exe DormHorror.uproject -ExecCmds="py <이 파일>"
결과: Saved/Screenshots/WindowsEditor/ScreenShot*.png (UI 포함) + 로그 [DormShot]
"""
import builtins

import unreal

les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)


def log(msg):
	unreal.log(f"[DormShot] {msg}")


def world():
	return ues.get_game_world()


def pawn():
	return unreal.GameplayStatics.get_player_pawn(world(), 0)


def day():
	return unreal.DormDaySubsystem.get(world())


def put(x, y, z, yaw, pitch=0.0):
	p = pawn()
	p.set_actor_location(unreal.Vector(x, y, z), False, True)
	p.get_controller().set_control_rotation(unreal.Rotator(roll=0.0, pitch=pitch, yaw=yaw))


def shot(tag):
	cam = pawn().get_component_by_class(unreal.CameraComponent)
	f = pawn().get_focus()
	log(f"{tag}: {day().get_day()}일차 {day().get_phase_id()} 밤={day().is_night()} 초점={f.id if f else None} 눈높이={cam.get_world_location().z:.0f}")
	unreal.SystemLibrary.execute_console_command(world(), "shot showui")


def step_crouch_report():
	cam = pawn().get_component_by_class(unreal.CameraComponent)
	log(f"숙임={pawn().get_editor_property('is_crouched')} 눈높이={cam.get_world_location().z:.0f}")


STEPS = [
	(0.0, lambda: put(-300, -120, 100, -152, -28)),
	(1.0, lambda: shot("01 책상 보기")),
	(1.0, lambda: pawn().interact()),
	(0.5, lambda: shot("02 업무 끝")),
	(0.5, lambda: put(60, 0, 100, 0, 0)),
	(1.0, lambda: shot("03 낮 복도")),
	(0.5, lambda: (day().advance_phase(), day().advance_phase())),
	(0.3, lambda: put(60, 0, 100, 0, 0)),
	(0.2, lambda: pawn().set_flashlight(True)),
	(1.5, lambda: shot("04 밤 순찰 손전등")),
	(0.5, lambda: put(1820, -30, 100, 8, -3)),
	(1.0, lambda: shot("05 복도 끝 체크 지점")),
	(0.5, lambda: pawn().crouch()),
	(1.0, step_crouch_report),
	(0.5, lambda: unreal.SystemLibrary.quit_editor()),
]

st = {"t": 0.0, "i": 0, "started": False, "wait": 0.0}
builtins._dorm_shot = st


def tick(dt):
	if world() is None or pawn() is None:
		st["wait"] += dt
		if st["wait"] > 60:
			log("플레이가 안 시작됨")
			unreal.SystemLibrary.quit_editor()
		return
	if not st["started"]:
		st["started"] = True
		st["t"] = -2.0  # 첫 화면 안정될 때까지
		log("플레이 시작")
	st["t"] += dt
	while st["i"] < len(STEPS) and st["t"] >= STEPS[st["i"]][0]:
		st["t"] -= STEPS[st["i"]][0]
		try:
			STEPS[st["i"]][1]()
		except Exception as e:  # noqa: BLE001
			log(f"단계 {st['i']} 실패: {e}")
		st["i"] += 1


les.load_level("/Game/Maps/TestCorridor")
builtins._dorm_shot_handle = unreal.register_slate_post_tick_callback(tick)
les.editor_request_begin_play()
