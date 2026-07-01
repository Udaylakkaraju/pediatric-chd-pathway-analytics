# Pediatric CHD Pathway Analytics - Project Bullets

## One-Line Positioning

Built an Excel + SQL healthcare operations project analyzing a 15,000-patient CHD pathway inside a 100,000-patient synthetic EHR dataset, with Python used for reproducible generation and validation.

## Resume-Ready Bullets

- Built an end-to-end analytics workflow across 100,000 patients, 240,000 encounters, 720,000 observations, and 50,000 referrals, including a 15,000-patient CHD pathway cohort.
- Created a source-to-mart data model with sequential care stages and business dimensions for payer, SVI, referral priority, authorization, appointment status, distance, region, and provider capacity.
- Wrote 17 SQLite analyses spanning data-quality audits, joins, conditional aggregation, CTEs, `ROW_NUMBER`, `RANK`, `NTILE`, `LAG`, and rolling averages.
- Built an interactive Excel workbook with formula-driven KPIs, dynamic action queues, lookups, scenario analysis, charts, validation controls, and a 15,000-row analysis table.
- Identified the main pathway bottlenecks: 3,948 of 15,000 patients reached diagnosis (26.3%), with 35.4% drop-off from PCP to referral and 34.1% from referral to specialist.
- Built a stage scorecard and access segmentation analysis; found a 28-day median specialist wait and a 12.1-point specialist-completion gap between high- and low-capacity networks.
- Modeled operational scenarios with sequential funnel math; estimated that two targeted 5-point conversion improvements could add about 610 diagnoses.
- Added automated tests for chronology, foreign keys, stage nesting, source consistency, metric calculations, and realistic payer/SVI/capacity effects.

## Interview One-Liner

I turned a care-coordination problem into a measurable operations funnel, built trustworthy source data and SQL outputs, and translated the bottlenecks into timed work queues and measurable recommendations.

## Non-Healthcare Framing

The same framework applies to customer onboarding, claims processing, sales handoffs, support escalation, or any multi-step workflow where records stall, exit, or complete.
