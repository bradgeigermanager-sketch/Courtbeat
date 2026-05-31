import pytest
from bs4 import BeautifulSoup

from courtbeat.retrieval.jails.washoe_jail_routines import (
    WashoeJailRoutines,
    InmateContext,
)


def test_discover_inmates_parses_json(monkeypatch):
    data = {
        "inmates": [
            {
                "booking_number": "12345",
                "name": "JOHN DOE",
                "dob": "1990-01-01",
                "booking_date": "2024-01-10",
                "facility": "Washoe County Jail",
            }
        ]
    }

    class FakeResp:
        def json(self):
            return data

    def fake_get(url):
        return FakeResp()

    monkeypatch.setattr(
        "courtbeat.retrieval.jails.washoe_jail_routines.http_get",
        fake_get,
    )

    routines = WashoeJailRoutines()
    inmates = list(routines.discover_inmates())

    assert len(inmates) == 1
    ctx = inmates[0]

    assert ctx.booking_number == "12345"
    assert ctx.name == "JOHN DOE"
    assert ctx.dob == "1990-01-01"
    assert ctx.booking_date == "2024-01-10"


def test_fetch_booking_details(monkeypatch):
    details = {
        "status": "In Custody",
        "charges": [
            {"statute": "NRS 484C.110", "description": "DUI", "severity": "Misdemeanor"}
        ],
    }

    class FakeResp:
        def json(self):
            return details

    def fake_get(url):
        return FakeResp()

    monkeypatch.setattr(
        "courtbeat.retrieval.jails.washoe_jail_routines.http_get",
        fake_get,
    )

    routines = WashoeJailRoutines()
    result = routines.fetch_booking_details("12345")

    assert result["status"] == "In Custody"
    assert result["charges"][0]["description"] == "DUI"


def test_parse_inmate_record():
    context = InmateContext(
        booking_number="12345",
        name="JOHN DOE",
        dob="1990-01-01",
        booking_date="2024-01-10",
        facility="Washoe County Jail",
    )

    details = {
        "status": "In Custody",
        "charges": [
            {"statute": "NRS 484C.110", "description": "DUI", "severity": "Misdemeanor"}
        ],
    }

    routines = WashoeJailRoutines()
    record = routines.parse_inmate_record(context, details)

    assert record["source"] == "washoe_jail"
    assert record["name"] == "JOHN DOE"
    assert record["charges"][0]["description"] == "DUI"
    assert record["status"] == "In Custody"
