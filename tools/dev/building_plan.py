"""별관 1층·2층 평면 초안 (docs/plan/building-layout.md §10·§11). 크기·배치는 [작업값].
ㅁ자 편복도: 방은 바깥쪽, 복도는 중정 쪽. 아래 숫자만 바꾸면 다시 그려진다.
사용: python tools/dev/building_plan.py <출력.png>
"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Polygon, Rectangle

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

# ---- 크기 [작업값] (§11 추천안: 방 3×5.5m, 복도 1.8m) ----
R = 5.5  # 방 깊이
CW = 1.8  # 복도 폭
CELL = 3.0  # 방 폭
N = 3  # 날개 가운데 칸 수
Y = N * CELL  # 중정 한 변
WING = R + CW  # 날개 깊이
OUT = Y + 2 * WING  # 바깥 한 변

C = {"room": "#f1e6d2", "cor": "#a7b0b9", "stair": "#c0504d", "fac": "#7fa7c9", "staff": "#e5b85c",
	"lock": "#8c8c8c", "yard": "#dfe9d8", "single": "#f6d2a8", "shop": "#8fc98f", "old": "#c9b8d6"}

MID = {
	"S": [(WING + i * CELL, 0, CELL, R) for i in range(N)],  # 서→동
	"E": [(OUT - R, WING + i * CELL, R, CELL) for i in range(N)],  # 남→북
	"N": [(WING + i * CELL, OUT - R, CELL, R) for i in range(N)],  # 서→동
	"W": [(0, WING + i * CELL, R, CELL) for i in range(N)],  # 남→북
}
A, B = WING, WING + Y
CORNER = {
	"SW": [(0, 0), (A, 0), (A, R), (R, R), (R, A), (0, A)],
	"SE": [(B, 0), (OUT, 0), (OUT, A), (OUT - R, A), (OUT - R, R), (B, R)],
	"NE": [(OUT - R, B), (OUT, B), (OUT, OUT), (B, OUT), (B, OUT - R), (OUT - R, OUT - R)],
	"NW": [(0, B), (R, B), (R, OUT - R), (A, OUT - R), (A, OUT), (0, OUT)],
}
K = R * 0.48
CORNER_C = {"SW": (K, K), "SE": (OUT - K, K), "NE": (OUT - K, OUT - K), "NW": (K, OUT - K)}


def draw_floor(ax, title, mid, corner, extra=None):
	ax.add_patch(Rectangle((A, A), Y, Y, fc=C["yard"], ec="#555", lw=0.8))
	ax.text(OUT / 2, OUT / 2, f"중정 {Y:g}×{Y:g}m\n(1층에서만 나감)", ha="center", va="center", fontsize=8.5, color="#4a6b3a")
	ring = [(R, R, OUT - 2 * R, CW), (R, OUT - R - CW, OUT - 2 * R, CW),
		(R, R + CW, CW, OUT - 2 * R - 2 * CW), (OUT - R - CW, R + CW, CW, OUT - 2 * R - 2 * CW)]
	for x, y, w, h in ring:
		ax.add_patch(Rectangle((x, y), w, h, fc=C["cor"], ec="none"))
	ax.add_patch(Rectangle((A, A), Y, Y, fc="none", ec="#3b6fb6", lw=1.6, ls=(0, (3, 2))))
	# 칸: (이름, 종류) 또는 (이름, 종류, 칸 수) — 여러 칸을 합침. None = 앞 칸에 합쳐짐
	for side, cells in MID.items():
		entries = mid[side]
		i = 0
		while i < len(cells):
			e = entries[i]
			if e is None:
				i += 1
				continue
			label, kind, span = (tuple(e) + (1,))[:3]
			x, y, w, h = cells[i]
			if side in ("S", "N"):
				w = CELL * span
			else:
				h = CELL * span
			ax.add_patch(Rectangle((x, y), w, h, fc=C[kind], ec="#333", lw=0.6))
			ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=6.8)
			i += span
	# 모서리: (이름, 종류[, 다른 모양 점들, 글자 자리])
	for k, pts in CORNER.items():
		e = corner[k]
		label, kind = e[0], e[1]
		poly = e[2] if len(e) > 2 else pts
		pos = e[3] if len(e) > 3 else CORNER_C[k]
		ax.add_patch(Polygon(poly, closed=True, fc=C[kind], ec="#333", lw=0.6))
		ax.text(*pos, label, ha="center", va="center", fontsize=6.8)
	# 순찰 길: 시계 방향 (남동 계단 → 서 → 북 → 동 → 계단)
	m0, m1 = R + CW / 2, OUT - R - CW / 2
	path = [(m1 - 0.3, m0), (m0, m0), (m0, m1), (m1, m1), (m1, m0 + 0.6)]
	for a, b in zip(path, path[1:]):
		ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=10, color="#1a7f37", lw=1.8))
	if extra:
		extra(ax)
	ax.set_title(title, fontsize=12)
	ax.set_xlim(-1.5, OUT + 1.5)
	ax.set_ylim(-3.0, OUT + 2.0)
	ax.set_aspect("equal")
	ax.axis("off")


def f1_extra(ax):
	ax.annotate("현관 (바깥문)", xy=(A + CELL / 2, 0), xytext=(A + CELL / 2, -2.2), ha="center", fontsize=8.5,
		arrowprops=dict(arrowstyle="-|>", color="#333"))


# 1층 (§14, 사용자 11-28 3차): 식당 없음 · 매점 3칸 · 세탁실 2칸 · 휴게실+취사실 합침 · 독서실+창고 → 창고
F1_MID = {
	"S": [("현관 홀\n신발장 · 우편함\n게시판", "cor"),
		("사감실 (2칸, 약 10평)\n책상 · 창구(← 현관) · 열쇠함\n택배 보관 선반\n숙직 간이침대", "staff", 2), None],
	"E": [("매점 (3칸, 약 15평)\n알바생 1 · 계산대\n진열대 · 음료장\n\n안쪽 벽에\n막힌 옛 배식구\n\n밤엔 셔터", "shop", 3)],
	"N": [("세탁실 (2칸, 약 10평)\n세탁기 6 · 건조기 2\n전원 스위치 함", "fac", 2), None, None],
	"W": [("창고 (2칸)", "lock", 2), None, ("번호가 다른\n옛 문패 방\n(잠김)", "old")],
}
NE_LOUNGE = [(OUT - R, B), (OUT, B), (OUT, OUT), (B - CELL, OUT), (B - CELL, OUT - R), (OUT - R, OUT - R)]
F1_CORNER = {"SE": ("주 계단\n+ 엘리베이터\n(B 버튼은\n열쇠로 막힘)", "stair"), "SW": ("공용 화장실\n+ 사감 화장실", "fac"),
	"NE": ("휴게실 · 취사실 (합침, 약 20평)\nTV · 소파 · 냉장고\n싱크 · 전자레인지 · 라면 조리", "fac", NE_LOUNGE, (OUT - R * 0.75, OUT - R * 0.5)),
	"NW": ("비상계단 (잠김)\n지하 철문\n(잠김)", "lock")}

F2_CORNER = {"SE": ("주 계단\n+ 엘리베이터", "stair"), "SW": ("샤워실", "fac"),
	"NE": ("화장실·세면\n(여자만)", "fac"), "NW": ("비상계단 (잠김)\n앞 막다른 구석", "lock")}

# 방 종류 (§18, 사용자 11-28: 1인실·2인실 섞기 + 32명) — 방 번호 끝 두 자리
SINGLE = (3, 5, 6, 7, 9, 10)  # 1인실 (나머지 01·02·08·11 = 2인실)
QUAD = 4  # 옛 큰 방 — 비어 있음(창고)


def floor_rooms(f, vacant=(), single=SINGLE):
	"""층 뼈대를 f층 번호로. 번호 = 순찰 순서(계단에서 시계 방향). vacant = 빈방(잠김)"""
	def cell(n):
		num = f"{f}{n:02d}"
		if n in vacant:
			return (f"{num}\n빈방\n(잠김)", "lock")
		if n == QUAD:
			return (f"{num}\n옛 큰 방\n(비어 있음\n· 창고)", "old")
		if n in single:
			return (f"{num}\n1인실", "single")
		return (f"{num}\n2인실", "room")
	return {
		"S": [cell(2), cell(1), ("층 휴게\n정수기\n소화기", "fac")],
		"W": [cell(3), cell(4), cell(5)],
		"N": [cell(6), cell(7), cell(8)],
		"E": [cell(11), cell(10), cell(9)],
	}


F2_MID = floor_rooms(2)
F3_MID = floor_rooms(3)
F3_MID["S"][2] = ("층 휴게\n정수기 · 소화기\n공중전화", "fac")
F3_CORNER = dict(F2_CORNER)
# 4층: 거의 빈 층 — 401(2인실)·402·411(1인실)만 사람
F4_MID = floor_rooms(4, vacant=(3, 4, 5, 6, 7, 8, 9, 10), single=(2, 11))
F4_CORNER = dict(F2_CORNER, SE=("주 계단\n+ 엘리베이터\n↑ 옥상 계단\n(옥상 문 잠김)", "stair"),
	NW=("비상계단 (잠김)\n앞 막다른 구석\n\n★ '복도 끝' 창문\n(수칙 6)", "lock"))


def f4_extra(ax):
	# 수칙 6 창문 표시: 북서 막다른 구석의 바깥벽
	ax.plot([0, 0], [OUT - R + 0.6, OUT - 0.6], color="#d62728", lw=4)
	ax.annotate("창문", xy=(0, OUT - R / 2), xytext=(-1.4, OUT - R / 2), fontsize=8, color="#d62728", ha="right", va="center",
		arrowprops=dict(arrowstyle="-", color="#d62728"))


def draw_roof(ax):
	"""옥상: ㅁ자 지붕 고리 + 가운데 중정 구멍(난간). 평소 잠김."""
	ax.add_patch(Rectangle((0, 0), OUT, OUT, fc="#d9d6cf", ec="#333", lw=0.8))
	ax.add_patch(Rectangle((A, A), Y, Y, fc="white", ec="#c0504d", lw=2.0, ls=(0, (4, 2))))
	ax.text(OUT / 2, OUT / 2, "중정 위 빈 공간\n(낮은 난간 — 붉은 점선)\n아래로 각 층 창이 보임", ha="center", va="center", fontsize=8.5, color="#8a3b3b")
	ax.add_patch(Rectangle((0.2, 0.2), OUT - 0.4, OUT - 0.4, fc="none", ec="#c0504d", lw=1.2, ls=(0, (4, 2))))
	# 계단탑 + 옥상 문 + 엘리베이터 기계실 (남동)
	ax.add_patch(Rectangle((OUT - 5.2, 0.6), 4.6, 4.2, fc=C["stair"], ec="#333", lw=0.8))
	ax.text(OUT - 2.9, 2.7, "계단탑\n옥상 문(잠김)\n= 점검 8", ha="center", va="center", fontsize=7)
	ax.add_patch(Rectangle((OUT - 8.0, 0.6), 2.6, 2.6, fc="#8c8c8c", ec="#333", lw=0.8))
	ax.text(OUT - 6.7, 1.9, "엘리베이터\n기계실", ha="center", va="center", fontsize=6.5)
	# 물탱크 (북동)
	ax.add_patch(matplotlib.patches.Circle((OUT - 3.2, OUT - 3.2), 2.2, fc="#7fa7c9", ec="#333", lw=0.8))
	ax.text(OUT - 3.2, OUT - 3.2, "물탱크", ha="center", va="center", fontsize=7)
	# 빨래 줄 (남 날개 지붕)
	for k in range(3):
		yy = 1.8 + k * 1.3
		ax.plot([A - 3.0, OUT - 8.6], [yy, yy], color="#555", lw=0.8)
	ax.text((A - 3.0 + OUT - 8.6) / 2, 5.6, "빨래 줄", ha="center", fontsize=7, color="#333")
	# 옛 굴뚝 (북서, 원래 건물 흔적 — 지하와 이어짐?)
	ax.add_patch(Rectangle((1.2, OUT - 3.0), 1.8, 1.8, fc=C["old"], ec="#333", lw=0.8))
	ax.text(2.1, OUT - 4.0, "옛 굴뚝\n(막힘)", ha="center", va="top", fontsize=7)
	# 비상계단 꼭대기 해치
	ax.add_patch(Rectangle((1.2, OUT - 7.0), 1.6, 1.6, fc="#8c8c8c", ec="#333", lw=0.8))
	ax.text(3.2, OUT - 6.2, "비상계단\n해치(잠김)", ha="left", va="center", fontsize=6.5)
	# 옛 TV 안테나
	ax.plot([OUT / 2 + 5, OUT / 2 + 5], [OUT - 4.5, OUT - 1.0], color="#333", lw=1.2)
	for d in (0.6, 1.2, 1.8):
		ax.plot([OUT / 2 + 5 - d, OUT / 2 + 5 + d], [OUT - 1.0 - d, OUT - 1.0 - d], color="#333", lw=0.8)
	ax.text(OUT / 2 + 5, OUT - 5.0, "옛 TV 안테나", ha="center", va="top", fontsize=6.5)
	ax.set_title("옥상 — 평소 잠김 (3주차·후반)", fontsize=12)
	ax.set_xlim(-1.5, OUT + 1.5)
	ax.set_ylim(-3.0, OUT + 2.0)
	ax.set_aspect("equal")
	ax.axis("off")


if __name__ == "__main__" and "--upper" in sys.argv:
	fig, axs = plt.subplots(1, 3, figsize=(24, 9.2))
	draw_floor(axs[0], "3층 — 301~311 (2주차부터 순찰)", F3_MID, F3_CORNER)
	draw_floor(axs[1], "4층 — 거의 빈 층: 401·402·411만 4명 (3주차)", F4_MID, F4_CORNER, f4_extra)
	draw_roof(axs[2])
	fig.text(0.5, 0.015,
		"3·4층은 2층과 같은 뼈대 · 4층 북서 막다른 구석에 '복도 끝' 창문(수칙 6) · 옥상은 주 계단 위 계단탑으로만 나감 · 모두 [작업값]",
		ha="center", fontsize=10)
	fig.tight_layout(rect=(0, 0.035, 1, 0.97))
	fig.savefig(sys.argv[1], dpi=100)
elif __name__ == "__main__":
	fig, axs = plt.subplots(1, 2, figsize=(17, 9.6))
	draw_floor(axs[0], "1층 — 사감실에서 출발·복귀", F1_MID, F1_CORNER, f1_extra)
	draw_floor(axs[1], "2층 (3층도 같음) — 1인실 6 · 2인실 4 = 14명", F2_MID, F2_CORNER)
	loop = 4 * (OUT - 2 * R - CW)
	fig.text(0.5, 0.015,
		f"위에서 본 평면 · 남쪽이 아래 · 바깥 {OUT:g}×{OUT:g}m · 방 {CELL:g}×{R:g}m · 복도 {CW:g}m · 복도 한 바퀴 약 {loop:.0f}m (모두 [작업값]) · "
		"초록 = 순찰 길(시계 방향) · 파란 점선 = 중정 창 · 보라 = 옛 건물 흔적 · 연베이지 = 2인실 · 주황 = 1인실",
		ha="center", fontsize=9.5)
	fig.tight_layout(rect=(0, 0.035, 1, 0.97))
	fig.savefig(sys.argv[1], dpi=110)
