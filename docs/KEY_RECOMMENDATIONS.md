# Key Recommendations: Operating Rules

These recommendations convert the analysis into concrete workflow rules that an operations team could implement.

## Baseline Metrics

| Metric | Current value |
|---|---:|
| Diagnosis completion rate | 21.0% |
| PCP -> Referral drop-off | 43.8% |
| Specialist -> Diagnosis drop-off | 44.8% |
| Referral -> Specialist median wait | 36 days |
| Combined +5pp referral and diagnosis closure scenario | +195.5 diagnoses |

## Rule 1: Referral must have a documented outcome within 7 days

**Trigger:** Patient has a primary care visit with suspected CHD.

**Required outcome within 7 days:**
- referral sent
- referral not needed, reason documented
- family declined, reason documented
- unable to contact, outreach attempt documented

**Owner:** Primary care operations / referral coordinator.

**Escalation:** If no referral outcome after 7 days, case appears on the referral exception list.

**KPI:** PCP -> Referral conversion rate.

**Target:** Reduce PCP -> Referral drop-off from **43.8%** to below **35%**.

**Why this matters:** This is one of the two largest loss points in the pathway.

## Rule 2: Critical referrals must be scheduled within 7 days

**Trigger:** `referral_priority = critical`.

**Required action:** Specialist appointment scheduled within 7 days of referral.

**Owner:** Specialty scheduling team.

**Escalation:** If no appointment is scheduled by day 7, route to care navigation lead.

**KPI:** Percent of critical referrals scheduled within 7 days.

**Target:** Greater than **90%** of critical referrals scheduled within 7 days.

**Why this matters:** Critical cases should not sit in the same queue as routine referrals.

## Rule 3: Urgent referrals must be scheduled within 14 days

**Trigger:** `referral_priority = urgent`.

**Required action:** Specialist appointment scheduled within 14 days of referral.

**Owner:** Specialty scheduling team.

**Escalation:** If no appointment is scheduled by day 14, review capacity and contact family.

**KPI:** Percent of urgent referrals scheduled within 14 days.

**Target:** Greater than **85%** of urgent referrals scheduled within 14 days.

**Why this matters:** Urgent referrals are a manageable subset where access delays should be actively monitored.

## Rule 4: Routine referrals waiting more than 45 days require review

**Trigger:** Routine referral has no completed specialist visit after 45 days.

**Required action:** Review appointment status and document one of:
- scheduled pending
- cancelled and rescheduled
- no-show outreach started
- unable to contact
- capacity delay
- family cost/travel barrier

**Owner:** Referral coordination / care navigation.

**Escalation:** If still unresolved after 60 days, route to operations manager.

**KPI:** Median Referral -> Specialist wait time.

**Target:** Keep median Referral -> Specialist wait at or below **36 days**, then reduce toward **30 days**.

**Why this matters:** Referral -> Specialist is the longest wait-time step.

## Rule 5: No-shows must receive outreach within 48 hours

**Trigger:** `specialist_appointment_status = no_show`.

**Required action within 48 hours:**
- call/text caregiver
- document barrier
- reschedule or close with reason

**Owner:** Care navigation team.

**Escalation:** If no contact after two attempts, flag as unable to contact and route to community outreach workflow.

**KPI:** Percent of no-shows contacted within 48 hours.

**Target:** Greater than **90%** outreach completion.

**Why this matters:** No-shows are not just lost patients; they are a recoverable follow-up queue.

## Rule 6: Cancelled visits must be rescheduled within 7 days

**Trigger:** `specialist_appointment_status = cancelled`.

**Required action:** New appointment date scheduled within 7 days.

**Owner:** Specialty scheduling team.

**Escalation:** If not rescheduled within 7 days, route to scheduling supervisor.

**KPI:** Percent of cancelled appointments rescheduled within 7 days.

**Target:** Greater than **85%** rescheduled within 7 days.

**Why this matters:** Cancelled visits can look like drop-off unless the reschedule loop is closed.

## Rule 7: Specialist visits without diagnosis must be closed within 14 days

**Trigger:** Specialist visit completed and no diagnosis recorded.

**Required outcome within 14 days:**
- diagnosis confirmed
- CHD ruled out
- follow-up scheduled
- diagnostic test ordered
- documentation incomplete
- patient did not return

**Owner:** Cardiology clinic operations / documentation quality team.

**Escalation:** If no documented outcome after 14 days, case appears on diagnostic closure work queue.

**KPI:** Specialist -> Diagnosis conversion rate.

**Target:** More than **85%** of specialist visits have a documented outcome within 14 days.

**Modeled impact:** Specialist -> Diagnosis +10pp adds about **189 diagnoses**.

**Why this matters:** This is the largest drop-off point in the pathway.

## Rule 8: High-friction access cases get navigator review at 30 days

**Trigger:** Referral is open for more than 30 days and any of the following are true:
- Medicaid or uninsured
- high SVI
- distance to specialist greater than 40 miles
- low-capacity clinic region
- authorization pending or denied

**Required action:** Care navigator reviews barrier and documents next action.

**Owner:** Care navigation team.

**Escalation:** If unresolved by 45 days, route to access manager.

**KPI:** Median Referral -> Specialist wait by payer, SVI, distance, and capacity tier.

**Target:** Reduce access gaps between high-friction and lower-friction groups.

**Why this matters:** It turns equity/access analysis into a specific follow-up process.

## Rule 9: Clinics below referral benchmark get workflow review

**Trigger:** Clinic or provider group has at least 20 suspected CHD primary care cases and PCP -> Referral conversion below 50%.

**Required action:** Review workflow for missed referral documentation, referral criteria, staffing, or follow-up process.

**Owner:** Operations manager / primary care leadership.

**Escalation:** Repeat low performance for two months triggers training or process redesign.

**KPI:** PCP -> Referral conversion by clinic/provider group.

**Target:** Bring low-performing groups above **50%** first, then toward pathway benchmark.

**Why this matters:** It creates a practical way to use provider/clinic variation without blaming individual clinicians.

## Rule 10: Review the five-metric pathway scorecard monthly

**Trigger:** Monthly operations review.

**Scorecard metrics:**
1. Diagnosis completion rate
2. PCP -> Referral drop-off
3. Specialist -> Diagnosis drop-off
4. Referral -> Specialist median wait
5. Modeled additional diagnoses from scenario improvements

**Owner:** Analytics + operations leadership.

**Required action:** Assign an owner for any metric that worsens month over month.

**KPI:** Month-over-month improvement in bottleneck metrics.

**Target:** Improve pathway completion from **21.0%** toward **25.0%** using referral and diagnostic closure improvements.

## Highest-Impact Package

| Improvement package | Modeled result |
|---|---:|
| PCP -> Referral +5pp and Specialist -> Diagnosis +5pp | +195.5 diagnoses |
| New modeled completion rate | 24.9% |

## Plain-English Recommendation

Do not start with a complex model. Start with workflow closure:

1. Every suspected case needs a referral decision.
2. Every referral needs a scheduled or documented outcome.
3. Every missed/cancelled appointment needs follow-up.
4. Every specialist visit needs a diagnosis, rule-out, or follow-up plan.
5. Every month, leadership reviews whether those handoffs are improving.

## Caveat

These operating rules are based on synthetic data and are intended to demonstrate how analytics can become an operational playbook. They should be validated and adjusted before use in a real clinical setting.
