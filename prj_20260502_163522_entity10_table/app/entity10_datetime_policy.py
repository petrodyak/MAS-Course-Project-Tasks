from __future__ import annotations

import datetime as _dt


def utc_now_iso() -> str:
    """Return an ISO-8601 UTC string.

    Note: migration/DDL uses SQLite CURRENT_TIMESTAMP for defaults and
    trigger-based updates. This helper is for potential future code paths.
    """

    return _dt.datetime.now(tz=_dt.timezone.utc).isoformat()
