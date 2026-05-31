"""
Jail Records Transformer
v0.3.0

Normalizes raw jail/inmate records into unified schema dictionaries.
"""

from __future__ import annotations


class JailRecordTransformer:
    name = "jail_record_transformer"
    version = "0.3.0"

    def transform(self, record: dict) -> dict:
        """
        Normalize raw jail record dictionaries into unified schema.
        """
        return {
            "source": record.get("source"),
            "entity": "arrest_event",
            "inmate": {
                "name": record.get("name"),
                "booking_number": record.get("booking_number"),
                "dob": record.get("dob"),
            },
            "charges": record.get("charges", []),
            "booking": {
                "date": record.get("booking_date"),
                "location": record.get("facility"),
                "status": record.get("status"),
            },
            "meta": record.get("meta", {}),
        }
