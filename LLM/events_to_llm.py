import json

input_file = "val1.jsonl"
output_file = "val.jsonl"

INSTRUCTION = (
    "You are an expert system analyst. "
    "Analyze the sensor data and explain the system condition and severity."
)

def map_fault_label(label):
    # handles 0/1 or string labels
    if isinstance(label, str):
        return label.lower()
    return "normal" if int(label) == 0 else "fault"

def map_fuzzy_severity(sev):
    # Case 1: categorical fuzzy output
    if isinstance(sev, str):
        sev = sev.lower()
        if sev in ["low", "normal"]:
            return "low-severity"
        elif sev in ["warning", "medium", "moderate"]:
            return "moderate-severity"
        elif sev in ["high", "critical", "severe"]:
            return "high-severity"
        else:
            return "unknown-severity"

    # Case 2: numeric fuzzy output
    try:
        sev = float(sev)
        if sev < 0.3:
            return "low-severity"
        elif sev < 0.6:
            return "moderate-severity"
        else:
            return "high-severity"
    except:
        return "unknown-severity"

with open(input_file, "r", encoding="utf-8") as fin, \
     open(output_file, "w", encoding="utf-8") as fout:

    for line in fin:
        event = json.loads(line)

        fault_text = map_fault_label(event["fault_label"])
        severity_text = map_fuzzy_severity(event["fuzzy_severity"])

        llm_sample = {
            "instruction": INSTRUCTION,
            "input": (
                f"Timestamp={event['timestamp']}, "
                f"Vibration={event['vibration']} mm/s, "
                f"Temperature={event['temperature']} °C, "
                f"Pressure={event['pressure']} bar"
            ),
            "output": (
                f"The system is operating in a {severity_text} "
                f"{fault_text} condition based on the sensor readings."
            )
        }

        fout.write(json.dumps(llm_sample) + "\n")

print("✅ LLM training data generated successfully (mixed fuzzy types handled).")