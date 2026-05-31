"""
Clark Jail Connector
v0.3.0

This connector orchestrates:
- ClarkJailRoutines (retrieval)
- Raw arrest event emission for the DAG

It does NOT normalize data — that is handled by transformers.
"""

from __future__ import annotations

from typing import Iterable, Dict, Any

from courtbeat.retrieval.jails.clark_jail_routines import ClarkJailRoutines


class ClarkJailConnector:
    """
    Connector for the Clark County Detention Center (CCDC).

    Responsibilities:
    - Instantiate retrieval routines
    - Iterate through discovered inmates
    - Fetch booking details
    - Parse into raw arrest event dictionaries
    """

    name = "clark_jail"
    version = "0.3.0"

    def __init__(self, routines: ClarkJailRoutines | None = None):
        self.routines = routines or ClarkJailRoutines()

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def fetch(self) -> Iterable[Dict[str, Any]]:
        """
        Yield raw arrest event dictionaries from Clark County Jail.
        """
        for context in self.routines.discover_inmates():
            details = self.routines.fetch_booking_details(context.inmate_id)
            if not details:
                continue

            record = self.routines.parse_inmate_record(context, details)
            if record:
                yield record
