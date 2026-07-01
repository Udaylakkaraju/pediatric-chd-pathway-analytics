-- Business question: Is the source data reliable enough for analysis?
WITH quality_checks AS (
    SELECT 'Patient ID uniqueness' AS check_name,
           COUNT(*) - COUNT(DISTINCT patient_id) AS issue_count
    FROM stg_patients

    UNION ALL

    SELECT 'Encounter patient foreign keys', COUNT(*)
    FROM stg_encounters e
    LEFT JOIN stg_patients p ON e.patient_id = p.patient_id
    WHERE p.patient_id IS NULL

    UNION ALL

    SELECT 'Referral patient foreign keys', COUNT(*)
    FROM stg_referrals r
    LEFT JOIN stg_patients p ON r.patient_id = p.patient_id
    WHERE p.patient_id IS NULL

    UNION ALL

    SELECT 'Encounter dates before birth', COUNT(*)
    FROM stg_encounters e
    JOIN stg_patients p ON e.patient_id = p.patient_id
    WHERE DATE(e.encounter_datetime) < DATE(p.dob)

    UNION ALL

    SELECT 'Referral dates before birth', COUNT(*)
    FROM stg_referrals r
    JOIN stg_patients p ON r.patient_id = p.patient_id
    WHERE DATE(r.referral_datetime) < DATE(p.dob)

    UNION ALL

    SELECT 'Diagnosis before referral', COUNT(*)
    FROM mart_delay_scored_cleaned
    WHERE diagnosis_date IS NOT NULL
      AND referral_date IS NOT NULL
      AND DATE(diagnosis_date) < DATE(referral_date)
)
SELECT
    check_name,
    issue_count,
    CASE WHEN issue_count = 0 THEN 'PASS' ELSE 'REVIEW' END AS status
FROM quality_checks
ORDER BY status DESC, check_name;
