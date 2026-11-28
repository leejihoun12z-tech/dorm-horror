"""층별 방 배정 그림 (docs/plan/cast-rooms.md). 배정은 [후보].
사용: python tools/dev/cast_rooms.py <출력.png>
"""
import sys

import matplotlib.pyplot as plt

import building_plan as bp

C = dict(bp.C, main="#e9b949", sub="#9ec3e6", extra="#f1e6d2", empty="#8c8c8c")


def room(num, kind, who, people):
	return (f"{num} {kind}\n{who}", people)


# 방 번호 끝 두 자리 → (표시, 색 종류)
F2 = {
	1: ("201 2인\n뒤통수 입 ★도우미\n+ 사람 룸메이트", "main"),
	2: ("202 2인\n엑스트라 2", "extra"),
	3: ("203 1인\n마네킹", "main"),
	5: ("205 1인\n엑스트라(사람)\n1일차 외박", "extra"),
	6: ("206 1인\n도깨비", "main"),
	7: ("207 1인\nTV 머리\n(중반에 사라짐)", "sub"),
	8: ("208 2인\n엑스트라 2", "extra"),
	9: ("209 1인\n엑스트라\n(2층 층장)", "extra"),
	10: ("210 1인\n엑스트라", "extra"),
	11: ("211 2인\n엑스트라 2", "extra"),
}
F3 = {
	1: ("301 2인\n장산범\n+ 사람 룸메이트", "main"),
	2: ("302 2인\n강시\n+ 엑스트라", "main"),
	3: ("303 1인\n우산 요괴", "sub"),
	5: ("305 1인\n포투쏙독새", "sub"),
	6: ("306 1인\n엑스트라", "extra"),
	7: ("307 1인\n엑스트라", "extra"),
	8: ("308 2인\n엑스트라 2", "extra"),
	9: ("309 1인\n해파리(우비)", "sub"),
	10: ("310 1인\n엑스트라\n(3층 층장)", "extra"),
	11: ("311 2인\n엑스트라 2", "extra"),
}
F4 = {
	1: ("401 2인\n좀비\n+ 엑스트라(사람)", "sub"),
	2: ("402 1인\n팔척", "sub"),
	11: ("411 1인\n우물 원혼", "sub"),
}


def mid_for(f, table, empty=False):
	def cell(n):
		if n == 4:
			return (f"{f}04 옛 큰 방\n(빈 창고)", "old")
		if n in table:
			return table[n]
		return (f"{f}{n:02d}\n빈방(잠김)", "empty")
	lounge = ("층 휴게", "fac")
	return {
		"S": [cell(2), cell(1), lounge],
		"W": [cell(3), cell(4), cell(5)],
		"N": [cell(6), cell(7), cell(8)],
		"E": [cell(11), cell(10), cell(9)],
	}


if __name__ == "__main__":
	bp.C.update(C)
	fig, axs = plt.subplots(1, 3, figsize=(25, 9.6))
	bp.draw_floor(axs[0], "2층 — 14명 (1주차부터) · 메인 3", mid_for(2, F2), bp.F2_CORNER)
	bp.draw_floor(axs[1], "3층 — 14명 (2주차부터) · 메인 2", mid_for(3, F3), bp.F3_CORNER)
	bp.draw_floor(axs[2], "4층 — 4명 (3주차부터) · 조연 3", mid_for(4, F4), bp.F4_CORNER, bp.f4_extra)
	fig.text(0.5, 0.015,
		"노랑 = 메인 5 · 파랑 = 조연(기숙생 7) · 베이지 = 엑스트라 20 · 회색 = 빈방 · 알바생(아귀)은 기숙생이 아님 — 1층 매점 · 모두 [후보]",
		ha="center", fontsize=11)
	fig.tight_layout(rect=(0, 0.035, 1, 0.97))
	fig.savefig(sys.argv[1], dpi=95)
