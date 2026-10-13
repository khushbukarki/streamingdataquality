"""Data-quality rules for order events. Pure Python, so it is easy to unit test with pytest."""
from datetime import datetime

from events import PRODUCTS

REQUIRED_FIELDS = ["event_id", "customer_id", "product", "quantity", "amount_nzd", "event_time"]


def validate(event: dict) -> list[str]:
    """Return a list of rule violations. An empty list means the event is valid."""
    errors = []

    # Completeness
    for field in REQUIRED_FIELDS:
        if event.get(field) is None:
            errors.append(f"missing:{field}")

    # Validity
    if event.get("product") is not None and event["product"] not in PRODUCTS:
        errors.append("invalid:product")
    amount = event.get("amount_nzd")
    if isinstance(amount, (int, float)) and amount <= 0:
        errors.append("invalid:amount_nzd")
    qty = event.get("quantity")
    if isinstance(qty, int) and not 1 <= qty <= 100:
        errors.append("invalid:quantity")

    # Format
    if event.get("event_time") is not None:
        try:
            datetime.fromisoformat(event["event_time"])
        except (TypeError, ValueError):
            errors.append("invalid:event_time")

    return errors


def mask_email(email: str | None) -> str | None:
    """Mask PII: keep the first character and the domain, e.g. u***@example.com."""
    if not email or "@" not in email:
        return email
    name, domain = email.split("@", 1)
    return f"{name[0]}***@{domain}"
