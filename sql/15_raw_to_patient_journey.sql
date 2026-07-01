-- Technical question: How can normalized source tables become one analysis-ready journey?
-- Note: staging lower-cases text columns (see scripts/regenerate_realistic_data.py
-- write_staging), so category/stage filters below match the lower-cased stg_* values.
WITH chd_patients AS (
    SELECT *
    FROM stg_patients
    WHERE has_chd = 1
),
ranked_referrals AS (
    SELECT
        r.*,
        ROW_NUMBER() OVER (
            PARTITION BY r.patient_id
            ORDER BY DATETIME(r.referral_datetime), r.referral_id
        ) AS referral_order
    FROM stg_referrals r
    WHERE r.referral_category = 'chd'
),
first_stage_dates AS (
    SELECT
        patient_id,
        MIN(CASE WHEN care_stage = 'symptom' THEN encounter_datetime END) AS symptom_date,
        MIN(CASE WHEN care_stage = 'pcp' THEN encounter_datetime END) AS pcp_date,
        MIN(CASE WHEN care_stage = 'specialist' THEN encounter_datetime END) AS specialist_date
    FROM stg_encounters
    GROUP BY patient_id
),
first_diagnosis AS (
    SELECT patient_id, MIN(condition_start) AS diagnosis_date
    FROM stg_conditions
    WHERE condition_category = 'chd'
    GROUP BY patient_id
),
first_intervention AS (
    SELECT patient_id, MIN(procedure_datetime) AS intervention_date
    FROM stg_procedures
    WHERE procedure_category = 'chd intervention'
    GROUP BY patient_id
)
SELECT
    p.patient_id,
    p.age_years,
    p.sex,
    p.insurance_type,
    p.svi_index,
    p.clinic_region,
    p.distance_to_specialist_miles,
    p.chd_type,
    o.provider_capacity_tier,
    s.symptom_date,
    s.pcp_date,
    r.referral_datetime AS referral_date,
    s.specialist_date,
    d.diagnosis_date,
    i.intervention_date,
    r.referral_priority,
    r.authorization_status,
    r.appointment_status,
    CAST(JULIANDAY(s.pcp_date) - JULIANDAY(s.symptom_date) AS INTEGER) AS days_symptom_to_pcp,
    CAST(JULIANDAY(r.referral_datetime) - JULIANDAY(s.pcp_date) AS INTEGER) AS days_pcp_to_referral,
    CAST(JULIANDAY(s.specialist_date) - JULIANDAY(r.referral_datetime) AS INTEGER) AS days_referral_to_specialist,
    CASE WHEN d.diagnosis_date IS NOT NULL THEN 1 ELSE 0 END AS reached_diagnosis
FROM chd_patients p
LEFT JOIN first_stage_dates s ON p.patient_id = s.patient_id
LEFT JOIN ranked_referrals r
    ON p.patient_id = r.patient_id AND r.referral_order = 1
LEFT JOIN first_diagnosis d ON p.patient_id = d.patient_id
LEFT JOIN first_intervention i ON p.patient_id = i.patient_id
LEFT JOIN stg_organizations o ON p.assigned_specialist_org_id = o.org_id
ORDER BY p.patient_id;
