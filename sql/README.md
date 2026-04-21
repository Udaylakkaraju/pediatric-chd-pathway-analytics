# SQL Pack (Simple + Interview-Friendly)

This SQL folder is intentionally short and easy to read.

Each file focuses on one business question:

1. `01_basic_profile.sql` -> How big is each table?
2. `02_pathway_funnel.sql` -> How many patients reach each stage?
3. `03_stage_dropoff.sql` -> Where do we lose patients?
4. `04_stage_delay_contribution.sql` -> Which stage has the longest waits?
5. `05_insurance_segmentation.sql` -> Are payer groups different?
6. `06_provider_root_cause.sql` -> Which providers have low referral completion?
7. `07_trend_by_month.sql` -> Is diagnosis rate improving over time?
8. `08_cohort_scorecard.sql` -> One compact executive scorecard

## Tables used

- `mart_delay_scored_cleaned` (main patient mart)
- `stg_referrals`
- `stg_providers`

## Notes

- Queries use simple SQL patterns: `GROUP BY`, `CASE WHEN`, `CTE`, and one window function.
- Keep this as a learning + portfolio layer, then adapt syntax for your target database.
