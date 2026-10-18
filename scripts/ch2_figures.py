"""第2章の図。

    python scripts/ch2_figures.py      # 図2-4は先に ch2_count.py --six を実行しておく

図2-1：部品 → 外接矩形 → 部品箱（内側と外側）→ トレイのマス目
図2-2：詰め方の良い例・悪い例（同じ部品箱の組が、1枚に収まるか2枚になるか）
図2-3：親戚の問題の家系図
図2-4：部品箱の数と置き方の数（縦軸は対数）
図2-5：ボトムレフト法の動き
図2-6：解法の地図（計算時間と答えの良さ）
"""
import csv
import os

import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Polygon, Rectangle

from _common import FIGURES, RESULTS
from ch3_figures import arrow, rbox, save
from kitting.config import BLOCK_MM, WALL_MM


def grid(ax, x0, y0, W, H, lw=0.3):
    for x in range(1, W):
        ax.plot([x0 + x, x0 + x], [y0, y0 + H], lw=lw, color="0.75")
    for y in range(1, H):
        ax.plot([x0, x0 + W], [y0 + y, y0 + y], lw=lw, color="0.75")
    ax.add_patch(Rectangle((x0, y0), W, H, fill=False, lw=1.2, ec="black"))


def cell_box(ax, x, y, w, h, label="", g="0.8", fs=8, ls="-"):
    ax.add_patch(Rectangle((x + 0.06, y + 0.06), w - 0.12, h - 0.12, fc=g, ec="black", lw=0.8, ls=ls))
    if label:
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=fs)


# ---------------------------------------------------------------- 図2-1
def fig2_2():
    fig, axes = plt.subplots(1, 4, figsize=(12, 3.4), gridspec_kw=dict(width_ratios=[1, 1, 1.15, 1.6]))
    for ax in axes:
        ax.set_aspect("equal")
        ax.set_axis_off()
    # L字型ブラケット（上から見た形）。外接矩形は 120×50 mm
    L = [(0, 0), (120, 0), (120, 14), (14, 14), (14, 50), (0, 50)]
    # ① 部品
    a = axes[0]
    a.add_patch(Polygon(L, closed=True, fc="0.7", ec="black", lw=1))
    a.set_xlim(-15, 140)
    a.set_ylim(-35, 80)
    a.set_title("① 部品（上から見た形）", fontsize=9)
    a.text(60, -22, "L字型のブラケット", ha="center", fontsize=8)
    # ② 外接矩形
    a = axes[1]
    a.add_patch(Polygon(L, closed=True, fc="0.85", ec="0.4", lw=0.8))
    a.add_patch(Rectangle((0, 0), 120, 50, fill=False, lw=1.5, ls="--"))
    a.set_xlim(-15, 140)
    a.set_ylim(-35, 80)
    a.set_title("② 外接矩形で表す", fontsize=9)
    a.text(60, 56, "120 mm", ha="center", fontsize=8)
    a.text(126, 25, "50\nmm", va="center", fontsize=8)
    a.text(60, -22, "空いたところは使わない", ha="center", fontsize=8)
    # ③ 部品箱の外側と内側
    a = axes[2]
    ow, oh = 2 * BLOCK_MM, BLOCK_MM                       # 外形 150×75
    iw, ih = ow - WALL_MM, oh - WALL_MM                   # 内寸 140×65
    a.add_patch(Rectangle((0, 0), ow, oh, fc="0.9", ec="black", lw=1.4))
    a.add_patch(Rectangle((WALL_MM / 2, WALL_MM / 2), iw, ih, fc="white", ec="black", lw=0.8, ls=":"))
    a.add_patch(Rectangle((12, 9), 120, 50, fill=False, lw=1.2, ls="--"))
    a.set_xlim(-10, 175)
    a.set_ylim(-45, 110)
    a.set_title("③ 部品箱に入れる", fontsize=9)
    a.text(ow / 2, oh + 8, f"外側 {ow}×{oh} mm（トレイの場所を決める）", ha="center", fontsize=7.5)
    a.text(ow / 2, -14, f"内側 {iw}×{ih} mm（部品が入るかを決める）", ha="center", fontsize=7.5)
    a.text(ow / 2, -32, "120×50 mm の部品は内側に入る", ha="center", fontsize=7.5)
    # ④ トレイのマス目
    a = axes[3]
    grid(a, 0, 0, 16, 8)
    cell_box(a, 1, 5, 2, 1, "部品箱\n2×1", g="0.75", fs=7)
    a.set_xlim(-0.5, 16.5)
    a.set_ylim(-2.2, 9.6)
    a.set_title("④ トレイのマス目に置く", fontsize=9)
    a.text(8, -1.0, f"1200×600 mm のトレイ＝横16×縦8マス（1マス{BLOCK_MM} mm）", ha="center", fontsize=7.5)
    a.text(3.4, 5.5, "← 外形がマスの整数倍なので\n　 「何列目・何行目」で表せる", va="center", fontsize=7.5)
    fig.tight_layout(w_pad=2.5)
    # パネル間の矢印（各パネルの右端と次のパネルの左端の間）
    for a0, a1 in zip(axes[:-1], axes[1:]):
        x = (a0.get_position().x1 + a1.get_position().x0) / 2
        fig.text(x, 0.5, "▶", ha="center", va="center", fontsize=14, color="0.3")
    save(fig, "fig2-1_part_to_grid.png")


# ---------------------------------------------------------------- 図2-2
GOOD = [("A", 0, 0, 2, 2), ("B", 2, 0, 2, 2), ("G", 4, 0, 2, 2),
        ("C", 0, 2, 3, 1), ("D", 3, 2, 3, 1), ("E", 0, 3, 2, 1), ("F", 2, 3, 2, 1)]
BAD1 = [("A", 0, 0, 2, 2), ("B", 3, 0, 2, 2), ("C", 0, 2, 3, 1), ("D", 3, 3, 3, 1),
        ("E", 3, 2, 2, 1), ("F", 2, 0, 1, 2)]
BAD2 = [("G", 0, 0, 2, 2)]


def _check(layout, W=6, H=4):
    used = set()
    for _, x, y, w, h in layout:
        cells = {(x + i, y + j) for i in range(w) for j in range(h)}
        assert not used & cells and all(0 <= cx < W and 0 <= cy < H for cx, cy in cells)
        used |= cells
    return used


def _fits_anywhere(used, w, h, W=6, H=4):
    for ww, hh in {(w, h), (h, w)}:
        for x in range(W - ww + 1):
            for y in range(H - hh + 1):
                if not any((x + i, y + j) in used for i in range(ww) for j in range(hh)):
                    return True
    return False


def fig2_3():
    _check(GOOD)
    used = _check(BAD1)
    assert not _fits_anywhere(used, 2, 2)                 # Gは1枚目のどこにも入らない
    shade = {"A": "0.6", "B": "0.6", "G": "0.6", "C": "0.8", "D": "0.8", "E": "0.92", "F": "0.92"}
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.0), gridspec_kw=dict(width_ratios=[1, 1, 1]))
    panels = [(axes[0], GOOD, "良い詰め方：1枚に収まる"),
              (axes[1], BAD1, "悪い詰め方：1枚目に隙間が残り…"),
              (axes[2], BAD2, "…Gが入らず、2枚目が要る")]
    for ax, layout, title in panels:
        ax.set_aspect("equal")
        ax.set_axis_off()
        # 上が奥になるよう、行0を上に描く
        grid(ax, 0, 0, 6, 4)
        for name, x, y, w, h in layout:
            cell_box(ax, x, 4 - y - h, w, h, name, g=shade[name], fs=10)
        ax.set_xlim(-0.3, 6.3)
        ax.set_ylim(-0.9, 4.6)
        ax.set_title(title, fontsize=9.5)
    axes[0].text(3, -0.5, "使ったブロック 22／24", ha="center", fontsize=8.5)
    axes[1].text(3, -0.5, "空きは6ブロック分あるが、2×2の形の空きがない", ha="center", fontsize=8.5)
    axes[2].text(3, -0.5, "トレイ2枚目", ha="center", fontsize=8.5)
    fig.suptitle("同じ7個の部品箱（A, B, G は2×2、C, D は3×1、E, F は2×1）を、横6×縦4マスのトレイに並べる",
                 fontsize=9.5, y=1.02)
    fig.tight_layout()
    save(fig, "fig2-2_good_bad.png")


# ---------------------------------------------------------------- 図2-3
def fig2_4():
    fig, ax = plt.subplots(figsize=(10, 5.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5.6)
    ax.set_axis_off()
    rbox(ax, 3.3, 4.6, 3.4, 0.8, "長方形を、重ならずに並べる", fc="0.85", fs=10, bold=True)
    rbox(ax, 0.4, 3.0, 3.6, 0.9, "枚数を減らす系統\n（隙間なく詰める）", fs=9.5)
    rbox(ax, 6.0, 3.0, 3.6, 0.9, "近くに置く系統\n（関係の深いものを近くに）", fs=9.5)
    arrow(ax, 4.4, 4.6, 2.4, 3.92)
    arrow(ax, 5.6, 4.6, 7.6, 3.92)
    left = [("ビンパッキング\n（箱に詰める）", 0.1), ("板取り\n（板から切り出す）", 1.45), ("積付け\n（荷台に積む）", 2.8)]
    right = [("回路の配置\n（チップ）", 5.7), ("工場の配置\n（設備・区画）", 7.05), ("棚割り\n（倉庫の棚）", 8.4)]
    for text, x in left + right:
        rbox(ax, x, 1.75, 1.3, 0.8, text, fs=8)
    for _, x in left:
        arrow(ax, 2.2, 3.0, x + 0.65, 2.57)
    for _, x in right:
        arrow(ax, 7.8, 3.0, x + 0.65, 2.57)
    rbox(ax, 3.1, 0.2, 3.8, 0.9, "この本の問題：トレイの配置\n枚数を減らし、同じ工程を近くに置く", fc="0.92", fs=9,
         lw=2.0, bold=True)
    ax.annotate("", xy=(3.6, 1.12), xytext=(0.75, 1.73),
                arrowprops=dict(arrowstyle="-|>", lw=1.0, ls="--", color="black"))
    ax.annotate("", xy=(6.4, 1.12), xytext=(6.35, 1.73),
                arrowprops=dict(arrowstyle="-|>", lw=1.0, ls="--", color="black"))
    ax.text(5.0, 1.4, "両方にまたがる", ha="center", fontsize=8.5)
    save(fig, "fig2-3_family_tree.png")


# ---------------------------------------------------------------- 図2-4
def fig2_5():
    with open(os.path.join(RESULTS, "ch2_count.csv"), encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    small = [r for r in rows if r["tray"] != "16x8"]
    big = [r for r in rows if r["tray"] == "16x8"]
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    xs, ys = [int(r["bins"]) for r in small], [float(r["layouts"]) for r in small]
    ax.plot(xs, ys, marker="o", color="black", mfc="white", lw=1,
            label=f"横{small[0]['tray'].split('x')[0]}×縦{small[0]['tray'].split('x')[1]}マスの小さなトレイ（全通り数えた実測）")
    xb, yb = [int(r["bins"]) for r in big], [float(r["layouts"]) for r in big]
    ax.plot(xb, yb, marker="s", color="black", lw=1, ls="--",
            label="横16×縦8マス（128ブロック）のトレイ、1×1の部品箱だけ（計算）")
    for x, y in zip(xb, yb):
        e = int(f"{y:.0e}".split("e")[1])
        right = x == 10                                     # 左下の点は右下に書いて、説明の文字と重ねない
        ax.annotate(f"10の{e}乗", (x, y), textcoords="offset points", xytext=(8, -12) if right else (-6, 7),
                    ha="left" if right else "right", fontsize=7.5)
    lim = 1e8 * 4.4e17                                     # 1秒に1億通り×宇宙の年齢（約4.4×10^17秒）
    ax.axhline(lim, color="0.4", lw=0.8, ls=":")
    ax.text(1.05, lim * 1e3, "1秒に1億通り調べても、宇宙の年齢の間に\n調べきれるのはこの線（約10の25乗）まで", fontsize=7.5,
            color="0.2", va="bottom")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xticks([1, 2, 3, 5, 10, 20, 40, 80, 126])
    ax.set_xticklabels(["1", "2", "3", "5", "10", "20", "40", "80", "126"])
    ax.set_xlabel("部品箱の数")
    ax.set_ylabel("置き方の数（対数目盛）")
    ax.set_ylim(1, 1e240)
    ax.grid(lw=0.3, color="0.85")
    ax.legend(fontsize=7.5, frameon=False, loc="upper left")
    save(fig, "fig2-4_count.png")


# ---------------------------------------------------------------- 図2-6
def fig2_6():
    fig, ax = plt.subplots(figsize=(7.4, 4.8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel("計算時間　短い → 長い", fontsize=10)
    ax.set_ylabel("答えの良さ　悪い → 良い", fontsize=10)
    items = [
        (2.1, 2.2, 3.4, 2.2, "0.92", "② 構築型の解法\nルール、ファーストフィット、\nボトムレフト法\n一瞬で終わる"),
        (5.0, 5.2, 3.8, 2.3, "0.85", "③ メタヒューリスティクス\n焼きなまし法、遺伝的アルゴリズム、\nSequence-Pair\n少しずつ直していく"),
        (8.3, 7.4, 3.2, 2.6, "0.75", "① 厳密解法\nMILP、CP-SAT\n最適と証明できるが、\n大きい問題は\n時間内に終わらない"),
    ]
    for x, y, w, h, g, text in items:
        ax.add_patch(Ellipse((x, y), w, h, fc=g, ec="black", lw=1))
        ax.text(x, y, text, ha="center", va="center", fontsize=8)
    ax.add_patch(Ellipse((4.6, 9.0), 2.6, 1.4, fc="white", ec="black", lw=1.8, ls="--"))
    ax.text(4.6, 9.0, "LNS（大近傍探索）\n①を③のように使う\n第5章で使う", ha="center", va="center", fontsize=8,
            fontweight="bold")
    ax.annotate("", xy=(3.4, 8.7), xytext=(1.6, 3.35),
                arrowprops=dict(arrowstyle="-|>", lw=0.8, color="0.3", connectionstyle="arc3,rad=-0.2"))
    ax.text(0.2, 6.6, "ルールの答えを\n出発点にして\n一部ずつ厳密に解き直す", fontsize=7.5, color="0.2")
    save(fig, "fig2-6_solver_map.png")


# ---------------------------------------------------------------- 図2-5
def fig2_7():
    W, H = 8, 5
    placed = [("A", 0, 0, 2, 4), ("B", 2, 0, 3, 1), ("C", 5, 0, 3, 3)]   # (x, y, w, h)、y=0 が下
    path = [(6, 3), (2, 3), (2, 1)]                                       # 新しい2×2の部品箱の動き
    fig, ax = plt.subplots(figsize=(6.2, 4.4))
    ax.set_aspect("equal")
    ax.set_axis_off()
    grid(ax, 0, 0, W, H)
    for name, x, y, w, h in placed:
        cell_box(ax, x, y, w, h, f"置いた\n部品箱{name}", g="0.8", fs=8)
    labels = ["① 右上から入れる", "② 下へ：Cに当たって動けない\n　 左へ：Aに当たるまで寄せる", "③ 下へ：Bに当たるまで落とす"]
    for i, (x, y) in enumerate(path):
        last = i == len(path) - 1
        cell_box(ax, x, y, 2, 2, "新しい\n部品箱" if last else "", g="0.45" if last else "white", fs=8,
                 ls="-" if last else "--")
        if last:
            ax.texts[-1].set_color("white")
    arrow(ax, 6.0, 4.0, 4.05, 4.0)
    arrow(ax, 4.35, 3.9, 4.35, 2.1)
    ax.text(7.0, 5.25, labels[0], ha="center", fontsize=8)
    ax.text(8.2, 4.0, labels[1], va="center", fontsize=8)
    ax.text(8.2, 1.9, labels[2] + "\n　 左へ：Aに当たって動けない → ここに置く", va="center", fontsize=8)
    ax.set_xlim(-0.3, 14.5)
    ax.set_ylim(-0.5, 5.8)
    ax.text(4, -0.4, "トレイ（下が手前）", ha="center", va="top", fontsize=8)
    save(fig, "fig2-5_bottom_left.png")


if __name__ == "__main__":
    for f in (fig2_2, fig2_3, fig2_4, fig2_5, fig2_6, fig2_7):
        f()
