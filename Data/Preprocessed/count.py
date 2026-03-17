import pandas as pd

# Load dataset
df = pd.read_csv("industrial_fault_detection_with_fuzzy_severity.csv")

# Count values in Fuzzy_Severity column
counts = df["Fuzzy_Severity"].value_counts()

print("Fuzzy Severity Counts:")
print(counts)

# If you want individual numbers
normal = counts.get("Normal", 0)
warning = counts.get("Warning", 0)
critical = counts.get("Critical", 0)

print("\nDetailed Counts:")
print("Normal:", normal)
print("Warning:", warning)
print("Critical:", critical)