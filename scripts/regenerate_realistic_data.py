"""
Regenerate the CHD patient mart with realistic, business-readable patterns.

This is synthetic data, but it is shaped to behave like healthcare operations
data:
- right-skewed wait times instead of flat/random intervals
- urgent CHD types presenting faster than mild/incidental defects
- Medicaid/uninsured and high-SVI patients waiting longer for specialists
- simple operational fields for BI users: priority, appointment status,
  authorization status, region, capacity tier, and distance to specialist

Drop-off counts are preserved from the current mart so the funnel story stays
stable. The script changes timing and context fields, then downstream analytics
scripts rebuild reporting outputs from this single mart.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
rng = np.random.default_rng(SEED)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MART_PATH = PROJECT_ROOT / "data" / "marts" / "cleaned" / "mart_delay_scored_cleaned.csv"

COMPLEX = {
    "Hypoplastic Left Heart Syndrome",
    "Transposition of the Great Arteries",
    "Tricuspid Atresia",
    "Double Outlet Right Ventricle (DORV)",
    "Other complex CHD",
}

MODERATE = {
    "Tetralogy of Fallot",
    "Coarctation of the Aorta",
    "Pulmonary Stenosis",
    "Aortic Stenosis",
}

INTERVAL_WEIGHTS = {
    "days_symptom_to_pcp_clean": 0.25,
    "days_pcp_to_referral_clean": 0.30,
    "days_referral_to_specialist_clean": 0.20,
    "days_specialist_to_diagnosis_clean": 0.15,
    "days_diagnosis_to_intervention_clean": 0.10,
}


def lognormal_days(median_days: float, sigma: float, lo: int, hi: int) -> int:
    raw = rng.lognormal(mean=np.log(max(median_days, 0.1)), sigma=sigma)
    return int(np.clip(round(raw), lo, hi))


def random_dates_in_range(start: str, end: str, n: int) -> pd.Series:
    start_ns = pd.Timestamp(start).value
    end_ns = pd.Timestamp(end).value
    return pd.to_datetime(rng.integers(start_ns, end_ns, size=n))


def severity_bucket(chd_type: object) -> str:
    value = str(chd_type)
    if value in COMPLEX:
        return "Complex"
    if value in MODERATE:
        return "Moderate"
    return "Simple"


def choose_priority(severity: str, svi: float) -> str:
    if severity == "Complex":
        return rng.choice(["urgent", "critical"], p=[0.55, 0.45])
    if severity == "Moderate":
        return rng.choice(["routine", "urgent"], p=[0.65, 0.35])
    if svi >= 0.80:
        return rng.choice(["routine", "urgent"], p=[0.82, 0.18])
    return "routine"


def median_symptom_to_pcp(severity: str, chd_type: str, svi: float) -> float:
    if severity == "Complex":
        base = 7.0
    elif severity == "Moderate":
        base = 18.0
    elif "Atrial Septal" in chd_type or "Patent Ductus" in chd_type:
        base = 46.0
    else:
        base = 30.0
    return base * (1.0 + 0.20 * max(svi - 0.50, 0.0))


def median_pcp_to_referral(priority: str, payer: str, svi: float) -> float:
    base = {"critical": 3.0, "urgent": 7.0, "routine": 16.0}[priority]
    payer_factor = {
        "private": 0.95,
        "medicaid": 1.12,
        "uninsured": 1.25,
        "other": 1.05,
    }.get(payer, 1.0)
    return base * payer_factor * (1.0 + 0.25 * max(svi - 0.50, 0.0))


def median_referral_to_specialist(priority: str, payer: str, svi: float, distance: float) -> float:
    base = {"critical": 12.0, "urgent": 28.0, "routine": 48.0}[priority]
    payer_factor = {
        "private": 0.82,
        "medicaid": 1.28,
        "uninsured": 1.45,
        "other": 1.10,
    }.get(payer, 1.0)
    return (base * payer_factor * (1.0 + 0.40 * max(svi - 0.45, 0.0))) + (distance / 18.0)


def median_specialist_to_diagnosis(severity: str, priority: str) -> float:
    if priority == "critical":
        return 3.0
    if severity == "Complex":
        return 5.0
    if severity == "Moderate":
        return 9.0
    return 15.0


def median_diagnosis_to_intervention(severity: str, priority: str) -> float:
    if priority == "critical":
        return 21.0
    if severity == "Complex":
        return 38.0
    if severity == "Moderate":
        return 75.0
    return 120.0


def format_dates(values: pd.Series, mask: pd.Series) -> pd.Series:
    out = pd.Series([None] * len(values), dtype=object)
    out.loc[mask] = values.loc[mask].dt.strftime("%Y-%m-%d")
    return out


def weighted_subset(candidates: np.ndarray, count: int, weights: np.ndarray) -> np.ndarray:
    if count > len(candidates):
        raise ValueError(f"Cannot sample {count} rows from {len(candidates)} candidates")
    candidate_weights = np.asarray(weights[candidates], dtype=float)
    candidate_weights = np.where(np.isfinite(candidate_weights) & (candidate_weights > 0), candidate_weights, 1.0)
    probabilities = candidate_weights / candidate_weights.sum()
    return rng.choice(candidates, size=count, replace=False, p=probabilities)


def main() -> None:
    df = pd.read_csv(MART_PATH)
    n = len(df)
    print(f"Loaded {n} patients from {MART_PATH}")

    original_counts = {
        "pcp": int(df["first_pcp_date"].notna().sum()),
        "referral": int(df["referral_date"].notna().sum()),
        "specialist": int(df["specialist_date"].notna().sum()),
        "diagnosis": int(df["diagnosis_date"].notna().sum()),
        "intervention": int(df["intervention_date"].notna().sum()),
    }

    df["chd_severity"] = df["chd_type"].apply(severity_bucket)
    svi = pd.to_numeric(df["svi_index"], errors="coerce").fillna(0.5)

    df["referral_priority"] = [
        choose_priority(severity, float(score))
        for severity, score in zip(df["chd_severity"], svi)
    ]
    df["clinic_region"] = rng.choice(
        ["North", "South", "East", "West", "Central"],
        size=n,
        p=[0.20, 0.23, 0.18, 0.19, 0.20],
    )
    df["provider_capacity_tier"] = rng.choice(
        ["low_capacity", "standard_capacity", "high_capacity"],
        size=n,
        p=[0.24, 0.56, 0.20],
    )

    severity_weight = df["chd_severity"].map({"Complex": 1.25, "Moderate": 1.05, "Simple": 0.95}).to_numpy()
    priority_weight = pd.Series(df["referral_priority"]).map(
        {"critical": 1.35, "urgent": 1.15, "routine": 0.95}
    ).to_numpy()
    access_weight = (1.25 - (0.40 * svi.to_numpy())).clip(0.55, 1.35)
    base_weight = severity_weight * priority_weight * access_weight

    all_idx = np.arange(n)
    pcp_idx = weighted_subset(all_idx, original_counts["pcp"], base_weight)
    referral_idx = weighted_subset(pcp_idx, original_counts["referral"], base_weight)
    specialist_idx = weighted_subset(referral_idx, original_counts["specialist"], base_weight)
    diagnosis_idx = weighted_subset(specialist_idx, original_counts["diagnosis"], base_weight)
    intervention_n = min(original_counts["intervention"], original_counts["diagnosis"])
    intervention_idx = weighted_subset(diagnosis_idx, intervention_n, base_weight)

    has_pcp = pd.Series(False, index=df.index)
    has_referral = pd.Series(False, index=df.index)
    has_specialist = pd.Series(False, index=df.index)
    has_diagnosis = pd.Series(False, index=df.index)
    has_intervention = pd.Series(False, index=df.index)
    has_pcp.iloc[pcp_idx] = True
    has_referral.iloc[referral_idx] = True
    has_specialist.iloc[specialist_idx] = True
    has_diagnosis.iloc[diagnosis_idx] = True
    has_intervention.iloc[intervention_idx] = True

    distance_base = rng.gamma(shape=2.0, scale=11.0, size=n)
    capacity_add = df["provider_capacity_tier"].map(
        {"low_capacity": 9.0, "standard_capacity": 3.0, "high_capacity": 0.0}
    ).to_numpy()
    df["distance_to_specialist_miles"] = np.clip(
        distance_base + (25.0 * svi.to_numpy()) + capacity_add,
        1,
        160,
    ).round(1)

    is_public_or_uninsured = df["insurance_type"].isin(["medicaid", "uninsured"])
    df["authorization_status"] = "not_required"
    public_count = int(is_public_or_uninsured.sum())
    df.loc[is_public_or_uninsured, "authorization_status"] = rng.choice(
        ["approved", "pending", "denied"],
        size=public_count,
        p=[0.58, 0.32, 0.10],
    )
    df.loc[has_specialist & is_public_or_uninsured, "authorization_status"] = rng.choice(
        ["approved", "not_required"],
        size=int((has_specialist & is_public_or_uninsured).sum()),
        p=[0.85, 0.15],
    )
    df.loc[~has_referral, "authorization_status"] = "not_started"

    df["specialist_appointment_status"] = "not_referred"
    referred_not_seen = has_referral & ~has_specialist
    df.loc[referred_not_seen, "specialist_appointment_status"] = rng.choice(
        ["scheduled_pending", "cancelled", "no_show", "unable_to_contact"],
        size=int(referred_not_seen.sum()),
        p=[0.38, 0.18, 0.24, 0.20],
    )
    df.loc[has_specialist, "specialist_appointment_status"] = "completed"

    sigma = 0.72
    d_symptom_to_pcp = np.array(
        [
            lognormal_days(median_symptom_to_pcp(severity, chd, float(score)), sigma, 1, 365)
            for severity, chd, score in zip(df["chd_severity"], df["chd_type"], svi)
        ]
    )
    d_pcp_to_referral = np.array(
        [
            lognormal_days(median_pcp_to_referral(priority, payer, float(score)), sigma, 1, 90)
            for priority, payer, score in zip(df["referral_priority"], df["insurance_type"], svi)
        ]
    )
    d_referral_to_specialist = np.array(
        [
            lognormal_days(
                median_referral_to_specialist(priority, payer, float(score), float(distance)),
                sigma,
                3,
                180,
            )
            for priority, payer, score, distance in zip(
                df["referral_priority"],
                df["insurance_type"],
                svi,
                df["distance_to_specialist_miles"],
            )
        ]
    )
    d_specialist_to_diagnosis = np.array(
        [
            lognormal_days(median_specialist_to_diagnosis(severity, priority), sigma, 0, 90)
            for severity, priority in zip(df["chd_severity"], df["referral_priority"])
        ]
    )
    d_diagnosis_to_intervention = np.array(
        [
            lognormal_days(median_diagnosis_to_intervention(severity, priority), sigma, 7, 365)
            for severity, priority in zip(df["chd_severity"], df["referral_priority"])
        ]
    )

    symptom_dates = pd.Series(random_dates_in_range("2018-01-01", "2023-06-30", n))
    pcp_dates = symptom_dates + pd.to_timedelta(d_symptom_to_pcp, unit="D")
    referral_dates = pcp_dates + pd.to_timedelta(d_pcp_to_referral, unit="D")
    specialist_dates = referral_dates + pd.to_timedelta(d_referral_to_specialist, unit="D")
    diagnosis_dates = specialist_dates + pd.to_timedelta(d_specialist_to_diagnosis, unit="D")
    intervention_dates = diagnosis_dates + pd.to_timedelta(d_diagnosis_to_intervention, unit="D")

    df["symptom_onset_date"] = symptom_dates.dt.strftime("%Y-%m-%d")
    df["first_pcp_date"] = format_dates(pcp_dates, has_pcp)
    df["referral_date"] = format_dates(referral_dates, has_referral)
    df["specialist_date"] = format_dates(specialist_dates, has_specialist)
    df["diagnosis_date"] = format_dates(diagnosis_dates, has_diagnosis)
    df["intervention_date"] = format_dates(intervention_dates, has_intervention)

    df["days_symptom_to_pcp_clean"] = np.where(has_pcp, d_symptom_to_pcp, np.nan)
    df["days_pcp_to_referral_clean"] = np.where(has_referral, d_pcp_to_referral, np.nan)
    df["days_referral_to_specialist_clean"] = np.where(has_specialist, d_referral_to_specialist, np.nan)
    df["days_specialist_to_diagnosis_clean"] = np.where(has_diagnosis, d_specialist_to_diagnosis, np.nan)
    df["days_diagnosis_to_intervention_clean"] = np.where(has_intervention, d_diagnosis_to_intervention, np.nan)

    delay_score = pd.Series(0.0, index=df.index)
    for col, weight in INTERVAL_WEIGHTS.items():
        delay_score += pd.to_numeric(df[col], errors="coerce").fillna(0) * weight
    df["delay_severity_score_clean"] = delay_score.round(2)

    df.to_csv(MART_PATH, index=False)
    print(f"Saved regenerated mart -> {MART_PATH}")

    print("\nInterval sanity check")
    for col in INTERVAL_WEIGHTS:
        values = pd.to_numeric(df[col], errors="coerce").dropna()
        print(
            f"{col}: mean={values.mean():.1f}d median={values.median():.1f}d "
            f"p95={values.quantile(0.95):.1f}d max={values.max():.1f}d n={len(values)}"
        )

    print("\nFunnel preserved")
    for col, original in [
        ("first_pcp_date", original_counts["pcp"]),
        ("referral_date", original_counts["referral"]),
        ("specialist_date", original_counts["specialist"]),
        ("diagnosis_date", original_counts["diagnosis"]),
        ("intervention_date", intervention_n),
    ]:
        current = df[col].notna().sum()
        status = "OK" if original == current else "MISMATCH"
        print(f"{col}: {original} -> {current} {status}")


if __name__ == "__main__":
    main()
