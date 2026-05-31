"""
Ingestion DAG Runner
v0.3.0

Executes ingestion across all enabled sources defined in the registry.

Responsibilities:
- Load enabled sources
- Instantiate connectors, retrieval routines, and transformers
- Stream normalized events
- Provide a clean, extensible execution interface
"""

from __future__ import annotations

from typing import Iterable, Dict, Any

from courtbeat.registry import Registry, SourceSpec


class IngestionDAG:
    """
    DAG orchestrator for ingestion.

    Each source is defined by:
    - connector class
    - retrieval routines class
    - transformer class

    The DAG:
    - Instantiates each component
    - Calls connector.fetch()
    - Passes raw records to transformer.transform()
    - Yields normalized events
    """

    version = "0.3.0"

    def __init__(self, registry: Registry):
        self.registry = registry

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def run(self, max_pages: int = 10) -> Iterable[Dict[str, Any]]:
        """
        Run ingestion for all enabled sources.

        Yields normalized event dictionaries.
        """
        for name, spec in self.registry.enabled_sources().items():
            yield from self._run_source(spec, max_pages=max_pages)

    # ---------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------

    def _run_source(self, spec: SourceSpec, max_pages: int) -> Iterable[Dict[str, Any]]:
        """
        Execute ingestion for a single source.
        """
        Connector = spec.load_connector()
        Retrieval = spec.load_retrieval()
        Transformer = spec.load_transformer()

        routines = Retrieval()
        connector = Connector(routines)
        transformer = Transformer()

        for raw in connector.fetch(max_pages=max_pages):
            normalized = transformer.transform(raw)
            yield normalized
