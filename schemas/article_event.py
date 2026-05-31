"""
Article Event Schema
v0.3.0

Represents metadata about a news article, independent of court/arrest events.
Useful for:
- Media analytics
- Provenance tracking
- Article-level clustering
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ArticleEvent:
    source: str
    article_id: Optional[str]
    url: str
    title: str
    published_date: Optional[datetime]
