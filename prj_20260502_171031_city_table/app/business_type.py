from __future__ import annotations

from enum import Enum


class BusinessType(str, Enum):
    COMPANY = "Company"
    STORE_SHOP = "Store / Shop"
    RESTAURANT = "Restaurant"
    OFFICE = "Office"

    @classmethod
    def values(cls) -> set[str]:
        return {t.value for t in cls}
