from typing import Optional

from pydantic.main import BaseModel
from pydantic.type_adapter import TypeAdapter

from rfantasy_bingo_stats.models.defined_types import SortedMapping


class YearlyBingoStatistics(BaseModel):
    """
    Summary statistics for comparing year-over-year changes in Bingo

    Mostly a convenience class for deserializing manually-acquired data
    """

    total_participant_count: int
    total_card_count: int
    total_square_count: Optional[int]
    total_story_count: Optional[int]
    unique_story_count: Optional[int]
    total_author_count: Optional[int]
    unique_author_count: Optional[int]
    hard_mode_cards: Optional[int]
    hard_mode_squares: Optional[int]
    hero_mode_cards: Optional[int]
    total_misspellings: Optional[int]


YearStatsAdapter: TypeAdapter[SortedMapping[int, YearlyBingoStatistics]] = TypeAdapter(
    SortedMapping[int, YearlyBingoStatistics]
)
