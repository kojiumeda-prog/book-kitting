"""本書の全結果（results/ と figures/）を作り直す。

    python scripts/run_all.py           # 本の数値を再現（30〜40分）
    python scripts/run_all.py --quick   # 動作確認（数分）
"""
import subprocess
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))
quick = ["--quick"] if "--quick" in sys.argv else []
steps = [["check_env.py"], ["ch2_count.py", *([] if quick else ["--six"])], ["ch2_figures.py"], ["ch3_rule.py"], ["ch3_figures.py"], ["ch4_sizing.py"], ["ch4_figures.py"], ["ch4_excel.py"], ["ch5_layout.py", *quick]]
if not quick:
    steps.append(["scale_test.py"])
steps.append(["ch5_figures.py"])
steps.append(["ch1_figures.py"])   # 図1-5は第5章の配置を使う     # scale_test.csv がないときは、先に scale_test.py を実行する
steps.append(["ch6_tradeoff.py", *quick])   # 第6章（20分前後。--quick なら数分）
steps.append(["ch6_figures.py"])
steps.append(["ch6_concept_figures.py"])
steps.append(["ch7_check.py"])
steps.append(["ch7_figures.py"])
for s in steps:
    print(f"\n=== {' '.join(s)} ===", flush=True)
    subprocess.run([sys.executable, os.path.join(HERE, s[0]), *s[1:]], check=True)
