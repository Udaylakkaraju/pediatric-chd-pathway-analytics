"""Coordination scorecard conversion rates align with funnel metrics."""

from __future__ import annotations

import csv

import pytest


def test_scorecard_matches_funnel(project_root):
    funnel_path = project_root / "outputs" / "analytics" / "funnel metrics.csv"
    score_path = project_root / "outputs" / "analytics" / "coordination_failure_scorecard.csv"
    if not score_path.exists():
        pytest.skip("regenerate with build_coordination_scorecard.py")

    with funnel_path.open(newline="", encoding="utf-8") as fh:
        f = next(csv.DictReader(fh))
    pcp = int(f["pcp"])
    sym = int(f["symptom"])
    ref = int(f["referral"])
    spec = int(f["specialist"])
    dx = int(f["diagnosis"])
    expected = [pcp / sym, ref / pcp, spec / ref, dx / spec]

    with score_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = sorted(
            [r for r in reader if str(r.get("stage_order", "")).strip().isdigit()],
            key=lambda r: int(r["stage_order"]),
        )
    assert len(rows) == 4
    for r, exp in zip(rows, expected, strict=True):
        # Scorecard may round to 3–4 decimals; compare to exact ratio with tolerance
        assert float(r["conversion_rate"]) == pytest.approx(exp, rel=1e-4)
