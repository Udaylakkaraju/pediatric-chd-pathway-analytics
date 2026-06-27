# Project Context

## Clean Story

This is a healthcare operations analytics project. It tracks synthetic pediatric CHD patients through a multi-step diagnostic pathway and measures where patients are delayed, lost, or completed.

The value is not that the data is real. The value is the repeatable analytics workflow:

```text
synthetic EHR-style data -> patient mart -> SQL/Python analysis -> QA checks -> BI-ready outputs -> recommendations
```

## Business Question

Where are patients falling out of the pathway, how long do completed steps take, and which operational improvements could produce the biggest gain?

## Modeled Pathway

```text
Symptom documented -> Primary care -> Referral -> Specialist visit -> Diagnosis
```

## Current Numbers

| Metric | Value |
|---|---:|
| Symptom cohort | 4,969 |
| Reached primary care | 4,333 |
| Received referral | 2,436 |
| Completed specialist visit | 1,889 |
| Reached diagnosis | 1,042 |
| Diagnosis completion rate | 21.0% |

## Stage Scorecard

| Stage | Conversion | Drop-off | Average wait | Median wait |
|---|---:|---:|---:|---:|
| Symptom -> PCP | 87.2% | 12.8% | 30.3 days | 19 days |
| PCP -> Referral | 56.2% | 43.8% | 14.8 days | 10 days |
| Referral -> Specialist | 77.6% | 22.5% | 50.0 days | 36 days |
| Specialist -> Diagnosis | 55.2% | 44.8% | 10.0 days | 6 days |

## Main Findings

- Only 21.0% of patients reach diagnosis in the synthetic pathway.
- The largest loss is Specialist -> Diagnosis, with 44.8% drop-off.
- The second-largest loss is PCP -> Referral, with 43.8% drop-off.
- Referral -> Specialist is the longest wait-time bottleneck, with a 36-day median wait.
- Scenario modeling suggests that improving PCP -> Referral and Specialist -> Diagnosis by 5 percentage points each could add about 196 diagnoses.

## Realism Choices

The synthetic data is designed to mimic operational patterns:

- pathway stages are sequential
- wait times are right-skewed
- complex CHD tends to reach care faster
- payer and SVI can affect specialist access waits
- appointment status and authorization status create realistic workflow friction
- capacity tier, region, and distance help create BI-relevant slices

## Important Fields

Patient and clinical fields:
- `patient_id`
- `insurance_type`
- `svi_index`
- `chd_type`
- `chd_severity`

Pathway fields:
- `symptom_onset_date`
- `first_pcp_date`
- `referral_date`
- `specialist_date`
- `diagnosis_date`
- `intervention_date`

Operational fields:
- `referral_priority`
- `authorization_status`
- `specialist_appointment_status`
- `clinic_region`
- `provider_capacity_tier`
- `distance_to_specialist_miles`

## Key Outputs

Technical outputs:
- `outputs/analytics/funnel metrics.csv`
- `outputs/analytics/coordination_failure_scorecard.csv`
- `outputs/analytics/recommendations_counterfactuals.csv`
- `outputs/analytics/segment_comparison.csv`
- `outputs/analytics/QC_Report.csv`

Business outputs:
- `outputs/business_ready/patient_pathway_summary.csv`
- `outputs/business_ready/stage_leakage_and_waits.csv`
- `outputs/business_ready/scenario_impact_estimates.csv`
- `outputs/business_ready/payer_comparison.csv`

Power BI outputs:
- `outputs/bi_ready/patient_pathway_detail.csv`
- `outputs/bi_ready/pathway_funnel_summary.csv`
- `outputs/bi_ready/stage_dropoff_rates.csv`
- `outputs/bi_ready/stage_wait_time_summary.csv`
- `outputs/bi_ready/payer_summary.csv`

## Validation

The project includes pytest checks for:

- funnel count consistency
- conversion-rate math
- counterfactual baseline consistency
- coordination scorecard alignment
- output tables matching the mart
- valid conversion rates in SQL outputs
- BI-ready table field availability

Current test result: 11 passing tests.

## Guardrails

- Synthetic data only.
- Demonstrates analytics workflow, not clinical truth.
- Scenario outputs are estimates, not causal forecasts.
- Provider/segment cuts are for operations triage, not quality judgment.
- Median waits should be used for communication because wait times are skewed.
