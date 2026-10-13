import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from events import make_event  # noqa: E402
from validation import mask_email, validate  # noqa: E402


def good_event():
    return {
        "event_id": "e1",
        "customer_id": "C0001",
        "email": "anna@example.com",
        "product": "coffee",
        "quantity": 2,
        "amount_nzd": 9.5,
        "event_time": "2026-10-13T08:00:00+00:00",
    }


def test_valid_event_passes():
    assert validate(good_event()) == []


def test_missing_customer_is_caught():
    e = good_event()
    e["customer_id"] = None
    assert "missing:customer_id" in validate(e)


def test_negative_amount_is_caught():
    e = good_event()
    e["amount_nzd"] = -4
    assert "invalid:amount_nzd" in validate(e)


def test_unknown_product_is_caught():
    e = good_event()
    e["product"] = "???"
    assert "invalid:product" in validate(e)


def test_missing_event_time_is_caught():
    e = good_event()
    del e["event_time"]
    assert "missing:event_time" in validate(e)


def test_bad_timestamp_format_is_caught():
    e = good_event()
    e["event_time"] = "yesterday"
    assert "invalid:event_time" in validate(e)


def test_email_is_masked():
    assert mask_email("anna@example.com") == "a***@example.com"


def test_generator_produces_bad_records():
    events = [make_event(bad_rate=1.0, late_rate=0) for _ in range(50)]
    assert all(validate(e) for e in events)
