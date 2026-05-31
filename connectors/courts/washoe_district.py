"""
Washoe District Court Connector
v0.3.0

This connector orchestrates:
- WashoeDistrictRoutines (retrieval)
- Raw court event emission for the DAG

It does NOT normalize data — that is handled by transformers.
"""

from __future__ import annotations

from typing import Iterable, Dict, Any

from courtbeat.retrieval.courts.washoe_district_routines import WashoeDistrictRoutines


class WashoeDistrictConnector:
    """
    Connector for the Washoe County District Court (Odyssey Portal).

    Responsibilities:
    - Instantiate retrieval routines
    - Iterate through discovered cases
    - Fetch case detail pages
    - Parse into raw court record dictionaries
    """

    name = "washoe_district"
    version = "0.3.0"

    def __init__(self, routines: WashoeDistrictRoutines | None = None):
        self.routines = routines or WashoeDistrictRoutines()

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def fetch(self, max_pages: int = 20) -> Iterable[Dict[str, Any]]:
        """
        Yield raw court record dictionaries from Washoe District Court.
        """
        for context in self.routines.discover_cases(max_pages=max_pages):
            soup = self.routines.fetch_case_details(context.detail_url)
            if soup is None:
                continue

            record = self.routines.parse_case(context, soup)
            if record:
                yield record
