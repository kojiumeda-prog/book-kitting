"""第6章：作業順か面積効率か。

    python scripts/ch6_tradeoff.py            # 3つの実験をすべて行う（20分前後）
    python scripts/ch6_tradeoff.py --quick    # 計算時間を短くして動作確認

実験1（6.2節、コード6-1）：罰則の重みを3通りに変えて、SA-10の配置がどう変わるか
実験2（6.4節、コード6-2）：トレイ枚数の上限を4・5・6枚にして解く（ε制約法）。枚数と使いやすさの関係
実験1b（6.2節）：同じ3通りの重みを、トレイに余裕のあるSA-02で試す（--sa02-weights でこれだけ実行）
実験3（6.2節の補足）：SA-02で順序一致率が下がった問題を、罰則(d)を足して直す
"""
import csv
import json
import math
import os
import sys
import time

from _common import RESULTS
from kitting.bins import BinType, assign_cheapest
from kitting.config import TRAY_H as H, TRAY_W as W
from kitting.data import generate_portfolio
from kitting.evaluate import check_feasible, evaluate
from kitting.layout import Placement, improve_lns, layout_rule, make_bins, penalty_of

QUICK = "--quick" in sys.argv
PASSES = 1 if QUICK else 2
DET = 1.0 if QUICK else 3.0
CH4_CHOSEN = [BinType(1, 1), BinType(2, 2), BinType(4, 3), BinType(8, 1)]   # 第4章で選んだ4種類

# ---- コード6-1 ここから ---------------------------------------------------
WEIGHTS = {
    "標準（第5章）":   dict(split_w=100, spread_w=6, inv_w=20),
    "まとまり重視":     dict(split_w=100, spread_w=20, inv_w=5),
    "読み順重視":       dict(split_w=100, spread_w=2, inv_w=60),
}


def run_weights(bins, init, n_trays):
    rows, layouts = [], {}
    for name, w in WEIGHTS.items():
        t0 = time.perf_counter()
        pl, obj, _ = improve_lns(bins, init, n_trays, passes=PASSES, det_time=DET, log=None, **w)
        check_feasible(bins, pl)
        rows.append(dict(weights=name, **w, **evaluate(bins, pl), penalty=obj,
                         seconds=round(time.perf_counter() - t0, 1)))
        layouts[name] = pl
        print(rows[-1], flush=True)
    return rows, layouts
# ---- コード6-1 ここまで ---------------------------------------------------


def layout_step_balanced(bins, n_trays):
    """作業順ルール（第5章）を、トレイ n_trays 枚にほぼ均等に配るように変えたもの。
    次の工程を足すと1枚あたりの目安面積を超えるなら、次のトレイへ進む。"""
    target = math.ceil(sum(b.type.area for b in bins) / n_trays)
    occ = [[[False] * W for _ in range(H)] for _ in range(n_trays)]
    used = [0] * n_trays
    res, t = {}, 0
    steps = sorted({b.step for b in bins})

    def fits(t, x, y, w, h):
        return x + w <= W and y + h <= H and all(
            not occ[t][yy][xx] for yy in range(y, y + h) for xx in range(x, x + w))

    def try_place(b, t):
        for x in range(W):                       # 左の列から
            for y in range(H):                   # 上の行から
                for (w, h) in b.shapes:
                    if fits(t, x, y, w, h):
                        for yy in range(y, y + h):
                            for xx in range(x, x + w):
                                occ[t][yy][xx] = True
                        res[b.id] = Placement(t, x, y, w, h)
                        used[t] += w * h
                        return True
        return False

    for s in steps:
        group = sorted([b for b in bins if b.step == s], key=lambda b: (-b.type.area, b.id))
        area = sum(b.type.area for b in group)
        if t < n_trays - 1 and used[t] > 0 and used[t] + area > target:
            t += 1
        for b in group:
            while not try_place(b, t):
                t += 1
                if t >= n_trays:
                    raise RuntimeError("トレイが足りません")
    return res


# ---- コード6-2 ここから ---------------------------------------------------
def run_epsilon(bins, eps_list=(4, 5, 6), **w):
    """ε制約法：トレイ枚数を「ε枚まで」に制限し、その中で罰則を最小にする。
    εを変えて解き、枚数と使いやすさの組を並べる。"""
    rows, layouts = [], {}
    for eps in eps_list:
        t0 = time.perf_counter()
        init = layout_step_balanced(bins, eps)
        pl, obj, _ = improve_lns(bins, init, eps, passes=PASSES, det_time=DET, log=None, exact=False, **w)
        check_feasible(bins, pl)
        rows.append(dict(eps=eps, **evaluate(bins, pl), penalty=obj, seconds=round(time.perf_counter() - t0, 1)))
        layouts[eps] = pl
        print(rows[-1], flush=True)
    return rows, layouts
# ---- コード6-2 ここまで ---------------------------------------------------


def run_tail(boms, name="SA-02"):
    parts = boms[name]
    bins = make_bins(parts, assign_cheapest(parts, CH4_CHOSEN))
    init = layout_rule(bins, "step")
    n = max(p.tray for p in init.values()) + 1
    rows = []
    for label, w in (("第5章の罰則", dict()), ("罰則(d)を追加（重み20）", dict(tail_w=20)),
                     ("罰則(d)を追加（重み60）", dict(tail_w=60))):
        t0 = time.perf_counter()
        pl, obj, _ = improve_lns(bins, init, n, passes=PASSES, det_time=DET, log=None, **w)
        check_feasible(bins, pl)
        rows.append(dict(bom=name, penalty_set=label, **evaluate(bins, pl), penalty=obj,
                         seconds=round(time.perf_counter() - t0, 1)))
        print(rows[-1], flush=True)
    return rows


def run_weights_sa02(boms, name="SA-02"):
    """実験1b（6.2節）：トレイに余裕のあるSA-02で、コード6-1と同じ3通りの重みを試す"""
    parts = boms[name]
    bins = make_bins(parts, assign_cheapest(parts, CH4_CHOSEN))
    init = layout_rule(bins, "step")
    n = max(p.tray for p in init.values()) + 1
    rows, lay = run_weights(bins, init, n)
    for r in rows:
        r["bom"] = name
    return rows, lay, bins


def merge_layouts(extra):
    path = os.path.join(RESULTS, "ch6_layouts.json")
    out = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            out = json.load(f)
    out.update(extra)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)


def main_sa02(boms):
    print("== 実験1b：SA-02で重み", flush=True)
    rows, lay, bins = run_weights_sa02(boms)
    save_csv(rows, "ch6_weights_sa02.csv")
    return {"weights_sa02": {k: {str(i): vars(p) for i, p in v.items()} for k, v in lay.items()},
            "bins_sa02": [b.to_dict() for b in bins]}


def save_csv(rows, name):
    path = os.path.join(RESULTS, name)
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    print("saved", path, flush=True)


def main():
    boms = generate_portfolio()
    parts = boms["SA-10"]
    bins = make_bins(parts, assign_cheapest(parts, CH4_CHOSEN))
    init = layout_rule(bins, "step")
    n = max(p.tray for p in init.values()) + 1
    print("SA-10: bins", len(bins), "trays", n, "init penalty", penalty_of(bins, init, n), flush=True)

    out = {}
    print("== 実験3：SA-02の罰則(d)", flush=True)
    save_csv(run_tail(boms), "ch6_tail.csv")
    print("== 実験1：重み", flush=True)
    rows, lay = run_weights(bins, init, n)
    save_csv(rows, "ch6_weights.csv")
    out["weights"] = {k: {str(i): vars(p) for i, p in v.items()} for k, v in lay.items()}
    print("== 実験2：ε制約法", flush=True)
    rows, lay = run_epsilon(bins)
    save_csv(rows, "ch6_epsilon.csv")
    out["epsilon"] = {str(k): {str(i): vars(p) for i, p in v.items()} for k, v in lay.items()}
    out["bins"] = [b.to_dict() for b in bins]
    out.update(main_sa02(boms))
    merge_layouts(out)
    print("done", flush=True)


if __name__ == "__main__":
    if "--sa02-weights" in sys.argv:          # 実験1bだけをやり直す（約1分）
        merge_layouts(main_sa02(generate_portfolio()))
    else:
        main()
