-- File: 08_cohort_scorecard.sql
-- Purpose: executive one-row scorecard
-- Business question: What is the high-level pathway status in one quick view?
-- Output: stage counts + average delay score

SELECT
  COUNT(*) AS symptom_patients,
  SUM(CASE WHEN first_pcp_date IS NOT NULL THEN 1 ELSE 0 END) AS primary_care_patients,
  SUM(CASE WHEN referral_date IS NOT NULL THEN 1 ELSE 0 END) AS referral_patients,
  SUM(CASE WHEN specialist_date IS NOT NULL THEN 1 ELSE 0 END) AS specialist_patients,
  SUM(CASE WHEN diagnosis_date IS NOT NULL THEN 1 ELSE 0 END) AS diagnosed_patients,
  ROUND(AVG(delay_severity_score_clean), 2) AS avg_delay_score
FROM mart_delay_scored_cleaned;
