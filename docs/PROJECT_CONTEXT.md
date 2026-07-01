# Project Context

## Positioning

This is a healthcare operations and care-pathway analytics project. It demonstrates a reproducible workflow:

```text
synthetic EHR source tables -> staging -> patient mart -> SQL + Excel -> QA -> operating recommendations
```

The CHD cohort is deliberately oversampled so operational patterns can be analyzed at useful scale. It is not a disease-prevalence estimate.

## Business Question

Where are patients falling out of the pathway, how long do completed steps take, which access factors overlap, and which workflow improvements offer the largest modeled gain?

## Current Funnel

| Stage | Patients | Conversion | Drop-off | Average wait | Median wait |
|---|---:|---:|---:|---:|---:|
| Symptom documented | 15,000 | - | - | - | - |
| Primary care | 13,276 | 88.5% | 11.5% | 24.7 days | 16 days |
| Referral | 8,581 | 64.6% | 35.4% | 10.3 days | 6 days |
| Specialist visit | 5,657 | 65.9% | 34.1% | 40.5 days | 28 days |
| Diagnosis | 3,948 | 69.8% | 30.2% | 9.1 days | 6 days |

## Main Findings

- Overall diagnosis completion is 26.3%.
- PCP -> Referral is the largest loss point at 35.4%.
- Referral -> Specialist is close behind at 34.1% and has the longest median wait at 28 days.
- High-capacity networks complete specialist visits for 42.0% of the cohort versus 29.9% in low-capacity networks.
- Diagnosis completion is 29.3% for privately insured patients versus 17.8% for uninsured patients.
- Two targeted +5 percentage-point conversion improvements model about 610 additional diagnoses.

## Data Scale

| Table | Rows |
|---|---:|
| Patients | 100,000 |
| CHD patient mart | 15,000 |
| Encounters | 240,000 |
| Observations | 720,000 |
| Referrals | 50,000 |
| Conditions | 20,000 |
| Procedures | 7,500 |

## Validation

Automated checks cover duplicate keys, foreign keys, DOB/event chronology, strict stage nesting, source-to-mart payer and CHD-type consistency, interval validity, funnel math, authorization semantics, conditional intervention, and visible capacity/SVI/payer effects.

## Guardrails

- Synthetic data only.
- Findings are descriptive, not causal.
- Wait metrics are labeled as applying to completed stages.
- Scenario outputs are planning math, not forecasts.
- Segment cuts support workflow triage, not clinical or individual-provider judgment.
