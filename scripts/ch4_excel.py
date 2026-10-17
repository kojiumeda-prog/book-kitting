"""第4章 4.6節：Excelのソルバー（シンプレックスLP）で解けるシートを作る（図4-8用）。

SA-01（部品17点）、寸法候補8種類、K=3。変数144個・制約26個で、Excel標準ソルバーの上限
（変数200・制約100）に収まる。ソルバーの設定はブックに保存してあるので、
[データ]→[ソルバー]を開くと目的セル・変数セル・制約が入った状態で表示される。

    python scripts/ch4_excel.py      # results/ch4_solver_SA01.xlsx を作り、PuLPで同じ問題を解いて答えを確かめる
"""
import os

import pulp
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.workbook.defined_name import DefinedName

from _common import RESULTS
from kitting.bins import BinType, bins_needed
from kitting.data import generate_portfolio

BOM = "SA-01"
K = 3
CAND = [BinType(*t) for t in [(1, 1), (2, 1), (2, 2), (3, 1), (3, 2), (4, 2), (4, 3), (4, 4)]]
BIG = 1000          # 入らない組合せのコスト（選ばれないように大きくする）
SHEET = "モデル"

thin = Side(style="thin", color="999999")
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
HEAD = PatternFill("solid", fgColor="DDDDDD")
VAR = PatternFill("solid", fgColor="FFF2CC")      # 変数セル（淡い黄色）
OBJ = PatternFill("solid", fgColor="CCCCCC")


def col(j):  # 0始まりの候補番号 → 列記号（E列から）
    return "EFGHIJKLMNOP"[j]


def build(parts):
    wb = Workbook()
    ws = wb.active
    ws.title = SHEET
    calc = wb.create_sheet("計算用")
    n_p, n_k = len(parts), len(CAND)
    last = col(n_k - 1)                       # L
    sumc = col(n_k)                           # M

    r_n0 = 9                                  # 必要部品箱数 n の表（データの1行目）
    r_x0 = r_n0 + n_p + 3                     # x の表
    r_y = r_x0 + n_p + 1                      # y の行
    r_cnt, r_cap = r_y + 1, r_y + 2

    def label(r, text, bold=False):
        ws.merge_cells(f"A{r}:D{r}")
        ws[f"A{r}"] = text
        ws[f"A{r}"].font = Font(bold=bold)

    ws["A1"] = f"部品箱の寸法を選ぶ（{BOM}、寸法候補{n_k}種類）― Excelソルバー版"
    ws["A1"].font = Font(bold=True, size=13)
    label(3, "採用する種類数 K")
    ws["E3"] = K
    label(4, "必要面積［目的セル・最小化］", bold=True)
    obj = "$E$4"
    ws["E4"] = f"=SUMPRODUCT('計算用'!E{r_n0}:{last}{r_n0 + n_p - 1},E{r_x0}:{last}{r_x0 + n_p - 1})"
    ws["E4"].fill = OBJ
    for c in ("E3", "E4"):
        ws[c].border = BOX
        ws[c].font = Font(bold=True)
        ws[c].alignment = Alignment(horizontal="center")
    label(5, "部品箱1個の面積（ブロック）")
    for j, k in enumerate(CAND):
        ws[f"{col(j)}5"] = k.area

    # 表1：必要部品箱数 n
    ws[f"A{r_n0 - 2}"] = "① 必要な部品箱の数 n（前計算。空欄＝入らない）"
    ws[f"A{r_n0 - 2}"].font = Font(bold=True)
    for j, h in enumerate(["部品番号", "部品名", "寸法(mm)", "数量"]):
        ws.cell(row=r_n0 - 1, column=j + 1, value=h)
    for j, k in enumerate(CAND):
        ws[f"{col(j)}{r_n0 - 1}"] = k.name
    for i, p in enumerate(parts):
        r = r_n0 + i
        ws.cell(row=r, column=1, value=p.part_no)
        ws.cell(row=r, column=2, value=p.name)
        ws.cell(row=r, column=3, value=f"{p.w_mm}×{p.l_mm}")
        ws.cell(row=r, column=4, value=p.qty)
        for j, k in enumerate(CAND):
            ws[f"{col(j)}{r}"] = bins_needed(p, k)
            # 計算用シート：コスト＝面積×n（入らなければ大きな値）
            calc[f"{col(j)}{r}"] = (f"=IF(ISBLANK('{SHEET}'!{col(j)}{r}),{BIG},"
                                    f"'{SHEET}'!{col(j)}$5*'{SHEET}'!{col(j)}{r})")

    # 表2：変数 x
    ws[f"A{r_x0 - 2}"] = "② x：部品をその寸法の部品箱に入れるか（0/1、変数セル）"
    ws[f"A{r_x0 - 2}"].font = Font(bold=True)
    for j, h in enumerate(["部品番号", "部品名", "寸法(mm)", "数量"]):
        ws.cell(row=r_x0 - 1, column=j + 1, value=h)
    for j, k in enumerate(CAND):
        ws[f"{col(j)}{r_x0 - 1}"] = k.name
    ws[f"{sumc}{r_x0 - 1}"] = "合計＝1"
    for i, p in enumerate(parts):
        r = r_x0 + i
        ws.cell(row=r, column=1, value=p.part_no)
        ws.cell(row=r, column=2, value=p.name)
        ws.cell(row=r, column=3, value=f"{p.w_mm}×{p.l_mm}")
        ws.cell(row=r, column=4, value=p.qty)
        for j in range(n_k):
            ws[f"{col(j)}{r}"] = 0
            ws[f"{col(j)}{r}"].fill = VAR
        ws[f"{sumc}{r}"] = f"=SUM(E{r}:{last}{r})"

    # y と、まとめて書いた x ≦ y
    label(r_y, "③ y：その寸法を採用するか（0/1、変数セル）", bold=True)
    label(r_cnt, "その寸法に入れた部品の数")
    label(r_cap, f"≦ 部品の総数（{n_p}）× y")
    for j in range(n_k):
        c = col(j)
        ws[f"{c}{r_y}"] = 0
        ws[f"{c}{r_y}"].fill = VAR
        ws[f"{c}{r_cnt}"] = f"=SUM({c}{r_x0}:{c}{r_x0 + n_p - 1})"
        ws[f"{c}{r_cap}"] = f"={n_p}*{c}{r_y}"
    ws[f"{sumc}{r_y}"] = f"=SUM(E{r_y}:{last}{r_y})"
    ws[f"{col(n_k + 1)}{r_y}"] = "≦ K"

    # 体裁
    for r in (r_n0 - 1, r_x0 - 1):
        for cc in range(1, 6 + n_k):
            c = ws.cell(row=r, column=cc)
            if c.value is not None:
                c.fill, c.font = HEAD, Font(bold=True)
    blocks = [(5, 5, 5), (r_n0 - 1, r_n0 + n_p - 1, 1), (r_x0 - 1, r_x0 + n_p - 1, 1), (r_y, r_cap, 5)]
    for r1, r2, c1 in blocks:
        c2 = 4 + n_k + (1 if r1 in (r_x0 - 1, r_y) else 0)
        for row in ws.iter_rows(min_row=r1, max_row=r2, min_col=c1, max_col=c2):
            for c in row:
                c.border = BOX
                if c.column >= 3:
                    c.alignment = Alignment(horizontal="center")
    for c, w in zip("ABCD", (10, 10, 9, 5)):
        ws.column_dimensions[c].width = w
    for j in range(n_k + 2):
        ws.column_dimensions[col(j)].width = 8.5
    calc.sheet_state = "hidden"

    # ソルバーの設定をブックに保存する（[データ]→[ソルバー]で読み込まれる）
    q = f"'{SHEET}'!"
    xs = f"$E${r_x0}:${last}${r_x0 + n_p - 1}"
    ys = f"$E${r_y}:${last}${r_y}"
    names = {
        "solver_opt": q + obj,
        "solver_typ": "2",                     # 最小化
        "solver_val": "0",
        "solver_adj": f"{q}{xs},{q}{ys}",
        "solver_eng": "2",                     # シンプレックスLP
        "solver_neg": "1",                     # 制約のない変数を非負にする
        "solver_ver": "3",
        "solver_rlx": "2",                     # 整数条件を無視しない（1だと「整数制約を無視する」がオンになる）
        "solver_tol": "0",                     # 整数最適性 0%（最適解まで探す）
        "solver_num": "5",
        # 1) 各部品はちょうど1種類（行の合計＝1）
        "solver_lhs1": f"{q}${sumc}${r_x0}:${sumc}${r_x0 + n_p - 1}", "solver_rel1": "2", "solver_rhs1": "1",
        # 2) 入れた部品の数 ≦ 部品の総数 × y（x≦y をまとめた形）
        "solver_lhs2": f"{q}$E${r_cnt}:${last}${r_cnt}", "solver_rel2": "1",
        "solver_rhs2": f"{q}$E${r_cap}:${last}${r_cap}",
        # 3) 採用する種類は K 以下
        "solver_lhs3": f"{q}${sumc}${r_y}", "solver_rel3": "1", "solver_rhs3": f"{q}$C$3",
        # 4)・5) x と y はバイナリ
        "solver_lhs4": q + xs, "solver_rel4": "5", "solver_rhs4": '"binary"',
        "solver_lhs5": q + ys, "solver_rel5": "5", "solver_rhs5": '"binary"',
    }
    for k, v in names.items():
        ws.defined_names[k] = DefinedName(k, attr_text=v, hidden=True)

    n_vars = n_p * n_k + n_k
    n_cons = n_p + n_k + 1
    note = r_cap + 2
    ws[f"A{note}"] = (f"変数 {n_vars} 個（x {n_p}×{n_k}＋y {n_k}）、制約 {n_cons} 個（整数条件を除く）。"
                      "[データ]→[ソルバー]を開き、[解決]を押す。")
    return wb, n_vars, n_cons


def check(parts):
    """同じ問題をPuLPで解き、Excelで出るはずの答えを表示する"""
    prob = pulp.LpProblem("excel_check", pulp.LpMinimize)
    y = {k: pulp.LpVariable(f"y_{k.name}", cat="Binary") for k in CAND}
    x = {(p.part_no, k): pulp.LpVariable(f"x_{p.part_no}_{k.name}", cat="Binary") for p in parts for k in CAND}
    cost = {(p.part_no, k): (BIG if (n := bins_needed(p, k)) is None else k.area * n) for p in parts for k in CAND}
    prob += pulp.lpSum(cost[i] * x[i] for i in x)
    for p in parts:
        prob += pulp.lpSum(x[p.part_no, k] for k in CAND) == 1
    for k in CAND:
        prob += pulp.lpSum(x[p.part_no, k] for p in parts) <= len(parts) * y[k]
    prob += pulp.lpSum(y.values()) <= K
    prob.solve(pulp.PULP_CBC_CMD(msg=False, threads=1))
    chosen = [k.name for k in CAND if y[k].value() > 0.5]
    return pulp.value(prob.objective), chosen


def main():
    parts = generate_portfolio()[BOM]
    wb, nv, nc = build(parts)
    path = os.path.join(RESULTS, "ch4_solver_SA01.xlsx")
    wb.save(path)
    val, chosen = check(parts)
    print(f"saved {path}  変数{nv}個・制約{nc}個")
    print(f"答え（PuLPで確認）：必要面積 {val:.0f} ブロック、採用 {chosen}")


if __name__ == "__main__":
    main()
