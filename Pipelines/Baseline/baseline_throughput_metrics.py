import time
import json
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    "base_data",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda m: json.loads(m.decode("utf-8"))
)

WINDOW = 60
start_time = time.time()
count = 0

print("⚡ Measuring baseline throughput...")

for msg in consumer:
    count += 1
    if time.time() - start_time >= WINDOW:
        break

print("===== BASELINE THROUGHPUT RESULTS =====")
print(f"Events processed : {count}")
print(f"Throughput       : {count/WINDOW:.2f} events/sec")
