"""
Churchill Sheriff Retrieval Routines
v0.3.0

Implements source-specific routines for the Churchill County Sheriff's Office
arrest logs, which are published as simple HTML tables.

These routines support:
- Log discovery
- Log fetching
- Arrest extraction
- Charge parsing

They produce raw dictionaries that the connector emits and the
SheriffLogTransformer normalizes.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Optional, Dict, Any, List

from bs4 import BeautifulSoup

from courtbeat.utils.http import http_get
from courtbeat.utils.text import clean_text


CHURCHILL_SHERIFF_ROUTINES_VERSION = "0.3.0"


# ---------------------------------------------------------------------------
# Context object for log metadata
# ---------------------------------------------------------------------------

@dataclass
class LogContext:
    date: datetime
    url: str


# ---------------------------------------------------------------------------
# Main routines class
# ---------------------------------------------------------------------------

class ChurchillSheriffRoutines:
    """
    Retrieval routines for Churchill County Sheriff's Office arrest logs.
    """

    BASE_URL = "https://www.churchillcounty.org/DocumentCenter/Index/124"  # Arrest Logs folder

    # ---------------------------------------------------------
    # Log discovery
    # ---------------------------------------------------------

    def discover_logs(self) -> Iterable[LogContext]:
        """
        Discover available arrest logs by scanning the DocumentCenter.
        """
        resp = http_get(self.BASE_URL)
        if resp is None:
            return

        soup = BeautifulSoup(resp.text, "lxml")
        links = soup.select("a[href*='Arrest-Log']")

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

            yield LogContext(date=date, url=url)

    # ---------------------------------------------------------
    # Log fetching
    # ---------------------------------------------------------

    def fetch_log(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch and parse the HTML arrest log.
        """
        resp = http_get(url)
        if resp is None:
            return None

        # Skip PDFs for now
        if "application/pdf" in resp.headers.get("Content-Type", ""):
            return None

        return BeautifulSoup(resp.text, "lxml")

    # ---------------------------------------------------------
    # Parsing
    # ---------------------------------------------------------

    def parse_log(self, context: LogContext, soup: BeautifulSoup) -> Iterable[Dict[str, Any]]:
        """
        Parse the HTML arrest log into raw arrest event dictionaries.
        """
        rows = soup.select("table tr")
        for row in rows[1:]:  # skip header
            cols = [clean_text(td.get_text()) for td in row.find_all("td")]
            if len(cols) < 5:
                continue

            arrest_date = cols[0]
            name = cols[1]
            age = cols[2]
            location = cols[3]
            agency = cols[4]

            # Charges may be in a separate column or nested table
            charges = self._extract_charges(row)

            yield {
                "source": "churchill_sheriff",
                "entity": "arrest_event",
                "name": name,
                "age": age,
                "arrest_date": arrest_date or context.date.strftime("%Y-%m-%d"),
                "location": location,
                "agency": agency,
                "charges": charges,
                "meta": {
                    "log_url": context.url,
                },
            }

    # ---------------------------------------------------------
    # Charge extraction
    # ---------------------------------------------------------

    def _extract_charges(self, row) -> List[Dict[str, Any]]:
        """
        Extract charges from a row. Some logs use a nested table.
        """
        charges = []

        # Look for nested table
        nested = row.find("table")
        if nested:
            for tr in nested.find_all("tr")[1:]:
                cols = [clean_text(td.get_text()) for td in tr.find_all("td")]
                if len(cols) >= 2:
                    charges.append({
                        "statute": cols[0],
                        "description": cols[1],
                        "severity": cols[2] if len(cols) > 2 else None,
                    })
            return charges

        # Otherwise, look for a single "Charges" column
        tds = row.find_all("td")
        if len(tds) >= 6:
            raw = clean_text(tds[5].get_text())
            if raw:
                charges.append({
                    "statute": None,
                    "description": raw,
                    "severity": None,
                })

        return charges
