"""CHD type -> severity bucket for segmentation (project-defined, documented)."""

from __future__ import annotations

# Critical / complex lesions (typical need for earlier specialist/cardiology closure)
COMPLEX = {
    "Hypoplastic Left Heart Syndrome",
    "Transposition of the Great Arteries",
    "Tricuspid Atresia",
    "Double Outlet Right Ventricle (DORV)",
    "Tetralogy of Fallot",
    "Other complex CHD",
}

SIMPLE = {
    "Patent Ductus Arteriosus (PDA)",
    "Atrial Septal Defect (ASD)",
    "Ventricular Septal Defect (VSD)",
}

# Lesion often needing intervention but not grouped with single-ventricle physiology in this demo
MODERATE = {
    "Coarctation of the Aorta",
}


def severity_bucket(chd_type: str | float | None) -> str:
    if chd_type is None or (isinstance(chd_type, float) and str(chd_type) == "nan"):
        return "Unknown"
    s = str(chd_type).strip()
    if s in COMPLEX:
        return "Complex"
    if s in SIMPLE:
        return "Simple"
    if s in MODERATE:
        return "Moderate"
    return "Unknown"


def age_band(age_years: float | None) -> str:
    if age_years is None or str(age_years) in ("nan", "NaN"):
        return "Unknown"
    try:
        a = float(age_years)
    except (TypeError, ValueError):
        return "Unknown"
    if a <= 2:
        return "0-2"
    if a <= 5:
        return "3-5"
    if a <= 12:
        return "6-12"
    return "13+"


def cohort_era(symptom_year: float | None) -> str:
    if symptom_year is None or str(symptom_year) == "nan":
        return "Unknown"
    try:
        y = int(symptom_year)
    except (TypeError, ValueError):
        return "Unknown"
    return "2017-2020" if y < 2021 else "2021+"
