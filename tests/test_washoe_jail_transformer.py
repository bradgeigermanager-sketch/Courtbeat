import pytest

from courtbeat.transformers.jail_records import JailRecordTransformer


def test_transform_basic_record():
    raw = {
        "source": "washoe_jail",
        "entity": "arrest_event",
        "name": "JOHN DOE",
        "dob": "1990-01-01",
        "booking_number": "12345",
        "booking_date": "2024-01-10",
        "facility": "Washoe County Jail",
        "status": "In Custody",
        "charges": [
            {
                "statute": "NRS 484C.110",
                "description": "DUI",
                "severity": "Misdemeanor",
            }
        ],
        "meta": {"raw": {"foo": "bar"}},
    }

    t = JailRecordTransformer()
    out = t.transform(raw)

    # Core identity fields
    assert out["person"]["name"] == "JOHN DOE"
    assert out["person"]["dob"] == "1990-01-01"

    # Booking metadata
    assert out["booking"]["number"] == "12345"
    assert out["booking"]["date"] == "2024-01-10"
    assert out["booking"]["facility"] == "Washoe County Jail"
    assert out["booking"]["status"] == "In Custody"

    # Charges normalized
    assert len(out["charges"]) == 1
    ch = out["charges"][0]
    assert ch["statute"] == "NRS 484C.110"
    assert ch["description"] == "DUI"
    assert ch["severity"] == "Misdemeanor"

    # Source + entity preserved
    assert out["source"] == "washoe_jail"
    assert out["entity"] == "arrest_event"


def test_transform_handles_missing_fields():
    raw = {
        "source": "washoe_jail",
        "entity": "arrest_event",
        "name": "JANE DOE",
        "booking_number": "99999",
        "charges": [],
        "meta": {},
    }

    t = JailRecordTransformer()
    out = t.transform(raw)

    # Missing fields should not break the transformer
    assert out["person"]["name"] == "JANE DOE"
    assert out["booking"]["number"] == "99999"
    assert out["charges"] == []


def test_transform_multiple_charges():
    raw = {
        "source": "washoe_jail",
        "entity": "arrest_event",
        "name": "JOHN SMITH",
        "booking_number": "77777",
        "charges": [
            {
                "statute": "NRS 200.010",
                "description": "Murder",
                "severity": "Felony A",
            },
            {
                "statute": "NRS 205.060",
                "description": "Burglary",
                "severity": "Felony B",
            },
        ],
        "meta": {},
    }

    t = JailRecordTransformer()
    out = t.transform(raw)

    assert len(out["charges"]) == 2
    assert out["charges"][0]["description"] == "Murder"
    assert out["charges"][1]["description"] == "Burglary"
