# Pediatric CHD Pathway Analytics - Project Bullets

Use these for resume, LinkedIn, portfolio notes, and interview prep.

## One-Line Positioning

Built a healthcare operations funnel analytics project using Python, SQL, Excel-ready outputs, and Power BI-ready tables to track 4,969 synthetic pediatric CHD patients through a diagnostic pathway and identify where patients are lost or delayed.

## Resume-Ready Bullets

- Built an end-to-end operations analytics project using Python, SQL, Excel-ready exports, and Power BI-ready tables to analyze 4,969 synthetic pediatric CHD patient records across symptom, primary care, referral, specialist visit, and diagnosis stages.

- Created a patient-level analytical mart from synthetic EHR-style data, added realistic workflow fields such as referral priority, authorization status, appointment status, provider capacity tier, and distance to specialist, and validated sequential pathway logic with automated tests.

- Identified the largest pathway bottlenecks: only 1,042 of 4,969 patients reached diagnosis (21.0%), with 43.8% drop-off from PCP to referral and 44.8% drop-off from specialist visit to diagnosis.

- Built a coordination scorecard combining stage conversion, drop-off, average wait, and median wait; found referral-to-specialist access had the longest median wait at 36 days.

- Modeled operational improvement scenarios with sequential funnel math; estimated that improving PCP-to-referral and specialist-to-diagnosis conversion by 5 percentage points each could add about 196 diagnoses in the synthetic cohort.

- Added a pytest validation suite to verify funnel math, counterfactual baselines, output consistency, and conversion-rate validity across generated analytics and SQL outputs.

## Interview One-Liner

I took a vague care coordination problem, turned it into a measurable funnel, validated the numbers, and built business-ready outputs that show where patients are lost, how long they wait, and which operational fixes could move the outcome.

## Non-Healthcare Framing

This can also be described as an operations funnel analytics project. The same framework applies to customer onboarding, sales handoffs, claims processing, support escalation, or any multi-step workflow where records can stall, drop off, or complete.

## Best Stack Summary

Python + SQL + Excel-ready outputs + Power BI-ready data + pytest validation.
