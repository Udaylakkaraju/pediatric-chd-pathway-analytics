-- File: 11_delay_percentile_bands.sql
-- Purpose: Segment patients into delay severity bands and compare diagnosis outcomes
-- Business question: Do high-delay patients have worse diagnosis rates? Where is the threshold?
-- Technique: CASE bucketing + GROUP BY aggregation with HAVING
-- Output: Delay band, patient count, diagnosis rate, avg wait per stage

WITH delay_bands AS (
  SELECT
    patient_id,
    insurance_type,
    chd_type,
    delay_severity_score_clean,
    diagnosis_date,
    days_symptom_to_pcp_clean,
    days_referral_to_specialist_clean,
    CASE
      WHEN delay_severity_score_clean < 5        THEN '1_Low (0-5)'
      WHEN delay_severity_score_clean < 15       THEN '2_Moderate (5-15)'
      WHEN delay_severity_score_clean < 30       THEN '3_High (15-30)'
      ELSE                                            '4_Critical (30+)'
    END AS delay_band
  FROM mart_delay_scored_cleaned
)

SELECT
  delay_band,
  COUNT(*)                                                         AS patients,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1)              AS pct_of_cohort,
  SUM(CASE WHEN diagnosis_date IS NOT NULL THEN 1 ELSE 0 END)      AS diagnosed,
  ROUND(AVG(CASE WHEN diagnosis_date IS NOT NULL
                 THEN 1.0 ELSE 0.0 END) * 100, 1)                 AS diagnosis_rate_pct,
  ROUND(AVG(days_symptom_to_pcp_clean), 1)                        AS avg_days_to_pcp,
  ROUND(AVG(days_referral_to_specialist_clean), 1)                AS avg_days_referral_to_spec,
  ROUND(AVG(delay_severity_score_clean), 2)                       AS avg_delay_score
FROM delay_bands
GROUP BY delay_band
ORDER BY delay_band;
