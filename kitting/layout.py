"""第5章：ビンをトレイに並べる。

  layout_rule      : 小さいビンから上の行・左の列に詰める貪欲法（2008年のサイズ順の配置、本書 図3-5(b)）
  TrayModel        : CP-SAT による配置モデル
      sequence=False -> トレイ枚数の最小化
      sequence=True  -> 枚数を固定し、作業順・まとまりの罰則を最小化

複数のトレイを横に並べた1枚の長い板とみなし、全体のx座標を
    X = トレイ番号 * TRAY_W + トレイ内の列
と置くと、トレイをまたいだ重なりも AddNoOverlap2D 1本で禁止できる。
"""
from __future__ import annotations

from dataclasses import dataclass, asdict

from ortools.sat.python import cp_model

from .bins import BinType
from .config import TRAY_W as W, TRAY_H as H
from .data import Part, step_label


@dataclass(frozen=True)
class Bin:
    id: int
    step: int
    step_label: str
    type: BinType
    part_no: str
    part_name: str

    @property
    def shapes(self) -> list[tuple[int, int]]:
        """置ける向き（横, 縦）。正方形でなければ90度回転も可"""
        w, h = self.type.w, self.type.h
        return [(w, h)] if w == h else [(w, h), (h, w)]

    def to_dict(self):
        d = asdict(self)
        d["type"] = [self.type.w, self.type.h]
        return d


@dataclass
class Placement:
    tray: int
    x: int
    y: int
    w: int
    h: int


def make_bins(parts: list[Part], assign: dict[str, tuple[BinType, int]]) -> list[Bin]:
    """部品の割当結果から、トレイに置くビンの一覧を作る（工程順）"""
    bins: list[Bin] = []
    for p in sorted(parts, key=lambda p: (p.step, p.part_no)):
        t, n = assign[p.part_no]
        for _ in range(n):
            bins.append(Bin(len(bins), p.step, p.step_label, t, p.part_no, p.name))
    return bins


# ---------------------------------------------------------------- ルール
def layout_rule(bins: list[Bin], order: str = "size", max_trays: int = 10) -> dict[int, Placement]:
    """単純なルールで並べる（貪欲法）。

    order="size": 小さいビンから順に、すべてのトレイの上の行・左の列から空き場所に詰める（First-Fit）。
                  2008年の「サイズ順の配置」の考え方（本書 図3-5(b)）。
    order="step": 工程順に、今のトレイの左の列・上の行から詰め、入らなくなったら次のトレイへ進む。
                  2008年の「作業順の配置」（本書 図3-5(a)）を単純なルールで再現したもの。CP-SATの初期解（ヒント）にも使う。
    """
    if order == "size":
        seq = sorted(bins, key=lambda b: (b.type.area, b.step, b.id))
    else:
        seq = sorted(bins, key=lambda b: (b.step, -b.type.area, b.id))
    occ = [[[False] * W for _ in range(H)] for _ in range(max_trays)]
    res: dict[int, Placement] = {}

    def fits(t, x, y, w, h):
        return x + w <= W and y + h <= H and all(
            not occ[t][yy][xx] for yy in range(y, y + h) for xx in range(x, x + w))

    def cells(t):
        if order == "size":                       # 行優先（上の行から）
            return [(x, y) for y in range(H) for x in range(W)]
        return [(x, y) for x in range(W) for y in range(H)]   # 列優先（左の列から）

    current = 0
    for b in seq:
        done = False
        trays = range(max_trays) if order == "size" else range(current, max_trays)
        for t in trays:
            for (x, y) in cells(t):
                for (w, h) in b.shapes:
                    if fits(t, x, y, w, h):
                        for yy in range(y, y + h):
                            for xx in range(x, x + w):
                                occ[t][yy][xx] = True
                        res[b.id] = Placement(t, x, y, w, h)
                        current = t
                        done = True
                        break
                if done: break
            if done: break
        if not done:
            raise RuntimeError("max_trays に収まりません")
    return res


# ---------------------------------------------------------------- CP-SAT
@dataclass
class SolveInfo:
    status: str
    objective: float
    bound: float
    seconds: float
    deterministic_time: float


class TrayModel:
    def __init__(self, bins: list[Bin], n_trays: int, sequence: bool,
                 fix_trays: int | None = None,
                 split_w: int = 100, inv_w: int = 20, spread_w: int = 6, tail_w: int = 0):
        self.bins = bins
        self.m = m = cp_model.CpModel()
        self.v: dict[int, dict] = {}
        XMAX = n_trays * W
        xs, ys = [], []
        for b in bins:
            (w0, h0) = b.shapes[0]
            lo, hi = min(w0, h0), max(w0, h0)
            t = m.NewIntVar(0, n_trays - 1, f"t{b.id}")
            if len(b.shapes) == 2:
                r = m.NewBoolVar(f"r{b.id}")                      # 90度回転するか
                w = m.NewIntVar(lo, hi, f"w{b.id}")
                h = m.NewIntVar(lo, hi, f"h{b.id}")
                m.Add(w == w0 + (h0 - w0) * r)
                m.Add(h == h0 + (w0 - h0) * r)
            else:
                w, h = m.NewConstant(w0), m.NewConstant(h0)
            x = m.NewIntVar(0, W - lo, f"x{b.id}")
            y = m.NewIntVar(0, H - lo, f"y{b.id}")
            m.Add(x + w <= W)                                     # はみ出さない
            m.Add(y + h <= H)
            X = m.NewIntVar(0, XMAX, f"X{b.id}")
            m.Add(X == t * W + x)
            Xe = m.NewIntVar(0, XMAX, f"Xe{b.id}")
            Ye = m.NewIntVar(0, H, f"Ye{b.id}")
            m.Add(Xe == X + w)
            m.Add(Ye == y + h)
            xs.append(m.NewIntervalVar(X, w, Xe, f"ix{b.id}"))
            ys.append(m.NewIntervalVar(y, h, Ye, f"iy{b.id}"))
            self.v[b.id] = dict(t=t, x=x, y=y, w=w, h=h, X=X, Xe=Xe, Ye=Ye)
        m.AddNoOverlap2D(xs, ys)                                  # 重ならない

        self.n_used = m.NewIntVar(1, n_trays, "n_used")
        m.AddMaxEquality(self.n_used, [self.v[b.id]["t"] + 1 for b in bins])
        total = sum(b.type.area for b in bins)
        m.Add(self.n_used * W * H >= total)                       # 面積の下界
        if fix_trays is not None:
            m.Add(self.n_used == fix_trays)

        if not sequence:
            m.Minimize(self.n_used)
            return

        steps = sorted({b.step for b in bins})
        by_step = {s: [b for b in bins if b.step == s] for s in steps}
        terms, tmin_, tmax_, anchor, tail = [], {}, {}, {}, {}
        KEYMAX = (XMAX + 1) * H
        for s in steps:
            vv = [self.v[b.id] for b in by_step[s]]
            tmin = m.NewIntVar(0, n_trays - 1, f"tmin{s}")
            tmax = m.NewIntVar(0, n_trays - 1, f"tmax{s}")
            m.AddMinEquality(tmin, [a["t"] for a in vv])
            m.AddMaxEquality(tmax, [a["t"] for a in vv])
            tmin_[s], tmax_[s] = tmin, tmax
            split = m.NewIntVar(0, n_trays - 1, f"split{s}")      # (a) トレイをまたぐ
            m.Add(split == tmax - tmin)
            terms.append(split_w * split)
            xmin = m.NewIntVar(0, XMAX, f"xmin{s}")               # (b) 散らばり
            xmax = m.NewIntVar(0, XMAX, f"xmax{s}")
            ymin = m.NewIntVar(0, H, f"ymin{s}")
            ymax = m.NewIntVar(0, H, f"ymax{s}")
            m.AddMinEquality(xmin, [a["X"] for a in vv])
            m.AddMaxEquality(xmax, [a["Xe"] for a in vv])
            m.AddMinEquality(ymin, [a["y"] for a in vv])
            m.AddMaxEquality(ymax, [a["Ye"] for a in vv])
            terms.append(spread_w * ((xmax - xmin) + (ymax - ymin)))
            keys = []                                             # 読み順キー＝列優先
            for a in vv:
                k = m.NewIntVar(0, KEYMAX, "")
                m.Add(k == a["X"] * H + a["y"])
                keys.append(k)
            an = m.NewIntVar(0, KEYMAX, f"anchor{s}")
            m.AddMinEquality(an, keys)
            anchor[s] = an
            if tail_w:                                            # 第6章：工程の最後のビン
                en = m.NewIntVar(0, KEYMAX, f"end{s}")
                m.AddMaxEquality(en, keys)
                tail[s] = en
        for s, s2 in zip(steps, steps[1:]):
            m.Add(tmax_[s] <= tmin_[s2])                          # (c) トレイは工程順に進む
            inv = m.NewBoolVar(f"inv{s}")                         # (d) 読み始めの逆転
            m.Add(anchor[s2] >= anchor[s] + 1 - KEYMAX * inv)
            terms.append(inv_w * inv)
            if tail_w:                                            # (e) 前の工程の最後より手前に、次の工程が始まる
                inv2 = m.NewBoolVar(f"tail{s}")
                m.Add(anchor[s2] >= tail[s] + 1 - KEYMAX * inv2)
                terms.append(tail_w * inv2)
        m.Minimize(sum(terms))

    def solve(self, det_time: float = 60.0, workers: int = 8, seed: int = 0,
              hint: dict[int, Placement] | None = None):
        """決定的時間（deterministic time）で打ち切る。
        workers=1 なら何度実行しても同じ解になる（同じ版のOR-Tools）。
        workers>1 は速いが、並列探索のため実行ごとに解が少し変わる。"""
        if hint:
            for b in self.bins:
                p = hint[b.id]
                a = self.v[b.id]
                self.m.AddHint(a["t"], p.tray)
                self.m.AddHint(a["x"], p.x)
                self.m.AddHint(a["y"], p.y)
        s = cp_model.CpSolver()
        s.parameters.max_deterministic_time = det_time
        s.parameters.num_workers = workers
        s.parameters.random_seed = seed
        st = s.Solve(self.m)
        info = SolveInfo(s.StatusName(st), s.ObjectiveValue(), s.BestObjectiveBound(),
                         s.wall_time, s.deterministic_time)
        if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return None, info
        res = {}
        for b in self.bins:
            a = self.v[b.id]
            res[b.id] = Placement(s.Value(a["t"]), s.Value(a["x"]), s.Value(a["y"]),
                                  s.Value(a["w"]), s.Value(a["h"]))
        return res, info


def solve_min_trays(bins, max_trays=6, det_time=30.0, workers=1):
    """トレイ枚数の最小化。既定は1スレッド（再現性を優先）"""
    return TrayModel(bins, max_trays, sequence=False).solve(det_time, workers=workers)


def solve_sequence(bins, n_trays, det_time=120.0, extra_trays=2, hint=None):
    """作業順の制約のもとで、n_trays 枚から順に試し、解けた最小枚数で罰則を最小化する。
    全体を並列で一度に解く方法（速いが再現性はない）。本書の結果は improve_lns で作る。"""
    for nt in range(n_trays, n_trays + extra_trays + 1):
        res, info = TrayModel(bins, nt, sequence=True, fix_trays=nt).solve(
            det_time, hint=hint if hint and max(p.tray for p in hint.values()) < nt else None)
        if res is not None:
            return res, info, nt
    raise RuntimeError("配置が見つかりません")


def penalty_of(bins: list[Bin], pl: dict[int, Placement], n_trays: int, exact: bool = True,
               **weights) -> float:
    """与えた配置の罰則（作業順モデルの目的関数値）を計算する。全ビンを固定して解くだけ。
    exact=False なら、トレイは n_trays 枚「まで」（第6章のε制約法）。"""
    mdl = TrayModel(bins, n_trays, sequence=True, fix_trays=n_trays if exact else None, **weights)
    for b in bins:
        p, a = pl[b.id], mdl.v[b.id]
        for k, v in (("t", p.tray), ("x", p.x), ("y", p.y), ("w", p.w)):
            mdl.m.Add(a[k] == v)
    s = cp_model.CpSolver()
    s.parameters.num_workers = 1
    st = s.Solve(mdl.m)
    return s.ObjectiveValue() if st in (cp_model.OPTIMAL, cp_model.FEASIBLE) else float("nan")


def improve_lns(bins: list[Bin], init: dict[int, Placement], n_trays: int,
                window: int = 4, stride: int = 2, passes: int = 3, det_time: float = 3.0,
                log=print, exact: bool = True, **weights):
    """大近傍探索（LNS）：工程を数個ずつ順番に「解き直し」て、配置を少しずつ良くする。

    全体を一度に解くと時間がかかる大きな問題でも、一部の工程のビンだけを動かし、
    残りを固定した小さな問題なら1スレッドで速く解ける。
    1スレッド＋決定的時間で解くので、何度実行しても同じ結果になる（再現性がある）。
    """
    steps = sorted({b.step for b in bins})
    cur = dict(init)
    best_obj = penalty_of(bins, init, n_trays, exact=exact, **weights)   # 初期解の罰則
    history = [dict(pass_=0, steps="初期解", objective=best_obj)]
    for ps in range(passes):
        for i in range(0, max(1, len(steps) - window + 1), stride):
            free = set(steps[i:i + window])
            mdl = TrayModel(bins, n_trays, sequence=True, fix_trays=n_trays if exact else None, **weights)
            for b in bins:
                p, a = cur[b.id], mdl.v[b.id]
                if b.step in free:
                    mdl.m.AddHint(a["t"], p.tray)
                    mdl.m.AddHint(a["x"], p.x)
                    mdl.m.AddHint(a["y"], p.y)
                else:                                  # 窓の外のビンは今の位置に固定
                    mdl.m.Add(a["t"] == p.tray)
                    mdl.m.Add(a["x"] == p.x)
                    mdl.m.Add(a["y"] == p.y)
                    mdl.m.Add(a["w"] == p.w)
            s = cp_model.CpSolver()
            s.parameters.num_workers = 1
            s.parameters.max_deterministic_time = det_time
            st = s.Solve(mdl.m)
            if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                obj = s.ObjectiveValue()
                if best_obj is None or obj < best_obj:
                    best_obj = obj
                    for b in bins:
                        a = mdl.v[b.id]
                        cur[b.id] = Placement(s.Value(a["t"]), s.Value(a["x"]), s.Value(a["y"]),
                                              s.Value(a["w"]), s.Value(a["h"]))
            history.append(dict(pass_=ps + 1, steps=f"{step_label(steps[i])}-{step_label(steps[min(i + window, len(steps)) - 1])}",
                                objective=best_obj))
            if log:
                log(f"  pass {ps + 1} 工程 {history[-1]['steps']}: 罰則 {best_obj}")
    return cur, best_obj, history
