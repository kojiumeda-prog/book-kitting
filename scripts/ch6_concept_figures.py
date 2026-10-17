"""第6章の概念図（計算なし）。

    python scripts/ch6_concept_figures.py

図6-4：辞書式の流れ（上段：枚数が第一、下段：順位を逆にした場合）
図6-7：候補提示 → 意見 → 制約追加のループ
図6-8：聞き取りシートの例（印刷して使う形）
図6-9：3つの決め方の使い分け（判断の木）
"""
import math

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

from ch3_figures import arrow, rbox, save


# ---------------------------------------------------------------- 図6-4
def fig6_4():
    fig, ax = plt.subplots(figsize=(10.5, 4.6))
    ax.set_xlim(0, 10.5)
    ax.set_ylim(0, 4.8)
    ax.set_axis_off()
    rows = [
        (3.2, "(a) 第5章の順位：枚数が第一",
         ["第1段階\n枚数を最小にする", "枚数を固定する\n（「4枚」を制約に入れる）", "第2段階\n罰則を最小にする",
          "結果\n4枚の中で\n最も使いやすい配置"], "0.92"),
        (0.6, "(b) 順位を逆にすると：使いやすさが第一",
         ["第1段階\n罰則を最小にする\n（枚数は何枚でもよい）", "罰則を固定する\n（最良の値を制約に入れる）",
          "第2段階\n枚数を最小にする", "結果\n罰則を保つと\n枚数はほとんど減らない"], "white"),
    ]
    for y, title, steps, fc in rows:
        ax.text(0.1, y + 1.45, title, fontsize=10, fontweight="bold")
        for i, s in enumerate(steps):
            x = 0.1 + i * 2.6
            last = i == len(steps) - 1
            rbox(ax, x, y, 2.1, 1.15, s, fc="0.8" if last else fc, fs=8.5, lw=1.6 if last else 1.0)
            if not last:
                arrow(ax, x + 2.12, y + 0.575, x + 2.58, y + 0.575)
    ax.text(10.4, 0.25, "上位の目的をわずかに良くするために、下位の目的をいくらでも犠牲にする（辞書式の弱点）",
            ha="right", fontsize=8.5)
    save(fig, "fig6-4_lexicographic.png")


# ---------------------------------------------------------------- 図6-7
def fig6_7():
    fig, ax = plt.subplots(figsize=(8.4, 5.4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.4)
    ax.set_aspect("equal")
    ax.set_axis_off()
    cx, cy, r = 4.0, 3.2, 2.2
    nodes = [(90, "① 解く\n（候補を並べる）"), (0, "② 配置図を見せる\n（組立者・班長・管理者）"),
             (270, "③ 使えない理由を聞く\n（暗黙の制約）"), (180, "④ 制約か罰則にして\nモデルに足す")]
    pos = {}
    for ang, text in nodes:
        x, y = cx + r * math.cos(math.radians(ang)), cy + r * math.sin(math.radians(ang))
        pos[ang] = (x, y)
        rbox(ax, x - 1.15, y - 0.45, 2.3, 0.9, text, fs=8.5, fc="0.92" if ang == 270 else "white")
    order = [90, 0, 270, 180, 90]
    for a0, a1 in zip(order[:-1], order[1:]):
        # 円周に沿って、箱の外側どうしを曲線の矢印でつなぐ
        m0, m1 = a0 - 28, a1 + 28                     # 箱から少し離れた円周上の点
        p0 = (cx + r * math.cos(math.radians(m0)), cy + r * math.sin(math.radians(m0)))
        p1 = (cx + r * math.cos(math.radians(m1)), cy + r * math.sin(math.radians(m1)))
        ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=13, lw=1.1, color="black",
                                     connectionstyle="arc3,rad=-0.35"))
    ax.text(cx, cy, "2〜3回\n繰り返す", ha="center", va="center", fontsize=10, fontweight="bold")
    x2, y2 = pos[0]
    rbox(ax, 8.1, y2 - 0.45, 1.6, 0.9, "採用\n（現場に導入）", fc="0.8", fs=9, lw=1.6)
    arrow(ax, x2 + 1.17, y2, 8.08, y2)
    ax.text((x2 + 1.17 + 8.08) / 2, y2 + 0.15, "使える", ha="center", va="bottom", fontsize=8.5)
    ax.text(cx, 0.15, "自分の意見で答えが変わるのを見ると、現場はモデルを「自分たちの道具」として信頼する",
            ha="center", fontsize=8.5)
    save(fig, "fig6-7_feedback_loop.png")


# ---------------------------------------------------------------- 図6-8
def fig6_8():
    fig, ax = plt.subplots(figsize=(7.6, 7.0))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10.6)
    ax.set_axis_off()
    ax.add_patch(Rectangle((0.1, 0.1), 9.8, 10.4, fill=False, lw=1.4))
    ax.text(0.4, 9.95, "トレイ配置の聞き取りシート", fontsize=13, fontweight="bold", va="center")
    ax.text(9.6, 9.95, "記入日 ____／____　記入者 ________", fontsize=9, ha="right", va="center")
    ex = dict(fontsize=9, color="0.35", style="italic", va="center")
    rows = [  # (項目, 高さ, 描き方, 記入例)
        ("見た候補", 0.8, "line", "候補B（トレイ4枚）"),
        ("立場", 0.8, "check", ["組立者", "班長", "生産技術", "管理者"], 0),
        ("使えるか", 0.8, "check", ["使える", "直せば使える", "使えない"], 1),
        ("気になる場所", 1.6, "box", "2枚目の左上。工程12の部品箱が奥にある"),
        ("理由", 1.6, "box", "工程12の部品は重いので、奥だと取りにくい"),
        ("絶対か、できればか", 0.8, "check", ["絶対（制約へ）", "できれば（罰則へ）"], 1),
        ("ほかの工程にも\n当てはまるか", 1.0, "check", ["当てはまる", "この工程だけ"], 0),
        ("そのほか", 1.0, "box", ""),
    ]
    y = 9.4
    for row in rows:
        label, h, kind = row[0], row[1], row[2]
        y0 = y - h
        ax.plot([0.1, 9.9], [y, y], color="black", lw=0.8)
        ax.text(0.35, y0 + h / 2, label, fontsize=9.5, va="center")
        ax.plot([2.6, 2.6], [y0, y], color="black", lw=0.8)
        if kind == "line":
            ax.plot([2.9, 9.5], [y0 + 0.2, y0 + 0.2], color="0.5", lw=0.6)
            ax.text(3.0, y0 + h / 2 + 0.05, row[3], **ex)
        elif kind == "box":
            if row[3]:
                ax.text(2.9, y - 0.35, row[3], **ex)
        else:
            x = 2.9
            for i, opt in enumerate(row[3]):
                ax.add_patch(Rectangle((x, y0 + h / 2 - 0.13), 0.26, 0.26, fill=False, lw=0.9))
                if i == row[4]:
                    ax.text(x + 0.13, y0 + h / 2, "✓", ha="center", va="center", fontsize=10, color="0.35")
                ax.text(x + 0.38, y0 + h / 2, opt, fontsize=9, va="center")
                x += 0.6 + 0.24 * len(opt)
        y = y0
    ax.plot([0.1, 9.9], [y, y], color="black", lw=0.8)
    ax.text(0.4, 0.45, "灰色の文字は記入例。最後の2つの項目で、制約にするか罰則にするか、例外か一般の条件かを決める",
            fontsize=8, color="0.25", va="center")
    save(fig, "fig6-8_interview_sheet.png")


# ---------------------------------------------------------------- 図6-9
def fig6_9():
    fig, ax = plt.subplots(figsize=(9.6, 4.8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5.2)
    ax.set_axis_off()
    rbox(ax, 2.6, 4.0, 4.8, 0.9, "問1　目的の優先度を、答えを見る前に決められるか", fc="0.92", fs=9.5, bold=True)
    rbox(ax, 4.2, 2.2, 5.2, 0.9, "問2　悪さを同じ単位（秒など）にそろえられるか", fc="0.92", fs=9.5, bold=True)
    rbox(ax, 0.2, 2.1, 3.2, 1.1, "解を並べて選ぶ（6.4節）\n枚数ごとの候補を見て、人が選ぶ", fs=9, lw=1.6)
    rbox(ax, 3.4, 0.2, 3.0, 1.1, "重みを付けて足す（6.2節）\n交換レートを秒などで決める", fs=9, lw=1.6)
    rbox(ax, 6.8, 0.2, 3.0, 1.1, "優先順位を付ける（6.3節）\n「枚数が第一」のように\n順に解く", fs=9, lw=1.6)
    arrow(ax, 3.8, 4.0, 2.0, 3.22)
    ax.text(2.55, 3.65, "いいえ", fontsize=9, ha="right")
    arrow(ax, 6.2, 4.0, 6.8, 3.12)
    ax.text(6.6, 3.65, "はい", fontsize=9)
    arrow(ax, 5.8, 2.2, 4.9, 1.32)
    ax.text(5.15, 1.85, "はい", fontsize=9, ha="right")
    arrow(ax, 7.8, 2.2, 8.3, 1.32)
    ax.text(8.15, 1.85, "いいえ", fontsize=9)
    ax.text(0.3, 1.2, "どの方法でも、最後は\n人の判断が残る。\n候補は配置図で見せる", fontsize=8.5, color="0.25",
            va="top")
    save(fig, "fig6-9_decision_tree.png")


if __name__ == "__main__":
    for f in (fig6_4, fig6_7, fig6_8, fig6_9):
        f()
