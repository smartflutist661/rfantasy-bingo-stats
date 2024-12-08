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
    cast,
)

from .defined_types import (
    Author,
    Book,
)
from .utils import (
    AnyData,
    to_data,
)


@dataclass(frozen=True)
class UniqueStatistics:
    """Counters for unique books + authors"""

    unique_books: Counter[Book] = field(default_factory=Counter)
    unique_authors: Counter[Author] = field(default_factory=Counter)

    @classmethod
    def from_data(cls, data: Any) -> UniqueStatistics:
        """Construct from JSON data"""
        return cls(
            unique_books=Counter(
                {
                    Book(str(key)): int(cast(int, val))
                    for key, val in data["unique_books"].items()
                }
            ),
            unique_authors=Counter(
                {
                    Author(str(key)): int(cast(int, val))
                    for key, val in data["unique_authors"].items()
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
