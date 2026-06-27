-- File: 12_running_total_diagnoses.sql
-- Purpose: Track cumulative diagnoses and running diagnosis rate by month
-- Business question: How is the total diagnosed patient count building over time?
-- Technique: Window functions (SUM OVER with ORDER BY for running totals)
-- Output: Monthly cohort with running totals and cumulative diagnosis rate

WITH monthly AS (
  SELECT
    STRFTIME('%Y-%m', symptom_onset_date)            AS symptom_month,
    COUNT(*)                                          AS cohort_n,
    SUM(CASE WHEN diagnosis_date IS NOT NULL
             THEN 1 ELSE 0 END)                       AS diagnosed_n
  FROM mart_delay_scored_cleaned
  GROUP BY STRFTIME('%Y-%m', symptom_onset_date)
)

SELECT
  symptom_month,
  cohort_n,
  diagnosed_n,
  ROUND(diagnosed_n * 100.0 / cohort_n, 1)           AS monthly_diagnosis_rate_pct,
  SUM(cohort_n)    OVER (ORDER BY symptom_month)      AS running_total_patients,
  SUM(diagnosed_n) OVER (ORDER BY symptom_month)      AS running_total_diagnosed,
  ROUND(
    SUM(diagnosed_n) OVER (ORDER BY symptom_month) * 100.0 /
    SUM(cohort_n)    OVER (ORDER BY symptom_month), 1
  )                                                    AS cumulative_diagnosis_rate_pct
FROM monthly
ORDER BY symptom_month;
