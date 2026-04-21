"""
Multi-dimensional segmentation on pathway mart + patient demographics.
Outputs: outputs/analytics/segment_comparison.csv, segment_deep_dive.md
"""

from __future__ import annotations

import _bootstrap_path  # noqa: F401
import pandas as pd

from chd_analytics.chd_severity_map import age_band, cohort_era, severity_bucket
from chd_analytics.paths import ANALYTICS, COLS, MART_CLEANED, PATIENTS

OUT_CSV = ANALYTICS / "segment_comparison.csv"
OUT_MD = ANALYTICS / "segment_deep_dive.md"


def _one_dim(df: pd.DataFrame, dimension: str, col: str) -> pd.DataFrame:
    out = (
        df.groupby(col, dropna=False, observed=True)
        .agg(
            n=("patient_id", "count"),
            diagnosis_rate=("diagnosed", "mean"),
            mean_delay=("_score", "mean"),
            median_delay=("_score", "median"),
        )
        .reset_index()
    )
    out.insert(0, "segment_dimension", dimension)
    return out.rename(columns={col: "segment_value"})


def main() -> None:
    mart = pd.read_csv(MART_CLEANED)
    pat = pd.read_csv(PATIENTS, usecols=["patient_id", "age_years", "zip_code"])
    df = mart.merge(pat, on="patient_id", how="left")

    sdt = pd.to_datetime(df[COLS["symptom_date"]], errors="coerce")
    df["symptom_year"] = sdt.dt.year
    df["chd_severity"] = df["chd_type"].apply(severity_bucket)
    df["age_band"] = df["age_years"].apply(age_band)
    df["cohort_era"] = df["symptom_year"].apply(cohort_era)
    df["diagnosed"] = pd.to_datetime(df[COLS["diagnosis_date"]], errors="coerce").notna()
    df["_score"] = pd.to_numeric(df[COLS["delay_score"]], errors="coerce")

    svi = pd.to_numeric(df["svi_index"], errors="coerce")
    df["svi_tertile"] = pd.qcut(
        svi.rank(method="first"),
        3,
        labels=["T1_lowest_SVI", "T2_mid_SVI", "T3_highest_SVI"],
    )

    blocks = [
        _one_dim(df, "insurance_type", "insurance_type"),
        _one_dim(df, "chd_severity", "chd_severity"),
        _one_dim(df, "age_band", "age_band"),
        _one_dim(df, "cohort_era", "cohort_era"),
        _one_dim(df, "svi_tertile", "svi_tertile"),
    ]

    cross = (
        df.groupby(["insurance_type", "chd_severity"], dropna=False, observed=True)
        .agg(
            n=("patient_id", "count"),
            diagnosis_rate=("diagnosed", "mean"),
            mean_delay=("_score", "mean"),
            median_delay=("_score", "median"),
        )
        .reset_index()
    )
    cross.insert(0, "segment_dimension", "insurance_x_severity")
    cross["segment_value"] = (
        cross["insurance_type"].astype(str) + " | " + cross["chd_severity"].astype(str)
    )
    cross = cross[
        ["segment_dimension", "segment_value", "n", "diagnosis_rate", "mean_delay", "median_delay"]
    ]
    blocks.append(cross)

    full = pd.concat(blocks, ignore_index=True)
    ANALYTICS.mkdir(parents=True, exist_ok=True)
    full.to_csv(OUT_CSV, index=False)

    lines = ["# Segment deep dive\n", "_Synthetic cohort; descriptive segments only._\n"]
    for dim in full["segment_dimension"].unique():
        sub = full.loc[full["segment_dimension"] == dim].sort_values("n", ascending=False)
        lines.append(f"\n## {dim}\n")
        lines.append("| segment | n | diagnosis_rate | mean_delay | median_delay |\n")
        lines.append("|---|---:|---:|---:|---:|\n")
        for _, r in sub.iterrows():
            med = f"{r['median_delay']:.1f}" if pd.notna(r["median_delay"]) else ""
            lines.append(
                f"| {r['segment_value']} | {int(r['n'])} | {float(r['diagnosis_rate']):.3f} | "
                f"{float(r['mean_delay']):.1f} | {med} |\n"
            )

    big_cross = cross[cross["n"] >= 80].sort_values("mean_delay", ascending=False)
    if len(big_cross):
        top = big_cross.iloc[0]
        lines.append(
            "\n### Callout (insurance × severity, n≥80, highest mean delay)\n\n"
            f"- **{top['segment_value']}**: n={int(top['n'])}, "
            f"diagnosis_rate={float(top['diagnosis_rate']):.3f}, "
            f"mean_delay={float(top['mean_delay']):.1f}\n"
        )

    OUT_MD.write_text("".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_CSV} and {OUT_MD}")


if __name__ == "__main__":
    main()
