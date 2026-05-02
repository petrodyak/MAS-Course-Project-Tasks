from __future__ import annotations

from datetime import datetime, timezone


def utc_iso8601_now() -> str:
    """Return current UTC time as ISO-8601 string with microsecond precision."""

    return datetime.now(timezone.utc).isoformat(timespec="microseconds")
