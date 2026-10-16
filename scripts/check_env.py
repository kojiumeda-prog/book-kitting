"""付録A コードA-1：動作環境の確認。

    python scripts/check_env.py

Python とライブラリの版を表示し、CP-SAT と CBC で小さな問題が解けるかを確かめる。
"""
import platform
import sys


# ---- コードA-1 ここから ---------------------------------------------------
def main():
    print("Python     :", platform.python_version())
    ok = True
    try:
        import ortools
        from ortools.sat.python import cp_model
        print("OR-Tools   :", ortools.__version__)
        m = cp_model.CpModel()                     # x + y = 3、x - y = 1 を解く
        x, y = m.NewIntVar(0, 9, "x"), m.NewIntVar(0, 9, "y")
        m.Add(x + y == 3)
        m.Add(x - y == 1)
        s = cp_model.CpSolver()
        assert s.Solve(m) == cp_model.OPTIMAL and (s.Value(x), s.Value(y)) == (2, 1)
        print("  CP-SAT   : OK")
    except Exception as e:                          # 入っていない、または動かない
        ok = False
        print("  CP-SAT   : NG", e)
    try:
        import pulp
        print("PuLP       :", pulp.__version__)
        p = pulp.LpProblem("check", pulp.LpMaximize)
        a = pulp.LpVariable("a", 0, 4, cat="Integer")
        p += a
        p.solve(pulp.PULP_CBC_CMD(msg=False))
        assert pulp.value(a) == 4
        print("  CBC      : OK")
    except Exception as e:
        ok = False
        print("  CBC      : NG", e)
    try:
        import matplotlib
        print("matplotlib :", matplotlib.__version__)
    except ImportError:
        ok = False
        print("matplotlib : NG（図を作るときに必要）")
    print("すべて動きます。" if ok else "NG の行を確かめてください（付録Aを参照）。")
    return 0 if ok else 1
# ---- コードA-1 ここまで ---------------------------------------------------


if __name__ == "__main__":
    sys.exit(main())
