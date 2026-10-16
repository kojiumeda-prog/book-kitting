"""第4章の図（図4-1〜4-5、4-7、4-9）を作る。白黒でも読めるよう、濃淡・線種・文字で区別する。

    python scripts/ch4_figures.py
"""
import os
from collections import Counter

from _common import FIGURES
import kitting.plot  # 日本語フォントの設定
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from kitting.bins import BinType, assign_cheapest, bins_needed
from kitting.config import BLOCK_MM, CANDIDATE_BINS, TRAY_H, TRAY_W
from kitting.data import COMPLEX_BOM, generate_portfolio
from kitting.sizing import solve_sizing

CAND = [BinType(*t) for t in CANDIDATE_BINS]


def save(fig, name):
    path = os.path.join(FIGURES, name)
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("saved", path)


def fig4_1():
    """寸法候補18種類を同じ縮尺で並べる"""
    fig, ax = plt.subplots(figsize=(8, 4.2))
    x = y = 0
    row_h = 0
    for k in sorted(CAND, key=lambda k: (k.h, k.w)):
        if x + k.w > 30:
            x, y = 0, y + row_h + 1.6
            row_h = 0
        ax.add_patch(Rectangle((x, y), k.w, k.h, fc="0.9", ec="black", lw=0.8))
        ax.text(x + k.w / 2, y + k.h + 0.45, k.name, ha="center", va="center", fontsize=7)
        x += k.w + 0.8
        row_h = max(row_h, k.h)
    ax.set_xlim(-0.5, 30.5)
    ax.set_ylim(y + row_h + 1, -0.5)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(f"寸法候補18種類（外形mm、1マス＝{BLOCK_MM}mmのブロック）", fontsize=10)
    save(fig, "fig4-1_candidates.png")


def fig4_2_3_4(boms):
    """SA-01：部品×寸法の必要個数の表（図4-2）、K=3で選ばれた寸法（図4-3）と割当（図4-4）"""
    parts = boms["SA-01"]
    r = solve_sizing({"SA-01": parts}, CAND, K=3)
    chosen = r.chosen
    cols = sorted(set(chosen) | {BinType(2, 1), BinType(3, 2), BinType(4, 4)}, key=lambda k: (k.area, k.w))
    sample = [p for p in parts if not p.hardware][:6] + [p for p in parts if p.hardware][:1]

    # 図4-2
    fig, ax = plt.subplots(figsize=(8.2, 3.6))
    ax.axis("off")
    cell = [[("—" if (n := bins_needed(p, k)) is None else str(n)) for k in cols] for p in sample]
    labels = [f"{p.name} {p.w_mm}×{p.l_mm}mm ×{p.qty}" for p in sample]
    tb = ax.table(cellText=cell, rowLabels=labels, colLabels=[k.name for k in cols],
                  loc="center", cellLoc="center")
    tb.auto_set_font_size(False)
    tb.set_fontsize(8)
    tb.scale(1, 1.5)
    for (i, j), c in tb.get_celld().items():
        if i == 0 and j >= 0 and cols[j] in chosen:
            c.set_facecolor("0.8")
            c.get_text().set_fontweight("bold")
        if i >= 1 and j >= 0:
            p, k = sample[i - 1], cols[j]
            if r.assign[("SA-01", p.part_no)][0] == k:
                c.set_linewidth(2.0)
                c.get_text().set_fontweight("bold")
    ax.set_title("部品×寸法候補ごとの必要ビン数 n（—は入らない）\n"
                 "灰色の列＝採用した寸法（y=1）、太枠＝割り当てた組合せ（x=1）。SA-01、K=3の解", fontsize=9)
    save(fig, "fig4-2_n_matrix.png")

    # 図4-3 と 図4-4
    groups = {k: [] for k in chosen}
    for p in parts:
        k, n = r.assign[("SA-01", p.part_no)]
        groups[k].append((p, n))
    fig, axes = plt.subplots(1, len(chosen), figsize=(9, 3.8),
                             gridspec_kw={"width_ratios": [max(2.5, k.w) for k in chosen]})
    for ax, k in zip(axes, chosen):
        ax.add_patch(Rectangle((0, 0), k.w, k.h, fc="0.88", ec="black", lw=1.2))
        ax.text(k.w / 2, k.h / 2, k.name, ha="center", va="center", fontsize=9, fontweight="bold")
        lines = [f"{p.name}（{p.w_mm}×{p.l_mm}）×{n}個" for p, n in groups[k]]
        total = sum(n for _, n in groups[k])
        ax.text(0, k.h + 0.5, f"ビン{total}個\n" + "\n".join(lines), va="top", fontsize=7)
        ax.set_xlim(-0.2, max(2.5, k.w) + 0.2)
        ax.set_ylim(k.h + 0.5 + 0.42 * (len(lines) + 1), -0.3)
        ax.set_aspect("equal")
        ax.axis("off")
    fig.suptitle(f"SA-01でK=3のとき選ばれた寸法と、入れた部品（必要面積 {round(r.value)} ブロック）",
                 fontsize=10)
    save(fig, "fig4-3_4_sa01_k3.png")
    return r


def fig4_5(boms):
    """最悪ケース：寸法ごとに、BOMごとの必要個数と、その最大（共通トレイに用意する個数）"""
    r = solve_sizing(boms, CAND, K=4, objective="worst")
    per = Counter()
    for (bom, _), (k, n) in r.assign.items():
        per[(bom, k)] += n
    names = list(boms)
    fig, axes = plt.subplots(1, len(r.chosen), figsize=(10, 3.2), sharey=False)
    for ax, k in zip(axes, r.chosen):
        vals = [per[(b, k)] for b in names]
        mx = max(vals)
        ax.bar(range(len(names)), vals, color=["black" if v == mx else "0.75" for v in vals],
               edgecolor="black", lw=0.5)
        ax.axhline(mx, ls="--", lw=0.8, color="black")
        ax.text(len(names) - 0.5, mx, f"用意する数 {mx}", ha="right", va="bottom", fontsize=7)
        ax.set_title(f"{k.name}mm（{k.area}ブロック）", fontsize=8)
        ax.set_xticks(range(len(names)))
        ax.set_xticklabels([b[-2:] for b in names], fontsize=6)
        ax.tick_params(axis="y", labelsize=7)
        ax.set_ylim(0, mx * 1.25)
    axes[0].set_ylabel("必要なビンの数", fontsize=8)
    fig.suptitle("最悪ケースの考え方：寸法ごとに、どのBOMでも足りる数（最大値）を共通トレイに用意する\n"
                 "横軸はサブアッセンブリSA-01〜SA-10、黒い棒が最大のBOM", fontsize=9)
    fig.tight_layout()
    save(fig, "fig4-5_worst_case.png")
    return r


def fig4_7():
    """ブロック倍数のビンがトレイの格子に収まる様子と、入れ替えの例"""
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.2), gridspec_kw={"width_ratios": [16, 9]})
    for ax in (a1, a2):
        ax.set_aspect("equal")
        ax.axis("off")
    # 左：トレイに4種類（1,4,8,16ブロック）を並べる
    a1.add_patch(Rectangle((0, 0), TRAY_W, TRAY_H, fill=False, lw=1.4))
    for x in range(1, TRAY_W):
        a1.plot([x, x], [0, TRAY_H], lw=0.3, color="0.8")
    for y in range(1, TRAY_H):
        a1.plot([0, TRAY_W], [y, y], lw=0.3, color="0.8")
    items = [(0, 0, 4, 4, "16"), (4, 0, 4, 2, "8"), (4, 2, 4, 2, "8"), (8, 0, 2, 2, "4"), (10, 0, 2, 2, "4"),
             (8, 2, 2, 2, "4"), (12, 0, 1, 1, "1"), (13, 0, 1, 1, "1"), (12, 1, 1, 1, "1"), (13, 1, 1, 1, "1"),
             (0, 4, 4, 4, "16"), (4, 4, 2, 2, "4"), (6, 4, 2, 2, "4"), (8, 4, 4, 2, "8")]
    for x, y, w, h, lab in items:
        g = {"1": "0.95", "4": "0.8", "8": "0.6", "16": "0.45"}[lab]
        a1.add_patch(Rectangle((x + 0.05, y + 0.05), w - 0.1, h - 0.1, fc=g, ec="black", lw=0.6, zorder=3))
        a1.text(x + w / 2, y + h / 2, lab, ha="center", va="center", fontsize=8, zorder=4,
                color="white" if lab == "16" else "black")
    a1.set_xlim(-0.2, TRAY_W + 0.2)
    a1.set_ylim(TRAY_H + 0.2, -0.2)
    a1.set_title("(a) 1・4・8・16ブロックのビンはすき間なく並ぶ（数字はブロック数）", fontsize=8)
    # 右：8ブロック1個 ＝ 4ブロック1個＋1ブロック4個
    a2.add_patch(Rectangle((0, 0), 4, 2, fc="0.6", ec="black", lw=0.8))
    a2.text(2, 1, "8", ha="center", va="center", fontsize=9)
    a2.text(4.5, 1, "＝", ha="center", va="center", fontsize=12)
    a2.add_patch(Rectangle((5, 0), 2, 2, fc="0.8", ec="black", lw=0.8))
    a2.text(6, 1, "4", ha="center", va="center", fontsize=9)
    for i, (x, y) in enumerate([(7, 0), (8, 0), (7, 1), (8, 1)]):
        a2.add_patch(Rectangle((x, y), 1, 1, fc="0.95", ec="black", lw=0.8))
        a2.text(x + 0.5, y + 0.5, "1", ha="center", va="center", fontsize=8)
    a2.set_xlim(-0.2, 9.2)
    a2.set_ylim(2.6, -0.4)
    a2.set_title("(b) 入れ替えの例：8ブロック1個の場所に4ブロック1個と1ブロック4個", fontsize=8)
    fig.suptitle("ブロックの整数倍にそろえたビン", fontsize=10)
    save(fig, "fig4-7_block_multiples.png")


def fig4_9(boms, r4):
    """第5章への入力：SA-10のビン一覧"""
    cnt = Counter()
    for k, n in assign_cheapest(boms[COMPLEX_BOM], r4.chosen).values():
        cnt[k] += n
    rows = [[k.name, str(k.area), str(cnt[k]), str(k.area * cnt[k])] for k in r4.chosen]
    rows.append(["合計", "", str(sum(cnt.values())), str(sum(k.area * n for k, n in cnt.items()))])
    fig, ax = plt.subplots(figsize=(5.5, 1.9))
    ax.axis("off")
    tb = ax.table(cellText=rows, colLabels=["外形（mm）", "1個のブロック数", "個数", "面積（ブロック）"],
                  loc="center", cellLoc="center")
    tb.auto_set_font_size(False)
    tb.set_fontsize(8)
    tb.scale(1, 1.4)
    for j in range(4):
        tb[(len(rows), j)].get_text().set_fontweight("bold")
    ax.set_title(f"SA-10（39工程・部品{len(boms[COMPLEX_BOM])}点）に必要なビン：第5章への入力\n"
                 f"トレイ1枚は{TRAY_W * TRAY_H}ブロックなので、面積の上では最低"
                 f"{-(-sum(k.area * n for k, n in cnt.items()) // (TRAY_W * TRAY_H))}枚", fontsize=8)
    save(fig, "fig4-9_sa10_bins.png")


def main():
    boms = generate_portfolio()
    fig4_1()
    fig4_2_3_4(boms)
    r4 = fig4_5(boms)
    fig4_7()
    fig4_9(boms, r4)


if __name__ == "__main__":
    main()
