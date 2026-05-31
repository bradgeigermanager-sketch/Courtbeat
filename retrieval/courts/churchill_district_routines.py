"""
Churchill District Court Retrieval Routines
v0.3.0

Implements source-specific routines for the Churchill County District Court,
which publishes a public HTML calendar rather than an Odyssey portal.

These routines support:
- Calendar discovery by date
- Hearing extraction
- Defendant/person extraction
- Case number parsing
- Event type parsing

They produce raw dictionaries that the connector emits and the
CourtRecordTransformer normalizes.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Optional, Dict, Any, List

from bs4 import BeautifulSoup

from courtbeat.utils.http import http_get
from courtbeat.utils.text import clean_text


CHURCHILL_DISTRICT_ROUTINES_VERSION = "0.3.0"


# ---------------------------------------------------------------------------
# Context object for calendar metadata
# ---------------------------------------------------------------------------

@dataclass
class CalendarContext:
    date: datetime
    url: str


# ---------------------------------------------------------------------------
# Main routines class
# ---------------------------------------------------------------------------

class ChurchillDistrictRoutines:
    """
    Retrieval routines for Churchill County District Court.
    """

    BASE_URL = "https://www.churchillcounty.org/DocumentCenter/View"

    # ---------------------------------------------------------
    # Calendar discovery
    # ---------------------------------------------------------

    def discover_calendars(self, months_back: int = 3) -> Iterable[CalendarContext]:
        """
        Discover available court calendars by scanning the DocumentCenter.
        Churchill County publishes PDFs and HTML calendars with predictable URLs.
        """
        # Example pattern:
        # https://www.churchillcounty.org/DocumentCenter/View/XXXXX/Court-Calendar-MM-DD-YYYY
        #
        # We scan the listing page and extract all calendar links.

        listing_url = "https://www.churchillcounty.org/DocumentCenter/Index/123"  # Court Calendar folder
        resp = http_get(listing_url)
        if resp is None:
            return

        soup = BeautifulSoup(resp.text, "lxml")
        links = soup.select("a[href*='Court-Calendar']")

        for a in links:
            href = a.get("href")
            if not href:
                continue

            url = href if href.startswith("http") else f"https://www.churchillcounty.org{href}"

            # Extract date from filename
            m = re.search(r"(\d{2})-(\d{2})-(\d{4})", url)
            if not m:
                continue

            month, day, year = m.groups()
            try:
                date = datetime(int(year), int(month), int(day))
            except ValueError:
                continue

            yield CalendarContext(date=date, url=url)

    # ---------------------------------------------------------
    # Calendar fetching
    # ---------------------------------------------------------

    def fetch_calendar(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch and parse the HTML calendar.
        Churchill sometimes publishes HTML, sometimes PDF.
        For v0.3.0 we support HTML calendars only.
        """
        resp = http_get(url)
        if resp is None:
            return None

        # If PDF, skip for now
        if "application/pdf" in resp.headers.get("Content-Type", ""):
            return None

        return BeautifulSoup(resp.text, "lxml")

    # ---------------------------------------------------------
    # Parsing
    # ---------------------------------------------------------

    def parse_calendar(self, context: CalendarContext, soup: BeautifulSoup) -> Iterable[Dict[str, Any]]:
        """
        Parse the HTML calendar into raw court event dictionaries.
        """
        rows = soup.select("table tr")
        for row in rows[1:]:  # skip header
            cols = [clean_text(td.get_text()) for td in row.find_all("td")]
            if len(cols) < 4:
                continue

            time_str = cols[0]
            case_number = cols[1]
            defendant = cols[2]
            hearing_type = cols[3]

            yield {
                "source": "churchill_district",
                "entity": "court_event",
                "case_number": case_number,
                "case_type": None,
                "status": None,
                "filed_date": None,
                "person": {
                    "defendant": defendant,
                },
                "charges": [],
                "events": [
                    {
                        "date": context.date.strftime("%Y-%m-%d"),
                        "time": time_str,
                        "type": hearing_type,
                        "result": None,
                    }
                ],
                "meta": {
                    "calendar_url": context.url,
                },
            }
