from collections import Counter

from pydantic.main import BaseModel

from rfantasy_bingo_stats.models.defined_types import (
    Author,
    Book,
    SortedCounter,
)


class UniqueStatistics(BaseModel):
    """Counters for unique books + authors"""

    unique_books: SortedCounter[Book] = Counter()
    unique_authors: SortedCounter[Author] = Counter()
