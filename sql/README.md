# SQL Analysis Portfolio

This SQLite-compatible query pack progresses from foundational exploration to intermediate analytical SQL. Together, the queries show how normalized healthcare operations data becomes a validated patient-journey model and a set of business decisions.

## Learning path

| Level | Files | Skills demonstrated |
|---|---|---|
| Foundations | `01`-`05` | `SELECT`, filtering, aggregates, `GROUP BY`, `CASE`, percentages, null-safe division |
| Business analysis | `06`-`08`, `13` | Multi-table joins, conditional aggregation, segmentation, KPI scorecards |
| CTEs and windows | `09`-`12` | CTEs, `RANK`, running totals, windowed averages, analytical bands |
| Data preparation | `14`-`15` | Data-quality tests, foreign-key checks, chronology checks, `ROW_NUMBER` deduplication, raw-to-mart wrangling |
| Intermediate analytics | `16`-`17` | `NTILE`, `LAG`, rolling averages, access-risk segmentation, month-over-month change |

## Business questions

1. How large and complete are the source tables?
2. Where do patients leave the care pathway?
3. Which stage creates the longest delays?
4. How do payer, capacity, region, severity, and CHD type affect outcomes?
5. Which providers and access groups need operational attention?
6. Is performance changing over time?
7. Does the source data pass relational and chronological quality checks?
8. How can normalized raw tables be transformed into one patient-level analytical model?

## Data model

- `stg_patients`: one row per patient; demographics, access factors, and assigned specialist organization.
- `stg_encounters`: one row per care encounter and pathway stage.
- `stg_referrals`: one row per referral; priority, authorization, appointment, and completion status.
- `stg_conditions`: one row per recorded condition.
- `stg_procedures`: one row per procedure.
- `stg_providers` and `stg_organizations`: provider and facility dimensions.
- `mart_delay_scored_cleaned`: one row per CHD pathway patient for repeatable analysis.

Run all queries and export their final result sets with:

```powershell
python scripts/run_sql_queries.py
```

The generated CSVs in `sql/results/` make each query easy to review without requiring a database client.
