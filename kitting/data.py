"""合成データ：架空の組立品「装置X」の事前組立品と、その部品表（BOM）。

実在の部品・BOM・企業とは無関係。乱数の種を固定すれば、いつでも同じデータが得られる。
"""
from __future__ import annotations

import random
import string
from dataclasses import dataclass, asdict

from .config import DEFAULT_SEED


@dataclass(frozen=True)
class Part:
    bom: str            # 事前組立品名（例: SA-10）
    part_no: str        # 部品番号（架空）
    name: str           # 部品名（架空）
    step: int           # 使用する作業工程（0始まり）
    step_label: str     # 工程記号（A, B, ..., Z, AA, ...）
    w_mm: int           # 外接矩形の短辺 [mm]
    l_mm: int           # 外接矩形の長辺 [mm]
    qty: int            # 1台あたりの使用数
    hardware: bool      # ねじ・ワッシャ等の小物（1つの部品箱にまとめて入れる）

    def to_dict(self):
        return asdict(self)


def step_label(i: int) -> str:
    letters = string.ascii_uppercase
    return letters[i] if i < 26 else letters[i // 26 - 1] + letters[i % 26]


# 部品の種類ごとの寸法・数量の範囲と出現比率
CATEGORIES = {
    #  名前候補,                                              短辺,        長辺,        数量,    比率
    "hardware": (["ボルト", "ナット", "ワッシャ", "ねじ", "スペーサ"], (8, 30), (10, 40), (4, 24), 38),
    "small":    (["ブラケット", "継手", "センサ", "クランプ", "端子台"], (20, 60), (30, 90), (1, 4), 32),
    "medium":   (["カバー", "プレート", "バルブ", "ユニット", "ケーブル束"], (50, 120), (70, 160), (1, 2), 20),
    "large":    (["フレーム", "ベースプレート", "ハウジング"], (120, 200), (150, 280), (1, 1), 5),
    "long":     (["シャフト", "レール", "配管", "ガイド"], (30, 60), (300, 580), (1, 1), 5),
}


def generate_bom(name: str, n_steps: int, parts_per_step: float, rng: random.Random,
                 empty_step_rate: float = 0.15) -> list[Part]:
    """工程数 n_steps のBOMを1つ作る。部品を使わない工程（締付・検査など）も一定割合で混ぜる。"""
    cats = list(CATEGORIES)
    weights = [CATEGORIES[c][4] for c in cats]
    parts: list[Part] = []
    for s in range(n_steps):
        if rng.random() < empty_step_rate:
            continue
        n = max(1, round(rng.gauss(parts_per_step, 1.2)))
        for _ in range(n):
            c = rng.choices(cats, weights=weights)[0]
            names, wr, lr, qr, _ = CATEGORIES[c]
            w = rng.randint(*wr)
            l = max(w, rng.randint(*lr))
            parts.append(Part(
                bom=name,
                part_no=f"P-{rng.randint(10000, 99999)}",
                name=rng.choice(names),
                step=s, step_label=step_label(s),
                w_mm=w, l_mm=l, qty=rng.randint(*qr),
                hardware=(c == "hardware"),
            ))
    return parts


# 事前組立品の構成（名前, 工程数, 1工程あたりの平均部品数）
PORTFOLIO = [
    ("SA-01", 12, 2.0), ("SA-02", 15, 2.2), ("SA-03", 18, 2.4), ("SA-04", 20, 2.5),
    ("SA-05", 22, 2.6), ("SA-06", 25, 2.8), ("SA-07", 28, 2.8), ("SA-08", 30, 3.0),
    ("SA-09", 34, 3.0), ("SA-10", 39, 3.3),
]
COMPLEX_BOM = "SA-10"   # 第5章で使う最も複雑な事前組立品（39工程）


def generate_portfolio(seed: int = DEFAULT_SEED) -> dict[str, list[Part]]:
    """10種類の事前組立品のBOMを作る。SA-10 は39工程・部品100点以上になるように引き直す。"""
    rng = random.Random(seed)
    boms = {}
    for name, n_steps, pps in PORTFOLIO:
        while True:
            parts = generate_bom(name, n_steps, pps, rng)
            if name != COMPLEX_BOM or len(parts) >= 100:
                break
        boms[name] = parts
    return boms
