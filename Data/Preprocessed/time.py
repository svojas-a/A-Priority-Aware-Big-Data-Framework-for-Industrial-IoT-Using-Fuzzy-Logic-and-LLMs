import pandas as pd

# Load expanded dataset
df = pd.read_csv("fault_dataset_100k.csv")

# Create new sequential timestamps
df["timestamp"] = pd.date_range(
    start="2025-01-01 00:00:00",
    periods=len(df),
    freq="100ms"   # 100 millisecond interval
)

# Save dataset
df.to_csv("fault_dataset_100k_stream.csv", index=False)

print("New timestamps generated while keeping severity sequence intact.")