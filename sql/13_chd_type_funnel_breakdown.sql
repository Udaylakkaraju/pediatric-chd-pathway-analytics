-- File: 13_chd_type_funnel_breakdown.sql
-- Purpose: Break down nested funnel conversion rates by CHD type
-- Business question: Do certain CHD types have systematically worse pathway completion?
-- Technique: CTE + conditional aggregation with stage-specific denominators
-- Output: Per CHD type patient count, nested conversion rates, and diagnosis rate

WITH patient_flags AS (
  SELECT
    chd_type,
    patient_id,
    CASE WHEN first_pcp_date IS NOT NULL THEN 1 ELSE 0 END AS reached_pcp,
    CASE WHEN first_pcp_date IS NOT NULL AND referral_date IS NOT NULL THEN 1 ELSE 0 END AS pcp_and_referral,
    CASE WHEN referral_date IS NOT NULL AND specialist_date IS NOT NULL THEN 1 ELSE 0 END AS referral_and_specialist,
    CASE WHEN specialist_date IS NOT NULL AND diagnosis_date IS NOT NULL THEN 1 ELSE 0 END AS specialist_and_diagnosis,
    CASE WHEN referral_date IS NOT NULL THEN 1 ELSE 0 END AS has_referral,
    CASE WHEN specialist_date IS NOT NULL THEN 1 ELSE 0 END AS has_specialist,
    CASE WHEN diagnosis_date IS NOT NULL THEN 1 ELSE 0 END AS has_diagnosis,
    delay_severity_score_clean
  FROM mart_delay_scored_cleaned
)

SELECT
  chd_type,
  COUNT(*) AS total_patients,

  ROUND(SUM(reached_pcp) * 100.0 / NULLIF(COUNT(*), 0), 1) AS pct_reached_pcp,

  ROUND(
    SUM(pcp_and_referral) * 100.0 /
    NULLIF(SUM(reached_pcp), 0), 1
  ) AS pct_pcp_to_referral,

  ROUND(
    SUM(referral_and_specialist) * 100.0 /
    NULLIF(SUM(has_referral), 0), 1
  ) AS pct_referral_to_specialist,

  ROUND(
    SUM(specialist_and_diagnosis) * 100.0 /
    NULLIF(SUM(has_specialist), 0), 1
  ) AS pct_specialist_to_diagnosis,

  ROUND(SUM(has_diagnosis) * 100.0 / NULLIF(COUNT(*), 0), 1) AS overall_diagnosis_rate_pct,
  ROUND(AVG(delay_severity_score_clean), 2) AS avg_delay_score

FROM patient_flags
GROUP BY chd_type
ORDER BY overall_diagnosis_rate_pct DESC;
