-- File: 06_provider_root_cause.sql
-- Purpose: provider triage view
-- Business question: Which providers have lower referral completion at meaningful volume?
-- Output: provider-level referral counts + completion rates (minimum-volume filtered)

SELECT
  p.provider_id,
  p.provider_name,
  p.specialty,
  COUNT(*) AS referrals_sent,
  ROUND(AVG(CASE WHEN r.completed = 1 THEN 1.0 ELSE 0.0 END), 4) AS referral_completion_rate
FROM stg_referrals r
LEFT JOIN stg_providers p
  ON r.from_provider_id = p.provider_id
GROUP BY p.provider_id, p.provider_name, p.specialty
HAVING COUNT(*) >= 15
ORDER BY referral_completion_rate ASC, referrals_sent DESC;
