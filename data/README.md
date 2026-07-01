# Generated Data

The large raw, staging, and SQLite files are generated locally and intentionally excluded from Git.

Generate the complete dataset with:

```bash
python scripts/regenerate_realistic_data.py
python scripts/build_core_analytics_outputs.py
python scripts/run_sql_queries.py
```

Generated scale:

| Table | Rows |
|---|---:|
| Patients | 100,000 |
| CHD analytical mart | 15,000 |
| Encounters | 240,000 |
| Observations | 720,000 |
| Referrals | 50,000 |
| Conditions | 20,000 |
| Procedures | 7,500 |

The compact analytical mart remains versioned at `data/marts/cleaned/mart_delay_scored_cleaned.csv` so reviewers can inspect the analysis without regenerating the full EHR-style source layer.
