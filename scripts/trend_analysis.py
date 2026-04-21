"""
Trend analysis by symptom cohort month (synthetic data — interpret with maturity caveat).
Output: outputs/analytics/trend_by_month.csv
"""

from __future__ import annotations

import _bootstrap_path  # noqa: F401
import pandas as pd

from chd_analytics.paths import ANALYTICS, COLS, MART_CLEANED

OUT = ANALYTICS / "trend_by_month.csv"
MATURITY_LAG_MONTHS = 6


def main() -> None:
    df = pd.read_csv(MART_CLEANED)
    sdt = pd.to_datetime(df[COLS["symptom_date"]], errors="coerce")
    df = df.assign(_symptom_month=sdt.dt.to_period("M").astype(str))

    max_symptom = sdt.max()
    cutoff = max_symptom - pd.DateOffset(months=MATURITY_LAG_MONTHS)
    mature = df.loc[sdt <= cutoff].copy()

    mature["_diagnosed"] = pd.to_datetime(mature[COLS["diagnosis_date"]], errors="coerce").notna()
    mature["_score"] = pd.to_numeric(mature[COLS["delay_score"]], errors="coerce")

    g = mature.groupby("_symptom_month", dropna=True)
    by_month = g.agg(
        cohort_n=("patient_id", "count"),
        diagnosed_n=("_diagnosed", "sum"),
        mean_delay_score=("_score", "mean"),
        median_delay_score=("_score", "median"),
    ).reset_index()
    by_month = by_month.rename(columns={"_symptom_month": "symptom_index_month"})
    by_month["diagnosis_rate"] = by_month["diagnosed_n"] / by_month["cohort_n"]
    by_month = by_month.sort_values("symptom_index_month")
    note = (
        f"Mature months: symptom <= {cutoff.date()} "
        f"(max symptom {max_symptom.date()} minus {MATURITY_LAG_MONTHS}m lag)."
    )
    by_month["interpretation_note"] = note

    ANALYTICS.mkdir(parents=True, exist_ok=True)
    by_month.to_csv(OUT, index=False)
    print(f"Wrote {OUT} ({len(by_month)} rows)")


if __name__ == "__main__":
    main()
