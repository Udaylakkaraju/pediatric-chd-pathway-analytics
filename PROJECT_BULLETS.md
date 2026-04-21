# Project Bullets (Technical + Business-Friendly)

Use these bullets for resume, LinkedIn, portfolio, or interview prep.  
They are written to be understandable to both technical and non-technical audiences.

## Full-story bullets (detailed)

- Framed and solved a healthcare operations problem in pediatric congenital heart disease (CHD): too many patients were delayed or lost before diagnosis; translated this into measurable pathway questions (where leakage happens, how long each stage takes, and which operational levers matter most).

- Built an analysis-ready patient mart from 8 synthetic EHR-style source tables (4,969 patients) and modeled the care pathway from symptom onset to diagnosis; standardized stage timelines and interval features to support consistent funnel, delay, and segmentation analysis.

- Implemented a production-style quality layer with 20+ automated data checks (null rates, duplicate keys, date-order violations, future/implausible dates, negative intervals, long-delay outliers, and mart-vs-funnel alignment), improving trust in downstream metrics before recommendation-making.

- Quantified pathway performance with clear stage metrics: only ~21% of symptom-stage patients reached diagnosis (~79% non-completion in the documented pathway), with largest leakage at PCP->Referral (~44%) and Specialist->Diagnosis (~45%).

- Diagnosed operational risk patterns behind drop-off: 49% of patients had no referral record; Specialist->Diagnosis remained a high-friction stage with ~575 mean days among converters; used provider rollups (200+ providers meeting minimum referral volume) for triage, not blame.

- Built a coordination failure scorecard combining leakage and wait-time burden by stage (conversion, drop-off, average/median wait), enabling teams to prioritize the highest-impact bottlenecks instead of focusing on delay averages alone.

- Performed multi-dimensional segmentation (payer, CHD severity tier, age band, cohort era, social vulnerability tertiles, plus payer x severity) and found system-flow issues outweighed payer-only differences, guiding recommendations toward coordination workflows rather than narrow subgroup fixes.

- Modeled intervention scenarios using sequential conversion math with one-at-a-time +/-5 percentage-point sensitivity analysis; identified closed-loop referral completion and diagnostic closure as highest-ROI levers, with modeled upside of ~196 additional diagnoses (~+3.9 percentage points).

- Added maturity-lag-adjusted trend analysis to reduce right-censoring bias for recent cohorts; observed substantial delay improvement in post-2021 cohorts (mean delay ~1,351 -> ~424 days, ~3.2x reduction), strengthening the time-based operations narrative.

- Delivered results through a 4-tab Streamlit + Plotly dashboard and a business-friendly reporting layer (`outputs/business_ready/`) with plain-language file/column names, enabling self-serve monitoring by operations and leadership users without analyst dependency.


## Resume-ready bullets (concise)

- Engineered a patient-level CHD pathway analytics mart (4,969 patients; 8 source tables), implemented 20+ automated data quality checks, and validated metric consistency with a multi-module pytest suite and CI workflow.

- Identified primary diagnosis bottlenecks (PCP->Referral ~44% drop-off; Specialist->Diagnosis ~45% drop-off, 575-day mean among converters), built a stage-level coordination scorecard, and analyzed 200+ providers for referral completion triage.

- Modeled intervention scenarios with +/-5pp sensitivity and recommended closed-loop referral + diagnostic closure workflows, projecting ~196 additional diagnoses (+3.9pp), then deployed findings via Streamlit dashboard plus business-friendly exports for non-technical stakeholders.


## Interview one-liner

"I took a vague care-coordination problem, turned it into measurable pathway metrics, validated data quality and math rigor, and translated the analysis into operational recommendations with quantified upside that both analysts and hospital operators can use."
