from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class District:
    district_id: int
    city_id: int
    name: str
    code: str | None
    type: str
    status: str
