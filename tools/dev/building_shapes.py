"""건물 모양 후보 3개를 위에서 본 그림 (docs/plan/building-layout.md §3). 크기는 [작업값]."""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False
ROOM, COR, STAIR, FAC = "#f1e6d2", "#9aa3ad", "#c0504d", "#7fa7c9"


def rect(ax, x, y, w, h, c, label=None, fs=7):
	ax.add_patch(Rectangle((x, y), w, h, fc=c, ec="#333", lw=0.6))
	if label:
		ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=fs)


def arrow(ax, pts):
	for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
		ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=9, color="#1a7f37", lw=1.6))


fig, axs = plt.subplots(1, 3, figsize=(16, 7.6))
# A 일자형: 가운데 복도, 양쪽 방, 양 끝 계단
ax = axs[0]
rect(ax, 0, 6, 4, 2.2, STAIR, "계단 A")
rect(ax, 36, 6, 4, 2.2, STAIR, "계단 B")
rect(ax, 4, 6, 32, 2.2, COR, "복도 2.2m")
for i in range(8):
	rect(ax, 4 + i * 4, 8.2, 4, 6, ROOM, f"{201 + i}")
for i in range(6):
	rect(ax, 4 + i * 4, 0, 4, 6, ROOM, f"{209 + i}")
rect(ax, 28, 0, 8, 6, FAC, "화장실\n샤워실")
arrow(ax, [(2, 7.1), (38, 7.1)])
ax.set_title("A. 일자형 — 곧은 복도 + 양 끝 계단\n순찰: 층마다 끝에서 끝, 계단 A·B를 번갈아", fontsize=11)
ax.set_xlim(-1, 41); ax.set_ylim(-1, 15)

# B ㄷ자형
ax = axs[1]
rect(ax, 0, 0, 2.2, 26, COR)
rect(ax, 2.2, 23.8, 22, 2.2, COR)
rect(ax, 2.2, 0, 22, 2.2, COR)
rect(ax, 24.2, 23.8, 3.5, 2.2, STAIR, "계단")
rect(ax, 24.2, 0, 3.5, 2.2, STAIR, "계단")
for i in range(5):
	rect(ax, 2.2 + i * 4, 26, 4, 5, ROOM, f"{201 + i}")
	rect(ax, 2.2 + i * 4, -5, 4, 5, ROOM, f"{210 - i}")
rect(ax, -5, 8, 5, 10, FAC, "화장실\n휴게")
ax.text(13, 13, "안뜰\n(창 너머로 맞은편이 보임)", ha="center", va="center", fontsize=9, color="#555")
arrow(ax, [(25, 24.9), (1.1, 24.9), (1.1, 1.1), (25, 1.1)])
ax.set_title("B. ㄷ자형 — 모퉁이 2개 + 안뜰\n순찰: 한쪽 계단 → ㄷ자 한 바퀴 → 반대쪽 계단", fontsize=11)
ax.set_xlim(-6, 29); ax.set_ylim(-6, 32)

# C ㅁ자 중정형
ax = axs[2]
rect(ax, 0, 0, 24, 2.2, COR)
rect(ax, 0, 21.8, 24, 2.2, COR)
rect(ax, 0, 2.2, 2.2, 19.6, COR)
rect(ax, 21.8, 2.2, 2.2, 19.6, COR)
ax.text(12, 12, "중정\n(안쪽 벽 = 창문)", ha="center", va="center", fontsize=9, color="#555")
for i in range(5):
	rect(ax, i * 4.8, 24, 4.8, 5, ROOM, f"{201 + i}")
for i in range(3):
	rect(ax, 24, 21.8 - (i + 1) * 6.5, 5, 6.5, ROOM, f"{206 + i}")
rect(ax, 24, 0, 5, 2.2, STAIR, "계단")
for i in range(3):
	rect(ax, i * 4.8 + 4.8, -5, 4.8, 5, ROOM, f"{211 - i}")
rect(ax, 0, -5, 4.8, 5, FAC, "화장실")
rect(ax, -5, 2.2, 5, 19.6, FAC, "샤워실·휴게\n세탁(1층)")
arrow(ax, [(23, 1.1), (1.1, 1.1), (1.1, 22.9), (22.9, 22.9), (22.9, 3)])
ax.text(12, -7.2, "※ 수칙 '순찰은 정해진 길로 한 바퀴, 거꾸로 돌지 마십시오'와 그대로 맞음", ha="center", fontsize=8.5, color="#1a7f37")
ax.set_title("C. ㅁ자 중정형 — 층마다 고리 복도\n순찰: 층마다 한 바퀴 → 같은 계단으로 다음 층", fontsize=11)
ax.set_xlim(-6, 30); ax.set_ylim(-8.5, 30)

for ax in axs:
	ax.set_aspect("equal"); ax.axis("off")
fig.text(0.5, 0.01, "위에서 본 2층 (단위 m, 방 2인실 4×6m · 복도 2.2m — 모두 [작업값]) · 초록 화살표 = 순찰 길 · 빨강 = 계단 · 파랑 = 공용", ha="center", fontsize=10)
fig.tight_layout(rect=(0, 0.03, 1, 0.97))
fig.savefig(sys.argv[1], dpi=110)
