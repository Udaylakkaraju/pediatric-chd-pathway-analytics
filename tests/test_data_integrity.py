"""Source-to-mart integrity and synthetic realism contracts."""

from __future__ import annotations

import pandas as pd


def _raw(project_root, name: str, **kwargs) -> pd.DataFrame:
    return pd.read_csv(project_root / "data" / "raw" / name, **kwargs)


def test_expanded_dataset_scale(project_root):
    patients = _raw(project_root, "patients(Main Table).csv", usecols=["patient_id", "has_chd"])
    mart = pd.read_csv(
        project_root / "data" / "marts" / "cleaned" / "mart_delay_scored_cleaned.csv",
        usecols=["patient_id"],
    )
    assert len(patients) == 100_000
    assert patients["patient_id"].is_unique
    assert int(patients["has_chd"].sum()) == 15_000
    assert len(mart) == 15_000
    assert mart["patient_id"].is_unique


def test_foreign_keys_are_intact(project_root):
    patient_ids = set(_raw(project_root, "patients(Main Table).csv", usecols=["patient_id"])["patient_id"])
    encounters = _raw(project_root, "encounters.csv", usecols=["encounter_id", "patient_id"])
    observations = _raw(project_root, "observations.csv", usecols=["encounter_id", "patient_id"])
    assert set(encounters["patient_id"]).issubset(patient_ids)
    assert set(observations["patient_id"]).issubset(patient_ids)
    assert set(observations["encounter_id"]).issubset(set(encounters["encounter_id"]))
    for filename in ["referrals.csv", "conditions.csv", "procedures.csv"]:
        child_ids = set(_raw(project_root, filename, usecols=["patient_id"])["patient_id"])
        assert child_ids.issubset(patient_ids)


def test_no_event_occurs_before_birth(project_root):
    patients = _raw(project_root, "patients(Main Table).csv", usecols=["patient_id", "dob", "first_contact_date"])
    dob = pd.to_datetime(patients.set_index("patient_id")["dob"])
    contact = pd.to_datetime(patients.set_index("patient_id")["first_contact_date"])
    assert (contact >= dob).all()
    for filename, date_col in [
        ("encounters.csv", "encounter_datetime"),
        ("referrals.csv", "referral_datetime"),
        ("conditions.csv", "condition_start"),
        ("procedures.csv", "procedure_datetime"),
    ]:
        events = _raw(project_root, filename, usecols=["patient_id", date_col])
        dates = pd.to_datetime(events[date_col])
        births = dob.loc[events["patient_id"]].reset_index(drop=True)
        assert (dates.reset_index(drop=True) >= births).all()


def test_pathway_is_strictly_nested_and_ordered(project_root):
    mart = pd.read_csv(project_root / "data" / "marts" / "cleaned" / "mart_delay_scored_cleaned.csv")
    stages = [
        "symptom_onset_date",
        "first_pcp_date",
        "referral_date",
        "specialist_date",
        "diagnosis_date",
        "intervention_date",
    ]
    dates = mart[stages].apply(pd.to_datetime)
    for earlier, later in zip(stages, stages[1:]):
        assert (~dates[later].notna() | dates[earlier].notna()).all()
        comparable = dates[earlier].notna() & dates[later].notna()
        assert (dates.loc[comparable, earlier] <= dates.loc[comparable, later]).all()


def test_mart_dimensions_match_raw_source(project_root):
    patients = _raw(
        project_root,
        "patients(Main Table).csv",
        usecols=["patient_id", "has_chd", "insurance_type", "chd_type"],
    )
    mart = pd.read_csv(
        project_root / "data" / "marts" / "cleaned" / "mart_delay_scored_cleaned.csv",
        usecols=["patient_id", "insurance_type", "chd_type"],
    )
    expected = patients.loc[patients["has_chd"].eq(1), ["patient_id", "insurance_type", "chd_type"]]
    joined = mart.merge(expected, on="patient_id", suffixes=("_mart", "_raw"), validate="one_to_one")
    assert joined["insurance_type_mart"].eq(joined["insurance_type_raw"]).all()
    assert joined["chd_type_mart"].eq(joined["chd_type_raw"]).all()


def test_operational_factors_have_visible_overlapping_effects(project_root):
    mart = pd.read_csv(project_root / "data" / "marts" / "cleaned" / "mart_delay_scored_cleaned.csv")
    mart["specialist_completed"] = mart["specialist_date"].notna()
    mart["diagnosed"] = mart["diagnosis_date"].notna()
    capacity = mart.groupby("provider_capacity_tier").agg(
        completion=("specialist_completed", "mean"),
        wait=("days_referral_to_specialist_clean", "median"),
    )
    assert capacity.loc["high_capacity", "completion"] > capacity.loc["low_capacity", "completion"] + 0.05
    assert capacity.loc["low_capacity", "wait"] > capacity.loc["high_capacity", "wait"] + 8

    mart["svi_band"] = pd.qcut(mart["svi_index"], 3, labels=["Low", "Middle", "High"])
    svi = mart.groupby("svi_band", observed=True)["specialist_completed"].mean()
    assert svi.loc["Low"] > svi.loc["High"] + 0.05
    payer = mart.groupby("insurance_type")["diagnosed"].mean()
    assert payer.loc["private"] > payer.loc["uninsured"] + 0.05


def test_intervention_is_conditional_and_authorization_semantics_are_valid(project_root):
    mart = pd.read_csv(project_root / "data" / "marts" / "cleaned" / "mart_delay_scored_cleaned.csv")
    diagnosed = mart.loc[mart["diagnosis_date"].notna()]
    intervention_rate = diagnosed["intervention_date"].notna().mean()
    assert 0.20 < intervention_rate < 0.80
    by_severity = diagnosed.assign(intervened=diagnosed["intervention_date"].notna()).groupby("chd_severity")["intervened"].mean()
    assert by_severity.loc["Complex"] > by_severity.loc["Moderate"] > by_severity.loc["Simple"]

    uninsured = mart.loc[mart["insurance_type"].eq("uninsured") & mart["referral_date"].notna()]
    allowed = {"self_pay_cleared", "financial_assistance_pending", "financial_barrier"}
    assert set(uninsured["authorization_status"]).issubset(allowed)
