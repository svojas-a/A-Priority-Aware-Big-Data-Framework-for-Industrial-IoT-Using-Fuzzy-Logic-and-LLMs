import pandas as pd

# Load your balanced dataset
df = pd.read_csv("balanced_fault_dataset.csv")

target_rows = 100000

# Calculate how many times to repeat the dataset
repeat_factor = target_rows // len(df) + 1

# Duplicate dataset
expanded_df = pd.concat([df] * repeat_factor, ignore_index=True)

# Trim to exactly 100000 rows
expanded_df = expanded_df.sample(n=target_rows, random_state=42).reset_index(drop=True)

# Print statistics
print("Final Class Distribution:")
print(expanded_df["Fuzzy_Severity"].value_counts())

print("\nTotal Rows:", len(expanded_df))

# Save dataset
expanded_df.to_csv("fault_dataset_100k.csv", index=False)

print("\nDataset saved as fault_dataset_100k.csv")