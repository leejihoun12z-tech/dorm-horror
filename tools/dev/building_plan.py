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
	"lock": "#8c8c8c", "yard": "#dfe9d8", "shop": "#8fc98f", "old": "#c9b8d6"}

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
	ax.annotate("현관 (바깥문)", xy=(OUT / 2, 0), xytext=(OUT / 2, -2.2), ha="center", fontsize=8.5,
		arrowprops=dict(arrowstyle="-|>", color="#333"))


# 1층 (§14, 사용자 11-28 3차): 식당 없음 · 매점 3칸 · 세탁실 2칸 · 휴게실+취사실 합침 · 독서실+창고 → 창고
F1_MID = {
	"S": [("택배·우편실\n신발장", "fac"), ("현관 홀\n게시판", "cor"), ("사감실\n(창구→현관)", "staff")],
	"E": [("매점 (3칸, 약 15평)\n알바생 1 · 계산대\n진열대 · 음료장\n\n안쪽 벽에\n막힌 옛 배식구\n\n밤엔 셔터", "shop", 3)],
	"N": [("세탁실 (2칸, 약 10평)\n세탁기 6 · 건조기 2\n전원 스위치 함", "fac", 2), None, None],
	"W": [("창고 (2칸)", "lock", 2), None, ("번호가 다른\n옛 문패 방\n(잠김)", "old")],
}
NE_LOUNGE = [(OUT - R, B), (OUT, B), (OUT, OUT), (B - CELL, OUT), (B - CELL, OUT - R), (OUT - R, OUT - R)]
F1_CORNER = {"SE": ("주 계단\n+ 엘리베이터\n(B 버튼은\n열쇠로 막힘)", "stair"), "SW": ("공용 화장실\n+ 사감 화장실", "fac"),
	"NE": ("휴게실 · 취사실 (합침, 약 20평)\nTV · 소파 · 냉장고\n싱크 · 전자레인지 · 라면 조리", "fac", NE_LOUNGE, (OUT - R * 0.75, OUT - R * 0.5)),
	"NW": ("비상계단 (잠김)\n지하 철문\n(잠김)", "lock")}

F2_MID = {  # 번호 = 순찰 순서(계단에서 시계 방향)
	"S": [("202", "room"), ("201", "room"), ("층 휴게\n정수기\n소화기", "fac")],
	"W": [("203", "room"), ("204\n(4인실)\n옛 큰 방", "old"), ("205", "room")],
	"N": [("206", "room"), ("207", "room"), ("208", "room")],
	"E": [("211", "room"), ("210", "room"), ("209", "room")],
}
F2_CORNER = {"SE": ("주 계단\n+ 엘리베이터", "stair"), "SW": ("샤워실", "fac"),
	"NE": ("화장실·세면\n(여자만)", "fac"), "NW": ("비상계단 (잠김)\n앞 막다른 구석", "lock")}

if __name__ == "__main__":
	fig, axs = plt.subplots(1, 2, figsize=(17, 9.6))
	draw_floor(axs[0], "1층 — 사감실에서 출발·복귀", F1_MID, F1_CORNER, f1_extra)
	draw_floor(axs[1], "2층 (3·4층도 같은 뼈대) — 2인실 10 + 4인실 1 (번호 = 순찰 순서)", F2_MID, F2_CORNER)
	loop = 4 * (OUT - 2 * R - CW)
	fig.text(0.5, 0.015,
		f"위에서 본 평면 · 남쪽이 아래 · 바깥 {OUT:g}×{OUT:g}m · 방 {CELL:g}×{R:g}m · 복도 {CW:g}m · 복도 한 바퀴 약 {loop:.0f}m (모두 [작업값]) · "
		"초록 = 순찰 길(시계 방향) · 파란 점선 = 중정 창 · 보라 = 옛 건물 흔적",
		ha="center", fontsize=9.5)
	fig.tight_layout(rect=(0, 0.035, 1, 0.97))
	fig.savefig(sys.argv[1], dpi=110)
