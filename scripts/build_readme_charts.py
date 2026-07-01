"""
Build the five README chart visuals from the analytics outputs.

Inputs:
- outputs/analytics/funnel_metrics.csv
- outputs/analytics/stage_dropoff.csv
- outputs/analytics/stage_delay_contribution.csv
- outputs/analytics/insurance_analysis.csv
- outputs/analytics/access_segment_summary.csv

Output:
- outputs/charts/01_pathway_funnel.png
- outputs/charts/02_stage_dropoff.png
- outputs/charts/03_wait_time_by_stage.png
- outputs/charts/04_payer_comparison.png
- outputs/charts/05_capacity_comparison.png
"""

from __future__ import annotations

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

import _bootstrap_path  # noqa: F401
from chd_analytics.paths import ANALYTICS, ROOT

OUT = ROOT / "outputs" / "charts"

NAVY = "#1f3a5f"
TEAL = "#1b8a8a"
ORANGE = "#e07a2c"
BG = "#ffffff"

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "axes.edgecolor": "#d9dee3",
        "axes.labelcolor": "#33404e",
        "text.color": "#1f2937",
        "xtick.color": "#33404e",
        "ytick.color": "#33404e",
        "figure.facecolor": BG,
        "axes.facecolor": BG,
        "savefig.facecolor": BG,
    }
)


def build_funnel_chart() -> None:
    funnel = pd.read_csv(ANALYTICS / "funnel_metrics.csv").iloc[0]
    stages = ["Symptom", "Primary care", "Referral", "Specialist visit", "Diagnosis"]
    counts = [
        funnel["symptom"],
        funnel["pcp"],
        funnel["referral"],
        funnel["specialist"],
        funnel["diagnosis"],
    ]

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(stages, counts, color=[NAVY, NAVY, TEAL, TEAL, ORANGE], width=0.6)
    for bar, val in zip(bars, counts):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            val + 300,
            f"{int(val):,}",
            ha="center",
            fontsize=11,
            fontweight="bold",
        )
    pct = counts[-1] / counts[0]
    ax.annotate(
        f"{pct:.1%} reach diagnosis",
        xy=(4, counts[-1] + 700),
        xytext=(2.1, 13200),
        fontsize=12,
        color=ORANGE,
        fontweight="bold",
        arrowprops=dict(arrowstyle="->", color=ORANGE, lw=1.5),
    )
    ax.set_title(
        "Patient Pathway Funnel: Symptom to Diagnosis",
        fontsize=14,
        fontweight="bold",
        pad=15,
        loc="left",
    )
    ax.set_ylabel("Patients")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_ylim(0, 17000)
    plt.tight_layout()
    plt.savefig(OUT / "01_pathway_funnel.png", dpi=160)
    plt.close()


def build_dropoff_chart() -> None:
    dropoff = pd.read_csv(ANALYTICS / "stage_dropoff.csv")
    fig, ax = plt.subplots(figsize=(9, 5))
    colors = [ORANGE if v == dropoff["drop_off_rate"].max() else TEAL for v in dropoff["drop_off_rate"]]
    bars = ax.barh(dropoff["stage"], dropoff["drop_off_rate"], color=colors, height=0.55)
    for bar, val in zip(bars, dropoff["drop_off_rate"]):
        ax.text(
            val + 0.008,
            bar.get_y() + bar.get_height() / 2,
            f"{float(val):.1%}",
            va="center",
            fontsize=11,
            fontweight="bold",
        )
    ax.set_title("Where Patients Leave the Pathway", fontsize=14, fontweight="bold", pad=15, loc="left")
    ax.set_xlabel("Drop-off rate")
    ax.xaxis.set_major_formatter(mticker.PercentFormatter(xmax=1))
    ax.spines[["top", "right"]].set_visible(False)
    ax.invert_yaxis()
    ax.set_xlim(0, 0.42)
    plt.tight_layout()
    plt.savefig(OUT / "02_stage_dropoff.png", dpi=160)
    plt.close()


def build_wait_time_chart() -> None:
    delay = pd.read_csv(ANALYTICS / "stage_delay_contribution.csv").iloc[0]
    stage_labels = [
        "Symptom -> PCP",
        "PCP -> Referral",
        "Referral -> Specialist",
        "Specialist -> Diagnosis",
    ]
    waits = [
        delay["symptom_to_pcp"],
        delay["pcp_to_referral"],
        delay["referral_to_specialist"],
        delay["specialist_to_diagnosis"],
    ]
    fig, ax = plt.subplots(figsize=(9, 5))
    colors = [ORANGE if v == max(waits) else NAVY for v in waits]
    bars = ax.bar(stage_labels, waits, color=colors, width=0.55)
    for bar, val in zip(bars, waits):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            val + 0.8,
            f"{float(val):.1f}d",
            ha="center",
            fontsize=11,
            fontweight="bold",
        )
    ax.set_title("Average Wait Time by Pathway Stage (days)", fontsize=14, fontweight="bold", pad=15, loc="left")
    ax.set_ylabel("Average days")
    ax.spines[["top", "right"]].set_visible(False)
    plt.xticks(rotation=10, ha="right")
    plt.tight_layout()
    plt.savefig(OUT / "03_wait_time_by_stage.png", dpi=160)
    plt.close()


def build_payer_chart() -> None:
    ins = pd.read_csv(ANALYTICS / "insurance_analysis.csv").sort_values("diagnosis_rate", ascending=False)
    fig, ax = plt.subplots(figsize=(9, 5))
    colors = [TEAL if p != "uninsured" else ORANGE for p in ins["insurance_type"]]
    bars = ax.bar(ins["insurance_type"].str.title(), ins["diagnosis_rate"], color=colors, width=0.55)
    for bar, val in zip(bars, ins["diagnosis_rate"]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            val + 0.006,
            f"{float(val):.1%}",
            ha="center",
            fontsize=11,
            fontweight="bold",
        )
    ax.set_title("Diagnosis Completion by Payer Type", fontsize=14, fontweight="bold", pad=15, loc="left")
    ax.set_ylabel("Diagnosis completion rate")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1))
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    plt.savefig(OUT / "04_payer_comparison.png", dpi=160)
    plt.close()


def build_capacity_chart() -> None:
    seg = pd.read_csv(ANALYTICS / "access_segment_summary.csv")
    cap = seg[seg["segment_type"] == "Provider capacity"].sort_values(
        "specialist_completion_rate", ascending=False
    )
    fig, ax = plt.subplots(figsize=(9, 5))
    labels = cap["segment"].str.replace("_", " ").str.title()
    colors = [TEAL, NAVY, ORANGE]
    bars = ax.bar(labels, cap["specialist_completion_rate"], color=colors, width=0.55)
    for bar, val in zip(bars, cap["specialist_completion_rate"]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            val + 0.006,
            f"{float(val):.1%}",
            ha="center",
            fontsize=11,
            fontweight="bold",
        )
    ax.set_title(
        "Specialist Completion by Provider Network Capacity",
        fontsize=14,
        fontweight="bold",
        pad=15,
        loc="left",
    )
    ax.set_ylabel("Specialist completion rate")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1))
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    plt.savefig(OUT / "05_capacity_comparison.png", dpi=160)
    plt.close()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    build_funnel_chart()
    build_dropoff_chart()
    build_wait_time_chart()
    build_payer_chart()
    build_capacity_chart()
    print(f"Wrote README charts to {OUT}")


if __name__ == "__main__":
    main()
