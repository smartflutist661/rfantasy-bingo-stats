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
from types import MappingProxyType as MAP
from typing import (
    Any,
    Mapping,
    cast,
)

from ..constants import SUBBED_SQUARE_SEPARATOR
from .author_statistics import AuthorStatistics
from .defined_types import (
    Author,
    Book,
    CardID,
    SquareName,
)
from .unique_statistics import UniqueStatistics
from .utils import (
    AnyData,
    author_counter_from_data,
    book_counter_from_data,
    card_id_counter_from_data,
    square_name_counter_from_data,
    to_data,
)


@dataclass(frozen=True)
class BingoStatistics:
    """All summary statistics for a year of Bingo"""

    total_card_count: int
    total_story_count: int
    incomplete_cards: Counter[CardID]
    incomplete_squares: Counter[SquareName]
    incomplete_squares_per_card: Counter[int]
    max_incomplete_squares: int
    subbed_squares: Counter[tuple[SquareName, SquareName]]
    subbed_out_squares: Counter[SquareName]
    avoided_squares: Counter[SquareName]
    overall_uniques: UniqueStatistics
    square_uniques: Mapping[SquareName, UniqueStatistics]
    unique_squares_by_book: Counter[Book]
    unique_squares_by_author: Counter[Author]
    bad_spellings_by_card: Counter[CardID]
    bad_spellings_by_book: Counter[Book]
    card_uniques: Counter[CardID]
    hard_mode_by_card: Counter[CardID]
    hard_mode_by_square: Counter[SquareName]
    books_per_author: Counter[Author]
    overall_author_stats: AuthorStatistics
    square_author_stats: Mapping[SquareName, AuthorStatistics]

    @classmethod
    def from_data(cls, data: Any) -> BingoStatistics:
        """Create BingoStatistics from JSON data"""
        return cls(
            total_card_count=int(cast(int, data["total_card_count"])),
            incomplete_cards=card_id_counter_from_data(data["incomplete_cards"]),
            incomplete_squares=square_name_counter_from_data(data["incomplete_squares"]),
            max_incomplete_squares=int(cast(int, data["max_incomplete_squares"])),
            incomplete_squares_per_card=Counter(
                {
                    int(cast(int, key)): int(cast(int, val))
                    for key, val in data["incomplete_squares_per_card"].items()
                }
            ),
            total_story_count=int(cast(int, data["total_story_count"])),
            subbed_squares=Counter(
                {
                    cast(
                        tuple[SquareName, SquareName],
                        tuple(SquareName(k) for k in key.split(SUBBED_SQUARE_SEPARATOR)),
                    ): int(cast(int, val))
                    for key, val in data["subbed_squares"].items()
                }
            ),
            subbed_out_squares=square_name_counter_from_data(data["subbed_out_squares"]),
            avoided_squares=square_name_counter_from_data(data["avoided_squares"]),
            overall_uniques=UniqueStatistics.from_data(data["overall_uniques"]),
            square_uniques=MAP(
                {
                    SquareName(str(key)): UniqueStatistics.from_data(val)
                    for key, val in data["square_uniques"].items()
                }
            ),
            unique_squares_by_book=book_counter_from_data(data["unique_squares_by_book"]),
            unique_squares_by_author=author_counter_from_data(data["unique_squares_by_author"]),
            bad_spellings_by_card=card_id_counter_from_data(data["bad_spellings_by_card"]),
            bad_spellings_by_book=book_counter_from_data(data["bad_spellings_by_book"]),
            card_uniques=card_id_counter_from_data(data["card_uniques"]),
            hard_mode_by_card=card_id_counter_from_data(data["hard_mode_by_card"]),
            hard_mode_by_square=square_name_counter_from_data(data["hard_mode_by_square"]),
            books_per_author=author_counter_from_data(data["books_per_author"]),
            overall_author_stats=AuthorStatistics.from_data(data["overall_author_stats"]),
            square_author_stats=MAP(
                {
                    SquareName(str(key)): AuthorStatistics.from_data(val)
                    for key, val in data["square_author_stats"].items()
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
                    SUBBED_SQUARE_SEPARATOR.join(key): to_data(val)
                    for key, val in field_val.items()
                }
            else:
                out[field_name] = to_data(field_val)
        return out
