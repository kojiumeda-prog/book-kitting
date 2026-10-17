"""第7章 コード7-1：入力データの点検。

BOM（部品表）と部品寸法の表を読み込み、モデルに入れる前にまちがいを探す。
現場のデータには、寸法の抜け、単位の取り違え（mmとcm）、数量0、工程番号の抜けがよくある。

    python scripts/ch7_check.py                     # 例題データ（わざとまちがいを混ぜたもの）を作って点検する
    python scripts/ch7_check.py 自社のBOM.csv        # 自社のデータを点検する

CSVの列：bom, part_no, name, step, w_mm, l_mm, qty, hardware（1か0）
"""
import csv
import os
import sys

from _common import RESULTS
from kitting.bins import BinType, bins_needed
from kitting.data import Part, generate_portfolio

CH4_CHOSEN = [BinType(1, 1), BinType(2, 2), BinType(4, 3), BinType(8, 1)]   # 第4章で選んだ4種類


def make_sample(path):
    """例題：SA-03のBOMに、現場でよくあるまちがいを5つ混ぜたCSVを作る"""
    parts = generate_portfolio()["SA-03"]
    rows = [p.to_dict() for p in parts]
    rows[2]["w_mm"] = ""                    # 寸法の抜け
    rows[5]["l_mm"] = rows[5]["l_mm"] / 10  # cmで入力してしまった
    rows[8]["qty"] = 0                      # 数量0
    rows[11]["step"] = ""                   # 工程番号の抜け
    rows[14]["w_mm"], rows[14]["l_mm"] = 650, 700   # どの部品箱にも入らない大物（桁の打ちまちがい）
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["bom", "part_no", "name", "step", "w_mm", "l_mm", "qty", "hardware"],
                           extrasaction="ignore")
        w.writeheader()
        for r in rows:
            r["hardware"] = int(bool(r["hardware"]))
            w.writerow(r)
    return path


# ---- コード7-1 ここから ---------------------------------------------------
def check_rows(rows, bin_types, min_mm=5, max_mm=600):
    """1行ずつ確かめて、問題のある行を (行番号, 部品番号, 内容) のリストで返す"""
    problems = []
    seen = set()
    for i, r in enumerate(rows, start=2):                 # 2行目からがデータ
        pn = r.get("part_no", "")
        key = (r.get("bom"), pn, r.get("step"))
        if key in seen:
            problems.append((i, pn, "同じ部品が同じ工程に2回出てくる"))
        seen.add(key)
        if not str(r.get("step", "")).strip():
            problems.append((i, pn, "工程番号がない（作業順に並べられない）"))
        try:
            w, l, q = float(r["w_mm"]), float(r["l_mm"]), int(float(r["qty"]))
        except (ValueError, KeyError):
            problems.append((i, pn, "寸法か数量が空、または数字でない"))
            continue
        if q <= 0:
            problems.append((i, pn, f"数量が {q}"))
        for name, v in (("幅", w), ("長さ", l)):
            if v < min_mm:
                problems.append((i, pn, f"{name}が {v}mm と小さすぎる（cmで入力した？）"))
            if v > max_mm:
                problems.append((i, pn, f"{name}が {v}mm と大きすぎる（桁の打ちまちがい？）"))
        part = Part(r["bom"], pn, r.get("name", ""), 0, "", int(min(w, l)), int(max(w, l)),
                    max(q, 1), str(r.get("hardware")) == "1")
        if all(bins_needed(part, t) is None for t in bin_types):
            problems.append((i, pn, "どの部品箱にも入らない（大物として別に置くか、寸法を確かめる）"))
    return problems
# ---- コード7-1 ここまで ---------------------------------------------------


def main():
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = make_sample(os.path.join(RESULTS, "ch7_sample_bom.csv"))
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    problems = check_rows(rows, CH4_CHOSEN)
    print(f"{path}：{len(rows)}行を点検、問題 {len(problems)}件")
    for i, pn, msg in problems:
        print(f"  {i}行目 {pn}：{msg}")


if __name__ == "__main__":
    main()
