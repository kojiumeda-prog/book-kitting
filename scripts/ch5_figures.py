"""第5章の図（ch5_layout.py が作る図5-3・5-7〜5-9以外）を作る。

    python scripts/ch5_layout.py     # 先に実行（results/ch5_layouts.json を作る）
    python scripts/scale_test.py     # 先に実行（results/scale_test.csv を作る）
    python scripts/ch5_figures.py

図5-1 ：2008年の2つの設計案（作業順の配置／サイズ順の配置）を SA-03 で再現（本では第3章の図3-5として載せ、第5章は参照）
図5-2 ：トレイの格子とビンの位置の表し方、ファーストフィットの手順
図5-4 ：CP-SATの探索（仮に決める→絞り込む→行き詰まったら戻る）
図5-5 ：区間変数と「重ならない」の意味
図5-6 ：トレイを横につないで1枚の板とみなす座標変換
図5-10：4つの配置方法の指標の比較
図5-11：4つの配置方法の1枚目のトレイ
図5-12：LNSの窓ごとの罰則の推移
図5-13：ビンの数と計算時間
"""
import csv
import json
import os

from _common import FIGURES
import kitting.plot  # 日本語フォントの設定
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

from _common import RESULTS

from kitting.bins import BinType, assign_cheapest
from kitting.config import TRAY_H as H, TRAY_W as W
from kitting.data import generate_portfolio
from kitting.layout import layout_rule, make_bins
from kitting.plot import _gray

CH4_CHOSEN = [BinType(1, 1), BinType(2, 2), BinType(4, 3), BinType(8, 1)]   # 第4章で選んだ4種類
BOM = "SA-03"


def draw_tray(ax, bins, pl, t, rank, n_steps):
    ax.set_axis_off()
    ax.set_xlim(-0.2, W + 0.2)
    ax.set_ylim(H + 0.2, -0.2)
    ax.set_aspect("equal")
    ax.add_patch(Rectangle((0, 0), W, H, fill=False, lw=1.2, ec="black"))
    for x in range(1, W):
        ax.plot([x, x], [0, H], lw=0.3, color="0.8")
    for y in range(1, H):
        ax.plot([0, W], [y, y], lw=0.3, color="0.8")
    for b in bins:
        p = pl[b.id]
        if p.tray != t:
            continue
        g = _gray(rank[b.step], n_steps)
        ax.add_patch(Rectangle((p.x + 0.06, p.y + 0.06), p.w - 0.12, p.h - 0.12,
                               fc=str(g), ec="black", lw=0.6, zorder=3))
        ax.text(p.x + p.w / 2, p.y + p.h / 2, b.step_label, ha="center", va="center",
                fontsize=7 if min(p.w, p.h) == 1 else 9,
                color="black" if g > 0.55 else "white", zorder=4)


def fig5_1():
    parts = generate_portfolio()[BOM]
    bins = make_bins(parts, assign_cheapest(parts, CH4_CHOSEN))
    steps = sorted({b.step for b in bins})
    rank = {s: i for i, s in enumerate(steps)}
    layouts = [("(a) 作業順の配置：工程ごとにまとめ、左から工程順に並べる", layout_rule(bins, "step")),
               ("(b) サイズ順の配置：小さいビンを上、大きいビンを下に詰める", layout_rule(bins, "size"))]
    n_trays = max(max(p.tray for p in pl.values()) for _, pl in layouts) + 1
    fig, axes = plt.subplots(n_trays, 2, figsize=(10.4, n_trays * 2.9 + 0.9), squeeze=False)
    for c, (title, pl) in enumerate(layouts):
        for t in range(n_trays):
            draw_tray(axes[t][c], bins, pl, t, rank, len(steps))
            axes[t][c].set_title((title + "\n" if t == 0 else "") + f"トレイ{t + 1}", fontsize=9)
    fig.suptitle(f"2008年の2つの設計案を再現（{BOM}、ビン{len(bins)}個）。"
                 "記号は工程、色が濃いほど後の工程", fontsize=10)
    fig.tight_layout()
    path = os.path.join(FIGURES, "fig5-1_two_designs.png")
    fig.savefig(path, dpi=200)
    plt.close(fig)
    print("saved", path)


def save(fig, name):
    path = os.path.join(FIGURES, name)
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("saved", path)


def grid(ax, w, h, labels=False):
    ax.set_axis_off()
    ax.set_aspect("equal")
    ax.add_patch(Rectangle((0, 0), w, h, fill=False, lw=1.2, ec="black"))
    for x in range(1, w):
        ax.plot([x, x], [0, h], lw=0.3, color="0.75")
    for y in range(1, h):
        ax.plot([0, w], [y, y], lw=0.3, color="0.75")
    if labels:
        for x in range(w):
            ax.text(x + 0.5, -0.35, str(x), ha="center", va="center", fontsize=6.5, color="0.35")
        for y in range(h):
            ax.text(-0.4, y + 0.5, str(y), ha="center", va="center", fontsize=6.5, color="0.35")


def box(ax, x, y, w, h, label="", g="0.8", lw=0.8, fs=8, color="black"):
    ax.add_patch(Rectangle((x + 0.06, y + 0.06), w - 0.12, h - 0.12, fc=g, ec="black", lw=lw, zorder=3))
    if label:
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=fs, color=color, zorder=4)


def fig5_2():
    """(a) 位置と向きの表し方 (b) ファーストフィットで4個置く"""
    fig = plt.figure(figsize=(10.4, 5.6))
    a = fig.add_axes([0.03, 0.42, 0.60, 0.52])
    grid(a, W, H, labels=True)
    a.set_xlim(-1, W + 0.3)
    a.set_ylim(H + 2.4, -1)
    box(a, 5, 2, 4, 3, "300×225\n回さない", g="0.82")
    box(a, 11, 3, 3, 4, "300×225\n90度回す", g="0.6", color="white")
    a.plot([5], [2], "o", ms=5, color="black", zorder=5)
    a.plot([11], [3], "o", ms=5, color="black", zorder=5)
    a.annotate("左上の角 (x, y) = (5, 2)\nw = 4、h = 3、r = 0", xy=(5, 2), xytext=(0.5, 9.9),
               fontsize=8, arrowprops=dict(arrowstyle="->", lw=0.7))
    a.annotate("(x, y) = (11, 3)\nw = 3、h = 4、r = 1", xy=(11, 3), xytext=(10.5, 9.9),
               fontsize=8, arrowprops=dict(arrowstyle="->", lw=0.7))
    a.set_title("(a) トレイ1枚＝横16×縦8マス（1マス75mm）。ビンの位置は左上の角の列 x・行 y、向きは r で表す",
                fontsize=8.5, loc="left", pad=14)
    t = fig.add_axes([0.66, 0.42, 0.32, 0.52])
    t.set_axis_off()
    rows = [("小型", "75×75", "1×1", "1"), ("中型", "150×150", "2×2", "4"),
            ("大型", "300×225", "4×3", "12"), ("長尺", "600×75", "8×1", "8")]
    tb = t.table(cellText=[list(r) for r in rows], colLabels=["ビン", "外形mm", "マス（横×縦）", "ブロック"],
                 loc="center", cellLoc="center")
    tb.auto_set_font_size(False)
    tb.set_fontsize(8)
    tb.scale(1, 1.5)
    t.set_title("第4章で選んだ4種類", fontsize=8.5)

    # (b) ファーストフィット：横6×縦3の小さなトレイに4個
    seq = [("①", 1, 1, 0, 0), ("②", 1, 1, 1, 0), ("③", 2, 2, 2, 0), ("④", 4, 1, 0, 2)]
    notes = ["①1×1：左上の角に置く", "②1×1：すぐ右の空き", "③2×2：右へ探して置く",
             "④4×1：1行目・2行目には\n4マス続く空きがない。\n3行目の左端に置く"]
    for i in range(4):
        ax = fig.add_axes([0.03 + i * 0.245, 0.02, 0.22, 0.3])
        grid(ax, 6, 3)
        ax.set_xlim(-0.2, 6.2)
        ax.set_ylim(3.2, -0.2)
        for j, (lab, w, h, x, y) in enumerate(seq[:i + 1]):
            box(ax, x, y, w, h, lab, g="0.35" if j == i else "0.85", color="white" if j == i else "black")
        ax.set_title(notes[i], fontsize=8, va="top", y=-0.12 if i < 3 else -0.1)
    fig.text(0.03, 0.355, "(b) ファーストフィット：上の行の左から空きを探し、最初に置ける場所に置く（濃い色が今置いたビン）",
             fontsize=8.5)
    save(fig, "fig5-2_grid_first_fit.png")


def fig5_4():
    """探索の木：仮に決める→絞り込む→行き詰まったら戻る"""
    fig, ax = plt.subplots(figsize=(9.6, 4.4))
    ax.set_axis_off()
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.2, 4.9)

    def node(x, y, text, g="white", lw=0.9, style="round,pad=0.08"):
        ax.add_patch(FancyBboxPatch((x - 1.0, y - 0.28), 2.0, 0.56, boxstyle=style, fc=g, ec="black", lw=lw))
        ax.text(x, y, text, ha="center", va="center", fontsize=8)

    def edge(x1, y1, x2, y2, text="", ls="-"):
        ax.annotate("", xy=(x2, y2 + 0.34), xytext=(x1, y1 - 0.34),
                    arrowprops=dict(arrowstyle="->", lw=0.8, ls=ls))
        if text:
            ax.text((x1 + x2) / 2 + 0.1, (y1 + y2) / 2, text, fontsize=7.5, ha="left", va="center", color="0.25")

    node(5, 4.4, "どのビンもまだ置いていない")
    node(2.6, 3.0, "ビンAを左上に置く")
    node(7.4, 3.0, "ビンAを右上に置く")
    node(1.2, 1.6, "ビンBの候補が減る")
    node(4.1, 1.6, "ビンCの置き場所がない", g="0.85")
    node(7.4, 1.6, "ビンB、Cも置ける")
    node(7.4, 0.4, "全部置けた（解）", g="0.6", lw=1.4)
    edge(5, 4.4, 2.6, 3.0, "仮に決める")
    edge(5, 4.4, 7.4, 3.0)
    edge(2.6, 3.0, 1.2, 1.6, "絞り込む")
    edge(2.6, 3.0, 4.1, 1.6)
    edge(7.4, 3.0, 7.4, 1.6)
    edge(7.4, 1.6, 7.4, 0.4)
    ax.annotate("", xy=(6.2, 3.05), xytext=(5.1, 1.75),
                arrowprops=dict(arrowstyle="->", lw=0.9, ls="--", connectionstyle="arc3,rad=-0.35"))
    ax.text(5.75, 2.25, "行き詰まったら戻り、\n別の決め方を試す", fontsize=7.5, ha="left", color="0.25")
    ax.text(4.1, 0.85, "行き詰まった理由を覚えておき、\n同じ失敗を繰り返さない（学習）", fontsize=7.5, ha="center", va="center", color="0.25")
    ax.set_title("CP-SATの探索のイメージ（数独を解くときと同じ「仮に決める・絞り込む・戻る」）", fontsize=9.5)
    save(fig, "fig5-4_search_tree.png")


def fig5_5():
    """区間変数：横の帯と縦の帯が両方重なったときだけ、ビンが重なる"""
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 3.9))
    cases = [("(a) 横の帯は重なるが、縦の帯は重ならない → ビンは重ならない（置ける）", (1, 1, 4, 2), (3, 4, 3, 2)),
             ("(b) 横の帯も縦の帯も重なる → ビンが重なる（置けない）", (1, 1, 4, 3), (3, 3, 3, 3))]
    for ax, (title, A, B) in zip(axes, cases):
        grid(ax, 9, 7)
        ax.set_xlim(-1.6, 9.3)
        ax.set_ylim(7.3, -1.8)
        for (x, y, w, h), lab, g in ((A, "A", "0.85"), (B, "B", "0.55")):
            ax.add_patch(Rectangle((x, y), w, h, fc=g, ec="black", lw=0.9, alpha=0.85, zorder=3))
            ax.text(x + w / 2, y + h / 2, lab, ha="center", va="center", fontsize=10, zorder=4,
                    color="white" if g == "0.55" else "black")
        # 横の帯（上に投影）と縦の帯（左に投影）
        for (x, y, w, h), off, g in ((A, -0.6, "0.85"), (B, -1.2, "0.55")):
            ax.add_patch(Rectangle((x, off), w, 0.4, fc=g, ec="black", lw=0.6))
            ax.add_patch(Rectangle((off - 0.2, y), 0.4, h, fc=g, ec="black", lw=0.6))
        ax.text(9.1, -0.9, "横の帯", fontsize=7.5, ha="left", va="center")
        ax.text(-1.0, 7.25, "縦の帯", fontsize=7.5, ha="center", va="top")
        ax.set_title(title, fontsize=8.5)
    fig.suptitle("区間変数（始まり・長さ・終わり）。AddNoOverlap2Dは、横と縦の両方で帯が重なる組を禁止する", fontsize=9.5)
    fig.tight_layout()
    save(fig, "fig5-5_intervals.png")


def fig5_6():
    """トレイを横につなぐ：全体の列 X = 16t + x"""
    fig, ax = plt.subplots(figsize=(10.4, 2.9))
    n = 2
    grid(ax, W * n, H)
    ax.plot([W, W], [0, H], lw=2.2, color="black")
    ax.set_xlim(-0.5, W * n + 0.5)
    ax.set_ylim(H + 1.9, -1.4)
    for t in range(n):
        ax.text(t * W + W / 2, -0.8, f"トレイ{t + 1}（t = {t}）", ha="center", fontsize=8.5)
        ax.text(t * W + W / 2, H + 0.65, f"トレイ内の列 x = 0〜15", ha="center", fontsize=7.5, color="0.35")
        ax.text(t * W + W / 2, H + 1.35, f"全体の列 X = {t * W}〜{t * W + W - 1}", ha="center", fontsize=7.5)
    box(ax, 3, 2, 2, 2, "", g="0.85")
    box(ax, W + 3, 2, 2, 2, "", g="0.55")
    ax.text(4, 3, "t=0, x=3\nX=3", ha="center", va="center", fontsize=7, zorder=5)
    ax.text(W + 4, 3, "t=1, x=3\nX=19", ha="center", va="center", fontsize=7, color="white", zorder=5)
    ax.set_title("2つのビンは同じ「3列目」だが、全体の列 X = 16t + x で見ると3列目と19列目なので重ならない",
                 fontsize=9)
    save(fig, "fig5-6_long_board.png")


def load_layouts():
    with open(os.path.join(RESULTS, "ch5_layouts.json"), encoding="utf-8") as f:
        return json.load(f)


NAMES = {"size_rule": "① サイズ順ルール", "min_trays": "② 枚数だけ最小化",
         "step_rule": "③ 作業順ルール", "lns": "④ 作業順の最適化"}


def fig5_10():
    """5つの指標のうち、差の出る4つを並べる（トレイ枚数はどれも4枚）"""
    with open(os.path.join(RESULTS, "ch5_metrics.csv"), encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    labels = ["①", "②", "③", "④"]
    specs = [("トレイをまたぐ工程（/31）", "split_steps", "{:.0f}", "少ないほど良い"),
             ("工程の散らばり（マス）", "avg_spread", "{:.1f}", "小さいほど良い"),
             ("読み順の一致率（%）", "order_match", "{:.1f}", "高いほど良い"),
             ("トレイ間の移動（回）", "tray_switches", "{:.0f}", "少ないほど良い")]
    fig, axes = plt.subplots(1, 4, figsize=(10.4, 3.0))
    for ax, (title, key, fmt, better) in zip(axes, specs):
        vals = [float(r[key]) * (100 if key == "order_match" else 1) for r in rows]
        bars = ax.bar(range(4), vals, color=["0.8", "0.8", "0.55", "0.2"], edgecolor="black", lw=0.5)
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v, fmt.format(v), ha="center", va="bottom", fontsize=7.5)
        ax.set_xticks(range(4))
        ax.set_xticklabels(labels, fontsize=8)
        ax.set_title(f"{title}\n{better}", fontsize=8)
        ax.tick_params(axis="y", labelsize=7)
        ax.set_ylim(0, max(vals) * 1.2)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    fig.suptitle("4つの配置方法の比較（SA-10、トレイ枚数はどれも4枚）。"
                 "①サイズ順ルール ②枚数だけ最小化 ③作業順ルール ④作業順の最適化", fontsize=9)
    fig.tight_layout()
    save(fig, "fig5-10_metrics.png")


def fig5_11():
    """4つの配置方法の1枚目のトレイ"""
    d = load_layouts()
    bins = d["bins"]
    steps = sorted({b["step"] for b in bins})
    rank = {s: i for i, s in enumerate(steps)}
    fig, axes = plt.subplots(2, 2, figsize=(10.4, 5.6))
    for ax, k in zip(axes.flat, ["size_rule", "min_trays", "step_rule", "lns"]):
        pl = d["layouts"][k]
        grid(ax, W, H)
        ax.set_xlim(-0.2, W + 0.2)
        ax.set_ylim(H + 0.2, -0.2)
        for b in bins:
            p = pl[str(b["id"])]
            if p["tray"] != 0:
                continue
            g = _gray(rank[b["step"]], len(steps))
            box(ax, p["x"], p["y"], p["w"], p["h"], b["step_label"], g=str(g),
                fs=6.5 if min(p["w"], p["h"]) == 1 else 8, color="black" if g > 0.55 else "white", lw=0.6)
        ax.set_title(NAMES[k], fontsize=9)
    fig.suptitle("4つの配置方法の1枚目のトレイ（SA-10）。記号は工程、色が濃いほど後の工程", fontsize=10)
    fig.tight_layout()
    save(fig, "fig5-11_tray1.png")


def fig5_12():
    """LNSの窓ごとの罰則の推移"""
    hist = load_layouts()["info"]["lns"]["history"]
    ys = [h["objective"] for h in hist]
    fig, ax = plt.subplots(figsize=(8.6, 3.2))
    ax.step(range(len(ys)), ys, where="post", color="black", lw=1.4)
    ax.plot(range(len(ys)), ys, "o", ms=2.5, color="black")
    for p in (1, 2, 3):
        idx = [i for i, h in enumerate(hist) if h["pass_"] == p]
        ax.axvspan(idx[0] - 0.5, idx[-1] + 0.5, color="0.93" if p % 2 else "white", zorder=0)
        ax.text((idx[0] + idx[-1]) / 2, max(ys) * 1.005, f"{p}周目", ha="center", va="bottom", fontsize=8)
    ax.annotate(f"作業順ルール {ys[0]:,.0f}", xy=(0, ys[0]), xytext=(2.5, ys[0] - 30), fontsize=8,
                arrowprops=dict(arrowstyle="->", lw=0.6))
    ax.annotate(f"3周後 {ys[-1]:,.0f}（−{(1 - ys[-1] / ys[0]) * 100:.0f}%）", xy=(len(ys) - 1, ys[-1]),
                xytext=(len(ys) - 13, ys[-1] + 90), fontsize=8, arrowprops=dict(arrowstyle="->", lw=0.6))
    ax.set_xlabel("解き直した窓の数（4工程の窓を2工程ずつずらす）", fontsize=8)
    ax.set_ylabel("罰則の合計", fontsize=8)
    ax.tick_params(labelsize=7)
    ax.set_ylim(min(ys) - 60, max(ys) + 60)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.set_title("LNSで罰則が下がっていく様子（SA-10）。下がるのはほとんど1周目で、2周目以降はわずか",
                 fontsize=9)
    save(fig, "fig5-12_lns_history.png")


def fig5_13():
    """ビンの数と計算時間"""
    with open(os.path.join(RESULTS, "scale_test.csv"), encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    marks = {"1": "o", "2": "s", "3": "^", "4": "D"}
    for t in sorted({r["trays"] for r in rows}):
        rs = [r for r in rows if r["trays"] == t]
        ax.scatter([int(r["bins"]) for r in rs], [float(r["seconds"]) for r in rs], marker=marks[t],
                   s=30, facecolor="0.5", edgecolor="black", lw=0.6, label=f"トレイ{t}枚", zorder=3)
    for r in rows:
        ax.annotate(r["bom"][-2:], (int(r["bins"]), float(r["seconds"])), xytext=(4, 3),
                    textcoords="offset points", fontsize=7, color="0.3")
    ax.set_xlabel("ビンの数", fontsize=8)
    ax.set_ylabel("計算時間（秒、LNS 2周）", fontsize=8)
    ax.tick_params(labelsize=7)
    ax.set_xlim(0, 140)
    ax.set_ylim(0, 140)
    ax.legend(fontsize=7, frameon=False, loc="upper left")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.set_title("ビンの数と計算時間（事前組立品10種類、数字はSA-01〜SA-10）。\n"
                 "一度に解くのは常に4工程分なので、ビンが6倍でも2分以内", fontsize=9)
    save(fig, "fig5-13_scale.png")


if __name__ == "__main__":
    fig5_1()
    fig5_2()
    fig5_4()
    fig5_5()
    fig5_6()
    fig5_10()
    fig5_11()
    fig5_12()
    fig5_13()
