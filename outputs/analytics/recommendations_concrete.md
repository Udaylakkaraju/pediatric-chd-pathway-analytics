# Operating Recommendations

Scope: synthetic pediatric CHD diagnostic pathway.

Current baseline:

| Metric | Value |
|---|---:|
| Patients in pathway | 4,969 |
| Patients reaching diagnosis | 1,042 |
| Diagnosis completion rate | 21.0% |
| PCP -> Referral drop-off | 43.8% |
| Specialist -> Diagnosis drop-off | 44.8% |
| Referral -> Specialist median wait | 36 days |

## What The Analysis Says

The pathway problem is not one vague delay. It is a handoff problem:

1. Too many patients reach primary care but do not receive a documented referral.
2. Too many patients complete a specialist visit but do not receive a documented diagnosis, rule-out, or follow-up plan.
3. Referral-to-specialist access is the longest wait-time step.

## Operating Rules

| Rule | Trigger | Required action | KPI | Target |
|---|---|---|---|---|
| Referral outcome within 7 days | Suspected CHD at PCP visit | Referral sent or reason documented | PCP -> Referral conversion | Drop-off below 35% |
| Critical referral scheduled within 7 days | `referral_priority = critical` | First available specialist slot | Critical referral scheduling rate | >90% within 7 days |
| Urgent referral scheduled within 14 days | `referral_priority = urgent` | Appointment scheduled | Urgent referral scheduling rate | >85% within 14 days |
| Routine referral reviewed at 45 days | No specialist visit after 45 days | Document status/barrier | Referral -> Specialist median wait | <=36 days, then toward 30 |
| No-show outreach within 48 hours | Appointment no-show | Contact caregiver and reschedule/close | No-show outreach rate | >90% within 48 hours |
| Cancelled visit rescheduled within 7 days | Appointment cancelled | New date scheduled | Reschedule rate | >85% within 7 days |
| Specialist visit closed within 14 days | Specialist visit with no diagnosis | Diagnosis, rule-out, test, or follow-up documented | Specialist -> Diagnosis conversion | >85% documented outcome |
| High-friction case reviewed at 30 days | Open referral + payer/SVI/distance/capacity risk | Navigator review | Wait gap by access segment | Reduce segment gaps |
| Low referral benchmark review | Clinic with 20+ cases and <50% PCP -> Referral conversion | Workflow audit | Clinic conversion rate | >50%, then improve |
| Monthly pathway scorecard | Monthly ops review | Assign owner for worsening metric | Five scorecard KPIs | Move completion toward 25% |

## Highest-Impact Package

| Improvement package | Modeled result |
|---|---:|
| PCP -> Referral +5pp and Specialist -> Diagnosis +5pp | +195.5 diagnoses |
| New modeled completion rate | 24.9% |

## Recommended First 30 Days

1. Build the referral exception list: PCP visits with no referral outcome after 7 days.
2. Build the diagnostic closure list: specialist visits with no diagnosis/rule-out/follow-up after 14 days.
3. Add appointment status queues for no-show, cancelled, scheduled pending, unable to contact, and not referred.
4. Slice referral-to-specialist wait time by payer, SVI, distance, capacity tier, and priority.
5. Publish the first monthly pathway scorecard.

## Plain-English Summary

The best first move is not a more complex model. It is a better handoff system.

Every suspected case should have a referral decision. Every referral should have a scheduled or documented outcome. Every missed appointment should trigger follow-up. Every specialist visit should end with a diagnosis, rule-out, or follow-up plan.

## Caveat

These recommendations are based on synthetic EHR-style data. They demonstrate how analytics can become an operational playbook, but they are not clinical evidence or causal forecasts.
