import json
import time

INPUT_FILE = "low_severity_input.txt"
BATCH_WINDOW = 30  # seconds (you can say "batch interval")

print("📊 LOW PIPELINE METRICS (BATCH WINDOW MODE)")
print(f"⏳ Batch window = {BATCH_WINDOW} seconds")

# -------------------------
# Batch accumulation phase
# -------------------------
batch = []
batch_start = time.time()

with open(INPUT_FILE, "r") as f:
    for line in f:
        event = json.loads(line)
        batch.append(event)

# Simulate waiting for batch window to close
remaining = BATCH_WINDOW - (time.time() - batch_start)
if remaining > 0:
    time.sleep(remaining)

# -------------------------
# Batch processing phase
# -------------------------
process_start = time.time()

for event in batch:
    _ = event["timestamp"]
    _ = event["vibration"]

# Simulate disk write (HDFS-like)
with open("low_pipeline_output.tmp", "w") as f:
    for _ in batch:
        f.write("ok\n")

process_end = time.time()

# -------------------------
# Metrics
# -------------------------
total_events = len(batch)
batch_latency = process_end - batch_start
throughput = total_events / batch_latency

print("===================================")
print(f"📦 Total events processed = {total_events}")
print(f"⏱ Batch latency = {batch_latency:.2f} sec")
print(f"⚡ Throughput = {throughput:.2f} events/sec")
print("===================================")

