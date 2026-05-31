"""
Arrest Event Schema
v0.3.0

Represents normalized arrest events from:
- Jail systems (Washoe Jail, Clark Jail)
- Sheriff logs (Churchill Sheriff)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from datetime import datetime

from courtbeat.schemas.person import Person


@dataclass
class ArrestCharge:
    statute: Optional[str]
    description: str
    severity: Optional[str] = None


@dataclass
class ArrestDetails:
    date: Optional[datetime]
    location: Optional[str]
    agency: Optional[str]
    booking_number: Optional[str] = None
    facility: Optional[str] = None
    status: Optional[str] = None


@dataclass
class ArrestEventRecord:
    source: str                   # e.g., "washoe_jail"
    entity: str                   # always "arrest_event"
    person: Person
    charges: List[ArrestCharge] = field(default_factory=list)
    arrest: ArrestDetails = None
    meta: Dict = field(default_factory=dict)
