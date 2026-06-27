"""
Shared funnel arithmetic for counterfactuals and tests.
Sequential model: diagnoses = n_pcp * c_pr * c_rs * c_sd
(where c_* are conversion rates between adjacent stages after PCP).
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


def funnel_csv_path(project_root: Path) -> Path:
    return project_root / "outputs" / "analytics" / "funnel metrics.csv"


def load_funnel_metrics(project_root: Path) -> dict[str, Any]:
    path = funnel_csv_path(project_root)
    with path.open(newline="", encoding="utf-8") as f:
        row = next(csv.DictReader(f))
    return {
        "symptom": int(row["symptom"]),
        "pcp": int(row["pcp"]),
        "referral": int(row["referral"]),
        "specialist": int(row["specialist"]),
        "diagnosis": int(row["diagnosis"]),
        "symptom_to_pcp_conversion": float(row["symptom_to_pcp_conversion"]),
        "pcp_to_referral_conversion": float(row["pcp_to_referral_conversion"]),
        "referral_to_specialist_conversion": float(row["referral_to_specialist_conversion"]),
        "specialist_to_diagnosis_conversion": float(row["specialist_to_diagnosis_conversion"]),
    }


def modeled_diagnoses(
    n_pcp: int,
    c_pr: float,
    c_rs: float,
    c_sd: float,
) -> float:
    """Expected diagnosis count from referral onward (matches compute_counterfactuals)."""
    return n_pcp * c_pr * c_rs * c_sd


def conversions_from_counts(f: dict[str, Any]) -> dict[str, float]:
    """Hand-check: conversion rates implied by integer stage counts."""
    s, p, r, sp, d = f["symptom"], f["pcp"], f["referral"], f["specialist"], f["diagnosis"]
    return {
        "symptom_to_pcp": p / s if s else 0.0,
        "pcp_to_referral": r / p if p else 0.0,
        "referral_to_specialist": sp / r if r else 0.0,
        "specialist_to_diagnosis": d / sp if sp else 0.0,
    }
