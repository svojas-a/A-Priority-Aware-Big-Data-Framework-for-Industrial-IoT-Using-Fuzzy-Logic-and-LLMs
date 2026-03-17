import pandas as pd
import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral"

INPUT_FILE = "Data/Preprocessed/fault_dataset_100k.csv"
OUTPUT_FILE = "LLM/llm_results.json"

NORMAL_SAMPLES = 40
WARNING_SAMPLES = 30
CRITICAL_SAMPLES = 30


df = pd.read_csv(INPUT_FILE)

print("Dataset loaded:", len(df))

# Use fuzzy severity directly
normal_df = df[df["Fuzzy_Severity"] == "Normal"].sample(
    n=NORMAL_SAMPLES, random_state=42
)

warning_df = df[df["Fuzzy_Severity"] == "Warning"].sample(
    n=WARNING_SAMPLES, random_state=42
)

critical_df = df[df["Fuzzy_Severity"] == "Critical"].sample(
    n=CRITICAL_SAMPLES, random_state=42
)

df_sample = pd.concat([normal_df, warning_df, critical_df]).reset_index(drop=True)

print("Balanced dataset created:", len(df_sample))


results = []

for idx, row in df_sample.iterrows():

    event_summary = {
        "timestamp": row["Timestamp"],
        "vibration": row["Vibration (mm/s)"],
        "temperature": row["Temperature (°C)"],
        "pressure": row["Pressure (bar)"],
        "severity": row["Fuzzy_Severity"]
    }

    prompt = f"""
You are an Industrial IoT system analyst.

Analyze the following sensor event and provide:

1. Explanation
2. Risk Assessment
3. Recommended Actions

Event:
{json.dumps(event_summary, indent=2)}
"""

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload)
    output = response.json()["response"]

    results.append({
        "event_id": idx + 1,
        "severity": row["Fuzzy_Severity"],
        "llm_response": output
    })

    print(f"Processed event {idx+1}/100")


with open(OUTPUT_FILE, "w") as f:
    json.dump(results, f, indent=2)

print("✅ LLM inference complete")
print("Saved to:", OUTPUT_FILE)