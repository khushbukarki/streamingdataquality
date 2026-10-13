"""Synthetic order events, including deliberately bad and late records."""
import random
import uuid
from datetime import datetime, timedelta, timezone

PRODUCTS = ["coffee", "pie", "sandwich", "juice", "muffin"]


def make_event(bad_rate: float = 0.1, late_rate: float = 0.05) -> dict:
    """Build one order event. A share of events are invalid or arrive late on purpose,
    so the quality checks and DLQ have something real to catch."""
    now = datetime.now(timezone.utc)
    event = {
        "event_id": str(uuid.uuid4()),
        "customer_id": f"C{random.randint(1, 500):04d}",
        "email": f"user{random.randint(1, 500)}@example.com",  # PII: to be masked downstream
        "product": random.choice(PRODUCTS),
        "quantity": random.randint(1, 5),
        "amount_nzd": round(random.uniform(3, 40), 2),
        "event_time": now.isoformat(),
    }

    if random.random() < late_rate:  # late-arriving event (for watermark testing)
        event["event_time"] = (now - timedelta(minutes=random.randint(2, 30))).isoformat()

    if random.random() < bad_rate:  # inject one data-quality problem
        problem = random.choice(["null_customer", "negative_amount", "bad_product", "missing_time"])
        if problem == "null_customer":
            event["customer_id"] = None
        elif problem == "negative_amount":
            event["amount_nzd"] = -abs(event["amount_nzd"])
        elif problem == "bad_product":
            event["product"] = "???"
        else:
            del event["event_time"]
    return event
