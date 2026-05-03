from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Business:
    id: int
    name: str
    type: str
    city_id: int
    description: str | None = None
    established_year: str | None = None