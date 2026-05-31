import pytest
from bs4 import BeautifulSoup
from courtbeat.retrieval.news.fallon_post_routines import FallonPostRoutines, ArticleContext


def test_extract_lines_basic():
    routines = FallonPostRoutines()
    html = """
    <article>
        <p>JOHN DOE, pleaded guilty for DUI.</p>
        <p>JANE SMITH, arraigned for battery.</p>
    </article>
    """
    soup = BeautifulSoup(html, "lxml")
    lines = routines.extract_lines(soup)

    assert len(lines) == 2
    assert "JOHN DOE" in lines[0]


def test_parse_line_basic():
    routines = FallonPostRoutines()
    context = ArticleContext(
        url="https://example.com/article/123",
        title="District Court – Feb 24",
        date=None,
    )

    line = "JOHN DOE, pleaded guilty for DUI."
    record = routines.parse_line(line, context)

    assert record is not None
    assert record.person.full_name == "JOHN DOE"
    assert record.event.type == "plea"
    assert "DUI" in record.event.charges_raw
