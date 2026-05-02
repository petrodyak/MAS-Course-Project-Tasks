from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Entity6CreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entity_name: str = Field(min_length=1)
    entity_revenue: float

    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    import_source: Optional[str] = None
    external_reference: Optional[str] = None
    notes: Optional[str] = None


class Entity6UpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entity_name: Optional[str] = Field(default=None, min_length=1)
    entity_revenue: Optional[float] = None

    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    import_source: Optional[str] = None
    external_reference: Optional[str] = None
    notes: Optional[str] = None

    @model_validator(mode="after")
    def non_empty_update(self) -> "Entity6UpdateRequest":
        # allow all fields nullable but ensure at least one field provided
        if (
            self.entity_name is None
            and self.entity_revenue is None
            and self.created_by is None
            and self.updated_by is None
            and self.import_source is None
            and self.external_reference is None
            and self.notes is None
        ):
            raise ValueError("At least one field must be provided for update")
        return self


class Entity6Response(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    Entity6Id: int
    entity_name: str
    entity_revenue: float
    entity_creation_date: datetime
    entity_updated_date: datetime

    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    import_source: Optional[str] = None
    external_reference: Optional[str] = None
    notes: Optional[str] = None

    is_deleted: int

    # Pydantic will serialize datetime to ISO-8601 strings.
