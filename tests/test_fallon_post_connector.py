import pytest
from courtbeat.connectors.news.fallon_post import FallonPostConnector
from courtbeat.retrieval.news.fallon_post_routines import FallonPostRoutines


def test_connector_initializes():
    connector = FallonPostConnector()
    assert connector.name == "fallon_post"


def test_connector_fetch_monkeypatched(monkeypatch):
    """
    Avoid network calls by monkeypatching routines.
    """

    class FakeRoutines(FallonPostRoutines):
        def discover_articles(self, max_pages=10):
            from courtbeat.retrieval.news.fallon_post_routines import ArticleContext
            yield ArticleContext(
                url="http://example.com",
                title="District Court – Test",
                date=None,
            )

        def fetch_article(self, url):
            from bs4 import BeautifulSoup
            return BeautifulSoup("<article><p>JOHN DOE, pleaded guilty for DUI.</p></article>", "lxml")

    connector = FallonPostConnector(routines=FakeRoutines())
    events = list(connector.fetch(max_pages=1))

    assert len(events) == 1
    assert events[0].person.full_name == "JOHN DOE"
