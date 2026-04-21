-- File: 02_pathway_funnel.sql
-- Purpose: pathway funnel summary
-- Business question: How many patients reach each stage, and what share moves forward?
-- Output: stage counts + transition conversion rates

SELECT
  COUNT(*) AS symptom_patients,
  SUM(CASE WHEN first_pcp_date IS NOT NULL THEN 1 ELSE 0 END) AS primary_care_patients,
  SUM(CASE WHEN referral_date IS NOT NULL THEN 1 ELSE 0 END) AS referral_patients,
  SUM(CASE WHEN specialist_date IS NOT NULL THEN 1 ELSE 0 END) AS specialist_patients,
  SUM(CASE WHEN diagnosis_date IS NOT NULL THEN 1 ELSE 0 END) AS diagnosed_patients,

  ROUND(
    SUM(CASE WHEN first_pcp_date IS NOT NULL THEN 1 ELSE 0 END) * 1.0 / COUNT(*), 4
  ) AS symptom_to_primary_care_rate,
  ROUND(
    SUM(CASE WHEN referral_date IS NOT NULL THEN 1 ELSE 0 END) * 1.0 /
    NULLIF(SUM(CASE WHEN first_pcp_date IS NOT NULL THEN 1 ELSE 0 END), 0), 4
  ) AS primary_care_to_referral_rate,
  ROUND(
    SUM(CASE WHEN specialist_date IS NOT NULL THEN 1 ELSE 0 END) * 1.0 /
    NULLIF(SUM(CASE WHEN referral_date IS NOT NULL THEN 1 ELSE 0 END), 0), 4
  ) AS referral_to_specialist_rate,
  ROUND(
    SUM(CASE WHEN diagnosis_date IS NOT NULL THEN 1 ELSE 0 END) * 1.0 /
    NULLIF(SUM(CASE WHEN specialist_date IS NOT NULL THEN 1 ELSE 0 END), 0), 4
  ) AS specialist_to_diagnosis_rate
FROM mart_delay_scored_cleaned;
