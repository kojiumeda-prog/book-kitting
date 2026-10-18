"""第7章の図（概念図と、本文の表を描いたグラフ）。

    python scripts/ch7_figures.py

図7-1：パイロットの進め方
図7-2：入力データの流れ
図7-3：2方式の費用構成（本文7.3節の架空の価格）
図7-4：部品を集める2つのやり方と、待ちのできる場所
図7-5：変更から新しい印刷シートまでの流れ
図7-6：効果測定の指標と、第1章の問題の対応
図7-7：導入前後の比較の例（本文7.6節の架空の数字）
（図7-8 導入チェックリストは、本文のチェックリストをそのまま使う）
"""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Polygon

from ch3_figures import arrow, rbox, save


def diamond(ax, x, y, w, h, text, fs=8.5):
    ax.add_patch(Polygon([(x, y + h / 2), (x + w / 2, y + h), (x + w, y + h / 2), (x + w / 2, y)],
                         closed=True, fc="0.85", ec="black", lw=1.0))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs)


def triangle(ax, x, y, s=0.32):
    ax.add_patch(Polygon([(x - s / 2, y), (x + s / 2, y), (x, y + s * 0.9)], closed=True, fc="0.6",
                         ec="black", lw=0.8))


# ---------------------------------------------------------------- 図7-1
def fig7_1():
    fig, ax = plt.subplots(figsize=(11, 4.4))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 4.6)
    ax.set_axis_off()
    top = ["① 範囲を決める\n（作業台・品目）", "② 成功の基準を\n決める", "③ 導入前に\n測る（7.6節）",
           "④ データを集め\n点検する（7.2節）"]
    bottom = ["⑤ 部品箱と\nトレイの準備（7.3節）", "⑥ 試行", "⑦ 導入後に\n測る（7.6節）"]
    for i, t in enumerate(top):
        x = 0.2 + i * 2.75
        rbox(ax, x, 3.0, 2.2, 1.1, t, fs=8.5, fc="0.92" if i == 2 else "white")
        if i < 3:
            arrow(ax, x + 2.22, 3.55, x + 2.73, 3.55)
    arrow(ax, 9.5, 2.98, 9.5, 2.42)
    for i, t in enumerate(bottom):
        x = 8.4 - i * 2.75
        rbox(ax, x, 1.3, 2.2, 1.1, t, fs=8.5, fc="0.92" if i == 2 else "white")
        if i < 2:
            arrow(ax, x - 0.02, 1.85, x - 0.53, 1.85)
    diamond(ax, 0.2, 1.25, 2.4, 1.2, "⑧ 広げるか？")      # 頂点：右(2.6, 1.85)、上(1.4, 2.45)、下(1.4, 1.25)

    def link(p0, p1, ls="-"):                          # 頂点にぴったり付ける矢印（縮めない）
        ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=12, lw=1.0, color="black",
                                     linestyle=ls, shrinkA=0, shrinkB=0))
    link((2.9, 1.85), (2.6, 1.85))                     # ⑦の左辺 → 右の頂点
    link((1.4, 1.25), (1.4, 0.3))                      # 下の頂点 → はい
    ax.text(1.55, 0.6, "はい：ほかの作業台・品目へ", fontsize=8.5)
    link((1.4, 2.45), (1.4, 3.0), ls="--")             # 上の頂点 → ①の下辺
    ax.text(1.52, 2.72, "いいえ：直して再試行", fontsize=8, ha="left", va="center")
    ax.text(5.6, 0.45, "灰色の箱＝同じ物差しで測る2回。導入前に測っておかないと、効果は示せない",
            fontsize=8.5, ha="left")
    save(fig, "fig7-1_pilot_flow.png")


# ---------------------------------------------------------------- 図7-2
def fig7_2():
    fig, ax = plt.subplots(figsize=(10, 4.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4.4)
    ax.set_axis_off()
    inputs = [(3.3, "BOM\n（部品と数量）"), (1.9, "寸法表\n（縦・横・高さ）"), (0.5, "手順書\n（工程の順番）")]
    for y, t in inputs:
        rbox(ax, 0.2, y, 2.0, 0.9, t, fc="0.92", fs=8.5)
        arrow(ax, 2.22, y + 0.45, 3.78, 2.35)
    ax.text(1.2, 3.18, "品番で手順書と突き合わせる", fontsize=7.5, ha="center", va="top")
    ax.text(1.2, 1.78, "欠けている寸法は実測で埋める", fontsize=7.5, ha="center", va="top")
    rbox(ax, 3.8, 1.75, 2.0, 1.2, "点検\n（コード7-1）", fs=9.5, lw=1.6, bold=True)
    rbox(ax, 7.2, 2.7, 2.6, 0.95, "部品箱の選択\n（第4章）", fs=9)
    rbox(ax, 7.2, 1.05, 2.6, 0.95, "トレイの配置\n（第5章）", fs=9)
    arrow(ax, 5.82, 2.55, 7.18, 3.15)
    arrow(ax, 5.82, 2.15, 7.18, 1.55)
    arrow(ax, 8.5, 2.68, 8.5, 2.02)
    ax.text(4.8, 1.35, "まちがいの疑いがある行は、\n直してから先へ進む", ha="center", va="top", fontsize=8)
    save(fig, "fig7-2_data_flow.png")


# ---------------------------------------------------------------- 図7-3
def fig7_3():
    kits = list(range(0, 13))
    std = [5.92 * k for k in kits]                 # 標準部品箱：1組 59,200円
    mold = [200 + 8 * k for k in kits]              # 成形トレイ：金型200万円＋トレイ4枚×2万円
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.plot(kits, std, color="black", lw=1.6, label="標準部品箱方式（1組あたり5.92万円）")
    ax.plot(kits, mold, color="black", lw=1.6, ls="--", label="成形トレイ方式（金型200万円＋1組あたり8万円）")
    ax.scatter([6, 6], [5.92 * 6, 200 + 48], color="black", zorder=3, s=25)
    ax.annotate("6組で約36万円", (6, 5.92 * 6), xytext=(8, 10), textcoords="offset points", fontsize=8.5)
    ax.annotate("6組で248万円", (6, 248), xytext=(8, -14), textcoords="offset points", fontsize=8.5)
    ax.set_xlabel("同時に用意するキットの組数")
    ax.set_ylabel("初期費用（万円、架空の価格）")
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 320)
    ax.set_xticks(kits)
    ax.grid(lw=0.3, color="0.85")
    ax.legend(fontsize=8, frameon=False, loc="upper left")
    save(fig, "fig7-3_cost.png")


# ---------------------------------------------------------------- 図7-4
def fig7_4():
    fig, ax = plt.subplots(figsize=(10.5, 4.2))
    ax.set_xlim(0, 10.5)
    ax.set_ylim(0, 4.4)
    ax.set_axis_off()
    ax.text(0.1, 4.1, "(a) 組立者が自分で集める", fontsize=10, fontweight="bold")
    xs = [0.2, 2.4, 5.6, 8.6]
    labels = ["注文", "組立者が\n部品を集める", "組立", "完成"]
    for i, (x, t) in enumerate(zip(xs, labels)):
        w = 1.4 if i in (0, 3) else 2.4
        rbox(ax, x, 2.75, w, 0.9, t, fs=8.5, fc="0.92" if i == 1 else "white")
    arrow(ax, 1.62, 3.2, 2.38, 3.2)
    arrow(ax, 4.82, 3.2, 5.58, 3.2)
    arrow(ax, 8.02, 3.2, 8.58, 3.2)
    ax.text(5.2, 3.75, "集め終わったらすぐ組む（待ちがない）", fontsize=8, ha="center")
    ax.text(0.1, 2.2, "(b) 専任者が集める", fontsize=10, fontweight="bold")
    xs = [0.2, 2.0, 5.6, 8.6]
    labels = ["注文", "専任者が\n部品を集める", "組立者（5人）\nが組む", "完成"]
    for i, (x, t) in enumerate(zip(xs, labels)):
        w = 1.4 if i in (0, 3) else 2.2
        rbox(ax, x, 0.85, w, 0.9, t, fs=8.5, fc="0.92" if i == 1 else "white")
    arrow(ax, 1.62, 1.3, 1.98, 1.3)
    arrow(ax, 4.22, 1.3, 4.45, 1.3)
    triangle(ax, 4.9, 1.12)
    ax.text(4.9, 0.55, "そろったカートの待ち\n（置き場は6台分）", fontsize=8, ha="center", va="top")
    arrow(ax, 5.25, 1.3, 5.58, 1.3)
    arrow(ax, 7.82, 1.3, 8.58, 1.3)
    ax.text(10.4, 0.2, "▲＝待ちのできる場所（在庫の記号）", fontsize=8, ha="right")
    save(fig, "fig7-4_who_picks.png")


# ---------------------------------------------------------------- 図7-5
def fig7_5():
    steps = [("① 変更を受け取る", "設計変更の通知、手順書の改訂", "生産技術"),
             ("② データを直す", "BOMを出し直し、新しい部品の寸法を測る", "生産技術"),
             ("③ 点検する", "コード7-1で入力を確かめる", "生産技術"),
             ("④ 配置を作る", "第5章のモデルを実行する", "モデルを回す人"),
             ("⑤ 前の版と比べる", "動いた部品箱の数を確かめる", "モデルを回す人"),
             ("⑥ 印刷して置き換える", "古いシートを回収し、新しいシートを貼る", "班長")]
    fig, ax = plt.subplots(figsize=(9.6, 6.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7.0)
    ax.set_axis_off()
    ax.text(7.95, 6.75, "担当（例）", fontsize=9, ha="center", fontweight="bold")
    for i, (t, d, who) in enumerate(steps):
        y = 5.9 - i * 1.1
        rbox(ax, 1.6, y, 5.0, 0.8, f"{t}\n{d}", fs=8.5, fc="0.92" if i == 3 else "white")
        ax.add_patch(plt.Rectangle((6.9, y), 2.1, 0.8, fill=False, ls=":", lw=0.9))
        ax.text(7.95, y + 0.4, who, ha="center", va="center", fontsize=8.5, color="0.3")
        if i < len(steps) - 1:
            arrow(ax, 4.1, y - 0.02, 4.1, y - 0.28)
    y4 = 5.9 - 3 * 1.1
    rbox(ax, 0.05, y4 + 1.6, 1.25, 0.8, "第4章へ戻り\n部品箱を\n見直す", fs=7.5, fc="0.85")
    ax.annotate("", xy=(0.68, y4 + 1.58), xytext=(1.58, y4 + 0.4),
                arrowprops=dict(arrowstyle="-|>", lw=1.0, ls="--", connectionstyle="arc3,rad=-0.3"))
    ax.text(0.15, y4 + 0.15, "今の部品箱に\n入らないとき", fontsize=7.5, va="top")
    ax.annotate("", xy=(1.58, y4 + 0.65), xytext=(0.68, y4 + 1.58),
                arrowprops=dict(arrowstyle="-|>", lw=1.0, ls="--", connectionstyle="arc3,rad=-0.3"))
    ax.text(5.0, 0.15, "担当の欄は自社で書き込む。誰が回すかを決めておかないと、配置はいつの間にか古くなる",
            fontsize=8.5, ha="center")
    save(fig, "fig7-5_change_flow.png")


# ---------------------------------------------------------------- 図7-6
def fig7_6():
    fig, ax = plt.subplots(figsize=(9.6, 4.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4.8)
    ax.set_axis_off()
    ax.text(1.6, 4.5, "第1章で挙げた問題", ha="center", fontsize=10, fontweight="bold")
    ax.text(8.2, 4.5, "測る指標（7.6節）", ha="center", fontsize=10, fontweight="bold")
    probs = ["部品を探す時間がかかる", "欠品に気づくのが遅い", "注文の波に合わせられない", "部品と棚が場所を取る"]
    inds = ["部品を探す時間", "欠品の件数", "組立のリードタイム", "必要な床面積"]
    py = [3.5, 2.5, 1.5, 0.5]
    for y, t in zip(py, probs):
        rbox(ax, 0.1, y, 3.0, 0.7, t, fc="0.92", fs=9)
    for y, t in zip(py, inds):
        rbox(ax, 6.9, y, 2.6, 0.7, t, fs=9)
    links = [(0, 0), (1, 1), (0, 2), (1, 2), (2, 2), (3, 3)]
    for p, i in links:
        ax.plot([3.12, 6.88], [py[p] + 0.35, py[i] + 0.35], color="black", lw=1.0,
                ls="-" if p == i else "--")
    ax.text(5.0, 0.1, "実線＝直接測る指標、破線＝結果として表れる指標", fontsize=8.5, ha="center")
    save(fig, "fig7-6_indicators.png")


# ---------------------------------------------------------------- 図7-7
def fig7_7():
    panels = [("欠品の件数（4週間）", [12, 3, 1], "件"),
              ("部品を探す時間（1台あたり）", [25, 10, 4], "分"),
              ("組立と部品集めの合計時間（1台あたり）", [3.6, 3.9, 3.5], "時間"),
              ("必要な床面積", [40, 34, 34], "m²")]
    fig, axes = plt.subplots(1, 4, figsize=(11, 3.2))
    labels = ["導入前", "1週目", "4週目"]
    styles = [dict(fc="0.85", hatch=None), dict(fc="white", hatch="///"), dict(fc="0.45", hatch=None)]
    for ax, (title, vals, unit) in zip(axes, panels):
        for i, (v, st) in enumerate(zip(vals, styles)):
            ax.bar(i, v, width=0.65, color=st["fc"], edgecolor="black", hatch=st["hatch"], lw=0.8)
            ax.text(i, v, f"{v}{unit}", ha="center", va="bottom", fontsize=8)
        ax.set_xticks(range(3))
        ax.set_xticklabels(labels, fontsize=8.5)
        ax.set_ylim(0, max(vals) * 1.25)
        ax.set_yticks([])
        for s in ("top", "right", "left"):
            ax.spines[s].set_visible(False)
        ax.set_title(title, fontsize=8.5)
    fig.suptitle("導入前後の比較の例（数字は架空）。1週目は慣れないので合計時間が増えるが、4週目には導入前より短くなる",
                 fontsize=9, y=1.03)
    fig.tight_layout()
    save(fig, "fig7-7_before_after.png")


if __name__ == "__main__":
    for f in (fig7_1, fig7_2, fig7_3, fig7_4, fig7_5, fig7_6, fig7_7):
        f()
