"""第4章：ビンの寸法を決める（品揃え問題）を混合整数計画（MILP）で解く。

決めること
    y[k]    : 寸法候補 k を標準ビンとして採用するか（0/1）
    x[p,k]  : 部品 p を寸法 k のビンに入れるか（0/1）
守ること
    各部品はちょうど1種類の寸法に入れる               sum_k x[p,k] = 1
    採用した寸法にしか入れられない                     x[p,k] <= y[k]
    採用する種類は K 種類まで                          sum_k y[k] <= K
良し悪しの基準（2通り）
    "total": すべてのBOMで必要なビン面積の合計を最小にする
    "worst": BOMをまたいで共通のトレイを作る。寸法ごとに「どのBOMでも足りる個数」z[k] を用意し、
             その面積 sum_k area[k] * z[k] を最小にする（論文の Worst Case Scenario を最適化したもの）

部品がその寸法に何個入り、ビンが何個要るかは bins.bins_needed で事前に計算しておく。
こうすると制約も目的もすべて一次式になり、Excelのソルバー（シンプレックスLP）でも同じ問題が解ける。
"""
from __future__ import annotations

import time
from dataclasses import dataclass

import pulp

from .bins import BinType, bins_needed
from .data import Part


@dataclass
class SizingResult:
    objective: str
    K: int
    chosen: list[BinType]
    assign: dict[tuple[str, str], tuple[BinType, int]]   # (BOM名, 部品番号) -> (ビン, 個数)
    value: float           # 目的関数値 [ブロック]
    status: str
    seconds: float

    def area_by_bom(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for (bom, _), (t, n) in self.assign.items():
            out[bom] = out.get(bom, 0) + t.area * n
        return out

    def worst_counts(self) -> dict[BinType, int]:
        """寸法ごとに、BOMの中で最も多く必要になる個数（共通トレイに必要な個数）"""
        per: dict[tuple[str, BinType], int] = {}
        for (bom, _), (t, n) in self.assign.items():
            per[(bom, t)] = per.get((bom, t), 0) + n
        out: dict[BinType, int] = {}
        for (bom, t), n in per.items():
            out[t] = max(out.get(t, 0), n)
        return out


def solve_sizing(boms: dict[str, list[Part]], candidates: list[BinType], K: int,
                 objective: str = "total", time_limit: int = 120) -> SizingResult:
    # ---- コード4-1 ここから -------------------------------------------------
    prob = pulp.LpProblem("bin_sizing", pulp.LpMinimize)

    # 前計算：部品ごとに、入る寸法 k と、そのとき必要なビンの数 n[p][k]
    #   部品のキー p は (BOM名, 部品番号)。入らない寸法は最初から候補に入れない。
    need: dict[tuple[str, str], dict[BinType, int]] = {}
    for bom, parts in boms.items():
        for part in parts:
            need[(bom, part.part_no)] = {
                k: n for k in candidates if (n := bins_needed(part, k)) is not None}

    # 決めること
    y = {k: pulp.LpVariable(f"y_{k.name}", cat="Binary") for k in candidates}
    x = {(p, k): pulp.LpVariable(f"x_{p[0]}_{p[1]}_{k.name}", cat="Binary")
         for p, opts in need.items() for k in opts}

    # 守ること
    for p, opts in need.items():
        prob += pulp.lpSum(x[p, k] for k in opts) == 1      # どれか1種類に入れる
        for k in opts:
            prob += x[p, k] <= y[k]                          # 採用した寸法だけ
    prob += pulp.lpSum(y.values()) <= K                      # K種類まで
    # ---- コード4-1 ここまで -------------------------------------------------
    if bad := [p for p, opts in need.items() if not opts]:
        raise ValueError(f"どの寸法候補にも入らない部品があります: {bad}")

    if objective == "total":
        # 良し悪しの基準：必要なトレイ面積の合計
        prob += pulp.lpSum(k.area * n * x[p, k]
                           for p, opts in need.items() for k, n in opts.items())
    elif objective == "worst":
        # ---- コード4-3 ここから ---------------------------------------------
        z = {k: pulp.LpVariable(f"z_{k.name}", lowBound=0, cat="Integer")
             for k in candidates}
        for bom in boms:
            for k in candidates:
                terms = [opts[k] * x[p, k] for p, opts in need.items()
                         if p[0] == bom and k in opts]
                if terms:
                    prob += z[k] >= pulp.lpSum(terms)        # どのBOMでも足りる個数
        prob += pulp.lpSum(k.area * z[k] for k in candidates)  # 共通トレイの面積
        # ---- コード4-3 ここまで ---------------------------------------------
    else:
        raise ValueError(objective)

    solver = pulp.PULP_CBC_CMD(msg=False, timeLimit=time_limit, threads=1)   # PuLP同梱のCBC
    t0 = time.perf_counter()
    prob.solve(solver)
    sec = time.perf_counter() - t0

    chosen = sorted(k for k in candidates if y[k].value() > 0.5)
    assign = {}
    for p, opts in need.items():
        for k, n in opts.items():
            if x[p, k].value() > 0.5:
                assign[p] = (k, n)
    return SizingResult(objective, K, chosen, assign, pulp.value(prob.objective),
                        pulp.LpStatus[prob.status], sec)


def evaluate_fixed_set(boms: dict[str, list[Part]], types: list[BinType]) -> dict:
    """寸法を固定したとき（例：論文の4種類）の面積を、第3章の割当ルールで計算する。
    total: 全BOMの合計面積、worst: 共通トレイの面積（寸法ごとの最大個数＋大物の最大面積）"""
    from .bins import assign_smallest, area_of, bulk_area
    total, worst_n, worst_bulk, n_bulk = 0, {}, 0, 0
    for bom, parts in boms.items():
        a, bulk = assign_smallest(parts, types)
        total += area_of(a, bulk)
        n_bulk += len(bulk)
        cnt: dict[BinType, int] = {}
        for t, n in a.values():
            cnt[t] = cnt.get(t, 0) + n
        for t, n in cnt.items():
            worst_n[t] = max(worst_n.get(t, 0), n)
        worst_bulk = max(worst_bulk, sum(bulk_area(p) for p in bulk))
    worst = sum(t.area * n for t, n in worst_n.items()) + worst_bulk
    return dict(total=total, worst=worst, bulk_parts=n_bulk)
