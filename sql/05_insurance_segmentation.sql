-- File: 05_insurance_segmentation.sql
-- Purpose: payer segmentation
-- Business question: Do pathway completion and specialist waits vary by payer?
-- Wait is calculated only among completed specialist visits and labeled explicitly.

SELECT
  insurance_type AS payer,
  COUNT(*) AS patients,
  ROUND(AVG(CASE WHEN referral_date IS NOT NULL THEN 1.0 ELSE 0.0 END), 4) AS referral_rate,
  ROUND(AVG(CASE WHEN specialist_date IS NOT NULL THEN 1.0 ELSE 0.0 END), 4) AS specialist_completion_rate,
  ROUND(AVG(CASE WHEN diagnosis_date IS NOT NULL THEN 1.0 ELSE 0.0 END), 4) AS diagnosis_rate,
  ROUND(AVG(CASE WHEN days_referral_to_specialist_clean IS NOT NULL THEN days_referral_to_specialist_clean END), 1)
    AS avg_specialist_wait_days_among_completed
FROM mart_delay_scored_cleaned
GROUP BY insurance_type
ORDER BY patients DESC;
