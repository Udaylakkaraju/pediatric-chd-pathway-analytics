# Quantified Business Recommendations

These recommendations convert the synthetic pathway findings into measurable operating rules. Counts and baseline rates are observed in the project data. Modeled outcomes assume later-stage conversion remains constant. Labor figures are illustrative workload estimates using an editable **$32 loaded hourly cost**, not claimed savings or clinical ROI.

## Executive Decision Table

| Priority | Eligible queue | Current problem | Target | Standalone modeled outcome | Time implication | Illustrative implementation effort |
|---|---:|---|---|---:|---|---:|
| Close referral decisions | 4,695 (31.3% of cohort) | 35.4% PCP-to-referral drop-off | 30.0% | +712 referrals; **+328 diagnoses** | Decision recorded within 7 days | 626 hours / **$20,032** |
| Capacity-aware scheduling | 2,924 (19.5%) | 34.1% referral-to-specialist drop-off | 28.0% | +521 specialist visits; **+364 diagnoses** | Reducing median wait 28 to 25 days equals **16,971 patient-days earlier** across current completers | 487 hours / **$15,594** |
| Recover appointments | 2,032 (13.5%) | No-show, cancellation, or unable-to-contact queue | Recover 10% | +203 visits; **+142 diagnoses** | Outreach within 48 hours; cancellation rebooking within 7 days | 508 hours / **$16,256** |
| Close specialist outcomes | 1,709 (11.4%) | 30.2% specialist-to-diagnosis drop-off | 25.0% | **+295 diagnoses** | Outcome recorded within 14 days | 228 hours / **$7,293** |
| Navigate high-friction cases | 2,533 (16.9%) | 86.6% of open referrals carry an access flag | Resolve 10% to a visit | +253 visits; **+177 diagnoses** | Barrier and next action recorded at day 30 | 844 hours / **$27,018** |

The scenarios are **standalone planning estimates** and should not be summed because the appointment and high-friction populations overlap the open-referral queue.

## 1. Close the Referral Decision

**Problem:** Of 13,276 patients reaching primary care, 4,695 have no subsequent referral, equal to 31.3% of the full cohort and a 35.4% stage drop-off.

**Operating rule:** At day 7, require one documented outcome: referral sent, referral not indicated with reason, family declined, or outreach unsuccessful. Route cases still unresolved at day 14 to the clinic operations manager.

**Owner:** Primary-care referral coordinator.

**Business target:** Reduce stage drop-off to 30.0%. This creates approximately 712 additional referrals and 328 additional diagnoses if downstream conversion remains unchanged.

**Measurement:** Weekly unresolved count, percentage resolved within 7 days, and PCP-to-referral conversion.

## 2. Run a Capacity-Aware Specialist Queue

**Problem:** 2,924 referrals remain open. The queue includes 754 critical, 1,137 urgent, and 1,033 routine referrals. Low-capacity networks complete specialist visits for 29.9% of the cohort versus 42.0% in high-capacity networks.

**Operating rule:** Schedule critical referrals within 7 days and urgent referrals within 14 days. Review routine cases open at day 30 for authorization, financial clearance, appointment status, distance, and alternate-site capacity; escalate unresolved cases at day 45.

**Owner:** Specialty scheduling lead.

**Business target:** Reduce referral-to-specialist drop-off from 34.1% to 28.0%, producing about 521 additional specialist visits and 364 diagnoses at the current diagnostic-closure rate.

**Time target:** Reduce median completed wait from 28 to 25 days. Applied to the current 5,657 completed visits, that represents 16,971 patient-days of earlier specialist access. This is a timing measure, not staff-hours saved.

## 3. Recover Missed Appointments

**Problem:** 2,032 patients require appointment recovery: 692 no-shows, 613 cancellations, and 727 unable-to-contact cases.

**Operating rule:** Contact no-shows within 48 hours, offer cancelled cases a new date within 7 days, and make two attempts using different channels for unable-to-contact cases before community-outreach escalation.

**Owner:** Care navigation team.

**Business target:** Recover 10% of the queue, equal to about 203 additional specialist visits and 142 diagnoses at the current 69.8% specialist-to-diagnosis conversion.

**Measurement:** Recovery rate by status, percentage contacted within SLA, days to rebooking, and eventual specialist completion.

## 4. Close the Specialist Outcome

**Problem:** 1,709 completed specialist visits have no recorded diagnosis, rule-out, testing plan, or follow-up outcome. That is 30.2% of specialist visits and 11.4% of the full cohort.

**Operating rule:** Add visits without an outcome after 14 days to a diagnostic-closure queue. Require diagnosis, rule-out, testing plan, or documented follow-up disposition.

**Owner:** Cardiology operations and documentation-quality lead.

**Business target:** Reduce stage drop-off to 25.0%, closing approximately 295 additional outcomes.

**Measurement:** Open closure queue, percentage closed within 14 days, and specialist-to-diagnosis conversion.

## 5. Navigate High-Friction Access Cases

**Problem:** 2,533 open referrals have at least one access flag: Medicaid/uninsured coverage, high SVI, travel over 40 miles, low-capacity assignment, or unresolved authorization/financial clearance. They represent 86.6% of the open-referral queue.

**Operating rule:** At day 30, assign a navigator to record the dominant barrier, next action, and due date. Use financial-clearance terminology for uninsured patients rather than insurance authorization language.

**Owner:** Access manager.

**Business target:** Resolve 10% of this queue to a specialist visit, equal to approximately 253 visits and 177 diagnoses at current downstream conversion.

**Measurement:** Resolution rate by barrier, time to next action, completion gaps by payer/SVI/capacity, and urgent-case wait as a balancing measure.

## Financial Interpretation

The dataset does not contain salaries, reimbursement, treatment costs, or avoided-utilization values. Therefore, it cannot support a defensible dollar benefit or ROI claim.

The dollar amounts above estimate **labor capacity required to operate each queue**, using the following transparent assumptions:

| Queue | Minutes per record | Loaded hourly cost |
|---|---:|---:|
| Referral decision review | 8 | $32 |
| Open-referral scheduling review | 10 | $32 |
| Appointment recovery outreach | 15 | $32 |
| Diagnostic-closure review | 8 | $32 |
| High-friction navigation | 20 | $32 |

These assumptions should be replaced with an employer's actual handling times and loaded labor rate. A real ROI model would additionally require the financial value of a completed specialist visit or diagnosis.

## Leadership Scorecard

Review monthly:

1. Diagnosis completion rate and count.
2. PCP-to-referral drop-off and unresolved decisions over 7 days.
3. Open referrals by priority, capacity tier, and age.
4. Referral-to-specialist conversion and median completed wait.
5. Appointment recovery rate and time to rebooking.
6. Diagnostic-closure queue and 14-day closure rate.
7. Completion gaps by payer, SVI, distance, and capacity.
8. Staff hours used versus the workload assumption.

## Guardrail

This is a synthetic operations model. The recommendations demonstrate workflow analytics and planning methods; they are not clinical guidance, causal estimates, or guaranteed financial returns.
