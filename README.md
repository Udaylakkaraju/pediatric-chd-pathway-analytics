# Pediatric CHD Care Pathway Analytics

> **End-to-end healthcare operations analytics project** — tracking 4,969 patients through a five-stage diagnostic pathway to identify where they are lost, how long they wait, and what operational changes would help the most.

**Stack:** Python · SQL · Excel · Power BI-ready outputs · pytest

**Data:** Synthetic EHR-style dataset. No real patient records.

---

## The Problem

Only **21% of patients** in this cohort reach a recorded diagnosis. The other 79% stall or exit the pathway before that point — and the data shows *where*, *why*, and *for how long*.

```
Symptom  →  PCP Visit  →  Referral  →  Specialist  →  Diagnosis
  4,969       4,333         2,436        1,889          1,042
```

---

## Key Numbers

| Metric | Value |
|---|---|
| Patients in cohort | 4,969 |
| Reached diagnosis | 1,042 **(21.0%)** |
| Largest single drop-off | Specialist → Diagnosis **(44.8%)** |
| Second-largest drop-off | PCP → Referral **(43.8%)** |
| Longest median wait | Referral → Specialist **(36 days)** |
| Modeled uplift (2 × +5pp conversion) | **+196 additional diagnoses** |

---

## Visual Story

### The funnel — most patients never reach diagnosis

![Pathway Funnel](outputs/charts/portfolio/01_pathway_funnel.png)

### Two stages account for nearly all the loss

![Stage Drop-off](outputs/charts/portfolio/02_stage_dropoff.png)

### Specialty access is the longest wait-time bottleneck

![Wait Time Bottleneck](outputs/charts/portfolio/03_wait_time_bottleneck.png)

### Payer type and social vulnerability drive the widest access gaps

![Access Segments](outputs/charts/portfolio/05_access_segments.png)

### Targeting two conversion points models the most improvement

![Scenario Impact](outputs/charts/portfolio/06_scenario_impact.png)

### Recommendations translated into operating rules with triggers and SLAs

![Operating Rules Roadmap](outputs/charts/portfolio/07_operating_rules_roadmap.png)

---

## What I Built

| Deliverable | Description |
|---|---|
| **Patient-level mart** | `data/marts/cleaned/` — cleaned, scored, stage-flagged |
| **SQL analysis pack** | 13 queries covering funnel, segmentation, window functions, CTEs |
| **Excel skills workbook** | `outputs/CHD_Excel_Skills.xlsx` — INDEX/MATCH, COUNTIFS, AVERAGEIF, nested IF, scenario calculator, dashboard |
| **Power BI-ready tables** | `outputs/bi_ready/` — patient detail, funnel summary, stage drop-off, payer summary |
| **Business-ready CSVs** | `outputs/business_ready/` — plain-language exports for non-technical stakeholders |
| **Operating recommendations** | `docs/KEY_RECOMMENDATIONS.md` — rules with triggers, owners, SLAs, KPIs |
| **Pytest validation suite** | Funnel math, counterfactual baselines, output consistency, conversion-rate validity |

---

## Project Structure

```
data/
  raw/                        Source-style synthetic EHR tables
  marts/cleaned/              Patient-level analytical mart

sql/                          13 SQL queries + regenerated results
scripts/                      Data generation, QA, analytics, exports
tests/                        Pytest validation suite

outputs/
  charts/portfolio/           Visual story (8 charts)
  bi_ready/                   Power BI-ready fact and summary tables
  business_ready/             Plain-language CSVs
  analytics/                  Technical outputs — scorecard, counterfactuals, QC

docs/
  KEY_RECOMMENDATIONS.md      Operating rules with triggers, SLAs, and KPIs
  DATA_DICTIONARY.md          Field definitions
```

---

## Stack

| Layer | Tools |
|---|---|
| Data generation & cleaning | Python, pandas, numpy |
| Analysis | SQL (SQLite), Python |
| Excel skills | COUNTIFS, AVERAGEIF, INDEX/MATCH, nested IF, charts, dashboard |
| Data quality | pytest, QC report |
| BI outputs | Power BI-ready CSVs, Excel workbook |
| Scenario modeling | Python sequential funnel model |

---

## Quick Start

```bash
pip install -r requirements.txt
python scripts/regenerate_realistic_data.py
python scripts/build_core_analytics_outputs.py
python scripts/run_sql_queries.py
pytest
```

---

## Docs

- [`docs/KEY_RECOMMENDATIONS.md`](docs/KEY_RECOMMENDATIONS.md) — operating rules with triggers, owners, SLAs, and KPIs
- [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md) — field definitions for all columns

---

*Synthetic data only. Designed to demonstrate analytics methodology — not real clinical evidence.*
