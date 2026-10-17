"""第6章の図。

    python scripts/ch6_figures.py      # 先に ch6_tradeoff.py を実行しておく（SA-02の配置は1分ほどで計算する）

図6-1：SA-02の配置（作業順ルール／第5章の罰則／罰則(d)を追加）
図6-2：重みを3通りに変えた配置（SA-02）
図6-3：重みと指標の関係（SA-10とSA-02）
図6-5：ε制約法の解（枚数と罰則、トレイ間の移動）
図6-6：代表的な3つの解の配置（ε=4、ε=5、第5章）
"""
import csv
import json
import os

import matplotlib.pyplot as plt

from _common import FIGURES, RESULTS
from ch5_figures import box, grid
from kitting.bins import BinType, assign_cheapest
from kitting.config import TRAY_H as H, TRAY_W as W
from kitting.data import generate_portfolio
from kitting.evaluate import check_feasible, evaluate
from kitting.layout import improve_lns, layout_rule, make_bins
from kitting.plot import _gray

CH4_CHOSEN = [BinType(1, 1), BinType(2, 2), BinType(4, 3), BinType(8, 1)]


def save(fig, name):
    path = os.path.join(FIGURES, name)
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("saved", path)


def draw_tray(ax, bins, pl, tray=0, title=""):
    """bins: dict のリスト（id, step, step_label）、pl: {id文字列: {tray,x,y,w,h}}"""
    steps = sorted({b["step"] for b in bins})
    rank = {s: i for i, s in enumerate(steps)}
    grid(ax, W, H)
    ax.set_xlim(-0.2, W + 0.2)
    ax.set_ylim(H + 0.2, -0.2)
    for b in bins:
        p = pl[str(b["id"])]
        if p["tray"] != tray:
            continue
        g = _gray(rank[b["step"]], len(steps))
        box(ax, p["x"], p["y"], p["w"], p["h"], b["step_label"], g=str(g),
            fs=6.5 if min(p["w"], p["h"]) == 1 else 8, color="black" if g > 0.55 else "white", lw=0.6)
    if title:
        ax.set_title(title, fontsize=9)


def sa02_layouts():
    path = os.path.join(RESULTS, "ch6_sa02_layouts.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    parts = generate_portfolio()["SA-02"]
    bins = make_bins(parts, assign_cheapest(parts, CH4_CHOSEN))
    init = layout_rule(bins, "step")
    out = {"bins": [b.to_dict() for b in bins], "layouts": {}, "metrics": {}}
    cases = {"step_rule": None, "ch5": {}, "tail60": {"tail_w": 60}}
    for k, w in cases.items():
        pl = init if w is None else improve_lns(bins, init, 1, passes=2, det_time=3.0, log=None, **w)[0]
        check_feasible(bins, pl)
        out["layouts"][k] = {str(i): vars(p) for i, p in pl.items()}
        out["metrics"][k] = evaluate(bins, pl)
        print(k, out["metrics"][k], flush=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)
    return out


def fig6_1():
    d = sa02_layouts()
    names = {"step_rule": "(a) 作業順ルール", "ch5": "(b) 第5章の罰則で最適化", "tail60": "(c) 罰則(d)を追加（重み60）"}
    fig, axes = plt.subplots(3, 1, figsize=(5.6, 8.4))
    for ax, k in zip(axes, names):
        m = d["metrics"][k]
        draw_tray(ax, d["bins"], d["layouts"][k],
                  title=f"{names[k]}　読み順との一致率 {m['order_match']:.0%}、広がり {m['avg_spread']:.2f}")
    fig.suptitle("SA-02の配置。記号は工程、色が濃いほど後の工程", fontsize=10)
    fig.tight_layout()
    save(fig, "fig6-1_sa02_three.png")


def load():
    with open(os.path.join(RESULTS, "ch6_layouts.json"), encoding="utf-8") as f:
        return json.load(f)


def fig6_2():
    d = load()
    with open(os.path.join(RESULTS, "ch6_weights_sa02.csv"), encoding="utf-8") as f:
        m = {r["weights"]: r for r in csv.DictReader(f)}
    fig, axes = plt.subplots(3, 1, figsize=(5.6, 8.4))
    for ax, (i, k) in zip(axes, enumerate(d["weights_sa02"])):
        r = m[k]
        draw_tray(ax, d["bins_sa02"], d["weights_sa02"][k],
                  title=f"({'abc'[i]}) {k}　読み順との一致率 {float(r['order_match']):.0%}、広がり {float(r['avg_spread']):.2f}")
    fig.suptitle("重みを3通りに変えた配置（SA-02、トレイ1枚）。記号は工程、色が濃いほど後の工程", fontsize=10)
    fig.tight_layout()
    save(fig, "fig6-2_weights_sa02.png")


def fig6_3():
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.9))
    for ax, (fname, title, xlim, ylim) in zip(axes, [
            ("ch6_weights.csv", "(a) SA-10（トレイ4枚、ほぼ満杯）", (7.7, 8.4), (90, 100)),
            ("ch6_weights_sa02.csv", "(b) SA-02（トレイ1枚、余裕あり）", (6.0, 7.8), (40, 100))]):
        with open(os.path.join(RESULTS, fname), encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        for r, mk in zip(rows, ["o", "^", "s"]):
            x, y = float(r["avg_spread"]), float(r["order_match"]) * 100
            ax.scatter([x], [y], marker=mk, s=70, facecolor="white", edgecolor="black", zorder=3)
            dy = 6 if r["weights"] == "読み順重視" else -10      # 近い点の文字が重ならないように
            ax.annotate(r["weights"], (x, y), textcoords="offset points", xytext=(8, dy), fontsize=8.5)
        ax.set_xlabel("まとまり（平均の広がり、マス）　← 小さいほどよい", fontsize=8.5)
        ax.set_ylabel("読み順との一致率（%）　↑ 高いほどよい", fontsize=8.5)
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
        ax.grid(lw=0.3, color="0.8")
        ax.set_title(title, fontsize=9.5)
    fig.suptitle("重みと指標の関係（縦軸・横軸の目盛りは左右で違う）", fontsize=10)
    fig.tight_layout()
    save(fig, "fig6-3_weights_scatter.png")


def fig6_5():
    with open(os.path.join(RESULTS, "ch6_epsilon.csv"), encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    with open(os.path.join(RESULTS, "ch5_metrics.csv"), encoding="utf-8") as f:
        ch5 = [r for r in csv.DictReader(f) if r["penalty"]][-1]
    best = {}
    for r in rows:                                   # 支配されているかどうか
        best[int(r["trays"])] = float(r["penalty"])
    fig, ax = plt.subplots(figsize=(5.6, 3.9))
    xs = [int(r["trays"]) for r in rows]
    ys = [float(r["penalty"]) for r in rows]
    for x, y in zip(xs, ys):
        dominated = any(x2 <= x and y2 < y and (x2, y2) != (x, y) for x2, y2 in zip(xs, ys))
        ax.scatter([x], [y], s=70, marker="o", facecolor="white" if dominated else "black",
                   edgecolor="black", zorder=3)
        ax.annotate(f"ε={x}" + ("（支配された解）" if dominated else ""), (x, y),
                    textcoords="offset points", xytext=(8, 4), fontsize=8.5)
    ax.scatter([int(ch5["trays"])], [float(ch5["penalty"])], marker="x", s=70, color="black", zorder=3)
    ax.annotate("第5章の解", (int(ch5["trays"]), float(ch5["penalty"])),
                textcoords="offset points", xytext=(8, -4), fontsize=8.5)
    ax.set_xlabel("トレイの枚数")
    ax.set_ylabel("罰則の合計")
    ax.set_xticks([4, 5, 6])
    ax.set_xlim(3.6, 7.4)
    ax.set_ylim(1400, 1640)
    ax.grid(lw=0.3, color="0.8")
    ax2 = ax.twinx()
    ax2.plot(xs, [int(r["tray_switches"]) for r in rows], ls="--", color="0.3", marker="s",
             mfc="white", ms=5, lw=1)
    ax2.set_ylabel("トレイ間の移動（回、破線）")
    ax2.set_ylim(0, 8)
    ax.set_title("ε制約法の解（SA-10）", fontsize=10)
    save(fig, "fig6-5_epsilon.png")


def fig6_6():
    d = load()
    with open(os.path.join(RESULTS, "ch5_layouts.json"), encoding="utf-8") as f:
        ch5 = json.load(f)["layouts"]["lns"]
    cases = [("ε=4（4枚）", d["epsilon"]["4"]), ("ε=5（5枚）", d["epsilon"]["5"]), ("第5章の解（4枚）", ch5)]
    fig, axes = plt.subplots(3, 5, figsize=(13, 4.6))
    for r, (name, pl) in enumerate(cases):
        n = max(p["tray"] for p in pl.values()) + 1
        for t in range(5):
            ax = axes[r][t]
            ax.set_axis_off()
            if t < n:
                draw_tray(ax, d["bins"], pl, tray=t, title=f"{name} トレイ{t + 1}" if t == 0 else f"トレイ{t + 1}")
    fig.suptitle("代表的な3つの解の配置（SA-10）。記号は工程、色が濃いほど後の工程", fontsize=10)
    fig.tight_layout()
    save(fig, "fig6-6_three_solutions.png")


if __name__ == "__main__":
    for f in (fig6_1, fig6_2, fig6_3, fig6_5, fig6_6):
        f()
