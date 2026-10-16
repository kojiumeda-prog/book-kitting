"""本書の全結果（results/ と figures/）を作り直す。

    python scripts/run_all.py           # 本の数値を再現（10分前後）
    python scripts/run_all.py --quick   # 動作確認（数分）
"""
import subprocess
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))
quick = ["--quick"] if "--quick" in sys.argv else []
steps = [["ch3_rule.py"], ["ch4_sizing.py"], ["ch5_layout.py", *quick]]
if not quick:
    steps.append(["scale_test.py"])
for s in steps:
    print(f"\n=== {' '.join(s)} ===", flush=True)
    subprocess.run([sys.executable, os.path.join(HERE, s[0]), *s[1:]], check=True)
