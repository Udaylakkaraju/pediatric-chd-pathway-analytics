# Root cause exploratory summary
_Associational patterns only. No payer auth/denial fields in this synthetic schema._

## Referral documentation
- Patients with **≥1 referral row**: 71.6% of mart cohort.
- Diagnosis rate **with** referral record: 0.367; **without**: 0.000.

## Diagnostic closure proxy (echocardiogram timing)
- Among **patients with a recorded diagnosis** (n=3948):
  - **Any** echocardiogram record: 0.0%
  - Echo **on or before** diagnosis date: 0.0%
- Among **specialist seen but no diagnosis** (stalled cohort, n=1709):
  - **Any** echo record: 0.0%

## Referring provider activity (min referrals)
- Providers with **≥15** outbound referrals in extract: **320** (see `provider_performance.csv`).
- Use these metrics for **operational triage** (volume, completion), not individual clinician quality verdicts.
