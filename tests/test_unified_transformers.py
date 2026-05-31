import pytest
from datetime import datetime

from courtbeat.transformers.news_media import NewsMediaTransformer
from courtbeat.transformers.court_records import CourtRecordTransformer
from courtbeat.transformers.jail_records import JailRecordTransformer
from courtbeat.transformers.sheriff_logs import SheriffLogTransformer


# ---------------------------------------------------------
# News Media Transformer
# ---------------------------------------------------------

def test_news_media_transformer_basic():
    raw = type("Obj", (), {})()
    raw.source = "news_media"
    raw.entity = "court_event"
    raw.article_id = "A123"
    raw.article_url = "https://news.example.com/a123"
    raw.article_title = "Arrest in Reno"
    raw.article_date = datetime(2024, 1, 10)
    raw.person = type("P", (), dict(
        full_name="JOHN DOE",
        first_name="JOHN",
        middle_name=None,
        last_name="DOE",
    ))()
    raw.event = type("E", (), dict(
        type="Arraignment",
        court_level="District",
        charges_raw="DUI",
        disposition_raw="Pending",
        disposition_normalized="pending",
        hearing_date=datetime(2024, 1, 15),
    ))()
    raw.meta = {"foo": "bar"}

    t = NewsMediaTransformer()
    out = t.transform(raw)

    assert out["article"]["id"] == "A123"
    assert out["person"]["full_name"] == "JOHN DOE"
    assert out["event"]["type"] == "Arraignment"
    assert out["event"]["disposition_normalized"] == "pending"


# ---------------------------------------------------------
# Court Records Transformer
# ---------------------------------------------------------

def test_court_record_transformer_basic():
    raw = {
        "source": "washoe_district",
        "case_number": "CR24-00123",
        "case_type": "Criminal",
        "status": "Open",
        "filed_date": "01/02/2024",
        "person": {"defendant": "JOHN DOE"},
        "charges": [{"description": "DUI"}],
        "events": [{"type": "Arraignment"}],
        "meta": {"detail_url": "https://example.com"},
    }

    t = CourtRecordTransformer()
    out = t.transform(raw)

    assert out["case"]["number"] == "CR24-00123"
    assert out["person"]["defendant"] == "JOHN DOE"
    assert out["charges"][0]["description"] == "DUI"
    assert out["events"][0]["type"] == "Arraignment"


# ---------------------------------------------------------
# Jail Records Transformer
# ---------------------------------------------------------

def test_jail_record_transformer_basic():
    raw = {
        "source": "washoe_jail",
        "entity": "arrest_event",
        "name": "JOHN DOE",
        "booking_number": "12345",
        "dob": "1990-01-01",
        "booking_date": "2024-01-10",
        "facility": "Washoe Jail",
        "status": "In Custody",
        "charges": [{"description": "DUI"}],
        "meta": {},
    }

    t = JailRecordTransformer()
    out = t.transform(raw)

    assert out["person"]["name"] == "JOHN DOE"
    assert out["booking"]["number"] == "12345"
    assert out["charges"][0]["description"] == "DUI"


# ---------------------------------------------------------
# Sheriff Logs Transformer
# ---------------------------------------------------------

def test_sheriff_log_transformer_basic():
    raw = {
        "source": "churchill_sheriff",
        "entity": "arrest_event",
        "name": "JOHN DOE",
        "age": "32",
        "arrest_date": "01/15/2024",
        "location": "Fallon",
        "agency": "CCSO",
        "charges": [{"description": "DUI"}],
        "meta": {},
    }

    t = SheriffLogTransformer()
    out = t.transform(raw)

    assert out["person"]["name"] == "JOHN DOE"
    assert out["arrest"]["location"] == "Fallon"
    assert out["charges"][0]["description"] == "DUI"
