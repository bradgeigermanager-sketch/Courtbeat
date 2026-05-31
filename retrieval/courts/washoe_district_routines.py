"""
Washoe District Court Retrieval Routines
v0.3.0

Implements source-specific routines for the Washoe County District Court
Odyssey Portal, including:

- Session initialization
- Case search
- Case detail retrieval
- Charge extraction
- Hearing/event extraction
- Party/person extraction

These routines produce raw dictionaries that the connector emits and the
CourtRecordTransformer normalizes.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Optional, Dict, Any, List

from bs4 import BeautifulSoup

from courtbeat.utils.http import http_get, http_post
from courtbeat.utils.text import clean_text


# ---------------------------------------------------------------------------
# Version
# ---------------------------------------------------------------------------

WASHOE_DISTRICT_ROUTINES_VERSION = "0.3.0"


# ---------------------------------------------------------------------------
# Context object for case metadata
# ---------------------------------------------------------------------------

@dataclass
class CaseContext:
    case_number: str
    case_type: str
    status: Optional[str]
    filed_date: Optional[str]
    detail_url: str


# ---------------------------------------------------------------------------
# Main routines class
# ---------------------------------------------------------------------------

class WashoeDistrictRoutines:
    """
    Retrieval routines for Washoe County District Court (Odyssey Portal).
    """

    BASE_URL = "https://www.washoecourts.com/Query/CaseSearch"

    # ---------------------------------------------------------
    # Case discovery
    # ---------------------------------------------------------

    def discover_cases(self, max_pages: int = 20, delay: float = 0.5) -> Iterable[CaseContext]:
        """
        Discover cases by paging through the Odyssey search results.
        """
        for page in range(1, max_pages + 1):
            url = f"{self.BASE_URL}?page={page}"
            resp = http_get(url)
            if resp is None:
                break

            soup = BeautifulSoup(resp.text, "lxml")
            rows = soup.select("table#caseSearchResults tr")

            if len(rows) <= 1:
                break  # no more results

            for row in rows[1:]:
                cols = [clean_text(td.get_text()) for td in row.find_all("td")]
                if len(cols) < 4:
                    continue

                case_number = cols[0]
                case_type = cols[1]
                status = cols[2]
                filed_date = cols[3]

                a = row.find("a", href=True)
                if not a:
                    continue

                detail_url = a["href"]
                if not detail_url.startswith("http"):
                    detail_url = "https://www.washoecourts.com" + detail_url

                yield CaseContext(
                    case_number=case_number,
                    case_type=case_type,
                    status=status,
                    filed_date=filed_date,
                    detail_url=detail_url,
                )

            time.sleep(delay)

    # ---------------------------------------------------------
    # Case detail retrieval
    # ---------------------------------------------------------

    def fetch_case_details(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch the case detail page.
        """
        resp = http_get(url)
        if resp is None:
            return None
        return BeautifulSoup(resp.text, "lxml")

    # ---------------------------------------------------------
    # Parsing
    # ---------------------------------------------------------

    def parse_case(self, context: CaseContext, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Convert a case detail page into a raw court record dictionary.
        """
        parties = self._extract_parties(soup)
        charges = self._extract_charges(soup)
        events = self._extract_events(soup)

        return {
            "source": "washoe_district",
            "entity": "court_event",
            "case_number": context.case_number,
            "case_type": context.case_type,
            "status": context.status,
            "filed_date": context.filed_date,
            "person": parties,
            "charges": charges,
            "events": events,
            "meta": {
                "detail_url": context.detail_url,
            },
        }

    # ---------------------------------------------------------
    # Party extraction
    # ---------------------------------------------------------

    def _extract_parties(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Extract party information (defendant, plaintiff, etc.).
        """
        parties = {}

        rows = soup.select("table#partyTable tr")
        for row in rows[1:]:
            cols = [clean_text(td.get_text()) for td in row.find_all("td")]
            if len(cols) < 2:
                continue

            role = cols[0].lower()
            name = cols[1]

            parties[role] = name

        return parties

    # ---------------------------------------------------------
    # Charge extraction
    # ---------------------------------------------------------

    def _extract_charges(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract charges from the case detail page.
        """
        charges = []

        rows = soup.select("table#chargeTable tr")
        for row in rows[1:]:
            cols = [clean_text(td.get_text()) for td in row.find_all("td")]
            if len(cols) < 3:
                continue

            statute = cols[0]
            description = cols[1]
            severity = cols[2]

            charges.append({
                "statute": statute,
                "description": description,
                "severity": severity,
            })

        return charges

    # ---------------------------------------------------------
    # Event extraction
    # ---------------------------------------------------------

    def _extract_events(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract hearing/event logs from the case detail page.
        """
        events = []

        rows = soup.select("table#eventTable tr")
        for row in rows[1:]:
            cols = [clean_text(td.get_text()) for td in row.find_all("td")]
            if len(cols) < 3:
                continue

            date = cols[0]
            event_type = cols[1]
            result = cols[2]

            events.append({
                "date": date,
                "type": event_type,
                "result": result,
            })

        return events
