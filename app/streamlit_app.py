"""
Congenital Heart Disease diagnostic delay — analytics dashboard.
Run from project root: python -m streamlit run app/streamlit_app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from chd_analytics.paths import ANALYTICS as AN

st.set_page_config(
    page_title="Congenital Heart Disease — pathway analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Bar/line colors tuned for dark chart backgrounds
PALETTE = {
    "primary": "#2dd4bf",
    "secondary": "#94a3b8",
    "accent": "#fb923c",
    "muted": "#64748b",
}

# Dark surfaces — readable light text; avoids white-on-white label overlap
CHART_PAPER = "#111827"
CHART_PLOT = "#1f2937"
CHART_GRID = "rgba(148, 163, 184, 0.25)"
CHART_FONT = "#e5e7eb"
CHART_TITLE = "#f8fafc"


def load_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(AN / name)


@st.cache_data
def funnel_df():
    return load_csv("funnel metrics.csv")


@st.cache_data
def dropoff_df():
    return load_csv("stage dropoff.csv")


@st.cache_data
def delay_buckets_df():
    return load_csv("delay buckets.csv")


@st.cache_data
def insurance_df():
    return load_csv("insurance analysis.csv")


@st.cache_data
def counterfactual_df():
    return load_csv("recommendations_counterfactuals.csv")


@st.cache_data
def scorecard_df():
    df = load_csv("coordination_failure_scorecard.csv")
    valid = pd.to_numeric(df["stage_order"], errors="coerce").notna()
    return df.loc[valid].copy()


def _read_optional_csv(name: str) -> pd.DataFrame | None:
    p = AN / name
    if not p.exists():
        return None
    return pd.read_csv(p)


def _apply_chart_style(fig, title: str, *, height: int = 380) -> None:
    fig.update_layout(
        template="plotly_dark",
        height=height,
        title=dict(
            text=title,
            font=dict(size=15, color=CHART_TITLE),
            x=0,
            xanchor="left",
        ),
        margin=dict(l=8, r=16, t=52, b=8),
        paper_bgcolor=CHART_PAPER,
        plot_bgcolor=CHART_PLOT,
        font=dict(color=CHART_FONT, size=12),
        legend=dict(font=dict(color=CHART_FONT)),
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor=CHART_GRID,
        zeroline=False,
        tickfont=dict(color=CHART_FONT),
        title_font=dict(color=CHART_FONT),
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor=CHART_GRID,
        zeroline=False,
        tickfont=dict(color=CHART_FONT),
        title_font=dict(color=CHART_FONT),
    )


def _sidebar_context(funnel_row: pd.Series) -> None:
    n_sym = int(funnel_row["symptom"])
    n_dx = int(funnel_row["diagnosis"])
    rate = 100.0 * n_dx / n_sym
    st.sidebar.markdown("### Why this dashboard")
    st.sidebar.markdown(
        "**Congenital heart disease (CHD)** means structural heart problems present from birth. "
        "Here we focus on **where** pediatric patients stall or leave the documented pathway **before** "
        "diagnosis—whether delays cluster in access, referral, specialty, or closure. "
        "This supports **operations and care coordination**, not clinical decisions."
    )
    st.sidebar.divider()
    st.sidebar.markdown("### At a glance")
    st.sidebar.metric("Patients with symptom on file", f"{n_sym:,}")
    st.sidebar.metric("Reached recorded diagnosis", f"{n_dx:,}")
    st.sidebar.metric("Pathway completion (diagnosis / symptom)", f"{rate:.1f}%")
    st.sidebar.caption(
        "Completion rate answers: “Of everyone who entered with a symptom, how many got a diagnosis in data?”"
    )
    st.sidebar.divider()
    st.sidebar.info(
        "**Data:** Synthetic EHR-style cohort for analytics demonstration. "
        "Trends and scenarios are illustrative.",
        icon="ℹ️",
    )


def tab_overview() -> None:
    funnel = funnel_df()
    row = funnel.iloc[0]
    n_sym = int(row["symptom"])
    n_dx = int(row["diagnosis"])
    dx_rate = 100.0 * n_dx / n_sym

    dd = dropoff_df()
    worst = dd.loc[dd["drop_off_rate"].idxmax()]

    st.markdown(
        f"**Population:** {n_sym:,} patients with a documented symptom on the pathway. "
        f"**Outcome:** {n_dx:,} have a recorded diagnosis (**{dx_rate:.1f}%**). "
        "The charts below show **where volume is lost** between stages and **how severe delay is** when patients do move forward."
    )

    st.success(
        "**Key takeaways** · "
        f"(1) Most patients **do not** reach diagnosis in this pathway view (~**{100 - dx_rate:.0f}%**). "
        f"(2) The largest **single-stage** losses are **{worst['stage']}** and the other high bar in the drop-off chart—"
        "prioritize referral completion and diagnostic closure. "
        "(3) **Payer** differences exist but are smaller than pathway leakage—think system coordination first. "
        "(4) Scenario bars are **planning math**, not guaranteed program impact."
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Symptom cohort", f"{n_sym:,}", help="Patients entering the funnel with symptom documented")
    c2.metric("Recorded diagnoses", f"{n_dx:,}", help="Patients with a diagnosis date in the extract")
    c3.metric("Diagnosis rate", f"{dx_rate:.1f}%", help="Diagnoses ÷ symptom cohort")
    c4.metric("Not diagnosed (in data)", f"{100 - dx_rate:.1f}%", help="Remaining after pathway")

    st.divider()

    st.markdown("#### 1 · Pathway volume: where patients are in the record")
    st.caption(
        "**What this chart shows:** Count at each documented stage. Width shrinking means fewer patients "
        "carried forward—not necessarily “bad” clinically, but a coordination signal in admin data."
    )
    stages = ["Symptom", "PCP", "Referral", "Specialist", "Diagnosis"]
    counts = [int(row[k]) for k in ["symptom", "pcp", "referral", "specialist", "diagnosis"]]
    funnel_plot = go.Figure(
        go.Funnel(
            y=stages,
            x=counts,
            textinfo="value+percent initial",
            textfont=dict(color=CHART_TITLE, size=12),
            marker=dict(color=[PALETTE["primary"]] * len(stages), line=dict(width=0)),
        )
    )
    _apply_chart_style(
        funnel_plot,
        "Patients reaching each care stage (symptom → diagnosis)",
        height=420,
    )
    st.plotly_chart(funnel_plot, width="stretch")

    col_a, col_b = st.columns(2)

    with col_a:
        st.caption(
            "**What this chart shows:** Share of patients who **had the prior stage** but **did not** show "
            "the next stage in data. Higher bar = bigger leak for operations to investigate."
        )
        fig_d = px.bar(
            dd,
            x="drop_off_rate",
            y="stage",
            orientation="h",
            labels={
                "drop_off_rate": "Share lost before next stage",
                "stage": "Pathway step",
            },
            color_discrete_sequence=[PALETTE["accent"]],
        )
        _apply_chart_style(fig_d, "Drop-off: where the pathway loses patients (higher = worse leakage)", height=360)
        fig_d.update_xaxes(tickformat=".0%", title_standoff=8)
        st.plotly_chart(fig_d, width="stretch")

    with col_b:
        st.caption(
            "**What this chart shows:** Of those eligible at each step, what fraction **moved forward** "
            "(same math as referral/specialty completion KPIs)."
        )
        conv = pd.DataFrame(
            {
                "Step": [
                    "After symptom → PCP",
                    "After PCP → referral",
                    "After referral → specialist",
                    "After specialist → diagnosis",
                ],
                "Share moving forward": [
                    float(row["symptom_to_pcp_conversion"]),
                    float(row["pcp_to_referral_conversion"]),
                    float(row["referral_to_specialist_conversion"]),
                    float(row["specialist_to_diagnosis_conversion"]),
                ],
            }
        )
        fig_c = px.bar(
            conv,
            x="Step",
            y="Share moving forward",
            labels={"Share moving forward": "Conversion rate"},
            color_discrete_sequence=[PALETTE["primary"]],
        )
        _apply_chart_style(fig_c, "Stage conversion: forward progress rate", height=360)
        fig_c.update_yaxes(tickformat=".0%", title="Conversion rate")
        fig_c.update_xaxes(tickangle=-20)
        st.plotly_chart(fig_c, width="stretch")

    st.divider()

    st.markdown("#### 2 · Delay severity across the cohort")
    st.caption(
        "**What this chart shows:** How many patients fall into each **delay score** bucket (engineered severity "
        "metric from the mart). Use it to see if the problem is a thin tail vs widespread delay."
    )
    db = delay_buckets_df()
    order = ["No Delay", "Low", "Moderate", "High", "Severe"]
    vc = db["delay_bucket"].value_counts()
    bucket_counts = vc.reindex([x for x in order if x in vc.index])
    bcdf = pd.DataFrame({"bucket": bucket_counts.index.astype(str), "patients": bucket_counts.values})
    fig_h = px.bar(
        bcdf,
        x="bucket",
        y="patients",
        labels={"bucket": "Delay bucket", "patients": "Number of patients"},
        color_discrete_sequence=[PALETTE["secondary"]],
    )
    _apply_chart_style(fig_h, "Distribution of pathway delay severity (delay score buckets)", height=380)
    st.plotly_chart(fig_h, width="stretch")

    col_i, col_j = st.columns(2)
    ins = insurance_df().sort_values("diagnosis_rate")
    with col_i:
        st.caption("**What this chart shows:** Diagnosis rate by **payer**—equity check vs main funnel.")
        fig_i = px.bar(
            ins,
            x="insurance_type",
            y="diagnosis_rate",
            labels={"diagnosis_rate": "Share reaching diagnosis", "insurance_type": "Payer"},
            color_discrete_sequence=[PALETTE["primary"]],
        )
        _apply_chart_style(fig_i, "Diagnosis rate by insurance type", height=340)
        fig_i.update_yaxes(tickformat=".0%", title="Diagnosis rate")
        st.plotly_chart(fig_i, width="stretch")

    with col_j:
        st.caption("**What this chart shows:** Average **delay score** by payer—compare spread to funnel story.")
        fig_j = px.bar(
            ins,
            x="insurance_type",
            y="avg_delay",
            labels={"avg_delay": "Mean score", "insurance_type": "Payer"},
            color_discrete_sequence=[PALETTE["secondary"]],
        )
        _apply_chart_style(fig_j, "Average delay score by insurance type", height=340)
        fig_j.update_yaxes(title="Mean delay score")
        st.plotly_chart(fig_j, width="stretch")

    st.divider()

    st.markdown("#### 3 · Planning scenarios (illustrative)")
    st.caption(
        "**What this chart shows:** If **one or two** stage conversion rates improved by a few points—holding "
        "other stages fixed—how many **additional** modeled diagnoses might result. Not a forecast of a live program."
    )
    cf = counterfactual_df()
    cf_plot = cf[cf["scenario"].astype(str) != "baseline (current funnel)"].copy()
    fig_cf = px.bar(
        cf_plot,
        x="extra_diagnoses_vs_baseline",
        y="scenario",
        orientation="h",
        labels={
            "extra_diagnoses_vs_baseline": "Extra modeled diagnoses vs today",
            "scenario": "",
        },
        color_discrete_sequence=[PALETTE["accent"]],
    )
    _apply_chart_style(fig_cf, "Scenario impact: extra diagnoses if conversion improves (modeled)", height=340)
    st.plotly_chart(fig_cf, width="stretch")

    st.divider()

    st.markdown("#### 4 · Coordination scorecard (leakage + time)")
    st.caption(
        "**What this table shows:** For each transition, **conversion**, **drop-off**, and **mean days** among "
        "those with a completed interval—use to prioritize both **loss** and **wait time**."
    )
    sc = scorecard_df()
    show = sc[
        [
            "stage_transition",
            "conversion_rate",
            "drop_off_rate",
            "avg_days_among_converters",
        ]
    ].copy()
    show = show.rename(
        columns={
            "stage_transition": "Transition",
            "conversion_rate": "Conversion",
            "drop_off_rate": "Drop-off",
            "avg_days_among_converters": "Mean days (converters)",
        }
    )
    st.dataframe(show, width="stretch", hide_index=True, height=220)

    with st.expander("Regenerate outputs (developers)"):
        st.code(
            "python scripts/build_coordination_scorecard.py\n"
            "python scripts/compute_counterfactuals.py\n"
            "python scripts/data_quality_checks.py\n"
            "python scripts/trend_analysis.py\n"
            "python scripts/advanced_segmentation.py\n"
            "python scripts/root_cause_analysis.py",
            language="bash",
        )


def tab_quality_and_trends() -> None:
    st.markdown(
        "**Purpose:** Trust checks on the mart (nulls, dates, outliers) and **whether completion or delay** "
        "moves over time when symptom month is used as the cohort index."
    )

    qc = _read_optional_csv("QC_Report.csv")
    if qc is None:
        st.info("Run `python scripts/data_quality_checks.py` to generate `outputs/analytics/QC_Report.csv`.")
    else:
        st.markdown("##### Data quality — summary checks")
        show = qc.loc[qc["category"].isin(["mart", "date_sequence", "alignment", "delay_score"])].copy()
        st.dataframe(show, width="stretch", hide_index=True)
        with st.expander("Null rates by column"):
            st.dataframe(qc.loc[qc["category"] == "null_rate"], width="stretch", hide_index=True)
        with st.expander("Long intervals flagged (>730 days)"):
            st.dataframe(
                qc.loc[qc["check_name"].str.startswith("outlier_gt_", na=False)],
                width="stretch",
                hide_index=True,
            )

    st.divider()
    tr = _read_optional_csv("trend_by_month.csv")
    if tr is None or tr.empty:
        st.info("Run `python scripts/trend_analysis.py` to generate trend file.")
        return

    st.markdown("##### Trends by symptom month (mature months only)")
    note = tr["interpretation_note"].iloc[0] if "interpretation_note" in tr.columns else ""
    st.caption(note + " **What the lines show:** whether **diagnosis rate** and **mean delay** move for older symptom cohorts (reduces bias from very recent symptoms not yet diagnosed).")

    c1, c2 = st.columns(2)
    with c1:
        fig1 = px.line(
            tr,
            x="symptom_index_month",
            y="diagnosis_rate",
            markers=True,
            labels={
                "diagnosis_rate": "Share with diagnosis",
                "symptom_index_month": "Month of symptom (index)",
            },
        )
        _apply_chart_style(fig1, "Diagnosis rate over time (by symptom month)", height=380)
        fig1.update_yaxes(tickformat=".0%")
        st.plotly_chart(fig1, width="stretch")
    with c2:
        fig2 = px.line(
            tr,
            x="symptom_index_month",
            y="mean_delay_score",
            markers=True,
            labels={
                "mean_delay_score": "Mean delay score",
                "symptom_index_month": "Month of symptom (index)",
            },
        )
        _apply_chart_style(fig2, "Mean delay score over time (by symptom month)", height=380)
        st.plotly_chart(fig2, width="stretch")


def tab_segments() -> None:
    st.markdown(
        "**Purpose:** Compare **diagnosis rate** and **mean delay** across segments "
        "(payer, **heart defect severity** class, age, era, social vulnerability index). "
        "Use to spot equity or acuity gaps—not to explain the whole system alone."
    )
    seg = _read_optional_csv("segment_comparison.csv")
    if seg is None:
        st.info("Run `python scripts/advanced_segmentation.py` to generate segment outputs.")
        return
    dims = sorted(seg["segment_dimension"].astype(str).unique())
    dim = st.selectbox("Choose segment", dims, index=0)
    sub = seg.loc[seg["segment_dimension"] == dim].sort_values("n", ascending=False)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(
            sub,
            x="segment_value",
            y="diagnosis_rate",
            labels={"diagnosis_rate": "Diagnosis rate", "segment_value": "Segment"},
        )
        _apply_chart_style(fig, f"Diagnosis rate — {dim}", height=400)
        fig.update_yaxes(tickformat=".0%")
        fig.update_xaxes(tickangle=-35)
        st.plotly_chart(fig, width="stretch")
    with c2:
        fig2 = px.bar(
            sub,
            x="segment_value",
            y="mean_delay",
            labels={"mean_delay": "Mean delay score", "segment_value": "Segment"},
            color_discrete_sequence=[PALETTE["accent"]],
        )
        _apply_chart_style(fig2, f"Mean delay score — {dim}", height=400)
        fig2.update_xaxes(tickangle=-35)
        st.plotly_chart(fig2, width="stretch")

    st.dataframe(
        sub.rename(
            columns={
                "segment_value": "Segment",
                "n": "Patients",
                "diagnosis_rate": "Diagnosis rate",
                "mean_delay": "Mean delay",
                "median_delay": "Median delay",
            }
        ),
        width="stretch",
        hide_index=True,
    )


def tab_root_cause() -> None:
    st.markdown(
        "**Purpose:** Exploratory signals—referral volume/completion and **echo timing** proxies—not root cause proof. "
        "No payer authorization fields in this synthetic schema."
    )
    summ = AN / "root_cause_summary.md"
    if summ.exists():
        st.markdown(summ.read_text(encoding="utf-8"))
    else:
        st.info("Run `python scripts/root_cause_analysis.py` to generate the summary.")

    prov = _read_optional_csv("provider_performance.csv")
    if prov is not None and not prov.empty:
        st.markdown("##### Referring providers (minimum referral volume applied)")
        st.caption("Lower completion rate may reflect access, documentation, or data capture—use for triage, not blame.")
        view = prov.sort_values("referral_completed_rate", ascending=True).head(25)
        st.dataframe(view, width="stretch", hide_index=True)
    elif prov is not None:
        st.warning("No providers met the minimum referral threshold.")


def main() -> None:
    funnel = funnel_df()
    row = funnel.iloc[0]
    _sidebar_context(row)

    st.title("Pediatric congenital heart disease — diagnostic pathway")
    st.caption(
        "**Congenital heart disease (CHD)** = structural heart problems present from birth. "
        "Care coordination view from first symptom in data through diagnosis (synthetic cohort)."
    )

    overview, quality, segments, root = st.tabs(
        ["Overview", "Quality & trends", "Segments", "Root-cause probes"]
    )
    with overview:
        tab_overview()
    with quality:
        tab_quality_and_trends()
    with segments:
        tab_segments()
    with root:
        tab_root_cause()


if __name__ == "__main__":
    main()
