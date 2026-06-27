"""
Create a clean static visual pack for the portfolio project.

Outputs:
- outputs/charts/portfolio/01_pathway_funnel.png
- outputs/charts/portfolio/02_stage_dropoff.png
- outputs/charts/portfolio/03_wait_time_bottleneck.png
- outputs/charts/portfolio/04_operational_status_mix.png
- outputs/charts/portfolio/05_access_segments.png
- outputs/charts/portfolio/06_scenario_impact.png
- outputs/charts/portfolio/07_operating_rules_roadmap.png
"""

from __future__ import annotations

import textwrap

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

import _bootstrap_path  # noqa: F401
from chd_analytics.paths import ANALYTICS, COLS, MART_CLEANED, ROOT

OUT_DIR = ROOT / "outputs" / "charts" / "portfolio"

COLORS = {
    "navy": "#243B53",
    "blue": "#2F80ED",
    "teal": "#00A6A6",
    "orange": "#F2994A",
    "red": "#D64545",
    "green": "#219653",
    "purple": "#7B61FF",
    "gray": "#7B8794",
    "light_gray": "#E5E7EB",
    "dark": "#1F2933",
}


def setup_style() -> None:
    sns.set_theme(style="whitegrid")
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.titleweight": "bold",
            "axes.titlesize": 15,
            "axes.labelsize": 11,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "figure.dpi": 150,
            "savefig.dpi": 180,
            "axes.edgecolor": COLORS["light_gray"],
            "grid.color": "#EEF2F7",
        }
    )


def clean_axis(ax) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(COLORS["light_gray"])
    ax.spines["bottom"].set_color(COLORS["light_gray"])
    ax.tick_params(colors=COLORS["dark"])
    ax.xaxis.label.set_color(COLORS["dark"])
    ax.yaxis.label.set_color(COLORS["dark"])
    ax.title.set_color(COLORS["navy"])


def save(fig, filename: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_DIR / filename, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def chart_pathway_funnel() -> None:
    funnel = pd.read_csv(ANALYTICS / "funnel metrics.csv").iloc[0]
    stages = ["Symptom", "Primary care", "Referral", "Specialist visit", "Diagnosis"]
    counts = [funnel["symptom"], funnel["pcp"], funnel["referral"], funnel["specialist"], funnel["diagnosis"]]
    pct_initial = [count / counts[0] for count in counts]

    fig, ax = plt.subplots(figsize=(10, 5.8))
    colors = [COLORS["blue"], COLORS["teal"], COLORS["orange"], COLORS["purple"], COLORS["green"]]
    bars = ax.barh(stages, counts, color=colors, alpha=0.92)
    ax.invert_yaxis()
    ax.set_title("1. Problem: only 21% of patients reach diagnosis", loc="left", pad=14)
    ax.set_xlabel("Patients")
    ax.set_ylabel("")
    ax.set_xlim(0, max(counts) * 1.18)

    for bar, count, pct in zip(bars, counts, pct_initial):
        ax.text(
            bar.get_width() + max(counts) * 0.025,
            bar.get_y() + bar.get_height() / 2,
            f"{int(count):,} ({pct:.1%})",
            va="center",
            ha="left",
            fontsize=10.5,
            color=COLORS["dark"],
        )

    clean_axis(ax)
    save(fig, "01_pathway_funnel.png")


def chart_stage_dropoff() -> None:
    scorecard = pd.read_csv(ANALYTICS / "coordination_failure_scorecard.csv")
    df = scorecard.sort_values("drop_off_rate")
    fig, ax = plt.subplots(figsize=(10, 5.8))
    colors = [COLORS["gray"] if x < 0.40 else COLORS["red"] for x in df["drop_off_rate"]]
    bars = ax.barh(df["stage_transition"], df["drop_off_rate"], color=colors, alpha=0.92)
    ax.set_title("2. Bottleneck: referral and diagnostic closure drive most loss", loc="left", pad=14)
    ax.set_xlabel("Drop-off rate")
    ax.set_ylabel("")
    ax.set_xlim(0, 0.55)
    ax.xaxis.set_major_formatter(lambda x, _: f"{x:.0%}")

    for bar, value in zip(bars, df["drop_off_rate"]):
        ax.text(
            value + 0.012,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.1%}",
            va="center",
            ha="left",
            fontsize=10.5,
            color=COLORS["dark"],
        )

    clean_axis(ax)
    save(fig, "02_stage_dropoff.png")


def chart_wait_time_bottleneck() -> None:
    scorecard = pd.read_csv(ANALYTICS / "coordination_failure_scorecard.csv")
    plot_df = scorecard.melt(
        id_vars="stage_transition",
        value_vars=["avg_days_among_converters", "median_days_among_converters"],
        var_name="metric",
        value_name="days",
    )
    plot_df["metric"] = plot_df["metric"].map(
        {
            "avg_days_among_converters": "Average",
            "median_days_among_converters": "Median",
        }
    )
    fig, ax = plt.subplots(figsize=(10.5, 5.8))
    sns.barplot(
        data=plot_df,
        x="stage_transition",
        y="days",
        hue="metric",
        palette=[COLORS["orange"], COLORS["blue"]],
        ax=ax,
    )
    ax.set_title("3. Delay: specialty access is the longest wait-time step", loc="left", pad=14)
    ax.set_xlabel("")
    ax.set_ylabel("Days among patients completing the step")
    ax.set_ylim(0, max(plot_df["days"]) * 1.25)
    ax.tick_params(axis="x", rotation=15)
    ax.legend(title="", frameon=False, loc="upper left")

    for container in ax.containers:
        ax.bar_label(container, fmt="%.0f", padding=3, fontsize=9, color=COLORS["dark"])

    clean_axis(ax)
    save(fig, "03_wait_time_bottleneck.png")


def chart_scenario_impact() -> None:
    scenarios = pd.read_csv(ANALYTICS / "recommendations_counterfactuals.csv")
    df = scenarios[~scenarios["scenario"].str.contains("baseline", case=False)].copy()
    df["label"] = df["scenario"].str.replace(" percentage points", "pp", regex=False)
    df["label"] = df["label"].apply(lambda x: "\n".join(textwrap.wrap(x, width=30)))
    df = df.sort_values("extra_diagnoses_vs_baseline")

    fig, ax = plt.subplots(figsize=(10, 6.2))
    bars = ax.barh(df["label"], df["extra_diagnoses_vs_baseline"], color=COLORS["green"], alpha=0.9)
    ax.set_title("6. Recommendation: target referral completion and diagnostic closure", loc="left", pad=14)
    ax.set_xlabel("Additional modeled diagnoses")
    ax.set_ylabel("")
    ax.set_xlim(0, df["extra_diagnoses_vs_baseline"].max() * 1.20)

    for bar, value in zip(bars, df["extra_diagnoses_vs_baseline"]):
        ax.text(
            value + 4,
            bar.get_y() + bar.get_height() / 2,
            f"+{value:.0f}",
            va="center",
            ha="left",
            fontsize=10.5,
            color=COLORS["dark"],
        )

    clean_axis(ax)
    save(fig, "06_scenario_impact.png")


def chart_access_segments() -> None:
    mart = pd.read_csv(MART_CLEANED)
    mart["svi_group"] = pd.cut(
        mart["svi_index"],
        bins=[-0.01, 0.33, 0.67, 1.01],
        labels=["Low SVI", "Middle SVI", "High SVI"],
    )

    payer = (
        mart.groupby("insurance_type", observed=True)[COLS["referral_to_specialist"]]
        .median()
        .dropna()
        .reset_index(name="median_days")
        .sort_values("median_days")
    )
    svi = (
        mart.groupby("svi_group", observed=True)[COLS["referral_to_specialist"]]
        .median()
        .dropna()
        .reset_index(name="median_days")
    )

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.4), sharey=True)
    axes[0].bar(payer["insurance_type"], payer["median_days"], color=COLORS["teal"], alpha=0.9)
    axes[0].set_title("By payer", loc="left")
    axes[0].set_xlabel("")
    axes[0].set_ylabel("Median referral-to-specialist wait")

    axes[1].bar(svi["svi_group"].astype(str), svi["median_days"], color=COLORS["purple"], alpha=0.9)
    axes[1].set_title("By social vulnerability", loc="left")
    axes[1].set_xlabel("")
    axes[1].set_ylabel("")

    fig.suptitle(
        "5. Prioritization: access waits vary by payer and social context",
        x=0.02,
        ha="left",
        y=1.02,
        fontweight="bold",
        color=COLORS["navy"],
    )

    for axis in axes:
        axis.set_ylim(0, max(payer["median_days"].max(), svi["median_days"].max()) * 1.25)
        for container in axis.containers:
            axis.bar_label(container, fmt="%.0f", padding=3, fontsize=9, color=COLORS["dark"])
        clean_axis(axis)

    fig.tight_layout()
    save(fig, "05_access_segments.png")


def chart_operational_status_mix() -> None:
    mart = pd.read_csv(MART_CLEANED)
    status = (
        mart["specialist_appointment_status"]
        .value_counts(normalize=True)
        .rename_axis("status")
        .reset_index(name="share")
    )
    status["status"] = status["status"].str.replace("_", " ").str.title()
    status = status.sort_values("share")

    fig, ax = plt.subplots(figsize=(10, 5.8))
    colors = [
        COLORS["green"] if "Completed" in status_name else COLORS["orange"] if "Pending" in status_name else COLORS["gray"]
        for status_name in status["status"]
    ]
    bars = ax.barh(status["status"], status["share"], color=colors, alpha=0.92)
    ax.set_title("4. Diagnosis: drop-off becomes follow-up work when status is visible", loc="left", pad=14)
    ax.set_xlabel("Share of patients")
    ax.set_ylabel("")
    ax.set_xlim(0, status["share"].max() * 1.22)
    ax.xaxis.set_major_formatter(lambda x, _: f"{x:.0%}")

    for bar, value in zip(bars, status["share"]):
        ax.text(
            value + 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.1%}",
            va="center",
            ha="left",
            fontsize=10.5,
            color=COLORS["dark"],
        )

    clean_axis(ax)
    save(fig, "04_operational_status_mix.png")


def chart_operating_rules_roadmap() -> None:
    rules = pd.DataFrame(
        [
            ["Referral decision", "Document referral outcome", "Suspected CHD at PCP", "7 days", "PCP -> Referral drop-off"],
            ["Specialty scheduling", "Schedule critical referrals", "Critical referral", "7 days", "Critical scheduled on time"],
            ["Specialty scheduling", "Schedule urgent referrals", "Urgent referral", "14 days", "Urgent scheduled on time"],
            ["Appointment recovery", "Contact no-shows", "No-show", "48 hours", "No-show outreach rate"],
            ["Appointment recovery", "Reschedule cancelled visits", "Cancelled visit", "7 days", "Reschedule rate"],
            ["Diagnostic closure", "Close specialist visit outcome", "Visit without diagnosis", "14 days", "Specialist -> Diagnosis drop-off"],
            ["Care navigation", "Review high-friction referrals", "Open referral + access risk", "30 days", "Wait gap by segment"],
        ],
        columns=["Workstream", "Rule", "Trigger", "SLA", "KPI"],
    )

    fig, ax = plt.subplots(figsize=(12.5, 6.8))
    ax.axis("off")
    fig.suptitle(
        "7. Operating playbook: convert bottlenecks into timed follow-up rules",
        x=0.03,
        ha="left",
        y=0.98,
        fontweight="bold",
        fontsize=15,
        color=COLORS["navy"],
    )
    fig.text(
        0.03,
        0.91,
        "Each rule turns an analytics finding into an owner, trigger, SLA, and KPI.",
        ha="left",
        fontsize=10.5,
        color=COLORS["dark"],
    )

    wrap_widths = [18, 25, 23, 9, 25]
    wrapped_rows = [
        ["\n".join(textwrap.wrap(str(value), width=width)) for value, width in zip(row, wrap_widths)]
        for row in rules.to_numpy()
    ]
    table = ax.table(
        cellText=wrapped_rows,
        colLabels=rules.columns,
        cellLoc="left",
        colLoc="left",
        colColours=[COLORS["navy"]] * len(rules.columns),
        bbox=[0.02, 0.02, 0.96, 0.84],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8.7)
    table.scale(1, 1.55)

    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor("#D9E2EC")
        if row == 0:
            cell.set_text_props(color="white", weight="bold")
            cell.set_height(0.07)
        else:
            cell.set_facecolor("#F8FAFC" if row % 2 == 0 else "white")
            cell.set_text_props(color=COLORS["red"] if col == 3 else COLORS["dark"])
            if col == 3:
                cell.set_text_props(weight="bold", color=COLORS["red"])

    save(fig, "07_operating_rules_roadmap.png")


def main() -> None:
    setup_style()
    chart_pathway_funnel()
    chart_stage_dropoff()
    chart_wait_time_bottleneck()
    chart_operational_status_mix()
    chart_access_segments()
    chart_scenario_impact()
    chart_operating_rules_roadmap()
    print(f"Wrote portfolio visuals to {OUT_DIR}")


if __name__ == "__main__":
    main()
