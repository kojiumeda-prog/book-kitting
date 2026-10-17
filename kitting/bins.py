"""部品箱の寸法と、部品を部品箱に入れるときの計算（第3章・第4章）。"""
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
    """1つの部品箱に入る部品の数。入らなければ0。
    小物（hardware）は寸法が入れば数量に関係なく1つの部品箱にまとめる（論文と同じ扱い）。
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
    """その部品に必要な部品箱の数。入らなければ None。"""
    cap = capacity(part, bt)
    return None if cap == 0 else math.ceil(part.qty / cap)


def bulk_area(part: Part) -> int:
    """どの部品箱にも入らない大物部品を、トレイに直置きするときの面積 [ブロック]。
    論文の「unlimited size」と同じく、外接矩形をブロック単位に切り上げて数量分を足す。"""
    return math.ceil(part.w_mm / BLOCK_MM) * math.ceil(part.l_mm / BLOCK_MM) * part.qty


def assign_smallest(parts: list[Part], types: list[BinType]):
    """第3章：2008年のExcelと同じ割当ルール。
    部品が入る最も小さい（面積の小さい）部品箱を選び、必要個数を数える。
    どの部品箱にも入らない部品は「大物」として別に返す。

    戻り値: (割当 {部品番号: (部品箱, 個数)}, 大物部品のリスト)"""
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
    """必要なトレイ面積 [ブロック]＝部品箱の面積の合計＋大物の直置き面積"""
    return sum(t.area * n for t, n in assign.values()) + sum(bulk_area(p) for p in bulk)


def assign_cheapest(parts: list[Part], types: list[BinType]) -> dict[str, tuple[BinType, int]]:
    """寸法が決まった後の割当：部品ごとに、必要な面積（部品箱1個の面積×個数）が最小になる部品箱を選ぶ。
    同じ面積なら部品箱の個数が少ないほう、さらに同じなら小さい部品箱を選ぶ（結果が一通りに決まる）。
    第5章では、第4章で選んだ寸法をこの方法で各部品に割り当てる。"""
    out = {}
    for p in parts:
        opts = [(t.area * n, n, t.area, t.w, t) for t in types if (n := bins_needed(p, t)) is not None]
        if not opts:
            raise ValueError(f"{p.part_no} は選んだ寸法のどれにも入りません")
        best = min(opts, key=lambda o: o[:4])
        out[p.part_no] = (best[4], best[1])
    return out
