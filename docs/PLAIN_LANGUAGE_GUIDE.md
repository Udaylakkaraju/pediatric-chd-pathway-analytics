# Plain-Language Guide

This guide maps technical names to business-friendly wording.

## Folder names

- `data/raw/` → source records  
- `data/marts/cleaned/` → analysis-ready patient table  
- `outputs/analytics/` → technical outputs (for analysts)  
- `outputs/business_ready/` → plain-language outputs (for business users)  
- `scripts/` → run-ready analysis steps  
- `app/streamlit_app.py` → interactive dashboard  

## Key terms

- **Funnel** → patient pathway counts by stage  
- **Conversion rate** → share of patients moving to the next stage  
- **Drop-off rate** → share of patients lost before the next stage  
- **Delay score** → combined indicator of pathway delay severity  
- **Counterfactual / Scenario** → “what-if” estimate, not guaranteed outcome  

## Most useful business-ready files

- `outputs/business_ready/patient_pathway_summary.csv`  
- `outputs/business_ready/stage_loss_rates.csv`  
- `outputs/business_ready/average_wait_by_stage.csv`  
- `outputs/business_ready/payer_comparison.csv`  
- `outputs/business_ready/stage_leakage_and_waits.csv`  
- `outputs/business_ready/monthly_pathway_trends.csv`  
- `outputs/business_ready/scenario_impact_estimates.csv`  
- `outputs/business_ready/data_health_report.csv`  

## Run command

```bash
python scripts/create_business_friendly_exports.py
```
