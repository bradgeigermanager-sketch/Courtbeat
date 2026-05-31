"""
Fallon Post Retrieval Routines
v0.3.0

Source-specific routines for:
- Article discovery
- Pagination
- HTML fetching
- Segmentation
- Line-level parsing

These routines are intentionally atomic so they can be reused by:
- Connectors
- Transformers
- Tests
- DAG nodes
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Iterable

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from courtbeat.utils.http import http_get
from courtbeat.utils.text import clean_text
from courtbeat.schemas.person import Person
from courtbeat.schemas.court_event import CourtEventRecord, Event, Charge


# ---------------------------------------------------------------------------
# Version
# ---------------------------------------------------------------------------

FALLON_POST_ROUTINES_VERSION = "0.3.0"


# ---------------------------------------------------------------------------
# Context object for article metadata
# ---------------------------------------------------------------------------

@dataclass
class ArticleContext:
    url: str
    title: str
    date: Optional[datetime]


# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------

COURT_TITLE_PATTERNS = [
    re.compile(r"district\s+court", re.I),
    re.compile(r"justice\s+court", re.I),
    re.compile(r"sheriff", re.I),
    re.compile(r"arrest", re.I),
    re.compile(r"booking", re.I),
]

NAME_WITH_COMMA = re.compile(
    r"^([A-Z][A-Za-z'.-]+(?:\s+[A-Z][A-Za-z'.-]+){0,3}),\s*(.*)$"
)

EVENT_VERBS = {
    "pleaded": "plea",
    "pleads": "plea",
    "plead": "plea",
    "sentenced": "sentencing",
    "arraigned": "arraignment",
    "appeared": "appearance",
    "arrested": "arrest",
    "booked": "arrest",
}

DISPOSITION_WORDS = {
    "guilty": "guilty",
    "not guilty": "not_guilty",
    "no contest": "no_contest",
    "dismissed": "dismissed",
}


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def extract_article_id(url: str) -> Optional[str]:
    path = urlparse(url).path
    m = re.search(r"/article/(\d+)", path)
    return m.group(1) if m else None


def parse_date(text: Optional[str]) -> Optional[datetime]:
    if not text:
        return None
    for fmt in ("%Y-%m-%d", "%B %d, %Y", "%b %d, %Y"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def split_name(full_name: str) -> Person:
    parts = full_name.split()
    if len(parts) == 1:
        return Person(full_name=full_name)
    if len(parts) == 2:
        return Person(full_name=full_name, first_name=parts[0], last_name=parts[1])
    return Person(
        full_name=full_name,
        first_name=parts[0],
        middle_name=" ".join(parts[1:-1]),
        last_name=parts[-1],
    )


def infer_event_type(text: str) -> Optional[str]:
    t = text.lower()
    for verb, etype in EVENT_VERBS.items():
        if verb in t:
            return etype
    return None


def extract_disposition(text: str):
    t = text.lower()
    for phrase, norm in DISPOSITION_WORDS.items():
        if phrase in t:
            return phrase, norm
    return None, None


def extract_charges(text: str) -> str:
    m = re.search(r"\bfor\b\s+(.*)", text, re.I)
    if m:
        return m.group(1).strip()
    m = re.search(r"on a charge of\s+(.*)", text, re.I)
    if m:
        return m.group(1).strip()
    return text.strip()


def infer_court_level(title: str) -> str:
    t = title.lower()
    if "district court" in t:
        return "district"
    if "justice court" in t:
        return "justice"
    return "unknown"


# ---------------------------------------------------------------------------
# Main routines class
# ---------------------------------------------------------------------------

class FallonPostRoutines:
    BASE_URL = "https://www.thefallonpost.org"

    # ---------------------------------------------------------
    # Article discovery
    # ---------------------------------------------------------

    def discover_articles(self, max_pages: int = 10, delay: float = 0.5) -> Iterable[ArticleContext]:
        """
        Crawl the Fallon Post article index and yield ArticleContext objects
        for articles matching court/sheriff patterns.
        """
        for page in range(1, max_pages + 1):
            soup = self._fetch_index(page)
            summaries = list(self._extract_summaries(soup))
            if not summaries:
                break

            for s in summaries:
                if self._is_court_article(s["title"]):
                    yield ArticleContext(
                        url=s["url"],
                        title=s["title"],
                        date=parse_date(s["date_text"]),
                    )

            time.sleep(delay)

    # ---------------------------------------------------------
    # Fetching
    # ---------------------------------------------------------

    def fetch_article(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch and parse an article page.
        """
        resp = http_get(url)
        if resp is None or resp.status_code == 404:
            return None
        return BeautifulSoup(resp.text, "lxml")

    # ---------------------------------------------------------
    # Segmentation
    # ---------------------------------------------------------

    def extract_lines(self, soup: BeautifulSoup) -> List[str]:
        """
        Extract text lines from article body.
        """
        if soup is None:
            return []

        body = soup.select_one("article") or soup.select_one(".post-content") or soup
        lines = []
        for el in body.find_all(["p", "li"]):
            text = clean_text(el.get_text(" ", strip=True))
            if text:
                lines.append(text)
        return lines

    # ---------------------------------------------------------
    # Parsing
    # ---------------------------------------------------------

    def parse_line(self, line: str, context: ArticleContext) -> Optional[CourtEventRecord]:
        """
        Convert a single line of text into a CourtEventRecord.
        """
        m = NAME_WITH_COMMA.match(line)
        if not m:
            return None

        name_raw, rest = m.groups()
        person = split_name(name_raw)

        event_type = infer_event_type(rest) or "unknown"
        disp_raw, disp_norm = extract_disposition(rest)
        charges_raw = extract_charges(rest)

        event = Event(
            type=event_type,
            court_level=infer_court_level(context.title),
            charges_raw=charges_raw,
            charges_normalized=[Charge(statute=None, description=charges_raw)],
            disposition_raw=disp_raw,
            disposition_normalized=disp_norm,
            hearing_date=context.date,
        )

        return CourtEventRecord(
            source="fallon_post",
            entity="court_event",
            article_id=extract_article_id(context.url),
            article_url=context.url,
            article_title=context.title,
            article_date=context.date,
            person=person,
            event=event,
            meta={"raw_line": line},
        )

    # ---------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------

    def _fetch_index(self, page: int) -> BeautifulSoup:
        url = f"{self.BASE_URL}/article/?page={page}"
        resp = http_get(url)
        return BeautifulSoup(resp.text, "lxml") if resp else BeautifulSoup("", "lxml")

    def _extract_summaries(self, soup: BeautifulSoup):
        cards = soup.select("article, .article-card, .post")
        for card in cards:
            a = card.find("a", href=True)
            if not a:
                continue
            title = clean_text(a.get_text())
            href = a["href"]
            url = urljoin(self.BASE_URL, href)
            date_el = card.find("time")
            date_text = date_el.get("datetime") if date_el and date_el.has_attr("datetime") else (
                clean_text(date_el.get_text()) if date_el else None
            )
            yield {
                "title": title,
                "url": url,
                "date_text": date_text,
            }

    def _is_court_article(self, title: str) -> bool:
        return any(p.search(title or "") for p in COURT_TITLE_PATTERNS)
