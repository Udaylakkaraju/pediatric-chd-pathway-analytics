"""Checks that published CSV outputs match the cleaned mart."""

from __future__ import annotations

import pandas as pd
import pytest


def test_stage_delay_export_matches_mart(project_root):
    mart = pd.read_csv(project_root / "data" / "marts" / "cleaned" / "mart_delay_scored_cleaned.csv")
    exported = pd.read_csv(project_root / "outputs" / "analytics" / "stage_delay_contribution.csv").iloc[0]

    checks = {
        "symptom_to_pcp": "days_symptom_to_pcp_clean",
        "pcp_to_referral": "days_pcp_to_referral_clean",
        "referral_to_specialist": "days_referral_to_specialist_clean",
        "specialist_to_diagnosis": "days_specialist_to_diagnosis_clean",
    }
    for exported_col, mart_col in checks.items():
        expected = round(pd.to_numeric(mart[mart_col], errors="coerce").mean(), 2)
        assert float(exported[exported_col]) == pytest.approx(expected, abs=0.01)


def test_chd_type_funnel_rates_are_valid(project_root):
    path = project_root / "sql" / "results" / "13_chd_type_funnel_breakdown_result.csv"
    if not path.exists():
        pytest.skip("regenerate with scripts/run_sql_queries.py")
    df = pd.read_csv(path)
    rate_cols = [col for col in df.columns if col.startswith("pct_") or col.endswith("_rate_pct")]
    for col in rate_cols:
        values = pd.to_numeric(df[col], errors="coerce").dropna()
        assert (values >= 0).all()
        assert (values <= 100).all()


def test_excel_patient_detail_has_plain_language_fields(project_root):
    path = project_root / "outputs" / "excel_data" / "patient_pathway_detail.csv"
    if not path.exists():
        pytest.skip("regenerate with scripts/build_core_analytics_outputs.py")
    df = pd.read_csv(path, nrows=5)
    expected = {
        "pathway_status",
        "referral_priority",
        "authorization_status",
        "specialist_appointment_status",
        "distance_to_specialist_miles",
    }
    assert expected.issubset(df.columns)
