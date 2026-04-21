"""
Exploratory root-cause style analysis (associational — not causal).
Outputs: outputs/analytics/provider_performance.csv, root_cause_summary.md
"""

from __future__ import annotations

import _bootstrap_path  # noqa: F401
import pandas as pd

from chd_analytics.paths import (
    ANALYTICS,
    COLS,
    MART_CLEANED,
    PROCEDURES,
    REFERRALS,
    TABLES,
)
PROVIDERS = TABLES / "providers.csv"
MIN_REFERRALS = 15
OUT_PROV = ANALYTICS / "provider_performance.csv"
OUT_MD = ANALYTICS / "root_cause_summary.md"


def main() -> None:
    mart = pd.read_csv(MART_CLEANED)
    mart["_diagnosis_dt"] = pd.to_datetime(mart[COLS["diagnosis_date"]], errors="coerce")
    mart["_specialist_dt"] = pd.to_datetime(mart[COLS["specialist_date"]], errors="coerce")

    ref = pd.read_csv(REFERRALS)
    ref["completed"] = pd.to_numeric(ref["completed"], errors="coerce").fillna(0).astype(int)
    ref_counts = ref.groupby("patient_id").agg(
        referral_rows=("referral_id", "count"),
        referral_completed_any=("completed", "max"),
    )

    m = mart.merge(ref_counts, on="patient_id", how="left")
    m["referral_rows"] = m["referral_rows"].fillna(0).astype(int)
    m["has_referral_record"] = m["referral_rows"] > 0

    # referring-provider rollups
    prov_stats = (
        ref.groupby("from_provider_id")
        .agg(
            referrals_sent=("referral_id", "count"),
            referral_completed_rate=("completed", "mean"),
        )
        .reset_index()
    )
    prov_stats = prov_stats.loc[prov_stats["referrals_sent"] >= MIN_REFERRALS]
    if PROVIDERS.exists():
        pv = pd.read_csv(PROVIDERS)
        prov_stats = prov_stats.merge(
            pv,
            left_on="from_provider_id",
            right_on="provider_id",
            how="left",
        )
    ANALYTICS.mkdir(parents=True, exist_ok=True)
    prov_stats.to_csv(OUT_PROV, index=False)

    # Echo before / on diagnosis (documentation closure proxy)
    proc = pd.read_csv(PROCEDURES)
    echo = proc.loc[proc["procedure_type"].astype(str) == "Echocardiogram"].copy()
    echo["procedure_datetime"] = pd.to_datetime(echo["procedure_datetime"], errors="coerce")
    first_echo = echo.groupby("patient_id")["procedure_datetime"].min().rename("first_echo_dt")

    mx = mart.merge(first_echo, on="patient_id", how="left")
    mx["_diagnosis_dt"] = pd.to_datetime(mx[COLS["diagnosis_date"]], errors="coerce")
    diagnosed = mx["_diagnosis_dt"].notna()
    has_echo = mx["first_echo_dt"].notna()
    echo_on_or_before_dx = has_echo & diagnosed & (mx["first_echo_dt"] <= mx["_diagnosis_dt"])

    specialist_no_dx = mx["_specialist_dt"].notna() & mx["_diagnosis_dt"].isna()
    share_dx_with_echo_timing = float(echo_on_or_before_dx.sum() / diagnosed.sum()) if diagnosed.any() else 0.0
    share_dx_with_any_echo = float((diagnosed & has_echo).sum() / diagnosed.sum()) if diagnosed.any() else 0.0

    m["diagnosed"] = m["_diagnosis_dt"].notna()
    dx_rate_with = float(m.loc[m["has_referral_record"], "diagnosed"].mean())
    dx_rate_without = float(m.loc[~m["has_referral_record"], "diagnosed"].mean())

    # Specialist→diagnosis gap: echo among those stalled after specialist
    stalled = mx[specialist_no_dx]
    stalled_echo = stalled["first_echo_dt"].notna().mean() if len(stalled) else 0.0

    lines = [
        "# Root cause exploratory summary\n",
        "_Associational patterns only. No payer auth/denial fields in this synthetic schema._\n\n",
        "## Referral documentation\n",
        f"- Patients with **≥1 referral row**: {m['has_referral_record'].mean():.1%} of mart cohort.\n",
        f"- Diagnosis rate **with** referral record: {dx_rate_with:.3f}; **without**: {dx_rate_without:.3f}.\n\n",
        "## Diagnostic closure proxy (echocardiogram timing)\n",
        f"- Among **patients with a recorded diagnosis** (n={int(diagnosed.sum())}):\n",
        f"  - **Any** echocardiogram record: {share_dx_with_any_echo:.1%}\n",
        f"  - Echo **on or before** diagnosis date: {share_dx_with_echo_timing:.1%}\n",
        f"- Among **specialist seen but no diagnosis** (stalled cohort, n={int(specialist_no_dx.sum())}):\n",
        f"  - **Any** echo record: {stalled_echo:.1%}\n\n",
        "## Referring provider activity (min referrals)\n",
        f"- Providers with **≥{MIN_REFERRALS}** outbound referrals in extract: **{len(prov_stats)}** "
        f"(see `provider_performance.csv`).\n",
        "- Use these metrics for **operational triage** (volume, completion), not individual clinician quality verdicts.\n",
    ]
    OUT_MD.write_text("".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_PROV} and {OUT_MD}")


if __name__ == "__main__":
    main()
