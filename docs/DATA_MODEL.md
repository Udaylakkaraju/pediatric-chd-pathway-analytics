# Data Model

## Purpose

The project uses normalized EHR-style source tables for realistic relational analysis and a patient-level mart for repeatable Excel and SQL reporting.

## Source Tables

| Table | Grain | Primary key | Main relationships |
|---|---|---|---|
| `stg_patients` | One row per patient | `patient_id` | Parent of encounters, referrals, conditions, and procedures |
| `stg_encounters` | One row per encounter | `encounter_id` | `patient_id`, `provider_id`, `org_id` |
| `stg_referrals` | One row per referral | `referral_id` | `patient_id`, referring and receiving providers |
| `stg_conditions` | One row per condition record | `condition_id` | `patient_id`, diagnosing provider |
| `stg_procedures` | One row per procedure | `procedure_id` | `patient_id`, `provider_id`, `org_id` |
| `stg_observations` | One row per clinical observation | `observation_id` | `patient_id`, encounter |
| `stg_providers` | One row per provider | `provider_id` | Organization dimension |
| `stg_organizations` | One row per facility/network | `org_id` | Provider and patient assignments |

## Analytical Mart

`mart_delay_scored_cleaned` has one row per CHD pathway patient. It combines patient attributes with the first valid date at each pathway stage, derived wait intervals, access dimensions, operational statuses, and completion flags.

The mart is deliberately denormalized for Excel usability and stable KPI calculation. SQL file `15_raw_to_patient_journey.sql` demonstrates how the normalized source model is transformed into this analysis grain using CTEs, joins, conditional aggregation, and `ROW_NUMBER`.

## Relationship Flow

```text
organizations -> providers -> encounters/referrals/conditions/procedures
       |                         |
       +------ patients --------+
                    |
                    v
          patient pathway mart
                    |
             SQL + Excel KPIs
```

## Modeling Rules

- Patient IDs are unique and all child records must resolve to a patient.
- Events cannot occur before birth.
- Pathway stages are sequential: symptom, PCP, referral, specialist, diagnosis, intervention.
- Later-stage nulls represent valid pathway attrition, not automatically missing-data errors.
- Wait intervals are calculated only for patients completing both relevant stages.
- Intervention is conditional on diagnosis and clinical severity.
