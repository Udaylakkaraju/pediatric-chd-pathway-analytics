-- Business question: Are pathway outcomes improving, and is the trend sustained?
-- Note: cohort is indexed by symptom_onset_date (first pathway event), and
-- reached_diagnosis is derived from diagnosis_date since the mart stores dates, not flags.
WITH monthly AS (
    SELECT
        STRFTIME('%Y-%m', symptom_onset_date) AS cohort_month,
        COUNT(*) AS patients,
        SUM(CASE WHEN diagnosis_date IS NOT NULL THEN 1 ELSE 0 END) AS diagnoses,
        100.0 * SUM(CASE WHEN diagnosis_date IS NOT NULL THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0)
            AS diagnosis_rate_pct
    FROM mart_delay_scored_cleaned
    GROUP BY STRFTIME('%Y-%m', symptom_onset_date)
),
with_windows AS (
    SELECT
        *,
        LAG(diagnosis_rate_pct) OVER (ORDER BY cohort_month) AS prior_month_rate,
        AVG(diagnosis_rate_pct) OVER (
            ORDER BY cohort_month
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS rolling_3_month_rate
    FROM monthly
)
SELECT
    cohort_month,
    patients,
    diagnoses,
    ROUND(diagnosis_rate_pct, 1) AS diagnosis_rate_pct,
    ROUND(diagnosis_rate_pct - prior_month_rate, 1) AS month_over_month_change_pp,
    ROUND(rolling_3_month_rate, 1) AS rolling_3_month_rate_pct
FROM with_windows
ORDER BY cohort_month;
