from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, slots=True)
class Entity9:
    id: str
    entity_name: str
    entity_revenue: Optional[float]
    entity_creation_date: str
    entity_updated_date: str
