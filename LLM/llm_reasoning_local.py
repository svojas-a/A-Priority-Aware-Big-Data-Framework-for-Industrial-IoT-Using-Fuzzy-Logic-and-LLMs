import pandas as pd
import requests
import json

# Ollama settings
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral"

# Load dataset (from project root)
df = pd.read_csv("iot_events.csv")

results = []

for _, row in df.iterrows():

    # Call LLM only for Warning / Critical
    if row["severity"] not in ["Warning", "Critical"]:
        continue

    event_summary = {
        "severity": row["severity"],
        "sensor_type": row["sensor_type"],
        "value": row["value"],
        "threshold": row["threshold"],
        "location": row["location"],
        "pipeline": row["pipeline"]
    }

    prompt = f"""
You are an IoT decision-support assistant.

Analyze the following event and provide:
1. Explanation
2. Risk assessment
3. Recommended actions

Event:
{json.dumps(event_summary, indent=2)}
"""

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload)
    response.raise_for_status()

    output = response.json()["response"]

    results.append({
        "event_id": int(row.get("event_id", len(results) + 1)),
        "severity": row["severity"],
        "llm_response": output
    })

# Save output in project root
with open("llm_results.json", "w") as f:
    json.dump(results, f, indent=2)

print("✅ Local LLM processing complete. Output saved to llm_results.json")