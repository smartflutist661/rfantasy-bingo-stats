from pydantic.main import BaseModel

from rfantasy_bingo_stats.models.defined_types import (
    BingoName,
    CardID,
    SortedCounter,
)


class BingoTypeStatistics(BaseModel):
    """Counters for unique books + authors"""

    complete_bingos_by_card: SortedCounter[CardID]
    incomplete_bingos: SortedCounter[BingoName]
    incomplete_squares_by_bingo: SortedCounter[BingoName]
