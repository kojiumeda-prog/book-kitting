"""図の出力（matplotlib）。Kindleの白黒表示でも読めるよう、色ではなく濃淡と工程記号で区別する。"""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Rectangle

from .config import TRAY_W as W, TRAY_H as H
from .layout import Bin, Placement

# 日本語フォント（macOS: ヒラギノ / Windows: 游ゴシック / Linux: Noto Sans CJK）
_JP = ["Hiragino Sans", "Hiragino Kaku Gothic ProN", "Yu Gothic", "Meiryo",
       "Noto Sans CJK JP", "Noto Sans CJK TC", "IPAexGothic"]
_have = {f.name for f in font_manager.fontManager.ttflist}
plt.rcParams["font.family"] = [f for f in _JP if f in _have] or ["sans-serif"]
plt.rcParams["axes.unicode_minus"] = False


def _gray(rank: int, n: int) -> float:
    """工程の順番 -> 灰色の濃さ（0=黒, 1=白）。最初の工程が明るく、最後の工程が暗い。"""
    return 0.92 - 0.62 * rank / max(1, n - 1)


def draw_layout(bins: list[Bin], pl: dict[int, Placement], title: str, path: str,
                cols: int = 2):
    steps = sorted({b.step for b in bins})
    rank = {s: i for i, s in enumerate(steps)}
    n_trays = max(p.tray for p in pl.values()) + 1
    rows = (n_trays + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 5.2, rows * 2.9 + 0.5), squeeze=False)
    for t in range(rows * cols):
        ax = axes[t // cols][t % cols]
        ax.set_axis_off()
        if t >= n_trays:
            continue
        ax.set_xlim(-0.2, W + 0.2)
        ax.set_ylim(H + 0.2, -0.2)
        ax.set_aspect("equal")
        ax.add_patch(Rectangle((0, 0), W, H, fill=False, lw=1.2, ec="black"))
        for x in range(1, W):
            ax.plot([x, x], [0, H], lw=0.3, color="0.8")
        for y in range(1, H):
            ax.plot([0, W], [y, y], lw=0.3, color="0.8")
        used = 0
        for b in bins:
            p = pl[b.id]
            if p.tray != t:
                continue
            used += p.w * p.h
            g = _gray(rank[b.step], len(steps))
            ax.add_patch(Rectangle((p.x + 0.06, p.y + 0.06), p.w - 0.12, p.h - 0.12,
                                   fc=str(g), ec="black", lw=0.6, zorder=3))
            ax.text(p.x + p.w / 2, p.y + p.h / 2, b.step_label, ha="center", va="center",
                    fontsize=7 if min(p.w, p.h) == 1 else 9,
                    color="black" if g > 0.55 else "white", zorder=4)
        ax.set_title(f"トレイ{t + 1}（使用 {used}/{W * H} ブロック）", fontsize=9)
    fig.suptitle(title, fontsize=11)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def draw_k_curve(rows: list[dict], path: str, thesis: dict | None = None):
    """第4章：採用する寸法の種類数 K と必要面積の関係。目的ごとに縦軸の大きさが違うので2枚に分ける。"""
    fig, axes = plt.subplots(1, 2, figsize=(8.0, 3.2))
    panels = (("total", "(a) 全BOMの合計面積"), ("worst", "(b) 共通トレイの面積（最悪ケース）"))
    for ax, (obj, title) in zip(axes, panels):
        rr = [r for r in rows if r["objective"] == obj]
        ks, vs = [r["K"] for r in rr], [r["area_blocks"] for r in rr]
        ax.plot(ks, vs, marker="o", color="black", label="最適化（MILP）")
        for k, v in zip(ks, vs):
            ax.annotate(f"{v:,}", (k, v), xytext=(0, 6), textcoords="offset points",
                        ha="center", fontsize=7)
        if thesis:
            ax.scatter([4], [thesis[obj]], marker="s", facecolor="white", edgecolor="black",
                       s=45, zorder=3, label="論文の4種類＋割当ルール")
            if obj == "total":   # 最適化の点と重なるので、引き出し線で白い四角につなぐ
                ax.annotate(f"{thesis[obj]:,}（論文）", (4, thesis[obj]), xytext=(14, -24),
                            textcoords="offset points", fontsize=7, ha="left", va="center",
                            arrowprops=dict(arrowstyle="-", lw=0.6, color="black", shrinkA=0, shrinkB=4))
            else:                # 白い四角の真上に置く
                ax.annotate(f"{thesis[obj]:,}", (4, thesis[obj]), xytext=(0, 7),
                            textcoords="offset points", fontsize=7, ha="center")
        ax.set_title(title, fontsize=9)
        ax.set_xlabel("採用する部品箱寸法の種類数 K", fontsize=8)
        ax.set_ylabel("必要なトレイ面積 [ブロック]", fontsize=8)
        ax.set_xticks(ks)
        ax.set_ylim(0, max(vs) * 1.15)
        ax.tick_params(labelsize=7)
        ax.grid(True, lw=0.3, color="0.85")
    axes[0].legend(fontsize=7, frameon=False, loc="upper right")
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)
