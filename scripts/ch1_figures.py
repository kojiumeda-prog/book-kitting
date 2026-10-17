"""第1章の図（すべて概念図。数値の割合は示さない）。

    python scripts/ch1_figures.py

図1-1：部品供給の3つの方式
図1-2：キットの流れと、どこまでが外段取りか
図1-3：組む時間の内訳のイメージ
図1-4：部品をトレイに並べる3つの方法
図1-5：トレイに部品箱が並んだ様子（第5章の配置をもとに描く）
"""
import json
import os

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Polygon, Rectangle

from _common import RESULTS
from ch3_figures import arrow, rbox, save
from ch6_figures import draw_tray
from kitting.config import TRAY_H as H, TRAY_W as W


# ---------------------------------------------------------------- 図1-1
def person(ax, x, y, s=0.22, fc="black"):
    ax.add_patch(Circle((x, y + s * 1.6), s * 0.45, fc=fc, ec="black", zorder=4))
    ax.add_patch(Polygon([(x - s * 0.55, y), (x + s * 0.55, y), (x + s * 0.35, y + s * 1.1),
                          (x - s * 0.35, y + s * 1.1)], closed=True, fc=fc, ec="black", zorder=4))


def fig1_1():
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.6))
    titles = ["① 作業場所に置く", "② 取りに行く", "③ キットで運ぶ"]
    for ax, t in zip(axes, titles):
        ax.set_xlim(0, 4)
        ax.set_ylim(0, 4.6)
        ax.set_axis_off()
        ax.set_title(t, fontsize=11, fontweight="bold")
    # ① セル方式：部品棚がコの字に作業者を囲み、作業者は作業台と向き合う
    a = axes[0]
    a.add_patch(Rectangle((0.2, 1.45), 3.6, 2.85, fill=False, ls="--", lw=0.9))
    a.text(0.3, 4.05, "セル（製品専用）", fontsize=8.5)
    rbox(a, 0.45, 3.35, 3.1, 0.5, "部品棚", fc="0.8", fs=8.5)
    rbox(a, 0.45, 1.75, 0.5, 1.5, "部\n品\n棚", fc="0.8", fs=8.5)
    rbox(a, 3.05, 1.75, 0.5, 1.5, "部\n品\n棚", fc="0.8", fs=8.5)
    rbox(a, 1.25, 1.6, 1.5, 0.45, "作業台", fs=8.5)
    person(a, 2.0, 2.35)
    arrow(a, 2.0, 2.95, 2.0, 3.3)
    arrow(a, 1.72, 2.55, 1.0, 2.55)
    arrow(a, 2.28, 2.55, 3.0, 2.55)
    a.text(2.0, 1.05, "組みながら、振り向いて棚から取る", ha="center", fontsize=8.5)
    # ② 部品置き場を一か所に集め、複数の作業台から取りに行く
    a = axes[1]
    rbox(a, 1.0, 3.4, 2.0, 0.8, "部品置き場\n（一か所に集約）", fc="0.8", fs=8.5)
    for bx in (0.25, 2.55):
        rbox(a, bx, 1.5, 1.2, 0.45, "作業台", fs=8.5)
        person(a, bx + 0.6, 2.05)
        a.annotate("", xy=(1.55 if bx < 1 else 2.45, 3.35), xytext=(bx + 0.6, 2.55),
                   arrowprops=dict(arrowstyle="<|-|>", lw=1.0, ls="--"))
    a.text(2.0, 2.55, "途中で\n歩いて\n取りに行く", ha="center", va="center", fontsize=8)
    a.text(2.0, 1.05, "組立の途中で場を離れる", ha="center", fontsize=8.5)
    # ③ 一か所の部品置き場で一式そろえ、カートで各作業台へ運ぶ
    a = axes[2]
    rbox(a, 1.0, 3.4, 2.0, 0.8, "部品置き場\n（一か所）", fc="0.8", fs=8.5)
    for bx in (0.5, 2.3):
        rbox(a, bx + 0.15, 2.3, 0.9, 0.55, "カート", fc="0.92", fs=8)
        arrow(a, 1.55 if bx < 1 else 2.45, 3.38, bx + 0.6, 2.88)
        arrow(a, bx + 0.6, 2.28, bx + 0.6, 1.98)
        rbox(a, bx, 1.5, 1.2, 0.45, "作業台", fs=8.5)
    person(a, 0.25, 1.5)
    person(a, 3.75, 1.5)
    a.text(2.0, 2.55, "そろえて\n運ぶ", ha="center", va="center", fontsize=8)
    a.text(2.0, 1.05, "組み始める前に一式そろえて運ぶ", ha="center", fontsize=8.5)
    for a, when in zip(axes, ["部品を取る時点：組みながら", "部品を取る時点：組みながら",
                              "部品を取る時点：組み始める前"]):
        a.add_patch(Rectangle((0.1, 0.25), 3.8, 0.55, fc="0.93", ec="black", lw=0.6))
        a.text(2.0, 0.52, when, ha="center", va="center", fontsize=9)
    fig.tight_layout()
    save(fig, "fig1-1_supply_methods.png")


# ---------------------------------------------------------------- 図1-2
def bar(ax, x, y, w, h, text, fc="white", hatch=None, fs=8):
    ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec="black", lw=0.8, hatch=hatch))
    if text:
        kw = dict(bbox=dict(fc="white", ec="none", pad=1.0)) if hatch else {}
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, **kw)


def fig1_2():
    fig, ax = plt.subplots(figsize=(11, 5.4))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 5.6)
    ax.set_axis_off()
    # 上：流れ
    steps = ["部品置き場", "部品を\nそろえる", "トレイに\n並べる", "カートで\n運ぶ", "組立"]
    xs = [0.2, 2.3, 4.4, 6.5, 8.8]
    for i, (x, s) in enumerate(zip(xs, steps)):
        rbox(ax, x, 4.1, 1.7 if i < 4 else 2.0, 0.9, s, fc="0.85" if i < 4 else "white", fs=9.5)
        if i < 4:
            arrow(ax, x + 1.72, 4.55, xs[i + 1] - 0.02, 4.55)
    ax.annotate("", xy=(0.2, 3.85), xytext=(8.2, 3.85), arrowprops=dict(arrowstyle="<->", lw=0.9))
    ax.text(4.2, 3.6, "外段取り：組み始める前に済ませる（組立は止まらない）", ha="center", fontsize=9)
    ax.annotate("", xy=(8.8, 3.85), xytext=(10.8, 3.85), arrowprops=dict(arrowstyle="<->", lw=0.9))
    ax.text(9.8, 3.6, "組立に専念", ha="center", fontsize=9)
    # 下：時間の帯
    ax.text(0.2, 2.75, "時間の使い方のイメージ", fontsize=9.5, fontweight="bold")
    ax.text(0.2, 2.1, "今（内段取り）", fontsize=9, va="center")
    seq = [(1.4, "組立"), (0.6, "探す"), (1.6, "組立"), (0.9, "取りに行く"), (1.2, "組立"), (0.7, "欠品待ち"),
           (1.5, "組立")]
    x = 2.2
    for w, t in seq:
        bar(ax, x, 1.85, w, 0.5, t, fc="white" if t == "組立" else "0.85",
            hatch=None if t == "組立" else "///", fs=7.5)
        x += w
    ax.text(0.2, 1.25, "キット（外段取り）", fontsize=9, va="center")
    bar(ax, 2.2, 1.0, 2.0, 0.5, "部品をそろえる・並べる", fc="0.85", fs=7.5)
    ax.text(3.2, 0.75, "（前の組立の間に、別の人や別の時間に行える）", ha="center", va="top", fontsize=7.5)
    bar(ax, 4.2, 1.0, 5.7, 0.5, "組立（途中で止まらない）", fs=8)
    ax.text(10.95, 0.1, "帯の長さはイメージ", ha="right", fontsize=7.5, color="0.35")
    save(fig, "fig1-2_kit_flow.png")


# ---------------------------------------------------------------- 図1-3
def fig1_3():
    fig, ax = plt.subplots(figsize=(10, 3.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3.6)
    ax.set_axis_off()
    parts = [(4.6, "組み付け", "white", None), (1.4, "探す", "0.8", "///"), (1.4, "取りに行く", "0.65", "\\\\\\"),
             (1.3, "欠品で待つ", "0.45", "xxx"), (0.9, "手順書を見る", "0.88", "...")]
    x = 0.3
    for w, t, fc, h in parts:
        bar(ax, x, 2.0, w, 0.9, "", fc=fc, hatch=h)
        ax.text(x + w / 2, 3.1, t, ha="center", fontsize=9)
        x += w
    ax.annotate("", xy=(0.3, 1.8), xytext=(4.9, 1.8), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text(2.6, 1.55, "価値を生む時間", ha="center", va="top", fontsize=9)
    ax.annotate("", xy=(4.9, 1.8), xytext=(9.9, 1.8), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text(7.4, 1.55, "減らしたい時間（キッティングで組立の前へ移す）", ha="center", va="top", fontsize=9)
    ax.text(0.3, 0.55, "2008年の工場での目安：ほかのセルへ探しに行くと1回30分ほど。"
                       "倉庫から取り寄せる欠品は2日に1度ほどで、そのたびに数時間〜半日",
            fontsize=8.5)
    ax.text(9.9, 0.1, "帯の長さはイメージで、割合を表すものではない", ha="right", fontsize=7.5, color="0.35")
    save(fig, "fig1-3_time_breakdown.png")


# ---------------------------------------------------------------- 図1-4
def fig1_4():
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.9))
    titles = ["① フォームを部品の形に切り抜く", "② 切り目入りのウレタンフォーム", "③ 標準部品箱＋印刷シート"]
    for ax, t in zip(axes, titles):
        ax.set_xlim(-0.3, 8.3)
        ax.set_ylim(-1.2, 4.6)
        ax.set_aspect("equal")
        ax.set_axis_off()
        ax.set_title(t, fontsize=10.5, fontweight="bold")
        ax.add_patch(Rectangle((0, 0), 8, 4, fc="0.85", ec="black", lw=1.2))
    # ① 部品の形の穴
    a = axes[0]
    a.add_patch(Circle((1.3, 2.9), 0.7, fc="white", ec="black"))
    a.add_patch(Polygon([(2.6, 0.5), (4.6, 0.5), (4.6, 1.2), (3.3, 1.2), (3.3, 3.4), (2.6, 3.4)],
                        closed=True, fc="white", ec="black"))
    a.add_patch(Rectangle((5.2, 2.3), 2.3, 1.2, fc="white", ec="black"))
    a.add_patch(Polygon([(5.3, 0.4), (7.4, 0.9), (7.2, 1.7), (5.1, 1.2)], closed=True, fc="white", ec="black"))
    a.add_patch(Circle((1.3, 1.0), 0.45, fc="white", ec="black"))
    a.text(4.0, -0.6, "部品ごとに形を写して切り抜く。型はBOMごとに要る", ha="center", fontsize=8.5)
    # ② キューブ
    a = axes[1]
    removed = {(c, r) for c in range(1, 3) for r in range(4, 7)} | {(c, r) for c in range(4, 8) for r in range(1, 3)} \
        | {(c, r) for c in range(10, 14) for r in range(5, 7)} | {(11, 1), (12, 1), (11, 2), (12, 2)}
    for c in range(16):
        for r in range(8):
            x, y = c * 0.5, r * 0.5
            fc = "white" if (c, r) in removed else "0.85"
            a.add_patch(Rectangle((x, y), 0.5, 0.5, fc=fc, ec="0.4", lw=0.4))
    a.text(4.0, -0.6, "サイコロを押し出して穴を作る。穴はサイコロの倍数の大きさ", ha="center", fontsize=8.5)
    # ③ 印刷シート＋部品箱
    a = axes[2]
    a.patches[-1].set_facecolor("white")
    bins = [(0.2, 2.2, 1.6, 1.6, "A"), (2.0, 2.2, 1.6, 1.6, "B"), (3.8, 2.9, 0.8, 0.8, "B"),
            (4.7, 2.9, 0.8, 0.8, "C"), (3.8, 2.0, 0.8, 0.8, "C"), (4.7, 2.0, 0.8, 0.8, "C"),
            (5.7, 0.2, 2.1, 3.6, "D"), (0.2, 0.2, 3.2, 1.6, "E"), (3.6, 0.2, 1.9, 1.6, "E")]
    for x, y, w, h, t in bins:
        a.add_patch(FancyBboxPatch((x + 0.05, y + 0.05), w - 0.1, h - 0.1, boxstyle="round,pad=0,rounding_size=0.1",
                                   fc="0.9", ec="black", lw=0.8))
        a.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=9)
    a.text(4.0, -0.6, "数種類の標準部品箱を、工程記号の入った配置図の上に置く", ha="center", fontsize=8.5)
    fig.tight_layout()
    save(fig, "fig1-4_three_methods.png")


# ---------------------------------------------------------------- 図1-5
def fig1_5():
    with open(os.path.join(RESULTS, "ch5_layouts.json"), encoding="utf-8") as f:
        d = json.load(f)
    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    ax.add_patch(Rectangle((-0.45, -0.45), W + 0.9, H + 0.9, fc="0.55", ec="black", lw=1.4))
    ax.add_patch(Rectangle((0, 0), W, H, fc="white", ec="black", lw=1.0))
    draw_tray(ax, d["bins"], d["layouts"]["lns"], tray=0)
    ax.set_xlim(-0.8, W + 0.8)
    ax.set_ylim(H + 1.3, -0.8)
    ax.text(W / 2, H + 0.95, "金属製のトレイ（1200×600mm、カートに備え付け）。濃い灰色の枠は高さ約4cmの縁",
            ha="center", va="center", fontsize=8.5)
    ax.set_title("トレイに部品箱が並んだ様子（上から見た図、SA-10の1枚目）。記号は工程", fontsize=10)
    save(fig, "fig1-5_tray.png")


if __name__ == "__main__":
    for f in (fig1_1, fig1_2, fig1_3, fig1_4, fig1_5):
        f()
