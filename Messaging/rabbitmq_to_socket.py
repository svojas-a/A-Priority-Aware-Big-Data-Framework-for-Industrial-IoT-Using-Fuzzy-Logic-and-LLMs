import pika
import socket
import time

# ---------- Socket setup ----------
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(("localhost", 9999))
sock.listen(1)

print("Waiting for Spark to connect...")
conn, addr = sock.accept()
print("Spark connected")

# ---------- RabbitMQ setup ----------
credentials = pika.PlainCredentials("user", "user123")
params = pika.ConnectionParameters("localhost", credentials=credentials)
connection = pika.BlockingConnection(params)
channel = connection.channel()

channel.queue_declare(queue="medium_severity_queue", durable=True)

consumed_count = 0

def callback(ch, method, properties, body):
    global consumed_count

    try:
        conn.sendall(body + b"\n")
    except BrokenPipeError:
        print("⚠ Consumer disconnected. Stopping bridge.")
        ch.stop_consuming()
        return

    consumed_count += 1
    if consumed_count % 50 == 0:
        print(f"Consumed so far: {consumed_count}")

    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(
    queue="medium_severity_queue",
    on_message_callback=callback,
    auto_ack=False
)

print("Consuming messages...")

try:
    channel.start_consuming()
except KeyboardInterrupt:
    pass

connection.close()
conn.close()

