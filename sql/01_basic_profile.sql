-- File: 01_basic_profile.sql
-- Purpose: quick quality/profile snapshot
-- Business question: How large are key tables and how complete are pathway dates?
-- Output: row counts + stage-date coverage counts

SELECT 'stg_patients' AS table_name, COUNT(*) AS rows FROM stg_patients
UNION ALL
SELECT 'stg_referrals', COUNT(*) FROM stg_referrals
UNION ALL
SELECT 'mart_delay_scored_cleaned', COUNT(*) FROM mart_delay_scored_cleaned;

SELECT
  COUNT(*) AS patients,
  SUM(CASE WHEN first_pcp_date IS NOT NULL THEN 1 ELSE 0 END) AS has_primary_care,
  SUM(CASE WHEN referral_date IS NOT NULL THEN 1 ELSE 0 END) AS has_referral,
  SUM(CASE WHEN specialist_date IS NOT NULL THEN 1 ELSE 0 END) AS has_specialist,
  SUM(CASE WHEN diagnosis_date IS NOT NULL THEN 1 ELSE 0 END) AS has_diagnosis
FROM mart_delay_scored_cleaned;
