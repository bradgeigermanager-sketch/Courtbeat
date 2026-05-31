import pytest
from bs4 import BeautifulSoup

from courtbeat.connectors.jails.washoe_jail import WashoeJailConnector
from courtbeat.retrieval.jails.washoe_jail_routines import (
    WashoeJailRoutines,
    InmateContext,
)


def test_connector_fetches_and_parses(monkeypatch):
    # Fake roster
    def fake_discover(self):
        yield InmateContext(
            booking_number="12345",
            name="JOHN DOE",
            dob="1990-01-01",
            booking_date="2024-01-10",
            facility="Washoe County Jail",
        )

    # Fake booking details
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

    monkeypatch.setattr(WashoeJailRoutines, "discover_inmates", fake_discover)
    monkeypatch.setattr(
        "courtbeat.retrieval.jails.washoe_jail_routines.http_get",
        fake_get,
    )

    connector = WashoeJailConnector(routines=WashoeJailRoutines())
    events = list(connector.fetch())

    assert len(events) == 1
    rec = events[0]

    assert rec["entity"] == "arrest_event"
    assert rec["name"] == "JOHN DOE"
    assert rec["charges"][0]["description"] == "DUI"
