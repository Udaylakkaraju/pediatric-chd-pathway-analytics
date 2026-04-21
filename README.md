# Pediatric CHD Pathway Analytics

**Congenital heart diagnosis delay and care coordination analysis**

This project asks a simple question:  
**Why are pediatric patients getting delayed or lost before diagnosis, and what should operations teams fix first?**

---

## What This Project Shows

- **4,969 patients** across a synthetic EHR-style cohort
- **~21%** reached diagnosis in the documented pathway
- Largest losses happen at:
  - **Primary Care -> Referral (~44% drop-off)**
  - **Specialist -> Diagnosis (~45% drop-off)**
- Scenario modeling suggests targeted workflow improvements could recover **~196 additional diagnoses** in this cohort view

---

## Care Pathway

Symptom -> Primary Care -> Referral -> Specialist -> Diagnosis

The work combines:
- pathway funnel metrics
- delay/wait analysis
- segmentation
- root-cause probes
- intervention scenario modeling

---

## Visual Snapshot

![Pathway Funnel](python%20visuals/Pathway%20Funnel.png)
*Patient volume by stage: where the pathway narrows most.*

![Delay Severity Score Distribution](python%20visuals/Delay%20Severity%20Score%20Distribution.png)
*Most patients cluster in low-to-moderate delay, with a meaningful long tail.*

![Delay Severity Score Insurance Type](python%20visuals/Delay%20Severity%20Score%20Insurance%20Type.png)
*Insurance differences exist, but are smaller than stage-level pathway leakage.*

![Interval Distributions](python%20visuals/Interval%20Distributions.png)
*Wait-time distributions by stage highlight where delays are concentrated.*

---

## Dashboard

Run the interactive dashboard:

```bash
python -m streamlit run app/streamlit_app.py
```

It includes:
- **Overview** (funnel, drop-off, delay severity, scenario impact)
- **Quality & trends**
- **Segments**
- **Root-cause probes**

---

## SQL Work (Beginner -> Intermediate)

This repo includes a short SQL query pack in `sql/` to mirror core analytics logic in plain, interview-friendly steps:

- `01_basic_profile.sql` -> table size + data coverage
- `02_pathway_funnel.sql` -> stage counts + conversion rates
- `03_stage_dropoff.sql` -> drop-off by transition
- `04_stage_delay_contribution.sql` -> average waits by stage
- `05_insurance_segmentation.sql` -> payer comparison
- `06_provider_root_cause.sql` -> provider referral completion
- `07_trend_by_month.sql` -> monthly trend
- `08_cohort_scorecard.sql` -> one-row executive scorecard

See `sql/README.md` for run order and usage notes.

---

## Business-Friendly Outputs

For non-technical stakeholders, plain-language files are available in:

- `outputs/business_ready/`

Examples:
- `patient_pathway_summary.csv`
- `stage_loss_rates.csv`
- `average_wait_by_stage.csv`
- `scenario_impact_estimates.csv`

Regenerate them with:

```bash
python scripts/create_business_friendly_exports.py
```

---

## Quick Run (Full Pipeline)

```bash
pip install -r requirements.txt
python scripts/data_quality_checks.py
python scripts/trend_analysis.py
python scripts/advanced_segmentation.py
python scripts/root_cause_analysis.py
python scripts/sensitivity_counterfactuals.py
python scripts/build_coordination_scorecard.py
python scripts/compute_counterfactuals.py
python scripts/create_business_friendly_exports.py
python -m pytest
```

---

## Repository Layout

```text
app/                    Streamlit app
scripts/                Analysis scripts
chd_analytics/          Shared logic (paths, funnel math, severity mapping)
data/raw/               Source tables
data/staging/           Cleaned staging tables (stg_*.csv)
data/marts/cleaned/     Analysis-ready patient mart
sql/                    Beginner -> intermediate SQL query pack
outputs/analytics/      Technical outputs
outputs/business_ready/ Plain-language outputs
tests/                  Validation tests
```

---

## Key Recommendations

1. **Strengthen referral completion after primary care**  
   (largest early-stage loss)
2. **Improve diagnostic closure after specialist visits**  
   (largest late-stage loss + long waits)
3. **Track leakage + wait time together**  
   (not delay-only or conversion-only)

---

## Important Notes

- Data is **synthetic** (portfolio/demo use).
- Scenario impacts are **planning estimates**, not causal guarantees.
- Provider-level metrics are for **operational triage**, not performance judgment.

---

For detailed technical context: see `PROJECT_CONTEXT.md` and `PROJECT_BULLETS.md`.
