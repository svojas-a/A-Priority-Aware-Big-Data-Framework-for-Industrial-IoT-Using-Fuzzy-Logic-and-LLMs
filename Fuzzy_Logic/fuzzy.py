import pandas as pd
import numpy as np
from sklearn.metrics import confusion_matrix, classification_report

# -----------------------------
# 1) Load dataset
# -----------------------------
INPUT_CSV = "industrial_fault_detection_training_10000.csv"
OUTPUT_CSV = "industrial_fault_detection_with_fuzzy_severity_training_10000.csv"

df = pd.read_csv(INPUT_CSV)

# Normalize column names (in case of slight variations)
# Expected columns from your dataset:
# "Vibration (mm/s)", "Temperature (°C)", "Pressure (bar)", "Fault Label"
vib_col = "Vibration (mm/s)"
temp_col = "Temperature (°C)"
pres_col = "Pressure (bar)"
label_col = "Fault Label"

for c in [vib_col, temp_col, pres_col, label_col]:
    if c not in df.columns:
        raise ValueError(f"Missing expected column: {c}. Found columns: {list(df.columns)}")

# -----------------------------
# 2) Industry-aligned thresholds -> fuzzy levels
# -----------------------------
# Vibration (overall RMS velocity in mm/s) typical ISO 10816/20816-style boundaries (simplified into 3 bins)
# Low:    < 1.12
# Medium: 1.12 to 2.8
# High:   > 2.8
def vib_level(v):
    if v < 1.12:
        return "Low"
    elif v <= 2.8:
        return "Medium"
    else:
        return "High"

# Temperature (bearing/motor monitoring typical alarm practice; simplified into 3 bins)
# Low:    < 80
# Medium: 80 to 90
# High:   > 90  (often alarm/trip region begins here; trip commonly around ~100)
def temp_level(t):
    if t < 80:
        return "Low"
    elif t <= 90:
        return "Medium"
    else:
        return "High"

# Pressure (factory pneumatics / compressed-air style ranges, simplified into 3 bins)
# Low:    < 6
# Normal: 6 to 8
# High:   > 8
def pres_level(p):
    if p < 6:
        return "Low"
    elif p <= 8:
        return "Normal"
    else:
        return "High"

df["Vib_Level"] = df[vib_col].apply(vib_level)
df["Temp_Level"] = df[temp_col].apply(temp_level)
df["Pres_Level"] = df[pres_col].apply(pres_level)

# -----------------------------
# 3) Fuzzy rules (EXACT 27 rules from your images)
# -----------------------------
# Format: (VibrationLevel, TemperatureLevel, PressureLevel) -> Severity
# Pressure levels in your rules: Low, Normal, High
RULES = {
    # Pressure = Low (rules 1-9)
    ("Low",    "Low",    "Low"):    "Normal",   # 1
    ("Low",    "Medium", "Low"):    "Warning",  # 2
    ("Low",    "High",   "Low"):    "Warning",  # 3
    ("Medium", "Low",    "Low"):    "Warning",  # 4
    ("Medium", "Medium", "Low"):    "Warning",  # 5
    ("Medium", "High",   "Low"):    "Critical", # 6
    ("High",   "Low",    "Low"):    "Warning",  # 7
    ("High",   "Medium", "Low"):    "Critical", # 8
    ("High",   "High",   "Low"):    "Critical", # 9

    # Pressure = Normal (rules 10-18)  (matrix matches your images)
    ("Low",    "Low",    "Normal"): "Normal",   # 10
    ("Low",    "Medium", "Normal"): "Warning",  # 11
    ("Low",    "High",   "Normal"): "Warning",  # 12
    ("Medium", "Low",    "Normal"): "Warning",  # 13
    ("Medium", "Medium", "Normal"): "Warning",  # 14
    ("Medium", "High",   "Normal"): "Critical", # 15
    ("High",   "Low",    "Normal"): "Warning",  # 16
    ("High",   "Medium", "Normal"): "Critical", # 17
    ("High",   "High",   "Normal"): "Critical", # 18

    # Pressure = High (rules 19-27) (from your Case 3 table + full list)
    ("Low",    "Low",    "High"):   "Warning",  # 19
    ("Low",    "Medium", "High"):   "Warning",  # 20
    ("Low",    "High",   "High"):   "Critical", # 21
    ("Medium", "Low",    "High"):   "Warning",  # 22
    ("Medium", "Medium", "High"):   "Critical", # 23
    ("Medium", "High",   "High"):   "Critical", # 24
    ("High",   "Low",    "High"):   "Critical", # 25
    ("High",   "Medium", "High"):   "Critical", # 26
    ("High",   "High",   "High"):   "Critical", # 27
}

def apply_rules(vl, tl, pl):
    key = (vl, tl, pl)
    if key not in RULES:
        # Should never happen if levels are only Low/Medium/High (and Pressure Low/Normal/High)
        return "Warning"
    return RULES[key]

df["Fuzzy_Severity"] = df.apply(lambda r: apply_rules(r["Vib_Level"], r["Temp_Level"], r["Pres_Level"]), axis=1)

# -----------------------------
# 4) Results + statistics
# -----------------------------
# Map dataset fault label to severity class (as you requested)
label_to_severity = {0: "Normal", 1: "Warning", 2: "Critical"}
df["Label_Severity"] = df[label_col].map(label_to_severity)

# Basic distributions
severity_counts = df["Fuzzy_Severity"].value_counts().sort_index()
print("\n=== Fuzzy Severity Distribution ===")
print(severity_counts)

# Crosstab (how fuzzy results align with original labels)
print("\n=== Crosstab: Fault Label vs Fuzzy Severity ===")
print(pd.crosstab(df[label_col], df["Fuzzy_Severity"], rownames=["Fault Label"], colnames=["Fuzzy Severity"]))

# Confusion matrix + classification report (using severity classes)
# Ensure consistent ordering
order = ["Normal", "Warning", "Critical"]
y_true = df["Label_Severity"].astype(pd.CategoricalDtype(categories=order, ordered=True))
y_pred = df["Fuzzy_Severity"].astype(pd.CategoricalDtype(categories=order, ordered=True))

cm = confusion_matrix(y_true, y_pred, labels=order)
cm_df = pd.DataFrame(cm, index=[f"True_{o}" for o in order], columns=[f"Pred_{o}" for o in order])

print("\n=== Confusion Matrix (Label Severity vs Fuzzy Severity) ===")
print(cm_df)

print("\n=== Classification Report ===")
print(classification_report(y_true, y_pred, labels=order, target_names=order, zero_division=0))

# Save output with fuzzy severity
df.to_csv(OUTPUT_CSV, index=False)
print(f"\nSaved: {OUTPUT_CSV}")

# Optional: show a few example rows
print("\n=== Sample Output Rows ===")
print(df[[vib_col, temp_col, pres_col, "Vib_Level", "Temp_Level", "Pres_Level", "Fuzzy_Severity", label_col, "Label_Severity"]].head(10))
