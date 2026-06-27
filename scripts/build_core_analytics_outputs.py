"""
Build core analytics outputs directly from the cleaned patient mart.

These CSVs feed the README, Excel/Power BI layer, Streamlit dashboard, and
tests. Keeping them in one script helps prevent stale or contradictory numbers.
"""

from __future__ import annotations

import pandas as pd

import _bootstrap_path  # noqa: F401
from chd_analytics.paths import ANALYTICS, COLS, INTERVAL_COLS, MART_CLEANED

STAGES = [
    (
        "Symptom -> PCP",
        "symptom",
        "pcp",
        COLS["symptom_to_pcp"],
    ),
    (
        "PCP -> Referral",
        "pcp",
        "referral",
        COLS["pcp_to_referral"],
    ),
    (
        "Referral -> Specialist",
        "referral",
        "specialist",
        COLS["referral_to_specialist"],
    ),
    (
        "Specialist -> Diagnosis",
        "specialist",
        "diagnosis",
        COLS["specialist_to_diagnosis"],
    ),
]


def _stage_counts(df: pd.DataFrame) -> dict[str, int]:
    return {
        "symptom": int(df[COLS["symptom_date"]].notna().sum()),
        "pcp": int(df[COLS["pcp_date"]].notna().sum()),
        "referral": int(df[COLS["referral_date"]].notna().sum()),
        "specialist": int(df[COLS["specialist_date"]].notna().sum()),
        "diagnosis": int(df[COLS["diagnosis_date"]].notna().sum()),
    }


def _rate(numerator: int | float, denominator: int | float) -> float:
    return float(numerator / denominator) if denominator else 0.0


def build_funnel(df: pd.DataFrame) -> pd.DataFrame:
    counts = _stage_counts(df)
    row = {
        **counts,
        "symptom_to_pcp_conversion": round(_rate(counts["pcp"], counts["symptom"]), 4),
        "pcp_to_referral_conversion": round(_rate(counts["referral"], counts["pcp"]), 4),
        "referral_to_specialist_conversion": round(_rate(counts["specialist"], counts["referral"]), 4),
        "specialist_to_diagnosis_conversion": round(_rate(counts["diagnosis"], counts["specialist"]), 4),
    }
    return pd.DataFrame([row])


def build_stage_dropoff(funnel: pd.DataFrame) -> pd.DataFrame:
    row = funnel.iloc[0].to_dict()
    return pd.DataFrame(
        [
            {
                "stage": stage,
                "drop_off_rate": round(1.0 - _rate(row[next_key], row[start_key]), 4),
            }
            for stage, start_key, next_key, _ in STAGES
        ]
    )


def build_stage_delay(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "symptom_to_pcp": round(pd.to_numeric(df[COLS["symptom_to_pcp"]], errors="coerce").mean(), 2),
                "pcp_to_referral": round(pd.to_numeric(df[COLS["pcp_to_referral"]], errors="coerce").mean(), 2),
                "referral_to_specialist": round(
                    pd.to_numeric(df[COLS["referral_to_specialist"]], errors="coerce").mean(),
                    2,
                ),
                "specialist_to_diagnosis": round(
                    pd.to_numeric(df[COLS["specialist_to_diagnosis"]], errors="coerce").mean(),
                    2,
                ),
            }
        ]
    )


def build_insurance(df: pd.DataFrame) -> pd.DataFrame:
    work = df.copy()
    work["_diagnosed"] = pd.to_datetime(work[COLS["diagnosis_date"]], errors="coerce").notna()
    work["_delay"] = pd.to_numeric(work[COLS["delay_score"]], errors="coerce")
    out = (
        work.groupby("insurance_type", dropna=False)
        .agg(
            total_patients=("patient_id", "count"),
            avg_delay=("_delay", "mean"),
            diagnosis_rate=("_diagnosed", "mean"),
        )
        .reset_index()
        .sort_values("total_patients", ascending=False)
    )
    out["avg_delay"] = out["avg_delay"].round(2)
    out["diagnosis_rate"] = out["diagnosis_rate"].round(4)
    return out


def build_delay_buckets(df: pd.DataFrame) -> pd.DataFrame:
    values = pd.to_numeric(df[COLS["delay_score"]], errors="coerce").fillna(0)
    bins = [-0.01, 0.01, 10, 20, 35, float("inf")]
    labels = ["No delay", "Low", "Moderate", "High", "Severe"]
    return pd.DataFrame(
        {
            "patient_id": df["patient_id"],
            "delay_score": values.round(2),
            "delay_bucket": pd.cut(values, bins=bins, labels=labels).astype(str),
        }
    )


def build_bi_patient_table(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["reached_primary_care"] = out[COLS["pcp_date"]].notna()
    out["received_referral"] = out[COLS["referral_date"]].notna()
    out["completed_specialist_visit"] = out[COLS["specialist_date"]].notna()
    out["received_diagnosis"] = out[COLS["diagnosis_date"]].notna()
    out["pathway_status"] = "Symptom documented only"
    out.loc[out["reached_primary_care"], "pathway_status"] = "Seen in primary care"
    out.loc[out["received_referral"], "pathway_status"] = "Referral created"
    out.loc[out["completed_specialist_visit"], "pathway_status"] = "Specialist visit completed"
    out.loc[out["received_diagnosis"], "pathway_status"] = "Diagnosis recorded"
    out["high_svi_flag"] = pd.to_numeric(out["svi_index"], errors="coerce") >= 0.67
    return out[
        [
            "patient_id",
            "insurance_type",
            "chd_type",
            "chd_severity",
            "svi_index",
            "high_svi_flag",
            "clinic_region",
            "provider_capacity_tier",
            "distance_to_specialist_miles",
            "referral_priority",
            "authorization_status",
            "specialist_appointment_status",
            "pathway_status",
            "reached_primary_care",
            "received_referral",
            "completed_specialist_visit",
            "received_diagnosis",
            *INTERVAL_COLS,
            COLS["delay_score"],
        ]
    ]


def main() -> None:
    ANALYTICS.mkdir(parents=True, exist_ok=True)
    bi_dir = ANALYTICS.parent / "bi_ready"
    bi_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(MART_CLEANED)

    funnel = build_funnel(df)
    funnel.to_csv(ANALYTICS / "funnel metrics.csv", index=False)
    build_stage_dropoff(funnel).to_csv(ANALYTICS / "stage dropoff.csv", index=False)
    build_stage_delay(df).to_csv(ANALYTICS / "stage delay contribution.csv", index=False)
    build_insurance(df).to_csv(ANALYTICS / "insurance analysis.csv", index=False)
    build_delay_buckets(df).to_csv(ANALYTICS / "delay buckets.csv", index=False)

    build_bi_patient_table(df).to_csv(bi_dir / "patient_pathway_detail.csv", index=False)
    funnel.to_csv(bi_dir / "pathway_funnel_summary.csv", index=False)
    build_stage_dropoff(funnel).to_csv(bi_dir / "stage_dropoff_rates.csv", index=False)
    build_stage_delay(df).to_csv(bi_dir / "stage_wait_time_summary.csv", index=False)
    build_insurance(df).to_csv(bi_dir / "payer_summary.csv", index=False)

    print(f"Wrote core analytics outputs to {ANALYTICS}")
    print(f"Wrote BI-ready outputs to {bi_dir}")


if __name__ == "__main__":
    main()
