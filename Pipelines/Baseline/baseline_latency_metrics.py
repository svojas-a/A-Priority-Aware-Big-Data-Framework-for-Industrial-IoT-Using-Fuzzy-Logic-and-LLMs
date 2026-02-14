import time
import json
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    "base_data",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda m: json.loads(m.decode("utf-8"))
)

latencies = []

print("⏱ Measuring baseline latency...")

for msg in consumer:
    latency = time.time() - msg.value["event_timestamp"]
    latencies.append(latency)

    if len(latencies) >= 300:
        break

print("===== BASELINE LATENCY RESULTS =====")
print(f"Average latency : {sum(latencies)/len(latencies):.4f} sec")
print(f"Minimum latency : {min(latencies):.4f} sec")
print(f"Maximum latency : {max(latencies):.4f} sec")
