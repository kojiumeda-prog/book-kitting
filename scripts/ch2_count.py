"""第2章 コード2-1：配置の組合せを数える小さな実験。

小さなトレイにビンを重ならないように置く方法が何通りあるかを、全通り数える（後戻り法）。
ビンが増えると、通り数が爆発的に増えることを確かめる。

    python scripts/ch2_count.py          # ビン5個まで（数秒）
    python scripts/ch2_count.py --six    # ビン6個まで（1分以上かかる）
"""
import sys
import csv
import math
import os
import time

from _common import RESULTS


# ---- コード2-1 ここから ---------------------------------------------------
def count_layouts(W, H, bins):
    """横W×縦Hマスのトレイに、bins（(w, h) のリスト）を重ならずに置く方法の数。
    ビンは1個ずつ区別する（同じ大きさでも別のビン）。90度回転も許す。"""
    used = [[False] * W for _ in range(H)]

    def fits(x, y, w, h):
        if x + w > W or y + h > H:
            return False
        return all(not used[yy][xx] for yy in range(y, y + h) for xx in range(x, x + w))

    def mark(x, y, w, h, v):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                used[yy][xx] = v

    def place(i):
        if i == len(bins):                 # 全部置けたら1通り
            return 1
        w0, h0 = bins[i]
        shapes = {(w0, h0), (h0, w0)}      # 向き（正方形なら1通り）
        total = 0
        for (w, h) in shapes:
            for y in range(H):
                for x in range(W):
                    if fits(x, y, w, h):
                        mark(x, y, w, h, True)
                        total += place(i + 1)   # 次のビンへ
                        mark(x, y, w, h, False) # 元に戻して別の場所を試す
        return total

    return place(0)
# ---- コード2-1 ここまで ---------------------------------------------------


def main():
    W, H = 6, 4                                    # 小さなトレイ（24マス）
    pattern = [(1, 1), (2, 1), (1, 1), (2, 2), (1, 1), (2, 1)]
    n_max = 6 if "--six" in sys.argv else 5
    rows = []
    for n in range(1, n_max + 1):
        t0 = time.perf_counter()
        c = count_layouts(W, H, pattern[:n])
        rows.append(dict(tray=f"{W}x{H}", bins=n, shapes=" ".join(f"{w}x{h}" for w, h in pattern[:n]),
                         layouts=c, seconds=round(time.perf_counter() - t0, 3)))
        print(rows[-1])
    # 本物の大きさ（16×8マス）で、1×1のビンだけをn個置く方法の数 = 128×127×…（順列）
    for n in (5, 10, 20, 40, 80, 126):
        c = math.perm(128, n)
        rows.append(dict(tray="16x8", bins=n, shapes="1x1のみ", layouts=f"{c:.2e}", seconds=""))
        print(n, f"{c:.2e}", f"1秒に1億通り調べると {c / 1e8 / 3.15e7:.1e} 年")
    path = os.path.join(RESULTS, "ch2_count.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print("saved", path)


if __name__ == "__main__":
    main()
