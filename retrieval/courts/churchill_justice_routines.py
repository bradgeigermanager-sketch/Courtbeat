"""
Churchill Justice Court Retrieval Routines
v0.3.0

Churchill County Justice Court does NOT publish:
- Online dockets
- Online calendars
- Online case lookup

All records must be obtained via the official Record Search Request Form.

These routines implement:
- Request payload construction
- Clerk-response ingestion (HTML or PDF)
- Charge extraction
- Hearing/event extraction
- Defendant/person extraction

They produce raw dictionaries that the connector emits and the
CourtRecordTransformer normalizes.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Optional, Dict, Any, List

from bs4 import BeautifulSoup

from courtbeat.utils.text import clean_text


CHURCHILL_JUSTICE_ROUTINES_VERSION = "0.3.0"


# ---------------------------------------------------------------------------
# Context object for search metadata
# ---------------------------------------------------------------------------

@dataclass
class JusticeSearchContext:
    query_type: str          # name | date_range | charge
    query_value: str
    returned_date: datetime
    source_file: str         # path to clerk-provided HTML/PDF


# ---------------------------------------------------------------------------
# Main routines class
# ---------------------------------------------------------------------------

class ChurchillJusticeRoutines:
    """
    Retrieval routines for Churchill County Justice Court.

    Since the court provides no online system, these routines operate on
    clerk-returned documents (HTML or PDF).
    """

    # ---------------------------------------------------------
    # Request payload construction
    # ---------------------------------------------------------

    def build_request_payload(self, query_type: str, value: str) -> Dict[str, Any]:
        """
        Build the payload for the Churchill Justice Court Record Search Request.
        """
        return {
            "query_type": query_type,
            "value": value,
            "fee_per_name_per_year": 0.50,
            "copy_fee_per_page": 0.50,
            "certification_fee": 3.00,
            "audio_fee": 25.00,
        }

    # ---------------------------------------------------------
    # Clerk response ingestion
    # ---------------------------------------------------------

    def load_clerk_document(self, path: str) -> Optional[BeautifulSoup]:
        """
        Load a clerk-provided HTML document.
        PDF support can be added later via OCR/PDF parsing.
        """
        if not path.lower().endswith(".html"):
            return None

        try:
            with open(path, "r", encoding="utf-8") as f:
                html = f.read()
            return BeautifulSoup(html, "lxml")
        except Exception:
            return None

    # ---------------------------------------------------------
    # Parsing
    # ---------------------------------------------------------

    def parse_document(
        self,
        context: JusticeSearchContext,
        soup: BeautifulSoup,
    ) -> Iterable[Dict[str, Any]]:
        """
        Parse the clerk-provided HTML into raw court event dictionaries.
        """
        rows = soup.select("table tr")
        for row in rows[1:]:  # skip header
            cols = [clean_text(td.get_text()) for td in row.find_all("td")]
            if len(cols) < 5:
                continue

            case_number = cols[0]
            defendant = cols[1]
            charge = cols[2]
            event_type = cols[3]
            event_date = cols[4]

            yield {
                "source": "churchill_justice",
                "entity": "court_event",
                "case_number": case_number,
                "case_type": None,
                "status": None,
                "filed_date": None,
                "person": {
                    "defendant": defendant,
                },
                "charges": [
                    {
                        "statute": None,
                        "description": charge,
                        "severity": None,
                    }
                ],
                "events": [
                    {
                        "date": event_date,
                        "type": event_type,
                        "result": None,
                    }
                ],
                "meta": {
                    "query_type": context.query_type,
                    "query_value": context.query_value,
                    "returned_date": context.returned_date.isoformat(),
                    "source_file": context.source_file,
                },
            }
