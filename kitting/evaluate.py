"""第5章：配置の評価指標と、重なり・はみ出しの独立検証。"""
from __future__ import annotations

from .config import TRAY_W as W, TRAY_H as H
from .layout import Bin, Placement


def check_feasible(bins: list[Bin], pl: dict[int, Placement]) -> bool:
    """モデルとは別のコードで、はみ出し・重なり・向きを確かめる"""
    seen = {}
    for b in bins:
        p = pl[b.id]
        assert (p.w, p.h) in b.shapes, f"向きが不正: {b}"
        assert 0 <= p.x and p.x + p.w <= W and 0 <= p.y and p.y + p.h <= H, f"はみ出し: {b}"
        for xx in range(p.x, p.x + p.w):
            for yy in range(p.y, p.y + p.h):
                k = (p.tray, xx, yy)
                assert k not in seen, f"重なり: {b.id} と {seen[k]}"
                seen[k] = b.id
    return True


def evaluate(bins: list[Bin], pl: dict[int, Placement]) -> dict:
    """5つの指標
    trays         : 使ったトレイ枚数
    split_steps   : 部品が2枚以上のトレイにまたがる工程の数
    avg_spread    : 工程ごとの部品箱を囲む長方形の縦＋横 [ブロック] の平均（トレイごとに合計）
    order_match   : 工程の違う部品箱の組のうち、トレイ→列→行の読み順が工程順と一致する割合
    tray_switches : 工程順に作業したときに別のトレイへ移る（歩く、または体を向け直す）回数
    """
    steps = sorted({b.step for b in bins})
    by_step = {s: [b for b in bins if b.step == s] for s in steps}
    trays = len({p.tray for p in pl.values()})
    split = sum(1 for s in steps if len({pl[b.id].tray for b in by_step[s]}) > 1)

    spreads = []
    for s in steps:
        tot = 0
        for t in {pl[b.id].tray for b in by_step[s]}:
            ps = [pl[b.id] for b in by_step[s] if pl[b.id].tray == t]
            tot += (max(p.x + p.w for p in ps) - min(p.x for p in ps)) + \
                   (max(p.y + p.h for p in ps) - min(p.y for p in ps))
        spreads.append(tot)

    key = {b.id: (pl[b.id].tray, pl[b.id].x, pl[b.id].y) for b in bins}
    ok = tot = 0
    for i, a in enumerate(bins):
        for b in bins[i + 1:]:
            if a.step == b.step:
                continue
            f, s2 = (a, b) if a.step < b.step else (b, a)
            tot += 1
            ok += key[f.id] < key[s2.id]

    switches, prev_last = 0, None
    for s in steps:
        trs = sorted({pl[b.id].tray for b in by_step[s]})
        if prev_last is not None and trs[0] != prev_last:
            switches += 1
        switches += len(trs) - 1
        prev_last = trs[-1]

    return dict(trays=trays, split_steps=split, n_steps=len(steps),
                avg_spread=round(sum(spreads) / len(spreads), 2),
                order_match=round(ok / tot, 3), tray_switches=switches)
