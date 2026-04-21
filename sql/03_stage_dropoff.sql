-- File: 03_stage_dropoff.sql
-- Purpose: leakage by stage
-- Business question: At which stage is patient loss highest before the next step?
-- Output: transition-level drop-off rates

WITH c AS (
  SELECT
    COUNT(*) AS symptom,
    SUM(CASE WHEN first_pcp_date IS NOT NULL THEN 1 ELSE 0 END) AS pcp,
    SUM(CASE WHEN referral_date IS NOT NULL THEN 1 ELSE 0 END) AS referral,
    SUM(CASE WHEN specialist_date IS NOT NULL THEN 1 ELSE 0 END) AS specialist,
    SUM(CASE WHEN diagnosis_date IS NOT NULL THEN 1 ELSE 0 END) AS diagnosis
  FROM mart_delay_scored_cleaned
)
SELECT 'Symptom -> Primary Care' AS stage, ROUND(1 - pcp * 1.0 / NULLIF(symptom, 0), 4) AS dropoff_rate FROM c
UNION ALL
SELECT 'Primary Care -> Referral', ROUND(1 - referral * 1.0 / NULLIF(pcp, 0), 4) FROM c
UNION ALL
SELECT 'Referral -> Specialist', ROUND(1 - specialist * 1.0 / NULLIF(referral, 0), 4) FROM c
UNION ALL
SELECT 'Specialist -> Diagnosis', ROUND(1 - diagnosis * 1.0 / NULLIF(specialist, 0), 4) FROM c;
