"""第5章 5.8節：問題の大きさ（工程数・ビン数）と計算時間の関係を調べる。

    python scripts/scale_test.py
"""
import csv
import os
import time

from _common import RESULTS
from kitting.bins import BinType, assign_cheapest
from kitting.config import CANDIDATE_BINS
from kitting.data import generate_portfolio
from kitting.evaluate import evaluate
from kitting.layout import improve_lns, layout_rule, make_bins, penalty_of


def main():
    boms = generate_portfolio()
    sizing = solve_sizing_k4(boms)
    rows = []
    for name, parts in boms.items():
        assign = assign_cheapest(parts, sizing.chosen)
        bins = make_bins(parts, assign)
        init = layout_rule(bins, "step")
        nt = max(p.tray for p in init.values()) + 1
        p0 = penalty_of(bins, init, nt)
        t0 = time.perf_counter()
        res, obj, _ = improve_lns(bins, init, nt, passes=2, det_time=2.0, log=None)
        sec = time.perf_counter() - t0
        m = evaluate(bins, res)
        rows.append(dict(bom=name, steps=len({p.step for p in parts}), parts=len(parts), bins=len(bins),
                         trays=nt, penalty_rule=p0, penalty_lns=obj,
                         improvement_pct=round(100 * (p0 - obj) / p0, 1), seconds=round(sec, 1),
                         order_match=m["order_match"], avg_spread=m["avg_spread"]))
        print(rows[-1])
    with open(os.path.join(RESULTS, "scale_test.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print("saved results/scale_test.csv")


def solve_sizing_k4(boms):
    from kitting.sizing import solve_sizing
    return solve_sizing(boms, [BinType(*t) for t in CANDIDATE_BINS], K=4, objective="worst")


if __name__ == "__main__":
    main()
