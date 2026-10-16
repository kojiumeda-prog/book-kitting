"""第5章：最も複雑な事前組立品（SA-10、39工程）のビンをトレイに並べ、4つの方法を比べる。

    python scripts/ch5_layout.py            # 本の数値を再現（数分）
    python scripts/ch5_layout.py --quick    # 短い計算時間で動作確認（1分程度）

  ① サイズ順ルール      : 小さいビンから上・左に詰める（2008年のサイズ順の配置、図5-1(b)）
  ② 枚数のみ最適化      : CP-SATでトレイ枚数を最小化
  ③ 作業順ルール        : 工程順に左の列から詰める（2008年の作業順の配置、図5-1(a)を単純なルールで）
  ④ 作業順の最適化（LNS）: ③を初期解に、工程を数個ずつ解き直して罰則を最小化
"""
import argparse
import csv
import json
import os
import time

from _common import FIGURES, RESULTS
from kitting.bins import BinType, assign_cheapest
from kitting.config import CANDIDATE_BINS
from kitting.data import COMPLEX_BOM, generate_portfolio
from kitting.evaluate import check_feasible, evaluate
from kitting.layout import (improve_lns, layout_rule, make_bins, penalty_of,
                            solve_min_trays)
from kitting.plot import draw_layout
from kitting.sizing import solve_sizing


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="計算時間を短くして動作確認する")
    args = ap.parse_args()
    passes, det = (1, 1.0) if args.quick else (3, 3.0)

    boms = generate_portfolio()
    sizing = solve_sizing(boms, [BinType(*t) for t in CANDIDATE_BINS], K=4, objective="worst")
    assign = assign_cheapest(boms[COMPLEX_BOM], sizing.chosen)   # 選んだ4種類で、面積が最小のビンに入れる
    bins = make_bins(boms[COMPLEX_BOM], assign)
    area = sum(b.type.area for b in bins)
    print(f"{COMPLEX_BOM}: 部品{len(boms[COMPLEX_BOM])}点, ビン{len(bins)}個, 面積{area}ブロック, "
          f"ビン寸法 {[t.name for t in sizing.chosen]}")

    layouts, info = {}, {}

    t0 = time.perf_counter()
    layouts["size_rule"] = layout_rule(bins, "size")
    info["size_rule"] = dict(seconds=round(time.perf_counter() - t0, 2))

    res, si = solve_min_trays(bins, max_trays=6, det_time=30.0)
    layouts["min_trays"] = res
    info["min_trays"] = dict(seconds=round(si.seconds, 1), status=si.status, trays=si.objective, bound=si.bound)
    n_trays = int(si.objective)

    t0 = time.perf_counter()
    layouts["step_rule"] = layout_rule(bins, "step")
    info["step_rule"] = dict(seconds=round(time.perf_counter() - t0, 2))
    n_step = max(p.tray for p in layouts["step_rule"].values()) + 1

    t0 = time.perf_counter()
    res, obj, hist = improve_lns(bins, layouts["step_rule"], n_step, passes=passes, det_time=det)
    layouts["lns"] = res
    info["lns"] = dict(seconds=round(time.perf_counter() - t0, 1), penalty=obj, history=hist)

    names = {"size_rule": "① サイズ順ルール", "min_trays": "② 枚数のみ最適化",
             "step_rule": "③ 作業順ルール", "lns": "④ 作業順の最適化（LNS）"}
    rows = []
    for k, pl in layouts.items():
        check_feasible(bins, pl)
        m = evaluate(bins, pl)
        m["penalty"] = penalty_of(bins, pl, m["trays"]) if k != "size_rule" and k != "min_trays" else None
        rows.append(dict(method=names[k], **m, seconds=info[k]["seconds"]))
        print(rows[-1])
        fig = {"size_rule": "fig5-3", "min_trays": "fig5-7", "step_rule": "fig5-8", "lns": "fig5-9"}[k]
        draw_layout(bins, pl, f"{names[k]}（{COMPLEX_BOM}）", os.path.join(FIGURES, f"{fig}_{k}.png"))

    with open(os.path.join(RESULTS, "ch5_metrics.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    with open(os.path.join(RESULTS, "ch5_layouts.json"), "w", encoding="utf-8") as f:
        json.dump(dict(bom=COMPLEX_BOM, quick=args.quick,
                       bins=[b.to_dict() for b in bins],
                       layouts={k: {str(i): vars(p) for i, p in pl.items()} for k, pl in layouts.items()},
                       info=info), f, ensure_ascii=False, indent=1)
    print("saved results/ch5_metrics.csv, results/ch5_layouts.json, figures/fig5-*.png")


if __name__ == "__main__":
    main()
