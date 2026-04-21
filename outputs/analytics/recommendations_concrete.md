# Concrete recommendations (metrics-backed)

Scope: pediatric CHD pathway (symptom → PCP → referral → specialist → diagnosis). Figures below come from `funnel metrics.csv`, `stage delay contribution.csv`, and modeled scenarios in `recommendations_counterfactuals.csv` (see `compute_counterfactuals.py`).

**Baseline snapshot (current funnel)**

| Metric | Value |
|--------|--------|
| Patients in symptom cohort | 4,969 |
| Reaching diagnosis | 1,042 |
| Share of symptom cohort diagnosed | **21.0%** |
| Largest single-stage drop-offs | **PCP → referral 43.8%**; **specialist → diagnosis 44.8%** |
| Mean days among converters — PCP → referral | **273** |
| Mean days among converters — specialist → diagnosis | **575** |

*Caveat:* “Extra diagnoses” scenarios assume the **same downstream conversions** except where noted, and isolate **one or two** stage-rate changes. They illustrate **order-of-magnitude** impact of coordination fixes, not a forecast of a specific program.

---

## How this ties to real-world use (operations, not theory)

These metrics mirror what hospitals and networks already run as **access and coordination** work. Your funnel KPIs are the same *shape* as internal dashboards—even when vendors differ (Epic, Cerner, Meditech, etc.).

| Theme in this project | What it looks like on the ground | Who often owns it | How success is measured (same spirit as your metrics) |
|------------------------|-----------------------------------|---------------------|--------------------------------------------------------|
| **PCP → referral** | **Closed-loop referral management**: referral sent → received → scheduled → completed (or documented reason not completed). Primary-care **Patient-Centered Medical Home** (PCMH) and care-coordination programs often track **referral completion rate** and **days to specialist appointment**. | Primary-care leadership, ambulatory ops, care navigation | Referral conversion / completion %, **median days** referral → booked visit |
| **Referral → specialist** | **Specialty access**: reducing **wait time** for first cardiology / pediatric cardiology visit; queue management; sometimes **eConsult** or triage so urgent CHD suspects are seen sooner. | Specialty clinic ops, access center, cardiology service line | % referred who get a specialist visit, **days wait** for first appointment |
| **Specialist → diagnosis** | **Diagnostic closure**: echo or advanced imaging scheduled and resulted; **problem list** and billing diagnosis aligned when appropriate; reducing “lost to follow-up” after first specialist contact. Teaching hospitals often track **time to definitive diagnosis** for complex cohorts internally. | Pediatric cardiology, imaging services, clinic managers | % of specialist patients with **documented diagnosis** (or clear pending plan), **days** first specialist → diagnosis |
| **Cross-cutting** | **CHD programs** (regional children’s hospitals, **ACC/AHA**-aligned quality work) routinely report **timeliness** and **care gaps**—your stages are a simplified version of that pathway view. | Quality, clinical program leadership | Funnel-style **conversion** + **interval** metrics by quarter |

**Important:** This project uses **synthetic EHR-style data**. Real programs would validate definitions against **local coding** (referral orders vs messages), **same-network vs outside referrals**, and **clinical appropriateness**—your metrics stay **analytics hypotheses** until run on production extracts.

---

## 1) Close the referral gap after PCP (care coordination + primary network)

**Problem metric:** Only **56.2%** of patients with a PCP visit receive a recorded referral (`pcp_to_referral_conversion`). This stage loses **~1,897** patients (4,333 → 2,436).

**Recommendation**

- Implement **closed-loop referral tracking** (status, timeliness, reason if not referred) and a **monthly referral completion rate** by clinic.
- Target: raise PCP→referral conversion by **+5 to +10 percentage points** over 12–18 months through workflow and access (not a substitute for clinical judgment).

**Modeled impact (same cohort math)**

| Target | Approx. extra diagnoses | Symptom cohort reaching diagnosis |
|--------|-------------------------|-----------------------------------|
| +5 pp PCP→referral | **+93** | **22.8%** (vs 21.0%) |
| +10 pp PCP→referral | **+185** | **24.7%** |

**KPIs to monitor:** `pcp_to_referral_conversion`, median **PCP → referral days** (reduce delay among referred patients toward operational targets).

**Time lever:** Mean PCP→referral interval is **273 days** among converters — even a **30-day** reduction in average delay for referred patients is a concrete operations target (e.g. **273 → 243 days**), reported as trend, not guaranteed “lives saved.”

---

## 2) Close the loop after specialist visit (cardiology / diagnostic completion)

**Problem metric:** Only **55.2%** of patients who saw a specialist reach a recorded diagnosis (`specialist_to_diagnosis_conversion`). This stage loses **847** patients (1,889 → 1,042).

**Recommendation**

- Standardize **specialist encounter documentation** and **diagnostic closure** (echo, formal CHD diagnosis code, or explicit “pending” with next step) within **X business days** of first specialist visit — set by program leadership.
- Target: **+10 percentage points** on specialist→diagnosis conversion through scheduling, testing throughput, and care navigation.

**Modeled impact**

| Target | Approx. extra diagnoses | Symptom cohort reaching diagnosis |
|--------|-------------------------|-----------------------------------|
| +10 pp specialist→diagnosis | **+189** | **24.8%** |

**KPIs:** `specialist_to_diagnosis_conversion`, median **specialist → diagnosis days** (baseline mean **575 days** — prioritize reducing long-tail delay, not only the mean).

---

## 3) Reduce leakage between referral and specialist (access / scheduling)

**Problem metric:** **22.5%** drop-off referral → specialist; mean interval among converters **224 days**.

**Recommendation**

- Prioritize **time-to-specialist** SLAs for referred CHD suspects (e.g. booked within **30–60 days** by severity tier — tiering can use your `chd_type` or acuity flags later).

**Modeled impact**

| Target | Approx. extra diagnoses |
|--------|-------------------------|
| +10 pp referral→specialist | **+134** |

**KPIs:** `referral_to_specialist_conversion`, median **referral → specialist days**.

---

## 4) Combined “coordination package” (small gains on the two worst leaks)

**Recommendation:** Run **referral completion** and **diagnostic closure** improvements together at modest targets.

**Modeled impact**

| Target | Approx. extra diagnoses | Symptom cohort reaching diagnosis |
|--------|-------------------------|-----------------------------------|
| +5 pp PCP→referral **and** +5 pp specialist→diagnosis | **+196** | **24.9%** (~**+3.9 percentage points** on diagnosis rate vs baseline) |

---

## 5) Insurance and equity (monitoring — not the primary lever in this dataset)

**Observation:** Diagnosis rate by insurance ranges **~17%–22%**; differences are **small relative to pathway leakage** (see `insurance analysis.csv`).

**Recommendation:** Use insurance as a **segmentation lens** for equity monitoring (e.g. track conversion and median delay by payer **in the same funnel**), not as the sole explanation for system delay.

---

## Summary for executives

| Priority | Lever | Example target | Modeled extra diagnoses (illustrative) |
|----------|--------|----------------|----------------------------------------|
| 1 | Referral after PCP | +10 pp conversion | **+185** |
| 2 | Diagnosis after specialist | +10 pp conversion | **+189** |
| 3 | Referral → specialist access | +10 pp conversion | **+134** |
| 4 | Combined modest | +5 pp + +5 pp | **+196** |

**Bottom line:** The system loses **~79%** of the symptom cohort before diagnosis; **concrete** programs should target **measurable conversion and time-to-next-step** at **PCP→referral**, **referral→specialist**, and **specialist→diagnosis**, with numbers above as **planning anchors** tied to your synthetic cohort.
