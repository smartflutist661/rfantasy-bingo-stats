"""
Created on Apr 7, 2023

@author: fred
"""

from __future__ import annotations

from dataclasses import (
    dataclass,
    fields,
)
from typing import (
    Any,
    Literal,
    Optional,
    cast,
)

from rfantasy_bingo_stats.models.utils import (
    AnyData,
    to_data,
)

Gender = Literal["Man", "Woman", "Nonbinary", "Unknown"]
Race = Literal["White", "Black", "Asian", "Hispanic", "Native", "Unknown"]
Nationality = Literal["Unknown"]


@dataclass(frozen=True)
class AuthorInfo:
    """Information about a single author"""

    gender: Gender = "Unknown"
    race: Race = "Unknown"
    queer: Optional[bool] = None
    nationality: Nationality = "Unknown"

    @classmethod
    def from_data(cls, data: Any) -> AuthorInfo:
        return cls(
            gender=cast(Gender, str(data["gender"])),
            race=cast(Race, str(data["race"])),
            queer=bool(data["queer"]) if data["queer"] is not None else None,
            nationality=cast(Nationality, str(data["nationality"])),
        )

    def to_data(self) -> dict[str, Any]:
        """Write to JSON data"""
        out: dict[str, AnyData] = {}
        for field_name, field_val in {
            field.name: getattr(self, field.name) for field in fields(self)
        }.items():
            out[field_name] = to_data(field_val)
        return out
