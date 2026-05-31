"""
Churchill Sheriff Connector
v0.3.0

This connector orchestrates:
- ChurchillSheriffRoutines (retrieval)
- Raw arrest event emission for the DAG

It does NOT normalize data — that is handled by transformers.
"""

from __future__ import annotations

from typing import Iterable, Dict, Any

from courtbeat.retrieval.sheriff.churchill_sheriff_routines import ChurchillSheriffRoutines


class ChurchillSheriffConnector:
    """
    Connector for the Churchill County Sheriff's Office arrest logs.

    Responsibilities:
    - Instantiate retrieval routines
    - Iterate through discovered logs
    - Fetch log pages
    - Parse into raw arrest event dictionaries
    """

    name = "churchill_sheriff"
    version = "0.3.0"

    def __init__(self, routines: ChurchillSheriffRoutines | None = None):
        self.routines = routines or ChurchillSheriffRoutines()

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def fetch(self) -> Iterable[Dict[str, Any]]:
        """
        Yield raw arrest event dictionaries from Churchill County Sheriff logs.
        """
        for context in self.routines.discover_logs():
            soup = self.routines.fetch_log(context.url)
            if soup is None:
                continue

            for record in self.routines.parse_log(context, soup):
                yield record
