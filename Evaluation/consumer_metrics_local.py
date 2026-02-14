import socket
import json
import time
from collections import deque

HOST = "localhost"
PORT = 10000

WINDOW = 60          # throughput window (paper definition)
IDLE_TIMEOUT = 5     # seconds with no events → assume stream ended

latencies = []
event_times = deque()
total = 0
last_event_time = time.time()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))
sock.listen(1)

print("📊 Consumer Metrics Started")
conn, addr = sock.accept()
print("Connected from", addr)

conn.settimeout(1.0)   # non-blocking receive
buffer = ""

while True:
    try:
        data = conn.recv(4096).decode()
        if data:
            buffer += data
            last_event_time = time.time()

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)

                event = json.loads(line)

                # ✅ CORRECT latency (Spark completion − ingest)
                latency = (event["processed_time"] - event["ingest_time"]) / 1000.0

                latencies.append(latency)
                event_times.append(time.time())
                total += 1

                # maintain sliding window
                while event_times and event_times[0] < time.time() - WINDOW:
                    event_times.popleft()

    except socket.timeout:
        pass

    # ----------------------------
    # IDLE-BASED FINAL FLUSH
    # ----------------------------
    if time.time() - last_event_time > IDLE_TIMEOUT and total > 0:
        avg_latency = sum(latencies) / len(latencies)
        throughput = len(event_times) / WINDOW

        print("===================================")
        print("📌 FINAL METRICS (IDLE DETECTED)")
        print(f"📦 Total events received = {total}")
        print(f"⏱ Avg latency = {avg_latency:.3f} sec")
        print(f"⚡ Throughput = {throughput:.2f} events/sec")
        print("===================================")
        break

