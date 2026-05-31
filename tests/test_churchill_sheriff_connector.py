import pytest
from bs4 import BeautifulSoup
from datetime import datetime

from courtbeat.connectors.sheriff.churchill_sheriff import ChurchillSheriffConnector
from courtbeat.retrieval.sheriff.churchill_sheriff_routines import (
    ChurchillSheriffRoutines,
    LogContext,
)


def test_connector_parses_log(monkeypatch):
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

    class FakeRoutines(ChurchillSheriffRoutines):
        def discover_logs(self):
            yield LogContext(date=datetime(2024, 1, 15), url="http://example.com")

        def fetch_log(self, url):
            return BeautifulSoup(html, "lxml")

    connector = ChurchillSheriffConnector(routines=FakeRoutines())
    events = list(connector.fetch())

    assert len(events) == 1
    rec = events[0]

    assert rec["entity"] == "arrest_event"
    assert rec["name"] == "JOHN DOE"
    assert rec["charges"][0]["description"] == "DUI"
