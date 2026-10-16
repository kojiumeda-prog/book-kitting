"""第5章の図（ch5_layout.py が作る図5-3・5-7〜5-9以外）を作る。

    python scripts/ch5_figures.py

図5-1：2008年の論文で手描きした2つの設計案（作業順の配置／サイズ順の配置）を、
       中くらいの事前組立品 SA-03 で再現したもの。論文の図を見なくても違いがわかるようにする。
"""
import os

from _common import FIGURES
import kitting.plot  # 日本語フォントの設定
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

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


if __name__ == "__main__":
    fig5_1()
