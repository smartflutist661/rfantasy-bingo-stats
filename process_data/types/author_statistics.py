"""
Created on Apr 22, 2023

@author: fred
"""
from __future__ import annotations

from collections import Counter
from dataclasses import (
    dataclass,
    field,
    fields,
)
from typing import (
    Any,
    Optional,
    cast,
)

from .author_info import (
    Gender,
    Nationality,
    Race,
)
from .utils import (
    AnyData,
    to_data,
)


@dataclass(frozen=True)
class AuthorStatistics:
    """Counters for unique books + authors"""

    gender_count: Counter[Gender] = field(default_factory=Counter)
    race_count: Counter[Race] = field(default_factory=Counter)
    queer_count: Counter[Optional[bool]] = field(default_factory=Counter)
    nationality_count: Counter[Nationality] = field(default_factory=Counter)

    @classmethod
    def from_data(cls, data: Any) -> AuthorStatistics:
        """Construct from JSON data"""
        return cls(
            gender_count=Counter(
                {
                    cast(Gender, str(key)): int(cast(int, val))
                    for key, val in data["gender_count"].items()
                }
            ),
            race_count=Counter(
                {
                    cast(Race, str(key)): int(cast(int, val))
                    for key, val in data["race_count"].items()
                }
            ),
            queer_count=Counter(
                {
                    bool(cast(bool, key)) if key is not None else key: int(cast(int, val))
                    for key, val in data["queer_count"].items()
                }
            ),
            nationality_count=Counter(
                {
                    cast(Nationality, str(key)): int(cast(int, val))
                    for key, val in data["nationality_count"].items()
                }
            ),
        )

    def to_data(self) -> dict[str, Any]:
        """Write to JSON data"""
        out: dict[str, AnyData] = {}
        for field_name, field_val in {
            field.name: getattr(self, field.name) for field in fields(self)
        }.items():
            out[field_name] = to_data(field_val)
        return out
