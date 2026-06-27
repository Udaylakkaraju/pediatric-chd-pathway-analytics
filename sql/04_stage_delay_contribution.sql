-- File: 04_stage_delay_contribution.sql
-- Purpose: wait-time contribution by stage
-- Business question: Which transition has the longest average wait?
-- Output: average days for each major stage transition

SELECT
  ROUND(AVG(days_symptom_to_pcp_clean), 2) AS avg_days_symptom_to_primary_care,
  ROUND(AVG(days_pcp_to_referral_clean), 2) AS avg_days_primary_care_to_referral,
  ROUND(AVG(days_referral_to_specialist_clean), 2) AS avg_days_referral_to_specialist,
  ROUND(AVG(days_specialist_to_diagnosis_clean), 2) AS avg_days_specialist_to_diagnosis
FROM mart_delay_scored_cleaned;
