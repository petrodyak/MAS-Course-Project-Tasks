from __future__ import annotations

import math
from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Float,
    Index,
    Integer,
    String,
    Text,
)

try:
    from sqlalchemy.orm import declarative_base

    Base = declarative_base()
except Exception:  # pragma: no cover
    Base = None


class Entity6(Base):
    __tablename__ = "Entity6"

    Entity6Id = Column(Integer, primary_key=True, autoincrement=True)

    entity_name = Column(String, nullable=False)
    entity_revenue = Column(Float, nullable=False)
    # Acceptance criteria expects this column name exactly.
    entity_revenue_last2years = Column(Float, nullable=False)

    entity_creation_date = Column(DateTime, nullable=False)
    entity_updated_date = Column(DateTime, nullable=False)

    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    import_source = Column(String, nullable=True)
    external_reference = Column(String, nullable=True, unique=True)
    notes = Column(Text, nullable=True)

    is_deleted = Column(Integer, nullable=False, default=0)

    __table_args__ = (
        CheckConstraint("entity_revenue = entity_revenue", name="ck_entity6_revenue_not_nan"),
        Index("uq_entity6_external_reference", "external_reference", unique=True),
    )


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def validate_revenue(value: object) -> float:
    if value is None:
        raise ValueError("entity_revenue is required")
    try:
        revenue = float(value)
    except (TypeError, ValueError) as e:
        raise ValueError("entity_revenue must be a number") from e
    if math.isnan(revenue) or math.isinf(revenue):
        raise ValueError("entity_revenue must be a finite number")
    return revenue
