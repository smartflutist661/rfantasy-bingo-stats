import warnings
from collections import Counter
from typing import (
    Any,
    cast,
)

from pydantic.functional_serializers import field_serializer
from pydantic.functional_validators import field_validator
from pydantic.main import BaseModel
from pydantic_core.core_schema import (
    SerializerFunctionWrapHandler,
    ValidatorFunctionWrapHandler,
)

from rfantasy_bingo_stats.constants import SUBBED_SQUARE_SEPARATOR
from rfantasy_bingo_stats.models.author_statistics import AuthorStatistics
from rfantasy_bingo_stats.models.bingo_type_statistics import BingoTypeStatistics
from rfantasy_bingo_stats.models.defined_types import (
    Author,
    Book,
    CardID,
    SortedCounter,
    SortedMapping,
    SquareName,
)
from rfantasy_bingo_stats.models.unique_statistics import UniqueStatistics


class BingoStatistics(BaseModel):
    """All summary statistics for a year of Bingo"""

    total_card_count: int
    total_story_count: int
    incomplete_cards: SortedCounter[CardID]
    incomplete_squares: SortedCounter[SquareName]
    incomplete_squares_per_card: SortedCounter[int]
    max_incomplete_squares: int
    subbed_squares: SortedCounter[tuple[SquareName, SquareName]]
    subbed_out_squares: SortedCounter[SquareName]
    avoided_squares: SortedCounter[SquareName]
    overall_uniques: UniqueStatistics
    square_uniques: SortedMapping[SquareName, UniqueStatistics]
    unique_squares_by_book: SortedCounter[Book]
    unique_squares_by_author: SortedCounter[Author]
    bad_spellings_by_card: SortedCounter[CardID]
    bad_spellings_by_book: SortedCounter[Book]
    card_uniques: SortedCounter[CardID]
    hard_mode_by_card: SortedCounter[CardID]
    hard_mode_by_square: SortedCounter[SquareName]
    books_per_author: SortedCounter[Author]
    overall_author_stats: AuthorStatistics
    square_author_stats: SortedMapping[SquareName, AuthorStatistics]
    unique_author_stats: AuthorStatistics
    unique_square_author_stats: SortedMapping[SquareName, AuthorStatistics]
    normal_bingo_type_stats: BingoTypeStatistics
    hardmode_bingo_type_stats: BingoTypeStatistics

    @field_serializer("subbed_squares", mode="wrap")
    def ser_tuple_key(
        self,
        data: Counter[tuple[str, ...]],
        handler: SerializerFunctionWrapHandler,
    ) -> dict[str, int]:
        out: Counter[str] = Counter()
        for key, val in data.items():
            out[SUBBED_SQUARE_SEPARATOR.join(key)] = val
        # Ignore the warning generated when the default handler receives a str instead of a tuple
        with warnings.catch_warnings(action="ignore", category=UserWarning):
            return cast(dict[str, int], handler(out))

    @field_validator("subbed_squares", mode="wrap")
    @classmethod
    def deser_tuple_key(  # type: ignore[explicit-any]
        cls,
        data: Any,
        handler: ValidatorFunctionWrapHandler,
    ) -> Counter[tuple[SquareName, SquareName]]:
        out: Counter[tuple[str, ...]] = Counter()
        for key, val in data.items():
            if isinstance(key, tuple):
                out[key] = val
            else:
                out[tuple(key.split(SUBBED_SQUARE_SEPARATOR))] = val
        return cast(Counter[tuple[SquareName, SquareName]], handler(out))
