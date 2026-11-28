"""별관 1층·2층 평면 초안 (docs/plan/building-layout.md §10). 크기·배치는 [작업값].
ㅁ자: 바깥 27×27m, 중정 12×12m, 날개 깊이 7.5m(방 5.5 + 복도 2.0, 편복도 — 복도는 중정 쪽).
사용: python tools/dev/building_plan.py <출력.png>
"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Polygon, Rectangle

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

C = {"room": "#f1e6d2", "cor": "#a7b0b9", "stair": "#c0504d", "fac": "#7fa7c9", "staff": "#e5b85c",
	"lock": "#8c8c8c", "yard": "#dfe9d8", "shop": "#8fc98f", "old": "#c9b8d6"}
OUT, CY0, CY1 = 27.0, 7.5, 19.5  # 바깥, 중정 범위
R = 5.5  # 방 깊이

# 칸 이름: 남(S)·동(E)·북(N)·서(W) 가운데 3칸 + 모서리 4개
MID = {
	"S": [(7.5 + i * 4, 0, 4, R) for i in range(3)],  # 서→동
	"E": [(OUT - R, 7.5 + i * 4, R, 4) for i in range(3)],  # 남→북
	"N": [(7.5 + i * 4, OUT - R, 4, R) for i in range(3)],
	"W": [(0, 7.5 + i * 4, R, 4) for i in range(3)],
}
CORNER = {
	"SW": [(0, 0), (7.5, 0), (7.5, R), (R, R), (R, 7.5), (0, 7.5)],
	"SE": [(19.5, 0), (OUT, 0), (OUT, 7.5), (OUT - R, 7.5), (OUT - R, R), (19.5, R)],
	"NE": [(OUT - R, 19.5), (OUT, 19.5), (OUT, OUT), (19.5, OUT), (19.5, OUT - R), (OUT - R, OUT - R)],
	"NW": [(0, 19.5), (R, 19.5), (R, OUT - R), (7.5, OUT - R), (7.5, OUT), (0, OUT)],
}
CORNER_C = {"SW": (2.6, 2.6), "SE": (24.4, 2.6), "NE": (24.4, 24.4), "NW": (2.6, 24.4)}


def draw_floor(ax, title, mid, corner, extra=None):
	ax.add_patch(Rectangle((CY0, CY0), 12, 12, fc=C["yard"], ec="#555", lw=0.8))
	ax.text(13.5, 13.5, "중정\n(1층에서만 나감)", ha="center", va="center", fontsize=9, color="#4a6b3a")
	# 복도 고리
	ring = [(R, R, OUT - 2 * R, 2), (R, OUT - R - 2, OUT - 2 * R, 2), (R, R + 2, 2, OUT - 2 * R - 4), (OUT - R - 2, R + 2, 2, OUT - 2 * R - 4)]
	for x, y, w, h in ring:
		ax.add_patch(Rectangle((x, y), w, h, fc=C["cor"], ec="none"))
	# 중정 창 (점선)
	ax.add_patch(Rectangle((CY0, CY0), 12, 12, fc="none", ec="#3b6fb6", lw=1.6, ls=(0, (3, 2))))
	for side, cells in MID.items():
		for (x, y, w, h), (label, kind) in zip(cells, mid[side]):
			ax.add_patch(Rectangle((x, y), w, h, fc=C[kind], ec="#333", lw=0.6))
			ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=7.2)
	for k, pts in CORNER.items():
		label, kind = corner[k]
		ax.add_patch(Polygon(pts, closed=True, fc=C[kind], ec="#333", lw=0.6))
		ax.text(*CORNER_C[k], label, ha="center", va="center", fontsize=7.2)
	# 순찰 길: 시계 방향 (계단 SE에서 출발 → 서 → 북 → 동 → 계단)
	m0, m1 = R + 1, OUT - R - 1
	path = [(m1 - 0.3, m0), (m0, m0), (m0, m1), (m1, m1), (m1, m0 + 0.6)]
	for a, b in zip(path, path[1:]):
		ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=10, color="#1a7f37", lw=1.8))
	if extra:
		extra(ax)
	ax.set_title(title, fontsize=12)
	ax.set_xlim(-1.5, OUT + 1.5)
	ax.set_ylim(-3.2, OUT + 2.5)
	ax.set_aspect("equal")
	ax.axis("off")


def f1_extra(ax):
	ax.annotate("현관 (바깥문)", xy=(13.5, 0), xytext=(13.5, -2.3), ha="center", fontsize=8.5,
		arrowprops=dict(arrowstyle="-|>", color="#333"))


F1_MID = {
	"S": [("택배·우편실\n신발장", "fac"), ("현관 홀\n게시판", "cor"), ("사감실\n(창구→현관)", "staff")],
	"E": [("식당", "fac"), ("식당", "fac"), ("옛 배식구\n(막힘)", "old")],
	"N": [("세탁실", "fac"), ("휴게실\n냉장고·TV", "fac"), ("매점\n(밤엔 셔터)\n자판기", "shop")],
	"W": [("수조 방\n(습성 배려)", "room"), ("창고", "lock"), ("번호가 다른\n옛 문패 방\n(잠김)", "old")],
}
F1_CORNER = {"SE": ("주 계단\n(위층으로)", "stair"), "SW": ("공용 화장실\n+ 사감 화장실", "fac"),
	"NE": ("주방\n식료품 창고", "fac"), "NW": ("비상계단 (잠김)\n지하 철문", "lock")}

F2_MID = {  # 번호 = 순찰 순서(계단에서 시계 방향)
	"S": [("202", "room"), ("201", "room"), ("층 휴게\n정수기·소화기", "fac")],
	"W": [("203", "room"), ("204 (4인실)\n옛 큰 방", "old"), ("205", "room")],
	"N": [("206", "room"), ("207", "room"), ("208", "room")],
	"E": [("211", "room"), ("210", "room"), ("209", "room")],
}
F2_CORNER = {"SE": ("주 계단", "stair"), "SW": ("샤워실", "fac"),
	"NE": ("화장실·세면\n(여자만)", "fac"), "NW": ("비상계단 (잠김)\n앞 막다른 구석", "lock")}

if __name__ == "__main__":
	fig, axs = plt.subplots(1, 2, figsize=(17, 9.4))
	draw_floor(axs[0], "1층 — 사감실에서 출발·복귀", F1_MID, F1_CORNER, f1_extra)
	draw_floor(axs[1], "2층 (3·4층도 같은 뼈대) — 2인실 10 + 4인실 1 (번호 = 순찰 순서)", F2_MID, F2_CORNER)
	fig.text(0.5, 0.015,
		"위에서 본 평면 · 남쪽이 아래 · 바깥 27×27m, 중정 12×12m, 방 4×5.5m, 복도 2.0m (모두 [작업값]) · "
		"초록 = 순찰 길(시계 방향, 거꾸로 돌지 않음) · 파란 점선 = 중정 창 · 보라 = 옛 건물 흔적",
		ha="center", fontsize=9.5)
	fig.tight_layout(rect=(0, 0.035, 1, 0.97))
	fig.savefig(sys.argv[1], dpi=110)
