import pytest
from bs4 import BeautifulSoup
from datetime import datetime

from courtbeat.retrieval.sheriff.churchill_sheriff_routines import (
    ChurchillSheriffRoutines,
    LogContext,
)


def test_discover_logs_parses_links(monkeypatch):
    html = """
    <a href="/DocumentCenter/View/1234/Arrest-Log-01-15-2024">Log</a>
    """

    class FakeResp:
        text = html

    def fake_get(url):
        return FakeResp()

    monkeypatch.setattr(
        "courtbeat.retrieval.sheriff.churchill_sheriff_routines.http_get",
        fake_get,
    )

    routines = ChurchillSheriffRoutines()
    logs = list(routines.discover_logs())

    assert len(logs) == 1
    ctx = logs[0]

    assert ctx.date == datetime(2024, 1, 15)
    assert ctx.url.endswith("Arrest-Log-01-15-2024")


def test_fetch_log_html(monkeypatch):
    html = "<html><body><table><tr><td>Test</td></tr></table></body></html>"

    class FakeResp:
        text = html
        headers = {"Content-Type": "text/html"}

    def fake_get(url):
        return FakeResp()

    monkeypatch.setattr(
        "courtbeat.retrieval.sheriff.churchill_sheriff_routines.http_get",
        fake_get,
    )

    routines = ChurchillSheriffRoutines()
    soup = routines.fetch_log("http://example.com")

    assert isinstance(soup, BeautifulSoup)
    assert "Test" in soup.get_text()


def test_parse_log_basic():
    html = """
    <table>
        <tr><th>Date</th><th>Name</th><th>Age</th><th>Location</th><th>Agency</th><th>Charges</th></tr>
        <tr>
            <td>01/15/2024</td>
            <td>JOHN DOE</td>
            <td>32</td>
            <td>Fallon</td>
            <td>CCSO</td>
            <td>DUI</td>
        </tr>
    </table>
    """

    soup = BeautifulSoup(html, "lxml")
    context = LogContext(date=datetime(2024, 1, 15), url="http://example.com")

    routines = ChurchillSheriffRoutines()
    records = list(routines.parse_log(context, soup))

    assert len(records) == 1
    rec = records[0]

    assert rec["source"] == "churchill_sheriff"
    assert rec["name"] == "JOHN DOE"
    assert rec["charges"][0]["description"] == "DUI"
    assert rec["agency"] == "CCSO"
