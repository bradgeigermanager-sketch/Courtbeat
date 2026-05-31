"""
Court Event Schema
v0.3.0

Represents a normalized court event extracted from:
- News media (Fallon Post, Reno Gazette, etc.)
- District court connectors
- Justice court connectors
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict

from courtbeat.schemas.person import Person


@dataclass
class Charge:
    statute: Optional[str]
    description: str
    severity: Optional[str] = None


@dataclass
class Event:
    type: str                     # plea, sentencing, arraignment, arrest, etc.
    court_level: str              # district | justice | unknown
    charges_raw: str
    charges_normalized: List[Charge] = field(default_factory=list)
    disposition_raw: Optional[str] = None
    disposition_normalized: Optional[str] = None
    hearing_date: Optional[datetime] = None


@dataclass
class CourtEventRecord:
    source: str                   # e.g., "fallon_post"
    entity: str                   # always "court_event"
    article_id: Optional[str]
    article_url: str
    article_title: str
    article_date: Optional[datetime]
    person: Person
    event: Event
    meta: Dict = field(default_factory=dict)
