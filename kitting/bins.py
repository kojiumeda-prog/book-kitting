"""ビンの寸法と、部品をビンに入れるときの計算（第3章・第4章）。"""
from __future__ import annotations

import math
from dataclasses import dataclass

from .config import BLOCK_MM, WALL_MM
from .data import Part

UNLIMITED = 10 ** 9


@dataclass(frozen=True, order=True)
class BinType:
    w: int   # 横 [ブロック]
    h: int   # 縦 [ブロック]

    @property
    def area(self) -> int:              # 占有面積 [ブロック]
        return self.w * self.h

    @property
    def outer_mm(self) -> tuple[int, int]:
        return self.w * BLOCK_MM, self.h * BLOCK_MM

    @property
    def inner_mm(self) -> tuple[int, int]:
        return self.w * BLOCK_MM - WALL_MM, self.h * BLOCK_MM - WALL_MM

    @property
    def name(self) -> str:
        ow, oh = self.outer_mm
        return f"{ow}x{oh}"


def capacity(part: Part, bt: BinType) -> int:
    """1つのビンに入る部品の数。入らなければ0。
    小物（hardware）は寸法が入れば数量に関係なく1つのビンにまとめる（論文と同じ扱い）。
    それ以外は、部品の外接矩形を2通りの向きで並べ、多く入るほうを採る。"""
    iw, ih = bt.inner_mm
    best = 0
    for pw, pl in ((part.w_mm, part.l_mm), (part.l_mm, part.w_mm)):
        if pw <= iw and pl <= ih:
            best = max(best, (iw // pw) * (ih // pl))
    if best and part.hardware:
        return UNLIMITED
    return best


def bins_needed(part: Part, bt: BinType) -> int | None:
    """その部品に必要なビンの数。入らなければ None。"""
    cap = capacity(part, bt)
    return None if cap == 0 else math.ceil(part.qty / cap)


def bulk_area(part: Part) -> int:
    """どのビンにも入らない大物部品を、トレイに直置きするときの面積 [ブロック]。
    論文の「unlimited size」と同じく、外接矩形をブロック単位に切り上げて数量分を足す。"""
    return math.ceil(part.w_mm / BLOCK_MM) * math.ceil(part.l_mm / BLOCK_MM) * part.qty


def assign_smallest(parts: list[Part], types: list[BinType]):
    """第3章：2008年のExcelと同じ割当ルール。
    部品が入る最も小さい（面積の小さい）ビンを選び、必要個数を数える。
    どのビンにも入らない部品は「大物」として別に返す。

    戻り値: (割当 {部品番号: (ビン, 個数)}, 大物部品のリスト)"""
    order = sorted(types, key=lambda t: (t.area, t.w))
    out, bulk = {}, []
    for p in parts:
        for t in order:
            n = bins_needed(p, t)
            if n is not None:
                out[p.part_no] = (t, n)
                break
        else:
            bulk.append(p)
    return out, bulk


def area_of(assign: dict, bulk: list[Part] = ()) -> int:
    """必要なトレイ面積 [ブロック]＝ビンの面積の合計＋大物の直置き面積"""
    return sum(t.area * n for t, n in assign.values()) + sum(bulk_area(p) for p in bulk)
