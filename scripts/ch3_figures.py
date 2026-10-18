"""第3章の図。

    python scripts/ch3_figures.py

図3-1：提案した仕組み（今のセル方式と、部品置き場＋カート方式）
図3-2：2008年のスプレッドシートの構造（架空のデータで描き直し）
図3-3：割当の判定の流れ（入る中で一番小さい部品箱を選ぶ）
図3-4：中型の部品箱の一辺と、最悪ケースの必要面積（階段）
図3-6：2008年に残った3つの宿題と、本書の章の対応
（図3-5は scripts/ch5_figures.py の fig3-5_two_designs.png。第5章はこれを参照する）
"""
import csv
import math
import os

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle

from _common import FIGURES, RESULTS
from kitting.bins import bulk_area
from kitting.config import BLOCK_MM, WALL_MM
from kitting.data import generate_portfolio
import kitting.plot  # noqa: F401  日本語フォントの設定


def save(fig, name):
    path = os.path.join(FIGURES, name)
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("saved", path)


def rbox(ax, x, y, w, h, text, fc="white", fs=9, lw=1.0, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                fc=fc, ec="black", lw=lw))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            fontweight="bold" if bold else "normal")


def arrow(ax, x0, y0, x1, y1, text="", fs=8, ls="-"):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=12,
                                 lw=1.0, color="black", linestyle=ls))
    if text:
        ax.text((x0 + x1) / 2, (y0 + y1) / 2 + 0.12, text, ha="center", va="bottom", fontsize=fs)


# ---------------------------------------------------------------- 図3-1
def fig3_1():
    fig, ax = plt.subplots(figsize=(10, 5.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5.4)
    ax.set_axis_off()
    # 上段：今の仕組み
    ax.text(0.1, 5.15, "今の仕組み（セル方式）：部品はセルごと、組みながら取る", fontsize=10, fontweight="bold")
    for i, name in enumerate(["セル1", "セル2", "セル3"]):
        x = 0.3 + i * 3.2
        ax.add_patch(Rectangle((x, 2.8), 2.8, 2.0, fill=False, ls="--", lw=0.9))
        ax.text(x + 0.1, 4.62, name, fontsize=9)
        rbox(ax, x + 0.15, 3.25, 1.15, 1.15, "部品棚\n（このセル\nの部品）", fc="0.85", fs=8)
        rbox(ax, x + 1.5, 3.25, 1.15, 1.15, "作業台\n（このセル\n専用）", fs=8)
        arrow(ax, x + 1.32, 3.95, x + 1.48, 3.95)
        ax.text(x + 1.4, 3.1, "組みながら取りに行く", ha="center", va="center", fontsize=7.5)
    # 下段：提案
    ax.text(0.1, 2.4, "提案した仕組み：部品を一か所に集め、組む前にカートへそろえる", fontsize=10, fontweight="bold")
    y = 0.7
    rbox(ax, 0.3, y, 2.0, 1.3, "① 部品置き場\n（全セルの部品を\n一か所に集める）", fc="0.85", fs=8.5)
    rbox(ax, 2.95, y, 2.0, 1.3, "② 部品をそろえる\n（BOMを見て\nカートに載せる）", fs=8.5)
    rbox(ax, 5.6, y, 1.6, 1.3, "カート\n（トレイに\n部品箱を並べる）", fc="0.92", fs=8.5)
    rbox(ax, 7.85, y, 1.9, 1.3, "③ 汎用の作業台\n（空いている台で\nどの製品も組む）", fs=8.5)
    arrow(ax, 2.32, y + 0.65, 2.93, y + 0.65)
    arrow(ax, 4.97, y + 0.65, 5.58, y + 0.65)
    arrow(ax, 7.22, y + 0.65, 7.83, y + 0.65, "運ぶ")
    ax.annotate("", xy=(2.3, 0.45), xytext=(7.2, 0.45),
                arrowprops=dict(arrowstyle="<->", lw=0.8, color="0.3"))
    ax.text(4.75, 0.38, "組み始める前に済ませる（外段取り）。この本の主題は、カートの上の並べ方", ha="center",
            va="top", fontsize=8.5)
    save(fig, "fig3-1_system.png")


# ---------------------------------------------------------------- 図3-2
def sheet(ax, x, y, w, title, header, rows, colw, fs=7.2, hl_col=None):
    rh = 0.32
    ax.text(x, y + 0.08, title, fontsize=9.5, fontweight="bold", va="bottom")
    cx = x
    for j, (hd, cw) in enumerate(zip(header, colw)):
        ax.add_patch(Rectangle((cx, y - rh), cw, rh, fc="0.75", ec="black", lw=0.6))
        ax.text(cx + cw / 2, y - rh / 2, hd, ha="center", va="center", fontsize=fs)
        for i, r in enumerate(rows):
            g = "0.92" if (hl_col is not None and j in hl_col) else "white"
            ax.add_patch(Rectangle((cx, y - rh * (i + 2)), cw, rh, fc=g, ec="black", lw=0.4))
            ax.text(cx + cw / 2, y - rh * (i + 1.5), str(r[j]), ha="center", va="center", fontsize=fs)
        cx += cw
    return y - rh * (len(rows) + 1)


def fig3_2():
    fig, ax = plt.subplots(figsize=(11, 4.4))
    ax.set_xlim(0, 11)
    ax.set_ylim(1.1, 5.8)
    ax.set_axis_off()
    # 寸法のシート（左上）
    sheet(ax, 0.2, 5.3, 3.2, "寸法のシート（1か所だけに書く）",
          ["区分", "横mm", "縦mm"],
          [["小型", 75, 75], ["中型", 150, 150], ["大型", 300, 150], ["特大", 300, 300], ["大物", "無制限", "無制限"]],
          [0.9, 0.8, 0.8], hl_col=[1, 2])
    # BOMのシート（中央）
    sheet(ax, 3.4, 5.3, 4.6, "BOMのシート（BOMごとに1枚）",
          ["品番", "数量", "幅", "長さ", "選んだ区分", "必要数"],
          [["P-1032", 4, 27, 50, "小型", 2], ["P-2210", 1, 120, 90, "中型", 1],
           ["P-3307", 10, 8, 12, "小型", 1], ["P-4415", 2, 260, 140, "大型", 1],
           ["P-5521", 1, 40, 480, "大物", "—"]],
          [0.85, 0.55, 0.5, 0.6, 1.0, 0.7], hl_col=[4, 5])
    # 集計のシート（右）
    sheet(ax, 8.35, 5.3, 2.6, "集計のシート",
          ["区分", "SA-01", "…", "最悪"],
          [["小型", 12, "…", 74], ["中型", 5, "…", 53], ["大型", 2, "…", 14], ["特大", 0, "…", 4],
           ["大物", 0, "…", "44"]],
          [0.7, 0.65, 0.4, 0.6], hl_col=[3])
    ax.text(9.65, 3.25, "必要面積＝個数×部品箱の面積\nの合計（最悪ケース）", ha="center", va="top", fontsize=8)
    arrow(ax, 2.75, 4.2, 3.35, 4.2, "参照")
    arrow(ax, 7.65, 4.2, 8.3, 4.2, "集計")
    # 下：論理関数の説明
    rbox(ax, 3.4, 1.25, 4.6, 1.2,
         "「選んだ区分」の列には論理関数（IF・AND）\n部品の幅と長さを小型から順に寸法と比べ、\n"
         "入る中で一番小さい区分を選ぶ（図3-3）。\n寸法のシートを書き換えると、全BOMが一度に再計算される",
         fc="0.95", fs=8)
    arrow(ax, 6.9, 2.5, 6.9, 3.3)
    ax.text(0.2, 1.3, "数値はすべて架空の例", fontsize=7.5, color="0.35")
    save(fig, "fig3-2_spreadsheet.png")


# ---------------------------------------------------------------- 図3-3
def diamond(ax, cx, cy, w, h, text, fs=8.5):
    ax.add_patch(Polygon([(cx, cy + h / 2), (cx + w / 2, cy), (cx, cy - h / 2), (cx - w / 2, cy)],
                         closed=True, fc="white", ec="black", lw=1.0))
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fs)


def fig3_3():
    fig, ax = plt.subplots(figsize=(8.6, 6.4))
    ax.set_xlim(0, 8.6)
    ax.set_ylim(0, 6.6)
    ax.set_axis_off()
    rbox(ax, 2.3, 5.85, 2.4, 0.55, "部品（幅・長さ・数量）", fs=9)
    ys = [4.9, 3.7, 2.5, 1.3]
    names = ["小型", "中型", "大型", "特大"]
    arrow(ax, 3.5, 5.83, 3.5, ys[0] + 0.45)
    for i, (y, n) in enumerate(zip(ys, names)):
        diamond(ax, 3.5, y, 2.6, 0.9, f"{n}の部品箱に入るか\n（90度回してもよい）", fs=8)
        arrow(ax, 4.8, y, 5.6, y, "入る")
        rbox(ax, 5.6, y - 0.32, 2.7, 0.64, f"{n}を選ぶ → 何個入るか\n→ 必要数＝数量÷入る個数（切り上げ）", fs=7.5)
        if i < 3:
            arrow(ax, 3.5, y - 0.45, 3.5, ys[i + 1] + 0.45)
            ax.text(3.6, y - 0.6, "入らない", fontsize=7.5, va="center")
    ax.text(3.6, ys[-1] - 0.6, "入らない", fontsize=7.5, va="center")
    arrow(ax, 3.5, ys[-1] - 0.45, 3.5, 0.48)
    rbox(ax, 2.1, -0.05, 2.8, 0.52, "大物：部品そのものの面積を足す", fc="0.85", fs=8.5)
    ax.text(0.1, 3.1, "小さい部品箱から\n順に試す", fontsize=8.5, ha="left", va="center")
    ax.annotate("", xy=(1.55, 1.3), xytext=(1.55, 4.9), arrowprops=dict(arrowstyle="-|>", lw=0.8))
    ax.text(5.6, 0.3, "例：27×50mmの部品を4個\n小型（内側65×65mm）に2個入る→必要数2", fontsize=8, va="center")
    ax.set_ylim(-0.2, 6.6)
    save(fig, "fig3-3_rule_flow.png")


# ---------------------------------------------------------------- 図3-4
def staircase():
    """中型（正方形）の一辺だけを変えたときの、最悪ケースの必要面積 [m²]。
    ほかの3種類（75×75、300×150、300×300mm）は固定。300mmは特大と同じ大きさになるので除く。"""
    boms = generate_portfolio()

    def cap(p, ow, oh):
        iw, ih = ow - WALL_MM, oh - WALL_MM
        best = 0
        for pw, pl in ((p.w_mm, p.l_mm), (p.l_mm, p.w_mm)):
            if pw <= iw and pl <= ih:
                best = max(best, (iw // pw) * (ih // pl))
        return 10 ** 9 if best and p.hardware else best

    def worst(types):
        order = sorted(types, key=lambda t: (t[0] * t[1], t[0]))
        mx, bmax = {t: 0 for t in types}, 0
        for parts in boms.values():
            cnt, b = {t: 0 for t in types}, 0
            for p in parts:
                for t in order:
                    c = cap(p, *t)
                    if c:
                        cnt[t] += math.ceil(p.qty / c)
                        break
                else:
                    b += bulk_area(p) * BLOCK_MM ** 2
            for t in types:
                mx[t] = max(mx[t], cnt[t])
            bmax = max(bmax, b)
        return (sum(t[0] * t[1] * mx[t] for t in types) + bmax) / 1e6

    xs = list(range(100, 300))
    ys = [worst([(75, 75), (s, s), (300, 150), (300, 300)]) for s in xs]
    with open(os.path.join(RESULTS, "ch3_staircase.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["medium_mm", "worst_area_m2"])
        w.writerows(zip(xs, ys))
    return xs, ys


def fig3_4():
    xs, ys = staircase()
    mins = sum(1 for i in range(1, len(ys) - 1) if ys[i] < ys[i - 1] and ys[i] <= ys[i + 1])
    jumps = sum(1 for i in range(1, len(ys)) if abs(ys[i] - ys[i - 1]) >= 0.05)
    print(f"範囲 {min(ys):.2f}〜{max(ys):.2f} m²、最小 {xs[ys.index(min(ys))]}mm、谷 {mins}、飛び {jumps}")
    fig, ax = plt.subplots(figsize=(8.4, 4.2))
    ax.step(xs, ys, where="post", color="black", lw=1.0)
    i120, i150 = xs.index(120), xs.index(150)
    ax.scatter([120], [ys[i120]], s=50, facecolor="black", zorder=3)
    ax.annotate(f"最小：一辺120mm\n約{ys[i120]:.2f}m²", (120, ys[i120]), xytext=(128, 2.30),
                fontsize=8.5, arrowprops=dict(arrowstyle="-", lw=0.6))
    ax.scatter([150], [ys[i150]], s=50, facecolor="white", edgecolor="black", zorder=3)
    ax.annotate(f"論文の寸法：150mm\n約{ys[i150]:.2f}m²", (150, ys[i150]), xytext=(158, 3.25),
                fontsize=8.5, arrowprops=dict(arrowstyle="-", lw=0.6))
    ax.set_xlabel("中型の部品箱の一辺（mm）")
    ax.set_ylabel("最悪ケースの必要面積（m²）")
    ax.set_xlim(100, 300)
    ax.set_ylim(2.2, 3.5)
    ax.grid(lw=0.3, color="0.8")
    ax.set_title("中型の一辺だけを1mmずつ変えたときの必要面積（ほかの3種類は固定）", fontsize=10)
    save(fig, "fig3-4_staircase.png")


# ---------------------------------------------------------------- 図3-6
def fig3_6():
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.set_axis_off()
    ax.text(1.6, 4.7, "2008年に起きたこと", ha="center", fontsize=10, fontweight="bold")
    ax.text(5.0, 4.7, "残った宿題", ha="center", fontsize=10, fontweight="bold")
    ax.text(8.4, 4.7, "この本での解き方", ha="center", fontsize=10, fontweight="bold")
    rows = [("Solverが動かず\n手で寸法を変えて反復", "1. 部品箱の寸法と\n種類数を決める", "第4章\n品揃え問題（混合整数計画）"),
            ("3人で手分けして手で描いた\n大きなものは約3時間", "2. トレイの枚数を最小にし\n作業順に並べる", "第5章\nマス目の配置（制約プログラミング）"),
            ("作業順とサイズ順の\n2つを描いて並べた", "3. 使いやすさと面積の\nどちらを取るか決める", "第6章\n重み・優先順位・解を並べて選ぶ")]
    for i, (a, b, c) in enumerate(rows):
        y = 3.55 - i * 1.15
        rbox(ax, 0.1, y, 3.0, 0.85, a, fs=8.5)
        rbox(ax, 3.6, y, 2.8, 0.85, b, fc="0.85", fs=8.5, bold=True)
        rbox(ax, 6.9, y, 3.0, 0.85, c, fs=8.5)
        arrow(ax, 3.12, y + 0.42, 3.58, y + 0.42)
        arrow(ax, 6.42, y + 0.42, 6.88, y + 0.42)
    rbox(ax, 0.1, 0.05, 9.8, 0.7,
         "宿題が解けた後：部品や手順が変わるたびに作り直す運用をどう回すか → 第7章", fc="0.95", fs=9)
    save(fig, "fig3-6_homework.png")


if __name__ == "__main__":
    for f in (fig3_1, fig3_2, fig3_3, fig3_4, fig3_6):
        f()
