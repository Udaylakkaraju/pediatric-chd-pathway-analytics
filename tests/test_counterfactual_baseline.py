"""Counterfactual baseline matches funnel diagnosis count."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from chd_analytics.funnel_math import load_funnel_metrics, modeled_diagnoses


def test_baseline_matches_funnel_diagnosis(project_root):
    f = load_funnel_metrics(project_root)
    dx = modeled_diagnoses(
        f["pcp"],
        f["pcp_to_referral_conversion"],
        f["referral_to_specialist_conversion"],
        f["specialist_to_diagnosis_conversion"],
    )
    assert dx == pytest.approx(f["diagnosis"], abs=1.0)


def test_exported_csv_baseline_row(project_root):
    path = project_root / "outputs" / "analytics" / "recommendations_counterfactuals.csv"
    if not path.exists():
        pytest.skip("regenerate with compute_counterfactuals.py")
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    base = next(r for r in rows if "baseline" in r["scenario"].lower())
    funnel = load_funnel_metrics(project_root)
    assert float(base["modeled_diagnoses"]) == pytest.approx(funnel["diagnosis"], abs=1.0)
