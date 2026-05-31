"""
Sheriff Logs Transformer
v0.3.0

Normalizes sheriff booking log entries into unified schema dictionaries.
"""

from __future__ import annotations


class SheriffLogTransformer:
    name = "sheriff_log_transformer"
    version = "0.3.0"

    def transform(self, record: dict) -> dict:
        """
        Normalize raw sheriff log dictionaries into unified schema.
        """
        return {
            "source": record.get("source"),
            "entity": "arrest_event",
            "person": {
                "name": record.get("name"),
                "age": record.get("age"),
            },
            "arrest": {
                "date": record.get("arrest_date"),
                "location": record.get("location"),
                "agency": record.get("agency"),
            },
            "charges": record.get("charges", []),
            "meta": record.get("meta", {}),
        }
