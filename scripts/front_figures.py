"""はじめにの図。

    python scripts/front_figures.py

図0-1：本書の全体像（章の流れと、各章で作るもの）
"""
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

from ch3_figures import rbox, save


def fig0_1():
    fig, ax = plt.subplots(figsize=(13, 4.6))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 4.8)
    ax.set_axis_off()
    stages = [("現場の問題", "第1章", "部品供給の3つの方式\n外段取りとキッティング", "図1-1〜1-5"),
              ("モデルにする", "第2・3章", "変数・制約・目的\n2008年のExcelの限界", "コード2-1、3-1"),
              ("解く", "第4・5章", "部品箱の寸法（MILP）\nトレイの配置（CP-SAT）", "コード4-1〜4-3\nコード5-1〜5-6"),
              ("選ぶ", "第6章", "重み・優先順位\n解を並べて選ぶ", "コード6-1、6-2\n聞き取りシート"),
              ("導入する", "第7章", "小さく始める、費用\n変更への追従", "コード7-1\n導入チェックリスト"),
              ("広げる", "第8章", "棚割り、配車、シフト\n自社で始めるには", "配車・シフトの例")]
    w, gap = 1.95, 0.17
    for i, (name, ch, what, made) in enumerate(stages):
        x = 0.15 + i * (w + gap)
        fc = "0.8" if i in (2, 3) else "0.92"
        ax.add_patch(Polygon([(x, 3.2), (x + w - 0.15, 3.2), (x + w + 0.08, 3.8), (x + w - 0.15, 4.4), (x, 4.4),
                              (x + 0.23 if i else x, 3.8)], closed=True, fc=fc, ec="black", lw=1.0))
        ax.text(x + w / 2, 3.95, name, ha="center", va="center", fontsize=11, fontweight="bold")
        ax.text(x + w / 2, 3.52, ch, ha="center", va="center", fontsize=9)
        ax.text(x + 0.03, 2.95, "扱うこと", fontsize=7.5, color="0.3", va="bottom")
        rbox(ax, x, 1.75, w - 0.1, 1.15, what, fs=8.3)
        ax.text(x + 0.03, 1.48, "作るもの", fontsize=7.5, color="0.3", va="bottom")
        rbox(ax, x, 0.45, w - 0.1, 1.0, made, fs=8.3)
    ax.text(6.5, 0.12, "灰色の濃い「解く」「選ぶ」が数理最適化の中心。数式を飛ばして読む場合は、第4・5章は各章の始めと終わり、図と表を追う",
            ha="center", fontsize=8.5, color="0.25")
    save(fig, "fig0-1_overview.png")


if __name__ == "__main__":
    fig0_1()
