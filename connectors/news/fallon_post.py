"""
Fallon Post Connector
v0.3.0

This connector orchestrates:
- FallonPostRoutines (retrieval)
- Raw event emission for the DAG

It does NOT normalize data — that is handled by transformers.
"""

from __future__ import annotations

from typing import Iterable

from courtbeat.retrieval.news.fallon_post_routines import FallonPostRoutines
from courtbeat.schemas.court_event import CourtEventRecord


class FallonPostConnector:
    """
    Connector for the Fallon Post news outlet.

    Responsibilities:
    - Instantiate retrieval routines
    - Iterate through discovered articles
    - Fetch article content
    - Extract lines
    - Parse lines into raw CourtEventRecord objects
    """

    name = "fallon_post"
    version = "0.3.0"

    def __init__(self, routines: FallonPostRoutines | None = None):
        self.routines = routines or FallonPostRoutines()

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def fetch(self, max_pages: int = 10) -> Iterable[CourtEventRecord]:
        """
        Yield raw CourtEventRecord objects from Fallon Post court reports.
        """
        for context in self.routines.discover_articles(max_pages=max_pages):
            soup = self.routines.fetch_article(context.url)
            if soup is None:
                continue

            lines = self.routines.extract_lines(soup)
            for line in lines:
                record = self.routines.parse_line(line, context)
                if record:
                    yield record
