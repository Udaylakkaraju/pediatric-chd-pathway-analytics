"""
Build the coordination scorecard: leakage plus wait time by pathway stage.

Inputs:
- outputs/analytics/funnel metrics.csv
- outputs/analytics/stage dropoff.csv
- outputs/analytics/stage delay contribution.csv
- data/marts/cleaned/mart_delay_scored_cleaned.csv

Output:
- outputs/analytics/coordination_failure_scorecard.csv
"""

from __future__ import annotations

import pandas as pd

import _bootstrap_path  # noqa: F401
from chd_analytics.paths import ANALYTICS, COLS, MART_CLEANED

OUT = ANALYTICS / "coordination_failure_scorecard.csv"

STAGES = [
    ("Symptom -> PCP", "symptom", "pcp", "symptom_to_pcp", COLS["symptom_to_pcp"]),
    ("PCP -> Referral", "pcp", "referral", "pcp_to_referral", COLS["pcp_to_referral"]),
    (
        "Referral -> Specialist",
        "referral",
        "specialist",
        "referral_to_specialist",
        COLS["referral_to_specialist"],
    ),
    (
        "Specialist -> Diagnosis",
        "specialist",
        "diagnosis",
        "specialist_to_diagnosis",
        COLS["specialist_to_diagnosis"],
    ),
]


def main() -> None:
    mart = pd.read_csv(MART_CLEANED)
    funnel = pd.read_csv(ANALYTICS / "funnel metrics.csv").iloc[0].to_dict()
    dropoff = pd.read_csv(ANALYTICS / "stage dropoff.csv").set_index("stage")["drop_off_rate"].to_dict()
    delay_avg = pd.read_csv(ANALYTICS / "stage delay contribution.csv").iloc[0].to_dict()

    rows = []
    for stage_order, (label, entry_key, next_key, delay_key, interval_col) in enumerate(STAGES, start=1):
        values = pd.to_numeric(mart[interval_col], errors="coerce").dropna()
        entry_n = int(funnel[entry_key])
        next_n = int(funnel[next_key])
        conversion = next_n / entry_n if entry_n else 0
        rows.append(
            {
                "stage_order": stage_order,
                "stage_transition": label,
                "patients_at_stage_entry": entry_n,
                "patients_converting_to_next": next_n,
                "conversion_rate": round(conversion, 4),
                "drop_off_rate": round(float(dropoff[label]), 4),
                "avg_days_among_converters": round(float(delay_avg[delay_key]), 2),
                "median_days_among_converters": round(float(values.median()), 2),
                "n_patients_used_for_median": int(values.count()),
            }
        )

    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
