# Root cause exploratory summary
_Associational patterns only. No payer auth/denial fields in this synthetic schema._

## Referral documentation
- Patients with **≥1 referral row**: 49.0% of mart cohort.
- Diagnosis rate **with** referral record: 0.222; **without**: 0.198.

## Diagnostic closure proxy (echocardiogram timing)
- Among **patients with a recorded diagnosis** (n=1042):
  - **Any** echocardiogram record: 7.3%
  - Echo **on or before** diagnosis date: 0.1%
- Among **specialist seen but no diagnosis** (stalled cohort, n=847):
  - **Any** echo record: 5.9%

## Referring provider activity (min referrals)
- Providers with **≥15** outbound referrals in extract: **200** (see `provider_performance.csv`).
- Use these metrics for **operational triage** (volume, completion), not individual clinician quality verdicts.
