import pytest
from datetime import datetime
from courtbeat.transformers.news_media import NewsMediaTransformer
from courtbeat.schemas.court_event import CourtEventRecord, Event, Charge
from courtbeat.schemas.person import Person


def test_news_media_transformer():
    transformer = NewsMediaTransformer()

    record = CourtEventRecord(
        source="fallon_post",
        entity="court_event",
        article_id="123",
        article_url="http://example.com",
        article_title="District Court – Test",
        article_date=datetime(2024, 1, 1),
        person=Person(full_name="JOHN DOE", first_name="JOHN", last_name="DOE"),
        event=Event(
            type="plea",
            court_level="district",
            charges_raw="DUI",
            charges_normalized=[Charge(statute=None, description="DUI")],
            disposition_raw="guilty",
            disposition_normalized="guilty",
            hearing_date=datetime(2024, 1, 1),
        ),
        meta={"raw_line": "JOHN DOE, pleaded guilty for DUI."},
    )

    out = transformer.transform(record)

    assert out["source"] == "fallon_post"
    assert out["person"]["full_name"] == "JOHN DOE"
    assert out["event"]["type"] == "plea"
    assert out["event"]["charges_raw"] == "DUI"
