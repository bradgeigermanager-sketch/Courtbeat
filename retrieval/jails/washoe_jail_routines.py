"""
Washoe Jail Retrieval Routines
v0.3.0

Source-specific routines for:
- Inmate roster discovery
- Booking detail retrieval
- Charge extraction
- Arrest metadata parsing

Washoe County exposes a JSON API for inmate data.
These routines wrap that API and produce raw arrest records
for the connector to emit.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Optional, Dict, Any, List

from courtbeat.utils.http import http_get
from courtbeat.utils.text import clean_text


# ---------------------------------------------------------------------------
# Version
# ---------------------------------------------------------------------------

WASHOE_JAIL_ROUTINES_VERSION = "0.3.0"


# ---------------------------------------------------------------------------
# Context object for inmate metadata
# ---------------------------------------------------------------------------

@dataclass
class InmateContext:
    booking_number: str
    name: str
    dob: Optional[str]
    booking_date: Optional[str]
    facility: Optional[str]


# ---------------------------------------------------------------------------
# Main routines class
# ---------------------------------------------------------------------------

class WashoeJailRoutines:
    """
    Retrieval routines for Washoe County Jail.
    """

    BASE_URL = "https://jail.washoesheriff.com/api"

    # ---------------------------------------------------------
    # Discovery
    # ---------------------------------------------------------

    def discover_inmates(self) -> Iterable[InmateContext]:
        """
        Retrieve the full inmate roster.
        """
        url = f"{self.BASE_URL}/inmates"
        resp = http_get(url)
        if resp is None:
            return

        try:
            data = resp.json()
        except json.JSONDecodeError:
            return

        for entry in data.get("inmates", []):
            yield InmateContext(
                booking_number=str(entry.get("booking_number")),
                name=clean_text(entry.get("name", "")),
                dob=entry.get("dob"),
                booking_date=entry.get("booking_date"),
                facility=entry.get("facility"),
            )

    # ---------------------------------------------------------
    # Fetch booking details
    # ---------------------------------------------------------

    def fetch_booking_details(self, booking_number: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve detailed booking information for a specific inmate.
        """
        url = f"{self.BASE_URL}/inmates/{booking_number}"
        resp = http_get(url)
        if resp is None:
            return None

        try:
            return resp.json()
        except json.JSONDecodeError:
            return None

    # ---------------------------------------------------------
    # Parsing
    # ---------------------------------------------------------

    def parse_inmate_record(
        self,
        context: InmateContext,
        details: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Convert inmate JSON into a raw arrest record dictionary.
        """
        charges = []
        for ch in details.get("charges", []):
            charges.append({
                "statute": ch.get("statute"),
                "description": clean_text(ch.get("description", "")),
                "severity": ch.get("severity"),
            })

        return {
            "source": "washoe_jail",
            "entity": "arrest_event",
            "name": context.name,
            "dob": context.dob,
            "booking_number": context.booking_number,
            "booking_date": context.booking_date,
            "facility": context.facility,
            "status": details.get("status"),
            "charges": charges,
            "meta": {
                "raw": details,
            },
        }
