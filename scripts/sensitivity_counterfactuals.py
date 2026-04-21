"""
One-at-a-time sensitivity: vary each stage conversion by ±5 percentage points.
Assumptions: same sequential model as compute_counterfactuals; other stages fixed.
Output: outputs/analytics/counterfactual_sensitivity.csv
"""

from __future__ import annotations

import _bootstrap_path  # noqa: F401
import pandas as pd

from chd_analytics.funnel_math import load_funnel_metrics, modeled_diagnoses
from chd_analytics.paths import ANALYTICS, ROOT

OUT = ANALYTICS / "counterfactual_sensitivity.csv"
DELTA = 0.05


def main() -> None:
    f = load_funnel_metrics(ROOT)
    n_pcp = f["pcp"]
    c_pr = f["pcp_to_referral_conversion"]
    c_rs = f["referral_to_specialist_conversion"]
    c_sd = f["specialist_to_diagnosis_conversion"]
    base = modeled_diagnoses(n_pcp, c_pr, c_rs, c_sd)

    rows: list[dict[str, object]] = []
    for label, pr, rs, sd in [
        ("baseline", c_pr, c_rs, c_sd),
        ("pcp_to_referral_minus_5pp", max(0, c_pr - DELTA), c_rs, c_sd),
        ("pcp_to_referral_plus_5pp", min(1, c_pr + DELTA), c_rs, c_sd),
        ("referral_to_specialist_minus_5pp", c_pr, max(0, c_rs - DELTA), c_sd),
        ("referral_to_specialist_plus_5pp", c_pr, min(1, c_rs + DELTA), c_sd),
        ("specialist_to_diagnosis_minus_5pp", c_pr, c_rs, max(0, c_sd - DELTA)),
        ("specialist_to_diagnosis_plus_5pp", c_pr, c_rs, min(1, c_sd + DELTA)),
    ]:
        dx = modeled_diagnoses(n_pcp, pr, rs, sd)
        rows.append(
            {
                "scenario": label,
                "modeled_diagnoses": round(dx, 2),
                "delta_vs_baseline": round(dx - base, 2),
            }
        )

    df = pd.DataFrame(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
