"""本書の全結果（results/ と figures/）を作り直す。

    python scripts/run_all.py           # 本の数値を再現（約30分）
    python scripts/run_all.py --quick   # 動作確認（数分）
"""
import subprocess
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))
quick = "--quick" in sys.argv
q = ["--quick"] if quick else []
steps = [
    ["check_env.py"],                              # 付録A：環境の確認
    ["ch2_count.py", *([] if quick else ["--six"])], ["ch2_figures.py"],   # 第2章
    ["ch3_rule.py"], ["ch3_figures.py"],           # 第3章
    ["ch4_sizing.py"], ["ch4_figures.py"], ["ch4_excel.py"],               # 第4章
    ["ch5_layout.py", *q],                         # 第5章
    *([] if quick else [["scale_test.py"]]),       # 第5章5.8節（約8分）
    ["ch5_figures.py"],
    ["ch1_figures.py"],                            # 図1-5は第5章の配置を使う
    ["ch6_tradeoff.py", *q],                       # 第6章（約20分。--quick なら数分）
    ["ch6_figures.py"], ["ch6_concept_figures.py"],
    ["ch7_check.py"], ["ch7_figures.py"],          # 第7章
    ["ch8_figures.py"],                            # 第8章（配車とシフトの例も解く）
    ["front_figures.py"],                          # はじめに：図0-1
]
for s in steps:
    print(f"\n=== {' '.join(s)} ===", flush=True)
    subprocess.run([sys.executable, os.path.join(HERE, s[0]), *s[1:]], check=True)
