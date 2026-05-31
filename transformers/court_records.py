"""
Court Records Transformer
v0.3.0

Normalizes raw court record objects from district/justice court connectors
into unified schema dictionaries.
"""

from __future__ import annotations


class CourtRecordTransformer:
    name = "court_record_transformer"
    version = "0.3.0"

    def transform(self, record: dict) -> dict:
        """
        Normalize raw court record dictionaries into unified schema.
        Expected input is a dict produced by court connectors.
        """
        return {
            "source": record.get("source"),
            "entity": "court_event",
            "case": {
                "number": record.get("case_number"),
                "type": record.get("case_type"),
                "status": record.get("status"),
                "filed_date": record.get("filed_date"),
            },
            "person": record.get("person"),
            "charges": record.get("charges", []),
            "events": record.get("events", []),
            "meta": record.get("meta", {}),
        }
