import pytest
from bs4 import BeautifulSoup

from courtbeat.connectors.courts.washoe_district import WashoeDistrictConnector
from courtbeat.retrieval.courts.washoe_district_routines import (
    WashoeDistrictRoutines,
    CaseContext,
)


def test_connector_fetches_and_parses(monkeypatch):
    # Fake discovery
    def fake_discover(self, max_pages):
        yield CaseContext(
            case_number="CR24-00123",
            case_type="Criminal",
            status="Open",
            filed_date="01/02/2024",
            detail_url="http://example.com/detail",
        )

    # Fake detail page
    html = """
    <html><body>
        <table id="partyTable">
            <tr><th>Role</th><th>Name</th></tr>
            <tr><td>Defendant</td><td>JOHN DOE</td></tr>
        </table>
        <table id="chargeTable">
            <tr><th>Statute</th><th>Description</th><th>Severity</th></tr>
            <tr><td>NRS 200.010</td><td>Murder</td><td>Felony A</td></tr>
        </table>
        <table id="eventTable">
            <tr><th>Date</th><th>Event</th><th>Result</th></tr>
            <tr><td>01/10/2024</td><td>Arraignment</td><td>Entered</td></tr>
        </table>
    </body></html>
    """

    class FakeResp:
        text = html

    def fake_get(url):
        return FakeResp()

    monkeypatch.setattr(WashoeDistrictRoutines, "discover_cases", fake_discover)
    monkeypatch.setattr(
        "courtbeat.retrieval.courts.washoe_district_routines.http_get",
        fake_get,
    )

    connector = WashoeDistrictConnector(routines=WashoeDistrictRoutines())
    events = list(connector.fetch(max_pages=1))

    assert len(events) == 1
    rec = events[0]

    assert rec["case_number"] == "CR24-00123"
    assert rec["person"]["defendant"] == "JOHN DOE"
    assert rec["charges"][0]["description"] == "Murder"
    assert rec["events"][0]["type"] == "Arraignment"
