from kafka import KafkaProducer
import csv
import json
import time

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

TOPIC = "base_data"
CSV_FILE = "/home/pes2ug23cs606/baseline_dataset.csv"

with open(CSV_FILE, "r") as file:
    reader = csv.DictReader(file)

    for row in reader:
        event = {
            "timestamp": row["Timestamp"],
            "vibration": float(row["Vibration (mm/s)"]),
            "temperature": float(row["Temperature (°C)"]),
            "pressure": float(row["Pressure (bar)"]),
            "rms_vibration": float(row["RMS Vibration"]),
            "mean_temperature": float(row["Mean Temp"]),
            "fault_label": int(row["Fault Label"]),
            "event_timestamp": time.time()
        }

        producer.send(TOPIC, event)
        time.sleep(0.05)   # event rate control

producer.flush()
print("✅ Baseline producer finished sending all events")
