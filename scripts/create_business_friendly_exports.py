"""
Create business-friendly copies of analytics outputs:
- simpler file names
- plain-language column names

Outputs are written to: outputs/business_ready/
"""

from __future__ import annotations

import _bootstrap_path  # noqa: F401
from pathlib import Path

import pandas as pd

from chd_analytics.paths import ANALYTICS, ROOT

OUT_DIR = ROOT / "outputs" / "business_ready"


def _write(src_name: str, dst_name: str, col_map: dict[str, str]) -> None:
    src = ANALYTICS / src_name
    if not src.exists():
        return
    df = pd.read_csv(src)
    keep = [c for c in col_map.keys() if c in df.columns]
    out = df[keep].rename(columns={k: v for k, v in col_map.items() if k in keep})
    out.to_csv(OUT_DIR / dst_name, index=False)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    _write(
        "funnel metrics.csv",
        "patient_pathway_summary.csv",
        {
            "symptom": "patients_with_symptoms",
            "pcp": "patients_seen_in_primary_care",
            "referral": "patients_with_referral",
            "specialist": "patients_seen_by_specialist",
            "diagnosis": "patients_with_diagnosis",
            "symptom_to_pcp_conversion": "symptom_to_primary_care_rate",
            "pcp_to_referral_conversion": "primary_care_to_referral_rate",
            "referral_to_specialist_conversion": "referral_to_specialist_rate",
            "specialist_to_diagnosis_conversion": "specialist_to_diagnosis_rate",
        },
    )

    _write(
        "stage dropoff.csv",
        "stage_loss_rates.csv",
        {
            "stage": "pathway_step",
            "drop_off_rate": "share_lost_before_next_step",
        },
    )

    _write(
        "stage delay contribution.csv",
        "average_wait_by_stage.csv",
        {
            "symptom_to_pcp": "avg_days_symptom_to_primary_care",
            "pcp_to_referral": "avg_days_primary_care_to_referral",
            "referral_to_specialist": "avg_days_referral_to_specialist",
            "specialist_to_diagnosis": "avg_days_specialist_to_diagnosis",
        },
    )

    _write(
        "insurance analysis.csv",
        "payer_comparison.csv",
        {
            "insurance_type": "payer_type",
            "total_patients": "patients",
            "avg_delay": "average_delay_score",
            "diagnosis_rate": "diagnosis_rate",
        },
    )

    _write(
        "coordination_failure_scorecard.csv",
        "stage_leakage_and_waits.csv",
        {
            "stage_order": "stage_order",
            "stage_transition": "pathway_transition",
            "patients_at_stage_entry": "patients_entering_step",
            "patients_converting_to_next": "patients_moving_to_next_step",
            "conversion_rate": "conversion_rate",
            "drop_off_rate": "drop_off_rate",
            "avg_days_among_converters": "average_wait_days",
            "median_days_among_converters": "median_wait_days",
            "n_patients_used_for_median": "patients_used_for_wait_median",
        },
    )

    _write(
        "trend_by_month.csv",
        "monthly_pathway_trends.csv",
        {
            "symptom_index_month": "month_of_first_symptom",
            "cohort_n": "patients_in_monthly_cohort",
            "diagnosed_n": "patients_with_diagnosis",
            "diagnosis_rate": "diagnosis_rate",
            "mean_delay_score": "average_delay_score",
            "median_delay_score": "median_delay_score",
            "interpretation_note": "note",
        },
    )

    _write(
        "recommendations_counterfactuals.csv",
        "scenario_impact_estimates.csv",
        {
            "scenario": "scenario_name",
            "modeled_diagnoses": "estimated_diagnoses",
            "extra_diagnoses_vs_baseline": "additional_diagnoses_vs_today",
            "pct_symptom_cohort_reaching_diagnosis": "estimated_pathway_completion_percent",
            "pct_increase_in_diagnoses_vs_baseline": "percent_increase_in_diagnoses",
        },
    )

    _write(
        "QC_Report.csv",
        "data_health_report.csv",
        {
            "category": "check_group",
            "check_name": "check_name",
            "metric_value": "value",
            "detail": "description",
        },
    )

    print(f"Wrote business-friendly outputs to {OUT_DIR}")


if __name__ == "__main__":
    main()
