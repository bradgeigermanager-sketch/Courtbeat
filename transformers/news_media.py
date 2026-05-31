"""
News Media Transformer
v0.3.0

Normalizes raw CourtEventRecord objects from news media sources
into unified schema dictionaries.
"""

from __future__ import annotations

from courtbeat.schemas.court_event import CourtEventRecord


class NewsMediaTransformer:
    name = "news_media_transformer"
    version = "0.3.0"

    def transform(self, record: CourtEventRecord) -> dict:
        """
        Convert a CourtEventRecord into a normalized dictionary.
        """
        return {
            "source": record.source,
            "entity": record.entity,
            "article": {
                "id": record.article_id,
                "url": record.article_url,
                "title": record.article_title,
                "date": (
                    record.article_date.isoformat()
                    if record.article_date else None
                ),
            },
            "person": {
                "full_name": record.person.full_name,
                "first_name": record.person.first_name,
                "middle_name": record.person.middle_name,
                "last_name": record.person.last_name,
            },
            "event": {
                "type": record.event.type,
                "court_level": record.event.court_level,
                "charges_raw": record.event.charges_raw,
                "disposition_raw": record.event.disposition_raw,
                "disposition_normalized": record.event.disposition_normalized,
                "hearing_date": (
                    record.event.hearing_date.isoformat()
                    if record.event.hearing_date else None
                ),
            },
            "meta": record.meta,
        }
