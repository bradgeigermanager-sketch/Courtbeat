import pytest
from datetime import datetime
from bs4 import BeautifulSoup

from courtbeat.retrieval.courts.churchill_justice_routines import (
    ChurchillJusticeRoutines,
    JusticeSearchContext,
)


def test_build_request_payload():
    routines = ChurchillJusticeRoutines()
    payload = routines.build_request_payload("name", "JOHN DOE")

    assert payload["query_type"] == "name"
    assert payload["value"] == "JOHN DOE"
    assert payload["fee_per_name_per_year"] == 0.50


def test_load_clerk_document(tmp_path):
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

    routines = ChurchillJusticeRoutines()
    soup = routines.load_clerk_document(str(file))

    assert isinstance(soup, BeautifulSoup)
    assert "JOHN DOE" in soup.get_text()


def test_parse_document_basic():
    html = """
    <html><body>
        <table>
            <tr><th>Case</th><th>Name</th><th>Charge</th><th>Event</th><th>Date</th></tr>
            <tr><td>23-1234</td><td>JOHN DOE</td><td>DUI</td><td>Arraignment</td><td>01/02/2024</td></tr>
        </table>
    </body></html>
    """

    soup = BeautifulSoup(html, "lxml")

    context = JusticeSearchContext(
        query_type="name",
        query_value="JOHN DOE",
        returned_date=datetime(2024, 1, 5),
        source_file="justice.html",
    )

    routines = ChurchillJusticeRoutines()
    records = list(routines.parse_document(context, soup))

    assert len(records) == 1
    rec = records[0]

    assert rec["source"] == "churchill_justice"
    assert rec["person"]["defendant"] == "JOHN DOE"
    assert rec["charges"][0]["description"] == "DUI"
    assert rec["events"][0]["type"] == "Arraignment"
    assert rec["events"][0]["date"] == "01/02/2024"
