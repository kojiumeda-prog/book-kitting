"""第4章：部品箱寸法の品揃え問題をMILPで解き、種類数Kと必要面積の関係を調べる。

    python scripts/ch4_sizing.py
"""
import csv
import json
import os

from _common import FIGURES, RESULTS
from kitting.bins import BinType
from kitting.config import CANDIDATE_BINS, THESIS_BINS
from kitting.data import generate_portfolio
from kitting.plot import draw_k_curve
from kitting.sizing import evaluate_fixed_set, solve_sizing


def main():
    boms = generate_portfolio()
    cand = [BinType(*t) for t in CANDIDATE_BINS]
    rows = []
    for obj in ("total", "worst"):
        for K in (2, 3, 4, 5, 6, 8):
            r = solve_sizing(boms, cand, K, obj)
            rows.append(dict(objective=obj, K=K, status=r.status, area_blocks=round(r.value),
                             chosen=" ".join(t.name for t in r.chosen), seconds=round(r.seconds, 2)))
            print(rows[-1])
            if obj == "worst" and K == 4:
                chosen = dict(K=4, objective="worst",
                              chosen=[[t.w, t.h] for t in r.chosen],
                              assign={f"{b}/{p}": [t.w, t.h, n] for (b, p), (t, n) in r.assign.items()},
                              worst_counts={t.name: n for t, n in r.worst_counts().items()})
                with open(os.path.join(RESULTS, "ch4_chosen_K4.json"), "w", encoding="utf-8") as f:
                    json.dump(chosen, f, ensure_ascii=False, indent=1)
    thesis = evaluate_fixed_set(boms, [BinType(*t) for t in THESIS_BINS])
    print("論文の4種類＋第3章ルール:", thesis)
    with open(os.path.join(RESULTS, "ch4_sizing.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
        w.writerow(dict(objective="thesis_rule_total", K=4, status="-", area_blocks=thesis["total"],
                        chosen=" ".join(BinType(*t).name for t in THESIS_BINS), seconds=0))
        w.writerow(dict(objective="thesis_rule_worst", K=4, status="-", area_blocks=thesis["worst"],
                        chosen=" ".join(BinType(*t).name for t in THESIS_BINS), seconds=0))
    draw_k_curve(rows, os.path.join(FIGURES, "fig4-6_k_vs_area.png"), thesis)
    print("saved results/ch4_sizing.csv, results/ch4_chosen_K4.json, figures/fig4-6_k_vs_area.png")


if __name__ == "__main__":
    main()
