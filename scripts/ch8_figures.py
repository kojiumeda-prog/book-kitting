"""第8章の図（概念図と、架空データで描く配車とシフトの例）。

    python scripts/ch8_figures.py

図8-1：矩形配置の応用先
図8-2：配車問題の変数・制約・目的（トレイの配置との対応）
図8-3：配車結果の地図の例（架空。OR-Tools の Routing で解く）
図8-4：シフト表の例（架空。CP-SAT で作る）
図8-5：始め方の3段階
図8-6：内製と委託の切り分け
"""
import math
import random

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, Polygon, Rectangle

from ch3_figures import arrow, rbox, save


# ---------------------------------------------------------------- 図8-1
def _shelf(ax, x, y, w, h):
    ax.add_patch(Rectangle((x, y), w, h, fill=False, lw=1.0))
    for k in range(1, 3):
        ax.plot([x, x + w], [y + h * k / 3] * 2, color="black", lw=0.8)
    rnd = random.Random(1)
    for k in range(3):
        xx = x + 0.05
        while True:
            bw = rnd.choice([0.18, 0.25, 0.32])
            if xx + bw > x + w - 0.05:
                break
            ax.add_patch(Rectangle((xx, y + h * k / 3 + 0.03), bw, h / 3 - 0.1, fc="0.8" if k == 1 else "white",
                                   ec="black", lw=0.6))
            xx += bw + 0.04
    ax.text(x + w + 0.05, y + h * 1.5 / 3, "←取りやすい段", fontsize=6.5, va="center")


def _pallet(ax, x, y, w, h):
    ax.add_patch(Rectangle((x, y), w, h, fc="0.95", ec="black", lw=1.0))
    sizes = [(0.45, 0.35), (0.45, 0.35), (0.35, 0.45), (0.3, 0.3), (0.3, 0.3), (0.55, 0.25)]
    pos = [(0.05, 0.05), (0.52, 0.05), (1.0, 0.05), (0.05, 0.45), (0.38, 0.45), (0.72, 0.55)]
    for (bw, bh), (px, py) in zip(sizes, pos):
        if px + bw <= w and py + bh <= h:
            ax.add_patch(Rectangle((x + px, y + py), bw, bh, fc="white", ec="black", lw=0.6))


def _truck(ax, x, y, w, h):
    ax.add_patch(Rectangle((x, y), w * 0.75, h, fill=False, lw=1.0))
    ax.add_patch(Polygon([(x + w * 0.75, y), (x + w, y), (x + w, y + h * 0.6), (x + w * 0.85, y + h * 0.8),
                          (x + w * 0.75, y + h * 0.8)], closed=True, fc="0.8", ec="black", lw=1.0))
    for i, lab in enumerate(["3", "2", "1"]):
        ax.add_patch(Rectangle((x + 0.05 + i * w * 0.24, y + 0.08), w * 0.21, h * 0.8, fc="white", ec="black", lw=0.6))
        ax.text(x + 0.05 + i * w * 0.24 + w * 0.105, y + 0.08 + h * 0.4, lab, ha="center", va="center", fontsize=7)
    ax.text(x + w + 0.05, y + h * 0.5, "←数字は降ろす順", fontsize=6.5, va="center")


def _board(ax, x, y, w, h):
    ax.add_patch(Rectangle((x, y), w, h, fc="white", ec="black", lw=1.0, hatch="////"))
    for px, py, bw, bh in [(0, 0, 0.5, 0.45), (0.5, 0, 0.45, 0.3), (0.95, 0, 0.3, 0.45), (0, 0.45, 0.35, 0.3),
                           (0.35, 0.3, 0.6, 0.3), (0.95, 0.45, 0.3, 0.2)]:
        if px + bw <= w + 1e-9 and py + bh <= h + 1e-9:
            ax.add_patch(Rectangle((x + px, y + py), bw, bh, fc="0.85", ec="black", lw=0.6))
    ax.text(x + w + 0.05, y + h * 0.85, "←斜線は端材", fontsize=6.5, va="center")


def _floor(ax, x, y, w, h):
    ax.add_patch(Rectangle((x, y), w, h, fill=False, lw=1.0))
    boxes = [(0.08, 0.1, 0.3, 0.25), (0.5, 0.1, 0.35, 0.25), (0.95, 0.12, 0.25, 0.3), (0.3, 0.5, 0.4, 0.2)]
    for bx, by, bw, bh in boxes:
        ax.add_patch(Rectangle((x + bx, y + by), bw, bh, fc="0.85", ec="black", lw=0.6))
    for (a, b) in [(0, 1), (1, 2), (1, 3)]:
        ax1 = (x + boxes[a][0] + boxes[a][2] / 2, y + boxes[a][1] + boxes[a][3] / 2)
        ax2 = (x + boxes[b][0] + boxes[b][2] / 2, y + boxes[b][1] + boxes[b][3] / 2)
        ax.add_patch(FancyArrowPatch(ax1, ax2, arrowstyle="-|>", mutation_scale=7, lw=0.7, ls="--"))


def fig8_1():
    fig, ax = plt.subplots(figsize=(12, 7.2))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7.4)
    ax.set_axis_off()
    panels = [  # (x, y, 題, 描く関数, 変数, 制約, 目的)
        (0.1, 4.6, "倉庫の棚割り", _shelf, "商品をどの段のどこに置くか", "段の幅に収まる、重ならない",
         "よく出る商品を取りやすい段に"),
        (4.1, 4.6, "パレットへの積付け", _pallet, "段ボールの位置と向き", "パレットからはみ出さない",
         "枚数を少なく、重い箱を下に"),
        (8.1, 4.6, "トラック荷台への積付け", _truck, "荷物の位置", "荷台に収まる、重ならない",
         "降ろす順に取り出せる"),
        (0.1, 0.3, "板材の板取り", _board, "部品を切り出す位置と向き", "定尺の板に収まる、重ならない",
         "捨てる端材を少なく"),
        (8.1, 0.3, "工場のレイアウト", _floor, "設備や作業台の位置", "建屋の床に収まる、重ならない",
         "物の流れる距離を短く"),
    ]
    for x, y, title, draw, v, c, o in panels:
        ax.add_patch(Rectangle((x, y), 3.8, 2.6, fill=False, lw=1.0, ls="-"))
        ax.text(x + 0.12, y + 2.38, title, fontsize=10, fontweight="bold", va="center")
        draw(ax, x + 0.2, y + 1.15, 1.25, 0.9)
        for k, (lab, t) in enumerate([("変数", v), ("制約", c), ("目的", o)]):
            ax.text(x + 0.15, y + 0.78 - k * 0.27, f"{lab}：{t}", fontsize=7.6, va="center")
    rbox(ax, 4.4, 1.25, 3.2, 1.6, "大きさの違う長方形を\n重ならずに並べる\n\n（第5章の AddNoOverlap2D）",
         fc="0.85", fs=10, lw=1.6, bold=True)
    for (px, py) in [(2.0, 4.6), (6.0, 4.6), (10.0, 4.6), (3.9, 1.6), (8.1, 1.6)]:
        ax.plot([6.0, px], [2.05, py] if py > 3 else [2.05, py], color="0.4", lw=0.9, ls="--", zorder=0)
    ax.text(6.0, 0.55, "違うのは、周りに付ける制約と目的だけ", ha="center", fontsize=9)
    save(fig, "fig8-1_applications.png")


# ---------------------------------------------------------------- 図8-2
def fig8_2():
    fig, ax = plt.subplots(figsize=(10.5, 5.6))
    ax.set_xlim(0, 10.5)
    ax.set_ylim(0, 6.0)
    ax.set_axis_off()
    rows = [("変数（決めること）", "部品箱をどのトレイの\nどの位置に置くか", "訪問先をどの車両の\n何番目に回るか"),
            ("入れ物の大きさ（制約）", "トレイ1枚に入る\nブロックの数", "車両1台に積める量、\n運転手の勤務時間"),
            ("順序の制約", "トレイは工程順に進む", "訪問先ごとの受け入れ\n時間帯に間に合う"),
            ("目的（良し悪し）", "トレイの枚数、\nまとまり、読み順", "車両の台数、\n走行距離、残業時間"),
            ("ぶつかる良さ（第6章）", "枚数と作業のしやすさ", "台数と、運転手ごとの\n担当地域の固定")]
    ax.text(3.9, 5.65, "トレイの配置（本書）", ha="center", fontsize=10, fontweight="bold")
    ax.text(8.2, 5.65, "配車計画", ha="center", fontsize=10, fontweight="bold")
    for i, (lab, a, b) in enumerate(rows):
        y = 4.55 - i * 1.07
        rbox(ax, 0.1, y, 2.2, 0.85, lab, fc="0.85", fs=9, bold=True)
        rbox(ax, 2.7, y, 2.4, 0.85, a, fs=8.8)
        rbox(ax, 7.0, y, 2.4, 0.85, b, fs=8.8, lw=1.4)
        ax.add_patch(FancyArrowPatch((5.15, y + 0.425), (6.95, y + 0.425), arrowstyle="<|-|>", mutation_scale=10,
                                     lw=0.9, ls="--"))
    ax.text(6.05, 4.55 + 0.55, "読み替える", ha="center", fontsize=8)
    save(fig, "fig8-2_vrp_model.png")


# ---------------------------------------------------------------- 図8-3
def _solve_vrp(pts, depot, n_veh=3, cap=8):
    from ortools.constraint_solver import pywrapcp, routing_enums_pb2
    nodes = [depot] + pts
    dist = [[int(100 * math.dist(a, b)) for b in nodes] for a in nodes]
    man = pywrapcp.RoutingIndexManager(len(nodes), n_veh, 0)
    r = pywrapcp.RoutingModel(man)
    cb = r.RegisterTransitCallback(lambda i, j: dist[man.IndexToNode(i)][man.IndexToNode(j)])
    r.SetArcCostEvaluatorOfAllVehicles(cb)
    dcb = r.RegisterUnaryTransitCallback(lambda i: 0 if man.IndexToNode(i) == 0 else 1)
    r.AddDimensionWithVehicleCapacity(dcb, 0, [cap] * n_veh, True, "load")
    p = pywrapcp.DefaultRoutingSearchParameters()
    p.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    p.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    p.time_limit.seconds = 3
    sol = r.SolveWithParameters(p)
    routes = []
    for v in range(n_veh):
        i, rt = r.Start(v), []
        while not r.IsEnd(i):
            rt.append(man.IndexToNode(i))
            i = sol.Value(r.NextVar(i))
        rt.append(0)
        routes.append(rt)
    return nodes, routes


def fig8_3():
    rnd = random.Random(8)
    depot = (5.0, 5.0)
    pts = []
    while len(pts) < 20:                      # 点どうし・拠点と重ならないように置く
        p = (rnd.uniform(0.6, 9.4), rnd.uniform(0.6, 9.4))
        if math.dist(p, depot) > 1.3 and all(math.dist(p, q) > 1.0 for q in pts):
            pts.append(p)
    nodes, routes = _solve_vrp(pts, depot)
    fig, ax = plt.subplots(figsize=(6.8, 6.4))
    styles = [("-", "車両1"), ("--", "車両2"), (":", "車両3")]
    for rt, (ls, lab) in zip(routes, styles):
        xs, ys = [nodes[k][0] for k in rt], [nodes[k][1] for k in rt]
        ax.plot(xs, ys, ls=ls, color="black", lw=1.4, label=f"{lab}（{len(rt) - 2}か所）")
    for k, (x, y) in enumerate(pts, start=1):
        ax.add_patch(Circle((x, y), 0.22, fc="white", ec="black", lw=0.9, zorder=3))
        ax.text(x, y, str(k), ha="center", va="center", fontsize=6.5, zorder=4)
    ax.add_patch(Rectangle((depot[0] - 0.3, depot[1] - 0.3), 0.6, 0.6, fc="black", zorder=3))
    ax.text(depot[0], depot[1] - 0.5, "拠点", ha="center", va="top", fontsize=9)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.02), ncol=3, fontsize=8.5, frameon=False)
    ax.set_title("架空の拠点1か所と訪問先20か所。1台に8か所まで、走行距離の合計を最小に", fontsize=9)
    save(fig, "fig8-3_vrp_map.png")


# ---------------------------------------------------------------- 図8-4
def fig8_4():
    from ortools.sat.python import cp_model
    P, D = 8, 14
    people = [f"{c}さん" for c in "ABCDEFGH"]
    S = {"日": 0, "夜": 1, "休": 2}
    need = {0: 4, 1: 1}
    wish = {(0, 3), (1, 9), (2, 5), (3, 12), (4, 0), (5, 7), (6, 10), (7, 2)}   # 希望休（人, 日）
    m = cp_model.CpModel()
    x = {(p, d, s): m.NewBoolVar("") for p in range(P) for d in range(D) for s in range(3)}
    for p in range(P):
        for d in range(D):
            m.AddExactlyOne(x[p, d, s] for s in range(3))
    for d in range(D):
        for s, n in need.items():
            m.Add(sum(x[p, d, s] for p in range(P)) == n)
    for p, d in wish:
        m.Add(x[p, d, 2] == 1)
    for p in range(P):
        for d in range(D - 1):
            m.AddImplication(x[p, d, 1], x[p, d + 1, 2])          # 夜勤の翌日は休み
        for d in range(D - 5):
            m.Add(sum(x[p, d + k, 2] for k in range(6)) >= 1)       # 6日続けて働かない
    nights = [sum(x[p, d, 1] for d in range(D)) for p in range(P)]
    hi, lo = m.NewIntVar(0, D, ""), m.NewIntVar(0, D, "")
    m.AddMaxEquality(hi, nights)
    m.AddMinEquality(lo, nights)
    m.Minimize(hi - lo)
    sv = cp_model.CpSolver()
    sv.parameters.num_workers = 1
    sv.parameters.random_seed = 0
    assert sv.Solve(m) in (cp_model.OPTIMAL, cp_model.FEASIBLE)
    fig, ax = plt.subplots(figsize=(10, 4.6))
    ax.set_xlim(-1.6, D + 0.1)
    ax.set_ylim(P + 1.2, -0.2)
    ax.set_axis_off()
    shade = {0: "0.85", 1: "0.35", 2: "white"}
    for d in range(D):
        ax.text(d + 0.5, 0.5, f"{d + 1}", ha="center", va="center", fontsize=9)
    for p in range(P):
        ax.text(-0.2, p + 1.5, people[p], ha="right", va="center", fontsize=9)
        for d in range(D):
            s = next(s for s in range(3) if sv.Value(x[p, d, s]))
            ax.add_patch(Rectangle((d, p + 1), 1, 1, fc=shade[s], ec="black", lw=0.6))
            lab = ["日", "夜", "休"][s]
            ax.text(d + 0.5, p + 1.5, lab, ha="center", va="center", fontsize=9,
                    color="white" if s == 1 else "black")
            if (p, d) in wish:
                ax.add_patch(Circle((d + 0.5, p + 1.5), 0.36, fill=False, lw=1.2))
    ax.text(-1.5, 0.5, "日付", va="center", fontsize=9)
    ax.text(0, P + 1.25, "○は希望休。各日に日勤4人・夜勤1人。夜勤の翌日は休み、6日続けて働かない。"
            "夜勤の回数の差を最小にした（全員" + f"{sv.Value(lo)}〜{sv.Value(hi)}回）",
            fontsize=8.5, va="top")
    save(fig, "fig8-4_shift_table.png")


# ---------------------------------------------------------------- 図8-5
def fig8_5():
    fig, ax = plt.subplots(figsize=(11, 5.2))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 5.4)
    ax.set_axis_off()
    stages = [("第1段階　問題を書き出す", "最初の1か月",
               "困りごとを変数・制約・目的に\n分けて紙に書き出す。\n今の決め方と時間を測る",
               "問題の書き出し、\n導入前の数字", "第1・2章、第7章7.6節"),
              ("第2段階　小さなモデルで解く", "1〜2か月目",
               "本書のコードを土台に\n小さなデータで解く。\n答えを見せて暗黙の制約を足す",
               "動く小さなモデル、\n候補の配置図", "第4〜6章"),
              ("第3段階　現場で試す", "3か月目",
               "範囲を絞って使い、\n第1段階の数字と比べる。\n変更に追従する手順と担当を決める",
               "効果の比較、\n運用の手順と担当", "第7章")]
    for i, (title, when, do, out, ch) in enumerate(stages):
        x = 0.2 + i * 3.6
        ax.add_patch(Polygon([(x, 4.0), (x + 3.2, 4.0), (x + 3.5, 4.55), (x + 3.2, 5.1), (x, 5.1),
                              (x + 0.3 if i else x, 4.55)], closed=True, fc="0.8" if i == 1 else "0.9",
                             ec="black", lw=1.0))
        ax.text(x + 1.75, 4.7, title, ha="center", va="center", fontsize=9.5, fontweight="bold")
        ax.text(x + 1.75, 4.3, f"（{when}）", ha="center", va="center", fontsize=8.5)
        for k, (lab, t, h) in enumerate([("やること", do, 1.35), ("できあがるもの", out, 0.75),
                                         ("本書の章", ch, 0.55)]):
            y0 = [2.25, 1.2, 0.3][k]
            ax.text(x + 0.05, y0 + h + 0.06, lab, fontsize=8, color="0.25", va="bottom")
            rbox(ax, x, y0, 3.2, h, t, fs=8.5)
    save(fig, "fig8-5_three_stages.png")


# ---------------------------------------------------------------- 図8-6
def fig8_6():
    fig, ax = plt.subplots(figsize=(7.6, 6.2))
    ax.add_patch(Rectangle((0.6, 0), 0.4, 1.0, fc="0.88", ec="none"))
    ax.text(0.8, 0.03, "自社にしかできない", ha="center", fontsize=9, color="0.2")
    ax.add_patch(Rectangle((0.02, 0.62), 0.56, 0.36, fill=False, ls="--", lw=1.0))
    ax.text(0.04, 0.95, "経験のある人の助けが役立つ", fontsize=9, va="top", color="0.2")
    pts = [("問題の書き出し", 0.86, 0.45, True), ("データ集めと点検", 0.80, 0.16, True),
           ("運用（変更への追従）", 0.70, 0.30, True), ("モデルの作成", 0.40, 0.82, False),
           ("画面や帳票の作成", 0.22, 0.32, False)]
    for name, x, y, own in pts:
        ax.plot(x, y, "o", ms=11, mfc="black" if own else "white", mec="black", mew=1.4)
        ax.text(x, y + 0.045, name, ha="center", va="bottom", fontsize=9)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel("現場の知識がどれだけ要るか　→ 多い", fontsize=9.5)
    ax.set_ylabel("数理最適化の知識がどれだけ要るか　→ 多い", fontsize=9.5)
    ax.set_title("●自社でやる仕事　○外部に頼んでもよい仕事", fontsize=9.5)
    save(fig, "fig8-6_make_or_buy.png")


if __name__ == "__main__":
    for f in (fig8_1, fig8_2, fig8_3, fig8_4, fig8_5, fig8_6):
        f()
