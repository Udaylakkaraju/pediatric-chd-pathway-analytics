# Data Dictionary

Schema reference for the synthetic pediatric CHD pathway analytics project.

## Primary Patient Mart

File: `data/marts/cleaned/mart_delay_scored_cleaned.csv`

Each row represents one synthetic pediatric patient.

## Patient And Segment Fields

| Column | Meaning | Business Use |
|---|---|---|
| `patient_id` | Unique synthetic patient ID | Cohort unit |
| `zip_code` | Synthetic residence ZIP | Geographic grouping |
| `svi_index` | Social vulnerability score from 0 to 1 | Access/equity segmentation |
| `insurance_type` | `private`, `medicaid`, `uninsured`, or `other` | Payer analysis |
| `chd_type` | CHD diagnosis category | Clinical grouping |
| `chd_severity` | `Simple`, `Moderate`, or `Complex` | Severity segmentation |

## Business Context Fields

These fields were added to make the dataset easier to use in Power BI and easier to explain to non-technical stakeholders.

| Column | Meaning | Example Use |
|---|---|---|
| `referral_priority` | Operational urgency: `routine`, `urgent`, `critical` | Filter wait times by urgency |
| `authorization_status` | Payer authorization state | Analyze access friction |
| `specialist_appointment_status` | Specialist appointment outcome | Separate completed visits from no-shows/cancellations |
| `clinic_region` | Synthetic clinic region | Regional dashboard slicer |
| `provider_capacity_tier` | Synthetic capacity grouping | Compare low/standard/high capacity |
| `distance_to_specialist_miles` | Estimated distance to specialist | Access burden measure |

## Pathway Date Fields

Dates are sequential. A patient cannot have a diagnosis date without a specialist date, or a specialist date without a referral date.

| Column | Meaning |
|---|---|
| `symptom_onset_date` | First symptom date in the synthetic record |
| `first_pcp_date` | First primary care visit |
| `referral_date` | Referral generated |
| `specialist_date` | Specialist visit completed |
| `diagnosis_date` | Diagnosis recorded |
| `intervention_date` | Treatment/intervention date |

Null dates mean the patient did not reach that stage in the documented pathway.

## Wait-Time Fields

| Column | Meaning |
|---|---|
| `days_symptom_to_pcp_clean` | Days from symptom to primary care |
| `days_pcp_to_referral_clean` | Days from primary care to referral |
| `days_referral_to_specialist_clean` | Days from referral to specialist visit |
| `days_specialist_to_diagnosis_clean` | Days from specialist visit to diagnosis |
| `days_diagnosis_to_intervention_clean` | Days from diagnosis to intervention |
| `delay_severity_score_clean` | Weighted operational delay score |

Use medians for most stakeholder communication because wait times are right-skewed.

## Core Output Tables

| File | Purpose |
|---|---|
| `outputs/analytics/funnel metrics.csv` | Stage counts and conversion rates |
| `outputs/analytics/stage dropoff.csv` | Drop-off rate by pathway step |
| `outputs/analytics/stage delay contribution.csv` | Average wait by stage |
| `outputs/analytics/coordination_failure_scorecard.csv` | Conversion, drop-off, mean wait, median wait |
| `outputs/analytics/segment_comparison.csv` | Segment-level diagnosis and delay comparison |
| `outputs/analytics/recommendations_counterfactuals.csv` | Scenario estimates for operational improvements |
| `outputs/analytics/QC_Report.csv` | Data quality checks |

## Power BI-Ready Tables

| File | Purpose |
|---|---|
| `outputs/bi_ready/patient_pathway_detail.csv` | Main patient-level fact table |
| `outputs/bi_ready/pathway_funnel_summary.csv` | Funnel KPI summary |
| `outputs/bi_ready/stage_dropoff_rates.csv` | Drop-off chart input |
| `outputs/bi_ready/stage_wait_time_summary.csv` | Wait-time chart input |
| `outputs/bi_ready/payer_summary.csv` | Payer comparison |

## KPI Definitions

| KPI | Definition |
|---|---|
| Diagnosis completion rate | Diagnosed patients / symptom cohort |
| Stage conversion rate | Patients reaching next stage / patients entering current stage |
| Stage drop-off rate | 1 - stage conversion rate |
| Median wait days | 50th percentile wait among patients who completed a stage |
| Scenario impact | Modeled additional diagnoses if a stage conversion improves |

## Interpretation Guardrails

- Data is synthetic and demonstration-grade.
- Findings are descriptive, not causal.
- Scenario estimates are planning math, not program forecasts.
- Provider and segment outputs should be used for operational triage, not individual performance judgment.
- Nulls in later pathway stages are expected because not every patient reaches every step.
