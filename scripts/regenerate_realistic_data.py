"""Generate the complete synthetic EHR dataset from one source of truth.

The project uses an enriched CHD operations cohort. It is intentionally not a
population-prevalence sample. Every downstream staging table and the patient
pathway mart is rebuilt from the raw tables generated here.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
AS_OF = pd.Timestamp("2025-12-31")

N_PATIENTS = 100_000
N_CHD = 15_000
N_ENCOUNTERS = 240_000
N_OBSERVATIONS = 720_000
N_REFERRALS = 50_000
N_CONDITIONS = 20_000
N_PROCEDURES = 7_500
N_ORGANIZATIONS = 40
N_PROVIDERS = 320

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
STAGING = ROOT / "data" / "staging"
MART = ROOT / "data" / "marts" / "cleaned" / "mart_delay_scored_cleaned.csv"

REGIONS = np.array(["North", "South", "East", "West", "Central"])
REGION_PROBS = np.array([0.18, 0.25, 0.17, 0.19, 0.21])
REGION_SVI = {"North": 0.38, "South": 0.66, "East": 0.48, "West": 0.43, "Central": 0.56}
REGION_COORDS = {
    "North": (42.2, -93.4),
    "South": (31.0, -90.8),
    "East": (39.8, -76.8),
    "West": (37.4, -119.7),
    "Central": (39.1, -97.4),
}

CHD_TYPES = np.array(
    [
        "Ventricular Septal Defect (VSD)",
        "Atrial Septal Defect (ASD)",
        "Patent Ductus Arteriosus (PDA)",
        "Tetralogy of Fallot",
        "Coarctation of the Aorta",
        "Transposition of the Great Arteries",
        "Hypoplastic Left Heart Syndrome",
        "Tricuspid Atresia",
        "Double Outlet Right Ventricle (DORV)",
        "Other complex CHD",
    ]
)
CHD_WEIGHTS = np.array([0.32, 0.13, 0.08, 0.06, 0.06, 0.04, 0.03, 0.02, 0.02, 0.24])
SEVERITY_MAP = {
    "Ventricular Septal Defect (VSD)": "Simple",
    "Atrial Septal Defect (ASD)": "Simple",
    "Patent Ductus Arteriosus (PDA)": "Simple",
    "Tetralogy of Fallot": "Moderate",
    "Coarctation of the Aorta": "Moderate",
    "Transposition of the Great Arteries": "Complex",
    "Hypoplastic Left Heart Syndrome": "Complex",
    "Tricuspid Atresia": "Complex",
    "Double Outlet Right Ventricle (DORV)": "Complex",
    "Other complex CHD": "Complex",
}


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def categorical_from_probabilities(rng: np.random.Generator, labels: list[str], probs: np.ndarray) -> np.ndarray:
    draws = rng.random(len(probs))
    cutoffs = np.cumsum(probs, axis=1)
    indexes = (draws[:, None] > cutoffs).sum(axis=1)
    return np.asarray(labels, dtype=object)[indexes]


def random_dates(rng: np.random.Generator, start: str, end: str, n: int) -> pd.DatetimeIndex:
    lo = pd.Timestamp(start).value // 86_400_000_000_000
    hi = pd.Timestamp(end).value // 86_400_000_000_000
    return pd.to_datetime(rng.integers(lo, hi + 1, size=n), unit="D")


def lognormal_days(
    rng: np.random.Generator,
    medians: np.ndarray,
    sigma: float,
    low: int,
    high: int,
) -> np.ndarray:
    values = rng.lognormal(np.log(np.maximum(medians, 0.1)), sigma)
    return np.clip(np.rint(values), low, high).astype(int)


def build_organizations(rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    capacity_values = {"low_capacity": 900, "standard_capacity": 1_700, "high_capacity": 2_800}
    for i in range(N_ORGANIZATIONS):
        region = REGIONS[i % len(REGIONS)]
        region_shift = {"South": -0.10, "Central": -0.04, "North": 0.05, "East": 0.03, "West": 0.06}[region]
        high_p = np.clip(0.22 + region_shift, 0.08, 0.38)
        low_p = np.clip(0.25 - region_shift, 0.12, 0.42)
        capacity = rng.choice(
            ["low_capacity", "standard_capacity", "high_capacity"],
            p=[low_p, 1 - low_p - high_p, high_p],
        )
        lat, lon = REGION_COORDS[region]
        rows.append(
            {
                "org_id": f"ORG{i + 1:03d}",
                "org_name": f"Regional Care Network {i + 1}",
                "org_type": rng.choice(["Community Health Center", "Hospital", "Clinic"], p=[0.45, 0.35, 0.20]),
                "clinic_region": region,
                "provider_capacity_tier": capacity,
                "annual_specialist_slots": capacity_values[capacity] + int(rng.integers(-150, 151)),
                "lat": round(lat + rng.normal(0, 1.2), 6),
                "lon": round(lon + rng.normal(0, 1.5), 6),
            }
        )
    return pd.DataFrame(rows)


def build_providers(rng: np.random.Generator, orgs: pd.DataFrame) -> pd.DataFrame:
    specialties = ["Pediatrics", "Family Medicine", "Pediatric Cardiology", "Cardiology", "Emergency Medicine", "Pulmonology"]
    probs = [0.30, 0.22, 0.18, 0.10, 0.12, 0.08]
    rows = []
    for i in range(N_PROVIDERS):
        org = orgs.iloc[i % len(orgs)]
        specialty = "Pediatric Cardiology" if i < N_ORGANIZATIONS else (
            "Pediatrics" if i < 2 * N_ORGANIZATIONS else rng.choice(specialties, p=probs)
        )
        rows.append(
            {
                "provider_id": f"PRV{i + 1:04d}",
                "provider_name": f"Clinician {i + 1:03d}",
                "specialty": specialty,
                "org_id": org["org_id"],
            }
        )
    return pd.DataFrame(rows)


def build_patients(
    rng: np.random.Generator,
    orgs: pd.DataFrame,
) -> tuple[pd.DataFrame, np.ndarray]:
    patient_ids = np.arange(10_000_001, 10_000_001 + N_PATIENTS)
    regions = rng.choice(REGIONS, N_PATIENTS, p=REGION_PROBS)
    region_svi = np.array([REGION_SVI[x] for x in regions])
    individual_svi = rng.beta(2.2, 2.6, N_PATIENTS)
    svi = np.clip(0.55 * individual_svi + 0.45 * region_svi + rng.normal(0, 0.06, N_PATIENTS), 0.01, 0.99)

    chd_idx = rng.choice(N_PATIENTS, N_CHD, replace=False)
    has_chd = np.zeros(N_PATIENTS, dtype=int)
    has_chd[chd_idx] = 1
    chd_type = np.full(N_PATIENTS, None, dtype=object)
    chd_type[chd_idx] = rng.choice(CHD_TYPES, N_CHD, p=CHD_WEIGHTS)

    contact = pd.Series(random_dates(rng, "2019-01-01", "2024-12-31", N_PATIENTS))
    contact.iloc[chd_idx] = random_dates(rng, "2019-01-01", "2023-12-31", N_CHD)
    age_at_contact = rng.choice(np.arange(18), N_PATIENTS, p=np.array([0.12, 0.09, 0.07] + [0.72 / 15] * 15))
    age_at_contact[chd_idx] = rng.choice(np.arange(18), N_CHD, p=np.array([0.28, 0.13, 0.08] + [0.51 / 15] * 15))
    dob = contact - pd.to_timedelta(age_at_contact * 365 + rng.integers(0, 365, N_PATIENTS), unit="D")
    age_as_of = np.floor((AS_OF - dob).dt.days / 365.2425).astype(int)

    payer_logits = np.column_stack(
        [
            1.7 - 1.8 * svi,
            0.3 + 1.1 * svi,
            -1.4 + 1.3 * svi,
            np.full(N_PATIENTS, -1.0),
        ]
    )
    payer_probs = np.exp(payer_logits - payer_logits.max(axis=1, keepdims=True))
    payer_probs /= payer_probs.sum(axis=1, keepdims=True)
    insurance = categorical_from_probabilities(rng, ["private", "medicaid", "uninsured", "other"], payer_probs)

    income_score = svi + rng.normal(0, 0.16, N_PATIENTS)
    income = np.select(
        [income_score >= 0.72, income_score >= 0.50, income_score >= 0.30],
        ["<25k", "25-50k", "50-75k"],
        default="75k+",
    )
    education_score = svi + rng.normal(0, 0.18, N_PATIENTS)
    education = np.select(
        [education_score >= 0.72, education_score >= 0.48, education_score >= 0.27],
        ["LessThanHS", "HighSchool", "SomeCollege"],
        default="CollegePlus",
    )

    region_orgs = {region: orgs.loc[orgs["clinic_region"].eq(region)].copy() for region in REGIONS}
    assigned_org = []
    for region in regions:
        choices = region_orgs[region]
        weight = choices["provider_capacity_tier"].map(
            {"low_capacity": 0.8, "standard_capacity": 1.0, "high_capacity": 1.25}
        ).to_numpy(dtype=float)
        assigned_org.append(rng.choice(choices["org_id"].to_numpy(), p=weight / weight.sum()))
    assigned_org = np.asarray(assigned_org)
    org_capacity = orgs.set_index("org_id")["provider_capacity_tier"]
    capacity = pd.Series(assigned_org).map(org_capacity).to_numpy()
    capacity_distance = pd.Series(capacity).map(
        {"low_capacity": 13.0, "standard_capacity": 5.0, "high_capacity": 0.0}
    ).to_numpy()
    distance = np.clip(rng.gamma(2.0, 8.0, N_PATIENTS) + 24 * svi + capacity_distance, 1, 180).round(1)

    patients = pd.DataFrame(
        {
            "patient_id": patient_ids,
            "dob": dob.dt.strftime("%Y-%m-%d"),
            "age_years": age_as_of,
            "sex": rng.choice(["F", "M"], N_PATIENTS),
            "race": rng.choice(["White", "Black", "Other", "Asian", "Unknown"], N_PATIENTS, p=[0.50, 0.16, 0.18, 0.08, 0.08]),
            "ethnicity": rng.choice(["Not Hispanic", "Hispanic", "Unknown"], N_PATIENTS, p=[0.67, 0.27, 0.06]),
            "zip_code": [f"{i + 1}{z:04d}" for i, z in zip(pd.Categorical(regions, categories=REGIONS).codes, rng.integers(0, 10_000, N_PATIENTS))],
            "income_bracket": income,
            "education_level": education,
            "insurance_type": insurance,
            "svi_index": svi.round(3),
            "has_chd": has_chd,
            "chd_type": chd_type,
            "first_contact_date": contact.dt.strftime("%Y-%m-%d"),
            "clinic_region": regions,
            "assigned_specialist_org_id": assigned_org,
            "distance_to_specialist_miles": distance,
        }
    )
    return patients, chd_idx


def build_chd_pathway(
    rng: np.random.Generator,
    patients: pd.DataFrame,
    chd_idx: np.ndarray,
    orgs: pd.DataFrame,
    providers: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    chd = patients.iloc[chd_idx].copy().reset_index(drop=True)
    n = len(chd)
    severity = chd["chd_type"].map(SEVERITY_MAP)
    svi = chd["svi_index"].to_numpy(float)
    distance = chd["distance_to_specialist_miles"].to_numpy(float)
    payer = chd["insurance_type"].to_numpy()
    org_capacity = orgs.set_index("org_id")["provider_capacity_tier"]
    capacity = chd["assigned_specialist_org_id"].map(org_capacity).to_numpy()

    severity_score = severity.map({"Simple": 0.0, "Moderate": 0.8, "Complex": 1.45}).to_numpy()
    critical_p = sigmoid(-2.5 + 1.8 * severity_score)
    urgent_p = sigmoid(-0.4 + 1.0 * severity_score)
    draw = rng.random(n)
    priority = np.where(draw < critical_p, "critical", np.where(draw < critical_p + (1 - critical_p) * urgent_p, "urgent", "routine"))
    priority_score = pd.Series(priority).map({"routine": 0.0, "urgent": 0.7, "critical": 1.3}).to_numpy()

    private = payer == "private"
    uninsured = payer == "uninsured"
    low_capacity = capacity == "low_capacity"
    high_capacity = capacity == "high_capacity"

    has_pcp = rng.random(n) < sigmoid(2.25 + 0.30 * severity_score - 0.75 * svi - 0.35 * uninsured)
    has_referral = has_pcp & (
        rng.random(n) < sigmoid(0.25 + 0.85 * severity_score + 0.35 * priority_score - 0.65 * svi - 0.25 * uninsured)
    )

    authorization = np.full(n, "not_started", dtype=object)
    referred = np.flatnonzero(has_referral)
    for i in referred:
        if payer[i] == "uninsured":
            probs = np.array([0.46, 0.34, 0.20]) + np.array([-0.18, 0.05, 0.13]) * svi[i]
            probs = probs / probs.sum()
            authorization[i] = rng.choice(["self_pay_cleared", "financial_assistance_pending", "financial_barrier"], p=probs)
        elif payer[i] in {"private", "other"} and rng.random() < 0.34:
            authorization[i] = "not_required"
        else:
            denial = 0.05 + 0.07 * svi[i]
            pending = 0.12 + 0.18 * svi[i]
            authorization[i] = rng.choice(["approved", "pending", "denied"], p=[1 - pending - denial, pending, denial])

    access_block = np.isin(authorization, ["pending", "denied", "financial_assistance_pending", "financial_barrier"])
    specialist_prob = sigmoid(
        1.35 + 0.35 * priority_score + 0.25 * severity_score + 0.32 * private - 0.90 * svi
        - 0.010 * distance - 0.75 * low_capacity + 0.35 * high_capacity - 1.35 * access_block
    )
    has_specialist = has_referral & (rng.random(n) < specialist_prob)
    has_diagnosis = has_specialist & (
        rng.random(n) < sigmoid(0.45 + 0.50 * severity_score + 0.20 * priority_score - 0.18 * svi)
    )
    intervention_prob = np.select(
        [severity.eq("Complex"), severity.eq("Moderate")],
        [0.68, 0.42],
        default=0.16,
    )
    intervention_prob = np.clip(intervention_prob + 0.10 * priority_score - 0.06 * svi, 0.05, 0.90)
    has_intervention = has_diagnosis & (rng.random(n) < intervention_prob)

    symptom = pd.to_datetime(chd["first_contact_date"])
    symptom_median = np.select([severity.eq("Complex"), severity.eq("Moderate")], [5.0, 13.0], default=28.0) * (1 + 0.22 * svi)
    pcp_wait = lognormal_days(rng, symptom_median, 0.68, 1, 120)
    referral_median = np.select([priority == "critical", priority == "urgent"], [2.0, 6.0], default=15.0)
    referral_median *= 1 + 0.28 * svi + 0.18 * uninsured
    referral_wait = lognormal_days(rng, referral_median, 0.62, 1, 90)
    specialist_median = np.select([priority == "critical", priority == "urgent"], [10.0, 24.0], default=43.0)
    specialist_median *= 1 + 0.36 * svi + 0.28 * (payer == "medicaid") + 0.42 * uninsured
    specialist_median *= np.where(low_capacity, 1.35, np.where(high_capacity, 0.78, 1.0))
    specialist_median += distance / 20
    specialist_wait = lognormal_days(rng, specialist_median, 0.70, 2, 210)
    diagnosis_median = np.select([severity.eq("Complex"), severity.eq("Moderate")], [4.0, 8.0], default=13.0)
    diagnosis_wait = lognormal_days(rng, diagnosis_median, 0.62, 0, 75)
    intervention_median = np.select([severity.eq("Complex"), severity.eq("Moderate")], [28.0, 58.0], default=105.0)
    intervention_wait = lognormal_days(rng, intervention_median, 0.68, 5, 300)

    pcp_date = symptom + pd.to_timedelta(pcp_wait, unit="D")
    referral_date = pcp_date + pd.to_timedelta(referral_wait, unit="D")
    specialist_date = referral_date + pd.to_timedelta(specialist_wait, unit="D")
    diagnosis_date = specialist_date + pd.to_timedelta(diagnosis_wait, unit="D")
    intervention_date = diagnosis_date + pd.to_timedelta(intervention_wait, unit="D")

    specialist_by_org = providers.loc[providers["specialty"].isin(["Pediatric Cardiology", "Cardiology"])].groupby("org_id")["provider_id"].apply(list)
    primary_by_region = (
        providers.merge(orgs[["org_id", "clinic_region"]], on="org_id")
        .loc[lambda x: x["specialty"].isin(["Pediatrics", "Family Medicine"])]
        .groupby("clinic_region")["provider_id"].apply(list)
    )
    all_specialists = providers.loc[providers["specialty"].isin(["Pediatric Cardiology", "Cardiology"]), "provider_id"].tolist()
    pcp_provider = np.array([rng.choice(primary_by_region[r]) for r in chd["clinic_region"]])
    specialist_provider = np.array(
        [rng.choice(specialist_by_org.get(org, all_specialists)) for org in chd["assigned_specialist_org_id"]]
    )
    provider_org = providers.set_index("provider_id")["org_id"]

    appointment = np.full(n, "not_referred", dtype=object)
    appointment[has_specialist] = "completed"
    incomplete = has_referral & ~has_specialist
    incomplete_probs = np.column_stack(
        [
            np.clip(0.38 - 0.18 * svi, 0.10, 0.45),
            np.clip(0.18 + 0.10 * low_capacity, 0.12, 0.34),
            np.clip(0.20 + 0.10 * svi, 0.16, 0.36),
            np.clip(0.24 + 0.10 * uninsured, 0.18, 0.38),
        ]
    )
    incomplete_probs /= incomplete_probs.sum(axis=1, keepdims=True)
    appointment[incomplete] = categorical_from_probabilities(
        rng,
        ["scheduled_pending", "cancelled", "no_show", "unable_to_contact"],
        incomplete_probs[incomplete],
    )

    patient_updates = pd.DataFrame(
        {
            "patient_id": chd["patient_id"],
            "chd_severity": severity,
            "referral_priority": priority,
            "symptom_onset_date": symptom,
            "has_pcp": has_pcp,
            "has_referral": has_referral,
            "has_specialist": has_specialist,
            "has_diagnosis": has_diagnosis,
            "has_intervention": has_intervention,
            "pcp_date": pcp_date,
            "referral_date": referral_date,
            "specialist_date": specialist_date,
            "diagnosis_date": diagnosis_date,
            "intervention_date": intervention_date,
            "pcp_provider": pcp_provider,
            "specialist_provider": specialist_provider,
            "authorization_status": authorization,
            "specialist_appointment_status": appointment,
        }
    )

    encounter_rows = []
    for i, row in patient_updates.iterrows():
        patient_id = int(row["patient_id"])
        encounter_rows.append((patient_id, row["symptom_onset_date"], "CHD symptom documented", row["pcp_provider"], "symptom", "outpatient", 0))
        if row["has_pcp"]:
            encounter_rows.append((patient_id, row["pcp_date"], "Primary care CHD assessment", row["pcp_provider"], "pcp", "outpatient", 0))
        if row["has_specialist"]:
            encounter_rows.append((patient_id, row["specialist_date"], "Pediatric cardiology consultation", row["specialist_provider"], "specialist", "specialty", 0))

    chd_encounters = pd.DataFrame(
        encounter_rows,
        columns=["patient_id", "encounter_datetime", "reason", "provider_id", "care_stage", "encounter_type", "no_show"],
    )
    chd_encounters["org_id"] = chd_encounters["provider_id"].map(provider_org)

    referrals = patient_updates.loc[patient_updates["has_referral"]].copy()
    chd_referrals = pd.DataFrame(
        {
            "patient_id": referrals["patient_id"].astype(int),
            "from_provider_id": referrals["pcp_provider"],
            "to_provider_id": referrals["specialist_provider"],
            "referral_datetime": referrals["referral_date"],
            "expected_appointment": referrals["referral_date"] + pd.to_timedelta(
                np.where(referrals["referral_priority"].eq("critical"), 7, np.where(referrals["referral_priority"].eq("urgent"), 14, 45)), unit="D"
            ),
            "completed": referrals["has_specialist"].astype(int),
            "referral_category": "CHD",
            "referral_priority": referrals["referral_priority"],
            "authorization_status": referrals["authorization_status"],
            "appointment_status": referrals["specialist_appointment_status"],
        }
    )

    diagnosed = patient_updates.loc[patient_updates["has_diagnosis"]].copy()
    diagnosed_type = chd.set_index("patient_id").loc[diagnosed["patient_id"], "chd_type"].to_numpy()
    chd_conditions = pd.DataFrame(
        {
            "patient_id": diagnosed["patient_id"].astype(int),
            "condition": diagnosed_type,
            "condition_start": diagnosed["diagnosis_date"],
            "diagnosed_by_provider": diagnosed["specialist_provider"],
            "condition_category": "CHD",
        }
    )

    intervened = patient_updates.loc[patient_updates["has_intervention"]].copy()
    intervention_severity = intervened["chd_severity"]
    procedure_type = np.where(
        intervention_severity.eq("Complex"),
        rng.choice(["Corrective surgery", "Palliative procedure", "Catheter intervention"], len(intervened), p=[0.46, 0.32, 0.22]),
        rng.choice(["Catheter intervention", "Corrective surgery", "Clinical monitoring procedure"], len(intervened), p=[0.50, 0.30, 0.20]),
    )
    chd_procedures = pd.DataFrame(
        {
            "patient_id": intervened["patient_id"].astype(int),
            "procedure_datetime": intervened["intervention_date"],
            "procedure_type": procedure_type,
            "provider_id": intervened["specialist_provider"],
            "org_id": intervened["specialist_provider"].map(provider_org),
            "urgent_flag": intervened["referral_priority"].isin(["urgent", "critical"]).astype(int),
            "procedure_category": "CHD intervention",
        }
    )
    return patient_updates, chd_encounters, chd_referrals, chd_conditions, chd_procedures


def finish_raw_tables(
    rng: np.random.Generator,
    patients: pd.DataFrame,
    providers: pd.DataFrame,
    pathway: pd.DataFrame,
    chd_encounters: pd.DataFrame,
    chd_referrals: pd.DataFrame,
    chd_conditions: pd.DataFrame,
    chd_procedures: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    provider_org = providers.set_index("provider_id")["org_id"]
    patient_contact = pd.to_datetime(patients.set_index("patient_id")["first_contact_date"])
    patient_dob = pd.to_datetime(patients.set_index("patient_id")["dob"])
    all_patient_ids = patients["patient_id"].to_numpy()
    all_provider_ids = providers["provider_id"].to_numpy()

    remaining = N_ENCOUNTERS - len(chd_encounters)
    if remaining < 0:
        raise ValueError("Pathway encounters exceed configured encounter count")
    filler_patient = rng.choice(all_patient_ids, remaining)
    start = patient_contact.loc[filler_patient].reset_index(drop=True)
    max_days = (AS_OF - start).dt.days.to_numpy()
    offsets = np.array([rng.integers(0, max(day, 1) + 1) for day in max_days])
    filler_date = start + pd.to_timedelta(offsets, unit="D")
    filler_provider = rng.choice(all_provider_ids, remaining)
    filler_encounters = pd.DataFrame(
        {
            "patient_id": filler_patient,
            "encounter_datetime": filler_date,
            "reason": rng.choice(["Routine follow-up", "Respiratory symptoms", "Preventive visit", "Acute complaint", "Medication review"], remaining),
            "provider_id": filler_provider,
            "care_stage": "general",
            "encounter_type": rng.choice(["outpatient", "emergency", "inpatient", "telehealth"], remaining, p=[0.61, 0.15, 0.10, 0.14]),
            "no_show": rng.choice([0, 1], remaining, p=[0.91, 0.09]),
            "org_id": pd.Series(filler_provider).map(provider_org).to_numpy(),
        }
    )
    encounters = pd.concat([chd_encounters, filler_encounters], ignore_index=True)
    encounters.insert(0, "encounter_id", [f"ENC{i + 1:07d}" for i in range(len(encounters))])
    encounters["encounter_datetime"] = pd.to_datetime(encounters["encounter_datetime"]).dt.strftime("%Y-%m-%dT%H:%M:%S")

    remaining = N_REFERRALS - len(chd_referrals)
    referral_patient = rng.choice(all_patient_ids, remaining)
    referral_start = patient_contact.loc[referral_patient].reset_index(drop=True)
    referral_max = np.maximum((AS_OF - referral_start).dt.days.to_numpy() - 60, 1)
    referral_offsets = np.array([rng.integers(0, day + 1) for day in referral_max])
    referral_dates = referral_start + pd.to_timedelta(referral_offsets, unit="D")
    from_provider = rng.choice(all_provider_ids, remaining)
    to_provider = rng.choice(all_provider_ids, remaining)
    general_referrals = pd.DataFrame(
        {
            "patient_id": referral_patient,
            "from_provider_id": from_provider,
            "to_provider_id": to_provider,
            "referral_datetime": referral_dates,
            "expected_appointment": referral_dates + pd.to_timedelta(rng.integers(7, 61, remaining), unit="D"),
            "completed": rng.choice([0, 1], remaining, p=[0.24, 0.76]),
            "referral_category": "general",
            "referral_priority": rng.choice(["routine", "urgent"], remaining, p=[0.86, 0.14]),
            "authorization_status": rng.choice(["not_required", "approved", "pending", "denied"], remaining, p=[0.38, 0.48, 0.11, 0.03]),
            "appointment_status": "general_referral",
        }
    )
    referrals = pd.concat([chd_referrals, general_referrals], ignore_index=True)
    referrals.insert(0, "referral_id", [f"REF{i + 1:07d}" for i in range(len(referrals))])
    for col in ["referral_datetime", "expected_appointment"]:
        referrals[col] = pd.to_datetime(referrals[col]).dt.strftime("%Y-%m-%dT%H:%M:%S")

    remaining = N_CONDITIONS - len(chd_conditions)
    condition_patient = rng.choice(all_patient_ids, remaining)
    condition_start = patient_contact.loc[condition_patient].reset_index(drop=True)
    condition_max = np.maximum((AS_OF - condition_start).dt.days.to_numpy(), 1)
    condition_dates = condition_start + pd.to_timedelta(
        np.array([rng.integers(0, day + 1) for day in condition_max]), unit="D"
    )
    general_conditions = pd.DataFrame(
        {
            "patient_id": condition_patient,
            "condition": rng.choice(["Asthma", "Hypertension", "Respiratory infection", "Diabetes", "Anemia"], remaining),
            "condition_start": condition_dates,
            "diagnosed_by_provider": rng.choice(all_provider_ids, remaining),
            "condition_category": "general",
        }
    )
    conditions = pd.concat([chd_conditions, general_conditions], ignore_index=True)
    conditions.insert(0, "condition_id", [f"CON{i + 1:07d}" for i in range(len(conditions))])
    conditions["condition_start"] = pd.to_datetime(conditions["condition_start"]).dt.strftime("%Y-%m-%dT%H:%M:%S")

    remaining = N_PROCEDURES - len(chd_procedures)
    procedure_patient = rng.choice(all_patient_ids, remaining)
    procedure_start = patient_contact.loc[procedure_patient].reset_index(drop=True)
    procedure_max = np.maximum((AS_OF - procedure_start).dt.days.to_numpy(), 1)
    procedure_dates = procedure_start + pd.to_timedelta(
        np.array([rng.integers(0, day + 1) for day in procedure_max]), unit="D"
    )
    procedure_provider = rng.choice(all_provider_ids, remaining)
    general_procedures = pd.DataFrame(
        {
            "patient_id": procedure_patient,
            "procedure_datetime": procedure_dates,
            "procedure_type": rng.choice(["Imaging", "Laboratory procedure", "Medication administration", "Minor procedure"], remaining),
            "provider_id": procedure_provider,
            "org_id": pd.Series(procedure_provider).map(provider_org).to_numpy(),
            "urgent_flag": rng.choice([0, 1], remaining, p=[0.86, 0.14]),
            "procedure_category": "general",
        }
    )
    procedures = pd.concat([chd_procedures, general_procedures], ignore_index=True)
    procedures.insert(0, "procedure_id", [f"PROC{i + 1:07d}" for i in range(len(procedures))])
    procedures["procedure_datetime"] = pd.to_datetime(procedures["procedure_datetime"]).dt.strftime("%Y-%m-%dT%H:%M:%S")

    encounter_repeat = np.repeat(np.arange(len(encounters)), N_OBSERVATIONS // N_ENCOUNTERS)
    if len(encounter_repeat) != N_OBSERVATIONS:
        raise ValueError("Observation count must be a whole multiple of encounter count")
    obs_enc = encounters.iloc[encounter_repeat].reset_index(drop=True)
    obs_patient = obs_enc["patient_id"].to_numpy()
    obs_date = pd.to_datetime(obs_enc["encounter_datetime"])
    age_days = (obs_date - patient_dob.loc[obs_patient].reset_index(drop=True)).dt.days.to_numpy()
    age_years = np.maximum(age_days / 365.2425, 0)
    observations = pd.DataFrame(
        {
            "observation_id": [f"OBS{i + 1:09d}" for i in range(N_OBSERVATIONS)],
            "encounter_id": obs_enc["encounter_id"],
            "patient_id": obs_patient,
            "obs_datetime": obs_date.dt.strftime("%Y-%m-%dT%H:%M:%S"),
            "heart_rate": np.clip(np.rint(122 - 2.2 * age_years + rng.normal(0, 12, N_OBSERVATIONS)), 55, 190).astype(int),
            "systolic_bp": np.clip(np.rint(82 + 1.7 * age_years + rng.normal(0, 9, N_OBSERVATIONS)), 60, 150).astype(int),
            "diastolic_bp": np.clip(np.rint(48 + 0.8 * age_years + rng.normal(0, 7, N_OBSERVATIONS)), 35, 100).astype(int),
            "spo2": np.clip(rng.normal(97.2, 1.8, N_OBSERVATIONS), 82, 100).round(1),
            "weight_kg": np.clip(3.4 + 3.0 * age_years + rng.normal(0, 4.5, N_OBSERVATIONS), 2.0, 100).round(2),
        }
    )
    return encounters, observations, referrals, conditions, procedures


def build_mart(
    patients: pd.DataFrame,
    orgs: pd.DataFrame,
    encounters: pd.DataFrame,
    referrals: pd.DataFrame,
    conditions: pd.DataFrame,
    procedures: pd.DataFrame,
    pathway: pd.DataFrame,
) -> pd.DataFrame:
    chd = patients.loc[patients["has_chd"].eq(1)].copy()
    symptom = encounters.loc[encounters["care_stage"].eq("symptom")].groupby("patient_id")["encounter_datetime"].min()
    pcp = encounters.loc[encounters["care_stage"].eq("pcp")].groupby("patient_id")["encounter_datetime"].min()
    specialist = encounters.loc[encounters["care_stage"].eq("specialist")].groupby("patient_id")["encounter_datetime"].min()
    chd_referral = referrals.loc[referrals["referral_category"].eq("CHD")].drop_duplicates("patient_id").set_index("patient_id")
    diagnosis = conditions.loc[conditions["condition_category"].eq("CHD")].groupby("patient_id")["condition_start"].min()
    intervention = procedures.loc[procedures["procedure_category"].eq("CHD intervention")].groupby("patient_id")["procedure_datetime"].min()

    mart = chd[["patient_id", "zip_code", "svi_index", "insurance_type", "chd_type", "clinic_region", "assigned_specialist_org_id", "distance_to_specialist_miles"]].copy()
    mart["symptom_onset_date"] = mart["patient_id"].map(symptom)
    mart["first_pcp_date"] = mart["patient_id"].map(pcp)
    mart["referral_date"] = mart["patient_id"].map(chd_referral["referral_datetime"])
    mart["specialist_date"] = mart["patient_id"].map(specialist)
    mart["diagnosis_date"] = mart["patient_id"].map(diagnosis)
    mart["intervention_date"] = mart["patient_id"].map(intervention)
    mart["chd_severity"] = mart["chd_type"].map(SEVERITY_MAP)
    priority = pathway.set_index("patient_id")["referral_priority"]
    mart["referral_priority"] = mart["patient_id"].map(priority)
    mart["provider_capacity_tier"] = mart["assigned_specialist_org_id"].map(orgs.set_index("org_id")["provider_capacity_tier"])
    mart["authorization_status"] = mart["patient_id"].map(chd_referral["authorization_status"]).fillna("not_started")
    mart["specialist_appointment_status"] = mart["patient_id"].map(chd_referral["appointment_status"]).fillna("not_referred")

    date_pairs = {
        "days_symptom_to_pcp_clean": ("symptom_onset_date", "first_pcp_date"),
        "days_pcp_to_referral_clean": ("first_pcp_date", "referral_date"),
        "days_referral_to_specialist_clean": ("referral_date", "specialist_date"),
        "days_specialist_to_diagnosis_clean": ("specialist_date", "diagnosis_date"),
        "days_diagnosis_to_intervention_clean": ("diagnosis_date", "intervention_date"),
    }
    for out, (start, end) in date_pairs.items():
        mart[out] = (pd.to_datetime(mart[end]) - pd.to_datetime(mart[start])).dt.days
    weights = {
        "days_symptom_to_pcp_clean": 0.25,
        "days_pcp_to_referral_clean": 0.30,
        "days_referral_to_specialist_clean": 0.20,
        "days_specialist_to_diagnosis_clean": 0.15,
        "days_diagnosis_to_intervention_clean": 0.10,
    }
    mart["delay_severity_score_clean"] = sum(pd.to_numeric(mart[col], errors="coerce").fillna(0) * weight for col, weight in weights.items()).round(2)
    mart = mart.drop(columns="assigned_specialist_org_id")
    date_cols = ["symptom_onset_date", "first_pcp_date", "referral_date", "specialist_date", "diagnosis_date", "intervention_date"]
    for col in date_cols:
        mart[col] = pd.to_datetime(mart[col], errors="coerce").dt.strftime("%Y-%m-%d")
    return mart


def write_staging(tables: dict[str, pd.DataFrame]) -> None:
    STAGING.mkdir(parents=True, exist_ok=True)
    loaded_at = "2026-06-28T00:00:00Z"
    for name, frame in tables.items():
        staged = frame.copy()
        for col in staged.select_dtypes(include=["object", "string"]).columns:
            if not col.endswith("_id") and "date" not in col and "datetime" not in col:
                staged[col] = staged[col].astype("string").str.strip().str.lower()
        staged["loaded_at"] = loaded_at
        staged.to_csv(STAGING / f"stg_{name}.csv", index=False)


def validate_before_write(
    patients: pd.DataFrame,
    encounters: pd.DataFrame,
    observations: pd.DataFrame,
    referrals: pd.DataFrame,
    conditions: pd.DataFrame,
    procedures: pd.DataFrame,
    providers: pd.DataFrame,
    orgs: pd.DataFrame,
    mart: pd.DataFrame,
) -> None:
    assert len(patients) == N_PATIENTS and patients["patient_id"].is_unique
    assert len(mart) == N_CHD and mart["patient_id"].is_unique
    assert len(encounters) == N_ENCOUNTERS and encounters["encounter_id"].is_unique
    assert len(observations) == N_OBSERVATIONS and observations["observation_id"].is_unique
    assert len(referrals) == N_REFERRALS and referrals["referral_id"].is_unique
    assert len(conditions) == N_CONDITIONS and conditions["condition_id"].is_unique
    assert len(procedures) == N_PROCEDURES and procedures["procedure_id"].is_unique
    assert set(encounters["patient_id"]).issubset(set(patients["patient_id"]))
    assert set(observations["encounter_id"]).issubset(set(encounters["encounter_id"]))
    assert set(referrals["patient_id"]).issubset(set(patients["patient_id"]))
    assert set(conditions["patient_id"]).issubset(set(patients["patient_id"]))
    assert set(procedures["patient_id"]).issubset(set(patients["patient_id"]))
    assert set(encounters["provider_id"]).issubset(set(providers["provider_id"]))
    assert set(providers["org_id"]).issubset(set(orgs["org_id"]))

    dob = pd.to_datetime(patients.set_index("patient_id")["dob"])
    assert (pd.to_datetime(patients.set_index("patient_id")["first_contact_date"]) >= dob).all()
    for table, date_col in [
        (encounters, "encounter_datetime"),
        (referrals, "referral_datetime"),
        (conditions, "condition_start"),
        (procedures, "procedure_datetime"),
    ]:
        event = pd.to_datetime(table[date_col])
        event_dob = dob.loc[table["patient_id"]].reset_index(drop=True)
        assert (event.reset_index(drop=True) >= event_dob).all()

    sequence = ["symptom_onset_date", "first_pcp_date", "referral_date", "specialist_date", "diagnosis_date", "intervention_date"]
    parsed = mart[sequence].apply(pd.to_datetime)
    for earlier, later in zip(sequence, sequence[1:]):
        comparable = parsed[earlier].notna() & parsed[later].notna()
        assert (parsed.loc[comparable, earlier] <= parsed.loc[comparable, later]).all()
        assert (~parsed[later].notna() | parsed[earlier].notna()).all()


def main() -> None:
    rng = np.random.default_rng(SEED)
    RAW.mkdir(parents=True, exist_ok=True)
    MART.parent.mkdir(parents=True, exist_ok=True)

    orgs = build_organizations(rng)
    providers = build_providers(rng, orgs)
    patients, chd_idx = build_patients(rng, orgs)
    pathway, chd_encounters, chd_referrals, chd_conditions, chd_procedures = build_chd_pathway(
        rng, patients, chd_idx, orgs, providers
    )
    encounters, observations, referrals, conditions, procedures = finish_raw_tables(
        rng, patients, providers, pathway, chd_encounters, chd_referrals, chd_conditions, chd_procedures
    )
    mart = build_mart(patients, orgs, encounters, referrals, conditions, procedures, pathway)
    validate_before_write(patients, encounters, observations, referrals, conditions, procedures, providers, orgs, mart)

    tables = {
        "patients": patients,
        "encounters": encounters,
        "observations": observations,
        "referrals": referrals,
        "conditions": conditions,
        "procedures": procedures,
        "providers": providers,
        "organizations": orgs,
    }
    raw_names = {"patients": "patients(Main Table).csv", **{name: f"{name}.csv" for name in tables if name != "patients"}}
    for name, frame in tables.items():
        frame.to_csv(RAW / raw_names[name], index=False)
    write_staging(tables)
    mart.to_csv(MART, index=False)

    counts = {col: int(mart[col].notna().sum()) for col in ["symptom_onset_date", "first_pcp_date", "referral_date", "specialist_date", "diagnosis_date", "intervention_date"]}
    print(f"Generated {len(patients):,} patients, including {len(mart):,} CHD pathway patients")
    print(f"Generated {len(encounters):,} encounters, {len(observations):,} observations, and {len(referrals):,} referrals")
    print("Pathway counts:", counts)
    print(f"Wrote raw, staging, and mart data under {ROOT / 'data'}")


if __name__ == "__main__":
    main()
