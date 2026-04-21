# Pediatric CHD Pathway Analytics

*Congenital Heart Diagnosis Delay and Care Coordination Analysis*

## Project purpose

This project analyzes delay and patient drop-off in a pediatric Congenital Heart Disease (CHD) diagnostic pathway to identify where care coordination fails and what operational improvements may increase diagnosis completion.

Core business questions:

- Where are patients delayed or lost in the care pathway?
- Which stages contribute most to diagnostic delay?
- Are patterns driven mainly by system flow or by patient segments (e.g., insurance)?

## Care pathway modeled

Symptom -> PCP -> Referral -> Specialist -> Diagnosis -> Intervention

## Repository layout

- `data/raw/` — eight source EHR-style CSVs  
- `data/marts/cleaned/` — patient-level analytical mart (`mart_delay_scored_cleaned.csv`, full cohort)  
- `outputs/analytics/` — BI-style metrics, QC, trends, segments, scenarios  
- `outputs/business_ready/` — plain-language copies of key outputs for non-technical users  
- `chd_analytics/` — Python package: `paths`, `funnel_math`, `chd_severity_map`  
- `scripts/` — runnable analysis and validation scripts  
- `app/streamlit_app.py` — dashboard  
- `tests/` — pytest  

## Data used

Synthetic EHR-style relational data across 8 source tables in **`data/raw/`**:

- `patients(Main Table).csv`
- `encounters.csv`
- `observations.csv`
- `conditions.csv`
- `procedures.csv`
- `referrals.csv`
- `providers.csv`
- `organizations.csv`

## Analytics layers

Patient-level mart:

- `data/marts/cleaned/mart_delay_scored_cleaned.csv`

BI-ready exports under **`outputs/analytics/`**:

- `funnel metrics.csv`
- `stage dropoff.csv`
- `delay buckets.csv`
- `stage delay contribution.csv`
- `insurance analysis.csv`
- `coordination_failure_scorecard.csv`
- `recommendations_counterfactuals.csv`
- `counterfactual_sensitivity.csv` (±5 pp one-at-a-time sensitivity)
- `recommendations_concrete.md`
- `QC_Report.csv` (data quality checks)
- `trend_by_month.csv` (symptom-index trends, mature months)
- `segment_comparison.csv`, `segment_deep_dive.md` (multi-way segmentation)
- `provider_performance.csv`, `root_cause_summary.md` (exploratory root-cause probes)

Business-friendly exports under **`outputs/business_ready/`**:

- `patient_pathway_summary.csv`
- `stage_loss_rates.csv`
- `average_wait_by_stage.csv`
- `payer_comparison.csv`
- `stage_leakage_and_waits.csv`
- `monthly_pathway_trends.csv`
- `scenario_impact_estimates.csv`
- `data_health_report.csv`

## Primary mart for extended Python analysis

Scripts under **`scripts/`** (**`data_quality_checks.py`**, **`trend_analysis.py`**, **`advanced_segmentation.py`**, **`root_cause_analysis.py`**) use the full cohort file:

- `data/marts/cleaned/mart_delay_scored_cleaned.csv` (4,969 patients)

Column mapping lives in **`chd_analytics/paths.py`**.

**CHD severity buckets** (for segmentation) are defined in **`chd_analytics/chd_severity_map.py`** (project-owned mapping of `chd_type` → Simple / Moderate / Complex).

## Final analytical schema (`mart_delay_scored_cleaned`)

Identifiers and segmentation:

- `patient_id`, `zip_code`, `svi_index`, `insurance_type`, `chd_type`

Timeline fields:

- `symptom_onset_date`, `first_pcp_date`, `referral_date`, `specialist_date`, `diagnosis_date`, `intervention_date`

Interval features:

- `days_symptom_to_pcp_clean`
- `days_pcp_to_referral_clean`
- `days_referral_to_specialist_clean`
- `days_specialist_to_diagnosis_clean`
- `days_diagnosis_to_intervention_clean`

Target metric: `delay_severity_score_clean` (see below)

## `delay_score` / `delay_severity_score_clean` (what it means here)

In the **cleaned mart** (`data/marts/cleaned/mart_delay_scored_cleaned.csv`), the field **`delay_severity_score_clean`** is the engineered **pathway delay severity** used for ranking and bucketing. It is **not** a plain sum of the five interval columns in every row: the upstream mart build applies additional weighting / handling for **partial pathways** and edge cases. The exact SQL or notebook that defines the composite is **out of this repo**; this project **consumes** the published score and validates **intervals and dates** separately via **`scripts/data_quality_checks.py`**.

For presentation, treat **`delay_severity_score_clean`** as: *single scalar summarizing how long and/or incomplete the documented pathway is for that patient*, always alongside **stage intervals** and **funnel conversion** metrics.

## Counterfactual modeling assumptions

`scripts/compute_counterfactuals.py` and **`chd_analytics/funnel_math.py`** use a **sequential model**:

`modeled_diagnoses = n_pcp × c_pcp→referral × c_referral→specialist × c_specialist→diagnosis`

**Assumptions (document for stakeholders):**

- Stage conversion changes are **scenarios**, not measured causal impacts.
- Improvements to **one** stage are modeled **holding other conversion rates constant** (no automatic coupling).
- Scenarios do **not** account for capacity constraints, case mix shifts, or simultaneous operational changes unless you add them explicitly.

**Sensitivity:** run `python scripts/sensitivity_counterfactuals.py` to produce `outputs/analytics/counterfactual_sensitivity.csv` (±5 percentage points on **one** stage at a time vs baseline).

## Data engineering and cleaning approach

- Negative intervals handled with bounded logic (non-negative interval rule).
- Stage delay fields recomputed consistently.
- Full cohort preserved (no wholesale row drops).
- Standardized naming for analysis and visualization handoff.

## Key findings

From the current analytics exports:

- Funnel baseline: 4,969 symptom-stage patients; 1,042 with recorded diagnosis.
- Overall diagnosis reach is about 21% (about 79% do not reach diagnosis in this pathway view).
- Largest stage leakage:
  - PCP -> Referral drop-off: 43.78%
  - Specialist -> Diagnosis drop-off: 44.84%
- Stage mean delays among converters:
  - Symptom -> PCP: 700.63 days
  - PCP -> Referral: 272.62 days
  - Referral -> Specialist: 223.82 days
  - Specialist -> Diagnosis: 575.15 days
- Insurance segmentation differences exist but are smaller than pathway leakage effects.

## Coordination failure scorecard

The scorecard combines two operational dimensions by stage:

- Leakage (conversion and drop-off)
- Time (average/median days among converters)

Output:

- `outputs/analytics/coordination_failure_scorecard.csv`

This supports prioritization using both "how many patients are lost" and "how long those who progress are waiting."

Medians are now computed from the full cleaned mart (not a sample mart). Current median denominators by stage are:

- Symptom → PCP: 3,999 patients
- PCP → Referral: 2,027 patients
- Referral → Specialist: 737 patients
- Specialist → Diagnosis: 345 patients

## Recommendations (metrics-backed)

Primary levers:

1. Improve PCP -> Referral conversion (closed-loop referral operations).
2. Improve Specialist -> Diagnosis conversion (diagnostic closure workflows).
3. Improve Referral -> Specialist completion (specialty access/scheduling).

Scenario outputs (`recommendations_counterfactuals.csv`) model illustrative upside:

- PCP->Referral +5 pp: about +93 modeled diagnoses.
- PCP->Referral +10 pp: about +185 modeled diagnoses.
- Specialist->Diagnosis +10 pp: about +189 modeled diagnoses.
- Combined PCP->Referral +5 pp and Specialist->Diagnosis +5 pp: about +196 modeled diagnoses.

These are planning scenarios, not causal forecasts.

## Visualization layer

Interactive dashboard:

- `app/streamlit_app.py`

Design includes:

- Funnel, drop-off, conversion, delay severity, insurance segment, scenario impact, and coordination scorecard views.
- "Real-world tie-in" notes under visuals to connect metrics to hospital operations.

## Scripts and how to run

Install dependencies:

```bash
pip install -r requirements.txt
```

Build scorecard:

```bash
python scripts/build_coordination_scorecard.py
```

Build counterfactual scenarios:

```bash
python scripts/compute_counterfactuals.py
```

Run dashboard (from project root):

```bash
python -m streamlit run app/streamlit_app.py
```

Optional — regenerate extended analytics:

```bash
python scripts/data_quality_checks.py
python scripts/trend_analysis.py
python scripts/advanced_segmentation.py
python scripts/root_cause_analysis.py
python scripts/sensitivity_counterfactuals.py
python scripts/create_business_friendly_exports.py
```

## Testing and verification

Automated checks (**pytest**):

```bash
pip install -r requirements.txt
pytest
```

Tests assert:

- Funnel **counts** imply the same **conversion rates** as `funnel metrics.csv`.
- **Chain product** `n_pcp × c_pr × c_rs × c_sd` matches the **diagnosis** stage count (1042 for current extract).
- **Counterfactual baseline** row matches that chain.
- **Coordination scorecard** stage **conversion_rate** columns match funnel-implied rates.

Shared logic lives in **`chd_analytics/funnel_math.py`** (used by `scripts/compute_counterfactuals.py` and tests).

Optional **CI:** `.github/workflows/ci.yml` runs `pytest` on push/PR when hosted on GitHub.

## Data quality (systematic)

`scripts/data_quality_checks.py` writes **`outputs/analytics/QC_Report.csv`**: null rates, duplicate keys, **date order violations**, **future-dated** pathway fields (relative to run date), **implausibly early** dates (before 1995), negative intervals, long-interval flags, and mart vs funnel alignment.

## Limitations and interpretation guardrails

- Data is synthetic; insights are demonstration-grade for analytics and workflow reasoning.
- Counterfactual uplift values are arithmetic scenario models, not program impact guarantees.
- Date/timeline definition quality in real deployments depends on local EHR documentation practices.
- Ensure denominator alignment between funnel counts and stage-level medians when communicating results.

## Project positioning

This project demonstrates:

- SQL-style healthcare analytics and mart thinking
- Funnel and pathway operations analysis
- Stage-level root-cause diagnostics
- Segmentation analysis
- Recommendation design with measurable KPIs
- Lightweight Python automation and Streamlit storytelling
