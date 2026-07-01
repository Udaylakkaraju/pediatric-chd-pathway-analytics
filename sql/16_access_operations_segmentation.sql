-- Business question: Which access groups face the greatest pathway barriers?
-- Note: mart_delay_scored_cleaned stores stage completion as dates (NULL = not
-- reached), not boolean flags, so "reached_*" indicators are derived with CASE.
WITH flagged AS (
    SELECT
        *,
        CASE WHEN referral_date IS NOT NULL THEN 1 ELSE 0 END AS reached_referral,
        CASE WHEN specialist_date IS NOT NULL THEN 1 ELSE 0 END AS reached_specialist,
        CASE WHEN diagnosis_date IS NOT NULL THEN 1 ELSE 0 END AS reached_diagnosis
    FROM mart_delay_scored_cleaned
),
segmented AS (
    SELECT
        *,
        NTILE(4) OVER (ORDER BY svi_index) AS svi_quartile,
        NTILE(4) OVER (ORDER BY distance_to_specialist_miles) AS distance_quartile
    FROM flagged
),
access_groups AS (
    SELECT
        CASE
            WHEN insurance_type = 'uninsured' THEN 'Uninsured'
            WHEN svi_quartile = 4 AND distance_quartile = 4 THEN 'High SVI + Long Distance'
            WHEN svi_quartile = 4 THEN 'High SVI'
            WHEN distance_quartile = 4 THEN 'Long Distance'
            ELSE 'Lower Access Risk'
        END AS access_group,
        *
    FROM segmented
)
SELECT
    access_group,
    COUNT(*) AS patients,
    SUM(reached_referral) AS referred_patients,
    SUM(reached_specialist) AS specialist_patients,
    SUM(reached_diagnosis) AS diagnosed_patients,
    ROUND(100.0 * SUM(reached_diagnosis) / NULLIF(COUNT(*), 0), 1) AS diagnosis_rate_pct,
    ROUND(AVG(CASE WHEN reached_specialist = 1 THEN days_referral_to_specialist_clean END), 1)
        AS avg_referral_to_specialist_days
FROM access_groups
GROUP BY access_group
ORDER BY diagnosis_rate_pct, patients DESC;
