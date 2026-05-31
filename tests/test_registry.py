import pytest
from pathlib import Path
from courtbeat.registry import Registry, SourceSpec


def test_registry_loads_sources():
    base = Path(__file__).resolve().parents[1] / "courtbeat"
    registry = Registry(base)
    registry.load_all()

    sources = registry.enabled_sources()
    assert isinstance(sources, dict)
    assert "fallon_post" in sources
    assert isinstance(sources["fallon_post"], SourceSpec)


def test_registry_loads_connector_class():
    base = Path(__file__).resolve().parents[1] / "courtbeat"
    registry = Registry(base)
    registry.load_all()

    spec = registry.get("fallon_post")
    Connector = spec.load_connector()
    assert Connector.__name__ == "FallonPostConnector"
