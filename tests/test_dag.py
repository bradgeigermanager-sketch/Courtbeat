import pytest
from pathlib import Path
from courtbeat.registry import Registry
from courtbeat.dag import IngestionDAG


def test_dag_initialization():
    base = Path(__file__).resolve().parents[1] / "courtbeat"
    registry = Registry(base)
    registry.load_all()

    dag = IngestionDAG(registry)
    assert dag.version == "0.3.0"


def test_dag_runs_without_errors(monkeypatch):
    """
    We monkeypatch the FallonPostConnector.fetch() method
    to avoid hitting the network.
    """

    class FakeRecord:
        source = "fallon_post"
        entity = "court_event"
        article_id = "123"
        article_url = "http://example.com"
        article_title = "Test"
        article_date = None
        person = type("P", (), {"full_name": "JOHN DOE", "first_name": "JOHN",
                                "middle_name": None, "last_name": "DOE"})
        event = type("E", (), {"type": "plea", "court_level": "district",
                               "charges_raw": "Test Charge",
                               "disposition_raw": None,
                               "disposition_normalized": None,
                               "hearing_date": None})
        meta = {}

    def fake_fetch(self, max_pages=10):
        yield FakeRecord()

    from courtbeat.connectors.news.fallon_post import FallonPostConnector
    monkeypatch.setattr(FallonPostConnector, "fetch", fake_fetch)

    base = Path(__file__).resolve().parents[1] / "courtbeat"
    registry = Registry(base)
    registry.load_all()

    dag = IngestionDAG(registry)
    events = list(dag.run(max_pages=1))

    assert len(events) == 1
    assert events[0]["source"] == "fallon_post"
