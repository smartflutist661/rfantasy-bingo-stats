from pydantic.main import BaseModel

from rfantasy_bingo_stats.models.defined_types import (
    Book,
    SortedAbstractSet,
)


class CleanedPollData(BaseModel):
    poll_type: str
    poll_year: int
    votes: tuple[SortedAbstractSet[Book], ...]
