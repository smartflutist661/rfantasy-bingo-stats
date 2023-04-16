"""
Created on Apr 15, 2023

@author: fred
"""

from __future__ import annotations

from collections import Counter
from dataclasses import (
    dataclass,
    fields,
)
from typing import (
    Any,
    cast,
)

from ..data.current import CUSTOM_SEPARATOR
from ..data_operations.author_title_book_operations import (
    book_to_title_author,
    title_author_to_book,
)
from .defined_types import (
    Author,
    Book,
    CardID,
    SquareName,
    TitleAuthor,
)
from .utils import (
    AnyData,
    to_data,
)


@dataclass(frozen=True)
class BingoStatistics:
    """All summary statistics for a year of Bingo"""

    total_card_count: int
    incomplete_cards: Counter[CardID]
    incomplete_squares: Counter[SquareName]
    max_incomplete_squares: int
    incomplete_squares_per_card: Counter[int]
    total_incomplete_squares: int
    total_story_count: int
    unique_title_authors: Counter[TitleAuthor]
    unique_authors: Counter[Author]
    unique_story_count: int
    unique_author_count: int
    subbed_squares: Counter[tuple[SquareName, SquareName]]
    subbed_out_squares: Counter[SquareName]
    avoided_squares: Counter[SquareName]

    @classmethod
    def from_data(cls, data: Any) -> BingoStatistics:
        """Create BingoStatistics from JSON data"""
        return cls(
            total_card_count=int(cast(int, data["total_card_count"])),
            incomplete_cards=Counter(
                {
                    cast(CardID, str(key)): int(cast(int, val))
                    for key, val in data["incomplete_cards"].items()
                }
            ),
            incomplete_squares=Counter(
                {
                    cast(SquareName, str(key)): int(cast(int, val))
                    for key, val in data["incomplete_squares"].items()
                }
            ),
            max_incomplete_squares=int(cast(int, data["max_incomplete_squares"])),
            incomplete_squares_per_card=Counter(
                {
                    int(cast(int, key)): int(cast(int, val))
                    for key, val in data["incomplete_squares_per_card"].items()
                }
            ),
            total_incomplete_squares=int(cast(int, data["total_incomplete_squares"])),
            total_story_count=int(cast(int, data["total_story_count"])),
            unique_title_authors=Counter(
                {
                    book_to_title_author(cast(Book, str(key)), CUSTOM_SEPARATOR): int(
                        cast(int, val)
                    )
                    for key, val in data["unique_title_authors"].items()
                }
            ),
            unique_authors=Counter(
                {
                    cast(Author, str(key)): int(cast(int, val))
                    for key, val in data["unique_authors"].items()
                }
            ),
            unique_story_count=int(cast(int, data["unique_story_count"])),
            unique_author_count=int(cast(int, data["unique_author_count"])),
            subbed_squares=Counter(
                {
                    cast(tuple[SquareName, SquareName], tuple(key.split(CUSTOM_SEPARATOR))): int(
                        cast(int, val)
                    )
                    for key, val in data["subbed_squares"].items()
                }
            ),
            subbed_out_squares=Counter(
                {
                    cast(SquareName, str(key)): int(cast(int, val))
                    for key, val in data["subbed_out_squares"].items()
                }
            ),
            avoided_squares=Counter(
                {
                    cast(SquareName, str(key)): int(cast(int, val))
                    for key, val in data["avoided_squares"].items()
                }
            ),
        )

    def to_data(self) -> dict[str, Any]:
        """Write to JSON data"""
        out: dict[str, AnyData] = {}
        for field_name, field_val in {
            field.name: getattr(self, field.name) for field in fields(self)
        }.items():
            if field_name == "subbed_squares":
                out[field_name] = {
                    CUSTOM_SEPARATOR.join(key): to_data(val) for key, val in field_val.items()
                }
            elif field_name == "unique_title_authors":
                out[field_name] = {
                    title_author_to_book(key, CUSTOM_SEPARATOR): to_data(val)
                    for key, val in field_val.items()
                }
            else:
                out[field_name] = to_data(field_val)
        return out
