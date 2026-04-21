# CHD Diagnostic Delay Analytics System

**A data-driven analysis of pediatric care pathway optimization using synthetic EHR-style data.**

## Overview

This project demonstrates end-to-end healthcare analytics methodology: from problem definition through data engineering, exploratory analysis, root-cause investigation, scenario modeling, and stakeholder communication.

**Data:** Synthetic EHR-style dataset (4,969 patients, 8 source tables)  
**Scope:** Pediatric congenital heart disease (CHD) diagnostic pathway  
**Core Question:** Where do patients drop off in the care pathway, and what interventions would have the highest impact?

---

## Quick Start

### Installation
```bash
pip install -r requirements.txt
pytest tests/  # Validate data consistency
```

### Run Full Analysis Pipeline
```bash
# From project root — generate or validate outputs
python scripts/data_quality_checks.py        # → outputs/analytics/QC_Report.csv
python scripts/trend_analysis.py             # → outputs/analytics/trend_by_month.csv
python scripts/advanced_segmentation.py      # → segment_comparison.csv, segment_deep_dive.md
python scripts/root_cause_analysis.py        # → provider_performance.csv, root_cause_summary.md
python scripts/sensitivity_counterfactuals.py  # → counterfactual_sensitivity.csv

# View interactive dashboard
python -m streamlit run app/streamlit_app.py
```

### Test Suite
```bash
pytest tests/ -v  # Run all validation tests
```

---

## Project Structure

```
CHD Project/
├── README.md
├── PROJECT_CONTEXT.md                 # Full narrative + metric definitions + runbook
├── requirements.txt
├── pytest.ini
├── chd_analytics/                     # Shared package (paths, funnel math, CHD severity)
├── scripts/                           # Runnable analysis (import chd_analytics)
├── app/streamlit_app.py               # Dashboard
├── data/
│   ├── raw/                           # 8 synthetic EHR source tables
│   └── marts/                         # Patient-level marts + cleaned/ full cohort
├── outputs/analytics/                 # QC, funnel, segments, scenarios, markdown
├── outputs/business_ready/            # Plain-language copies for non-technical users
├── docs/                              # Plain-language guide
└── tests/                             # Pytest (funnel, scorecard, counterfactuals)
```

---

## Key Findings

### Pathway Leakage (The Core Problem)
- **Overall diagnosis rate: 21%** — 79% of symptomatic patients don't reach diagnosis
- **Largest drop-off stages:**
  - PCP → Referral: **43.78% drop-off** (referral completion failure)
  - Specialist → Diagnosis: **44.84% drop-off** (diagnostic closure failure)
- **Delays among converters:**
  - Symptom → PCP: 700.63 days (long entry point)
  - Specialist → Diagnosis: 575.15 days (long diagnostic phase)

### Temporal Trends
- **2021+ cohorts: 424-day mean delay** vs. **2017-2020: 1,351 days**
- **3.2x improvement** in diagnostic throughput for recent symptom cohorts
- Suggests operational improvements or earlier intervention patterns in recent years

### Segmentation Insights (Equity Check)
- **Insurance type:** Minimal variation (diagnosis rate 17.3–22.3%)
- **CHD severity:** Complex cases **11.7% diagnosis rate** vs. Simple **45.8%** (counterintuitive pattern)
- **Age band:** Minimal variation (19.5–21.8%)
- **SVI tertile:** Minimal variation (20.3–22.0%)
- **Interpretation:** System-wide coordination failures > segment-specific disparities

### Root Cause Diagnostics
- **Referral documentation:** 49% of cohort has referral record
  - With referral: 23.8% diagnosis rate
  - Without referral: 18.2% diagnosis rate
- **Diagnostic closure (echo proxy):** 8.8% of diagnosed patients have documented echocardiograms
  - Stalled cohort (specialist→no diagnosis): 7.8% have echo
  - **Suggests diagnostic workup incompleteness as barrier**
- **Provider coverage:** 200 providers with ≥15 referrals each (operational triage candidates)

### Scenario Impact (Counterfactuals)
- **PCP→Referral +5pp:** ~44 additional diagnoses (vs. baseline)
- **PCP→Referral +10pp:** ~185 additional diagnoses
- **Specialist→Diagnosis +10pp:** ~189 additional diagnoses
- **Combined (+5pp each):** ~196 additional diagnoses
- **Sensitivity:** ±5pp variations produce 28–212 diagnosis delta (validates model robustness)

---

## Visualizations

![Pathway Funnel](python%20visuals/Pathway%20Funnel.png)
*Shows patient volume shrinkage across the documented care pathway stages.*

![Delay Severity Score Distribution](python%20visuals/Delay%20Severity%20Score%20Distribution.png)
*Shows the distribution shape of delay severity scores across the cohort.*

![Delay Severity Score Insurance Type](python%20visuals/Delay%20Severity%20Score%20Insurance%20Type.png)
*Compares delay severity distributions across insurance groups.*

![Delay Severity Score (Log Y)](python%20visuals/Delay%20Severity%20Score(Log%20Y).png)
*Shows long-tail behavior in delay severity using a log-scaled y-axis.*

![Interval Distributions](python%20visuals/Interval%20Distributions.png)
*Shows distributions of stage-level delay intervals to highlight where waits cluster.*

![Delay Score vs Days symptoms to pcp](python%20visuals/Delay%20Score%20vs%20Days%20symptoms%20to%20pcp.png)
*Shows association between symptom-to-PCP delay and overall delay severity score.*

---

## Plain-language outputs (for non-technical users)

If you want simpler names for files/columns, generate the business-ready copies:

```bash
python scripts/create_business_friendly_exports.py
```

This creates easy-to-read files under `outputs/business_ready/`, for example:

- `patient_pathway_summary.csv` (pathway counts + completion rates)
- `stage_loss_rates.csv` (where patients are lost)
- `average_wait_by_stage.csv` (average days between stages)
- `payer_comparison.csv` (payer-level delay and diagnosis rates)
- `stage_leakage_and_waits.csv` (single scorecard view)
- `scenario_impact_estimates.csv` (what-if uplift estimates)
- `data_health_report.csv` (data quality checks in plain terms)

See `docs/PLAIN_LANGUAGE_GUIDE.md` for the full terminology map.

---

## Methodology

### Data Quality Framework
20+ automated checks across 4 dimensions:
- **Null rates** (field-level missingness)
- **Date sequencing** (symptom → PCP → referral → specialist → diagnosis → intervention)
- **Future-dated records** (impossible future events)
- **Implausible dates** (before 1995 for pediatric cohort)
- **Negative intervals** (should not occur)
- **Outlier intervals** (>730 days = data quality flag)
- **Funnel alignment** (mart vs. aggregated funnel counts match)

### Analytical Approach
1. **Funnel analysis** — quantify pathway leakage by stage
2. **Trend analysis** — temporal cohort progression with maturity-lag handling (6-month buffer)
3. **Segmentation** — slice cohort by insurance, severity, age, era, SVI; examine 2D interactions
4. **Root cause** — provider rollups, referral documentation rates, diagnostic closure proxies
5. **Sensitivity** — one-at-a-time conversion perturbations (±5pp) to validate model stability
6. **Scenario modeling** — illustrative upside if key conversion rates improve

### Production Features
- **Modular architecture** — shared utilities (paths, funnel math, severity classification)
- **Data validation** — automated QC with configurable thresholds
- **Testing** — pytest suite validating funnel math, metric consistency, counterfactual alignment
- **Documentation** — markdown summaries with business context ("real-world tie-ins")

---

## Important Limitations & Caveats

### Data
- **Synthetic data:** All rows are programmatically generated for demonstration purposes
- **Assumption:** Clinical patterns reflect realistic pediatric CHD workflows (based on domain knowledge)
- **Not causal:** Analysis is descriptive and associational, not causal inference

### Analysis
- **Counterfactuals are scenarios, not forecasts:** Assume isolated conversion improvements; don't account for system interactions or behavioral responses
- **Echo documentation as proxy:** Only 8.8% of diagnosed patients have documented echo—likely reflects synthetic data limitations, not real diagnostic closure rates
- **Provider metrics for triage, not verdicts:** Provider rollups (referral completion) are for operational triage, not individual clinician quality assessment

### Deployment
- **Real EHR integration:** In production, would require:
  - HIPAA compliance and proper data governance
  - Validation against local care pathways and documentation practices
  - Investigation of insurance authorization denials (not in synthetic schema)
  - Cohort definition alignment with clinical definitions

---

## How to Interpret Results

### For Operations Teams
- Use **coordination failure scorecard** to prioritize: focus on stages with both high leakage AND long delays
- Use **provider performance** for referral completion benchmarking and outreach
- Use **trend analysis** to monitor if recent cohorts continue to show shorter delays

### For Leadership
- Use **scenario/counterfactual views** for planning: "If we improve referral completion by X%, what's the modeled diagnosis recovery?"
- Use **segmentation** to confirm system-wide vs. equity-driven barriers (this data suggests system-wide)
- Use **funnel** for transparency: "This is where patients are lost in our pathway"

### For Analytics Colleagues
- Use **QC report** to assess data quality before running own analyses
- Use **test suite** to validate pipeline consistency
- Use **modular scripts** as templates for similar pathway analyses

---

## Running in Your Environment

### Prerequisites
- Python 3.8+
- pandas >= 2.0
- plotly >= 5.18
- streamlit >= 1.28
- pytest (for tests)

### Full Walkthrough
```bash
# 1. Install
pip install -r requirements.txt

# 2. Validate data quality
python scripts/data_quality_checks.py
# Review outputs/analytics/QC_Report.csv for flags

# 3. Run analyses
python scripts/trend_analysis.py
python scripts/advanced_segmentation.py
python scripts/root_cause_analysis.py
python scripts/sensitivity_counterfactuals.py

# 4. Test for consistency
python -m pytest

# 5. View dashboard (from project root)
python -m streamlit run app/streamlit_app.py
# Opens browser at http://localhost:8501

# 6. Review outputs in outputs/analytics/
```

---

## Project Positioning

**This project demonstrates:**
- ✅ End-to-end analytics ownership (problem → data → insights → recommendations)
- ✅ Healthcare domain knowledge (care pathways, referral workflows, equity considerations)
- ✅ Stakeholder-focused thinking (translating metrics to operational decisions)
- ✅ Production-quality code (modular, tested, validated)
- ✅ Data rigor (QC framework, sensitivity analysis, documented caveats)

**Suitable for roles:**
- Data Analyst (healthcare, operations, or general)
- BI Analyst (analytics-focused)
- Analytics Engineer (data pipeline + business logic)

---

## License

This is a demonstration project for educational and portfolio purposes. Synthetic data and code are open to review and discussion.

---

## Questions or Feedback?

This project is designed to be reproducible and discussable. Run the scripts, review the outputs, and you'll have talking points for interviews.

**Key discussion angles:**
- Why did you choose synthetic data over real EHR data?
- What surprised you in the findings (e.g., complexity vs. simplicity paradox)?
- How would you modify this analysis if you had access to [specific constraint]?
- Which findings would you prioritize as an operations director?

---

*Last updated: April 8, 2026*
