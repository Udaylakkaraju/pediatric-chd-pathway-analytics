"""
Counterfactual scenarios: if stage conversion rates improve, how many more
diagnoses (approx.) for the same symptom cohort? Uses sequential funnel math
matching analytics/funnel_metrics.csv.
"""

from __future__ import annotations

import _bootstrap_path  # noqa: F401
import csv

from chd_analytics.funnel_math import load_funnel_metrics, modeled_diagnoses
from chd_analytics.paths import ANALYTICS, ROOT

OUT = ANALYTICS / "recommendations_counterfactuals.csv"


def main() -> None:
    f = load_funnel_metrics(ROOT)
    n_sym = f["symptom"]
    n_pcp = f["pcp"]
    c_pr = f["pcp_to_referral_conversion"]
    c_rs = f["referral_to_specialist_conversion"]
    c_sd = f["specialist_to_diagnosis_conversion"]
    base_dx = modeled_diagnoses(n_pcp, c_pr, c_rs, c_sd)

    scenarios: list[tuple[str, float, float, float, float]] = [
        ("baseline (current funnel)", c_pr, c_rs, c_sd, 0.0),
        ("PCP→Referral +5 percentage points", c_pr + 0.05, c_rs, c_sd, 0.05),
        ("PCP→Referral +10 percentage points", c_pr + 0.10, c_rs, c_sd, 0.10),
        ("Referral→Specialist +10 percentage points", c_pr, c_rs + 0.10, c_sd, 0.10),
        ("Specialist→Diagnosis +10 percentage points", c_pr, c_rs, c_sd + 0.10, 0.10),
        ("PCP→Referral +5 and Specialist→Diagnosis +5 pp", c_pr + 0.05, c_rs, c_sd + 0.05, 0.05),
    ]

    rows: list[dict[str, object]] = []
    for name, pr, rs, sd, _ in scenarios:
        pr = min(pr, 1.0)
        rs = min(rs, 1.0)
        sd = min(sd, 1.0)
        dx = modeled_diagnoses(n_pcp, pr, rs, sd)
        extra = dx - base_dx
        pct_sym = 100.0 * dx / n_sym
        pct_extra_vs_base = 100.0 * extra / base_dx if base_dx else 0.0
        rows.append(
            {
                "scenario": name,
                "modeled_diagnoses": round(dx, 1),
                "extra_diagnoses_vs_baseline": round(extra, 1),
                "pct_symptom_cohort_reaching_diagnosis": round(pct_sym, 2),
                "pct_increase_in_diagnoses_vs_baseline": round(pct_extra_vs_base, 2),
            }
        )

    with OUT.open("w", newline="", encoding="utf-8") as file:
        w = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print(f"Wrote {OUT}")
    print(f"Baseline modeled diagnoses: {base_dx:.1f} (reported diagnosis count ~ {int(round(base_dx))})")


if __name__ == "__main__":
    main()
