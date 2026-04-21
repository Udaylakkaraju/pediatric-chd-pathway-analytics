"""
Build the Coordination Failure Scorecard: leakage (conversion / drop-off) + time
(avg and median days among patients who complete each stage interval).

Inputs:
  - outputs/analytics/funnel metrics.csv
  - outputs/analytics/stage dropoff.csv
  - outputs/analytics/stage delay contribution.csv
  - data/marts/cleaned/mart_delay_scored_cleaned.csv (medians)

Output:
  - outputs/analytics/coordination_failure_scorecard.csv
"""

from __future__ import annotations

import _bootstrap_path  # noqa: F401
import csv
import statistics

from chd_analytics.paths import ANALYTICS, MART_CLEANED

MART = MART_CLEANED
FUNNEL = ANALYTICS / "funnel metrics.csv"
DROPOFF = ANALYTICS / "stage dropoff.csv"
DELAY_AVG = ANALYTICS / "stage delay contribution.csv"
OUT = ANALYTICS / "coordination_failure_scorecard.csv"

STAGES = [
    {
        "stage_key": "symptom_to_pcp",
        "label": "Symptom → PCP",
        "mart_col": "days_symptom_to_pcp_clean",
    },
    {
        "stage_key": "pcp_to_referral",
        "label": "PCP → Referral",
        "mart_col": "days_pcp_to_referral_clean",
    },
    {
        "stage_key": "referral_to_specialist",
        "label": "Referral → Specialist",
        "mart_col": "days_referral_to_specialist_clean",
    },
    {
        "stage_key": "specialist_to_diagnosis",
        "label": "Specialist → Diagnosis",
        "mart_col": "days_specialist_to_diagnosis_clean",
    },
]


def read_funnel_row() -> dict[str, str]:
    with FUNNEL.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        row = next(r)
    return row


def read_dropoff_map() -> dict[str, float]:
    m: dict[str, float] = {}
    with DROPOFF.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            stage = row["stage"].strip()
            m[stage] = float(row["drop_off_rate"])
    return m


def read_delay_avg_row() -> dict[str, float]:
    with DELAY_AVG.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        row = next(r)
    out: dict[str, float] = {}
    for k, v in row.items():
        if k is None:
            continue
        key = k.strip()
        if key and v not in (None, ""):
            out[key] = float(v)
    return out


def median_interval(mart_path: Path, col: str) -> tuple[float | None, int]:
    vals: list[float] = []
    with mart_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw = row.get(col, "").strip().strip('"')
            if raw == "" or raw.upper() == "NULL":
                continue
            try:
                x = float(raw)
            except ValueError:
                continue
            if x >= 0:
                vals.append(x)
    if not vals:
        return None, 0
    return statistics.median(vals), len(vals)


def main() -> None:
    funnel = read_funnel_row()
    # Counts at each funnel node
    n_sym = int(funnel["symptom"])
    n_pcp = int(funnel["pcp"])
    n_ref = int(funnel["referral"])
    n_spec = int(funnel["specialist"])
    n_dx = int(funnel["diagnosis"])

    conversions = [
        ("symptom_to_pcp", n_sym, n_pcp, float(funnel["symptom_to_pcp_conversion"])),
        ("pcp_to_referral", n_pcp, n_ref, float(funnel["pcp_to_referral_conversion"])),
        ("referral_to_specialist", n_ref, n_spec, float(funnel["referral_to_specialist_conversion"])),
        ("specialist_to_diagnosis", n_spec, n_dx, float(funnel["specialist_to_diagnosis_conversion"])),
    ]
    conv_map = {k: (start, end, conv) for k, start, end, conv in conversions}

    dropoff_raw = read_dropoff_map()
    delay_avg = read_delay_avg_row()

    rows_out: list[dict[str, object]] = []
    for i, st in enumerate(STAGES, start=1):
        key = st["stage_key"]
        start_n, end_n, conv = conv_map[key]
        med, n_med = median_interval(MART, st["mart_col"])
        avg = delay_avg.get(key)

        drop = dropoff_raw.get(st["label"])
        if drop is None:
            for dk, dv in dropoff_raw.items():
                if dk.replace(" ", "") == st["label"].replace(" ", ""):
                    drop = dv
                    break

        rows_out.append(
            {
                "stage_order": i,
                "stage_transition": st["label"],
                "patients_at_stage_entry": start_n,
                "patients_converting_to_next": end_n,
                "conversion_rate": round(conv, 4),
                "drop_off_rate": round(drop, 4) if drop is not None else None,
                "avg_days_among_converters": round(avg, 2) if avg is not None else None,
                "median_days_among_converters": round(med, 2) if med is not None else None,
                "n_patients_used_for_median": n_med,
            }
        )

    # Rank stages by drop-off (highest leakage first)
    ranked = sorted(
        [r for r in rows_out if r["drop_off_rate"] is not None],
        key=lambda x: float(x["drop_off_rate"]),
        reverse=True,
    )
    top_labels = [str(r["stage_transition"]) for r in ranked[:2]]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows_out[0].keys()) if rows_out else []
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows_out:
            w.writerow(r)
        blank = {k: "" for k in fieldnames}
        w.writerow(blank)
        w.writerow(
            {
                "stage_order": "",
                "stage_transition": "SUMMARY — top_2_highest_drop_off_stages",
                "patients_at_stage_entry": "; ".join(top_labels),
                "patients_converting_to_next": "",
                "conversion_rate": "",
                "drop_off_rate": "",
                "avg_days_among_converters": "",
                "median_days_among_converters": "",
                "n_patients_used_for_median": "",
            }
        )

    print(f"Wrote {OUT}")
    safe = [s.replace("\u2192", "->") for s in top_labels]
    print("Top 2 coordination-failure (leakage) stages:", ", ".join(safe))

    with MART.open(encoding="utf-8") as mf:
        mart_rows = sum(1 for _ in mf) - 1
    print(f"Median denominators now come from full cleaned mart rows: {mart_rows}")


if __name__ == "__main__":
    main()
