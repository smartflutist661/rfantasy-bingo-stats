"""
Created on Apr 7, 2023

@author: fred
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import (
    dataclass,
    fields,
)
from typing import (
    Any,
    cast,
)

from .defined_types import Book
from .utils import to_data


@dataclass(frozen=True)
class RecordedStates:
    """Known duplicate title/author pairs and likely non-duplicate title/author pairs"""

    dupes: defaultdict[Book, set[Book]]
    non_dupes: set[Book]

    @classmethod
    def from_data(cls, data: Any) -> RecordedStates:
        """Restore from JSON data"""
        return cls(
            dupes=defaultdict(
                set,
                {
                    cast(Book, str(key)): {cast(Book, str(v)) for v in val}
                    for key, val in data["dupes"].items()
                },
            ),
            non_dupes={cast(Book, str(val)) for val in data["non_dupes"]},
        )

    def to_data(self) -> dict[str, Any]:
        """Write to JSON data"""
        out = {}
        for key, val in {field.name: getattr(self, field.name) for field in fields(self)}.items():
            out[key] = to_data(val)
        return out

    @classmethod
    def empty(cls) -> RecordedStates:
        """Create an empty RecordedStates"""
        return cls(
            dupes=defaultdict(set),
            non_dupes=set(),
        )
