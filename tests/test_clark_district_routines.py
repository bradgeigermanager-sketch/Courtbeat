import pytest
from bs4 import BeautifulSoup

from courtbeat.retrieval.courts.clark_district_routines import (
    ClarkDistrictRoutines,
    CaseContext,
)


def test_discover_cases_parses_rows(monkeypatch):
    html = """
    <table id="caseSearchResults">
        <tr><th>Case</th><th>Type</th><th>Status</th><th>Filed</th></tr>
        <tr>
            <td>24-CR-00123</td>
            <td>Criminal</td>
            <td>Open</td>
            <td>01/02/2024</td>
            <td><a href="/CaseDetail/123">View</a></td>
        </tr>
    </table>
    """

    class FakeResp:
        text = html

    def fake_get(url):
        return FakeResp()

    monkeypatch.setattr("courtbeat.retrieval.courts.clark_district_routines.http_get", fake_get)

    routines = ClarkDistrictRoutines()
    cases = list(routines.discover_cases(max_pages=1))

    assert len(cases) == 1
    ctx = cases[0]

    assert ctx.case_number == "24-CR-00123"
    assert ctx.case_type == "Criminal"
    assert ctx.status == "Open"
    assert ctx.filed_date == "01/02/2024"
    assert ctx.detail_url.endswith("/CaseDetail/123")


def test_parse_case_extracts_all_sections():
    html = """
    <html><body>
        <table id="partyTable">
            <tr><th>Role</th><th>Name</th></tr>
            <tr><td>Defendant</td><td>JOHN DOE</td></tr>
        </table>

        <table id="chargeTable">
            <tr><th>Statute</th><th>Description</th><th>Severity</th></tr>
            <tr><td>NRS 484C.110</td><td>DUI</td><td>Misdemeanor</td></tr>
        </table>

        <table id="eventTable">
            <tr><th>Date</th><th>Event</th><th>Result</th></tr>
            <tr><td>01/10/2024</td><td>Arraignment</td><td>Continued</td></tr>
        </table>
    </body></html>
    """

    soup = BeautifulSoup(html, "lxml")
    ctx = CaseContext(
        case_number="24-CR-00123",
        case_type="Criminal",
        status="Open",
        filed_date="01/02/2024",
        detail_url="https://example.com",
    )

    routines = ClarkDistrictRoutines()
    record = routines.parse_case(ctx, soup)

    assert record["case_number"] == "24-CR-00123"
    assert record["person"]["defendant"] == "JOHN DOE"
    assert record["charges"][0]["description"] == "DUI"
    assert record["events"][0]["type"] == "Arraignment"
