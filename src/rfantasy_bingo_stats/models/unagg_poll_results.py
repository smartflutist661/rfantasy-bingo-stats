from collections import Counter

from pydantic.main import BaseModel

from rfantasy_bingo_stats.models.defined_types import Book


class UnaggregatedPollResults(BaseModel):
    """Metadata and results for a particular poll"""

    poll_type: str
    year: int
    results: Counter[Book]
