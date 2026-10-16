"""動作確認テスト（数十秒）。   python -m pytest -q"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kitting.bins import BinType, assign_smallest, bins_needed
from kitting.config import CANDIDATE_BINS, THESIS_BINS
from kitting.data import COMPLEX_BOM, generate_portfolio
from kitting.evaluate import check_feasible, evaluate
from kitting.layout import improve_lns, layout_rule, make_bins
from kitting.sizing import solve_sizing


def test_data_is_reproducible():
    a, b = generate_portfolio(), generate_portfolio()
    assert a == b
    assert len(a[COMPLEX_BOM]) >= 100


def test_every_part_fits_some_candidate():
    cand = [BinType(*t) for t in CANDIDATE_BINS]
    for parts in generate_portfolio().values():
        for p in parts:
            assert any(bins_needed(p, t) for t in cand)


def test_sizing_small():
    boms = {k: v for k, v in list(generate_portfolio().items())[:3]}
    r = solve_sizing(boms, [BinType(*t) for t in CANDIDATE_BINS], K=3, objective="worst")
    assert r.status == "Optimal" and len(r.chosen) <= 3


def test_layouts_are_feasible_and_lns_is_deterministic():
    boms = generate_portfolio()
    parts = boms["SA-03"]
    assign, bulk = assign_smallest(parts, [BinType(*t) for t in CANDIDATE_BINS])
    assert not bulk
    bins = make_bins(parts, assign)
    for order in ("size", "step"):
        check_feasible(bins, layout_rule(bins, order))
    init = layout_rule(bins, "step")
    nt = max(p.tray for p in init.values()) + 1
    r1, o1, _ = improve_lns(bins, init, nt, passes=1, det_time=0.5, log=None)
    r2, o2, _ = improve_lns(bins, init, nt, passes=1, det_time=0.5, log=None)
    check_feasible(bins, r1)
    assert o1 == o2 and {k: vars(v) for k, v in r1.items()} == {k: vars(v) for k, v in r2.items()}
    assert evaluate(bins, r1)["trays"] == nt
