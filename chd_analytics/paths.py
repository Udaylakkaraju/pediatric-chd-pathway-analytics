"""Project root and data/output paths (single source of truth)."""

from __future__ import annotations

from pathlib import Path

# Package lives in ./chd_analytics/; project root is parent
ROOT = Path(__file__).resolve().parent.parent

ANALYTICS = ROOT / "outputs" / "analytics"
TABLES = ROOT / "data" / "raw"
MART_CLEANED = ROOT / "data" / "marts" / "cleaned" / "mart_delay_scored_cleaned.csv"
REFERRALS = TABLES / "referrals.csv"
PROCEDURES = TABLES / "procedures.csv"
PATIENTS = TABLES / "patients(Main Table).csv"

# Canonical column names (cleaned mart CSV)
COLS = {
    "patient_id": "patient_id",
    "symptom_date": "symptom_onset_date",
    "pcp_date": "first_pcp_date",
    "referral_date": "referral_date",
    "specialist_date": "specialist_date",
    "diagnosis_date": "diagnosis_date",
    "intervention_date": "intervention_date",
    "symptom_to_pcp": "days_symptom_to_pcp_clean",
    "pcp_to_referral": "days_pcp_to_referral_clean",
    "referral_to_specialist": "days_referral_to_specialist_clean",
    "specialist_to_diagnosis": "days_specialist_to_diagnosis_clean",
    "diagnosis_to_intervention": "days_diagnosis_to_intervention_clean",
    "delay_score": "delay_severity_score_clean",
}

INTERVAL_COLS = [
    COLS["symptom_to_pcp"],
    COLS["pcp_to_referral"],
    COLS["referral_to_specialist"],
    COLS["specialist_to_diagnosis"],
    COLS["diagnosis_to_intervention"],
]

DATE_COLS = [
    COLS["symptom_date"],
    COLS["pcp_date"],
    COLS["referral_date"],
    COLS["specialist_date"],
    COLS["diagnosis_date"],
    COLS["intervention_date"],
]
