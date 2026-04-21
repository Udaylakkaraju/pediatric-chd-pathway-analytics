"""
Data quality & validation for the pathway mart and related row counts.
Output: outputs/analytics/QC_Report.csv
"""

from __future__ import annotations

import _bootstrap_path  # noqa: F401
import pandas as pd

from chd_analytics.paths import (
    ANALYTICS,
    COLS,
    DATE_COLS,
    INTERVAL_COLS,
    MART_CLEANED,
    PATIENTS,
    ROOT,
    TABLES,
)

OUT = ANALYTICS / "QC_Report.csv"

INTERVAL_OUTLIER_DAYS = 730
DELAY_SCORE_OUTLIER = 2500
# Flag pathway dates before this as suspicious for pediatric EHR (configurable)
EARLIEST_PLAUSIBLE_YEAR = 1995


def _parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for c in DATE_COLS:
        if c in out.columns:
            out[c] = pd.to_datetime(out[c], errors="coerce")
    return out


def main() -> None:
    rows: list[dict[str, str | float | int]] = []

    mart = pd.read_csv(MART_CLEANED)
    n_mart = len(mart)
    n_pt_dup = mart["patient_id"].duplicated().sum()
    rows.append(
        {
            "category": "mart",
            "check_name": "mart_row_count",
            "metric_value": n_mart,
            "detail": str(MART_CLEANED.relative_to(ROOT)),
        }
    )
    rows.append(
        {
            "category": "mart",
            "check_name": "duplicate_patient_id_rows",
            "metric_value": int(n_pt_dup),
            "detail": "Extra rows beyond first occurrence for same patient_id",
        }
    )

    # Null rates
    for c in mart.columns:
        null_pct = 100.0 * mart[c].isna().mean()
        rows.append(
            {
                "category": "null_rate",
                "check_name": c,
                "metric_value": round(null_pct, 2),
                "detail": "percent_null",
            }
        )

    m = _parse_dates(mart)

    def bad_order(a: str, b: str) -> int:
        """Count rows where both dates present and a > b."""
        da, db = m[a], m[b]
        mask = da.notna() & db.notna() & (da > db)
        return int(mask.sum())

    seq_checks = [
        ("symptom_after_pcp", COLS["symptom_date"], COLS["pcp_date"]),
        ("pcp_after_referral", COLS["pcp_date"], COLS["referral_date"]),
        ("referral_after_specialist", COLS["referral_date"], COLS["specialist_date"]),
        ("specialist_after_diagnosis", COLS["specialist_date"], COLS["diagnosis_date"]),
        ("diagnosis_after_intervention", COLS["diagnosis_date"], COLS["intervention_date"]),
    ]
    for name, c0, c1 in seq_checks:
        if c0 not in m.columns or c1 not in m.columns:
            continue
        nbad = bad_order(c0, c1)
        rows.append(
            {
                "category": "date_sequence",
                "check_name": name,
                "metric_value": nbad,
                "detail": f"{c0} > {c1} when both present",
            }
        )

    # Future-dated pathway events (relative to run date)
    today = pd.Timestamp.today().normalize()
    for c in DATE_COLS:
        if c not in m.columns:
            continue
        col = m[c]
        future_n = int((col.notna() & (col > today)).sum())
        rows.append(
            {
                "category": "date_future",
                "check_name": f"future_{c}",
                "metric_value": future_n,
                "detail": f"Date strictly after as-of {today.date()}",
            }
        )

    # Implausibly early dates (documentation / extract errors)
    cutoff = pd.Timestamp(year=EARLIEST_PLAUSIBLE_YEAR, month=1, day=1)
    for c in DATE_COLS:
        if c not in m.columns:
            continue
        col = m[c]
        early_n = int((col.notna() & (col < cutoff)).sum())
        rows.append(
            {
                "category": "date_early",
                "check_name": f"before_{EARLIEST_PLAUSIBLE_YEAR}_{c}",
                "metric_value": early_n,
                "detail": f"Date before {cutoff.date()}",
            }
        )

    # Negative intervals (should be rare if cleaned)
    for ic in INTERVAL_COLS:
        if ic not in mart.columns:
            continue
        vals = pd.to_numeric(mart[ic], errors="coerce")
        neg = int((vals.notna() & (vals < 0)).sum())
        rows.append(
            {
                "category": "interval",
                "check_name": f"negative_{ic}",
                "metric_value": neg,
                "detail": "Values < 0",
            }
        )
        hi = int((vals.notna() & (vals > INTERVAL_OUTLIER_DAYS)).sum())
        rows.append(
            {
                "category": "interval",
                "check_name": f"outlier_gt_{INTERVAL_OUTLIER_DAYS}d_{ic}",
                "metric_value": hi,
                "detail": f"Interval > {INTERVAL_OUTLIER_DAYS} days (data quality flag)",
            }
        )

    ds = pd.to_numeric(mart[COLS["delay_score"]], errors="coerce")
    rows.append(
        {
            "category": "delay_score",
            "check_name": f"outlier_delay_score_gt_{DELAY_SCORE_OUTLIER}",
            "metric_value": int((ds.notna() & (ds > DELAY_SCORE_OUTLIER)).sum()),
            "detail": "Investigate long-tail delay engineering / documentation",
        }
    )

    # Row counts: raw tables
    try:
        pat = pd.read_csv(PATIENTS)
        rows.append(
            {
                "category": "raw_table",
                "check_name": "patients_csv_rows",
                "metric_value": len(pat),
                "detail": str(PATIENTS.name),
            }
        )
    except Exception as e:
        rows.append(
            {
                "category": "raw_table",
                "check_name": "patients_csv_rows",
                "metric_value": -1,
                "detail": str(e),
            }
        )

    for label, path in [
        ("encounters", TABLES / "encounters.csv"),
        ("referrals", TABLES / "referrals.csv"),
        ("observations", TABLES / "observations.csv"),
    ]:
        try:
            tmp = pd.read_csv(path)
            rows.append(
                {
                    "category": "raw_table",
                    "check_name": f"{label}_rows",
                    "metric_value": len(tmp),
                    "detail": path.name,
                }
            )
        except Exception as e:
            rows.append(
                {
                    "category": "raw_table",
                    "check_name": f"{label}_rows",
                    "metric_value": -1,
                    "detail": str(e),
                }
            )

    # Funnel alignment (optional)
    funnel_path = ANALYTICS / "funnel metrics.csv"
    if funnel_path.exists():
        f = pd.read_csv(funnel_path).iloc[0]
        f_sym = int(f["symptom"])
        delta = n_mart - f_sym
        rows.append(
            {
                "category": "alignment",
                "check_name": "mart_vs_funnel_symptom_cohort",
                "metric_value": delta,
                "detail": f"mart_rows({n_mart}) - funnel_symptom({f_sym})",
            }
        )

    ANALYTICS.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
