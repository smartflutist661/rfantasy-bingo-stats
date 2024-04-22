"""
Created on Apr 22, 2023

@author: fred
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import (
    dataclass,
    fields,
)
from typing import Any

from .defined_types import (
    Author,
    Book,
)
from .utils import to_data


@dataclass(frozen=True)
class RecordedIgnores:
    """Duplicates that were ignored in the past"""

    ignored_author_dupes: defaultdict[Author, set[Author]]
    ignored_book_dupes: defaultdict[Book, set[Book]]

    @classmethod
    def from_data(cls, data: dict[str, Any]) -> RecordedIgnores:
        """Reconstruct from JSON data"""
        return cls(
            ignored_author_dupes=defaultdict(
                set,
                {
                    Author(str(key)): {Author(str(v)) for v in val}
                    for key, val in data["ignored_author_dupes"].items()
                },
            ),
            ignored_book_dupes=defaultdict(
                set,
                {
                    Book(str(key)): {Book(str(v)) for v in val}
                    for key, val in data["ignored_book_dupes"].items()
                },
            ),
        )

    def to_data(self) -> dict[str, Any]:
        """Write to JSON data"""
        out = {}
        for key, val in {field.name: getattr(self, field.name) for field in fields(self)}.items():
            out[key] = to_data(val)
        return out
