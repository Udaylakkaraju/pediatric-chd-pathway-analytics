# Root cause exploratory summary
_Associational patterns only. No payer auth/denial fields in this synthetic schema._

## Referral documentation
- Patients with **≥1 referral row**: 49.0% of mart cohort.
- Diagnosis rate **with** referral record: 0.238; **without**: 0.182.

## Diagnostic closure proxy (echocardiogram timing)
- Among **patients with a recorded diagnosis** (n=1042):
  - **Any** echocardiogram record: 8.8%
  - Echo **on or before** diagnosis date: 0.0%
- Among **specialist seen but no diagnosis** (stalled cohort, n=1471):
  - **Any** echo record: 7.8%

## Referring provider activity (min referrals)
- Providers with **≥15** outbound referrals in extract: **200** (see `provider_performance.csv`).
- Use these metrics for **operational triage** (volume, completion), not individual clinician quality verdicts.
