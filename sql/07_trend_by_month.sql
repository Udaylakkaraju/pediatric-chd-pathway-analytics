-- File: 07_trend_by_month.sql
-- Purpose: monthly trend tracking
-- Business question: Is diagnosis completion improving over symptom-indexed cohorts?
-- Output: monthly cohort counts, diagnosed counts, diagnosis rate, and average delay

SELECT
  STRFTIME('%Y-%m', symptom_onset_date) AS symptom_month,
  COUNT(*) AS cohort_n,
  SUM(CASE WHEN diagnosis_date IS NOT NULL THEN 1 ELSE 0 END) AS diagnosed_n,
  ROUND(AVG(CASE WHEN diagnosis_date IS NOT NULL THEN 1.0 ELSE 0.0 END), 4) AS diagnosis_rate,
  ROUND(AVG(delay_severity_score_clean), 2) AS avg_delay_score
FROM mart_delay_scored_cleaned
GROUP BY STRFTIME('%Y-%m', symptom_onset_date)
ORDER BY symptom_month;
