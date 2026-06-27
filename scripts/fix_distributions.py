"""
fix_distributions.py

Fixes three unrealistic distributions in the CHD dataset:

1. CHD TYPE — was perfectly uniform (~10% each, 10 types)
   Real-world prevalence (AHA / CDC birth defects surveillance):
     VSD  32%  |  ASD  13%  |  PDA   8%  |  ToF   6%  |  CoA   6%
     TGA   4%  |  HLHS  3%  |  TA    2%  |  DORV  2%  |  Other 24%

2. INSURANCE — Private was 50%, Medicaid 35%
   Real-world pediatric (HCUP KID 2019): Medicaid ~45%, Private ~40%

3. RACE — perfectly uniform 20% each (obviously synthetic)
   US pediatric population (Census / HCUP):
     White 52%  |  Black 15%  |  Other 18%  |  Asian 6%  |  Unknown 9%
"""

import numpy as np
import pandas as pd
from pathlib import Path

SEED = 42
rng = np.random.default_rng(SEED)

ROOT = Path(__file__).resolve().parents[1]

# ── 1. CHD TYPE DISTRIBUTION ───────────────────────────────────────────────

CHD_TYPES = [
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

# Real-world approximate prevalence weights (sums to 1)
CHD_WEIGHTS = [0.32, 0.13, 0.08, 0.06, 0.06, 0.04, 0.03, 0.02, 0.02, 0.24]

# ── 2. INSURANCE DISTRIBUTION ──────────────────────────────────────────────

INSURANCE_TYPES   = ["medicaid", "private", "uninsured", "other"]
INSURANCE_WEIGHTS = [0.45,       0.40,      0.10,        0.05]

# ── 3. RACE DISTRIBUTION ───────────────────────────────────────────────────

RACE_TYPES   = ["White", "Black", "Other", "Asian", "Unknown"]
RACE_WEIGHTS = [0.52,    0.15,    0.18,    0.06,    0.09]


def resample(series: pd.Series, categories, weights, rng) -> pd.Series:
    """Resample a categorical column to match target weights, preserving index."""
    n = len(series)
    new_vals = rng.choice(categories, size=n, p=weights)
    return pd.Series(new_vals, index=series.index)


# ── Update mart ────────────────────────────────────────────────────────────

mart_path = ROOT / "data/marts/cleaned/mart_delay_scored_cleaned.csv"
mart = pd.read_csv(mart_path)
print(f"Mart loaded: {len(mart)} rows")

print("\nBEFORE:")
print("chd_type:\n", mart["chd_type"].value_counts().to_string())
print("\ninsurance_type:\n", mart["insurance_type"].value_counts().to_string())

mart["chd_type"]      = resample(mart["chd_type"],      CHD_TYPES,      CHD_WEIGHTS,      rng)
mart["insurance_type"] = resample(mart["insurance_type"], INSURANCE_TYPES, INSURANCE_WEIGHTS, rng)

print("\nAFTER:")
print("chd_type %:\n", (mart["chd_type"].value_counts() / len(mart) * 100).round(1).to_string())
print("\ninsurance_type %:\n", (mart["insurance_type"].value_counts() / len(mart) * 100).round(1).to_string())

mart.to_csv(mart_path, index=False)
print(f"\nMart saved -> {mart_path}")


# ── Update raw patients file (race + insurance) ────────────────────────────

pts_path = ROOT / "data/raw/patients(Main Table).csv"
pts = pd.read_csv(pts_path)
print(f"\nPatients loaded: {len(pts)} rows")

print("\nBEFORE race %:\n", (pts["race"].value_counts() / len(pts) * 100).round(1).to_string())

pts["race"] = resample(pts["race"], RACE_TYPES, RACE_WEIGHTS, rng)

# Also fix insurance in patients file to match mart logic
if "insurance_type" in pts.columns:
    pts["insurance_type"] = resample(pts["insurance_type"], INSURANCE_TYPES, INSURANCE_WEIGHTS, rng)

print("\nAFTER race %:\n", (pts["race"].value_counts() / len(pts) * 100).round(1).to_string())

pts.to_csv(pts_path, index=False)
print(f"Patients saved -> {pts_path}")


# ── Update conditions.csv chd_type to match mart ──────────────────────────

cond_path = ROOT / "data/raw/conditions.csv"
cond = pd.read_csv(cond_path)
print(f"\nConditions loaded: {len(cond)} rows")

# Build patient->chd_type map from updated mart
chd_map = mart.set_index("patient_id")["chd_type"].to_dict()

# Only update rows that correspond to CHD conditions
chd_condition_mask = cond["condition"].str.contains(
    "Defect|Atresia|Syndrome|Fallot|Transposition|Arteriosus|Coarctation|Ventricle|DORV|complex",
    case=False, na=False
)

cond.loc[chd_condition_mask, "condition"] = (
    cond.loc[chd_condition_mask, "patient_id"]
    .map(chd_map)
    .fillna(cond.loc[chd_condition_mask, "condition"])
)

cond.to_csv(cond_path, index=False)
print(f"Conditions saved -> {cond_path}")

print("\nDone. All distributions updated to real-world benchmarks.")
