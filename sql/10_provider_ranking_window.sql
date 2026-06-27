-- File: 10_provider_ranking_window.sql
-- Purpose: Rank providers by referral completion rate within each specialty
-- Business question: Within each specialty, who are the top and bottom performers on referral completion?
-- Technique: Window functions (RANK, AVG OVER PARTITION BY)
-- Output: Provider ranking within specialty with completion rate vs specialty average

WITH provider_stats AS (
  SELECT
    p.provider_id,
    p.provider_name,
    p.specialty,
    COUNT(*)                                                          AS referrals_sent,
    ROUND(AVG(CASE WHEN r.completed IN ('1','t','true','True')
                   THEN 1.0 ELSE 0.0 END), 4)                        AS completion_rate
  FROM stg_referrals r
  LEFT JOIN stg_providers p ON r.from_provider_id = p.provider_id
  WHERE p.specialty IS NOT NULL
  GROUP BY p.provider_id, p.provider_name, p.specialty
  HAVING COUNT(*) >= 15
),

specialty_avg AS (
  SELECT
    specialty,
    ROUND(AVG(completion_rate), 4) AS specialty_avg_completion
  FROM provider_stats
  GROUP BY specialty
)

SELECT
  ps.provider_id,
  ps.provider_name,
  ps.specialty,
  ps.referrals_sent,
  ps.completion_rate,
  sa.specialty_avg_completion,
  ROUND(ps.completion_rate - sa.specialty_avg_completion, 4) AS vs_specialty_avg,
  RANK() OVER (
    PARTITION BY ps.specialty
    ORDER BY ps.completion_rate DESC
  ) AS rank_within_specialty
FROM provider_stats ps
JOIN specialty_avg sa ON ps.specialty = sa.specialty
ORDER BY ps.specialty, rank_within_specialty;
