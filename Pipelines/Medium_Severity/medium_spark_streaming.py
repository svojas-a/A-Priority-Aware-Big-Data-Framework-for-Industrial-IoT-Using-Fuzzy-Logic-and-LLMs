from pyspark import SparkContext
from pyspark.streaming import StreamingContext
import socket
import json
import time

# ----------------------------
# Spark setup
# ----------------------------
sc = SparkContext("local[2]", "MediumSeverityPipeline")
ssc = StreamingContext(sc, 2)

# ----------------------------
# Input from RabbitMQ bridge
# ----------------------------
lines = ssc.socketTextStream("localhost", 9999)

# ----------------------------
# Output to consumer metrics
# ----------------------------
consumer_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
consumer_sock.connect(("localhost", 10000))

processed = 0

def process(rdd):
    global processed

    if not rdd.isEmpty():
        records = rdd.collect()
        batch_count = len(records)
        processed += batch_count

        for record in records:
            event = json.loads(record)

            # ✅ Processing completion time (ms)
            event["processed_time"] = int(time.time() * 1000)

            consumer_sock.sendall(
                (json.dumps(event) + "\n").encode()
            )

        print(f"Batch processed = {batch_count}, Total processed so far = {processed}")

lines.foreachRDD(process)

ssc.start()
ssc.awaitTermination()

