"""
cleanup_old_scripts.py
----------------------
Run this once to remove old/redundant scripts that have been superseded.
Safe to delete — their outputs are preserved in outputs/analytics/.

Run: python scripts/cleanup_old_scripts.py
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

OLD_SCRIPTS = [
    "scripts/advanced_segmentation.py",
    "scripts/build_coordination_scorecard.py",
    "scripts/compute_counterfactuals.py",
    "scripts/create_business_friendly_exports.py",
    "scripts/data_quality_checks.py",
    "scripts/root_cause_analysis.py",
    "scripts/sensitivity_counterfactuals.py",
    "scripts/trend_analysis.py",
]

OLD_OUTPUT_DIRS = [
    "outputs/business_ready",
]

for path in OLD_SCRIPTS + OLD_OUTPUT_DIRS:
    full = ROOT / path
    if full.exists():
        if full.is_file():
            full.unlink()
            print(f"  removed {path}")
        elif full.is_dir():
            import shutil
            shutil.rmtree(full)
            print(f"  removed dir {path}")
    else:
        print(f"  already gone: {path}")

print("\nDone. Safe to delete this script too.")
