"""
predict_dropout.py
------------------
Logistic regression model to predict which pediatric CHD patients
are at highest risk of dropping out before reaching a confirmed diagnosis.

Three barriers mapped to features:
  Awareness  → days_symptom_to_pcp_clean  (delay before seeking care)
  Financial  → insurance_type             (Medicaid / Uninsured flag)
  Access     → svi_index                  (neighborhood disadvantage)

Output:
  outputs/analytics/patient_dropout_risk.csv  — per-patient risk scores
  outputs/charts/06_dropout_risk_features.png — feature importance chart
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, roc_auc_score
import warnings
warnings.filterwarnings('ignore')

ROOT = Path(__file__).resolve().parents[1]
mart = pd.read_csv(ROOT / 'data/marts/cleaned/mart_delay_scored_cleaned.csv')

# ── Target: 1 = dropped out (no diagnosis) ──────────────────────────────
mart['dropped_out'] = mart['diagnosis_date'].isna().astype(int)

# ── CHD severity (clinical grouping) ────────────────────────────────────
COMPLEX  = ['Hypoplastic Left Heart Syndrome','Transposition of the Great Arteries',
            'Tricuspid Atresia','Double Outlet Right Ventricle']
MODERATE = ['Tetralogy of Fallot','Coarctation of the Aorta',
            'Pulmonary Stenosis','Aortic Stenosis']
mart['chd_severity'] = mart['chd_type'].apply(
    lambda x: 2 if x in COMPLEX else (1 if x in MODERATE else 0))

# ── Features ─────────────────────────────────────────────────────────────
ins_dummies = pd.get_dummies(mart['insurance_type'], prefix='ins')
features = pd.concat([
    mart[['svi_index', 'days_symptom_to_pcp_clean',
          'chd_severity', 'delay_severity_score_clean']],
    ins_dummies
], axis=1).fillna(0)

target = mart['dropped_out']

LABEL_MAP = {
    'svi_index':                  'Neighborhood Disadvantage (SVI)  [Access]',
    'days_symptom_to_pcp_clean':  'Days Before First Doctor Visit  [Awareness]',
    'chd_severity':               'CHD Severity (clinical)',
    'delay_severity_score_clean': 'Overall Delay Score',
    'ins_medicaid':               'Medicaid Insurance  [Financial]',
    'ins_uninsured':              'Uninsured  [Financial]',
    'ins_private':                'Private Insurance  [protective]',
    'ins_other':                  'Other Insurance',
}

# ── Train / evaluate ──────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    features, target, test_size=0.2, random_state=42, stratify=target)

scaler  = StandardScaler()
X_tr_sc = scaler.fit_transform(X_train)
X_te_sc = scaler.transform(X_test)

model = LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42)
model.fit(X_tr_sc, y_train)

y_pred = model.predict(X_te_sc)
y_prob = model.predict_proba(X_te_sc)[:, 1]
auc    = roc_auc_score(y_test, y_prob)
cv_auc = cross_val_score(model, scaler.transform(features), target,
                          cv=5, scoring='roc_auc').mean()

print(f"AUC (test):       {auc:.3f}")
print(f"AUC (5-fold CV):  {cv_auc:.3f}\n")
print(classification_report(y_test, y_pred,
      target_names=['Reached Diagnosis', 'Dropped Out']))

# ── Save risk scores ──────────────────────────────────────────────────────
mart['dropout_risk_score'] = model.predict_proba(scaler.transform(features))[:, 1]
out_path = ROOT / 'outputs/analytics/patient_dropout_risk.csv'
mart[['patient_id', 'chd_type', 'insurance_type', 'svi_index',
      'dropped_out', 'dropout_risk_score']].to_csv(out_path, index=False)
print(f"Risk scores saved → {out_path.relative_to(ROOT)}")

# ── Feature importance chart ──────────────────────────────────────────────
coef_df = pd.DataFrame({
    'feature': features.columns,
    'coef':    model.coef_[0]
}).assign(
    label = lambda d: d['feature'].map(LABEL_MAP).fillna(d['feature'])
).sort_values('coef')

NAVY  = "#1F3864"; TEAL = "#2E75B6"; RED   = "#C00000"
GREEN = "#375623"; AMBER= "#C55A11"; GRAY  = "#7F7F7F"

def bar_color(lbl):
    if 'Financial' in lbl: return RED
    if 'Access'    in lbl: return TEAL
    if 'Awareness' in lbl: return AMBER
    if 'protective' in lbl: return GREEN
    return NAVY

plt.rcParams.update({
    'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False,
    'figure.dpi':150,'axes.titlesize':13,'axes.titleweight':'bold',
    'axes.titlecolor':NAVY,'xtick.color':GRAY,'ytick.color':GRAY,
})
fig, ax = plt.subplots(figsize=(9.5, 5.5))
colors = [bar_color(l) for l in coef_df['label']]
bars   = ax.barh(coef_df['label'], coef_df['coef'], color=colors, height=0.55, alpha=0.88)
ax.axvline(0, color=GRAY, linewidth=1, alpha=0.5)
for bar, val in zip(bars, coef_df['coef']):
    txt  = f"+{val:.2f}" if val >= 0 else f"{val:.2f}"
    xpos = val + 0.012 if val >= 0 else val - 0.012
    ax.text(xpos, bar.get_y() + bar.get_height()/2, txt,
            va='center', ha='left' if val >= 0 else 'right', fontsize=8.5, color=GRAY)
ax.set_xlabel("Model Coefficient  (positive = raises dropout risk, negative = lowers it)",
              labelpad=8, color=GRAY, fontsize=9)
ax.set_title("Which Barriers Most Predict a Child NOT Getting Diagnosed?\n"
             "Logistic Regression — Feature Importance", pad=12)
patches = [
    mpatches.Patch(color=RED,   label='Financial barrier'),
    mpatches.Patch(color=TEAL,  label='Access barrier (neighborhood)'),
    mpatches.Patch(color=AMBER, label='Awareness barrier'),
    mpatches.Patch(color=NAVY,  label='Clinical / composite'),
    mpatches.Patch(color=GREEN, label='Protective factor'),
]
ax.legend(handles=patches, fontsize=8.5, framealpha=0.85, loc='lower right')
fig.text(0.5, 0.01,
    f"Model AUC: {auc:.2f}  |  5-fold CV AUC: {cv_auc:.2f}  |  "
    "Higher AUC = better at identifying which children are at risk.",
    ha='center', fontsize=8, color=GRAY, style='italic')
plt.tight_layout(rect=[0, 0.04, 1, 1])
chart_path = ROOT / 'outputs/charts/06_dropout_risk_features.png'
fig.savefig(chart_path, bbox_inches='tight', facecolor='white')
plt.close()
print(f"Chart saved → {chart_path.relative_to(ROOT)}")
