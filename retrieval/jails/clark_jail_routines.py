"""
Clark Jail Retrieval Routines
v0.3.0

Source-specific routines for:
- Inmate roster discovery (HTML-based)
- Booking detail retrieval
- Charge extraction
- Arrest metadata parsing

Clark County Detention Center (CCDC) uses an HTML-based inmate search
endpoint with predictable query parameters. These routines wrap that
endpoint and produce raw arrest records for the connector to emit.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Optional, Dict, Any, List

from bs4 import BeautifulSoup

from courtbeat.utils.http import http_get
from courtbeat.utils.text import clean_text


# ---------------------------------------------------------------------------
# Version
# ---------------------------------------------------------------------------

CLARK_JAIL_ROUTINES_VERSION = "0.3.0"


# ---------------------------------------------------------------------------
# Context object for inmate metadata
# ---------------------------------------------------------------------------

@dataclass
class InmateContext:
    inmate_id: str
    name: str
    booking_date: Optional[str]
    dob: Optional[str]
    facility: Optional[str]


# ---------------------------------------------------------------------------
# Main routines class
# ---------------------------------------------------------------------------

class ClarkJailRoutines:
    """
    Retrieval routines for Clark County Detention Center (CCDC).
    """

    BASE_URL = "https://www.clarkcountynv.gov/ccdc/inmate_search"

    # ---------------------------------------------------------
    # Discovery
    # ---------------------------------------------------------

    def discover_inmates(self) -> Iterable[InmateContext]:
        """
        Retrieve the inmate roster by scraping the HTML search results.
        """
        url = f"{self.BASE_URL}/results.php?search=all"
        resp = http_get(url)
        if resp is None:
            return

        soup = BeautifulSoup(resp.text, "lxml")
        rows = soup.select("table.inmateTable tr")

        for row in rows[1:]:  # skip header
            cols = [clean_text(td.get_text()) for td in row.find_all("td")]
            if len(cols) < 4:
                continue

            inmate_id = cols[0]
            name = cols[1]
            booking_date = cols[2]
            dob = cols[3]

            yield InmateContext(
                inmate_id=inmate_id,
                name=name,
                booking_date=booking_date,
                dob=dob,
                facility="Clark County Detention Center",
            )

    # ---------------------------------------------------------
    # Fetch booking details
    # ---------------------------------------------------------

    def fetch_booking_details(self, inmate_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve detailed booking information for a specific inmate.
        """
        url = f"{self.BASE_URL}/details.php?id={inmate_id}"
        resp = http_get(url)
        if resp is None:
            return None

        soup = BeautifulSoup(resp.text, "lxml")
        return self._parse_details_page(soup)

    # ---------------------------------------------------------
    # Parsing
    # ---------------------------------------------------------

    def _parse_details_page(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Parse the inmate detail page into a structured dictionary.
        """
        details = {}

        # Basic info
        details["status"] = self._extract_field(soup, "Status")
        details["booking_number"] = self._extract_field(soup, "Booking Number")
        details["arrest_date"] = self._extract_field(soup, "Arrest Date")
        details["agency"] = self._extract_field(soup, "Arresting Agency")

        # Charges
        charges = []
        charge_rows = soup.select("table.chargeTable tr")
        for row in charge_rows[1:]:
            cols = [clean_text(td.get_text()) for td in row.find_all("td")]
            if len(cols) < 3:
                continue
            charges.append({
                "statute": cols[0],
                "description": cols[1],
                "severity": cols[2],
            })

        details["charges"] = charges
        return details

    def _extract_field(self, soup: BeautifulSoup, label: str) -> Optional[str]:
        """
        Extract a labeled field from the details page.
        """
        el = soup.find("td", string=re.compile(label, re.I))
        if not el:
            return None
        sibling = el.find_next_sibling("td")
        return clean_text(sibling.get_text()) if sibling else None

    # ---------------------------------------------------------
    # Record construction
    # ---------------------------------------------------------

    def parse_inmate_record(
        self,
        context: InmateContext,
        details: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Convert inmate HTML details into a raw arrest record dictionary.
        """
        return {
            "source": "clark_jail",
            "entity": "arrest_event",
            "name": context.name,
            "dob": context.dob,
            "booking_number": details.get("booking_number"),
            "booking_date": context.booking_date,
            "facility": context.facility,
            "status": details.get("status"),
            "charges": details.get("charges", []),
            "arrest_date": details.get("arrest_date"),
            "agency": details.get("agency"),
            "meta": {
                "inmate_id": context.inmate_id,
                "raw": details,
            },
        }
