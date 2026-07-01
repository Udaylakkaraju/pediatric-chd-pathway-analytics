"""Build quantified operating recommendations from the patient pathway mart.

Observed queue sizes and conversion rates come from project data. Recovery rates,
handling minutes, and labor cost are explicit planning assumptions rather than
measured savings.
"""

from __future__ import annotations

import pandas as pd

import _bootstrap_path  # noqa: F401
from chd_analytics.paths import ANALYTICS

EXCEL_DETAIL = ANALYTICS.parent / "excel_data" / "patient_pathway_detail.csv"
OUTPUT = ANALYTICS / "business_impact_summary.csv"

HOURLY_LOADED_LABOR_COST = 32.0


def _pct(value: float) -> float:
    return round(100.0 * value, 1)


def main() -> None:
    df = pd.read_csv(EXCEL_DETAIL)

    cohort = len(df)
    pcp = int(df["reached_primary_care"].sum())
    referrals = int(df["received_referral"].sum())
    specialists = int(df["completed_specialist_visit"].sum())
    diagnoses = int(df["received_diagnosis"].sum())
    open_referrals = int(df["open_referral_flag"].sum())
    appointment_recovery = int(df["appointment_recovery_flag"].sum())
    diagnostic_closure = int(df["diagnostic_closure_flag"].sum())
    high_friction = int(df["high_friction_access_flag"].sum())

    downstream_diagnosis_rate = diagnoses / specialists
    referral_dropoff = 1 - referrals / pcp
    specialist_dropoff = 1 - specialists / referrals
    diagnosis_dropoff = 1 - diagnoses / specialists

    referral_target = 0.30
    specialist_target = 0.28
    diagnosis_target = 0.25
    appointment_recovery_assumption = 0.10
    access_resolution_assumption = 0.10

    referral_gain = round(pcp * (referral_dropoff - referral_target))
    specialist_gain = round(referrals * (specialist_dropoff - specialist_target))
    closure_gain = round(specialists * (diagnosis_dropoff - diagnosis_target))
    appointment_gain = round(appointment_recovery * appointment_recovery_assumption)
    access_gain = round(high_friction * access_resolution_assumption)

    rows = [
        {
            "priority": 1,
            "recommendation": "Close the referral decision",
            "eligible_records": pcp - referrals,
            "eligible_pct_of_cohort": _pct((pcp - referrals) / cohort),
            "baseline_metric": "PCP-to-referral drop-off",
            "baseline_pct": _pct(referral_dropoff),
            "target_pct": 30.0,
            "modeled_stage_completions": referral_gain,
            "modeled_additional_diagnoses": round(referral_gain * (specialists / referrals) * downstream_diagnosis_rate),
            "time_impact": "Decision documented within 7 days",
            "handling_minutes_per_record_assumption": 8,
        },
        {
            "priority": 2,
            "recommendation": "Run a capacity-aware specialist queue",
            "eligible_records": open_referrals,
            "eligible_pct_of_cohort": _pct(open_referrals / cohort),
            "baseline_metric": "Referral-to-specialist drop-off",
            "baseline_pct": _pct(specialist_dropoff),
            "target_pct": 28.0,
            "modeled_stage_completions": specialist_gain,
            "modeled_additional_diagnoses": round(specialist_gain * downstream_diagnosis_rate),
            "time_impact": f"3-day median reduction = {3 * specialists:,} patient-days earlier",
            "handling_minutes_per_record_assumption": 10,
        },
        {
            "priority": 3,
            "recommendation": "Recover missed appointments",
            "eligible_records": appointment_recovery,
            "eligible_pct_of_cohort": _pct(appointment_recovery / cohort),
            "baseline_metric": "Recovery rate assumption",
            "baseline_pct": 0.0,
            "target_pct": _pct(appointment_recovery_assumption),
            "modeled_stage_completions": appointment_gain,
            "modeled_additional_diagnoses": round(appointment_gain * downstream_diagnosis_rate),
            "time_impact": "No-show outreach in 48 hours; cancellations rebooked in 7 days",
            "handling_minutes_per_record_assumption": 15,
        },
        {
            "priority": 4,
            "recommendation": "Close the specialist outcome",
            "eligible_records": diagnostic_closure,
            "eligible_pct_of_cohort": _pct(diagnostic_closure / cohort),
            "baseline_metric": "Specialist-to-diagnosis drop-off",
            "baseline_pct": _pct(diagnosis_dropoff),
            "target_pct": 25.0,
            "modeled_stage_completions": closure_gain,
            "modeled_additional_diagnoses": closure_gain,
            "time_impact": "Outcome documented within 14 days",
            "handling_minutes_per_record_assumption": 8,
        },
        {
            "priority": 5,
            "recommendation": "Review high-friction access cases",
            "eligible_records": high_friction,
            "eligible_pct_of_cohort": _pct(high_friction / cohort),
            "baseline_metric": "Share of open referrals flagged high-friction",
            "baseline_pct": _pct(high_friction / open_referrals),
            "target_pct": _pct(access_resolution_assumption),
            "modeled_stage_completions": access_gain,
            "modeled_additional_diagnoses": round(access_gain * downstream_diagnosis_rate),
            "time_impact": "Barrier and next action documented at the 30-day review",
            "handling_minutes_per_record_assumption": 20,
        },
    ]

    out = pd.DataFrame(rows)
    out["estimated_staff_hours"] = (
        out["eligible_records"] * out["handling_minutes_per_record_assumption"] / 60
    ).round(1)
    out["illustrative_labor_cost"] = (
        out["estimated_staff_hours"] * HOURLY_LOADED_LABOR_COST
    ).round(0)
    out["labor_cost_assumption_per_hour"] = HOURLY_LOADED_LABOR_COST
    out.to_csv(OUTPUT, index=False)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
