"""Read `orders`, run quality checks, mask PII, and route records.

Valid events  -> `orders.clean`  (email masked)
Invalid events -> `orders.dlq`   (original event + list of errors)

Usage:  python src/consumer.py
"""
import json
from datetime import datetime, timezone

from confluent_kafka import Consumer, Producer

from validation import mask_email, validate

BROKER = "localhost:19092"


def main():
    consumer = Consumer({
        "bootstrap.servers": BROKER,
        "group.id": "dq-validator",
        "auto.offset.reset": "earliest",
    })
    producer = Producer({"bootstrap.servers": BROKER})
    consumer.subscribe(["orders"])

    stats = {"valid": 0, "dlq": 0}
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue

            try:
                event = json.loads(msg.value())
                errors = validate(event)
            except json.JSONDecodeError:
                event, errors = {"raw": msg.value().decode(errors="replace")}, ["invalid:json"]

            if errors:
                dlq_record = {
                    "event": event,
                    "errors": errors,
                    "failed_at": datetime.now(timezone.utc).isoformat(),
                }
                producer.produce("orders.dlq", value=json.dumps(dlq_record))
                stats["dlq"] += 1
            else:
                event["email"] = mask_email(event.get("email"))
                producer.produce("orders.clean", key=msg.key(), value=json.dumps(event))
                stats["valid"] += 1

            producer.poll(0)
            total = stats["valid"] + stats["dlq"]
            if total % 50 == 0:
                print(f"Processed {total}: {stats['valid']} clean, {stats['dlq']} to DLQ")
    except KeyboardInterrupt:
        pass
    finally:
        producer.flush()
        consumer.close()


if __name__ == "__main__":
    main()
