-- File: 05_insurance_segmentation.sql
-- Purpose: payer segmentation
-- Business question: Do diagnosis rates or delays vary meaningfully by insurance type?
-- Output: payer-level patient count, average delay score, and diagnosis rate

SELECT
  insurance_type AS payer,
  COUNT(*) AS patients,
  ROUND(AVG(delay_severity_score_clean), 2) AS avg_delay_score,
  ROUND(AVG(CASE WHEN diagnosis_date IS NOT NULL THEN 1.0 ELSE 0.0 END), 4) AS diagnosis_rate
FROM mart_delay_scored_cleaned
GROUP BY insurance_type
ORDER BY patients DESC;
