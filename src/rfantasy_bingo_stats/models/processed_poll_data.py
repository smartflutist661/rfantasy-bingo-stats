from pydantic.main import BaseModel

from rfantasy_bingo_stats.models.defined_types import TitleAuthor


class ProcessedPollData(BaseModel):
    poll_type: str
    poll_year: int
    votes: list[TitleAuthor]
