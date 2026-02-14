from kafka import KafkaConsumer
import time
import json

TOPIC = "high_severity"
BOOTSTRAP_SERVERS = "localhost:9092"

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=BOOTSTRAP_SERVERS,
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    consumer_timeout_ms=3000,
    value_deserializer=lambda x: json.loads(x.decode("utf-8"))
)

print("✅ Kafka consumer started")
print("⏱ Measuring end-to-end latency...\n")

latencies = []

for message in consumer:
    data = message.value

    if "ingest_time" not in data:
        continue

    consume_time_ms = int(time.time() * 1000)
    produce_time_ms = data["ingest_time"]

    latency_ms = consume_time_ms - produce_time_ms
    latencies.append(latency_ms)

consumer.close()

count = len(latencies)

if count > 0:
    print("===================================")
    print(f"📦 Total HIGH events = {count}")
    print(f"⏱ Average latency = {sum(latencies)/count:.2f} ms")
    print(f"⚡ Min latency = {min(latencies):.2f} ms")
    print(f"🔥 Max latency = {max(latencies):.2f} ms")
    print("===================================")
else:
    print("❌ No ingest_time found in messages")

