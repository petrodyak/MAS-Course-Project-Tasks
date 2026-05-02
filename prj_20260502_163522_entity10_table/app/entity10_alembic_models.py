from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Entity10(Base):
    __tablename__ = "Entity10"

    entity_id: Mapped[str] = mapped_column(sa.Text, primary_key=True, nullable=False)
    entity_name: Mapped[str] = mapped_column(sa.Text, nullable=False)
    entity_revenue: Mapped[float | None] = mapped_column(sa.REAL, nullable=True)
    entity_creation_date: Mapped[str] = mapped_column(sa.Text, nullable=True)
    entity_updated_date: Mapped[str] = mapped_column(sa.Text, nullable=True)
