"""
Person Schema
v0.3.0

Represents an individual mentioned in:
- Court events
- Arrest events
- News media reports
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class Person:
    full_name: str
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
