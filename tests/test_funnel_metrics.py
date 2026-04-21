"""Funnel counts and implied conversions match funnel metrics export."""

from __future__ import annotations

import pytest

from chd_analytics.funnel_math import conversions_from_counts, load_funnel_metrics


def test_funnel_counts_positive(project_root):
    f = load_funnel_metrics(project_root)
    assert f["symptom"] == 4969
    assert f["diagnosis"] == 1042
    assert f["symptom"] >= f["pcp"] >= f["referral"] >= f["specialist"] >= f["diagnosis"]


def test_implied_conversions_match_export(project_root):
    """Export rounds conversions (e.g. 4 decimals); exact ratios live in stage counts."""
    f = load_funnel_metrics(project_root)
    implied = conversions_from_counts(f)
    assert implied["symptom_to_pcp"] == pytest.approx(f["symptom_to_pcp_conversion"], rel=1e-4)
    assert implied["pcp_to_referral"] == pytest.approx(f["pcp_to_referral_conversion"], rel=1e-4)
    assert implied["referral_to_specialist"] == pytest.approx(f["referral_to_specialist_conversion"], rel=1e-4)
    assert implied["specialist_to_diagnosis"] == pytest.approx(f["specialist_to_diagnosis_conversion"], rel=1e-4)


def test_modeled_diagnoses_chain(project_root):
    """Rounded conversion floats reproduce diagnosis count within small drift."""
    f = load_funnel_metrics(project_root)
    chain = (
        f["pcp"]
        * f["pcp_to_referral_conversion"]
        * f["referral_to_specialist_conversion"]
        * f["specialist_to_diagnosis_conversion"]
    )
    assert chain == pytest.approx(f["diagnosis"], abs=1.0)


def test_counts_imply_diagnosis_exact(project_root):
    """Integer stage counts are internally consistent: multiply ratios → diagnosis."""
    f = load_funnel_metrics(project_root)
    p, r, sp, dx = f["pcp"], f["referral"], f["specialist"], f["diagnosis"]
    assert p * (r / p) * (sp / r) * (dx / sp) == dx
