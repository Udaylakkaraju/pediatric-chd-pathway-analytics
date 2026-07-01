"""
Create business-friendly copies of analytics outputs:
- simpler file names
- plain-language column names

Also writes outputs/business_ready/website_metrics.json, a small JSON payload
of headline metrics for use on an external portfolio site (e.g. GitHub Pages).

Outputs are written to: outputs/business_ready/
"""

from __future__ import annotations

import _bootstrap_path  # noqa: F401
import json

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
        "funnel_metrics.csv",
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
        "stage_dropoff.csv",
        "stage_loss_rates.csv",
        {
            "stage": "pathway_step",
            "drop_off_rate": "share_lost_before_next_step",
        },
    )

    _write(
        "stage_delay_contribution.csv",
        "average_wait_by_stage.csv",
        {
            "symptom_to_pcp": "avg_days_symptom_to_primary_care",
            "pcp_to_referral": "avg_days_primary_care_to_referral",
            "referral_to_specialist": "avg_days_referral_to_specialist",
            "specialist_to_diagnosis": "avg_days_specialist_to_diagnosis",
        },
    )

    _write(
        "insurance_analysis.csv",
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

    # Website metrics payload (simple JSON for GitHub Pages fetch)
    funnel_path = ANALYTICS / "funnel_metrics.csv"
    dropoff_path = ANALYTICS / "stage_dropoff.csv"
    scenario_path = ANALYTICS / "recommendations_counterfactuals.csv"
    trend_path = ANALYTICS / "trend_by_month.csv"

    website_metrics: dict[str, object] = {
        "project_name": "Pediatric CHD Pathway Analytics",
        "subtitle": "Congenital heart diagnosis delay and care coordination analysis",
    }

    if funnel_path.exists():
        f = pd.read_csv(funnel_path).iloc[0]
        symptom = int(f["symptom"])
        diagnosis = int(f["diagnosis"])
        diagnosis_rate = (diagnosis / symptom) if symptom else 0.0
        website_metrics.update(
            {
                "patients_total": symptom,
                "patients_diagnosed": diagnosis,
                "diagnosis_rate": round(diagnosis_rate, 4),
            }
        )

    if dropoff_path.exists():
        d = pd.read_csv(dropoff_path)
        drop_map = {
            row["stage"]: float(row["drop_off_rate"])
            for _, row in d.iterrows()
            if "stage" in d.columns and "drop_off_rate" in d.columns
        }
        website_metrics.update(
            {
                "dropoff_primary_care_to_referral": round(
                    drop_map.get("PCP -> Referral", 0.0), 4
                ),
                "dropoff_specialist_to_diagnosis": round(
                    drop_map.get("Specialist -> Diagnosis", 0.0), 4
                ),
            }
        )

    if scenario_path.exists():
        s = pd.read_csv(scenario_path)
        if "extra_diagnoses_vs_baseline" in s.columns and len(s) > 0:
            best = float(s["extra_diagnoses_vs_baseline"].max())
            website_metrics["best_case_additional_diagnoses"] = round(best, 1)

    if trend_path.exists():
        t = pd.read_csv(trend_path)
        if len(t) >= 2:
            website_metrics["trend_rows"] = int(len(t))

    website_metrics["top_recommendations"] = [
        "Close the referral decision within 7 days of a primary care visit",
        "Run a capacity-aware specialist scheduling queue",
        "Close the specialist outcome within 14 days of the visit",
    ]

    (OUT_DIR / "website_metrics.json").write_text(
        json.dumps(website_metrics, indent=2),
        encoding="utf-8",
    )

    print(f"Wrote business-friendly outputs to {OUT_DIR}")


if __name__ == "__main__":
    main()
