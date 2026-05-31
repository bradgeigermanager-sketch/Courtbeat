"""
Churchill Justice Court Connector
v0.3.0

This connector orchestrates:
- ChurchillJusticeRoutines (retrieval)
- Raw court event emission for the DAG

It does NOT normalize data — that is handled by transformers.
"""

from __future__ import annotations

from typing import Iterable, Dict, Any

from courtbeat.retrieval.courts.churchill_justice_routines import (
    ChurchillJusticeRoutines,
    JusticeSearchContext,
)


class ChurchillJusticeConnector:
    """
    Connector for the Churchill County Justice Court.

    Responsibilities:
    - Instantiate retrieval routines
    - Load clerk-provided documents (HTML for v0.3.0)
    - Parse into raw court event dictionaries

    NOTE:
    The caller (DAG or CLI) must provide:
    - query_type
    - query_value
    - returned_date
    - source_file (path to clerk-provided HTML)
    """

    name = "churchill_justice"
    version = "0.3.0"

    def __init__(self, routines: ChurchillJusticeRoutines | None = None):
        self.routines = routines or ChurchillJusticeRoutines()

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def fetch(
        self,
        query_type: str,
        query_value: str,
        returned_date,
        source_file: str,
    ) -> Iterable[Dict[str, Any]]:
        """
        Yield raw court event dictionaries from clerk-provided documents.
        """
        context = JusticeSearchContext(
            query_type=query_type,
            query_value=query_value,
            returned_date=returned_date,
            source_file=source_file,
        )

        soup = self.routines.load_clerk_document(source_file)
        if soup is None:
            return

        for record in self.routines.parse_document(context, soup):
            yield record
