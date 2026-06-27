-- File: 09_patient_journey_cte.sql
-- Purpose: Build a complete per-patient journey summary using CTEs
-- Business question: For each patient, how long did each stage take and did they reach diagnosis?
-- Technique: CTE chaining to build readable, layered logic
-- Output: One row per patient with all stage intervals and journey status

WITH stage_intervals AS (
  -- Step 1: compute raw intervals per patient
  SELECT
    patient_id,
    insurance_type,
    chd_type,
    symptom_onset_date,
    first_pcp_date,
    referral_date,
    specialist_date,
    diagnosis_date,
    days_symptom_to_pcp_clean       AS days_to_pcp,
    days_pcp_to_referral_clean      AS days_to_referral,
    days_referral_to_specialist_clean AS days_to_specialist,
    days_specialist_to_diagnosis_clean AS days_to_diagnosis
  FROM mart_delay_scored_cleaned
),

journey_flags AS (
  -- Step 2: classify each patient's furthest stage reached
  SELECT
    *,
    CASE
      WHEN diagnosis_date IS NOT NULL  THEN 'Diagnosed'
      WHEN specialist_date IS NOT NULL THEN 'Reached Specialist'
      WHEN referral_date IS NOT NULL   THEN 'Referred'
      WHEN first_pcp_date IS NOT NULL  THEN 'Reached PCP'
      ELSE 'Symptom Only'
    END AS furthest_stage,
    CASE
      WHEN diagnosis_date IS NOT NULL THEN 1 ELSE 0
    END AS reached_diagnosis
  FROM stage_intervals
)

-- Step 3: final output with total pathway days
SELECT
  patient_id,
  insurance_type,
  chd_type,
  furthest_stage,
  reached_diagnosis,
  days_to_pcp,
  days_to_referral,
  days_to_specialist,
  days_to_diagnosis,
  COALESCE(days_to_pcp, 0)
    + COALESCE(days_to_referral, 0)
    + COALESCE(days_to_specialist, 0)
    + COALESCE(days_to_diagnosis, 0) AS total_pathway_days
FROM journey_flags
ORDER BY total_pathway_days DESC;
