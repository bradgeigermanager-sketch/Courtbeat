import pytest
from datetime import datetime
from bs4 import BeautifulSoup

from courtbeat.connectors.courts.churchill_justice import ChurchillJusticeConnector
from courtbeat.retrieval.courts.churchill_justice_routines import (
    ChurchillJusticeRoutines,
    JusticeSearchContext,
)


def test_connector_parses_clerk_document(monkeypatch, tmp_path):
    html = """
    <html><body>
        <table>
            <tr><th>Case</th><th>Name</th><th>Charge</th><th>Event</th><th>Date</th></tr>
            <tr><td>23-1234</td><td>JOHN DOE</td><td>DUI</td><td>Arraignment</td><td>01/02/2024</td></tr>
        </table>
    </body></html>
    """

    file = tmp_path / "justice.html"
    file.write_text(html, encoding="utf-8")

    # Monkeypatch routines to avoid filesystem/network complexity
    class FakeRoutines(ChurchillJusticeRoutines):
        def load_clerk_document(self, path):
            return BeautifulSoup(html, "lxml")

    connector = ChurchillJusticeConnector(routines=FakeRoutines())

    records = list(
        connector.fetch(
            query_type="name",
            query_value="JOHN DOE",
            returned_date=datetime(2024, 1, 5),
            source_file=str(file),
        )
    )

    assert len(records) == 1
    rec = records[0]

    assert rec["entity"] == "court_event"
    assert rec["person"]["defendant"] == "JOHN DOE"
    assert rec["charges"][0]["description"] == "DUI"
