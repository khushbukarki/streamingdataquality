"""Send synthetic order events to the `orders` topic.

Usage:  python src/producer.py --rate 5 --count 500
"""
import argparse
import json
import time

from confluent_kafka import Producer

from events import make_event

BROKER = "localhost:19092"
TOPIC = "orders"


def on_delivery(err, msg):
    if err:
        print(f"Delivery failed: {err}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rate", type=float, default=5, help="events per second")
    parser.add_argument("--count", type=int, default=0, help="0 = run forever")
    args = parser.parse_args()

    producer = Producer({"bootstrap.servers": BROKER})
    sent = 0
    try:
        while args.count == 0 or sent < args.count:
            event = make_event()
            producer.produce(
                TOPIC,
                key=str(event.get("customer_id")),
                value=json.dumps(event),
                callback=on_delivery,
            )
            producer.poll(0)
            sent += 1
            if sent % 50 == 0:
                print(f"Sent {sent} events")
            time.sleep(1 / args.rate)
    except KeyboardInterrupt:
        pass
    finally:
        producer.flush()
        print(f"Done. Sent {sent} events to '{TOPIC}'.")


if __name__ == "__main__":
    main()
