"""
DisasterComm – Unified Severity-Aware Routing Pipeline
Correct version with ingest_time for latency measurement
"""

import csv
import json
import time
from kafka import KafkaProducer
import pika


# ==============================
# INPUT
# ==============================
CSV_FILE = "iot_data.csv"

# ==============================
# KAFKA (HIGH SEVERITY)
# ==============================
KAFKA_BROKER = "localhost:9092"
KAFKA_TOPIC = "high_severity"

# ==============================
# RABBITMQ (MEDIUM SEVERITY)
# ==============================
RABBIT_HOST = "localhost"
RABBIT_USER = "user"
RABBIT_PASS = "user123"
RABBIT_QUEUE = "medium_severity_queue"

# ==============================
# HADOOP INPUT (LOW SEVERITY)
# ==============================
LOW_SEVERITY_FILE = "low_severity_input.txt"
open(LOW_SEVERITY_FILE, "w").close()

# ==============================
# KAFKA PRODUCER
# ==============================
kafka_producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

# ==============================
# RABBITMQ PRODUCER
# ==============================
credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)
params = pika.ConnectionParameters(RABBIT_HOST, credentials=credentials)
rabbit_connection = pika.BlockingConnection(params)
rabbit_channel = rabbit_connection.channel()
rabbit_channel.queue_declare(queue=RABBIT_QUEUE, durable=True)

# ==============================
# COUNTERS
# ==============================
high = 0
medium = 0
low = 0

# ==============================
# MAIN ROUTING LOGIC
# ==============================
with open(CSV_FILE, "r") as f:
    reader = csv.DictReader(f)

    for row in reader:
        severity = row["Fuzzy_Severity"].strip().lower()

        # 🔥 PRODUCER-SIDE INGEST TIME (START OF LATENCY)
        ingest_time = int(time.time() * 1000)

        event = {
            "ingest_time": ingest_time,                 # ✅ used for latency
            "timestamp": row["Timestamp"],              # dataset time (historical)
            "vibration": float(row["Vibration (mm/s)"]),
            "temperature": float(row["Temperature (°C)"]),
            "pressure": float(row["Pressure (bar)"]),
            "rms_vibration": float(row["RMS Vibration"]),
            "mean_temp": float(row["Mean Temp"]),
            "fault_label": row["Fault Label"],
            "fuzzy_severity": row["Fuzzy_Severity"],
            "processed_by": "router"
        }

        # ==============================
        # HIGH SEVERITY → KAFKA
        # ==============================
        if severity == "critical":
            kafka_producer.send(KAFKA_TOPIC, event)
            high += 1

            # small delay to simulate streaming (optional but OK)
            #time.sleep(0.1)

        # ==============================
        # MEDIUM SEVERITY → RABBITMQ
        # ==============================
        elif severity == "warning":
            rabbit_channel.basic_publish(
                exchange="",
                routing_key=RABBIT_QUEUE,
                body=json.dumps(event),
                properties=pika.BasicProperties(delivery_mode=2)
            )
            medium += 1
            #time.sleep(0.1)

        # ==============================
        # LOW SEVERITY → FILE (HDFS INPUT)
        # ==============================
        else:
            with open(LOW_SEVERITY_FILE, "a") as out:
                out.write(json.dumps(event) + "\n")
            low += 1

# ==============================
# CLEANUP
# ==============================
kafka_producer.flush()
rabbit_connection.close()

print("Routing complete")
print("HIGH:", high, "MEDIUM:", medium, "LOW:", low)

