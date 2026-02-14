from kafka import KafkaConsumer
import time
import json

TOPIC = "high_severity"
BOOTSTRAP_SERVERS = "localhost:9092"

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=BOOTSTRAP_SERVERS,
    auto_offset_reset="earliest",
    enable_auto_commit=True,   # 🔥 IMPORTANT
    consumer_timeout_ms=3000,  # stop when no more data
    value_deserializer=lambda x: json.loads(x.decode("utf-8"))
)

print("✅ Kafka consumer started")
print("⏱ Measuring throughput (unique events)...\n")

start_time = time.time()
count = 0

for message in consumer:
    count += 1

end_time = time.time()
consumer.close()

time_taken = end_time - start_time

throughput = count / (time_taken / 60)

print("===================================")
print(f"📦 Total HIGH events consumed = {count}")
print(f"⏱ Time taken = {time_taken:.2f} seconds")
print(f"🔥 HIGH PIPELINE THROUGHPUT = {int(throughput)} events/min")
print("===================================")

