"""第3章：2008年のExcelと同じ割当ルール（入る最小のビンを選ぶ）を、論文の標準ビン4種で再現する。

    python scripts/ch3_rule.py
"""
import csv
import os

from _common import RESULTS
from kitting.bins import BinType, assign_smallest, area_of
from kitting.config import THESIS_BINS
from kitting.data import generate_portfolio


def main():
    boms = generate_portfolio()
    types = [BinType(*t) for t in THESIS_BINS]
    rows = []
    for name, parts in boms.items():
        a, bulk = assign_smallest(parts, types)
        rows.append(dict(bom=name, steps_with_parts=len({p.step for p in parts}), parts=len(parts),
                         bins=sum(n for _, n in a.values()), bulk_parts=len(bulk),
                         area_blocks=area_of(a, bulk)))
    path = os.path.join(RESULTS, "ch3_rule.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print(r)
    print("saved", path)


if __name__ == "__main__":
    main()
